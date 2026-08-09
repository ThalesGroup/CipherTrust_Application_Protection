"""CM Resources dashboards (Keys, Licensing, Domains, Audit, Crypto Ops, HSM, etc.)."""

from __future__ import annotations

from typing import Any

from ..store import ApplianceStore
from .panels import (
    _bar,
    _domain_name_map,
    _first_gauge,
    _group_by_account_friendly,
    _group_by_label_short,
    _keys_by_domain_from_deks,
    _named_series,
    _note,
    _rename_account_series,
    _short_account_label,
    _stat,
    _summed_by_label_series,
    _summed_series,
    _timeseries,
)


def _has_metric(store: ApplianceStore, name: str) -> bool:
    return any(s.name == name for s in store.latest_samples())


def build_resources_keys(
    store: ApplianceStore, appliance: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    del appliance  # Prometheus-only; REST /vault/keys2 is root-domain scoped.
    kek = _first_gauge(store, "ciphertrust_key_vault_keks_total", "ciphertrust_kek_count")
    has_rot = _has_metric(store, "ciphertrust_key_vault_key_rotations")
    has_create = _has_metric(store, "ciphertrust_key_vault_key_creations")
    rot_total = store.sum_value("ciphertrust_key_vault_key_rotations")
    rot_5m_sched = store.increase("ciphertrust_key_vault_key_rotations", {"source": "scheduler"}, 300)
    rot_5m_manual = store.increase("ciphertrust_key_vault_key_rotations", {"source": "manual"}, 300)
    has_deks = _has_metric(store, "ciphertrust_key_vault_deks_total")
    prom_keys = store.sum_value("ciphertrust_key_vault_deks_total") if has_deks else None
    # Sum all labeled DEK series — Prometheus covers the whole appliance (all domains).
    # REST /vault/keys2 only returns the logged-in (root) domain and must not be used here.
    keys_over_time = _summed_series(
        store,
        "ciphertrust_key_vault_deks_total",
        series_name="Total DEKs",
        limit_series=200,
    )
    keys_by_type_over_time = _summed_by_label_series(
        store,
        "ciphertrust_key_vault_deks_total",
        "algorithm",
        limit_series=200,
    )
    panels: list[dict[str, Any]] = [
        _stat("Total Keys", prom_keys),
        _stat("KEKs", kek),
        _stat("Key Creations", store.sum_value("ciphertrust_key_vault_key_creations") if has_create else None),
        _stat("Key Rotations Total", rot_total if has_rot else None),
        _stat("Rotations 5m (scheduler)", rot_5m_sched if has_rot else None),
        _stat("Rotations 5m (manual)", rot_5m_manual if has_rot else None),
        _timeseries(
            "Total Keys Over Time",
            keys_over_time,
            "keys",
            "Sum of ciphertrust_key_vault_deks_total across all domains (Prometheus).",
            wide=True,
        ),
        _timeseries(
            "Keys by Type Over Time",
            keys_by_type_over_time,
            "keys",
            "ciphertrust_key_vault_deks_total summed by algorithm label (AES, EC, RSA, …).",
            wide=True,
        ),
        _bar("Keys by Algorithm", store.group_by_label("ciphertrust_key_vault_deks_total", "algorithm")),
        _bar("Keys by State", store.group_by_label("ciphertrust_key_vault_deks_total", "state")),
        _bar(
            "Keys by Domain",
            _keys_by_domain_from_deks(store),
            "keys",
            "From ciphertrust_key_vault_deks_total (includes root). "
            "License-manager key_usage omits the root domain.",
        ),
    ]
    if has_create:
        id_to_name = _domain_name_map(store)
        create_series = _rename_account_series(
            _named_series(
                store,
                "ciphertrust_key_vault_key_creations",
                label_keys=["account_uri"],
                limit=12,
            ),
            id_to_name,
        )
        panels.extend(
            [
                _bar(
                    "Key Creations by Account",
                    _group_by_account_friendly(
                        store,
                        "ciphertrust_key_vault_key_creations",
                        "account_uri",
                        limit=15,
                        min_value=0,
                    ),
                    description="Mapped to domain names via license-manager key_usage when available.",
                ),
                _timeseries(
                    "Key Creations by Account Over Time",
                    create_series,
                    "ops",
                    "Per-account key creation counters (domain names when known).",
                    wide=True,
                ),
            ]
        )
    return panels


def build_resources_licensing(store: ApplianceStore) -> list[dict[str, Any]]:
    has_active = _has_metric(store, "ciphertrust_license_manager_number_of_active_connector_licenses")
    has_inactive = _has_metric(
        store, "ciphertrust_license_manager_number_of_inactive_connector_licenses"
    )
    # Sum across feature labels — gauge_value/first_value only returns one series.
    lic_active = (
        store.sum_value("ciphertrust_license_manager_number_of_active_connector_licenses")
        if has_active
        else None
    )
    lic_inactive = (
        store.sum_value("ciphertrust_license_manager_number_of_inactive_connector_licenses")
        if has_inactive
        else None
    )
    lic_units = store.sum_value("ciphertrust_license_manager_total_number_of_license_units")
    has_consumed = _has_metric(store, "ciphertrust_license_manager_number_of_consumed_license_units")
    lic_consumed = (
        store.sum_value("ciphertrust_license_manager_number_of_consumed_license_units")
        if has_consumed
        else None
    )
    lic_pct = None
    if has_consumed and lic_units and lic_consumed is not None and lic_units > 0:
        lic_pct = (lic_consumed / lic_units) * 100

    panels: list[dict[str, Any]] = [
        _stat(
            "Active Connector Licenses",
            lic_active,
            description="Sum of number_of_active_connector_licenses across features",
        ),
        _stat(
            "Inactive Connector Licenses",
            lic_inactive,
            description="Sum of number_of_inactive_connector_licenses across features",
        ),
    ]
    # Only show consumed panels when CM exports the metric (absent on some 2.23 builds).
    if has_consumed:
        panels.extend(
            [
                _stat("License Units Consumed", lic_consumed),
                _stat("License Consumption", lic_pct, "%"),
            ]
        )
    else:
        panels.append(
            _note(
                "This appliance does not export ciphertrust_license_manager_number_of_consumed_license_units "
                "(common on some CM 2.23 builds). Entitled units and connector licenses below are still available. "
                "Orphaned resources are under Domains & Users.",
                title="License consumption not exported",
            )
        )
    panels.extend(
        [
            _bar(
                "Active Connector Licenses by Feature",
                store.group_by_label(
                    "ciphertrust_license_manager_number_of_active_connector_licenses", "feature"
                ),
                description="From number_of_active_connector_licenses (not inactive).",
            ),
            _bar(
                "Inactive Connector Licenses by Feature",
                store.group_by_label(
                    "ciphertrust_license_manager_number_of_inactive_connector_licenses", "feature"
                ),
                description="From number_of_inactive_connector_licenses — sums to the Inactive total.",
            ),
        ]
    )
    if has_consumed:
        panels.append(
            _bar(
                "License Units Consumed by Feature",
                store.group_by_label(
                    "ciphertrust_license_manager_number_of_consumed_license_units", "feature"
                ),
                "units",
            )
        )
    panels.append(
        _bar(
            "License Units Entitled by Feature",
            store.group_by_label(
                "ciphertrust_license_manager_total_number_of_license_units", "feature"
            ),
            "units",
        )
    )
    return panels


def build_resources_domains(store: ApplianceStore) -> list[dict[str, Any]]:
    has_orphan = _has_metric(store, "ciphertrust_license_manager_orphaned_resources_total")
    has_orphan_acct = _has_metric(
        store, "ciphertrust_license_manager_orphaned_resources_by_account"
    )
    panels: list[dict[str, Any]] = [
        _stat(
            "Domains",
            store.gauge_value("ciphertrust_license_manager_number_of_subdomains"),
        ),
        _stat("Total Users", store.gauge_value("ciphertrust_user_management_total_users")),
        _stat("Group Users", store.gauge_value("ciphertrust_user_management_group_users")),
        _stat("Platform Tenants", store.gauge_value("ciphertrust_platform_tenants_total")),
        _stat(
            "Orphaned Resources",
            store.sum_value("ciphertrust_license_manager_orphaned_resources_total")
            if has_orphan
            else None,
            description="Leftovers from deleted domains (license_manager orphaned_resources_total).",
        ),
        _bar(
            "Keys by Domain",
            _keys_by_domain_from_deks(store),
            "keys",
            "From ciphertrust_key_vault_deks_total (includes root).",
        ),
        _bar(
            "Subdomain Nesting Count",
            _group_by_label_short(
                store,
                "ciphertrust_license_manager_subdomain_usage_count_including_subdomains_count",
                "domain_name",
                limit=15,
                min_value=0,
            ),
        ),
    ]
    if has_orphan:
        panels.append(
            _bar(
                "Orphaned Resources by Type",
                [
                    i
                    for i in store.group_by_label(
                        "ciphertrust_license_manager_orphaned_resources_total", "resource_type"
                    )
                    if (i.get("value") or 0) > 0
                ],
                description="Keys and other resources left after domain deletion.",
            )
        )
    if has_orphan_acct:
        panels.append(
            _bar(
                "Orphaned Keys by Account",
                _group_by_account_friendly(
                    store,
                    "ciphertrust_license_manager_orphaned_resources_by_account",
                    "account",
                    limit=15,
                    min_value=0,
                ),
                description="Orphaned resources by deleted account — domain name when still known, else short id.",
            )
        )
    return panels


def build_resources_audit(store: ApplianceStore) -> list[dict[str, Any]]:
    audit_rate = store.rate("ciphertrust_audit_log_records_total", {"service": "audit_log"})
    audit_total = store.gauge_value("ciphertrust_audit_log_records_total", {"service": "audit_log"})
    audit_5m = store.increase("ciphertrust_audit_log_records_total", {"service": "audit_log"}, 300)
    return [
        _stat("Audit Records Total", audit_total),
        _stat("Audit Records /s", audit_rate, "rec/s"),
        _stat("Audit Records (5m)", audit_5m),
        _stat(
            "Client Audit Logs",
            store.gauge_value("ciphertrust_audit_log_client_logs_total", {"service": "audit_log"}),
        ),
        _timeseries(
            "Audit Records Created Per Second",
            _named_series(store, "ciphertrust_audit_log_records_total", {"service": "audit_log"}, rate=True),
            "rec/s",
        ),
    ]


def build_resources_crypto_ops(store: ApplianceStore) -> list[dict[str, Any]]:
    enc = store.rate(
        "http_response_time_seconds_count",
        {"code": "200", "method": "POST", "path": "/encrypt", "service": "crypto"},
    )
    dec = store.rate(
        "http_response_time_seconds_count",
        {"code": "200", "method": "POST", "path": "/decrypt", "service": "crypto"},
    )
    nae_crypto = store.rate(
        "ciphertrust_nae_nae_key_management_operation_success",
        {"operation": "Cryptographic Operation"},
    )
    kmip_enc = store.rate("ciphertrust_nae_kmip_operation_success", {"operation": "Encrypt"})
    kmip_dec = store.rate("ciphertrust_nae_kmip_operation_success", {"operation": "Decrypt"})
    has_crypto_dec = _has_metric(store, "ciphertrust_crypto_decrypt_requests_total")
    crypto_dec_total = (
        store.sum_value("ciphertrust_crypto_decrypt_requests_total") if has_crypto_dec else None
    )
    crypto_dec_rate = (
        store.rate("ciphertrust_crypto_decrypt_requests_total") if has_crypto_dec else None
    )
    http_enc_series = _named_series(
        store,
        "http_response_time_seconds_count",
        {"method": "POST", "path": "/encrypt", "service": "crypto"},
        rate=True,
        label_keys=["code", "path"],
        limit=8,
    )
    http_dec_series = _named_series(
        store,
        "http_response_time_seconds_count",
        {"method": "POST", "path": "/decrypt", "service": "crypto"},
        rate=True,
        label_keys=["code", "path"],
        limit=8,
    )
    panels: list[dict[str, Any]] = [
        _stat("Encrypt ops/s (HTTP)", enc, "ops/s"),
        _stat("Decrypt ops/s (HTTP)", dec, "ops/s"),
        _stat(
            "Crypto Decrypt Requests",
            crypto_dec_total,
            description="ciphertrust_crypto_decrypt_requests_total (when exported).",
        ),
        _stat("Crypto Decrypt /s", crypto_dec_rate, "ops/s"),
        _stat("NAE Crypto ops/s", nae_crypto, "ops/s"),
        _stat("KMIP Encrypt ops/s", kmip_enc, "ops/s"),
        _stat("KMIP Decrypt ops/s", kmip_dec, "ops/s"),
        _timeseries(
            "HTTP Encrypt Ops",
            http_enc_series,
            "ops/s",
            "POST /encrypt on service=crypto (http_response_time_seconds_count rate).",
            wide=True,
        ),
        _timeseries(
            "HTTP Decrypt Ops",
            http_dec_series,
            "ops/s",
            "POST /decrypt on service=crypto (http_response_time_seconds_count rate).",
            wide=True,
        ),
    ]
    if has_crypto_dec:
        id_to_name = _domain_name_map(store)
        dec_series = _rename_account_series(
            _named_series(
                store,
                "ciphertrust_crypto_decrypt_requests_total",
                rate=True,
                label_keys=["account_uri"],
                limit=12,
            ),
            id_to_name,
        )
        panels.extend(
            [
                _bar(
                    "Crypto Decrypt Requests by Account",
                    _group_by_account_friendly(
                        store,
                        "ciphertrust_crypto_decrypt_requests_total",
                        "account_uri",
                        limit=15,
                        min_value=0,
                    ),
                    description="Mapped to domain names via license-manager key_usage when available.",
                ),
                _timeseries(
                    "Crypto Decrypt Requests /s by Account",
                    dec_series,
                    "ops/s",
                    "Rate of ciphertrust_crypto_decrypt_requests_total by account.",
                    wide=True,
                ),
            ]
        )
    panels.extend(
        [
            _timeseries(
                "NAE Cryptographic Operations",
                _named_series(
                    store,
                    "ciphertrust_nae_nae_key_management_operation_success",
                    {"operation": "Cryptographic Operation"},
                    rate=True,
                    label_keys=["operation"],
                ),
                "ops/s",
            ),
            _timeseries(
                "KMIP Encrypt/Decrypt Success",
                [
                    *_named_series(
                        store,
                        "ciphertrust_nae_kmip_operation_success",
                        {"operation": "Encrypt"},
                        rate=True,
                        label_keys=["operation"],
                    ),
                    *_named_series(
                        store,
                        "ciphertrust_nae_kmip_operation_success",
                        {"operation": "Decrypt"},
                        rate=True,
                        label_keys=["operation"],
                    ),
                ],
                "ops/s",
            ),
        ]
    )
    return panels


def build_resources_hsm(store: ApplianceStore) -> list[dict[str, Any]]:
    """HSM session metrics only — backups live under Ops → Backups."""
    return [
        _stat("HSM Active Sessions", store.gauge_value("ciphertrust_hsm_active_sessions")),
        _timeseries(
            "HSM Active Sessions",
            _named_series(store, "ciphertrust_hsm_active_sessions", limit=1),
        ),
    ]


# Alias kept for older imports / combined board.
build_resources_hsm_backups = build_resources_hsm


def build_resources_cckm(store: ApplianceStore) -> list[dict[str, Any]]:
    return [
        _stat(
            "CCKM Endpoints",
            store.gauge_value("ciphertrust_ciphertrust_cloud_key_manager_endpoints_total"),
        ),
        _stat(
            "CCKM Issuers",
            store.gauge_value("ciphertrust_ciphertrust_cloud_key_manager_issuers_total"),
        ),
        _stat(
            "CCKM Perimeters",
            store.gauge_value("ciphertrust_ciphertrust_cloud_key_manager_perimeters_total"),
        ),
    ]


# Backward-compatible alias: full board (unused by catalog chips, kept for imports/tests).
def build_resources(
    store: ApplianceStore, appliance: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return [
        *build_resources_keys(store, appliance),
        *build_resources_licensing(store),
        *build_resources_domains(store),
        *build_resources_audit(store),
        *build_resources_crypto_ops(store),
        *build_resources_hsm_backups(store),
        *build_resources_cckm(store),
    ]
