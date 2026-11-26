"""Cloud dashboards: CTE and CCKM."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _bar,
    _named_series,
    _stat,
    _timeseries,
)


def build_cte(store: ApplianceStore) -> list[dict[str, Any]]:
    # CM exports ciphertrust_cte_management_* (not ciphertrust_cte_clients_total).
    samples = store.latest_samples()
    has_mgmt_clients = any(s.name == "ciphertrust_cte_management_cte_clients" for s in samples)
    has_mgmt_groups = any(s.name == "ciphertrust_cte_management_cte_groups" for s in samples)
    has_mgmt_gp = any(s.name == "ciphertrust_cte_management_cte_guardpoints" for s in samples)
    has_mgmt_health = any(s.name == "ciphertrust_cte_management_clients_health_status" for s in samples)
    has_cte = any(s.name.startswith("ciphertrust_cte_") for s in samples)

    clients_total = (
        store.sum_value("ciphertrust_cte_management_cte_clients")
        if has_mgmt_clients
        else store.sum_value("ciphertrust_cte_clients_total")
    )
    groups_total = (
        store.sum_value("ciphertrust_cte_management_cte_groups")
        if has_mgmt_groups
        else store.sum_value("ciphertrust_cte_groups_total")
    )
    guardpoints_total = (
        store.sum_value("ciphertrust_cte_management_cte_guardpoints")
        if has_mgmt_gp
        else store.sum_value("ciphertrust_cte_guardpoints_state")
    )

    health = (
        store.group_by_label("ciphertrust_cte_management_clients_health_status", "health_status")
        if has_mgmt_health
        else store.group_by_label("ciphertrust_cte_clients_health", "status")
    )

    clients_by_type = store.group_by_label("ciphertrust_cte_management_cte_clients", "clients_type")
    groups_by_name = store.group_by_label("ciphertrust_cte_management_cte_groups", "group_name")
    guard_by_state = (
        store.group_by_label("ciphertrust_cte_management_cte_guardpoints", "guard_state")
        if has_mgmt_gp
        else store.group_by_label("ciphertrust_cte_guardpoints_state", "state")
    )

    healthy = next((i["value"] for i in health if str(i["label"]).upper() == "HEALTHY"), None)
    not_connected = next(
        (i["value"] for i in health if str(i["label"]).upper() == "NOT CONNECTED"), None
    )

    return [
        _stat("CTE Clients", clients_total if has_cte else None),
        _stat("CTE Groups", groups_total if has_cte else None),
        _stat("Guard Points", guardpoints_total if has_cte else None),
        _stat("Healthy Clients", healthy if has_cte else None),
        _stat("Not Connected", not_connected if has_cte else None),
        _bar("Clients by Type", clients_by_type),
        _bar("Client Health Status", health),
        _bar("CTE Groups", groups_by_name),
        _bar("Guard Point State", guard_by_state),
        _timeseries(
            "Clients by Type Over Time",
            _named_series(store, "ciphertrust_cte_management_cte_clients", label_keys=["clients_type"]),
        ),
        _timeseries(
            "Client Health Over Time",
            _named_series(
                store,
                "ciphertrust_cte_management_clients_health_status",
                label_keys=["health_status"],
            ),
        ),
        _timeseries(
            "Guard Points by State Over Time",
            _named_series(
                store,
                "ciphertrust_cte_management_cte_guardpoints",
                label_keys=["guard_state"],
            ),
        ),
    ]


def _cckm_friendly_label(name: str, prefix: str) -> str:
    """Turn long CCKM metric names into readable cache labels."""
    short = name.replace(prefix, "").replace("_cache_hits", "").replace("_cache_misses", "")
    # Collapse duplicated xks_xks_ / noisy prefixes
    replacements = (
        ("xks_xks_custom_keystore_local_m_keys", "XKS custom keystore Minerva keys"),
        ("xks_xks_custom_keystore_creds", "XKS custom keystore creds"),
        ("xks_xks_virtual_key", "XKS virtual key"),
        ("xks_xks_luna_slot", "XKS Luna slot"),
        ("xks_xks_luna_key", "XKS Luna key"),
        ("xks_xks_kms", "XKS KMS"),
        ("xks_xks_key", "XKS key"),
        ("aws_xks_virtual_key", "AWS XKS virtual key"),
        ("aws_xks_luna_slot", "AWS XKS Luna slot"),
        ("aws_xks_luna_key", "AWS XKS Luna key"),
        ("aws_xks_kms", "AWS XKS KMS"),
        ("aws_xks_key", "AWS XKS key"),
        ("ocihyok_local_key_version", "OCI HYOK local key version"),
        ("ocihyok_local_key_store", "OCI HYOK local keystore"),
        ("ocihyok_local_key", "OCI HYOK local key"),
        ("ocihyok_key_version", "OCI HYOK key version"),
        ("oci_tenancy", "OCI tenancy"),
        ("gws_add_routes_req_seconds", "GWS add routes"),
        ("gws_new_router_req_seconds", "GWS new router"),
    )
    for old, new in replacements:
        if short.startswith(old):
            return new
    return short.replace("_", " ")[:48]


def build_cckm(store: ApplianceStore) -> list[dict[str, Any]]:
    """CipherTrust Cloud Key Manager (CCKM / XKS / OCI HYOK) resources."""
    prefix = "ciphertrust_ciphertrust_cloud_key_manager_"
    endpoints = store.gauge_value(prefix + "endpoints_total")
    issuers = store.gauge_value(prefix + "issuers_total")
    perimeters = store.gauge_value(prefix + "perimeters_total")

    cache_hit_names = [
        s.name
        for s in store.latest_samples()
        if s.name.startswith(prefix) and s.name.endswith("_cache_hits")
    ]
    cache_miss_names = [
        s.name
        for s in store.latest_samples()
        if s.name.startswith(prefix) and s.name.endswith("_cache_misses")
    ]
    # Deduplicate while preserving order
    cache_hit_names = list(dict.fromkeys(cache_hit_names))
    cache_miss_names = list(dict.fromkeys(cache_miss_names))

    hit_items = []
    miss_by_base: dict[str, float] = {}
    for name in cache_miss_names:
        miss_by_base[_cckm_friendly_label(name, prefix)] = store.sum_value(name)

    hit_rate_items: list[dict[str, Any]] = []
    for name in cache_hit_names:
        label = _cckm_friendly_label(name, prefix)
        hits = store.sum_value(name)
        if hits:
            hit_items.append({"label": label, "value": hits})
        misses = miss_by_base.get(label, 0.0) or 0.0
        total = hits + misses
        if total > 0:
            hit_rate_items.append({"label": label, "value": (hits / total) * 100.0})

    hit_items.sort(key=lambda x: -x["value"])
    hit_rate_items.sort(key=lambda x: -x["value"])

    miss_items = []
    for name in cache_miss_names:
        val = store.sum_value(name)
        if val:
            miss_items.append({"label": _cckm_friendly_label(name, prefix), "value": val})
    miss_items.sort(key=lambda x: -x["value"])

    hit_series = []
    for name in cache_hit_names[:8]:
        for series in _named_series(store, name, rate=True, limit=1):
            series["name"] = _cckm_friendly_label(name, prefix)
            hit_series.append(series)

    route_series = [
        *_named_series(store, prefix + "gws_add_routes_req_seconds_count", rate=True, limit=3),
        *_named_series(store, prefix + "gws_new_router_req_seconds_count", rate=True, limit=3),
    ]
    for series in route_series:
        raw = series.get("name") or ""
        if "gws_add_routes" in raw:
            series["name"] = "GWS add routes"
        elif "gws_new_router" in raw:
            series["name"] = "GWS new router"

    overall_hits = sum(i["value"] for i in hit_items)
    overall_misses = sum(i["value"] for i in miss_items)
    overall_rate = None
    if overall_hits + overall_misses > 0:
        overall_rate = (overall_hits / (overall_hits + overall_misses)) * 100.0

    return [
        _stat("CCKM Endpoints", endpoints),
        _stat("CCKM Issuers", issuers),
        _stat("CCKM Perimeters", perimeters),
        _stat(
            "Cache Types",
            float(len(cache_hit_names)) if cache_hit_names else None,
            description="Distinct *_cache_hits series discovered.",
        ),
        _stat(
            "Overall Cache Hit %",
            overall_rate,
            "%",
            description="hits / (hits + misses) across discovered CCKM caches.",
        ),
        _bar("CCKM Cache Hits by Type", hit_items[:20]),
        _bar("CCKM Cache Misses by Type", miss_items[:20]),
        _bar(
            "CCKM Cache Hit Rate by Type",
            hit_rate_items[:20],
            "%",
            "Hit percentage per cache family (XKS / OCI HYOK / etc.).",
        ),
        _timeseries("CCKM Cache Hit Rate", hit_series, "hits/s"),
        _timeseries("CCKM Gateway Route Ops", route_series, "ops/s"),
    ]
