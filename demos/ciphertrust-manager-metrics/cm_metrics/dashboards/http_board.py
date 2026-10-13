"""HTTP traffic dashboard."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _named_series
)

def build_http(store: ApplianceStore) -> list[dict[str, Any]]:
    err_500 = store.increase(
        "http_response_time_seconds_count",
        {"code": "500"},
        60,
    )
    return [
        _stat("HTTP 500s (last minute)", err_500),
        _timeseries(
            "HTTP Requests In The Last Minute (rate)",
            _named_series(store, "http_response_time_seconds_count", rate=True, limit=12, label_keys=["method", "path"]),
            "req/s",
            "increase(http_response_time_seconds_count[1m])",
        ),
        _timeseries(
            "HTTP 500 Errors",
            _named_series(
                store,
                "http_response_time_seconds_count",
                {"code": "500"},
                rate=True,
                label_keys=["method", "path"],
            ),
            "req/s",
        ),
        _timeseries(
            "Internal HTTP Client Response Count",
            _named_series(store, "httpclient_response_time_seconds_count", rate=True, label_keys=["method", "path"]),
            "req/s",
        ),
        _timeseries(
            "Network Latency Samples",
            _named_series(
                store,
                "ciphertrust_httpclient_network_latency_seconds_count",
                rate=True,
                label_keys=["service", "upstream_service"],
            ),
            "samples/s",
        ),
    ]


