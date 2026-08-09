"""Background CipherTrust healthcheck runner (vendored ksctl-based tool)."""

from __future__ import annotations

import io
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import urllib3

from . import db
from .config import ROOT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

VENDOR_DIR = ROOT / "vendor" / "healthcheck"
TOOLS_DIR = ROOT / "tools"
DATA_DIR = ROOT / "data" / "healthcheck"

_lock = threading.RLock()
_running: dict[int, threading.Thread] = {}
_progress: dict[int, dict[str, Any]] = {}
_ksctl_download_lock = threading.Lock()

# Entries inside CM /downloads/ksctl_images.zip → local tools/ filename.
# Zip currently ships amd64 only (linux / darwin / windows).
_KSCTL_ZIP_BY_OS: dict[str, str] = {
    "windows": "ksctl-win-amd64.exe",
    "darwin": "ksctl-darwin-amd64",
    "linux": "ksctl-linux-amd64",
}
_KSCTL_LOCAL_BY_OS: dict[str, str] = {
    "windows": "ksctl.exe",
    "darwin": "ksctl-darwin-amd64",
    "linux": "ksctl-linux-amd64",
}


def _host_os() -> str:
    """Normalized OS key: windows | darwin | linux."""
    system = platform.system().lower()
    if system == "windows" or os.name == "nt":
        return "windows"
    if system == "darwin":
        return "darwin"
    return "linux"


def _ksctl_member_name() -> str:
    """Zip entry basename inside /downloads/ksctl_images.zip for this OS."""
    return _KSCTL_ZIP_BY_OS[_host_os()]


def _ksctl_install_path() -> Path:
    """Where we place the downloaded binary under tools/."""
    return TOOLS_DIR / _KSCTL_LOCAL_BY_OS[_host_os()]


def _looks_like_native_ksctl(path: Path) -> bool:
    """Reject obviously wrong-platform binaries (e.g. Linux ELF on Windows)."""
    try:
        with path.open("rb") as fh:
            magic = fh.read(4)
    except OSError:
        return False
    if len(magic) < 2:
        return False
    host = _host_os()
    if host == "windows":
        return magic[:2] == b"MZ"
    if host == "linux":
        return magic == b"\x7fELF"
    if host == "darwin":
        # Mach-O 64-bit / fat / 32-bit
        return magic in {
            b"\xcf\xfa\xed\xfe",  # MH_MAGIC_64 (LE)
            b"\xfe\xed\xfa\xcf",  # MH_CIGAM_64
            b"\xce\xfa\xed\xfe",  # MH_MAGIC
            b"\xfe\xed\xfa\xce",  # MH_CIGAM
            b"\xca\xfe\xba\xbe",  # FAT
            b"\xbe\xba\xfe\xca",
        }
    return True


def _ksctl_binary() -> Path | None:
    """Prefer the OS-matching tools/ binary; then tools/ksctl; then PATH."""
    host = _host_os()
    candidates: list[Path] = [_ksctl_install_path()]
    if host != "windows":
        candidates.append(TOOLS_DIR / "ksctl")
    # Do NOT probe other OS filenames (linux binary must not win on macOS).

    for c in candidates:
        if not c.is_file():
            continue
        if not _looks_like_native_ksctl(c):
            logger.warning("Ignoring non-native ksctl candidate: %s", c)
            continue
        try:
            c.chmod(0o755)
        except OSError:
            pass
        return c

    which = shutil.which("ksctl")
    if which:
        path = Path(which)
        if path.is_file() and _looks_like_native_ksctl(path):
            return path
    return None


