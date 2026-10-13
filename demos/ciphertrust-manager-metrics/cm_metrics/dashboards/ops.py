"""Ops dashboards: developer, backups, scheduler, properties, quorum, interfaces, explorer."""

from __future__ import annotations

from typing import Any

from ..security_posture import evaluate_interfaces, evaluate_modified_properties
from ..store import ApplianceStore
from .panels import (
    _stat,
    _timeseries,
    _bar,
    _note,
    _named_series,
    _first_gauge,
    _first_rate,
)

def build_developer(store: ApplianceStore) -> list[dict[str, Any]]:
    jwt_sum = _first_gauge(
        store,
        "ciphertrust_api_jwt_middleware_processing_time_seconds_sum",
        "ciphertrust_jwt_processing_time_seconds_sum",
    )
    jwt_cnt = _first_gauge(
        store,
        "ciphertrust_api_jwt_middleware_processing_time_seconds_count",
        "ciphertrust_jwt_processing_time_seconds_count",
    )
    jwt_avg = (jwt_sum / jwt_cnt) if jwt_sum is not None and jwt_cnt else None

    apps = _first_gauge(
        store,
        "ciphertrust_authorization_applications_total",
        "ciphertrust_applications_total",
    )
    accounts = _first_gauge(
        store,
        "ciphertrust_authorization_accounts_total",
        "ciphertrust_accounts_total",
    )
    users_authz = store.gauge_value("ciphertrust_authorization_users_total")
    identities = store.gauge_value("ciphertrust_authorization_identities_total")
    kek = _first_gauge(store, "ciphertrust_key_vault_keks_total", "ciphertrust_kek_count")

    policy_hits = _first_rate(
        store,
        "ciphertrust_authorization_effective_policies_cache_hits",
        "ciphertrust_auth_policies_cache_hits",
    )
    account_hits = store.rate("ciphertrust_authorization_account_cache_hits")
    identity_hits = store.rate("ciphertrust_authorization_identity_cache_hits")

    authz_sum = store.gauge_value("ciphertrust_authorization_authorization_seconds_sum")
    authz_cnt = store.gauge_value("ciphertrust_authorization_authorization_seconds_count")
    authz_avg = (authz_sum / authz_cnt) if authz_sum is not None and authz_cnt else None

    sql_open = store.sum_value("sql_open_connections")
    sql_in_use = store.sum_value("sql_in_use_connections")
    has_sql = any(s.name == "sql_open_connections" for s in store.latest_samples())

    # Internal microservice latency: avg = sum/count per upstream_service.
    has_httpclient = any(
        s.name == "ciphertrust_httpclient_network_latency_seconds_count"
        for s in store.latest_samples()
    )
    latency_items: list[dict[str, Any]] = []
    if has_httpclient:
        sums = {
            (s.labels.get("upstream_service") or "unknown"): s.value
            for s in store.latest_samples()
            if s.name == "ciphertrust_httpclient_network_latency_seconds_sum"
        }
        counts = {
            (s.labels.get("upstream_service") or "unknown"): s.value
            for s in store.latest_samples()
            if s.name == "ciphertrust_httpclient_network_latency_seconds_count"
        }
        for upstream, cnt in counts.items():
            if cnt and cnt > 0:
                total = sums.get(upstream, 0.0) or 0.0
                latency_items.append({"label": upstream, "value": total / cnt})
        latency_items.sort(key=lambda x: -x["value"])

    panels: list[dict[str, Any]] = [
        _stat("Avg JWT Processing Time", jwt_avg, "s"),
        _stat("Avg Authz Time", authz_avg, "s"),
        _stat("Applications", apps),
        _stat("Accounts", accounts),
        _stat("Authz Users", users_authz),
        _stat("Identities", identities),
        _stat("KEKs", kek),
        _stat("HSM Active Sessions", store.gauge_value("ciphertrust_hsm_active_sessions")),
        _stat("SQL Open Connections", sql_open if has_sql else None),
        _stat("SQL In Use", sql_in_use if has_sql else None),
        _stat("Policy Cache Hits /s", policy_hits, "hits/s"),
        _stat("Account Cache Hits /s", account_hits, "hits/s"),
        _stat("Identity Cache Hits /s", identity_hits, "hits/s"),
        _timeseries(
            "Effective Policy Cache Hits",
            _named_series(store, "ciphertrust_authorization_effective_policies_cache_hits", rate=True)
            or _named_series(store, "ciphertrust_auth_policies_cache_hits", rate=True),
            "hits/s",
        ),
        _timeseries(
            "Account / Identity Cache Hits",
            [
                *_named_series(store, "ciphertrust_authorization_account_cache_hits", rate=True),
                *_named_series(store, "ciphertrust_authorization_identity_cache_hits", rate=True),
                *_named_series(store, "ciphertrust_authorization_client_cache_hits", rate=True),
            ],
            "hits/s",
        ),
        _timeseries(
            "Cache Misses",
            [
                *_named_series(store, "ciphertrust_authorization_account_cache_misses", rate=True),
                *_named_series(store, "ciphertrust_authorization_identity_cache_misses", rate=True),
                *_named_series(store, "ciphertrust_authorization_client_cache_misses", rate=True),
                *_named_series(
                    store, "ciphertrust_authorization_effective_policies_cache_misses", rate=True
                ),
            ],
            "misses/s",
        ),
        _timeseries(
            "JWT Middleware Processing Count",
            _named_series(
                store,
                "ciphertrust_api_jwt_middleware_processing_time_seconds_count",
                rate=True,
            )
            or _named_series(store, "ciphertrust_jwt_processing_time_seconds_count", rate=True),
            "ops/s",
        ),
        _timeseries(
            "Authorization Ops",
            _named_series(
                store, "ciphertrust_authorization_authorization_seconds_count", rate=True
            ),
            "ops/s",
        ),
        _bar(
            "SQL Open Connections by DB",
            store.group_by_label("sql_open_connections", "db"),
        ),
        _bar(
            "SQL In-Use Connections by Service",
            store.group_by_label("sql_in_use_connections", "service"),
        ),
    ]
    if has_httpclient:
        panels.extend(
            [
                _bar(
                    "Avg Internal Latency by Upstream",
                    latency_items[:20],
                    "s",
                    "httpclient_network_latency_seconds sum/count by upstream_service.",
                ),
                _timeseries(
                    "Internal HTTP Client Ops by Upstream",
                    _named_series(
                        store,
                        "ciphertrust_httpclient_network_latency_seconds_count",
                        rate=True,
                        label_keys=["upstream_service"],
                        limit=12,
                    ),
                    "ops/s",
                    "Request rate to internal upstream services.",
                    wide=True,
                ),
            ]
        )
    return panels



