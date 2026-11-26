"""CSM (CipherTrust Secrets Management / Akeyless) dashboard."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _named_series,
    _first_gauge,
    _first_rate
)

def build_secrets(store: ApplianceStore) -> list[dict[str, Any]]:
    cpu = _first_gauge(
        store,
        "akeyless_gw_system_cpu_usage_percent",
        "akeyless_gateway_cpu_utilization_percent",
    )
    # Some CM builds export this as a 0..1 fraction despite the "_percent" name.
    if cpu is not None and 0 <= cpu <= 1.5:
        cpu = cpu * 100.0

    mem = _first_gauge(
        store,
        "akeyless_gw_system_memory_usage_in_bytes",
        "akeyless_gateway_memory_utilization_percent",
    )
    # memory is bytes on current builds
    mem_unit = "B"
    if mem is not None and any(
        s.name == "akeyless_gateway_memory_utilization_percent" for s in store.latest_samples()
    ):
        mem_unit = "%"

    health = store.gauge_value("akeyless_gw_system_healthcheck_status")
    saas = store.gauge_value("akeyless_gw_system_saas_connection_status")
    tx_current = store.gauge_value("akeyless_gw_quota_current_transactions_number")
    tx_admin = store.gauge_value("akeyless_gw_quota_gw_admin_client_transactions")
    tx_limit = store.gauge_value("akeyless_gw_quota_total_transactions_limit")
    # Sentinel / unlimited quotas often show as max uint32
    if tx_limit is not None and tx_limit >= 4_000_000_000:
        tx_limit = None
    load_1m = store.gauge_value("akeyless_gw_system_cpu_load_average_1m")
    load_5m = store.gauge_value("akeyless_gw_system_cpu_load_average_5m")
    load_15m = store.gauge_value("akeyless_gw_system_cpu_load_average_15m")
    req_rate = _first_rate(
        store,
        "akeyless_gw_system_request_count_total",
        "akeyless_gateway_transactions_total",
    )

    cpu_series = _named_series(
        store, "akeyless_gw_system_cpu_usage_percent", label_keys=["akeyless"]
    ) or _named_series(store, "akeyless_gateway_cpu_utilization_percent")
    # Scale fraction series to percent for charts
    for series in cpu_series:
        pts = series.get("points") or []
        if pts and max(abs(p["v"]) for p in pts) <= 1.5:
            for p in pts:
                p["v"] = p["v"] * 100.0

    return [
        _stat("Gateway CPU", cpu, "%"),
        _stat("Gateway Memory", mem, mem_unit),
        _stat("Healthcheck", health),
        _stat("SaaS Connection", saas),
        _stat("Current Transactions", tx_current),
        _stat("Admin Client Transactions", tx_admin),
        _stat("Transaction Limit", tx_limit),
        _stat("Load Avg 1m", load_1m),
        _stat("Load Avg 5m", load_5m),
        _stat("Load Avg 15m", load_15m),
        _stat("Request Rate", req_rate, "req/s"),
        _timeseries("Gateway CPU %", cpu_series, "%"),
        _timeseries(
            "Gateway Memory",
            _named_series(store, "akeyless_gw_system_memory_usage_in_bytes", label_keys=["akeyless"]),
            "B",
        ),
        _timeseries(
            "CPU Load Average",
            [
                *_named_series(store, "akeyless_gw_system_cpu_load_average_1m", label_keys=["akeyless"]),
                *_named_series(store, "akeyless_gw_system_cpu_load_average_5m", label_keys=["akeyless"]),
                *_named_series(store, "akeyless_gw_system_cpu_load_average_15m", label_keys=["akeyless"]),
            ],
        ),
        _timeseries(
            "Gateway Requests",
            _named_series(store, "akeyless_gw_system_request_count_total", rate=True, label_keys=["component"])
            or _named_series(store, "akeyless_gateway_transactions_total", rate=True),
            "req/s",
        ),
        _timeseries(
            "HTTP Status Codes",
            _named_series(
                store,
                "akeyless_gw_system_http_response_status_code_total",
                rate=True,
                label_keys=["status"],
            )
            or _named_series(store, "akeyless_gateway_http_requests_total", rate=True, label_keys=["code"]),
            "req/s",
        ),
        _timeseries(
            "Network I/O",
            [
                *_named_series(
                    store,
                    "akeyless_gw_system_network_io_receive_bytes",
                    rate=True,
                    label_keys=["akeyless"],
                ),
                *_named_series(
                    store,
                    "akeyless_gw_system_network_io_transmit_bytes",
                    rate=True,
                    label_keys=["akeyless"],
                ),
            ],
            "B/s",
        ),
        _timeseries(
            "Disk I/O",
            [
                *_named_series(
                    store,
                    "akeyless_gw_system_disk_io_read_bytes",
                    rate=True,
                    label_keys=["akeyless"],
                ),
                *_named_series(
                    store,
                    "akeyless_gw_system_disk_io_write_bytes",
                    rate=True,
                    label_keys=["akeyless"],
                ),
            ],
            "B/s",
        ),
        _bar(
            "HTTP Status Totals",
            store.group_by_label("akeyless_gw_system_http_response_status_code_total", "status"),
        ),
    ]


