"""Overview at-a-glance dashboard."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _named_series,
)


def build_overview(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Custom at-a-glance dashboard (not from Thales Grafana examples)."""
    import time as _time

    mem_total = store.gauge_value("node_memory_MemTotal_bytes")
    mem_avail = store.gauge_value("node_memory_MemAvailable_bytes")
    mem_use = None
    if mem_total and mem_avail is not None and mem_total > 0:
        mem_use = (1 - mem_avail / mem_total) * 100

    fs_size = store.sum_value("node_filesystem_size_bytes")
    fs_free = store.sum_value("node_filesystem_free_bytes")
    disk_use = None
    if fs_size > 0:
        disk_use = (1 - fs_free / fs_size) * 100

    # CPU utilization ≈ 1 - idle share (same approach as Host dashboard)
    cpu_use = None
    idle_rate = store.rate("node_cpu_seconds_total", {"mode": "idle"})
    # Sum rates across all modes/cpus for a rough busy fraction when possible
    cpu_samples = [s for s in store.latest_samples() if s.name == "node_cpu_seconds_total"]
    if cpu_samples:
        # Prefer irate-style: average non-idle fraction from stored history
        modes = {s.labels.get("mode") for s in cpu_samples}
        if "idle" in modes:
            # Estimate: for each cpu, rate(idle) / sum(rate(all modes)) is hard without
            # per-cpu grouping; use 1 - avg idle rate across series vs total capacity.
            # Simpler: use Host-style 1 - avg(idle rate) when idle rates exist.
            idle_series = store.series_by_name(
                "node_cpu_seconds_total",
                {"mode": "idle"},
                since=_time.time() - 300,
                limit_series=64,
            )
            idle_rates = []
            for item in idle_series:
                pts = item.get("points") or []
                if len(pts) < 2:
                    continue
                dt = pts[-1]["t"] - pts[-2]["t"]
                if dt > 0:
                    idle_rates.append((pts[-1]["v"] - pts[-2]["v"]) / dt)
            if idle_rates:
                # Each idle rate is ~0..1 cores idle; average idle fraction ≈ mean(idle_rates)
                # when each series is one CPU. Clamp to 0..100%.
                avg_idle = sum(idle_rates) / len(idle_rates)
                cpu_use = max(0.0, min(100.0, (1.0 - avg_idle) * 100.0))

    now = store.gauge_value("node_time_seconds")
    boot = store.gauge_value("node_boot_time_seconds")
    if now is None:
        now = _time.time()
    uptime = (now - boot) if boot is not None else None

    # Prometheus DEKs cover all domains on the appliance. REST /vault/keys2 is
    # scoped to the logged-in (root) domain only — do not use it for Total Keys.
    has_deks = any(s.name == "ciphertrust_key_vault_deks_total" for s in store.latest_samples())
    keys = store.sum_value("ciphertrust_key_vault_deks_total") if has_deks else None
    users = store.gauge_value("ciphertrust_user_management_total_users")
    subdomains = store.gauge_value("ciphertrust_license_manager_number_of_subdomains")
    hsm = store.gauge_value("ciphertrust_hsm_active_sessions")

    # Identity + version — prefer user-facing display_name, then CM /v1/system/info name.
    cm_name = (appliance or {}).get("cm_name") or None
    cm_version = (appliance or {}).get("cm_version") or None
    cm_model = (appliance or {}).get("cm_model") or None
    cm_uptime = ((appliance or {}).get("cm_uptime") or "").strip() or None
    display_name = None
    host = None
    if appliance:
        host = (appliance.get("host") or "").replace("https://", "").replace("http://", "") or None
        display_name = (appliance.get("display_name") or "").strip() or None
        # Prefer renamed label in the UI; fall back to CM-reported name, then connect host.
        if not display_name:
            display_name = cm_name or host
        elif cm_name and display_name != cm_name:
            # Keep CM hostname visible when the user renamed the node.
            pass

    ops = (appliance or {}).get("ops_snapshot") or {}
    users_ops = ops.get("users") if isinstance(ops, dict) else None
    if not isinstance(users_ops, dict):
        users_ops = {}
    top_logins = users_ops.get("top_recent_logins") or []
    api_users = users_ops.get("total")
    # Prefer API user total when available; Prometheus gauge is the fallback.
    users_total = float(api_users) if api_users is not None else users

    login_bar = [
        {
            "label": (r.get("username") or r.get("name") or "?")[:24],
            "value": float(r.get("logins_count") or 0),
        }
        for r in top_logins
    ]
    util_bar = [
        {"label": k, "value": float(v)}
        for k, v in (
            ("CPU", cpu_use),
            ("Memory", mem_use),
            ("Disk", disk_use),
        )
        if v is not None
    ]

    # Prefer CM /v1/system/info uptime string; fall back to Prometheus host uptime.
    uptime_panel = (
        _stat("Uptime", cm_uptime)
        if cm_uptime
        else _stat("Uptime", uptime, "duration")
    )

    panels: list[dict[str, Any]] = [
        _stat("Name", display_name),
        _stat("CM Hostname", cm_name or host),
        _stat("Connect Host", host),
        _stat("CM Version", cm_version),
        _stat("Model", cm_model),
        _stat("Total Keys", keys),
        _stat("Total Users", users_total, description=users_ops.get("error") or ""),
        _stat("Domains", subdomains),
        _stat("HSM Sessions", hsm),
        _stat("CPU Utilization", cpu_use, "%"),
        _stat("Memory Utilization", mem_use, "%"),
        _stat("Disk Utilization", disk_use, "%"),
        uptime_panel,
        _bar("Host Utilization", util_bar, "%", "Current CPU / memory / disk usage"),
        _bar(
            "Top 5 Users by Logins",
            login_bar,
            "",
            "Ranked by logins_count (root domain)",
        ),
        _timeseries(
            "Memory Available",
            _named_series(store, "node_memory_MemAvailable_bytes", limit=1),
            "bytes",
        ),
        _timeseries(
            "HTTP Requests (rate)",
            _named_series(
                store,
                "http_response_time_seconds_count",
                rate=True,
                limit=8,
                label_keys=["method", "path"],
            ),
            "req/s",
        ),
        _timeseries(
            "HSM Active Sessions",
            _named_series(store, "ciphertrust_hsm_active_sessions", limit=1),
            "",
        ),
        _timeseries(
            "Network Receive",
            _named_series(
                store,
                "node_network_receive_bytes_total",
                rate=True,
                limit=4,
                label_keys=["device"],
            ),
            "B/s",
        ),
    ]
    return panels