def build_backups(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Backups from REST /v1/backups (+ Prometheus backup counters when exported)."""
    ops = (appliance or {}).get("ops_snapshot") or {}
    backups = ops.get("backups") if isinstance(ops, dict) else None
    if not isinstance(backups, dict):
        backups = {}

    # Sum across scope labels (domain + system); gauge_value only returns the first series.
    has_prom = any(
        s.name.startswith("ciphertrust_backup_") for s in store.latest_samples()
    )
    prom_count = store.sum_value("ciphertrust_backup_number_of_backups_taken_count") if has_prom else None
    backup_avg = None
    bsum = store.sum_value("ciphertrust_backup_number_of_backups_taken_sum") if has_prom else None
    bcnt = prom_count
    if bsum is not None and bcnt and bcnt > 0:
        backup_avg = bsum / bcnt

    by_status = backups.get("by_status") or {}
    by_scope = backups.get("by_scope") or {}
    recent = backups.get("recent") or []
    total = backups.get("total")
    err = backups.get("error")

    completed = by_status.get("Completed") or by_status.get("completed")
    failed = sum(v for k, v in by_status.items() if "fail" in str(k).lower())

    return [
        _stat("Backups (API)", float(total) if total is not None else None, description=err or ""),
        _stat("Completed", float(completed) if completed is not None else None),
        _stat("Failed / other", float(failed) if by_status else None),
        _stat("Prometheus Backup Count", prom_count if has_prom else None),
        _stat("Avg Backup Time", backup_avg if has_prom else None, "s"),
        _bar(
            "Backups by Status",
            [{"label": str(k), "value": float(v)} for k, v in sorted(by_status.items())],
        ),
        _bar(
            "Backups by Scope",
            [{"label": str(k), "value": float(v)} for k, v in sorted(by_scope.items())],
        ),
        {
            "type": "table",
            "title": "Recent Backups",
            "columns": ["createdAt", "status", "scope", "description", "productVersion"],
            "rows": [
                {
                    "createdAt": r.get("createdAt") or "",
                    "status": r.get("status") or "",
                    "scope": r.get("scope") or "",
                    "description": r.get("description") or "",
                    "productVersion": r.get("productVersion") or "",
                }
                for r in recent
            ],
        },
    ]


def build_scheduler(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Scheduler job-configs + recent job runs from REST (no Prometheus schedule metrics)."""
    ops = (appliance or {}).get("ops_snapshot") or {}
    configs = ops.get("scheduler_configs") if isinstance(ops, dict) else None
    jobs = ops.get("scheduler_jobs") if isinstance(ops, dict) else None
    if not isinstance(configs, dict):
        configs = {}
    if not isinstance(jobs, dict):
        jobs = {}

    # Prometheus key-rotation counters (schedule-related when present)
    rot_sched = store.increase("ciphertrust_key_vault_key_rotations", {"source": "scheduler"}, 300)
    has_rot = any(s.name == "ciphertrust_key_vault_key_rotations" for s in store.latest_samples())

    by_op_cfg = configs.get("by_operation") or {}
    by_status = jobs.get("by_status") or {}
    by_op_jobs = jobs.get("by_operation") or {}
    cfg_items = configs.get("items") or []
    recent = jobs.get("recent") or []

    return [
        _stat("Job Configs", float(configs["total"]) if configs.get("total") is not None else None, description=configs.get("error") or ""),
        _stat("Configs Enabled", float(configs["enabled"]) if configs.get("enabled") is not None else None),
        _stat("Configs Disabled", float(configs["disabled"]) if configs.get("disabled") is not None else None),
        _stat("Job Runs (total)", float(jobs["total"]) if jobs.get("total") is not None else None, description=jobs.get("error") or ""),
        _stat("Recent Page Size", float(jobs["recent_count"]) if jobs.get("recent_count") is not None else None),
        _stat("Rotations 5m (scheduler)", rot_sched if has_rot else None),
        _bar(
            "Configs by Operation",
            [{"label": str(k), "value": float(v)} for k, v in sorted(by_op_cfg.items(), key=lambda x: -x[1])],
        ),
        _bar(
            "Recent Runs by Status",
            [{"label": str(k), "value": float(v)} for k, v in sorted(by_status.items())],
        ),
        _bar(
            "Recent Runs by Operation",
            [{"label": str(k), "value": float(v)} for k, v in sorted(by_op_jobs.items(), key=lambda x: -x[1])[:15]],
        ),
        {
            "type": "table",
            "title": "Job Configurations",
            "columns": ["name", "operation", "run_at", "run_on", "disabled", "updatedAt"],
            "rows": [
                {
                    "name": i.get("name") or "",
                    "operation": i.get("operation") or "",
                    "run_at": i.get("run_at") or "",
                    "run_on": i.get("run_on") or "",
                    "disabled": "yes" if i.get("disabled") else "no",
                    "updatedAt": i.get("updatedAt") or "",
                }
                for i in cfg_items
            ],
        },
        {
            "type": "table",
            "title": "Recent Job Runs",
            "columns": ["createdAt", "name", "operation", "status", "processing_node"],
            "rows": [
                {
                    "createdAt": r.get("createdAt") or "",
                    "name": r.get("name") or "",
                    "operation": r.get("operation") or "",
                    "status": r.get("status") or "",
                    "processing_node": r.get("processing_node") or "",
                }
                for r in recent
            ],
        },
    ]


def build_properties(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """System properties from REST /v1/configs/properties (Admin Settings → Properties)."""
    del store
    ops = (appliance or {}).get("ops_snapshot") or {}
    props = ops.get("system_properties") if isinstance(ops, dict) else None
    if not isinstance(props, dict):
        props = {}

    items = props.get("items") or []
    err = props.get("error") or ""
    total = props.get("total")
    lb = next((i for i in items if str(i.get("name") or "") == "LOAD_BALANCER_ADDRESS"), None)
    lb_value = (lb or {}).get("value") if lb else None
    if lb_value == "":
        lb_value = "(empty)"

    posture = evaluate_modified_properties(items if isinstance(items, list) else [])
    modified = posture.get("modified") or []
    mod_n = int(posture.get("modified_count") or 0)

    panels: list[dict[str, Any]] = [
        _stat(
            "Properties",
            float(total) if total is not None else (float(len(items)) if items else None),
            description=err or "From /v1/configs/properties",
        ),
        _stat("Load Balancer Address", lb_value if lb is not None else None),
        _stat(
            "Modified vs default",
            float(mod_n),
            description=f"Compared against {posture.get('known_defaults', 0)} documented defaults",
        ),
    ]

    if items and not err:
        if mod_n:
            panels.append(
                _note(
                    f"{mod_n} system propert{'y has' if mod_n == 1 else 'ies have'} a value different "
                    "from the documented default (same rules as healthcheck).",
                    title="Properties posture · modified",
                    tone="info",
                )
            )
        else:
            panels.append(
                _note(
                    "All known system properties match their documented defaults.",
                    title="Properties posture · defaults",
                    tone="pass",
                )
            )

    panels.append(
        {
            "type": "table",
            "title": "Modified Properties (vs default)",
            "description": "Live REST values compared to documented defaults — no healthcheck run required.",
            "columns": ["name", "value", "default", "description"],
            "rows": [
                {
                    "name": r.get("name") or "",
                    "value": r.get("value") if r.get("value") is not None else "",
                    "default": r.get("default") if r.get("default") is not None else "",
                    "description": r.get("description") or "",
                }
                for r in modified
            ]
            or (
                [{"name": "—", "value": "None modified", "default": "", "description": ""}]
                if items and not err
                else []
            ),
            "wide": True,
            "span": 12,
        }
    )
    panels.append(
        {
            "type": "table",
            "title": "System Properties",
            "columns": ["name", "value", "description"],
            "rows": [
                {
                    "name": r.get("name") or "",
                    "value": r.get("value") if r.get("value") is not None else "",
                    "description": r.get("description") or "",
                }
                for r in items
            ],
        }
    )
    return panels


def build_quorum(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Quorum profiles + active policy status from /v1/quorum-mgmt/*."""
    ops = (appliance or {}).get("ops_snapshot") or {}
    quorum = ops.get("quorum") if isinstance(ops, dict) else None
    if not isinstance(quorum, dict):
        quorum = {}

    err = quorum.get("error") or ""
    by_category = quorum.get("by_category") or {}
    profiles = quorum.get("profiles") or []
    statuses = quorum.get("statuses") or []
    active_ops = quorum.get("active_ops") or []

    return [
        _stat(
            "Quorum Profiles",
            float(quorum["profiles_total"]) if quorum.get("profiles_total") is not None else None,
            description=err,
        ),
        _stat("Policies Active", float(quorum["active"]) if quorum.get("active") is not None else None),
        _stat("Policies Inactive", float(quorum["inactive"]) if quorum.get("inactive") is not None else None),
        _stat(
            "Auto-executable Profiles",
            float(quorum["auto_executable"]) if quorum.get("auto_executable") is not None else None,
        ),
        _stat(
            "Avg Required Approvals",
            float(quorum["avg_required_approvals"])
            if quorum.get("avg_required_approvals") is not None
            else None,
        ),
        _bar(
            "Profiles by Category",
            [
                {"label": str(k), "value": float(v)}
                for k, v in sorted(by_category.items(), key=lambda x: -x[1])
            ],
        ),
        {
            "type": "table",
            "title": "Active Quorum Policies",
            "columns": ["operation", "profile", "description"],
            "rows": [
                {
                    "operation": r.get("operation") or "",
                    "profile": r.get("profile") or "",
                    "description": r.get("description") or "",
                }
                for r in active_ops
            ]
            or (
                [{"operation": "—", "profile": "None active", "description": ""}]
                if quorum and not err
                else []
            ),
        },
        {
            "type": "table",
            "title": "Quorum Profiles",
            "columns": [
                "name",
                "category",
                "operation_label",
                "required_approvals",
                "voter_groups",
                "auto_executable",
                "expiration_period",
            ],
            "rows": [
                {
                    "name": p.get("name") or "",
                    "category": p.get("category") or "",
                    "operation_label": p.get("operation_label") or "",
                    "required_approvals": p.get("required_approvals")
                    if p.get("required_approvals") is not None
                    else "",
                    "voter_groups": p.get("voter_groups") or "",
                    "auto_executable": "yes" if p.get("auto_executable") else "no",
                    "expiration_period": p.get("expiration_period")
                    if p.get("expiration_period") is not None
                    else "",
                }
                for p in profiles
            ],
        },
        {
            "type": "table",
            "title": "Policy Status (all)",
            "columns": ["active", "operation", "profile", "description"],
            "rows": [
                {
                    "active": "yes" if s.get("active") else "no",
                    "operation": s.get("operation") or "",
                    "profile": s.get("profile") or "",
                    "description": s.get("description") or "",
                }
                for s in statuses
            ],
        },
    ]



def build_interfaces(store: ApplianceStore, appliance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Network interfaces from REST /v1/configs/interfaces (TLS, PQC, trusted CAs)."""
    del store  # REST-only dashboard
    ops = (appliance or {}).get("ops_snapshot") or {}
    data = ops.get("interfaces") if isinstance(ops, dict) else None
    if not isinstance(data, dict):
        data = {}

    err = data.get("error") or ""
    items = data.get("items") or []
    by_type = data.get("by_type") or {}
    posture = evaluate_interfaces(items if isinstance(items, list) else [])
    per_iface = posture.get("per_iface") or {}
    findings = posture.get("findings") or []
    overall = posture.get("overall") or "PASS"
    tone = "fail" if overall == "FAIL" else "warning" if overall == "WARNING" else "pass"

    panels: list[dict[str, Any]] = [
        _stat(
            "Interfaces",
            float(data["total"]) if data.get("total") is not None else (float(len(items)) if items else None),
            description=err or "From /v1/configs/interfaces",
        ),
        _stat(
            "Enabled",
            float(data["enabled"]) if data.get("enabled") is not None else None,
        ),
        _stat(
            "Web PQC",
            float(data["pqc_enabled_interfaces"])
            if data.get("pqc_enabled_interfaces") is not None
            else None,
            description="Web interface only — ML-KEM / hybrid TLS groups or PQC ciphers",
        ),
        _stat(
            "Posture",
            overall,
            description="Live REST evaluation (healthcheck-equivalent rules)",
            tone=tone,
        ),
        _stat("Insecure modes", float(posture.get("insecure_modes") or 0)),
        _stat("Weak min TLS", float(posture.get("weak_tls") or 0)),
        _stat(
            "Web missing PQC",
            float(posture.get("no_pqc") or 0),
            description="Enabled Web interface(s) without PQC (N/A for NAE/KMIP/SSH/SNMP)",
        ),
        _stat("Disabled", float(posture.get("disabled") or 0)),
        _bar(
            "Interfaces by Type",
            [
                {"label": str(k), "value": float(v)}
                for k, v in sorted(by_type.items(), key=lambda x: -x[1])
            ],
        ),
    ]

    if findings:
        panels.append(
            {
                "type": "table",
                "title": "Interface Risk Findings",
                "description": "Same rules as healthcheck network checks, applied to live REST data.",
                "columns": ["severity", "finding"],
                "rows": [
                    {
                        "severity": f.get("severity") or "",
                        "finding": f.get("message") or "",
                    }
                    for f in findings
                ],
                "wide": True,
                "span": 12,
            }
        )

    panels.append(
        {
            "type": "table",
            "title": "Interfaces",
            "columns": [
                "type",
                "name",
                "enabled",
                "port",
                "mode",
                "min_tls",
                "max_tls",
                "pqc",
                "pqc_groups",
                "risks",
                "local_trusted_cas",
                "external_trusted_cas",
            ],
            "rows": [
                {
                    "type": r.get("interface_type") or "",
                    "name": r.get("name") or "",
                    "enabled": "yes" if r.get("enabled") else "no",
                    "port": "" if r.get("port") is None else str(r.get("port")),
                    "mode": r.get("mode") or "—",
                    "min_tls": r.get("minimum_tls_version") or "—",
                    "max_tls": r.get("maximum_tls_version") or "—",
                    "pqc": (
                        ("yes" if r.get("pqc_enabled") else "no")
                        if (r.get("pqc_applicable") is True
                            or str(r.get("interface_type") or "").lower() == "web"
                            or str(r.get("name") or "").lower() == "web")
                        else "n/a"
                    ),
                    "pqc_groups": (
                        (r.get("pqc_groups") or "—")
                        if (r.get("pqc_applicable") is True
                            or str(r.get("interface_type") or "").lower() == "web"
                            or str(r.get("name") or "").lower() == "web")
                        else "n/a"
                    ),
                    "risks": ", ".join(per_iface.get(str(r.get("name") or ""), [])) or "—",
                    "local_trusted_cas": r.get("local_trusted_cas") or "—",
                    "external_trusted_cas": r.get("external_trusted_cas") or "—",
                }
                for r in items
            ]
            or (
                [
                    {
                        "type": "—",
                        "name": err or "No interface data yet — wait for next ops scrape",
                        "enabled": "",
                        "port": "",
                        "mode": "",
                        "min_tls": "",
                        "max_tls": "",
                        "pqc": "",
                        "pqc_groups": "",
                        "risks": "",
                        "local_trusted_cas": "",
                        "external_trusted_cas": "",
                    }
                ]
            ),
        }
    )
    return panels


def build_explorer(store: ApplianceStore) -> list[dict[str, Any]]:
    """Raw metric browser summary by prefix."""
    samples = store.latest_samples()
    prefixes: dict[str, int] = {}
    for s in samples:
        prefix = s.name.split("_", 1)[0] + "_"
        prefixes[prefix] = prefixes.get(prefix, 0) + 1
    items = [{"label": k, "value": v} for k, v in sorted(prefixes.items(), key=lambda x: -x[1])]
    top = sorted(samples, key=lambda s: abs(s.value), reverse=True)[:25]
    return [
        _stat("Total Samples", float(len(samples))),
        _stat("Unique Metric Names", float(len({s.name for s in samples}))),
        _bar("Samples by Prefix", items),
        {
            "type": "table",
            "title": "Top Samples by Absolute Value",
            "columns": ["metric", "labels", "value"],
            "rows": [
                {
                    "metric": s.name,
                    "labels": ", ".join(f"{k}={v}" for k, v in s.labels.items()),
                    "value": s.value,
                }
                for s in top
            ],
        },
    ]


