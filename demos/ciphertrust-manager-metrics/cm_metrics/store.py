"""In-memory + SQLite-backed multi-appliance metrics store."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from . import db
from .config import Config
from .parser import Sample, find_samples, first_value, labels_match, sum_samples


@dataclass
class Snapshot:
    timestamp: float
    samples: list[Sample]
    source: str = "live"
    error: str | None = None


def _series_maxlen(history_seconds: int) -> int:
    """Room for ~one point per scrape over the retention window, with headroom."""
    interval = max(1, int(Config.SCRAPE_INTERVAL))
    return max(50_000, int(history_seconds / interval) + 2_000)


# Cap DB reads for chart queries — never pull full multi‑GB history.
_SERIES_POINT_LIMIT = 10_000
_SERIES_CACHE_TTL = 45.0
_DEFAULT_SERIES_WINDOW = 3600.0  # 1h when caller omits since


def _series_point_limit(window_seconds: float) -> int:
    """Fewer raw points for long ranges — load_series also stratifies slices."""
    if window_seconds <= 3600:
        return _SERIES_POINT_LIMIT
    if window_seconds <= 6 * 3600:
        return 8_000
    if window_seconds <= 24 * 3600:
        return 6_000
    return 5_000


class ApplianceStore:
    def __init__(self, appliance_id: int, history_seconds: int) -> None:
        self.appliance_id = appliance_id
        self.history_seconds = history_seconds
        self._lock = threading.RLock()
        maxlen = _series_maxlen(history_seconds)
        self._series: dict[str, deque[tuple[float, float]]] = defaultdict(
            lambda: deque(maxlen=maxlen)
        )
        self._labels: dict[str, tuple[str, dict[str, str]]] = {}
        self._latest: Snapshot | None = None
        self._hydrated = False
        self._series_hydrated = False
        # Short-lived chart query cache: (name, since_bucket, limit, labels_key) -> (expires, results)
        self._series_query_cache: dict[tuple[Any, ...], tuple[float, list[dict[str, Any]]]] = {}
        # Raw DB rows before label filtering — shared across panels that query the
        # same metric name/window with different label selectors.
        self._raw_series_cache: dict[tuple[Any, ...], tuple[float, list[dict[str, Any]]]] = {}

    def hydrate_from_db(self) -> None:
        """Load latest gauges only. Full series history is queried on demand."""
        self.hydrate_latest_only()

    def hydrate_latest_only(self) -> None:
        """Mark store ready without scanning multi‑GB metric_points.

        Latest gauges come from live scrapes into ``_latest``. Chart history is
        loaded on demand via scoped ``series_by_name`` queries. A full
        ``load_latest_samples`` over a huge DB was multi‑minute and blocked
        every dashboard request after restart.
        """
        if self._hydrated:
            return
        self._hydrated = True

    def ensure_series_hydrated(self) -> None:
        """No-op. Charts use scoped per-metric DB queries instead of bulk hydrate."""
        self._series_hydrated = True

    def ingest(
        self,
        samples: list[Sample],
        source: str = "live",
        error: str | None = None,
        persist: bool = True,
    ) -> None:
        now = time.time()
        persist_rows: list[tuple[str, str, dict[str, str], float, float]] = []
        with self._lock:
            self._latest = Snapshot(timestamp=now, samples=samples, source=source, error=error)
            cutoff = now - self.history_seconds
            for sample in samples:
                fp = sample.fingerprint
                self._series[fp].append((now, sample.value))
                self._labels[fp] = (sample.name, sample.labels)
                while self._series[fp] and self._series[fp][0][0] < cutoff:
                    self._series[fp].popleft()
                persist_rows.append((fp, sample.name, sample.labels, now, sample.value))
            self._pending_persist = (source, persist_rows)
            # New scrape invalidates cached chart windows.
            self._series_query_cache.clear()
            self._raw_series_cache.clear()
        # Persist outside the store lock — chunked SQLite writes must not block
        # concurrent series_by_name / gauge reads on this appliance.
        if persist:
            self._persist_rows(source, persist_rows)

    def persist_last_ingest(self) -> None:
        """Flush rows from the last ingest(persist=False) to SQLite."""
        with self._lock:
            pending = getattr(self, "_pending_persist", None)
            if not pending:
                return
            source, persist_rows = pending
            self._pending_persist = None
        self._persist_rows(source, persist_rows)

    def _persist_rows(
        self,
        source: str,
        persist_rows: list[tuple[str, str, dict[str, str], float, float]],
    ) -> None:
        if not persist_rows or source not in {"live", "demo"}:
            return
        skip_prefixes = ("dummy_",)
        skip_suffixes = ("_bucket",)  # histogram buckets explode cardinality
        to_store = [
            r
            for r in persist_rows
            if not r[1].startswith(skip_prefixes) and not r[1].endswith(skip_suffixes)
        ]
        if to_store:
            db.insert_metric_points(self.appliance_id, to_store)

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        *,
        persist: bool = True,
    ) -> None:
        """Append one synthetic gauge point (e.g. vault API key total) into history."""
        sample = Sample(name=name, labels=dict(labels or {}), value=float(value))
        now = time.time()
        with self._lock:
            fp = sample.fingerprint
            self._series[fp].append((now, sample.value))
            self._labels[fp] = (sample.name, sample.labels)
            cutoff = now - self.history_seconds
            while self._series[fp] and self._series[fp][0][0] < cutoff:
                self._series[fp].popleft()
            # Merge into latest snapshot so gauges/sum_value can see it too.
            if self._latest:
                samples = [s for s in self._latest.samples if s.fingerprint != fp]
                samples.append(sample)
                self._latest = Snapshot(
                    timestamp=now,
                    samples=samples,
                    source=self._latest.source,
                    error=self._latest.error,
                )
            else:
                self._latest = Snapshot(timestamp=now, samples=[sample], source="derived")
            self._series_query_cache.clear()
            self._raw_series_cache.clear()
        if persist:
            db.insert_metric_points(
                self.appliance_id,
                [(fp, sample.name, sample.labels, now, sample.value)],
            )

    def latest_samples(self) -> list[Sample]:
        with self._lock:
            return list(self._latest.samples) if self._latest else []

    def latest_snapshot(self) -> Snapshot | None:
        with self._lock:
            return self._latest

    def series_by_name(
        self,
        name: str,
        labels: dict[str, str] | None = None,
        since: float | None = None,
        limit_series: int = 20,
    ) -> list[dict[str, Any]]:
        """Return time series for one metric, scoped to the requested window.

        Loads only ``metric_name`` (+ ``since``) from SQLite via the name index —
        never bulk-hydrates multi‑GB history.
        """
        now = time.time()
        effective_since = float(since) if since is not None else (now - _DEFAULT_SERIES_WINDOW)
        window = max(0.0, now - effective_since)
        point_limit = _series_point_limit(window)
        labels_key = tuple(sorted((labels or {}).items()))
        # Bucket ``since`` so adjacent panel calls share a cache entry.
        since_bucket = int(effective_since // 10) * 10
        cache_key = (name, since_bucket, int(limit_series), point_limit, labels_key)

        with self._lock:
            cached = self._series_query_cache.get(cache_key)
            if cached and cached[0] > now:
                return cached[1]

        raw_key = (name, since_bucket, point_limit)
        rows: list[dict[str, Any]] | None = None
        with self._lock:
            raw_cached = self._raw_series_cache.get(raw_key)
            if raw_cached and raw_cached[0] > now:
                rows = raw_cached[1]
        if rows is None:
            rows = db.load_series(
                self.appliance_id,
                metric_name=name,
                since=effective_since,
                until=now,
                limit=point_limit,
            )
            with self._lock:
                self._raw_series_cache[raw_key] = (now + _SERIES_CACHE_TTL, rows)
                if len(self._raw_series_cache) > 40:
                    expired = [k for k, (exp, _) in self._raw_series_cache.items() if exp <= now]
                    for key in expired:
                        self._raw_series_cache.pop(key, None)

        by_fp: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not labels_match(row["labels"], labels):
                continue
            fp = row["fingerprint"]
            entry = by_fp.get(fp)
            if entry is None:
                by_fp[fp] = {
                    "fingerprint": fp,
                    "name": row["name"],
                    "labels": row["labels"],
                    "points": [{"t": row["t"], "v": row["v"]}],
                }
            else:
                entry["points"].append({"t": row["t"], "v": row["v"]})

        with self._lock:
            # Merge live in-memory points (newer than DB / not yet flushed).
            for fp, (metric_name, metric_labels) in self._labels.items():
                if metric_name != name:
                    continue
                if not labels_match(metric_labels, labels):
                    continue
                mem_pts = [
                    {"t": t, "v": v}
                    for t, v in self._series.get(fp, ())
                    if t >= effective_since
                ]
                if not mem_pts and fp not in by_fp:
                    continue
                if fp in by_fp:
                    existing_ts = {p["t"] for p in by_fp[fp]["points"]}
                    for p in mem_pts:
                        if p["t"] not in existing_ts:
                            by_fp[fp]["points"].append(p)
                    by_fp[fp]["points"].sort(key=lambda p: p["t"])
                else:
                    by_fp[fp] = {
                        "fingerprint": fp,
                        "name": metric_name,
                        "labels": metric_labels,
                        "points": mem_pts,
                    }

            # Latest-snapshot fallback when DB has nothing yet for this metric.
            if not by_fp and self._latest:
                matched = [
                    s
                    for s in self._latest.samples
                    if s.name == name and labels_match(s.labels, labels)
                ][:limit_series]
                for sample in matched:
                    pts = [
                        {"t": t, "v": v}
                        for t, v in self._series.get(sample.fingerprint, ())
                        if t >= effective_since
                    ]
                    by_fp[sample.fingerprint] = {
                        "fingerprint": sample.fingerprint,
                        "name": sample.name,
                        "labels": sample.labels,
                        "points": pts,
                        "value": sample.value,
                    }

            ranked = sorted(
                by_fp.values(),
                key=lambda item: item["points"][-1]["t"] if item.get("points") else 0.0,
                reverse=True,
            )[:limit_series]
            results: list[dict[str, Any]] = []
            for item in ranked:
                pts = item.get("points") or []
                if "value" not in item:
                    item["value"] = pts[-1]["v"] if pts else None
                results.append(item)

            self._series_query_cache[cache_key] = (now + _SERIES_CACHE_TTL, results)
            if len(self._series_query_cache) > 80:
                expired = [k for k, (exp, _) in self._series_query_cache.items() if exp <= now]
                for key in expired:
                    self._series_query_cache.pop(key, None)
            return results

    def gauge_value(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        return first_value(self.latest_samples(), name, labels)

    def uptime_seconds(self) -> float | None:
        """Host uptime from node_time_seconds − node_boot_time_seconds, if available."""
        now = self.gauge_value("node_time_seconds")
        boot = self.gauge_value("node_boot_time_seconds")
        if now is None:
            now = time.time()
        if boot is None:
            return None
        up = float(now) - float(boot)
        return up if up >= 0 else None

    def sum_value(self, name: str, labels: dict[str, str] | None = None) -> float:
        return sum_samples(self.latest_samples(), name, labels)

    def rate(
        self,
        name: str,
        labels: dict[str, str] | None = None,
        window_seconds: float = 60.0,
    ) -> float | None:
        series_list = self.series_by_name(name, labels, since=time.time() - window_seconds * 3)
        if not series_list:
            return None
        total_rate = 0.0
        any_points = False
        now = time.time()
        for item in series_list:
            pts = item["points"]
            if len(pts) < 2:
                continue
            window_pts = [p for p in pts if p["t"] >= now - window_seconds]
            if len(window_pts) < 2:
                window_pts = pts[-2:]
            dt = window_pts[-1]["t"] - window_pts[0]["t"]
            if dt <= 0:
                continue
            total_rate += (window_pts[-1]["v"] - window_pts[0]["v"]) / dt
            any_points = True
        return total_rate if any_points else None

    def increase(
        self,
        name: str,
        labels: dict[str, str] | None = None,
        window_seconds: float = 60.0,
    ) -> float | None:
        rate = self.rate(name, labels, window_seconds)
        if rate is None:
            return None
        return rate * window_seconds

    def group_by_label(
        self,
        name: str,
        group_label: str,
        labels: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        samples = find_samples(self.latest_samples(), name, labels)
        buckets: dict[str, float] = defaultdict(float)
        for sample in samples:
            key = sample.labels.get(group_label, "unknown")
            buckets[key] += sample.value
        return [{"label": k, "value": v} for k, v in sorted(buckets.items(), key=lambda x: -x[1])]


class MetricsStore:
    """Registry of per-appliance stores."""

    def __init__(self, history_seconds: int | None = None) -> None:
        self.history_seconds = history_seconds or Config.HISTORY_SECONDS
        self._lock = threading.RLock()
        self._stores: dict[int, ApplianceStore] = {}

    def for_appliance(self, appliance_id: int, *, hydrate: bool = True) -> ApplianceStore:
        with self._lock:
            store = self._stores.get(appliance_id)
            if store is None:
                store = ApplianceStore(appliance_id, self.history_seconds)
                self._stores[appliance_id] = store
        # Hydrate outside the registry lock. Scrapes pass hydrate=False so a
        # multi‑GB SQLite read cannot block status updates for minutes.
        if hydrate:
            store.hydrate_latest_only()
        return store

    def drop(self, appliance_id: int) -> None:
        with self._lock:
            self._stores.pop(appliance_id, None)

    def status_all(self) -> dict[str, Any]:
        appliances = db.list_appliances()
        return {
            "appliance_count": len(appliances),
            "scrape_interval": Config.SCRAPE_INTERVAL,
            "history_seconds": self.history_seconds,
            "appliances": [
                {
                    "id": a["id"],
                    "host": a["host"],
                    "display_name": a["display_name"],
                    "enabled": a["enabled"],
                    "last_status": a["last_status"],
                    "last_scrape_at": a["last_scrape_at"],
                    "last_error": a["last_error"],
                    "sample_count": a["sample_count"],
                    "fail_count": int(a.get("fail_count") or 0),
                    "is_clustered": a["is_clustered"],
                    "cluster_id": a.get("cluster_id"),
                }
                for a in appliances
            ],
        }
