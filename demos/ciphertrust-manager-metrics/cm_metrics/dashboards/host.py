"""Host, services, TCP, and database dashboards."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _pct,
    _bytes_to_gb,
    _named_series,
    _fmt_duration_seconds,
    _container_cpu_pct
)

def build_host(store: ApplianceStore) -> list[dict[str, Any]]:
    now = store.gauge_value("node_time_seconds")
    boot = store.gauge_value("node_boot_time_seconds")
    uptime = (now - boot) if now is not None and boot is not None else None
    mem_total = store.gauge_value("node_memory_MemTotal_bytes")
    mem_avail = store.gauge_value("node_memory_MemAvailable_bytes")
    mem_use = _pct((1 - mem_avail / mem_total) if mem_total and mem_avail is not None else None)
    fs_size = store.sum_value("node_filesystem_size_bytes")
    fs_free = store.sum_value("node_filesystem_free_bytes")
    disk_use = _pct((1 - fs_free / fs_size) if fs_size else None)
    cpus = len({s.labels.get("cpu") for s in store.latest_samples() if s.name == "node_cpu_seconds_total"})
    tcp = store.gauge_value("node_netstat_Tcp_CurrEstab")

    return [
        _stat("Uptime", uptime, "duration"),
        _stat("Processors", float(cpus) if cpus else None),
        _stat("RAM", _bytes_to_gb(mem_total), "GiB"),
        _stat("Memory Use", mem_use, "%"),
        _stat("Disk Usage", disk_use, "%"),
        _stat("TCP Established", tcp),
        _stat("Net IN (approx rate)", store.rate("node_network_receive_bytes_total"), "B/s"),
        _stat("Net OUT (approx rate)", store.rate("node_network_transmit_bytes_total"), "B/s"),
        _timeseries(
            "Network Receive Bytes",
            _named_series(store, "node_network_receive_bytes_total", rate=True, label_keys=["device"]),
            "B/s",
        ),
        _timeseries(
            "Network Transmit Bytes",
            _named_series(store, "node_network_transmit_bytes_total", rate=True, label_keys=["device"]),
            "B/s",
        ),
        _timeseries(
            "Disk Read Bytes",
            _named_series(store, "node_disk_read_bytes_total", rate=True, label_keys=["device"]),
            "B/s",
        ),
        _timeseries(
            "Disk Write Bytes",
            _named_series(store, "node_disk_written_bytes_total", rate=True, label_keys=["device"]),
            "B/s",
        ),
        _timeseries(
            "CPU Seconds by Mode (rate)",
            _named_series(store, "node_cpu_seconds_total", rate=True, limit=12, label_keys=["cpu", "mode"]),
            "cores",
        ),
    ]



def build_services(store: ApplianceStore) -> list[dict[str, Any]]:
    import time as _time

    now = _time.time()
    starts = {
        s.labels.get("name", "?"): s.value
        for s in store.latest_samples()
        if s.name == "docker_container_start_time_seconds" and s.labels.get("name")
    }
    running = {
        s.labels.get("name", "?"): s.value
        for s in store.latest_samples()
        if s.name == "docker_container_running_state" and s.labels.get("name")
    }
    restarts = {
        s.labels.get("name", "?"): s.value
        for s in store.latest_samples()
        if s.name == "docker_container_restart_count" and s.labels.get("name")
    }
    memory = {
        s.labels.get("name", "?"): s.value
        for s in store.latest_samples()
        if s.name == "docker_container_memory_used_bytes" and s.labels.get("name")
    }

    names = sorted(set(starts) | set(running) | set(memory))
    status_rows = []
    cpu_items = []
    mem_items = []
    uptime_items = []
    for name in names:
        start = starts.get(name)
        uptime = (now - start) if start is not None and start > 0 else None
        is_running = running.get(name, 0) >= 1
        cpu = _container_cpu_pct(store, name)
        mem_mib = (memory[name] / (1024**2)) if name in memory else None
        status_rows.append(
            {
                "service": name,
                "running": "yes" if is_running else "no",
                "uptime": _fmt_duration_seconds(uptime),
                "uptime_seconds": round(uptime, 1) if uptime is not None else None,
                "cpu_pct": round(cpu, 2) if cpu is not None else None,
                "memory_mib": round(mem_mib, 1) if mem_mib is not None else None,
                "restarts": int(restarts.get(name, 0)),
            }
        )
        if cpu is not None:
            cpu_items.append({"label": name, "value": round(cpu, 2)})
        if mem_mib is not None:
            mem_items.append({"label": name, "value": round(mem_mib, 1)})
        if uptime is not None:
            uptime_items.append({"label": name, "value": round(uptime, 0)})

    # Sort status by name; charts by value desc
    status_rows.sort(key=lambda r: r["service"])
    cpu_items.sort(key=lambda x: -x["value"])
    mem_items.sort(key=lambda x: -x["value"])

    running_count = sum(1 for r in status_rows if r["running"] == "yes")
    return [
        _stat("Services / Containers", float(len(names))),
        _stat("Running", float(running_count)),
        _stat("Stopped", float(len(names) - running_count)),
        {
            "type": "table",
            "title": "Service Status",
            "description": "docker_container_start_time_seconds / running_state / restart_count",
            "columns": ["service", "running", "uptime", "cpu_pct", "memory_mib", "restarts"],
            "rows": status_rows,
        },
        _bar("Container CPU %", cpu_items[:25], "%", "used/capacity from docker_container_cpu_*_total"),
        _bar("Container Memory", mem_items[:25], "MiB", "docker_container_memory_used_bytes"),
        _timeseries(
            "Container Memory Over Time",
            _named_series(store, "docker_container_memory_used_bytes", label_keys=["name"], limit=15),
            "B",
        ),
        _timeseries(
            "Network In (rate)",
            _named_series(
                store,
                "docker_container_network_in_bytes",
                rate=True,
                label_keys=["name"],
                limit=12,
            ),
            "B/s",
        ),
        _timeseries(
            "Network Out (rate)",
            _named_series(
                store,
                "docker_container_network_out_bytes",
                rate=True,
                label_keys=["name"],
                limit=12,
            ),
            "B/s",
        ),
        _timeseries(
            "Disk Read (rate)",
            _named_series(
                store,
                "docker_container_disk_read_bytes",
                rate=True,
                label_keys=["name"],
                limit=12,
            ),
            "B/s",
        ),
        _timeseries(
            "Disk Write (rate)",
            _named_series(
                store,
                "docker_container_disk_write_bytes",
                rate=True,
                label_keys=["name"],
                limit=12,
            ),
            "B/s",
        ),
        _timeseries(
            "Process Resident Memory (by service)",
            _named_series(store, "process_resident_memory_bytes", label_keys=["service"], limit=15),
            "B",
        ),
    ]



def build_tcp(store: ApplianceStore) -> list[dict[str, Any]]:
    # Per-port series from CM's tcp-connections-exporter (not present on all appliances).
    active = [s for s in store.latest_samples() if s.name == "active_tcp_connections"]
    by_port: dict[str, float] = {}
    for s in active:
        port = s.labels.get("port", "?")
        by_port[port] = by_port.get(port, 0.0) + s.value
    port_items = [
        {"label": f"port {k}", "value": v}
        for k, v in sorted(by_port.items(), key=lambda x: -x[1])
    ]
    active_total = sum(s.value for s in active) if active else None

    # Host-level TCP (node exporter) — available on both appliances.
    established = store.gauge_value("node_netstat_Tcp_CurrEstab")
    tcp_inuse = store.gauge_value("node_sockstat_TCP_inuse")
    tcp_alloc = store.gauge_value("node_sockstat_TCP_alloc")
    tcp_orphan = store.gauge_value("node_sockstat_TCP_orphan")
    tcp_tw = store.gauge_value("node_sockstat_TCP_tw")
    active_opens = store.rate("node_netstat_Tcp_ActiveOpens")
    passive_opens = store.rate("node_netstat_Tcp_PassiveOpens")
    retrans = store.rate("node_netstat_Tcp_RetransSegs")
    in_segs = store.rate("node_netstat_Tcp_InSegs")
    out_segs = store.rate("node_netstat_Tcp_OutSegs")

    return [
        _stat("Active TCP Total (by port)", active_total),
        _stat("TCP Established", established),
        _stat("TCP Sockets In Use", tcp_inuse),
        _stat("TCP Allocated", tcp_alloc),
        _stat("TCP Orphans", tcp_orphan),
        _stat("TIME_WAIT", tcp_tw),
        _stat("Active Opens /s", active_opens, "conn/s"),
        _stat("Passive Opens /s", passive_opens, "conn/s"),
        _bar("Active TCP by Port", port_items),
        _timeseries(
            "Active TCP Connections (by port)",
            _named_series(
                store,
                "active_tcp_connections",
                label_keys=["port", "network_interface_name"],
            ),
        ),
        _timeseries(
            "TCP Established",
            _named_series(store, "node_netstat_Tcp_CurrEstab"),
        ),
        _timeseries(
            "TCP Sockets In Use",
            _named_series(store, "node_sockstat_TCP_inuse"),
        ),
        _timeseries(
            "TCP Segment Rate",
            [
                *_named_series(store, "node_netstat_Tcp_InSegs", rate=True),
                *_named_series(store, "node_netstat_Tcp_OutSegs", rate=True),
                *_named_series(store, "node_netstat_Tcp_RetransSegs", rate=True),
            ],
            "seg/s",
        ),
        _timeseries(
            "TCP Connection Opens",
            [
                *_named_series(store, "node_netstat_Tcp_ActiveOpens", rate=True),
                *_named_series(store, "node_netstat_Tcp_PassiveOpens", rate=True),
            ],
            "conn/s",
        ),
    ]



def build_database(store: ApplianceStore) -> list[dict[str, Any]]:
    """SQL connection pool and query timing across CM microservices."""
    has_sql = any(s.name.startswith("sql_") for s in store.latest_samples())
    open_c = store.sum_value("sql_open_connections") if has_sql else None
    in_use = store.sum_value("sql_in_use_connections") if has_sql else None
    idle = store.sum_value("sql_idle_connections") if has_sql else None
    errors = store.sum_value("sql_errors") if has_sql else None
    wait = store.sum_value("sql_wait_count") if has_sql else None
    exec_cnt = store.rate("sql_execution_time_seconds_count") if has_sql else None

    return [
        _stat("Open Connections", open_c),
        _stat("In Use", in_use),
        _stat("Idle", idle),
        _stat("SQL Errors", errors),
        _stat("Wait Count", wait),
        _stat("Executions /s", exec_cnt, "ops/s"),
        _bar("Open Connections by DB", store.group_by_label("sql_open_connections", "db")),
        _bar("Open Connections by Service", store.group_by_label("sql_open_connections", "service")),
        _bar("In-Use by Service", store.group_by_label("sql_in_use_connections", "service")),
        _bar("Idle by DB", store.group_by_label("sql_idle_connections", "db")),
        _timeseries(
            "SQL Executions",
            _named_series(store, "sql_execution_time_seconds_count", rate=True, label_keys=["service", "db"], limit=12),
            "ops/s",
        ),
        _timeseries(
            "SQL Errors Over Time",
            _named_series(store, "sql_errors", label_keys=["service", "db"], limit=10),
        ),
        _timeseries(
            "SQL Wait Count",
            _named_series(store, "sql_wait_count", label_keys=["service", "db"], limit=10),
        ),
    ]


