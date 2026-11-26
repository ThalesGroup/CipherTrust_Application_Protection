"""NAE and KMIP crypto dashboards."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _named_series,
    _op_status_items
)

def build_nae(store: ApplianceStore) -> list[dict[str, Any]]:
    success = "ciphertrust_nae_nae_key_management_operation_success"
    failure = "ciphertrust_nae_nae_key_management_operation_failure"
    legacy = any(s.name == "ciphertrust_nae_operations_total" for s in store.latest_samples())

    if legacy:
        items = [
            {
                "label": f"{s.labels.get('operation', '?')}:{s.labels.get('status', '?')}",
                "value": s.value,
            }
            for s in store.latest_samples()
            if s.name == "ciphertrust_nae_operations_total"
        ]
        rate_series = _named_series(
            store, "ciphertrust_nae_operations_total", rate=True, label_keys=["operation", "status"], limit=20
        )
    else:
        items = _op_status_items(store, success, failure)
        rate_series = [
            *_named_series(store, success, rate=True, label_keys=["operation"], limit=15),
            *_named_series(store, failure, rate=True, label_keys=["operation"], limit=15),
        ]

    cache_hits = store.gauge_value("ciphertrust_nae_key_info_cache_hits_total")
    cache_misses = store.gauge_value("ciphertrust_nae_key_info_cache_misses_total")
    user_hits = store.gauge_value("ciphertrust_nae_user_info_cache_hits_total")
    user_misses = store.gauge_value("ciphertrust_nae_user_info_cache_misses_total")

    return [
        _stat("Key Info Cache Hits", cache_hits),
        _stat("Key Info Cache Misses", cache_misses),
        _stat("User Info Cache Hits", user_hits),
        _stat("User Info Cache Misses", user_misses),
        _bar("NAE Key Management Operations", items[:30]),
        _timeseries("NAE Operations Rate", rate_series, "ops/s"),
        _timeseries(
            "Key Info Cache Hits/Misses",
            [
                *_named_series(store, "ciphertrust_nae_key_info_cache_hits_total", rate=True),
                *_named_series(store, "ciphertrust_nae_key_info_cache_misses_total", rate=True),
            ],
            "ops/s",
        ),
        _timeseries(
            "NAE XML Response Samples",
            _named_series(store, "ciphertrust_nae_xml_response_time_seconds_count", rate=True),
            "samples/s",
        ),
        _timeseries(
            "NAE XML Processing Samples",
            _named_series(store, "ciphertrust_nae_xml_processing_time_seconds_count", rate=True),
            "samples/s",
        ),
    ]


def build_kmip(store: ApplianceStore) -> list[dict[str, Any]]:
    success = "ciphertrust_nae_kmip_operation_success"
    failure = "ciphertrust_nae_kmip_operation_failure"
    legacy = any(s.name == "ciphertrust_kmip_operations_total" for s in store.latest_samples())

    if legacy:
        items = [
            {
                "label": f"{s.labels.get('operation', '?')}:{s.labels.get('status', '?')}",
                "value": s.value,
            }
            for s in store.latest_samples()
            if s.name == "ciphertrust_kmip_operations_total"
        ]
        rate_series = _named_series(
            store, "ciphertrust_kmip_operations_total", rate=True, label_keys=["operation", "status"], limit=20
        )
    else:
        items = _op_status_items(store, success, failure)
        rate_series = [
            *_named_series(store, success, rate=True, label_keys=["operation"], limit=15),
            *_named_series(store, failure, rate=True, label_keys=["operation"], limit=15),
        ]

    has_kmip = any(s.name in {success, failure, "ciphertrust_kmip_operations_total"} for s in store.latest_samples())
    success_total = store.sum_value(success) if has_kmip and not legacy else (store.sum_value("ciphertrust_kmip_operations_total", {"status": "success"}) if legacy else None)
    failure_total = store.sum_value(failure) if has_kmip and not legacy else (store.sum_value("ciphertrust_kmip_operations_total", {"status": "failed"}) if legacy else None)

    return [
        _stat("KMIP Success Total", success_total if has_kmip else None),
        _stat("KMIP Failure Total", failure_total if has_kmip else None),
        _bar("KMIP Operations", items[:30]),
        _timeseries("KMIP Operations Rate", rate_series, "ops/s"),
    ]


