"""Cluster / node network dashboard."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _named_series
)

def build_cluster(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    connected = [
        {"label": s.labels.get("host") or s.labels.get("node", "?"), "value": s.value}
        for s in store.latest_samples()
        if s.name in {"ciphertrust_cluster_connected", "ciphertrust_cluster_node_connected"}
    ]
    ops = (appliance or {}).get("ops_snapshot") or {}
    cluster_api = ops.get("cluster_api") if isinstance(ops, dict) else None
    if not isinstance(cluster_api, dict):
        cluster_api = {}

    # Older / non-clustered CMs may omit these fields or return 404 for /v1/cluster.
    # Never raise — blank tiles ("—") when API data is missing.
    node_count_raw = cluster_api.get("nodeCount")
    node_count: float | None
    try:
        node_count = float(node_count_raw) if node_count_raw is not None else None
    except (TypeError, ValueError):
        node_count = None

    raft = cluster_api.get("raftStatus")
    status = cluster_api.get("status")
    node_id = cluster_api.get("nodeID")
    api_err = cluster_api.get("error")

    return [
        _stat(
            "Cluster Nodes",
            node_count,
            description=str(api_err) if api_err and node_count is None else "",
        ),
        _stat("Raft Status", raft if isinstance(raft, (str, int, float)) else None),
        _stat("Node Status", status if isinstance(status, (str, int, float)) else None),
        _stat("This Node ID", node_id if isinstance(node_id, (str, int, float)) else None),
        _bar("Node Connected", connected),
        _stat(
            "Replication Blocked",
            store.sum_value("ciphertrust_cluster_replication_blocked")
            if any(s.name == "ciphertrust_cluster_replication_blocked" for s in store.latest_samples())
            else None,
        ),
        _timeseries(
            "Write Lag",
            _named_series(store, "ciphertrust_cluster_write_lag", label_keys=["host"])
            or _named_series(store, "ciphertrust_cluster_write_lag_seconds", label_keys=["node"]),
            "s",
        ),
        _timeseries(
            "Replay Lag",
            _named_series(store, "ciphertrust_cluster_replay_lag", label_keys=["host"])
            or _named_series(store, "ciphertrust_cluster_replay_lag_seconds", label_keys=["node"]),
            "s",
        ),
        _timeseries(
            "Flush Lag",
            _named_series(store, "ciphertrust_cluster_flush_lag", label_keys=["host"]),
            "s",
        ),
        _timeseries(
            "Cluster Uptime",
            _named_series(store, "ciphertrust_cluster_uptime", label_keys=["host"]),
            "duration",
        ),
    ]


