"""Security posture rules applied to live REST ops data (healthcheck-equivalent).

These mirror vendor/healthcheck checks but run against the scheduled ops snapshot
(/configs/interfaces, /configs/properties) — no healthcheck job required.
"""

from __future__ import annotations

from typing import Any

# Documented defaults from ksctl properties list --help (same set as healthcheck).
DEFAULT_PROPERTIES: dict[str, str] = {
    "UI_IDLE_SESSION_TIMEOUT": "10m",
    "MAXIMUM_REFRESH_TOKEN_LIFETIME": "",
    "LOAD_BALANCER_ADDRESS": "",
    "HIDE_COMPOSITE_KEY": "false",
    "DEPRECATED_LEGACY_SYSLOG": "true",
    "CERT_REV_CHECK_TIMEOUT": "5",
    "ALLOW_USER_IMPERSONATION_ACROSS_DOMAIN": "false",
    "ALLOW_UNKNOWN_FIELDS": "false",
    "NAE_KEY_VERSION_FOR_OPERATIONS": "latest_key_version",
    "NAE_AUTH_RESPONSE_FOR_INTERNAL_SERVER_ERROR": "",
    "KEY_CACHE_EXPIRES_DURATION": "2",
    "ENFORCE_NAE_CLIENT_VALIDATION": "false",
    "ENFORCE_NAE_CLIENT_REGISTRATION": "false",
    "ENABLE_NAE_CRYPTO_RECORDS": "false",
    "ENABLE_NAE_ACTIVITY_LOGS": "false",
    "ENABLE_KMIP_ACTIVITY_LOGS": "false",
    "ENABLE_CERT_REV_CHECK": "true",
    "DISABLE_TLS_SESSION_RESUMPTION": "false",
    "PASSWORD_HASH_ITERATIONS": "10000",
    "KEY_STATES_METRIC_INTERVAL": "3600",
    "ENABLE_REST_CRYPTO_RECORDS": "false",
    "ENABLE_KEY_CACHE": "false",
    "PREVENT_DELETE_INUSE_CONNECTIONS": "true",
    "ENABLE_RECORDS_DB_STORE": "false",
    "ENABLE_ML_KEM_FOR_CLUSTER": "false",
    "CLUSTER_CERT_AUTO_RENEW_THRESHOLD": "30",
}

INSECURE_INTERFACE_MODES = frozenset(
    {
        "no-tls-pw-opt",
        "no-tls-pw-req",
        "unauth-tls-pw-opt",
        "unauth-tls-pw-req",
    }
)

# Normalized forms of weak minimum TLS (raw CM enums + display labels).
_WEAK_TLS_NORMALIZED = frozenset(
    {
        "ssl_v3",
        "sslv3",
        "tls_1_0",
        "tls1_0",
        "tls 1.0",
        "tls_1_1",
        "tls1_1",
        "tls 1.1",
    }
)


def _norm_tls(value: Any) -> str:
    text = str(value or "").strip().lower().replace("-", "_")
    text = text.replace("tls_", "tls ").replace("tls1_", "tls 1.")
    # Also accept already-pretty "TLS 1.0"
    pretty = str(value or "").strip().lower()
    return pretty if pretty.startswith("tls ") else text.replace(" ", "_")


def is_weak_min_tls(value: Any) -> bool:
    if value is None or value == "" or value == "—":
        return False
    raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    pretty = str(value).strip().lower()
    return raw in _WEAK_TLS_NORMALIZED or pretty in _WEAK_TLS_NORMALIZED


def is_insecure_mode(mode: Any) -> bool:
    return str(mode or "").strip().lower() in INSECURE_INTERFACE_MODES


def _is_web_interface(row: dict[str, Any]) -> bool:
    """PQC TLS groups apply to the Web UI interface only (not NAE/KMIP/SSH/SNMP)."""
    itype = str(row.get("interface_type") or "").strip().lower()
    name = str(row.get("name") or "").strip().lower()
    return itype == "web" or name == "web"


def evaluate_interfaces(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply healthcheck-equivalent interface rules to ops snapshot rows."""
    findings: list[dict[str, str]] = []
    per_iface: dict[str, list[str]] = {}
    fail = warn = 0
    insecure_modes = weak_tls = no_pqc = disabled = 0

    for row in items:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or row.get("interface_type") or "?")
        enabled = bool(row.get("enabled"))
        mode = row.get("mode")
        min_tls = row.get("minimum_tls_version")
        pqc = bool(row.get("pqc_enabled"))
        is_web = _is_web_interface(row)
        flags: list[str] = []

        if not enabled:
            disabled += 1
            warn += 1
            msg = f"Service Interface '{name}' is DISABLED."
            findings.append({"severity": "WARNING", "code": "net_interface_disabled", "message": msg})
            flags.append("disabled")

        if is_insecure_mode(mode):
            insecure_modes += 1
            fail += 1
            msg = f"Service Interface '{name}' is using insecure mode: '{mode}'."
            findings.append(
                {"severity": "FAIL", "code": "net_interface_insecure_mode", "message": msg}
            )
            flags.append(f"insecure mode ({mode})")

        if is_weak_min_tls(min_tls):
            weak_tls += 1
            fail += 1
            msg = (
                f"Service Interface '{name}' is configured with insecure minimum TLS version: "
                f"'{min_tls}'."
            )
            findings.append({"severity": "FAIL", "code": "net_interface_weak_tls", "message": msg})
            flags.append(f"weak TLS ({min_tls})")

        # PQC key-exchange groups are only meaningful on the Web interface.
        if is_web and enabled and not pqc:
            no_pqc += 1
            warn += 1
            msg = (
                f"Service Interface '{name}' does not have any Post-Quantum Cryptography "
                "(PQC) key exchange support enabled."
            )
            findings.append({"severity": "WARNING", "code": "net_interface_no_pqc", "message": msg})
            flags.append("no PQC")

        if flags:
            per_iface[name] = flags

    overall = "PASS"
    if fail:
        overall = "FAIL"
    elif warn:
        overall = "WARNING"

    return {
        "overall": overall,
        "fail": fail,
        "warn": warn,
        "insecure_modes": insecure_modes,
        "weak_tls": weak_tls,
        "no_pqc": no_pqc,
        "disabled": disabled,
        "findings": findings,
        "per_iface": per_iface,
    }


def evaluate_modified_properties(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Flag properties whose value differs from documented defaults."""
    modified: list[dict[str, str]] = []
    for row in items:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "")
        if not name or name not in DEFAULT_PROPERTIES:
            continue
        current = "" if row.get("value") is None else str(row.get("value"))
        default = DEFAULT_PROPERTIES[name]
        if current != default:
            modified.append(
                {
                    "name": name,
                    "value": current,
                    "default": default,
                    "description": str(row.get("description") or ""),
                }
            )

    modified.sort(key=lambda r: r["name"].lower())
    return {
        "known_defaults": len(DEFAULT_PROPERTIES),
        "modified_count": len(modified),
        "modified": modified,
    }
