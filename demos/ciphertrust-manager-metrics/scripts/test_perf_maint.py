"""Local unit checks for chunked inserts, stratified load_series, prune+optimize."""
from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Point Config at a temp DB before importing db helpers that read Config.
_TMP = tempfile.TemporaryDirectory()
_DB = Path(_TMP.name) / "test.db"
os.environ["DATABASE_PATH"] = str(_DB)
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-checks"

from cm_metrics import db  # noqa: E402
from cm_metrics.parser import Sample  # noqa: E402
from cm_metrics.store import ApplianceStore  # noqa: E402


class PerfMaintTests(unittest.TestCase):
    def setUp(self) -> None:
        if _DB.exists():
            _DB.unlink()
        for suffix in ("-wal", "-shm"):
            p = Path(str(_DB) + suffix)
            if p.exists():
                p.unlink()
        # Force re-init
        db._initialized = False  # noqa: SLF001
        db.init_db()
        now = time.time()
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO appliances (id, host, username, password_enc, created_at, updated_at) "
                "VALUES (1, 'h', 'u', 'x', ?, ?)",
                (now, now),
            )

    def test_chunked_insert_and_short_load(self) -> None:
        now = time.time()
        points = [
            (f"fp{i}", "metric_a", {"i": str(i % 3)}, now - (i % 100), float(i))
            for i in range(6000)
        ]
        with mock.patch.object(db, "_INSERT_BATCH_SIZE", 1000):
            db.insert_metric_points(1, points)
        rows = db.load_series(1, metric_name="metric_a", since=now - 200, limit=5000)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), 5000)

    def test_stratified_long_window_covers_old_and_new(self) -> None:
        now = time.time()
        points = []
        for i in range(200):
            points.append(("old", "m", {}, now - 20000 + i, 1.0))
        for i in range(200):
            points.append(("new", "m", {}, now - 200 + i, 2.0))
        db.insert_metric_points(1, points)
        rows = db.load_series(1, metric_name="m", since=now - 21000, until=now, limit=200)
        fps = {r["fingerprint"] for r in rows}
        self.assertIn("old", fps)
        self.assertIn("new", fps)
        ts = [r["t"] for r in rows]
        self.assertEqual(ts, sorted(ts))

    def test_prune_runs_optimize(self) -> None:
        now = time.time()
        db.insert_metric_points(
            1,
            [("fp", "m", {}, now - 40 * 86400, 1.0), ("fp", "m", {}, now, 2.0)],
        )
        with mock.patch.object(db, "optimize_db") as opt:
            deleted = db.prune_old_points(keep_days=7)
            opt.assert_called_once()
        self.assertGreaterEqual(deleted, 1)
        rows = db.load_series(1, metric_name="m", since=now - 10, limit=10)
        self.assertEqual(len(rows), 1)

    def test_chunked_prune_deletes_all_old(self) -> None:
        now = time.time()
        points = [("fp", "m", {}, now - 40 * 86400, float(i)) for i in range(120)]
        points.append(("fp", "m", {}, now, 999.0))
        db.insert_metric_points(1, points)
        with mock.patch.object(db, "optimize_db"), mock.patch.object(db, "_PRUNE_BATCH_SIZE", 40):
            n = db.prune_old_points(keep_days=7)
        self.assertGreaterEqual(n, 120)
        rows = db.load_series(1, metric_name="m", since=now - 10, limit=10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["v"], 999.0)

    def test_persist_releases_store_lock(self) -> None:
        store = ApplianceStore(1, history_seconds=3600)
        samples = [Sample(name="n", labels={"a": "1"}, value=1.0)]
        held = []

        def slow_insert(appliance_id, points):
            held.append(store._lock.acquire(blocking=False))
            if held[-1]:
                store._lock.release()

        with mock.patch.object(db, "insert_metric_points", side_effect=slow_insert):
            store.ingest(samples, source="live", persist=True)
        self.assertEqual(held, [True], "insert should run without holding store lock")

    def test_raw_series_cache_shared_across_labels(self) -> None:
        store = ApplianceStore(1, history_seconds=3600)
        now = time.time()
        db.insert_metric_points(
            1,
            [
                ("a", "m", {"mode": "idle"}, now - 10, 1.0),
                ("b", "m", {"mode": "user"}, now - 10, 2.0),
            ],
        )
        calls = {"n": 0}
        real = db.load_series

        def counting(*args, **kwargs):
            calls["n"] += 1
            return real(*args, **kwargs)

        with mock.patch.object(db, "load_series", side_effect=counting):
            store.series_by_name("m", {"mode": "idle"}, since=now - 60)
            store.series_by_name("m", {"mode": "user"}, since=now - 60)
        self.assertEqual(calls["n"], 1, "second label filter should reuse raw DB rows")

    def test_async_delete_chunk_and_notify(self) -> None:
        now = time.time()
        db.insert_metric_points(
            1,
            [("fp", "m", {}, now - i, float(i)) for i in range(90)],
        )
        meta = db.begin_appliance_delete(1)
        self.assertIsNotNone(meta)
        self.assertEqual(len(db.list_appliances()), 0)
        pending = db.list_delete_pending_appliances()
        self.assertEqual(len(pending), 1)
        with mock.patch.object(db, "_PRUNE_BATCH_SIZE", 40):
            # Use delete batch helper
            while db.delete_metric_points_batch(1, 40) > 0:
                pass
        self.assertTrue(db.finalize_appliance_delete(1))
        self.assertEqual(db.list_delete_pending_appliances(), [])

        # Failure notification path
        db.init_db()
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO appliances (id, host, username, password_enc, created_at, updated_at) "
                "VALUES (2, 'h2', 'u', 'x', ?, ?)",
                (now, now),
            )
        db.begin_appliance_delete(2)
        db.mark_appliance_delete_failed(2, "boom")
        nid = db.add_notification(
            kind="appliance_delete_failed",
            title="fail",
            message="boom",
            appliance_id=2,
        )
        notes = db.list_active_notifications()
        self.assertTrue(any(n["id"] == nid for n in notes))
        self.assertTrue(db.dismiss_notification(nid))
        self.assertFalse(any(n["id"] == nid for n in db.list_active_notifications()))
        apps = db.list_appliances()
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]["last_status"], "delete_failed")

    def test_vacuum_helper_smoke(self) -> None:
        now = time.time()
        db.insert_metric_points(1, [("fp", "m", {}, now, 1.0)])
        result = db.vacuum_db()
        self.assertIn("before_bytes", result)
        self.assertIn("after_bytes", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
