import getpass
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from typing import Any, Callable, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

# Set target paths
OUTPUT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthcheck_report.html")
OUTPUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthcheck_data.json")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Severities treated as "above Info" for event records (see 'ksctl records/client-records list --help').
SIGNIFICANT_SEVERITIES = {"error", "critical", "fatal"}

# Documented default values for system properties (see 'ksctl properties list --help').
# Used to detect administrator-modified properties worth flagging for review.
DEFAULT_PROPERTIES = {
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
    "CLUSTER_CERT_AUTO_RENEW_THRESHOLD": "30"
}


def first_present(d: Dict[str, Any], *names: str) -> Optional[Any]:
    """Returns the first non-None value found in d for any of the given key names."""
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return None


def collapse_key_versions(keys_raw: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Groups raw key resources by name and keeps only the highest version of each."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for k in keys_raw:
        name = k.get("name")
        if name:
            grouped.setdefault(name, []).append(k)
    return {name: max(versions, key=lambda x: x.get("version", 0)) for name, versions in grouped.items()}

def run_ksctl_cmd(args: List[str], suppress_errors: bool = False) -> Dict[str, Any]:
    """Runs a ksctl command and returns the parsed JSON, or None if error."""
    full_cmd = ["ksctl"] + args + ["--respfmt", "json"]
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except subprocess.CalledProcessError as e:
        if not suppress_errors:
            print(f"Error executing command: {' '.join(full_cmd)}")
            print(f"Exit code: {e.returncode}")
            print(f"Stderr: {e.stderr}")
        try:
            return json.loads(e.stdout)
        except Exception:
            return {"error": e.stderr.strip() or f"Process failed with exit code {e.returncode}"}
    except Exception as e:
        if not suppress_errors:
            print(f"Unexpected error running {' '.join(full_cmd)}: {str(e)}")
        return {"error": str(e)}

def run_ksctl_list_all(args: List[str]) -> Dict[str, Any]:
    """Runs a ksctl list command, automatically paging until all resources are retrieved."""
    page_size = 500
    skip = 0
    all_resources = []

    clean_args = []
    i = 0
    while i < len(args):
        if args[i] in ["--limit", "-l", "--skip", "-s"]:
            i += 2
        else:
            clean_args.append(args[i])
            i += 1

    while True:
        cmd_args = clean_args + ["--limit", str(page_size), "--skip", str(skip)]
        # Errors are suppressed here because "unknown flag" is an expected outcome for
        # commands that don't support pagination, not a real failure - so we retry quietly
        # instead of printing a scary error message on every such command.
        res = run_ksctl_cmd(cmd_args, suppress_errors=True)
        error = res.get("error") if isinstance(res, dict) else None
        if isinstance(error, str) and "unknown flag" in error:
            print(f"Note: '{' '.join(['ksctl'] + clean_args)}' does not support pagination; retrying without --limit/--skip.")
            return run_ksctl_cmd(clean_args)

        if error is not None:
            print(f"Error executing command: {' '.join(['ksctl'] + cmd_args + ['--respfmt', 'json'])}")
            print(f"Stderr: {error}")

        if not isinstance(res, dict) or "resources" not in res:
            return res
            
        resources = res.get("resources", [])
        all_resources.extend(resources)
        
        total = res.get("total", 0)
        limit = res.get("limit", page_size) or page_size
        
        if len(all_resources) >= total or not resources or len(resources) < limit:
            break
            
        skip += limit
        
    res["resources"] = all_resources
    res["skip"] = 0
    res["limit"] = len(all_resources)
    res["total"] = len(all_resources)
    return res
def filter_interesting_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filters the collected raw diagnostic data to retain only compliance-interesting information."""
    now = datetime.now(timezone.utc)
    
    # 1. Filter Users
    users_raw = data.get("users", {}).get("resources", [])
    interesting_users = []
    for u in users_raw:
        last_login = parse_date(u.get("last_login"))
        failed_cnt = u.get("failed_logins_count", 0)
        lockout_at = u.get("account_lockout_at")
        lf = u.get("login_flags", {})
        
        is_locked = lockout_at is not None
        is_inactive = last_login is None or (now - last_login).days > 30
        has_login_flag = isinstance(lf, dict) and lf.get("login_flags") is True
        has_failed = failed_cnt > 0
        
        if is_locked or is_inactive or has_login_flag or has_failed:
            interesting_users.append(u)
    if "users" in data and "resources" in data["users"]:
        data["users"]["resources"] = interesting_users
        data["users"]["total"] = len(interesting_users)
        
    # 2. Filter Keys (Collapse versions, keep only latest version of each unique key)
    keys_raw = data.get("keys", {}).get("resources", [])
    grouped_keys = {}
    for k in keys_raw:
        name = k.get("name")
        if name:
            grouped_keys.setdefault(name, []).append(k)

    collapsed = collapse_key_versions(keys_raw)
    interesting_keys = []
    for name, latest_key in collapsed.items():
        latest_key["_version_count"] = len(grouped_keys[name])
        interesting_keys.append(latest_key)

    if "keys" in data and "resources" in data["keys"]:
        data["keys"]["resources"] = interesting_keys
        data["keys"]["total"] = len(interesting_keys)
        
    # 3. Filter Backups (Keep latest 10 backups plus any backup referencing an issue)
    backups_raw = data.get("backups", {}).get("resources", [])
    backup_keys_raw = data.get("backup_keys", {}).get("resources", [])
    known_backup_key_ids = {bk.get("id"): bk for bk in backup_keys_raw}
    
    interesting_backups = []
    sorted_backups = sorted(backups_raw, key=lambda b: b.get("createdAt", ""), reverse=True)
    
    for idx, b in enumerate(sorted_backups):
        key_id = b.get("backupKey")
        has_issue = False
        if key_id:
            if key_id not in known_backup_key_ids:
                has_issue = True
            elif known_backup_key_ids[key_id].get("state") != "active":
                has_issue = True
        
        if idx < 10 or has_issue:
            interesting_backups.append(b)
            
    if "backups" in data and "resources" in data["backups"]:
        data["backups"]["resources"] = interesting_backups
        data["backups"]["total"] = len(interesting_backups)
        
    # 4. Filter Alarms (Keep only active, unacknowledged alarms)
    alarms_raw = data.get("alarms", {}).get("resources", [])
    interesting_alarms = [a for a in alarms_raw if a.get("state") == "on" and a.get("acknowledgedAt") is None]
    if "alarms" in data and "resources" in data["alarms"]:
        data["alarms"]["resources"] = interesting_alarms
        data["alarms"]["total"] = len(interesting_alarms)
        
    # 5. Filter Properties (Keep only modified properties)
    props_raw = data.get("properties", {}).get("resources", [])
    interesting_props = []
    for prop in props_raw:
        name = prop.get("name")
        val = prop.get("value")
        default_val = DEFAULT_PROPERTIES.get(name)
        if default_val is not None and val != default_val:
            interesting_props.append(prop)
            
    if "properties" in data and "resources" in data["properties"]:
        data["properties"]["resources"] = interesting_props
        data["properties"]["total"] = len(interesting_props)
        
    # 6. Filter Quorum Policies (Keep only active quorum policies)
    qp_raw = data.get("quorum_policies", {}).get("resources", [])
    interesting_qps = [qp for qp in qp_raw if qp.get("active") is True]
    if "quorum_policies" in data and "resources" in data["quorum_policies"]:
        data["quorum_policies"]["resources"] = interesting_qps
        data["quorum_policies"]["total"] = len(interesting_qps)
        
    # 7. Filter Services (Keep only non-started system services)
    if "services" in data:
        svc_raw = data["services"].get("services", [])
        interesting_svcs = [s for s in svc_raw if s.get("status") != "started"]
        data["services"]["services"] = interesting_svcs
        
    # 8. Filter Groups (Keep only custom groups where app_metadata.system is false)
    if "groups" in data:
        groups_raw = data["groups"].get("resources", [])
        custom_groups = []
        for g in groups_raw:
            meta = g.get("app_metadata")
            is_system = isinstance(meta, dict) and meta.get("system") is True
            if not is_system:
                custom_groups.append(g)
        data["groups"]["resources"] = custom_groups
        data["groups"]["total"] = len(custom_groups)
        
    # 9. Filter Trusted CAs (Drop huge PEM certs to save context space)
    if "trusted_ca_certs" in data:
        ca_raw = data["trusted_ca_certs"].get("resources", [])
        for ca in ca_raw:
            ca_details = ca.get("ca_details")
            if isinstance(ca_details, dict) and "cert" in ca_details:
                ca_details["cert"] = "[PEM Certificate Block Omitted for Brevity]"
                
    # 10. Filter Local CAs (Drop huge PEM certs)
    if "local_cas" in data:
        ca_raw = data["local_cas"].get("resources", [])
        for ca in ca_raw:
            if "cert" in ca:
                ca["cert"] = "[PEM Certificate Block Omitted for Brevity]"

    # 11. Filter External CAs (Drop huge PEM certs)
    if "external_cas" in data:
        ca_raw = data["external_cas"].get("resources", [])
        for ca in ca_raw:
            if "cert" in ca:
                ca["cert"] = "[PEM Certificate Block Omitted for Brevity]"

    # 12. Filter Connections (Redact secrets/certs, keep only LDAP connections since
    # OIDC/zone connections aren't relevant to the TLS validation checks in this report)
    if "connections" in data:
        conn_raw = data["connections"].get("resources", [])
        ldap_conns = []
        for conn in conn_raw:
            strategy = (conn.get("strategy") or conn.get("connection_type") or "").lower()
            if strategy != "ldap":
                continue
            conn = dict(conn)
            for secret_field in ("bind_password", "client_secret"):
                if secret_field in conn:
                    conn[secret_field] = "[REDACTED]"
            if conn.get("root_ca"):
                conn["root_ca"] = "[PEM Certificate Block Omitted for Brevity]"
            ldap_conns.append(conn)
        data["connections"]["resources"] = ldap_conns
        data["connections"]["total"] = len(ldap_conns)

    # 13. Filter Clients (Drop huge PEM cert/csr blocks; not needed for reporting)
    if "clients" in data:
        clients_raw = data["clients"].get("resources", [])
        for c in clients_raw:
            if "cert" in c:
                c["cert"] = "[PEM Certificate Block Omitted for Brevity]"
            if "csr" in c:
                c["csr"] = "[PEM CSR Block Omitted for Brevity]"

    # 14. Filter Event Records (Keep only records with severity above INFO)
    for records_key in ("server_event_records", "client_event_records"):
        if records_key in data:
            records_raw = data[records_key].get("resources", [])
            interesting_records = [r for r in records_raw if (r.get("severity") or "").lower() in SIGNIFICANT_SEVERITIES]
            data[records_key]["resources"] = interesting_records
            data[records_key]["total"] = len(interesting_records)

    return data



def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    clean_str = date_str.split(".")[0].rstrip("Z")
    # Some fields (e.g. license/feature expiration) are returned as a bare date
    # instead of a full timestamp, so a date-only format is tried as a fallback.
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(clean_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None

def format_readable_date(date_str: Optional[str]) -> str:
    dt = parse_date(date_str)
    if not dt:
        return "Never"
    return dt.strftime("%Y-%m-%d %H:%M")

def analyze_health(data: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        "status": "PASS",
        "system": {"status": "PASS", "issues": [], "metrics": {}},
        "access": {"status": "PASS", "issues": [], "metrics": {}},
        "keys": {"status": "PASS", "issues": [], "metrics": {}},
        "clients": {"status": "PASS", "issues": [], "metrics": {}},
        "licensing": {"status": "PASS", "issues": [], "metrics": {}},
        "network": {"status": "PASS", "issues": [], "metrics": {}},
        "domains": {"status": "PASS", "issues": [], "metrics": {}},
        "ca": {"status": "PASS", "issues": [], "metrics": {}},
        "records": {"status": "PASS", "issues": [], "metrics": {}}
    }
    
    now = datetime.now(timezone.utc)
    
    # 1. Licensing Checks
    licenses = data.get("licenses", {}).get("resources", [])
    features = data.get("features", {}).get("resources", [])
    trials = data.get("trials", {}).get("resources", [])
    lockdata = data.get("lockdata", {})

    def has_real_expiration(exp_str: Optional[str]) -> bool:
        return bool(exp_str) and exp_str.strip().lower() != "no expiration"

    has_active_trial = any(t.get("status") == "activated" for t in trials)
    results["licensing"]["metrics"]["has_active_trial"] = has_active_trial
    results["licensing"]["metrics"]["lock_code"] = lockdata.get("code")
    results["licensing"]["metrics"]["cluster_lock_code"] = lockdata.get("cluster_code")
    if has_active_trial:
        results["licensing"]["issues"].append({
            "code": "lic_trial_mode_active",
            "severity": "INFO",
            "message": "CipherTrust Manager trial mode is active."
        })

    def check_expiration(item_label: str, name: Optional[str], state_or_status: Optional[str], exp_str: Optional[str], code_prefix: str) -> str:
        """Flags FAIL/WARNING for expired/expiring items and returns 'expired', 'expiring', or ''."""
        if state_or_status == "expired":
            results["licensing"]["issues"].append({
                "code": f"{code_prefix}_expired",
                "severity": "FAIL",
                "message": f"{item_label} '{name}' is EXPIRED."
            })
            results["licensing"]["status"] = "FAIL"
            return "expired"

        if not has_real_expiration(exp_str):
            return ""

        exp_date = parse_date(exp_str)
        if not exp_date:
            results["licensing"]["issues"].append({
                "code": f"{code_prefix}_expiration_unparseable",
                "severity": "INFO",
                "message": f"{item_label} '{name}' has an unrecognized expiration value ('{exp_str}') that could not be evaluated."
            })
            return ""

        days_left = (exp_date - now).days
        if days_left < 0:
            results["licensing"]["issues"].append({
                "code": f"{code_prefix}_expired",
                "severity": "FAIL",
                "message": f"{item_label} '{name}' is EXPIRED ({abs(days_left)} days ago)."
            })
            results["licensing"]["status"] = "FAIL"
            return "expired"
        elif days_left <= 30:
            results["licensing"]["issues"].append({
                "code": f"{code_prefix}_expiring",
                "severity": "WARNING",
                "message": f"{item_label} '{name}' expires in {days_left} days."
            })
            if results["licensing"]["status"] != "FAIL":
                results["licensing"]["status"] = "WARNING"
            return "expiring"
        return ""

    # Trial licenses' "expiration" field is consistently "no expiration", even
    # while on a live trial countdown, so trial_seconds_remaining is used instead.
    expired_lics = 0
    expiring_soon_lics = 0
    for lic in licenses:
        state = lic.get("state")
        sec_rem = lic.get("trial_seconds_remaining", 0)
        lic["trial_days_remaining"] = sec_rem // 86400 if sec_rem else None

        if state == "inactive":
            continue

        outcome = check_expiration("License for feature", lic.get("feature"), state, lic.get("expiration"), code_prefix="license")
        if outcome == "expired":
            expired_lics += 1
        elif outcome == "expiring":
            expiring_soon_lics += 1

        if lic.get("type") == "trial" and lic["trial_days_remaining"] is not None and lic["trial_days_remaining"] <= 30:
            expiring_soon_lics += 1
            results["licensing"]["issues"].append({
                "code": "license_trial_expiring",
                "severity": "WARNING",
                "message": f"Trial license for feature '{lic.get('feature')}' expires in {lic['trial_days_remaining']} days."
            })
            if results["licensing"]["status"] != "FAIL":
                results["licensing"]["status"] = "WARNING"

    # Feature expiration is driven by trial_seconds_remaining rather than the
    # "expiration" field, which is consistently "no expiration" even for features
    # on a live trial countdown.
    expired_features = 0
    expiring_soon_features = 0
    for feat in features:
        status = feat.get("status")
        fname = feat.get("name")
        sec_rem = feat.get("trial_seconds_remaining", 0)
        days_left = sec_rem // 86400 if sec_rem else None
        feat["trial_days_remaining"] = days_left

        if status == "inactive":
            continue

        if status == "expired":
            expired_features += 1
            results["licensing"]["issues"].append({
                "code": "feature_expired",
                "severity": "FAIL",
                "message": f"Licensed feature '{fname}' is EXPIRED."
            })
            results["licensing"]["status"] = "FAIL"
        elif days_left is not None and days_left <= 30:
            expiring_soon_features += 1
            results["licensing"]["issues"].append({
                "code": "feature_expiring",
                "severity": "WARNING",
                "message": f"Licensed feature '{fname}' expires in {days_left} days."
            })
            if results["licensing"]["status"] != "FAIL":
                results["licensing"]["status"] = "WARNING"

    results["licensing"]["metrics"]["expired_licenses"] = expired_lics
    results["licensing"]["metrics"]["expiring_soon_licenses"] = expiring_soon_lics
    results["licensing"]["metrics"]["expired_features"] = expired_features
    results["licensing"]["metrics"]["expiring_soon_features"] = expiring_soon_features

    # 2. System Check (incorporating NTP, Backups, Cluster, Banners, Disk encryption, Alarms)
    sys_info = data.get("system_info", {})
    ntp_status = data.get("ntp_status", {})
    backups = data.get("backups", {}).get("resources", [])
    backup_keys = data.get("backup_keys", {}).get("resources", [])
    scheduler_configs = data.get("scheduler_configs", {}).get("resources", [])
    cluster_info = data.get("cluster_info", {})
    cluster_nodes = data.get("cluster_nodes", {}).get("resources", [])
    cluster_errors = data.get("cluster_errors")
    banner_data = data.get("banner", {})
    diskenc = data.get("disk_encryption", {})
    alarms = data.get("alarms", {}).get("resources", [])
    
    # NTP Check
    ntp_ok = False
    ntp_err = False
    if ntp_status and "ntpq -p" in ntp_status:
        ntpq_p = ntp_status["ntpq -p"]
        if "*" in ntpq_p:
            ntp_ok = True
        if "error" in ntp_status or "timeout" in ntpq_p.lower():
            ntp_err = True
            
    results["system"]["metrics"]["ntp_synced"] = ntp_ok
    if not ntp_ok or ntp_err:
        results["system"]["issues"].append({
            "code": "sys_ntp_not_synced",
            "severity": "WARNING",
            "message": "NTP time synchronization is not active or has sync errors."
        })
        results["system"]["status"] = "WARNING"

    # NTP Servers Configured Check
    ntp_servers = data.get("ntp_servers", {}).get("resources", [])
    results["system"]["metrics"]["ntp_servers_count"] = len(ntp_servers)
    if not ntp_servers:
        results["system"]["issues"].append({
            "code": "sys_ntp_no_servers",
            "severity": "WARNING",
            "message": "No NTP servers are configured."
        })
        results["system"]["status"] = "WARNING"

    # Disk Encryption Check
    results["system"]["metrics"]["disk_encryption_status"] = diskenc.get("encryptionStatus", "unknown")
    if diskenc.get("attendedBoot") is True:
        results["system"]["issues"].append({
            "code": "sys_disk_encryption_attended_boot",
            "severity": "WARNING",
            "message": "Disk encryption attendedBoot is ENABLED (requires manual passphrase entry on boot)."
        })
        results["system"]["status"] = "WARNING"

    # Logon Banner Check
    if not banner_data.get("value"):
        results["system"]["issues"].append({
            "code": "sys_no_login_banner",
            "severity": "WARNING",
            "message": "No pre-authentication login banner is configured."
        })
        results["system"]["status"] = "WARNING"

    # Backup Schedule Checks
    has_scheduled_backup = any(s.get("operation") == "database_backup" and not s.get("disabled") for s in scheduler_configs)
    results["system"]["metrics"]["has_scheduled_backup"] = has_scheduled_backup
    if not has_scheduled_backup:
        results["system"]["issues"].append({
            "code": "sys_no_scheduled_backup",
            "severity": "WARNING",
            "message": "No scheduled system backup job is active."
        })
        results["system"]["status"] = "WARNING"

    # Backup Age Check
    if not backups:
        results["system"]["issues"].append({
            "code": "sys_no_backups",
            "severity": "WARNING",
            "message": "No backups exist on the system."
        })
        results["system"]["status"] = "WARNING"
    else:
        latest_backup = None
        for b in backups:
            bt = parse_date(b.get("createdAt"))
            if bt:
                if not latest_backup or bt > latest_backup:
                    latest_backup = bt
        if latest_backup:
            age_days = (now - latest_backup).days
            results["system"]["metrics"]["latest_backup_age_days"] = age_days
            if age_days > 7:
                results["system"]["issues"].append({
                    "code": "sys_backup_too_old",
                    "severity": "WARNING",
                    "message": f"Latest backup is {age_days} days old (exceeds 7 days)."
                })
                results["system"]["status"] = "WARNING"
                
    # Backup Keys Verification
    known_backup_key_ids = {bk.get("id"): bk for bk in backup_keys}
    disabled_backup_keys = 0
    missing_key_backups = 0
    
    for b in backups:
        key_id = b.get("backupKey")
        if key_id:
            if key_id not in known_backup_key_ids:
                missing_key_backups += 1
                results["system"]["issues"].append({
                    "code": "sys_backup_missing_key",
                    "severity": "FAIL",
                    "message": f"Backup '{b.get('id')}' references missing backup key ID '{key_id}'."
                })
                results["system"]["status"] = "FAIL"
            elif known_backup_key_ids[key_id].get("state") != "active":
                disabled_backup_keys += 1
                results["system"]["issues"].append({
                    "code": "sys_backup_key_referenced_inactive",
                    "severity": "WARNING",
                    "message": f"Backup key ID '{key_id}' referenced by backup '{b.get('id')}' is not in active state."
                })
                results["system"]["status"] = "WARNING"

    # Check all backup keys for disabled status
    for bk in backup_keys:
        if bk.get("state") != "active":
            results["system"]["issues"].append({
                "code": "sys_backup_key_inactive",
                "severity": "WARNING",
                "message": f"Backup key '{bk.get('id')}' version {bk.get('version')} is not active (state: {bk.get('state')})."
            })
            results["system"]["status"] = "WARNING"
            
    # Cluster Checks
    is_clustered = cluster_info.get("status", {}).get("code") != "none"
    results["system"]["metrics"]["is_clustered"] = is_clustered
    if is_clustered:
        results["system"]["metrics"]["cluster_nodes_count"] = len(cluster_nodes)
        if cluster_errors:
            results["system"]["issues"].append({
                "code": "sys_cluster_errors",
                "severity": "FAIL",
                "message": f"Cluster errors detected: {json.dumps(cluster_errors)}"
            })
            results["system"]["status"] = "FAIL"
            
    # Alarms Check
    active_unacked = []
    sev_counts = {}
    critical_count = 0
    
    for alarm in alarms:
        if alarm.get("state") == "on" and alarm.get("acknowledgedAt") is None:
            active_unacked.append(alarm)
            sev = alarm.get("severity", "unknown").lower()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            if sev in ["emergency", "alert", "critical", "error", "emerg", "crit"]:
                critical_count += 1
                
    active_alarms = len(active_unacked)
    
    if active_alarms > 0:
        breakdown_str = ", ".join(f"{k}: {v}" for k, v in sorted(sev_counts.items()))
        msg = f"Active unacknowledged alarms: {active_alarms} ({breakdown_str})."
        
        if critical_count > 0:
            results["system"]["issues"].append({
                "code": "sys_active_alarms_critical",
                "severity": "FAIL",
                "message": msg
            })
            results["system"]["status"] = "FAIL"
        else:
            results["system"]["issues"].append({
                "code": "sys_active_alarms",
                "severity": "WARNING",
                "message": msg
            })
            if results["system"]["status"] != "FAIL":
                results["system"]["status"] = "WARNING"
                
    results["system"]["metrics"]["active_alarms"] = active_alarms
    results["system"]["metrics"]["critical_alarms"] = critical_count
    results["system"]["metrics"]["alarm_breakdown"] = sev_counts

    # 3. Access Check
    users = data.get("users", {}).get("resources", [])
    pwd_policies = data.get("password_policies", {}).get("resources", [])
    results["access"]["metrics"]["total_users"] = len(users)
    
    locked_users = 0
    inactive_users = 0
    unusual_logins = 0
    login_flags_count = 0
    
    for u in users:
        username = u.get("username")
        
        # 1. Lockout check
        lockout_at = u.get("account_lockout_at")
        if lockout_at is not None:
            locked_users += 1
            failed_cnt = u.get("failed_logins_count", 0)
            last_failed = u.get("last_failed_login_at") or "N/A"
            results["access"]["issues"].append({
                "code": "access_user_locked_out",
                "severity": "WARNING",
                "message": f"User account '{username}' is locked out. Failed login count: {failed_cnt}, last failed login time: {last_failed}."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"
                
        # 2. Never logged in or inactive > 30 days check
        last_login = parse_date(u.get("last_login"))
        if last_login is None:
            inactive_users += 1
            results["access"]["issues"].append({
                "code": "access_user_never_logged_in",
                "severity": "WARNING",
                "message": f"User account '{username}' has NEVER logged in."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"
        else:
            inactive_days = (now - last_login).days
            if inactive_days > 30:
                inactive_users += 1
                results["access"]["issues"].append({
                    "code": "access_user_inactive",
                    "severity": "WARNING",
                    "message": f"User account '{username}' has not logged in for {inactive_days} days."
                })
                if results["access"]["status"] != "FAIL":
                    results["access"]["status"] = "WARNING"
                    
        # 3. login_flags.login_flags == true check
        lf = u.get("login_flags")
        if isinstance(lf, dict) and lf.get("login_flags") is True:
            login_flags_count += 1
            results["access"]["issues"].append({
                "code": "access_user_login_flags_set",
                "severity": "WARNING",
                "message": f"User account '{username}' has login_flags.login_flags set to true."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"
                
        # 4. Failed logins check
        failed_cnt = u.get("failed_logins_count", 0)
        if failed_cnt > 0 and lockout_at is None:
            unusual_logins += 1
            results["access"]["issues"].append({
                "code": "access_user_failed_logins",
                "severity": "WARNING",
                "message": f"User account '{username}' has {failed_cnt} failed login attempts."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"
                
    results["access"]["metrics"]["locked_users"] = locked_users
    results["access"]["metrics"]["inactive_users"] = inactive_users
    results["access"]["metrics"]["unusual_logins"] = unusual_logins
    results["access"]["metrics"]["login_flags_count"] = login_flags_count
    
    # Password policies check (custom policy names + weak strength settings)

    custom_pwd_policies = []
    weak_pwd_policies = []
    for policy in pwd_policies:
        pname = policy.get("policy_name", "unknown")
        if pname != "global":
            custom_pwd_policies.append(pname)

        # Note: -1 is the ksctl sentinel for "inherit system default" on these fields,
        # so only explicit, non-sentinel values are treated as a policy's real setting.
        min_length = first_present(policy, "minlength", "min_length")
        history = first_present(policy, "history")
        lockout_thresholds = first_present(policy, "failed_logins_lockout_thresholds", "failedLoginsLockoutThresholds")
        pwd_change_days = first_present(policy, "pwdchngdays", "pwd_chng_days")

        if isinstance(min_length, int) and 0 <= min_length < 8:
            weak_pwd_policies.append(pname)
            results["access"]["issues"].append({
                "code": "access_pwd_policy_weak_min_length",
                "severity": "WARNING",
                "message": f"Password policy '{pname}' allows a minimum password length of {min_length} (recommended: >= 8)."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"

        if history == 0:
            weak_pwd_policies.append(pname)
            results["access"]["issues"].append({
                "code": "access_pwd_policy_no_history",
                "severity": "WARNING",
                "message": f"Password policy '{pname}' does not prevent password reuse (history = 0)."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"

        if isinstance(lockout_thresholds, list) and len(lockout_thresholds) == 0:
            weak_pwd_policies.append(pname)
            results["access"]["issues"].append({
                "code": "access_pwd_policy_no_lockout",
                "severity": "WARNING",
                "message": f"Password policy '{pname}' has account lockout disabled (no lockout thresholds configured)."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"

        if pwd_change_days == 0:
            results["access"]["issues"].append({
                "code": "access_pwd_policy_no_expiration",
                "severity": "INFO",
                "message": f"Password policy '{pname}' does not enforce password expiration (pwdchngdays = 0)."
            })

    results["access"]["metrics"]["custom_pwd_policies"] = custom_pwd_policies
    results["access"]["metrics"]["weak_password_policies"] = sorted(set(weak_pwd_policies))

    # Audit admin group members
    admin_users = data.get("admin_users", {}).get("resources", [])
    for u in admin_users:
        username = u.get("username")
        name = u.get("name") or u.get("nickname") or username
        last_login = u.get("last_login")
        if not last_login:
            results["access"]["issues"].append({
                "code": "access_admin_never_logged_in",
                "severity": "WARNING",
                "message": f"Admin group member '{username}' ({name}) has never logged in."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"
        else:
            results["access"]["issues"].append({
                "code": "access_admin_member_info",
                "severity": "INFO",
                "message": f"User '{username}' ({name}) is a member of the 'admin' system group."
            })

    # Quorum Policies check
    quorum_policies = data.get("quorum_policies", {}).get("resources", [])
    active_qps = []
    for qp in quorum_policies:
        if qp.get("active") is True:
            active_qps.append(qp)
            
    results["access"]["metrics"]["active_quorum_policies_count"] = len(active_qps)
    results["access"]["active_quorum_policies"] = active_qps

    # Custom Security Groups check
    groups = data.get("groups", {}).get("resources", [])
    custom_groups = []
    for g in groups:
        meta = g.get("app_metadata")
        is_system = isinstance(meta, dict) and meta.get("system") is True
        if not is_system:
            custom_groups.append(g)
            
    results["access"]["metrics"]["custom_groups_count"] = len(custom_groups)
    results["access"]["custom_groups"] = custom_groups

    # LDAP External Authentication Connections Check
    # Note: insecure_skip_verify/root_ca only apply when server_url uses the ldaps:// scheme;
    # OIDC/zone connections don't expose these TLS options per the ksctl connections docs.
    connections = data.get("connections", {}).get("resources", [])
    ldap_connections_count = 0
    insecure_skip_verify_connections = 0
    no_root_ca_connections = 0
    for conn in connections:
        strategy = (conn.get("strategy") or conn.get("connection_type") or "").lower()
        if strategy != "ldap":
            continue
        ldap_connections_count += 1
        cname = conn.get("name") or conn.get("id")
        server_url = (conn.get("server_url") or "").lower()
        if not server_url.startswith("ldaps"):
            continue

        if conn.get("insecure_skip_verify") is True:
            insecure_skip_verify_connections += 1
            results["access"]["issues"].append({
                "code": "access_ldap_insecure_skip_verify",
                "severity": "FAIL",
                "message": f"LDAP connection '{cname}' has certificate verification DISABLED (insecure_skip_verify = true)."
            })
            results["access"]["status"] = "FAIL"
        elif not conn.get("root_ca"):
            no_root_ca_connections += 1
            results["access"]["issues"].append({
                "code": "access_ldap_no_root_ca",
                "severity": "WARNING",
                "message": f"LDAP connection '{cname}' has no root_ca configured; it relies on the operating system's trusted CAs to validate the server certificate."
            })
            if results["access"]["status"] != "FAIL":
                results["access"]["status"] = "WARNING"

    results["access"]["metrics"]["ldap_connections_count"] = ldap_connections_count
    results["access"]["metrics"]["ldap_connections_insecure_skip_verify_count"] = insecure_skip_verify_connections
    results["access"]["metrics"]["ldap_connections_no_root_ca_count"] = no_root_ca_connections

    # 4. Domains Checks
    domains = data.get("domains", {}).get("resources", [])
    results["domains"]["metrics"]["total_domains"] = len(domains)
    for dom in domains:
        dname = dom.get("name")
        if dom.get("allow_user_management") is True:
            results["domains"]["issues"].append({
                "code": "domains_allow_user_management",
                "severity": "INFO",
                "message": f"Domain '{dname}' has allow_user_management enabled."
            })
        if dom.get("hsm_connection_id"):
            results["domains"]["issues"].append({
                "code": "domains_uses_hsm",
                "severity": "WARNING",
                "message": f"Domain '{dname}' uses HSM (connection ID: {dom.get('hsm_connection_id')}) with KEK label: {dom.get('hsm_kek_label')}"
            })
            if results["domains"]["status"] != "FAIL":
                results["domains"]["status"] = "WARNING"

    # 5. Service Interfaces & Log Forwarders Checks (Network Category)
    interfaces = data.get("interfaces", {}).get("resources", [])
    log_forwarders = data.get("log_forwarders", {}).get("resources", [])

    # Interfaces Checks
    results["network"]["metrics"]["total_interfaces"] = len(interfaces)
    for inter in interfaces:
        iname = inter.get("name")
        enabled = inter.get("enabled", True)
        mode = inter.get("mode")
        min_tls = inter.get("minimum_tls_version")
        tls_grps = inter.get("tls_groups", [])
        
        if not enabled:
            results["network"]["issues"].append({
                "code": "net_interface_disabled",
                "severity": "WARNING",
                "message": f"Service Interface '{iname}' is DISABLED."
            })
            if results["network"]["status"] != "FAIL":
                results["network"]["status"] = "WARNING"

        # Flag weak/anonymous authentication modes
        if mode in ["no-tls-pw-opt", "no-tls-pw-req", "unauth-tls-pw-opt", "unauth-tls-pw-req"]:
            results["network"]["issues"].append({
                "code": "net_interface_insecure_mode",
                "severity": "FAIL",
                "message": f"Service Interface '{iname}' is using insecure mode: '{mode}'."
            })
            results["network"]["status"] = "FAIL"

        # Flag weak TLS version
        if min_tls and min_tls.lower() in ["ssl_v3", "tls_1_0", "tls_1_1"]:
            results["network"]["issues"].append({
                "code": "net_interface_weak_tls",
                "severity": "FAIL",
                "message": f"Service Interface '{iname}' is configured with insecure minimum TLS version: '{min_tls}'."
            })
            results["network"]["status"] = "FAIL"
            
        # Flag lack of Post-Quantum Key Exchange support
        if enabled and tls_grps:
            pqc_enabled_groups = []
            pqc_groups_to_check = {
                "X25519MLKEM768", "SecP256r1MLKEM768", 
                "MLKEM512", "MLKEM768", "MLKEM1024"
            }
            for tg in tls_grps:
                gname = tg.get("group_name")
                genb = tg.get("enabled", False)
                if gname in pqc_groups_to_check and genb:
                    pqc_enabled_groups.append(gname)
                    
            if not pqc_enabled_groups:
                results["network"]["issues"].append({
                    "code": "net_interface_no_pqc",
                    "severity": "WARNING",
                    "message": f"Service Interface '{iname}' does not have any Post-Quantum Cryptography (PQC) key exchange support enabled."
                })
                if results["network"]["status"] != "FAIL":
                    results["network"]["status"] = "WARNING"
                    
    # Log Forwarder Check
    results["network"]["metrics"]["log_forwarders_count"] = len(log_forwarders)
    active_forwarders = any(not lf.get("disabled", False) for lf in log_forwarders)
    if not active_forwarders:
        results["network"]["issues"].append({
            "code": "net_no_active_log_forwarders",
            "severity": "FAIL",
            "message": "No active external log forwarders are configured."
        })
        results["network"]["status"] = "FAIL"

    # 6. Keys Checks
    keys_raw = data.get("keys", {}).get("resources", [])
    results["keys"]["metrics"]["total_raw_keys"] = len(keys_raw)
    
    # Group keys by name
    grouped_keys = {}
    for k in keys_raw:
        name = k.get("name")
        if not name:
            continue
        if name not in grouped_keys:
            grouped_keys[name] = []
        grouped_keys[name].append(k)
        
    # Collapse versions and analyze
    collapsed_keys = {}
    key_types = {}
    key_states = {}
    key_labels = {}
    non_active_keys = 0
    weak_keys = 0
    
    for name, latest_key in collapse_key_versions(keys_raw).items():
        highest_version = latest_key.get("version", 0)

        collapsed_keys[name] = {
            "name": name,
            "objectType": latest_key.get("objectType"),
            "algorithm": latest_key.get("algorithm"),
            "size": latest_key.get("size"),
            "state": latest_key.get("state"),
            "highest_version": highest_version,
            "version_count": len(grouped_keys[name]),
            "labels": latest_key.get("labels", {}),
            "createdAt": latest_key.get("createdAt")
        }
        
        # State stats
        state = latest_key.get("state", "Unknown")
        key_states[state] = key_states.get(state, 0) + 1
        
        # Type stats
        type_ = latest_key.get("objectType", "Unknown")
        key_types[type_] = key_types.get(type_, 0) + 1
        
        # Label stats
        labels = latest_key.get("labels", {})
        if isinstance(labels, dict):
            for lk, lv in labels.items():
                label_str = f"{lk}={lv}"
                key_labels[label_str] = key_labels.get(label_str, 0) + 1
                
        # Flag checks (warn if highest version is not Active)
        if state != "Active":
            non_active_keys += 1
            results["keys"]["issues"].append({
                "code": "keys_non_active",
                "severity": "WARNING",
                "message": f"Key '{name}' (highest version: v{highest_version}) is in non-Active state: '{state}'."
            })
            if results["keys"]["status"] != "FAIL":
                results["keys"]["status"] = "WARNING"
                
        # Weak checks
        algo = latest_key.get("algorithm", "")
        size = latest_key.get("size", 0)
        is_weak = False
        if algo == "RSA" and size < 2048:
            is_weak = True
        elif algo == "AES" and size < 128:
            is_weak = True
            
        if is_weak:
            weak_keys += 1
            results["keys"]["issues"].append({
                "code": "keys_weak_algorithm",
                "severity": "FAIL",
                "message": f"Key '{name}' has potentially weak configuration: {algo} ({size} bits)."
            })
            results["keys"]["status"] = "FAIL"
        collapsed_keys[name]["is_weak"] = is_weak
                
    results["keys"]["metrics"]["total_unique_keys"] = len(collapsed_keys)
    results["keys"]["metrics"]["non_active_keys"] = non_active_keys
    results["keys"]["metrics"]["weak_keys"] = weak_keys
    results["keys"]["metrics"]["key_types"] = key_types
    results["keys"]["metrics"]["key_states"] = key_states
    results["keys"]["metrics"]["key_labels"] = key_labels
    results["keys"]["collapsed_keys"] = list(collapsed_keys.values())

    # 6.4 Orphaned Resources Check (keys left behind in deleted domains)
    orphaned_report = data.get("orphaned_resources", {})
    orphaned_entries = orphaned_report.get("resources", []) if isinstance(orphaned_report, dict) else []
    if not orphaned_entries and isinstance(orphaned_report, dict) and orphaned_report and "error" not in orphaned_report:
        # This report endpoint may return a single summary object instead of a resources list.
        orphaned_entries = [orphaned_report]

    total_orphaned_keys = 0
    for entry in orphaned_entries:
        count = first_present(entry, "orphaned_key_count", "orphaned_keys_count", "key_count") or 0
        total_orphaned_keys += count
        if count > 0:
            dname = entry.get("domain_name") or entry.get("domain_id") or "unknown"
            results["keys"]["issues"].append({
                "code": "keys_orphaned",
                "severity": "WARNING",
                "message": f"Deleted domain '{dname}' has {count} orphaned key(s) that were never cleaned up."
            })
            if results["keys"]["status"] != "FAIL":
                results["keys"]["status"] = "WARNING"

    results["keys"]["metrics"]["orphaned_keys_count"] = total_orphaned_keys

    # 6.5 System Properties Check
    properties = data.get("properties", {}).get("resources", [])
    modified_props = []

    for prop in properties:
        name = prop.get("name")
        val = prop.get("value")
        default_val = DEFAULT_PROPERTIES.get(name)
        if default_val is not None and val != default_val:
            p_copy = dict(prop)
            p_copy["default_value"] = default_val
            modified_props.append(p_copy)
            results["system"]["issues"].append({
                "code": "sys_property_modified",
                "severity": "INFO",
                "message": f"System property '{name}' has been modified. Current value: '{val}' (default: '{default_val}')."
            })
                
    results["system"]["metrics"]["modified_properties_count"] = len(modified_props)
    results["system"]["modified_properties"] = modified_props

    # 6.6 Root-of-Trust Keys Check
    rot_keys = data.get("rot_keys", {}).get("resources", [])
    old_rot_keys = []
    for rk in rot_keys:
        rk_id = rk.get("id")
        created_at_str = rk.get("createdAt")
        rk_created = parse_date(created_at_str)
        if rk_created:
            age_days = (now - rk_created).days
            if age_days > 365:
                old_rot_keys.append(rk)
                results["system"]["issues"].append({
                    "code": "sys_rot_key_old",
                    "severity": "WARNING",
                    "message": f"Root-of-Trust key '{rk_id}' is older than 365 days ({age_days} days old)."
                })
                if results["system"]["status"] != "FAIL":
                    results["system"]["status"] = "WARNING"
    results["system"]["metrics"]["old_rot_keys_count"] = len(old_rot_keys)
    results["system"]["rot_keys"] = rot_keys

    # 6.7 Scheduler Configurations Check
    scheduler_configs = data.get("scheduler_configs", {}).get("resources", [])
    disabled_scheds = []
    for s in scheduler_configs:
        name = s.get("name")
        is_disabled = s.get("disabled") is True
        if is_disabled:
            disabled_scheds.append(s)
            results["system"]["issues"].append({
                "code": "sys_scheduler_disabled",
                "severity": "INFO",
                "message": f"Scheduler configuration '{name}' is disabled."
            })
    results["system"]["metrics"]["disabled_schedules_count"] = len(disabled_scheds)
    results["system"]["scheduler_configs"] = scheduler_configs

    # 6.8 System Services Check
    services_data = data.get("services", {})
    services_list = services_data.get("services", [])
    non_started_services = []
    
    top_status = services_data.get("status")
    if top_status and top_status != "started":
        results["system"]["issues"].append({
            "code": "sys_services_status_not_started",
            "severity": "WARNING",
            "message": f"Overall system services status is not started: '{top_status}'."
        })
        if results["system"]["status"] != "FAIL":
            results["system"]["status"] = "WARNING"

    for svc in services_list:
        svc_name = svc.get("name")
        svc_status = svc.get("status")
        if svc_status != "started":
            non_started_services.append(svc)
            results["system"]["issues"].append({
                "code": "sys_service_not_started",
                "severity": "WARNING",
                "message": f"System service '{svc_name}' is not in started state: '{svc_status}'."
            })
            if results["system"]["status"] != "FAIL":
                results["system"]["status"] = "WARNING"
                
    results["system"]["metrics"]["non_started_services_count"] = len(non_started_services)
    results["system"]["metrics"]["total_services_count"] = len(services_list)
    results["system"]["non_started_services"] = non_started_services
    results["system"]["services_status"] = services_data

    # Shared cert-expiry check used by both the trusted-CA and local/external-CA sections below.
    def check_cert_expiry(label: str, name: Optional[str], not_after_str: Optional[str], code_expired: str, code_expiring: str) -> None:
        not_after = parse_date(not_after_str)
        if not not_after:
            return
        days_to_expiry = (not_after - now).days
        if days_to_expiry < 0:
            results["ca"]["issues"].append({
                "code": code_expired,
                "severity": "FAIL",
                "message": f"{label} '{name}' has EXPIRED (expired on {not_after_str})."
            })
            results["ca"]["status"] = "FAIL"
        elif days_to_expiry < 30:
            results["ca"]["issues"].append({
                "code": code_expiring,
                "severity": "WARNING",
                "message": f"{label} '{name}' will expire in {days_to_expiry} days (expires on {not_after_str})."
            })
            if results["ca"]["status"] != "FAIL":
                results["ca"]["status"] = "WARNING"

    # 6.9 Trusted CA Certificates Check
    trusted_cas = data.get("trusted_ca_certs", {}).get("resources", [])
    results["ca"]["metrics"]["total_trusted_cas_count"] = len(trusted_cas)

    for ca in trusted_cas:
        ca_details = ca.get("ca_details") or {}
        ca_name = ca_details.get("name") or ca.get("id")
        check_cert_expiry("Trusted CA certificate", ca_name, ca_details.get("notAfter"), "ca_trusted_expired", "ca_trusted_expiring")

    # 6.10 Local/External CAs Check
    local_cas = data.get("local_cas", {}).get("resources", [])
    external_cas = data.get("external_cas", {}).get("resources", [])
    for ca_list, ca_type in [(local_cas, "Local"), (external_cas, "External")]:
        for ca in ca_list:
            check_cert_expiry(f"{ca_type} CA", ca.get("name") or ca.get("id"), ca.get("notAfter"), "ca_local_external_expired", "ca_local_external_expiring")

    # 6.11 CTE and Capacity Check
    results["cte"] = {"status": "PASS", "issues": [], "metrics": {}}
    cte_clients = data.get("cte_clients", {}).get("resources", [])
    cte_policies = data.get("cte_policies", {}).get("resources", [])
    capacity_report = data.get("capacity_report", {}) or {}
    
    results["cte"]["metrics"]["total_clients"] = len(cte_clients)
    results["cte"]["metrics"]["total_policies"] = len(cte_policies)
    results["cte"]["metrics"]["key_usage_count_this_domain"] = capacity_report.get("key_usage_count_this_domain", 0)
    results["cte"]["metrics"]["key_usage_count_including_subdomains"] = capacity_report.get("key_usage_count_including_subdomains", 0)
    results["cte"]["metrics"]["subdomain_count_this_domain"] = capacity_report.get("subdomain_count_this_domain", 0)
    results["cte"]["metrics"]["subdomain_count_including_subdomains"] = capacity_report.get("subdomain_count_including_subdomains", 0)

    for c in cte_clients:
        cname = c.get("name")
        cstatus = c.get("client_health_status")
        if cstatus != "Healthy":
            results["cte"]["issues"].append({
                "code": "cte_client_unhealthy",
                "severity": "WARNING",
                "message": f"CTE client '{cname}' status is not Healthy: '{cstatus}'."
            })
            if results["cte"]["status"] != "FAIL":
                results["cte"]["status"] = "WARNING"

        # Check client GuardPoints
        c_gps = data.get("cte_guardpoints", {}).get(cname, {})
        if isinstance(c_gps, dict):
            gps_list = c_gps.get("resources", [])
            for gp in gps_list:
                gp_state = gp.get("guard_point_state", "UNKNOWN")
                gp_path = gp.get("guard_path", "UNKNOWN")
                if gp_state.upper() != "ACTIVE":
                    results["cte"]["issues"].append({
                        "code": "cte_guardpoint_inactive",
                        "severity": "WARNING",
                        "message": f"CTE client '{cname}' GuardPoint '{gp_path}' is not ACTIVE (state: '{gp_state}')."
                    })
                    if results["cte"]["status"] != "FAIL":
                        results["cte"]["status"] = "WARNING"

    for p in cte_policies:
        pname = p.get("name")
        if p.get("never_deny") is True:
            results["cte"]["issues"].append({
                "code": "cte_policy_learn_mode",
                "severity": "WARNING",
                "message": f"CTE Policy '{pname}' has Learn Mode enabled (never_deny = true)."
            })
            if results["cte"]["status"] != "FAIL":
                results["cte"]["status"] = "WARNING"

    # 6.12 Outbound Notification & Proxy Configuration Check
    smtp_servers = data.get("smtp_servers", {}).get("resources", [])
    notification_emails = data.get("notification_emails", {}).get("resources", [])

    results["system"]["metrics"]["smtp_servers_count"] = len(smtp_servers)
    results["system"]["metrics"]["notification_emails_count"] = len(notification_emails)
    if not smtp_servers:
        results["system"]["issues"].append({
            "code": "sys_no_smtp_server",
            "severity": "WARNING",
            "message": "No SMTP server is configured for email alerting/notifications."
        })
        if results["system"]["status"] != "FAIL":
            results["system"]["status"] = "WARNING"
    elif not notification_emails:
        results["system"]["issues"].append({
            "code": "sys_no_notification_recipients",
            "severity": "WARNING",
            "message": "An SMTP server is configured but no notification email recipients are set."
        })
        if results["system"]["status"] != "FAIL":
            results["system"]["status"] = "WARNING"

    # Proxy responses may come back as a list of configs or a single config object.
    proxy_data = data.get("proxy", {})
    if isinstance(proxy_data, dict):
        proxy_entries = proxy_data.get("resources", [])
        if not proxy_entries and proxy_data and "error" not in proxy_data:
            proxy_entries = [proxy_data]
    elif isinstance(proxy_data, list):
        proxy_entries = proxy_data
    else:
        proxy_entries = []
    results["system"]["metrics"]["proxy_configured"] = bool(proxy_entries)

    # Prometheus Metrics API Check
    metrics_status = data.get("metrics_prometheus", {})
    prom_enabled = metrics_status.get("enabled", False)
    results["system"]["metrics"]["prometheus_enabled"] = prom_enabled
    if not prom_enabled:
        results["system"]["issues"].append({
            "code": "sys_prometheus_disabled",
            "severity": "WARNING",
            "message": "Prometheus Metrics API is disabled."
        })
        if results["system"]["status"] != "FAIL":
            results["system"]["status"] = "WARNING"

    results["licensing"]["metrics"]["total_features"] = len(features)

    # 7. Clients Checks
    clients = data.get("clients", {}).get("resources", [])
    active_clients = [c for c in clients if c.get("state") == "active"]
    results["clients"]["metrics"]["total_clients"] = len(clients)
    results["clients"]["metrics"]["active_clients"] = len(active_clients)
    results["clients"]["active_clients_list"] = active_clients

    # 8. Event Records Check (recent server/client audit records above INFO severity)
    server_records = data.get("server_event_records", {}).get("resources", [])
    client_records = data.get("client_event_records", {}).get("resources", [])

    significant_server_events = 0
    for rec in server_records:
        severity = (first_present(rec, "severity") or "").lower()
        if severity not in SIGNIFICANT_SEVERITIES:
            continue
        significant_server_events += 1
        created = first_present(rec, "created_at", "created", "time") or "unknown time"
        service = first_present(rec, "service") or "unknown service"
        message = first_present(rec, "message") or "No message provided"
        is_critical = severity in ("critical", "fatal")
        results["records"]["issues"].append({
            "code": "records_server_critical" if is_critical else "records_server_error",
            "severity": "FAIL" if is_critical else "WARNING",
            "message": f"[{created}] Server event ({service}, severity: {severity}): {message}"
        })
        if is_critical:
            results["records"]["status"] = "FAIL"
        elif results["records"]["status"] != "FAIL":
            results["records"]["status"] = "WARNING"

    significant_client_events = 0
    for rec in client_records:
        severity = (first_present(rec, "severity") or "").lower()
        if severity not in SIGNIFICANT_SEVERITIES:
            continue
        significant_client_events += 1
        created = first_present(rec, "created_at", "created", "time") or "unknown time"
        client_name = first_present(rec, "client") or "unknown client"
        event = first_present(rec, "event") or "No event description"
        is_critical = severity in ("critical", "fatal")
        results["records"]["issues"].append({
            "code": "records_client_critical" if is_critical else "records_client_error",
            "severity": "FAIL" if is_critical else "WARNING",
            "message": f"[{created}] Client event ({client_name}, severity: {severity}): {event}"
        })
        if is_critical:
            results["records"]["status"] = "FAIL"
        elif results["records"]["status"] != "FAIL":
            results["records"]["status"] = "WARNING"

    results["records"]["metrics"]["total_server_events_reviewed"] = len(server_records)
    results["records"]["metrics"]["significant_server_events"] = significant_server_events
    results["records"]["metrics"]["total_client_events_reviewed"] = len(client_records)
    results["records"]["metrics"]["significant_client_events"] = significant_client_events

    # Aggregate Overall status
    all_statuses = [
        results["system"]["status"],
        results["access"]["status"],
        results["keys"]["status"],
        results["clients"]["status"],
        results["licensing"]["status"],
        results["network"]["status"],
        results["domains"]["status"],
        results["cte"]["status"],
        results["ca"]["status"],
        results["records"]["status"]
    ]
    if "FAIL" in all_statuses:
        results["status"] = "FAIL"
    elif "WARNING" in all_statuses:
        results["status"] = "WARNING"
    else:
        results["status"] = "PASS"
        
    return results

def generate_html_report(data: Dict[str, Any], analysis: Dict[str, Any]) -> None:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Remediation guidance shown in the Overview tab, keyed by the stable "code"
    # each check attaches to its issue - one summary line per code rather than
    # one line per affected object (e.g. per weak key, per inactive user).
    REMEDIATIONS = {
        "lic_trial_mode_active": "Plan migration to a production license before the trial period ends.",
        "license_expired": "Renew or reinstall the expired license(s) to restore licensed functionality.",
        "license_expiring": "Renew the license(s) before they expire to avoid a licensing gap.",
        "license_expiration_unparseable": "Manually verify the license expiration date in the CipherTrust Manager UI.",
        "license_trial_expiring": "Convert the trial license(s) to a production license before the trial period ends.",
        "feature_expired": "Renew the expired licensed feature(s) to restore functionality.",
        "feature_expiring": "Renew the licensed feature(s) before the trial period ends.",

        "sys_ntp_not_synced": "Configure and verify NTP synchronization for accurate timestamps in logs and certificates.",
        "sys_ntp_no_servers": "Configure at least one NTP server so the appliance clock stays synchronized.",
        "sys_disk_encryption_attended_boot": "Disable attended boot, or document the manual passphrase-entry process for reboots.",
        "sys_no_login_banner": "Configure a pre-authentication login banner to meet compliance/legal notice requirements.",
        "sys_no_scheduled_backup": "Enable a scheduled database backup job to protect against data loss.",
        "sys_no_backups": "Take an initial backup and enable a recurring backup schedule.",
        "sys_backup_too_old": "Run a fresh backup and confirm the backup schedule is executing as expected.",
        "sys_backup_missing_key": "Restore or recreate the missing backup key so the affected backup(s) remain usable.",
        "sys_backup_key_referenced_inactive": "Reactivate or replace the backup key referenced by these backups.",
        "sys_backup_key_inactive": "Reactivate or rotate the inactive backup key(s).",
        "sys_cluster_errors": "Investigate and resolve the reported cluster errors to restore full cluster health.",
        "sys_active_alarms_critical": "Acknowledge and remediate the critical/emergency alarms immediately.",
        "sys_active_alarms": "Review and acknowledge the outstanding alarms.",
        "sys_property_modified": "Review modified system properties to confirm each change is intentional and documented.",
        "sys_rot_key_old": "Rotate the Root-of-Trust key(s) older than 365 days per your key rotation policy.",
        "sys_scheduler_disabled": "Review disabled scheduler configurations to confirm they are intentionally turned off.",
        "sys_services_status_not_started": "Investigate why overall system services are not fully started.",
        "sys_service_not_started": "Restart or investigate the system service(s) that are not in a started state.",
        "sys_no_smtp_server": "Configure an SMTP server so administrators receive email alerts and notifications.",
        "sys_no_notification_recipients": "Add notification email recipients so configured alerts are actually delivered.",
        "sys_prometheus_disabled": "Enable the Prometheus metrics API for monitoring, or confirm this is intentional.",

        "access_user_locked_out": "Investigate the cause of lockout and unlock or reset the affected account(s).",
        "access_user_never_logged_in": "Review accounts that have never logged in and disable or remove any that are not needed.",
        "access_user_inactive": "Review long-inactive user accounts and disable or remove any that are no longer needed.",
        "access_user_login_flags_set": "Investigate accounts flagged by login_flags to confirm the condition is expected.",
        "access_user_failed_logins": "Review accounts with failed login attempts for signs of brute-force or credential-stuffing activity.",
        "access_pwd_policy_weak_min_length": "Increase the minimum password length to at least 8 characters.",
        "access_pwd_policy_no_history": "Enable password history to prevent immediate password reuse.",
        "access_pwd_policy_no_lockout": "Configure account lockout thresholds to mitigate brute-force login attempts.",
        "access_pwd_policy_no_expiration": "Confirm that never-expiring passwords are an intentional exception for this policy.",
        "access_admin_never_logged_in": "Review admin group members who have never logged in and remove access no longer needed.",
        "access_admin_member_info": "Periodically audit admin group membership to ensure it reflects current staffing.",
        "access_ldap_insecure_skip_verify": "Enable certificate verification on the LDAP connection (remove insecure_skip_verify).",
        "access_ldap_no_root_ca": "Configure a root_ca on the LDAP connection to pin trust instead of relying on the OS trust store.",

        "domains_allow_user_management": "Confirm delegated user management is intended for this domain.",
        "domains_uses_hsm": "Verify the HSM-backed domain's connectivity and key custody are documented and monitored.",

        "net_interface_disabled": "Confirm the disabled service interface is intentionally turned off.",
        "net_interface_insecure_mode": "Reconfigure the service interface to require TLS and authentication.",
        "net_interface_no_pqc": "Enable a Post-Quantum Cryptography key exchange group on the service interface.",
        "net_interface_weak_tls": "Raise the minimum TLS version to TLS 1.2 or higher.",
        "net_no_active_log_forwarders": "Configure and enable an external log forwarder for centralized audit logging.",

        "keys_non_active": "Review non-Active keys and reactivate, rotate, or archive them as appropriate.",
        "keys_weak_algorithm": "Migrate weak keys to stronger key strengths or algorithms.",
        "keys_orphaned": "Clean up orphaned keys left behind in deleted domains.",

        "ca_trusted_expired": "Renew or replace the expired trusted CA certificate(s).",
        "ca_trusted_expiring": "Renew the trusted CA certificate(s) before they expire.",
        "ca_local_external_expired": "Renew or replace the expired CA certificate(s).",
        "ca_local_external_expiring": "Renew the CA certificate(s) before they expire.",

        "cte_client_unhealthy": "Investigate and restore connectivity/health for the affected CTE client(s).",
        "cte_guardpoint_inactive": "Reactivate the inactive GuardPoint(s) or confirm they are intentionally disabled.",
        "cte_policy_learn_mode": "Disable Learn Mode (never_deny) on CTE policies once policy tuning is complete.",

        "records_server_error": "Investigate the server-side error events reported in the audit log.",
        "records_server_critical": "Investigate the critical/fatal server-side events immediately - these indicate serious failures.",
        "records_client_error": "Investigate the client-side error events reported in the audit log.",
        "records_client_critical": "Investigate the critical/fatal client-side events immediately - these indicate serious failures.",
    }
    DEFAULT_REMEDIATION = "Review this finding and remediate as appropriate for your environment."

    # Construct Collapsible Severity Groups HTML
    severity_categories = {
        "FAIL": {"title": "Critical Failures (FAIL)", "class": "fail", "issues": [], "icon": "fa-solid fa-circle-exclamation"},
        "WARNING": {"title": "Warnings (WARNING)", "class": "warning", "issues": [], "icon": "fa-solid fa-triangle-exclamation"},
        "INFO": {"title": "Informational (INFO)", "class": "info", "issues": [], "icon": "fa-solid fa-circle-info"}
    }

    category_display_names = {
        "system": "System",
        "licensing": "Licensing",
        "access": "Access & Users",
        "domains": "Domains",
        "network": "Network",
        "keys": "Keys",
        "ca": "Certificate Authorities",
        "cte": "Transparent Encryption",
        "clients": "Clients",
        "records": "Event Records"
    }

    for cat_id, display_name in category_display_names.items():
        for issue in analysis.get(cat_id, {}).get("issues", []):
            sev = issue.get("severity", "INFO").upper()
            if sev not in severity_categories:
                sev = "INFO"
            severity_categories[sev]["issues"].append({
                "category": display_name,
                "code": issue.get("code", "uncategorized"),
                "message": issue.get("message", "")
            })

    findings_html_parts = []
    has_any_issues = False

    for sev_key in ["FAIL", "WARNING", "INFO"]:
        group = severity_categories[sev_key]
        issues_list = group["issues"]
        if issues_list:
            has_any_issues = True

            # Summarize per (category, code) instead of listing every affected object.
            grouped: Dict[tuple, Dict[str, Any]] = {}
            for issue in issues_list:
                key = (issue["category"], issue["code"])
                if key not in grouped:
                    grouped[key] = {"category": issue["category"], "code": issue["code"], "messages": []}
                grouped[key]["messages"].append(issue["message"])

            summaries = sorted(grouped.values(), key=lambda g: (g["category"], g["code"]))

            group_id = f"group-{group['class']}"
            header_html = f'''
            <div class="collapsible-severity-group">
                <button class="severity-header {group['class']}" onclick="toggleSeverityGroup('{group_id}')">
                    <i class="fa-solid fa-chevron-down toggle-icon"></i>
                    <i class="{group['icon']}" style="margin-left: 0.5rem; margin-right: 0.25rem;"></i>
                    <span>{group['title']} - {len(issues_list)} Finding{"s" if len(issues_list) > 1 else ""} ({len(summaries)} type{"s" if len(summaries) != 1 else ""})</span>
                </button>
                <div id="{group_id}" class="severity-content active">
            '''
            issue_items_html = []
            for summary in summaries:
                count = len(summary["messages"])
                remediation = REMEDIATIONS.get(summary["code"], DEFAULT_REMEDIATION)
                count_label = f"{count} finding{'s' if count > 1 else ''}"
                if count > 1:
                    detail_lines = "".join(f"<li>{m}</li>" for m in summary["messages"])
                    details_html = f'''
                        <details style="margin-top: 0.4rem;">
                            <summary style="cursor: pointer; color: var(--text-secondary); font-size: 0.8rem;">Show {count} affected items</summary>
                            <ul style="margin: 0.4rem 0 0 1.1rem; padding: 0; font-size: 0.8rem; color: var(--text-secondary);">{detail_lines}</ul>
                        </details>
                    '''
                else:
                    details_html = f'<div style="margin-top: 0.25rem; font-size: 0.8rem; color: var(--text-secondary);">{summary["messages"][0]}</div>'
                issue_items_html.append(f'''
                    <div class="issue-item {group['class']}">
                        <i class="{group['icon']}"></i>
                        <div>
                            <strong>{summary['category']}</strong> ({count_label}): {remediation}
                            {details_html}
                        </div>
                    </div>
                ''')
            footer_html = '''
                </div>
            </div>
            '''
            findings_html_parts.append(header_html + "".join(issue_items_html) + footer_html)

    if not has_any_issues:
        findings_html = '<div class="issue-item" style="background: rgba(16, 185, 129, 0.1); color: #d1fae5; border: 1px solid rgba(16, 185, 129, 0.2);"><i class="fa-solid fa-circle-check"></i> No critical issues, warnings or informational findings found across any check categories!</div>'
    else:
        findings_html = "\n".join(findings_html_parts)
    
    sys_info = data.get("system_info", {})
    ntp_status = data.get("ntp_status", {})
    backups = data.get("backups", {}).get("resources", [])
    backup_keys = data.get("backup_keys", {}).get("resources", [])
    scheduler_configs = data.get("scheduler_configs", {}).get("resources", [])
    users = data.get("users", {}).get("resources", [])
    keys = data.get("keys", {}).get("resources", [])
    clients = data.get("clients", {}).get("resources", [])
    active_clients = analysis.get("clients", {}).get("active_clients_list", [])
    server_records = data.get("server_event_records", {}).get("resources", [])
    client_records = data.get("client_event_records", {}).get("resources", [])
    cluster_info = data.get("cluster_info", {})
    cluster_nodes = data.get("cluster_nodes", {}).get("resources", [])
    domains = data.get("domains", {}).get("resources", [])
    dnshosts = data.get("dnshosts", {}).get("resources", [])
    interfaces = data.get("interfaces", {}).get("resources", [])
    log_forwarders = data.get("log_forwarders", {}).get("resources", [])
    licenses = data.get("licenses", {}).get("resources", [])
    features = data.get("features", {}).get("resources", [])
    diskenc = data.get("disk_encryption", {})
    metrics_status = data.get("metrics_prometheus", {})
    pwd_policies = data.get("password_policies", {}).get("resources", [])
    properties = data.get("properties", {}).get("resources", [])
    modified_properties = analysis.get("system", {}).get("modified_properties", [])
    proxy_info = data.get("proxy", {}) or {}
    http_proxy = proxy_info.get("HTTP_PROXY") or proxy_info.get("http_proxy") or "Not Configured"
    https_proxy = proxy_info.get("HTTPS_PROXY") or proxy_info.get("https_proxy") or "Not Configured"
    
    import re
    def mask_proxy(p_str):
        if not p_str or p_str == "Not Configured":
            return p_str
        return re.sub(r'^(https?://)?([^:]+):([^@]+)@', r'\1\2:******@', p_str)
        
    masked_http = mask_proxy(http_proxy)
    masked_https = mask_proxy(https_proxy)
    
    no_proxy_val = proxy_info.get("NO_PROXY") or proxy_info.get("no_proxy")
    if isinstance(no_proxy_val, list):
        no_proxy_str = ", ".join(no_proxy_val)
    else:
        no_proxy_str = no_proxy_val or "None"
        
    has_cert = "Yes" if (proxy_info.get("certificate") or proxy_info.get("ca_cert_file")) else "No"
    
    collapsed_keys = analysis.get("keys", {}).get("collapsed_keys", [])
    key_metrics = analysis.get("keys", {}).get("metrics", {})
    
    has_active_trial = analysis["licensing"]["metrics"]["has_active_trial"]
    is_clustered = analysis["system"]["metrics"]["is_clustered"]
    prom_enabled = analysis["system"]["metrics"]["prometheus_enabled"]
    active_quorum_policies = analysis.get("access", {}).get("active_quorum_policies", [])
    rot_keys = data.get("rot_keys", {}).get("resources", [])
    services_status = analysis.get("system", {}).get("services_status", {}) or {}
    non_started_services = analysis.get("system", {}).get("non_started_services", [])
    notification_emails = data.get("notification_emails", {}).get("resources", [])
    smtp_servers = data.get("smtp_servers", {}).get("resources", [])
    custom_groups = analysis.get("access", {}).get("custom_groups", [])
    admin_users = data.get("admin_users", {}).get("resources", [])
    trusted_ca_certs = data.get("trusted_ca_certs", {}).get("resources", [])
    local_cas = data.get("local_cas", {}).get("resources", [])
    external_cas = data.get("external_cas", {}).get("resources", [])
    cte_clients = data.get("cte_clients", {}).get("resources", [])
    cte_policies = data.get("cte_policies", {}).get("resources", [])
    sorted_cte_policies = sorted(cte_policies, key=lambda x: (x.get("policy_type") or "", x.get("name") or ""))
    capacity_report = data.get("capacity_report", {}) or {}
    cte_metrics = analysis.get("cte", {}).get("metrics", {})
    ca_to_interfaces = {}
    for i in interfaces:
        i_name = i.get("name")
        t_cas = i.get("trusted_cas", {})
        if isinstance(t_cas, dict):
            for lca_uri in t_cas.get("local", []):
                ca_to_interfaces.setdefault(lca_uri, []).append(i_name)
            for eca_uri in t_cas.get("external", []):
                ca_to_interfaces.setdefault(eca_uri, []).append(i_name)

    # Generate user rows split into Locked, Unused, and High Risk Accounts
    locked_users = []
    unused_users = []
    high_risk_users = []
    
    now = datetime.now(timezone.utc)
    for u in users:
        username = u.get("username")
        email = u.get("email")
        last_login_str = u.get("last_login")
        last_login = parse_date(last_login_str)
        logins_count = u.get("logins_count", 0)
        failed_cnt = u.get("failed_logins_count", 0)
        last_failed = u.get("last_failed_login_at")
        lockout_at = u.get("account_lockout_at")
        lf = u.get("login_flags", {})
        
        is_locked = lockout_at is not None
        is_unused = logins_count == 0 or last_login is None or (now - last_login).days > 90
        is_high_risk = failed_cnt > 5
        
        # Highlighting logic:
        is_inactive = last_login is None or (now - last_login).days > 30
        last_login_style = ' style="color: var(--fail-color); font-weight: bold;"' if is_inactive else ''
        status_style = ' style="color: var(--fail-color); font-weight: bold;"' if is_locked else ''
        failed_style = ' style="color: var(--fail-color); font-weight: bold;"' if failed_cnt > 0 else ''
        
        failed_disp = str(failed_cnt)
        if failed_cnt > 0:
            failed_disp = f'<span{failed_style}>{failed_cnt}</span>'
        if last_failed:
            failed_disp += f'<br><small style="color:var(--text-secondary);">Last: {format_readable_date(last_failed)}</small>'
            
        status_badge = f'<span class="badge-pill locked"{status_style}>Locked</span>' if is_locked else '<span class="badge-pill active">Active</span>'
        
        flags_disp = []
        if lf:
            for lk, lv in lf.items():
                if lv:
                    if lk == "login_flags":
                        flags_disp.append(f'<span class="badge-pill active" style="font-size:0.7rem; background:rgba(239, 68, 68, 0.15); color:var(--fail-color); font-weight:bold;">{lk}={lv}</span>')
                    else:
                        flags_disp.append(f'<span class="badge-pill active" style="font-size:0.7rem; background:rgba(255, 255, 255, 0.08); color:var(--text-secondary);">{lk}={lv}</span>')
        flags_str = " ".join(flags_disp) if flags_disp else "None"
        
        last_login_disp = format_readable_date(last_login_str)
        if is_inactive:
            last_login_disp = f'<span{last_login_style}>{last_login_disp}</span>'
            
        row = f'''<tr>
            <td><strong>{username}</strong></td>
            <td>{email}</td>
            <td>{last_login_disp}</td>
            <td>{logins_count}</td>
            <td>{failed_disp}</td>
            <td>{flags_str}</td>
            <td>{status_badge}</td>
        </tr>'''
        
        if is_locked:
            locked_users.append(row)
        if is_unused:
            unused_users.append(row)
        if is_high_risk:
            high_risk_users.append(row)
            
    locked_users_html = "".join(locked_users) if locked_users else '<tr><td colspan="7" style="text-align:center; color:var(--text-secondary);">No locked accounts detected.</td></tr>'
    unused_users_html = "".join(unused_users) if unused_users else '<tr><td colspan="7" style="text-align:center; color:var(--text-secondary);">No unused accounts (0 logins or inactive &gt; 90 days) detected.</td></tr>'
    high_risk_users_html = "".join(high_risk_users) if high_risk_users else '<tr><td colspan="7" style="text-align:center; color:var(--text-secondary);">No high risk accounts (failed logins &gt; 5) detected.</td></tr>'

    rot_key_rows = []
    for rk in rot_keys:
        rk_created = parse_date(rk.get("createdAt"))
        age_days = (now - rk_created).days if rk_created else None
        needs_rotation = age_days is not None and age_days > 365
        rot_key_rows.append(f'''<tr>
                                <td><strong>{rk.get("id")}</strong></td>
                                <td>{format_readable_date(rk.get("createdAt"))}</td>
                                <td>{age_days if age_days is not None else "N/A"}</td>
                                <td>
                                    <span class="badge-pill { "inactive" if needs_rotation else "active" }">
                                        { "Needs Rotation (Older than 365 days)" if needs_rotation else "Good (Active)" }
                                    </span>
                                </td>
                            </tr>''')
    rot_keys_html = "".join(rot_key_rows) if rot_key_rows else '<tr><td colspan="4" style="text-align:center;">No Root-of-Trust keys registered.</td></tr>'

    # Interface CAs: trusted_cas references are URIs like "kylo:kylo:naboo:localca:<id>",
    # so the CA's own id is resolved from the last colon-delimited segment to look up its name.
    local_ca_names_by_id = {c.get("id"): c.get("name") for c in local_cas}
    external_ca_names_by_id = {c.get("id"): c.get("name") for c in external_cas}

    def resolve_ca_names(ca_uris: List[str], names_by_id: Dict[str, Any]) -> str:
        if not ca_uris:
            return "N/A"
        labels = []
        for uri in ca_uris:
            ca_id = uri.rsplit(":", 1)[-1]
            labels.append(names_by_id.get(ca_id, ca_id))
        return ", ".join(labels)

    def format_auto_gen_attributes(attrs: Dict[str, Any]) -> str:
        if not attrs:
            return "N/A"
        parts = [f"CN: {attrs.get('cn')}"] if attrs.get("cn") else []
        names = attrs.get("names") or []
        if names:
            org = names[0].get("O")
            if org:
                parts.append(f"O: {org}")
        return "<br>".join(parts) if parts else "N/A"

    interface_ca_rows = []
    for i in interfaces:
        trusted_cas = i.get("trusted_cas") or {}
        interface_ca_rows.append(f'''<tr>
                                <td><strong>{i.get("name")}</strong></td>
                                <td>{resolve_ca_names(trusted_cas.get("local"), local_ca_names_by_id)}</td>
                                <td>{resolve_ca_names(trusted_cas.get("external"), external_ca_names_by_id)}</td>
                                <td>{i.get("cert_user_field") or "N/A"}</td>
                                <td>{format_auto_gen_attributes(i.get("local_auto_gen_attributes"))}</td>
                            </tr>''')
    interface_ca_html = "".join(interface_ca_rows) if interface_ca_rows else '<tr><td colspan="5" style="text-align:center;">No service interfaces configured.</td></tr>'

    nav_tabs = [
        {"id": "system", "icon": "fa-solid fa-microchip", "label": "System & Cluster"},
        {"id": "licensing", "icon": "fa-solid fa-file-invoice", "label": "Licensing"},
        {"id": "network", "icon": "fa-solid fa-ethernet", "label": "Network"},
        {"id": "ca", "icon": "fa-solid fa-file-shield", "label": "Certificate Authorities"},
        {"id": "domains", "icon": "fa-solid fa-network-wired", "label": "Domains"},
        {"id": "access", "icon": "fa-solid fa-user-shield", "label": "Access Control"},
        {"id": "keys", "icon": "fa-solid fa-key", "label": "Keys"},
        {"id": "clients", "icon": "fa-solid fa-address-card", "label": "Clients"},
        {"id": "cte", "icon": "fa-solid fa-lock", "label": "Transparent Encryption"},
        {"id": "records", "icon": "fa-solid fa-scroll", "label": "Event Records"},
    ]

    context: Dict[str, Any] = {
        "now_str": now_str,
        "analysis": analysis,
        "data": data,
        "nav_tabs": nav_tabs,
        "findings_html": findings_html,
        "sys_info": sys_info,
        "ntp_status": ntp_status,
        "backups": backups,
        "backup_keys": backup_keys,
        "scheduler_configs": scheduler_configs,
        "users": users,
        "keys": keys,
        "clients": clients,
        "active_clients": active_clients,
        "server_records": server_records,
        "client_records": client_records,
        "cluster_info": cluster_info,
        "cluster_nodes": cluster_nodes,
        "domains": domains,
        "dnshosts": dnshosts,
        "interfaces": interfaces,
        "log_forwarders": log_forwarders,
        "licenses": licenses,
        "features": features,
        "diskenc": diskenc,
        "metrics_status": metrics_status,
        "pwd_policies": pwd_policies,
        "properties": properties,
        "modified_properties": modified_properties,
        "masked_http": masked_http,
        "masked_https": masked_https,
        "no_proxy_str": no_proxy_str,
        "has_cert": has_cert,
        "collapsed_keys": collapsed_keys,
        "key_metrics": key_metrics,
        "has_active_trial": has_active_trial,
        "is_clustered": is_clustered,
        "prom_enabled": prom_enabled,
        "active_quorum_policies": active_quorum_policies,
        "rot_keys": rot_keys,
        "services_status": services_status,
        "non_started_services": non_started_services,
        "notification_emails": notification_emails,
        "smtp_servers": smtp_servers,
        "custom_groups": custom_groups,
        "admin_users": admin_users,
        "trusted_ca_certs": trusted_ca_certs,
        "local_cas": local_cas,
        "external_cas": external_cas,
        "cte_clients": cte_clients,
        "cte_policies": cte_policies,
        "sorted_cte_policies": sorted_cte_policies,
        "capacity_report": capacity_report,
        "cte_metrics": cte_metrics,
        "ca_to_interfaces": ca_to_interfaces,
        "locked_users_html": locked_users_html,
        "unused_users_html": unused_users_html,
        "high_risk_users_html": high_risk_users_html,
        "rot_keys_html": rot_keys_html,
        "interface_ca_html": interface_ca_html,
    }

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["format_readable_date"] = format_readable_date
    html = env.get_template("base.html").render(**context)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report successfully generated at: {OUTPUT_HTML}")

def main() -> None:
    print("=== CipherTrust Manager Healthcheck Configuration ===")
    url = input("Enter CipherTrust Manager Server URL (e.g. https://cm.example.com): ").strip()
    while not url:
        url = input("URL is required. Enter CipherTrust Manager Server URL: ").strip()
        
    user = input("Enter Username [default: readonly]: ").strip()
    if not user:
        user = "readonly"

    password = getpass.getpass("Enter Password: ")
    while not password:
        password = getpass.getpass("Password cannot be empty. Enter Password: ")

    skip_ssl_verify = input("Skip TLS certificate verification? [y/N]: ").strip().lower() in ("y", "yes")

    print("\nAttempting to login to CipherTrust Manager...")
    login_cmd = ["ksctl", "login", "--url", url, "--user", user, "--password", password, "-y"]
    if skip_ssl_verify:
        login_cmd.append("--nosslverify")
    try:
        subprocess.run(login_cmd, capture_output=True, text=True, check=True)
        print("Login successful! Starting data collection...")
    except subprocess.CalledProcessError as e:
        print(f"Login failed! Exit code: {e.returncode}")
        print(f"Error output:\n{e.stderr or e.stdout}")
        sys.exit(1)
    data: Dict[str, Any] = {}

    # These ksctl calls are all independent, read-only, and share the login session
    # established above, so they're safe to run concurrently rather than one at a time.
    collectors: Dict[str, Callable[[], Any]] = {
        "version": lambda: run_ksctl_cmd(["version"]),
        "system_info": lambda: run_ksctl_cmd(["system", "info", "get"]),
        "cluster_info": lambda: run_ksctl_cmd(["cluster", "info"]),
        "cluster_nodes": lambda: run_ksctl_list_all(["cluster", "nodes", "list"]),
        "cluster_errors": lambda: run_ksctl_cmd(["cluster", "errors"]),
        "ntp_status": lambda: run_ksctl_cmd(["ntp", "status"]),
        "ntp_servers": lambda: run_ksctl_list_all(["ntp", "servers", "list"]),
        "dnshosts": lambda: run_ksctl_list_all(["dnshosts", "list"]),
        "backups": lambda: run_ksctl_list_all(["backup", "list"]),
        "backup_keys": lambda: run_ksctl_list_all(["backupkeys", "list"]),
        "scheduler_configs": lambda: run_ksctl_list_all(["scheduler", "configs", "list"]),
        "users": lambda: run_ksctl_list_all(["users", "list"]),
        "keys": lambda: run_ksctl_list_all(["keys", "list"]),
        "clients": lambda: run_ksctl_list_all(["clientmgmt", "clients", "list"]),
        "server_event_records": lambda: run_ksctl_list_all(["records", "list", "--created-after", "7 days ago"]),
        "client_event_records": lambda: run_ksctl_list_all(["client-records", "list", "--created-after", "7 days ago"]),
        "alarms": lambda: run_ksctl_list_all(["alarms", "list"]),
        "licenses": lambda: run_ksctl_list_all(["licensing", "licenses", "list"]),
        "features": lambda: run_ksctl_list_all(["licensing", "features", "list"]),
        "trials": lambda: run_ksctl_list_all(["licensing", "trials", "list"]),
        "lockdata": lambda: run_ksctl_cmd(["licensing", "lockdata", "get"]),
        "domains": lambda: run_ksctl_list_all(["domains", "list"]),
        "banner": lambda: run_ksctl_cmd(["banners", "get", "--name", "pre-auth"]),
        "interfaces": lambda: run_ksctl_list_all(["interfaces", "list"]),
        "log_forwarders": lambda: run_ksctl_list_all(["log-forwarders", "list"]),
        "metrics_prometheus": lambda: run_ksctl_cmd(["metrics", "prometheus", "status"]),
        "password_policies": lambda: run_ksctl_list_all(["users", "pwdpolicy", "list"]),
        "disk_encryption": lambda: run_ksctl_cmd(["diskenc", "status"]),
        "properties": lambda: run_ksctl_list_all(["properties", "list"]),
        "proxy": lambda: run_ksctl_cmd(["proxy", "list"]),
        "quorum_policies": lambda: run_ksctl_list_all(["quorum-policy", "status"]),
        "rot_keys": lambda: run_ksctl_list_all(["rot-keys", "list"]),
        "services": lambda: run_ksctl_cmd(["services", "status"]),
        "notification_emails": lambda: run_ksctl_list_all(["notification", "email", "list"]),
        "smtp_servers": lambda: run_ksctl_list_all(["notification", "smtp-servers", "list"]),
        "groups": lambda: run_ksctl_list_all(["groups", "list"]),
        "connections": lambda: run_ksctl_list_all(["connections", "list"]),
        "trusted_ca_certs": lambda: run_ksctl_list_all(["trusted-ca-cert", "list"]),
        "local_cas": lambda: run_ksctl_list_all(["ca", "locals", "list"]),
        "external_cas": lambda: run_ksctl_list_all(["ca", "externals", "list"]),
        "capacity_report": lambda: run_ksctl_cmd(["reports", "capacity-report"]),
        "orphaned_resources": lambda: run_ksctl_cmd(["reports", "orphaned-resources", "--limit", "1000"]),
        "cte_clients": lambda: run_ksctl_list_all(["cte", "clients", "list"]),
        "cte_policies": lambda: run_ksctl_list_all(["cte", "policies", "list"]),
        "admin_users": lambda: run_ksctl_list_all(["users", "list", "--group", "admin"]),
    }

    print("Collecting diagnostics...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submitting in dict order and reading results back in that same order keeps
        # the resulting `data` dict's key order identical to the old sequential version,
        # even though the calls themselves complete in whatever order the threads finish.
        futures = {key: executor.submit(fn) for key, fn in collectors.items()}
        for key, future in futures.items():
            data[key] = future.result()

    # CTE GuardPoints depend on the CTE client list resolved above, but the lookup for
    # each client is itself independent, so these are parallelized as a second phase.
    data["cte_guardpoints"] = {}
    cte_clients_list = data["cte_clients"].get("resources", []) if isinstance(data.get("cte_clients"), dict) else []
    client_names = [c.get("name") for c in cte_clients_list if c.get("name")]
    if client_names:
        with ThreadPoolExecutor(max_workers=8) as executor:
            guardpoint_futures = {
                name: executor.submit(run_ksctl_list_all, ["cte", "clients", "list-guardpoints", "--cte-client-identifier", name])
                for name in client_names
            }
            for name, future in guardpoint_futures.items():
                data["cte_guardpoints"][name] = future.result()

    print("Analyzing diagnostics...")
    analysis = analyze_health(data)
    
    # Filter raw data to keep only compliance-interesting information for storage and HTML embedding
    data = filter_interesting_data(data)
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Diagnostics saved raw data at: {OUTPUT_JSON}")
        
    print("Generating interactive dashboard report...")
    generate_html_report(data, analysis)

if __name__ == "__main__":
    main()
