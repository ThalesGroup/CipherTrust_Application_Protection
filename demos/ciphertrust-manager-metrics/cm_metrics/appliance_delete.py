"""Background chunked appliance deletion (UI returns immediately)."""

from __future__ import annotations

import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator

from . import db

logger = logging.getLogger(__name__)

# Keep batches small and paced so Add/Connect/scrapes are not starved.
_BATCH = 2_000
_BATCH_PAUSE_SEC = 0.75
_lock = threading.Lock()
_threads: dict[int, threading.Thread] = {}
_started = False
# Orphan history purges after the appliances row was detached (id -> Thread).
_orphan_threads: dict[int, threading.Thread] = {}
# When set, purge loops wait — used during Add Appliance / connect.
_pause = threading.Event()
_pause_depth = 0
_pause_lock = threading.Lock()


def pause_purges() -> None:
    """Stop history-purge batches (nested-safe)."""
    global _pause_depth
    with _pause_lock:
        _pause_depth += 1
        _pause.set()


def resume_purges() -> None:
    global _pause_depth
    with _pause_lock:
        _pause_depth = max(0, _pause_depth - 1)
        if _pause_depth == 0:
            _pause.clear()


@contextmanager
def purges_paused() -> Iterator[None]:
    pause_purges()
    try:
        # Let an in-flight batch finish / release the SQLite write lock.
        time.sleep(0.3)
        yield
    finally:
        resume_purges()


def _wait_if_paused() -> None:
    while _pause.is_set():
        time.sleep(0.25)


def _label(meta: dict[str, Any]) -> str:
    name = (meta.get("display_name") or "").strip()
    host = (meta.get("host") or "").replace("https://", "").replace("http://", "")
    return name or host or f"#{meta.get('id')}"


def _purge_metric_history(appliance_id: int, label: str) -> None:
    deleted_batches = 0
    deleted_rows = 0
    started = time.time()
    while True:
        _wait_if_paused()
        try:
            n = db.delete_metric_points_batch(appliance_id, _BATCH)
        except Exception as exc:  # noqa: BLE001
            # Likely locked — back off and keep trying without crashing the job.
            logger.warning(
                "Delete purge batch deferred for appliance %s (%s): %s",
                appliance_id,
                label,
                exc,
            )
            time.sleep(2.0)
            continue
        if n <= 0:
            break
        deleted_batches += 1
        deleted_rows += n
        if deleted_batches == 1 or deleted_batches % 25 == 0:
            logger.info(
                "Delete purge appliance %s (%s): %s rows in %s batches (%.0fs)",
                appliance_id,
                label,
                deleted_rows,
                deleted_batches,
                time.time() - started,
            )
        time.sleep(_BATCH_PAUSE_SEC)
    logger.info(
        "Finished history purge for appliance %s (%s): %s rows, %s batches, %.0fs",
        appliance_id,
        label,
        deleted_rows,
        deleted_batches,
        time.time() - started,
    )


def _run_purge(appliance_id: int, label: str) -> None:
    try:
        logger.info("Starting async delete for appliance %s (%s)", appliance_id, label)
        # Drop the appliance identity first so the UI/API stay clean even if
        # multi‑GB history takes a long time to erase.
        db.detach_appliance_identity(appliance_id, label=label)
        logger.info("Detached appliance row %s (%s); purging history", appliance_id, label)
        _purge_metric_history(appliance_id, label)
        db.finalize_appliance_delete(appliance_id)
        db.clear_metric_purge_queue(appliance_id)
        logger.info("Finished async delete for appliance %s (%s)", appliance_id, label)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Async delete failed for appliance %s (%s)", appliance_id, label)
        try:
            db.mark_appliance_delete_failed(appliance_id, str(exc))
        except Exception:  # noqa: BLE001
            logger.debug("mark_appliance_delete_failed skipped", exc_info=True)
        try:
            db.add_notification(
                kind="appliance_delete_failed",
                title="Appliance removal failed",
                message=(
                    f'Could not finish removing "{label}". '
                    f"Retry Remove if it reappears, or check server logs. "
                    f"Error: {exc}"
                )[:1800],
                appliance_id=appliance_id,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Could not record delete-failure notification")
    finally:
        with _lock:
            _threads.pop(appliance_id, None)


def _run_orphan_purge(appliance_id: int, label: str) -> None:
    try:
        logger.info("Purging queued metric history for appliance_id=%s (%s)", appliance_id, label)
        _purge_metric_history(appliance_id, label)
        db.clear_metric_purge_queue(appliance_id)
        logger.info("Finished queued history purge for appliance_id=%s", appliance_id)
    except Exception:  # noqa: BLE001
        logger.exception("Queued purge failed for appliance_id=%s", appliance_id)
    finally:
        with _lock:
            _orphan_threads.pop(appliance_id, None)


def start_appliance_delete(appliance_id: int, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ensure a background purge thread is running for this appliance."""
    label = _label(meta or {"id": appliance_id})
    with _lock:
        existing = _threads.get(appliance_id)
        if existing and existing.is_alive():
            return {
                "accepted": False,
                "already_running": True,
                "appliance_id": appliance_id,
                "label": label,
            }
        thread = threading.Thread(
            target=_run_purge,
            args=(appliance_id, label),
            name=f"cm-delete-{appliance_id}",
            daemon=True,
        )
        _threads[appliance_id] = thread
        thread.start()
        return {
            "accepted": True,
            "already_running": False,
            "appliance_id": appliance_id,
            "label": label,
        }


def resume_pending_deletes() -> int:
    """Re-queue deletes interrupted by a process restart (+ queued history purges)."""
    pending = db.list_delete_pending_appliances()
    n = 0
    for row in pending:
        start_appliance_delete(int(row["id"]), row)
        n += 1
    try:
        queued = db.list_metric_purge_queue()
    except Exception:  # noqa: BLE001
        logger.debug("list_metric_purge_queue failed", exc_info=True)
        queued = []
    with _lock:
        for row in queued:
            aid = int(row["appliance_id"])
            label = row.get("label") or f"#{aid}"
            if aid in _threads and _threads[aid].is_alive():
                continue
            if aid in _orphan_threads and _orphan_threads[aid].is_alive():
                continue
            # If still in appliances as delete_pending, start_appliance_delete handles it.
            if any(int(p["id"]) == aid for p in pending):
                continue
            thread = threading.Thread(
                target=_run_orphan_purge,
                args=(aid, label),
                name=f"cm-orphan-purge-{aid}",
                daemon=True,
            )
            _orphan_threads[aid] = thread
            thread.start()
            n += 1
            logger.info("Resumed queued history purge for appliance_id=%s", aid)
    if n:
        logger.info("Resumed %s pending appliance delete/purge job(s)", n)
    return n


def ensure_started() -> None:
    """Idempotent: resume any pending deletes once per process."""
    global _started
    with _lock:
        if _started:
            return
        _started = True
    try:
        resume_pending_deletes()
    except Exception:  # noqa: BLE001
        logger.exception("resume_pending_deletes failed")
