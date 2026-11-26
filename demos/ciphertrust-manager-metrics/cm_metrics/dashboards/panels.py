"""Shared panel builders and metric helpers for dashboard boards."""

from __future__ import annotations

import re
import time
from collections import defaultdict
from contextvars import ContextVar
from typing import Any

from ..parser import find_samples
from ..store import ApplianceStore

# Active chart window for the current dashboard request (seconds). None = full history.
_dashboard_range_seconds: ContextVar[float | None] = ContextVar(
    "dashboard_range_seconds", default=None
)


def set_dashboard_range(seconds: float | None):
    """Bind the UI time-range for series helpers in this request."""
    return _dashboard_range_seconds.set(seconds)


def reset_dashboard_range(token) -> None:
    _dashboard_range_seconds.reset(token)


def _series_since() -> float | None:
    secs = _dashboard_range_seconds.get()
    if secs is None or secs <= 0:
        return None
    return time.time() - float(secs)


def _stat(
    title: str,
    value: float | str | None = None,
    unit: str = "",
    description: str = "",
    *,
    tone: str = "",
) -> dict[str, Any]:
    out_value: float | str | None
    if value is None:
        out_value = None
    elif isinstance(value, float):
        out_value = round(value, 4)
    else:
        out_value = value
    return {
        "type": "stat",
        "title": title,
        "description": description,
        "value": out_value,
        "unit": unit,
        "tone": (tone or "").lower(),
    }


def _note(text: str, *, title: str = "", tone: str = "") -> dict[str, Any]:
    """Full-width informational banner (e.g. domain-scope caveats).

    Optional tone: pass | warning | fail | info (UI accent only).
    """
    return {
        "type": "note",
        "title": title,
        "text": text,
        "tone": (tone or "").lower(),
        "wide": True,
        "span": 12,
    }


def _timeseries(
    title: str,
    series: list[dict[str, Any]],
    unit: str = "",
    description: str = "",
    *,
    wide: bool = False,
) -> dict[str, Any]:
    return {
        "type": "timeseries",
        "title": title,
        "description": description,
        "unit": unit,
        "series": series,
        "wide": wide,
    }


def _bar(
    title: str,
    items: list[dict[str, Any]],
    unit: str = "",
    description: str = "",
    *,
    wide: bool = False,
) -> dict[str, Any]:
    return {
        "type": "bar",
        "title": title,
        "description": description,
        "unit": unit,
        "items": items,
        "wide": wide,
    }


def _short_account_label(account: str) -> str:
    """Turn kylo:...:accounts:kylo-<uuid> into a short chart label."""
    if not account:
        return "unknown"
    if "accounts:" in account:
        account = account.rsplit("accounts:", 1)[-1]
    if account.startswith("kylo-") and len(account) > 16:
        return account[:13] + "…"
    if len(account) > 28:
        return account[:25] + "…"
    return account


def _domain_id_from_account(account: str) -> str | None:
    """Extract subdomain UUID from a key_vault account label, if present."""
    if not account:
        return None
    # e.g. kylo:kylo-<uuid>:admin:accounts:kylo-<uuid>
    m = re.search(
        r"kylo-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        account,
        flags=re.IGNORECASE,
    )
    return m.group(1).lower() if m else None


def _domain_name_map(store: ApplianceStore) -> dict[str, str]:
    """domain_id UUID -> domain_name from license-manager key_usage series."""
    id_to_name: dict[str, str] = {}
    for sample in find_samples(
        store.latest_samples(),
        "ciphertrust_license_manager_key_usage_count_including_subdomains",
    ):
        did = (sample.labels.get("domain_id") or "").strip().lower()
        dname = (sample.labels.get("domain_name") or "").strip()
        if did and dname:
            id_to_name[did] = dname
    return id_to_name