def ksctl_available() -> dict[str, Any]:
    path = _ksctl_binary()
    if not path:
        return {
            "ok": False,
            "path": None,
            "error": (
                "ksctl binary not found in tools/ or PATH "
                "(will auto-download from a CM /downloads/ksctl_images.zip when available)"
            ),
            "expected_zip_member": _ksctl_member_name(),
            "host_os": _host_os(),
        }
    try:
        res = subprocess.run(
            [str(path), "version"],
            capture_output=True,
            text=True,
            timeout=30,
            env=_ksctl_env(path),
        )
        return {
            "ok": res.returncode == 0,
            "path": str(path),
            "version_raw": (res.stdout or res.stderr or "").strip()[:500],
            "error": None if res.returncode == 0 else (res.stderr or res.stdout or "ksctl version failed"),
            "expected_zip_member": _ksctl_member_name(),
            "host_os": _host_os(),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "path": str(path),
            "error": str(exc),
            "expected_zip_member": _ksctl_member_name(),
            "host_os": _host_os(),
        }


def _cm_base_url(host: str) -> str:
    text = (host or "").strip().rstrip("/")
    if not text:
        raise ValueError("empty CM host")
    if "://" not in text:
        text = f"https://{text}"
    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"invalid CM host: {host!r}")
    return f"{parsed.scheme}://{parsed.netloc}"


def _find_zip_member(names: list[str], wanted: str) -> str | None:
    """Match exact zip entry or nested path ending with the wanted basename."""
    if wanted in names:
        return wanted
    wanted_l = wanted.lower()
    for name in names:
        base = name.rstrip("/").split("/")[-1]
        if base.lower() == wanted_l:
            return name
    return None


