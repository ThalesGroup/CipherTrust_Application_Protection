"""Dashboard registry, tab groups, and public lookup helpers."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .cloud import build_cckm, build_cte
from .crypto import build_kmip, build_nae
from .host import build_database, build_host, build_services, build_tcp
from .http_board import build_http
from .network import build_cluster
from .ops import (
    build_backups,
    build_developer,
    build_explorer,
    build_interfaces,
    build_properties,
    build_quorum,
    build_scheduler,
)
from .overview import build_overview
from .panels import _layout_panels, reset_dashboard_range, set_dashboard_range
from .resources import (
    build_resources_audit,
    build_resources_crypto_ops,
    build_resources_domains,
    build_resources_hsm,
    build_resources_keys,
    build_resources_licensing,
)
from .secrets import build_secrets

DASHBOARD_GROUPS: list[dict[str, str]] = [
    {"id": "overview", "title": "Overview"},
    {"id": "crypto", "title": "Crypto"},
    {"id": "resources", "title": "CM Resources"},
    {"id": "secrets", "title": "CSM"},
    {"id": "host", "title": "Host"},
    {"id": "network", "title": "Network"},
    {"id": "cloud", "title": "Connectors/Clients"},
    {"id": "ops", "title": "Ops"},
]

# dashboard_id -> primary group id
_DASHBOARD_GROUP: dict[str, str] = {
    "overview": "overview",
    "nae": "crypto",
    "kmip": "crypto",
    "resources-keys": "resources",
    "resources-licensing": "resources",
    "resources-domains": "resources",
    "resources-audit": "resources",
    "resources-crypto": "resources",
    "resources-hsm": "resources",
    "secrets": "secrets",
    "host": "host",
    "services": "host",
    "database": "host",
    "tcp": "host",
    "http": "network",
    "cluster": "network",
    "cckm": "cloud",
    "cte": "cloud",
    "backups": "ops",
    "scheduler": "ops",
    "quorum": "ops",
    "properties": "ops",
    "interfaces": "ops",
    "developer": "ops",
    "explorer": "ops",
}

# Chip order within each primary tab (first = default).
_GROUP_CHIP_ORDER: dict[str, list[str]] = {
    "overview": ["overview"],
    "crypto": ["nae", "kmip"],
    "resources": [
        "resources-keys",
        "resources-licensing",
        "resources-domains",
        "resources-audit",
        "resources-crypto",
        "resources-hsm",
    ],
    "secrets": ["secrets"],
    "host": ["host", "services", "database", "tcp"],
    "network": ["http", "cluster"],
    "cloud": ["cckm", "cte"],
    "ops": ["backups", "scheduler", "quorum", "properties", "interfaces", "developer", "explorer"],
}


DASHBOARDS: list[dict[str, Any]] = [
    {
        "id": "overview",
        "title": "Overview",
        "icon": "grid",
        "description": "Name/hostname, key stats, utilization charts, recent logins, HTTP/HSM trends.",
        "min_version": "2.7.0",
        "group": "overview",
        "builder": build_overview,
    },
    {
        "id": "resources-keys",
        "title": "Keys",
        "icon": "key",
        "description": "Vault key inventory, KEKs, creations, rotations, and key breakdowns.",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_keys,
    },
    {
        "id": "resources-licensing",
        "title": "Licensing",
        "icon": "award",
        "description": "Connector licenses, unit consumption, and entitled features.",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_licensing,
    },
    {
        "id": "resources-domains",
        "title": "Domains & Users",
        "icon": "users",
        "description": "Domains, users, tenants, subdomain nesting, and orphaned resources from deleted domains.",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_domains,
    },
    {
        "id": "resources-audit",
        "title": "Audit",
        "icon": "file-text",
        "description": "Audit log volume, rates, and client audit logs.",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_audit,
    },
    {
        "id": "resources-crypto",
        "title": "Crypto Ops",
        "icon": "zap",
        "description": "HTTP encrypt/decrypt, crypto decrypt requests, and NAE/KMIP rates.",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_crypto_ops,
    },
    {
        "id": "resources-hsm",
        "title": "HSM",
        "icon": "shield",
        "description": "HSM active sessions (backups are under Ops → Backups).",
        "min_version": "2.7.0",
        "group": "resources",
        "builder": build_resources_hsm,
    },
    {
        "id": "http",
        "title": "HTTP Traffic",
        "icon": "globe",
        "description": "REST API request rates, latency, and HTTP 500 errors.",
        "min_version": "2.7.0",
        "group": "network",
        "builder": build_http,
    },
    {
        "id": "host",
        "title": "Host Metrics",
        "icon": "server",
        "description": "CPU, memory, disk, network, and TCP on the CM host.",
        "min_version": "2.7.0",
        "group": "host",
        "builder": build_host,
    },
    {
        "id": "services",
        "title": "Services / Docker",
        "icon": "layers",
        "description": "Container status, uptime, CPU, memory, and I/O for CM microservices.",
        "min_version": "2.7.0",
        "group": "host",
        "builder": build_services,
    },
    {
        "id": "developer",
        "title": "Developer",
        "icon": "code",
        "description": "JWT, authz caches, HSM sessions, SQL pools, apps/accounts.",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_developer,
    },
    {
        "id": "nae",
        "title": "NAE",
        "icon": "shield",
        "description": "NAE-XML crypto/key operations and timing.",
        "min_version": "2.11.0",
        "group": "crypto",
        "builder": build_nae,
    },
    {
        "id": "kmip",
        "title": "KMIP",
        "icon": "key",
        "description": "KMIP key-management operation success/fail rates.",
        "min_version": "2.11.0",
        "group": "crypto",
        "builder": build_kmip,
    },
    {
        "id": "cluster",
        "title": "Cluster / Node",
        "icon": "git-branch",
        "description": "Appliance-wide raft status, node count, replication lags, and connectivity.",
        "min_version": "2.10.0",
        "group": "network",
        "builder": build_cluster,
    },
    {
        "id": "backups",
        "title": "Backups",
        "icon": "archive",
        "description": "Root domain only",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_backups,
    },
    {
        "id": "scheduler",
        "title": "Scheduler",
        "icon": "clock",
        "description": "Root domain only",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_scheduler,
    },
    {
        "id": "quorum",
        "title": "Quorum",
        "icon": "users",
        "description": "Root domain only",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_quorum,
    },
    {
        "id": "properties",
        "title": "Properties",
        "icon": "sliders",
        "description": "System properties from REST, plus modified-vs-default posture.",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_properties,
    },
    {
        "id": "interfaces",
        "title": "Interfaces",
        "icon": "server",
        "description": "Web / NAE / KMIP / SSH / SNMP — TLS, PQC, mode, trusted CAs, and live risk flags.",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_interfaces,
    },
    {
        "id": "cte",
        "title": "CTE Resources",
        "icon": "hard-drive",
        "description": "CTE clients, groups, health, and guard points.",
        "min_version": "2.12.0",
        "group": "cloud",
        "builder": build_cte,
    },
    {
        "id": "cckm",
        "title": "CCKM / Cloud Keys",
        "icon": "cloud",
        "description": "Cloud Key Manager endpoints, issuers, and XKS/OCI caches.",
        "min_version": "2.12.0",
        "group": "cloud",
        "builder": build_cckm,
    },
    {
        "id": "database",
        "title": "Database / SQL",
        "icon": "database",
        "description": "SQL connection pools, waits, and query rates by service.",
        "min_version": "2.7.0",
        "group": "host",
        "builder": build_database,
    },
    {
        "id": "secrets",
        "title": "CSM",
        "icon": "lock",
        "description": "CSM (Akeyless) CPU, memory, and transactions.",
        "min_version": "2.15.0",
        "group": "secrets",
        "builder": build_secrets,
    },
    {
        "id": "tcp",
        "title": "Active TCP",
        "icon": "activity",
        "description": "Real-time active TCP connections by port/interface.",
        "min_version": "2.22.0",
        "group": "host",
        "builder": build_tcp,
    },
    {
        "id": "explorer",
        "title": "Metric Explorer",
        "icon": "search",
        "description": "Browse raw scraped samples by prefix and value.",
        "min_version": "2.7.0",
        "group": "ops",
        "builder": build_explorer,
    },
]



def list_dashboards() -> list[dict[str, Any]]:
    by_id = {d["id"]: d for d in DASHBOARDS}
    items = []
    for d in DASHBOARDS:
        items.append(
            {
                "id": d["id"],
                "title": d["title"],
                "icon": d["icon"],
                "description": d["description"],
                "min_version": d["min_version"],
                "group": d.get("group") or _DASHBOARD_GROUP.get(d["id"], "ops"),
            }
        )
    # Overview pinned first; everything else A–Z by title (API consumers).
    overview = [d for d in items if d["id"] == "overview"]
    rest = sorted((d for d in items if d["id"] != "overview"), key=lambda d: d["title"].lower())
    return overview + rest


def list_dashboard_groups() -> list[dict[str, Any]]:
    """Primary tabs with ordered secondary chips for the tabbed workspace UI."""
    by_id = {
        d["id"]: {
            "id": d["id"],
            "title": d["title"],
            "icon": d["icon"],
            "description": d["description"],
            "min_version": d["min_version"],
            "group": d.get("group") or _DASHBOARD_GROUP.get(d["id"], "ops"),
        }
        for d in DASHBOARDS
    }
    groups: list[dict[str, Any]] = []
    for g in DASHBOARD_GROUPS:
        chip_ids = _GROUP_CHIP_ORDER.get(g["id"], [])
        chips = [by_id[cid] for cid in chip_ids if cid in by_id]
        groups.append({"id": g["id"], "title": g["title"], "dashboards": chips})
    return groups


# Allowed UI time-range windows (seconds).
RANGE_SECONDS = {
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "6h": 21600,
    "24h": 86400,
    "7d": 604800,
    "30d": 2592000,
}


def parse_range(raw: str | None) -> tuple[str, float]:
    """Return (range_id, seconds). Defaults to 24h."""
    key = (raw or "24h").strip().lower()
    if key not in RANGE_SECONDS:
        key = "24h"
    return key, float(RANGE_SECONDS[key])


def get_dashboard(
    dashboard_id: str,
    store: ApplianceStore,
    appliance: dict[str, Any] | None = None,
    *,
    range_seconds: float | None = None,
    range_id: str | None = None,
) -> dict[str, Any] | None:
    token = set_dashboard_range(range_seconds)
    try:
        for d in DASHBOARDS:
            if d["id"] == dashboard_id:
                builder = d["builder"]
                # Dashboards that mix Prometheus + REST ops snapshot need appliance context.
                if dashboard_id in {
                    "overview",
                    "resources-keys",
                    "cluster",
                    "backups",
                    "scheduler",
                    "quorum",
                    "properties",
                    "interfaces",
                }:
                    panels = _layout_panels(builder(store, appliance))
                else:
                    panels = _layout_panels(builder(store))
                return {
                    "id": d["id"],
                    "title": d["title"],
                    "description": d["description"],
                    "min_version": d["min_version"],
                    "range": range_id or "24h",
                    "range_seconds": range_seconds,
                    "panels": panels,
                }
    finally:
        reset_dashboard_range(token)
    return None