def _friendly_account_label(account: str, id_to_name: dict[str, str] | None = None) -> str:
    """Map account / account_uri to domain name when known; else root or short kylo id."""
    if not account:
        return "unknown"
    did = _domain_id_from_account(account)
    if did:
        if id_to_name and did in id_to_name:
            return id_to_name[did]
        # Unknown / deleted domain — keep a short id rather than the full URI
        return did[:8] + "…"
    # Root account: kylo:kylo:admin:accounts:kylo (no UUID)
    if "accounts:kylo" in account and "kylo-" not in account.split("accounts:", 1)[-1]:
        return "root"
    if account.endswith(":kylo") or account.rstrip("/").endswith("accounts:kylo"):
        return "root"
    return _short_account_label(account)


def _group_by_account_friendly(
    store: ApplianceStore,
    name: str,
    group_label: str = "account_uri",
    *,
    limit: int = 15,
    min_value: float = 0.0,
) -> list[dict[str, Any]]:
    """Group a metric by account label, resolving UUIDs to domain names when possible."""
    id_to_name = _domain_name_map(store)
    buckets: dict[str, float] = defaultdict(float)
    for sample in find_samples(store.latest_samples(), name):
        raw = sample.labels.get(group_label) or ""
        label = _friendly_account_label(raw, id_to_name)
        buckets[label] += float(sample.value)
    items = [
        {"label": k, "value": v}
        for k, v in sorted(buckets.items(), key=lambda x: -x[1])
        if v > min_value
    ]
    return items[:limit]