def ensure_ksctl(cm_host: str, *, force: bool = False) -> dict[str, Any]:
    """Ensure a local ksctl binary exists, downloading from the CM if needed.

    CipherTrust serves an unauthenticated zip at:
      https://<cm-host>/downloads/ksctl_images.zip
    containing:
      ksctl-linux-amd64, ksctl-darwin-amd64, ksctl-win-amd64.exe
    Only the binary for this host OS is extracted into tools/.
    """
    existing = ksctl_available()
    if existing.get("ok") and not force:
        return {**existing, "downloaded": False}

    with _ksctl_download_lock:
        existing = ksctl_available()
        if existing.get("ok") and not force:
            return {**existing, "downloaded": False}

        try:
            base = _cm_base_url(cm_host)
        except ValueError as exc:
            return {"ok": False, "path": None, "downloaded": False, "error": str(exc)}

        zip_url = f"{base}/downloads/ksctl_images.zip"
        member_wanted = _ksctl_member_name()
        dest = _ksctl_install_path()
        host = _host_os()
        logger.info(
            "Downloading ksctl for %s (%s → %s) from %s",
            host,
            member_wanted,
            dest.name,
            zip_url,
        )

        try:
            TOOLS_DIR.mkdir(parents=True, exist_ok=True)
            resp = requests.get(zip_url, verify=False, timeout=180)
            if resp.status_code != 200:
                return {
                    "ok": False,
                    "path": None,
                    "downloaded": False,
                    "error": f"ksctl download failed HTTP {resp.status_code} from {zip_url}",
                    "url": zip_url,
                    "expected_zip_member": member_wanted,
                    "host_os": host,
                }
            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                names = zf.namelist()
                member = _find_zip_member(names, member_wanted)
                if not member:
                    return {
                        "ok": False,
                        "path": None,
                        "downloaded": False,
                        "error": (
                            f"{member_wanted} not found in zip for host_os={host} "
                            f"(entries: {[Path(n).name for n in names[:20]]})"
                        ),
                        "url": zip_url,
                        "expected_zip_member": member_wanted,
                        "host_os": host,
                    }
                data = zf.read(member)

            if not data:
                return {
                    "ok": False,
                    "path": None,
                    "downloaded": False,
                    "error": f"empty zip member {member}",
                    "url": zip_url,
                }

            tmp = dest.with_name(dest.name + ".tmp")
            tmp.write_bytes(data)
            try:
                tmp.chmod(0o755)
            except OSError:
                pass
            if not _looks_like_native_ksctl(tmp):
                tmp.unlink(missing_ok=True)
                return {
                    "ok": False,
                    "path": None,
                    "downloaded": False,
                    "error": (
                        f"extracted {Path(member).name} is not a native {host} binary "
                        f"(wrong platform in zip?)"
                    ),
                    "url": zip_url,
                    "expected_zip_member": member_wanted,
                    "host_os": host,
                }
            tmp.replace(dest)

            # Unix: also expose as tools/ksctl for vendored script PATH lookups.
            if host != "windows":
                link = TOOLS_DIR / "ksctl"
                try:
                    if link.exists() or link.is_symlink():
                        link.unlink()
                    try:
                        link.symlink_to(dest.name)
                    except OSError:
                        shutil.copy2(dest, link)
                        try:
                            link.chmod(0o755)
                        except OSError:
                            pass
                except OSError as exc:
                    logger.warning("Could not create tools/ksctl link: %s", exc)

            check = ksctl_available()
            if not check.get("ok"):
                return {
                    **check,
                    "downloaded": True,
                    "url": zip_url,
                    "member": Path(member).name,
                    "error": check.get("error")
                    or f"extracted {Path(member).name} but ksctl version failed",
                }
            return {
                **check,
                "downloaded": True,
                "url": zip_url,
                "member": Path(member).name,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("ksctl download failed from %s", zip_url)
            return {
                "ok": False,
                "path": None,
                "downloaded": False,
                "error": f"ksctl download failed: {exc}",
                "url": zip_url,
                "expected_zip_member": member_wanted,
                "host_os": host,
            }


def ensure_ksctl_async(cm_host: str) -> None:
    """Background download after first appliance connect (no-op if already present)."""
    if ksctl_available().get("ok"):
        return

    def _run() -> None:
        result = ensure_ksctl(cm_host)
        if result.get("ok"):
            logger.info(
                "ksctl ready at %s (downloaded=%s)",
                result.get("path"),
                result.get("downloaded"),
            )
        else:
            logger.warning("ksctl auto-download failed: %s", result.get("error"))

    threading.Thread(target=_run, name="ksctl-download", daemon=True).start()


def _ksctl_env(ksctl_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    # Put tools dir first so child "ksctl" lookups work on Unix after symlink/copy.
    env["PATH"] = str(ksctl_path.parent) + os.pathsep + env.get("PATH", "")
    # Avoid interactive prompts / home-dir surprises.
    env.setdefault("HOME", str(Path.home()))
    return env


def appliance_dir(appliance_id: int) -> Path:
    path = DATA_DIR / str(appliance_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _import_healthcheck_module():
    if not VENDOR_DIR.is_dir():
        raise RuntimeError(f"Vendored healthcheck missing at {VENDOR_DIR}")
    vendor = str(VENDOR_DIR)
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    import run_healthcheck as hc  # type: ignore  # noqa: WPS433

    return hc


def _normalize_data(data: dict[str, Any]) -> dict[str, Any]:
    for key, val in list(data.items()):
        if val is None:
            data[key] = {}
        elif isinstance(val, dict) and val.get("error") and key in (
            "capacity_report",
            "orphaned_resources",
        ):
            data[key] = {}
    return data


def _severity_counts(analysis: dict[str, Any]) -> dict[str, int]:
    counts = {"FAIL": 0, "WARNING": 0, "INFO": 0}
    for section, body in analysis.items():
        if section == "status" or not isinstance(body, dict):
            continue
        for issue in body.get("issues") or []:
            if not isinstance(issue, dict):
                continue
            sev = (issue.get("severity") or "").upper()
            if sev in counts:
                counts[sev] += 1
    return counts


def _set_progress(appliance_id: int, **fields: Any) -> None:
    with _lock:
        cur = dict(_progress.get(appliance_id) or {})
        cur.update(fields)
        cur["appliance_id"] = appliance_id
        _progress[appliance_id] = cur


def get_live_progress(appliance_id: int) -> dict[str, Any] | None:
    with _lock:
        return dict(_progress[appliance_id]) if appliance_id in _progress else None


def is_running(appliance_id: int) -> bool:
    with _lock:
        t = _running.get(appliance_id)
        return bool(t and t.is_alive())


def get_status(appliance_id: int) -> dict[str, Any]:
    live = get_live_progress(appliance_id)
    row = db.get_healthcheck_run(appliance_id)
    ksctl = ksctl_available()
    if live and live.get("status") == "running":
        return {
            "appliance_id": appliance_id,
            "status": "running",
            "phase": live.get("phase") or "running",
            "message": live.get("message") or "Healthcheck in progress…",
            "started_at": live.get("started_at"),
            "finished_at": None,
            "overall": None,
            "severity_counts": None,
            "error": None,
            "has_report": False,
            "has_json": False,
            "ksctl": ksctl,
            "last_run": row,
        }
    if row:
        return {
            "appliance_id": appliance_id,
            "status": row.get("status") or "idle",
            "phase": row.get("status") or "idle",
            "message": row.get("error") or row.get("message") or "",
            "started_at": row.get("started_at"),
            "finished_at": row.get("finished_at"),
            "overall": row.get("overall"),
            "severity_counts": row.get("severity_counts"),
            "error": row.get("error"),
            "has_report": bool(row.get("html_path") and Path(row["html_path"]).is_file()),
            "has_json": bool(row.get("json_path") and Path(row["json_path"]).is_file()),
            "ksctl": ksctl,
            "last_run": row,
        }
    return {
        "appliance_id": appliance_id,
        "status": "idle",
        "phase": "idle",
        "message": "No healthcheck has been run yet.",
        "started_at": None,
        "finished_at": None,
        "overall": None,
        "severity_counts": None,
        "error": None,
        "has_report": False,
        "has_json": False,
        "ksctl": ksctl,
        "last_run": None,
    }


def start_healthcheck(appliance_id: int) -> dict[str, Any]:
    appliance = db.get_appliance(appliance_id, include_secrets=True)
    if not appliance:
        return {"ok": False, "error": "appliance not found"}
    if not appliance.get("password"):
        return {"ok": False, "error": "could not decrypt appliance password"}
    ksctl = ksctl_available()
    if not ksctl.get("ok"):
        # Pull unauthenticated ksctl_images.zip from this CM (same as CM UI downloads).
        dl = ensure_ksctl(str(appliance.get("host") or ""))
        ksctl = ksctl_available() if dl.get("ok") else dl
        if not ksctl.get("ok"):
            return {
                "ok": False,
                "error": ksctl.get("error") or "ksctl unavailable",
                "ksctl": ksctl,
            }

    with _lock:
        existing = _running.get(appliance_id)
        if existing and existing.is_alive():
            return {"ok": True, "started": False, "status": "running", "message": "already running"}

        started_at = time.time()
        _set_progress(
            appliance_id,
            status="running",
            phase="starting",
            message="Starting healthcheck…",
            started_at=started_at,
        )
        db.upsert_healthcheck_run(
            appliance_id,
            status="running",
            started_at=started_at,
            finished_at=None,
            overall=None,
            severity_counts=None,
            error=None,
            message="Starting…",
            html_path=None,
            json_path=None,
            analysis_path=None,
        )

        thread = threading.Thread(
            target=_run_job,
            args=(appliance_id,),
            name=f"healthcheck-{appliance_id}",
            daemon=True,
        )
        _running[appliance_id] = thread
        thread.start()

    return {"ok": True, "started": True, "status": "running"}


def _run_job(appliance_id: int) -> None:
    started_at = time.time()
    out_dir = appliance_dir(appliance_id)
    html_path = out_dir / "healthcheck_report.html"
    json_path = out_dir / "healthcheck_data.json"
    analysis_path = out_dir / "analysis_summary.json"

    try:
        appliance = db.get_appliance(appliance_id, include_secrets=True)
        if not appliance:
            raise RuntimeError("appliance not found")

        ksctl_path = _ksctl_binary()
        if not ksctl_path:
            raise RuntimeError("ksctl binary not found")

        # Ensure `ksctl` resolves for the vendored script's subprocess calls.
        if os.name != "nt":
            link = TOOLS_DIR / "ksctl"
            if not link.exists():
                try:
                    if ksctl_path.name != "ksctl":
                        shutil.copy2(ksctl_path, link)
                        link.chmod(0o755)
                except OSError:
                    pass
            os.environ["PATH"] = str(TOOLS_DIR) + os.pathsep + os.environ.get("PATH", "")
        else:
            os.environ["PATH"] = str(TOOLS_DIR) + os.pathsep + os.environ.get("PATH", "")

        hc = _import_healthcheck_module()
        hc.OUTPUT_HTML = str(html_path)
        hc.OUTPUT_JSON = str(json_path)
        hc.TEMPLATES_DIR = str(VENDOR_DIR / "templates")

        _set_progress(appliance_id, phase="login", message="Logging in with ksctl…")
        url = appliance["host"]
        user = appliance["username"]
        password = appliance["password"]
        login_cmd = [
            str(ksctl_path),
            "login",
            "--url",
            url,
            "--user",
            user,
            "--password",
            password,
            "-y",
            "--nosslverify",
        ]
        res = subprocess.run(
            login_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=_ksctl_env(ksctl_path),
        )
        if res.returncode != 0:
            raise RuntimeError(
                f"ksctl login failed: {(res.stderr or res.stdout or '').strip()[:800]}"
            )

        _set_progress(appliance_id, phase="collecting", message="Collecting diagnostics…")
        collectors: dict[str, Any] = {
            "version": lambda: hc.run_ksctl_cmd(["version"]),
            "system_info": lambda: hc.run_ksctl_cmd(["system", "info", "get"]),
            "cluster_info": lambda: hc.run_ksctl_cmd(["cluster", "info"]),
            "cluster_nodes": lambda: hc.run_ksctl_list_all(["cluster", "nodes", "list"]),
            "cluster_errors": lambda: hc.run_ksctl_cmd(["cluster", "errors"]),
            "ntp_status": lambda: hc.run_ksctl_cmd(["ntp", "status"]),
            "ntp_servers": lambda: hc.run_ksctl_list_all(["ntp", "servers", "list"]),
            "dnshosts": lambda: hc.run_ksctl_list_all(["dnshosts", "list"]),
            "backups": lambda: hc.run_ksctl_list_all(["backup", "list"]),
            "backup_keys": lambda: hc.run_ksctl_list_all(["backupkeys", "list"]),
            "scheduler_configs": lambda: hc.run_ksctl_list_all(["scheduler", "configs", "list"]),
            "users": lambda: hc.run_ksctl_list_all(["users", "list"]),
            "keys": lambda: hc.run_ksctl_list_all(["keys", "list"]),
            "clients": lambda: hc.run_ksctl_list_all(["clientmgmt", "clients", "list"]),
            "server_event_records": lambda: hc.run_ksctl_list_all(
                ["records", "list", "--created-after", "7 days ago"]
            ),
            "client_event_records": lambda: hc.run_ksctl_list_all(
                ["client-records", "list", "--created-after", "7 days ago"]
            ),
            "alarms": lambda: hc.run_ksctl_list_all(["alarms", "list"]),
            "licenses": lambda: hc.run_ksctl_list_all(["licensing", "licenses", "list"]),
            "features": lambda: hc.run_ksctl_list_all(["licensing", "features", "list"]),
            "trials": lambda: hc.run_ksctl_list_all(["licensing", "trials", "list"]),
            "lockdata": lambda: hc.run_ksctl_cmd(["licensing", "lockdata", "get"]),
            "domains": lambda: hc.run_ksctl_list_all(["domains", "list"]),
            "banner": lambda: hc.run_ksctl_cmd(["banners", "get", "--name", "pre-auth"]),
            "interfaces": lambda: hc.run_ksctl_list_all(["interfaces", "list"]),
            "log_forwarders": lambda: hc.run_ksctl_list_all(["log-forwarders", "list"]),
            "metrics_prometheus": lambda: hc.run_ksctl_cmd(["metrics", "prometheus", "status"]),
            "password_policies": lambda: hc.run_ksctl_list_all(["users", "pwdpolicy", "list"]),
            "disk_encryption": lambda: hc.run_ksctl_cmd(["diskenc", "status"]),
            "properties": lambda: hc.run_ksctl_list_all(["properties", "list"]),
            "proxy": lambda: hc.run_ksctl_cmd(["proxy", "list"]),
            "quorum_policies": lambda: hc.run_ksctl_list_all(["quorum-policy", "status"]),
            "rot_keys": lambda: hc.run_ksctl_list_all(["rot-keys", "list"]),
            "services": lambda: hc.run_ksctl_cmd(["services", "status"]),
            "notification_emails": lambda: hc.run_ksctl_list_all(["notification", "email", "list"]),
            "smtp_servers": lambda: hc.run_ksctl_list_all(["notification", "smtp-servers", "list"]),
            "groups": lambda: hc.run_ksctl_list_all(["groups", "list"]),
            "connections": lambda: hc.run_ksctl_list_all(["connections", "list"]),
            "trusted_ca_certs": lambda: hc.run_ksctl_list_all(["trusted-ca-cert", "list"]),
            "local_cas": lambda: hc.run_ksctl_list_all(["ca", "locals", "list"]),
            "external_cas": lambda: hc.run_ksctl_list_all(["ca", "externals", "list"]),
            "capacity_report": lambda: hc.run_ksctl_cmd(["reports", "capacity-report"]),
            "orphaned_resources": lambda: hc.run_ksctl_cmd(
                ["reports", "orphaned-resources", "--limit", "1000"]
            ),
            "cte_clients": lambda: hc.run_ksctl_list_all(["cte", "clients", "list"]),
            "cte_policies": lambda: hc.run_ksctl_list_all(["cte", "policies", "list"]),
            "admin_users": lambda: hc.run_ksctl_list_all(["users", "list", "--group", "admin"]),
        }

        data: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {key: executor.submit(fn) for key, fn in collectors.items()}
            for key, future in futures.items():
                data[key] = future.result()

        data["cte_guardpoints"] = {}
        cte_clients_list = (
            data["cte_clients"].get("resources", [])
            if isinstance(data.get("cte_clients"), dict)
            else []
        )
        client_names = [c.get("name") for c in cte_clients_list if c.get("name")]
        if client_names:
            _set_progress(
                appliance_id,
                phase="cte",
                message=f"Collecting CTE GuardPoints ({len(client_names)})…",
            )
            with ThreadPoolExecutor(max_workers=8) as executor:
                gp_futures = {
                    name: executor.submit(
                        hc.run_ksctl_list_all,
                        ["cte", "clients", "list-guardpoints", "--cte-client-identifier", name],
                    )
                    for name in client_names
                }
                for name, future in gp_futures.items():
                    data["cte_guardpoints"][name] = future.result()

        data = _normalize_data(data)

        _set_progress(appliance_id, phase="analyzing", message="Analyzing findings…")
        analysis = hc.analyze_health(data)
        with open(analysis_path, "w", encoding="utf-8") as fh:
            json.dump(analysis, fh, indent=2, default=str)

        data_filtered = hc.filter_interesting_data(data)
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(data_filtered, fh, indent=2)

        _set_progress(appliance_id, phase="report", message="Generating HTML report…")
        hc.generate_html_report(data_filtered, analysis)

        finished_at = time.time()
        counts = _severity_counts(analysis)
        overall = analysis.get("status") or "PASS"
        db.upsert_healthcheck_run(
            appliance_id,
            status="done",
            started_at=started_at,
            finished_at=finished_at,
            overall=overall,
            severity_counts=counts,
            error=None,
            message=f"Completed in {int(finished_at - started_at)}s",
            html_path=str(html_path),
            json_path=str(json_path),
            analysis_path=str(analysis_path),
        )
        _set_progress(
            appliance_id,
            status="done",
            phase="done",
            message="Healthcheck complete",
            finished_at=finished_at,
            overall=overall,
            severity_counts=counts,
        )
        logger.info(
            "Healthcheck done appliance=%s overall=%s counts=%s",
            appliance_id,
            overall,
            counts,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Healthcheck failed appliance=%s", appliance_id)
        finished_at = time.time()
        err = str(exc)[:2000]
        db.upsert_healthcheck_run(
            appliance_id,
            status="error",
            started_at=started_at,
            finished_at=finished_at,
            overall=None,
            severity_counts=None,
            error=err,
            message="Healthcheck failed",
            html_path=str(html_path) if html_path.exists() else None,
            json_path=str(json_path) if json_path.exists() else None,
            analysis_path=str(analysis_path) if analysis_path.exists() else None,
        )
        _set_progress(
            appliance_id,
            status="error",
            phase="error",
            message=err,
            finished_at=finished_at,
            error=err,
        )
    finally:
        with _lock:
            _running.pop(appliance_id, None)


def load_analysis(appliance_id: int) -> dict[str, Any] | None:
    row = db.get_healthcheck_run(appliance_id)
    if not row:
        return None
    path = row.get("analysis_path")
    if path and Path(path).is_file():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
    return None


def posture_summary(appliance_id: int, *, max_findings: int = 8) -> dict[str, Any]:
    """Compact last-run posture for Overview (and future dashboard overlays)."""
    status = get_status(appliance_id)
    run_status = status.get("status") or "idle"
    overall = status.get("overall")
    counts = status.get("severity_counts") if isinstance(status.get("severity_counts"), dict) else None
    findings: list[dict[str, Any]] = []
    section_status: dict[str, Any] = {}

    if run_status == "done":
        analysis = load_analysis(appliance_id)
        if isinstance(analysis, dict):
            if not overall:
                overall = analysis.get("status")
            order = {"FAIL": 0, "WARNING": 1, "INFO": 2}
            for section, body in analysis.items():
                if section == "status" or not isinstance(body, dict):
                    continue
                if body.get("status"):
                    section_status[section] = body.get("status")
                for issue in body.get("issues") or []:
                    if not isinstance(issue, dict):
                        continue
                    findings.append(
                        {
                            "section": section,
                            "severity": issue.get("severity"),
                            "code": issue.get("code"),
                            "message": issue.get("message"),
                        }
                    )
            findings.sort(key=lambda f: order.get(str(f.get("severity") or "").upper(), 9))
            findings = findings[:max_findings]
            if not counts:
                counts = _severity_counts(analysis)

    age_seconds = None
    finished_at = status.get("finished_at")
    if finished_at:
        try:
            age_seconds = max(0, int(time.time() - float(finished_at)))
        except (TypeError, ValueError):
            age_seconds = None

    return {
        "appliance_id": appliance_id,
        "run_status": run_status,
        "overall": overall,
        "severity_counts": counts,
        "findings": findings,
        "section_status": section_status,
        "started_at": status.get("started_at"),
        "finished_at": finished_at,
        "age_seconds": age_seconds,
        "message": status.get("message"),
        "error": status.get("error"),
        "has_report": bool(status.get("has_report")),
    }


def report_html_path(appliance_id: int) -> Path | None:
    row = db.get_healthcheck_run(appliance_id)
    if not row:
        return None
    path = row.get("html_path")
    if path and Path(path).is_file():
        return Path(path)
    fallback = appliance_dir(appliance_id) / "healthcheck_report.html"
    return fallback if fallback.is_file() else None