def _rename_account_series(
    series_list: list[dict[str, Any]],
    id_to_name: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Rewrite timeseries legend names that contain account_uri=… to friendly labels."""
    for series in series_list:
        raw = series.get("name") or ""
        if "account_uri=" in raw:
            uri = raw.split("account_uri=", 1)[-1]
            # Strip trailing ", other=…" if present
            uri = uri.split(",", 1)[0].strip()
            series["name"] = _friendly_account_label(uri, id_to_name)
        elif "account=" in raw:
            uri = raw.split("account=", 1)[-1].split(",", 1)[0].strip()
            series["name"] = _friendly_account_label(uri, id_to_name)
        else:
            series["name"] = _friendly_account_label(raw, id_to_name)
    return series_list


def _keys_by_domain_from_deks(
    store: ApplianceStore,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Domain key counts from DEKs (includes root). License-manager usage omits root.

    Maps account UUIDs to domain_name via
    ciphertrust_license_manager_key_usage_count_including_subdomains when available.
    """
    id_to_name = _domain_name_map(store)

    buckets: dict[str, float] = defaultdict(float)
    for sample in find_samples(store.latest_samples(), "ciphertrust_key_vault_deks_total"):
        account = sample.labels.get("account") or ""
        did = _domain_id_from_account(account)
        if did:
            label = id_to_name.get(did) or did
        else:
            # Root / default account has no UUID (kylo:kylo:admin:accounts:kylo)
            label = "root"
        buckets[label] += float(sample.value)

    items = [{"label": k, "value": v} for k, v in sorted(buckets.items(), key=lambda x: -x[1])]
    return items[:limit]


def _group_by_label_short(
    store: ApplianceStore,
    name: str,
    group_label: str,
    *,
    limit: int = 20,
    min_value: float = 0.0,
    shortener=None,
) -> list[dict[str, Any]]:
    items = store.group_by_label(name, group_label)
    out = []
    for item in items:
        if (item.get("value") or 0) <= min_value:
            continue
        label = item["label"]
        if shortener:
            label = shortener(label)
        out.append({"label": label, "value": item["value"]})
    return out[:limit]


def _layout_panels(panels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign grid spans so consecutive same-type panels fill rows evenly."""

    def _assign_stat_spans(group: list[dict[str, Any]]) -> None:
        count = len(group)
        if count == 1:
            group[0]["span"] = 12
            return
        if count == 2:
            for panel in group:
                panel["span"] = 6
            return
        if count == 5:
            for k, panel in enumerate(group):
                panel["span"] = 4 if k < 3 else 6
            return
        if count == 7:
            # 4 + 3: first row quarters, second row thirds
            for k, panel in enumerate(group):
                panel["span"] = 3 if k < 4 else 4
            return
        # Prefer complete rows of 4, else 3; stretch leftovers across the last row.
        if count % 4 == 0:
            per_row = 4
        elif count % 3 == 0:
            per_row = 3
        else:
            per_row = 4
        span = 12 // per_row
        for panel in group:
            panel["span"] = span
        rem = count % per_row
        if rem == 1:
            # Avoid a lonely card: pull last two into a half/half row
            if count >= 2:
                group[-2]["span"] = 6
                group[-1]["span"] = 6
        elif rem:
            each = 12 // rem
            for panel in group[-rem:]:
                panel["span"] = each

    def _assign_chart_spans(group: list[dict[str, Any]]) -> None:
        count = len(group)
        if count == 1:
            group[0]["span"] = 12
            group[0]["wide"] = True
            return
        for k, panel in enumerate(group):
            if panel.get("wide"):
                panel["span"] = 12
            elif count % 2 == 1 and k == count - 1:
                panel["span"] = 12
            else:
                panel["span"] = 6

    i = 0
    n = len(panels)
    while i < n:
        ptype = panels[i]["type"]
        j = i
        while j < n and panels[j]["type"] == ptype:
            j += 1
        group = panels[i:j]
        if ptype == "stat":
            _assign_stat_spans(group)
        elif ptype in ("timeseries", "bar"):
            _assign_chart_spans(group)
        else:
            for panel in group:
                panel["span"] = 12
                panel["wide"] = True
        i = j
    return panels


def _pct(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100


def _bytes_to_gb(value: float | None) -> float | None:
    if value is None:
        return None
    return value / (1024**3)



def _summed_series(
    store: ApplianceStore,
    name: str,
    labels: dict[str, str] | None = None,
    *,
    series_name: str = "Total",
    limit_series: int = 200,
) -> list[dict[str, Any]]:
    """Sum all matching labeled series into one timeseries (e.g. total keys over time).

    Per labeled series, keep only the last sample in each second so overlapping
    scrapes (Auto refresh + background loop) do not double-count.
    """
    raw = store.series_by_name(
        name, labels, since=_series_since(), limit_series=limit_series
    )
    if not raw:
        return []
    buckets: dict[float, float] = {}
    for item in raw:
        # Collapse duplicate timestamps within this series first (last wins).
        per_series: dict[float, float] = {}
        for pt in item.get("points") or []:
            key = round(float(pt["t"]))
            per_series[key] = float(pt["v"])
        for key, value in per_series.items():
            buckets[key] = buckets.get(key, 0.0) + value
    if not buckets:
        return []
    points = [{"t": float(t), "v": v} for t, v in sorted(buckets.items())]
    return [{"name": series_name, "points": points}]


def _summed_by_label_series(
    store: ApplianceStore,
    name: str,
    group_label: str,
    labels: dict[str, str] | None = None,
    *,
    limit_series: int = 200,
    max_groups: int = 12,
) -> list[dict[str, Any]]:
    """Sum matching series into one timeseries per distinct label value.

    Same per-second dedupe as ``_summed_series`` so Auto refresh + background
    scrapes do not double-count within a labeled group (e.g. algorithm).
    """
    raw = store.series_by_name(
        name, labels, since=_series_since(), limit_series=limit_series
    )
    if not raw:
        return []
    # group_key -> {second -> value}
    groups: dict[str, dict[float, float]] = {}
    for item in raw:
        labels_map = item.get("labels") or {}
        key = str(labels_map.get(group_label) or "unknown")
        per_series: dict[float, float] = {}
        for pt in item.get("points") or []:
            t = round(float(pt["t"]))
            per_series[t] = float(pt["v"])
        bucket = groups.setdefault(key, {})
        for t, value in per_series.items():
            bucket[t] = bucket.get(t, 0.0) + value
    if not groups:
        return []
    # Prefer groups with the highest latest value so charts stay readable.
    ranked = sorted(
        groups.items(),
        key=lambda kv: max(kv[1].values()) if kv[1] else 0.0,
        reverse=True,
    )[:max_groups]
    out: list[dict[str, Any]] = []
    for legend, buckets in ranked:
        points = [{"t": float(t), "v": v} for t, v in sorted(buckets.items())]
        out.append({"name": legend, "points": points})
    # Stable alphabetical legend order for the UI (after ranking/truncation).
    out.sort(key=lambda s: str(s["name"]).lower())
    return out


def _named_series(
    store: ApplianceStore,
    name: str,
    labels: dict[str, str] | None = None,
    rate: bool = False,
    limit: int = 10,
    label_keys: list[str] | None = None,
) -> list[dict[str, Any]]:
    raw = store.series_by_name(
        name, labels, since=_series_since(), limit_series=limit
    )
    skip_label_keys = {
        "otel_scope_name",
        "otel_scope_schema_url",
        "otel_scope_version",
        "job",
        "instance",
        "service",
        "component",
        "account_id",
        "access_id",
        "cluster_name",
    }
    out: list[dict[str, Any]] = []
    for item in raw:
        labels_map = item["labels"]
        if label_keys:
            legend = " / ".join(str(labels_map.get(k, "")) for k in label_keys if labels_map.get(k))
        else:
            preferred = [
                k
                for k in (
                    "name",
                    "akeyless",
                    "instance_id",
                    "port",
                    "device",
                    "operation",
                    "status",
                    "path",
                    "method",
                    "domain_name",
                    "db",
                    "feature",
                    "resource_type",
                )
                if k in labels_map
            ]
            if preferred:
                legend = " / ".join(str(labels_map[k]) for k in preferred[:2])
            else:
                parts = [
                    f"{k}={v}"
                    for k, v in labels_map.items()
                    if k not in skip_label_keys and not str(k).startswith("otel_")
                ][:2]
                legend = ", ".join(parts) if parts else item["name"]
        if not legend:
            legend = item["name"]
        # Keep legends short for UI tooltips
        if len(legend) > 48:
            legend = legend[:45] + "…"
        points = item["points"]
        if rate and len(points) >= 2:
            rate_points = []
            for i in range(1, len(points)):
                dt = points[i]["t"] - points[i - 1]["t"]
                if dt <= 0:
                    continue
                rate_points.append(
                    {"t": points[i]["t"], "v": (points[i]["v"] - points[i - 1]["v"]) / dt}
                )
            points = rate_points
        out.append({"name": legend, "points": points})
    return out


def _first_gauge(store: ApplianceStore, *names: str, labels: dict[str, str] | None = None) -> float | None:
    for name in names:
        val = store.gauge_value(name, labels)
        if val is not None:
            return val
    return None


def _first_sum(store: ApplianceStore, *names: str, labels: dict[str, str] | None = None) -> float:
    for name in names:
        # Prefer a name that actually exists in the latest scrape
        if any(s.name == name for s in store.latest_samples()):
            return store.sum_value(name, labels)
    return 0.0


def _first_rate(
    store: ApplianceStore,
    *names: str,
    labels: dict[str, str] | None = None,
    window_seconds: float = 60.0,
) -> float | None:
    for name in names:
        if any(s.name == name for s in store.latest_samples()):
            return store.rate(name, labels, window_seconds)
    return None


def _op_status_items(store: ApplianceStore, success_name: str, failure_name: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for s in store.latest_samples():
        if s.name == success_name:
            items.append({"label": f"{s.labels.get('operation', '?')}:success", "value": s.value})
        elif s.name == failure_name:
            items.append({"label": f"{s.labels.get('operation', '?')}:failed", "value": s.value})
    items.sort(key=lambda x: -x["value"])
    return items



def _fmt_duration_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    total = max(0, int(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours}h {mins}m"
    if hours > 0:
        return f"{hours}h {mins}m"
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"


def _container_cpu_pct(store: ApplianceStore, name: str) -> float | None:
    used = store.rate("docker_container_cpu_used_total", {"name": name})
    cap = store.rate("docker_container_cpu_capacity_total", {"name": name})
    if used is None or cap is None or cap <= 0:
        return None
    return max(0.0, min(100.0, (used / cap) * 100.0))


