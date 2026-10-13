"""CipherTrust Manager REST client (TLS verify always off)."""

from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import urlparse

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .parser import Sample, parse_prometheus_text

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


def _session_no_retries() -> requests.Session:
    """Session that fails fast — no urllib3 connect/read retries."""
    session = requests.Session()
    session.verify = False
    retry = Retry(
        total=0,
        connect=0,
        read=0,
        redirect=0,
        status=0,
        other=0,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    return session


class CMClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class CMClient:
    """Talk to a CipherTrust Manager appliance. SSL verification is always disabled."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        domain: str = "",
        *,
        timeout: float = 30.0,
    ) -> None:
        self.host = host.rstrip("/")
        if "://" not in self.host:
            self.host = f"https://{self.host}"
        self.username = username
        self.password = password
        self.domain = domain or ""
        self.timeout = float(timeout)
        self.jwt: str | None = None
        self.jwt_expires_at: float = 0.0
        self.metrics_token: str | None = None
        self.session = _session_no_retries()

    def set_timeout(self, timeout: float) -> None:
        """Tighten/loosen HTTP timeouts (e.g. shorter on manual Refresh retries)."""
        self.timeout = max(3.0, float(timeout))

    @property
    def base(self) -> str:
        return f"{self.host}/api/v1"

    def login(self) -> dict[str, Any]:
        body: dict[str, Any] = {"name": self.username, "password": self.password}
        if self.domain:
            body["domain"] = self.domain
        resp = self.session.post(f"{self.base}/auth/tokens/", json=body, timeout=self.timeout)
        if resp.status_code >= 400:
            raise CMClientError(
                f"Login failed ({resp.status_code}): {resp.text[:300]}",
                status_code=resp.status_code,
                payload=_safe_json(resp),
            )
        data = resp.json()
        jwt = data.get("jwt") or data.get("token")
        if not jwt:
            raise CMClientError("Login response missing jwt", payload=data)
        duration = float(data.get("duration") or 300)
        self.jwt = jwt
        self.jwt_expires_at = time.time() + max(60.0, duration - 30.0)
        return data

    def ensure_auth(self) -> None:
        if self.jwt and time.time() < self.jwt_expires_at:
            return
        self.login()

    def _auth_headers(self) -> dict[str, str]:
        self.ensure_auth()
        assert self.jwt
        return {"Authorization": f"Bearer {self.jwt}"}

    def get_json(self, path: str, **kwargs: Any) -> Any:
        url = path if path.startswith("http") else f"{self.base}{path}"
        resp = self.session.get(url, headers=self._auth_headers(), timeout=self.timeout, **kwargs)
        if resp.status_code == 401:
            self.login()
            resp = self.session.get(url, headers=self._auth_headers(), timeout=self.timeout, **kwargs)
        if resp.status_code >= 400:
            raise CMClientError(
                f"GET {path} failed ({resp.status_code}): {resp.text[:300]}",
                status_code=resp.status_code,
                payload=_safe_json(resp),
            )
        if not resp.content:
            return None
        return resp.json()

    def post_json(self, path: str, body: dict | None = None, **kwargs: Any) -> Any:
        url = path if path.startswith("http") else f"{self.base}{path}"
        resp = self.session.post(url, headers=self._auth_headers(), json=body or {}, timeout=self.timeout, **kwargs)
        if resp.status_code == 401:
            self.login()
            resp = self.session.post(url, headers=self._auth_headers(), json=body or {}, timeout=self.timeout, **kwargs)
        if resp.status_code >= 400:
            raise CMClientError(
                f"POST {path} failed ({resp.status_code}): {resp.text[:300]}",
                status_code=resp.status_code,
                payload=_safe_json(resp),
            )
        if not resp.content:
            return None
        try:
            return resp.json()
        except Exception:  # noqa: BLE001
            return {"raw": resp.text}

    def system_info(self) -> dict[str, Any]:
        for path in ("/system/info", "/system/version", "/nodes/self"):
            try:
                data = self.get_json(path)
                if isinstance(data, dict):
                    return data
            except CMClientError:
                continue
        return {}

    def network_interfaces(self) -> dict[str, Any]:
        """GET /v1/system/network/interfaces — host NIC config (inet IP, gateway, DNS)."""
        try:
            data = self.get_json("/system/network/interfaces?limit=100")
            if isinstance(data, dict):
                return data
        except CMClientError:
            pass
        try:
            data = self.get_json("/system/network/interfaces")
            if isinstance(data, dict):
                return data
        except CMClientError:
            pass
        return {"resources": []}

    def pick_private_ip_from_interfaces(self) -> str | None:
        """First RFC1918 IPv4 from /system/network/interfaces (standalone private IP)."""
        data = self.network_interfaces()
        resources = data.get("resources") if isinstance(data, dict) else None
        if not isinstance(resources, list):
            return None
        for iface in resources:
            if not isinstance(iface, dict):
                continue
            inet = iface.get("inet")
            if not isinstance(inet, dict):
                continue
            ip = str(inet.get("ip") or "").strip()
            if ip and _is_rfc1918_ipv4(ip):
                return ip
        return None

    def list_resources(self, path: str, *, limit: int = 100, max_pages: int = 5) -> dict[str, Any]:
        """Paginate a CM list endpoint that returns {total, resources}."""
        items: list[dict[str, Any]] = []
        total: int | None = None
        skip = 0
        for _ in range(max_pages):
            sep = "&" if "?" in path else "?"
            data = self.get_json(f"{path}{sep}skip={skip}&limit={limit}")
            if not isinstance(data, dict):
                break
            if total is None and data.get("total") is not None:
                try:
                    total = int(data["total"])
                except (TypeError, ValueError):
                    total = None
            page = _resources_list(data)
            items.extend(page)
            if not page or len(page) < limit:
                break
            skip += len(page)
            if total is not None and skip >= total:
                break
        return {"total": total if total is not None else len(items), "resources": items}

    def fetch_ops_snapshot(self) -> dict[str, Any]:
        """Collect backups / scheduler / cluster status for dashboards (not Prometheus)."""
        out: dict[str, Any] = {"fetched_at": time.time()}

        # Backups (domain-scoped to login domain — UI labels as Root domain only)
        try:
            backups = self.list_resources("/backups", limit=100, max_pages=3)
            items = backups["resources"]
            by_status: dict[str, int] = {}
            by_scope: dict[str, int] = {}
            for item in items:
                st = str(item.get("status") or "unknown")
                by_status[st] = by_status.get(st, 0) + 1
                sc = str(item.get("scope") or "unknown")
                by_scope[sc] = by_scope.get(sc, 0) + 1
            recent = sorted(
                items,
                key=lambda x: str(x.get("createdAt") or ""),
                reverse=True,
            )[:15]
            out["backups"] = {
                "total": backups["total"],
                "by_status": by_status,
                "by_scope": by_scope,
                "recent": [
                    {
                        "id": r.get("id"),
                        "status": r.get("status"),
                        "scope": r.get("scope"),
                        "createdAt": r.get("createdAt"),
                        "description": (r.get("description") or "")[:120],
                        "productVersion": r.get("productVersion"),
                    }
                    for r in recent
                ],
            }
        except CMClientError as exc:
            out["backups"] = {"error": str(exc)}

        # Users — top by logins_count (domain-scoped REST is intentional for Overview).
        # Do not fetch /vault/keys2 for totals — use Prometheus DEKs for appliance-wide keys.
        try:
            users = self.list_resources("/usermgmt/users", limit=100, max_pages=5)
            items = users["resources"]
            ranked = [
                u
                for u in items
                if isinstance(u, dict)
                and int(u.get("logins_count") or 0) > 0
            ]
            ranked.sort(key=lambda u: int(u.get("logins_count") or 0), reverse=True)
            top = []
            for u in ranked[:5]:
                top.append(
                    {
                        "username": u.get("username") or "",
                        "name": u.get("name") or "",
                        "email": u.get("email") or "",
                        "last_login": u.get("last_login") or "",
                        "logins_count": int(u.get("logins_count") or 0),
                    }
                )
            out["users"] = {
                "total": users["total"],
                "with_login": len(ranked),
                "top_recent_logins": top,
            }
        except CMClientError as exc:
            out["users"] = {"error": str(exc), "total": 0, "top_recent_logins": []}

        # Scheduler job configs
        try:
            configs = self.list_resources("/scheduler/job-configs", limit=100, max_pages=5)
            items = configs["resources"]
            by_op: dict[str, int] = {}
            enabled = disabled = 0
            for item in items:
                op = str(item.get("operation") or "unknown")
                by_op[op] = by_op.get(op, 0) + 1
                if item.get("disabled"):
                    disabled += 1
                else:
                    enabled += 1
            out["scheduler_configs"] = {
                "total": configs["total"],
                "enabled": enabled,
                "disabled": disabled,
                "by_operation": by_op,
                "items": [
                    {
                        "name": i.get("name"),
                        "operation": i.get("operation"),
                        "run_at": i.get("run_at"),
                        "run_on": i.get("run_on"),
                        "disabled": bool(i.get("disabled")),
                        "updatedAt": i.get("updatedAt") or i.get("createdAt"),
                    }
                    for i in sorted(items, key=lambda x: str(x.get("name") or ""))
                ][:40],
            }
        except CMClientError as exc:
            out["scheduler_configs"] = {"error": str(exc)}

        # Recent scheduler job runs (page only — totals can be huge)
        try:
            jobs = self.get_json("/scheduler/jobs?limit=100&sort=-createdAt")
            if not isinstance(jobs, dict):
                jobs = {}
            items = _resources_list(jobs)
            by_status = {}
            by_op = {}
            for item in items:
                st = str(item.get("status") or "unknown")
                by_status[st] = by_status.get(st, 0) + 1
                op = str(item.get("operation") or "unknown")
                by_op[op] = by_op.get(op, 0) + 1
            out["scheduler_jobs"] = {
                "total": jobs.get("total"),
                "recent_count": len(items),
                "by_status": by_status,
                "by_operation": by_op,
                "recent": [
                    {
                        "name": j.get("name"),
                        "operation": j.get("operation"),
                        "status": j.get("status"),
                        "createdAt": j.get("createdAt"),
                        "processing_node": j.get("processing_node"),
                    }
                    for j in items[:20]
                ],
            }
        except CMClientError as exc:
            out["scheduler_jobs"] = {"error": str(exc)}

        # Quorum profiles + policy active status (/v1/quorum-mgmt/*)
        try:
            profiles = self.list_resources("/quorum-mgmt/profiles", limit=100, max_pages=5)
            status = self.list_resources("/quorum-mgmt/policy/status", limit=100, max_pages=5)
            profile_items = profiles["resources"]
            status_items = status["resources"]

            by_category: dict[str, int] = {}
            approvals: list[float] = []
            auto_exec = 0
            for item in profile_items:
                cat = str(item.get("category") or "unknown")
                by_category[cat] = by_category.get(cat, 0) + 1
                req = item.get("required_approvals")
                if isinstance(req, (int, float)):
                    approvals.append(float(req))
                if item.get("auto_executable"):
                    auto_exec += 1

            active = 0
            inactive = 0
            active_ops: list[dict[str, Any]] = []
            for item in status_items:
                if item.get("active"):
                    active += 1
                    ops = item.get("operation") or []
                    if isinstance(ops, list):
                        op_label = ", ".join(str(x) for x in ops)
                    else:
                        op_label = str(ops)
                    active_ops.append(
                        {
                            "operation": op_label,
                            "profile": item.get("profile"),
                            "description": (item.get("description") or "")[:160],
                        }
                    )
                else:
                    inactive += 1

            avg_approvals = (sum(approvals) / len(approvals)) if approvals else None
            out["quorum"] = {
                "profiles_total": profiles["total"],
                "status_total": status["total"],
                "active": active,
                "inactive": inactive,
                "auto_executable": auto_exec,
                "avg_required_approvals": avg_approvals,
                "by_category": by_category,
                "active_ops": active_ops,
                "profiles": [
                    {
                        "name": p.get("name"),
                        "category": p.get("category"),
                        "operation_label": p.get("operation_label"),
                        "required_approvals": p.get("required_approvals"),
                        "voter_groups": ", ".join(p.get("voter_groups") or [])
                        if isinstance(p.get("voter_groups"), list)
                        else (p.get("voter_groups") or ""),
                        "auto_executable": bool(p.get("auto_executable")),
                        "expiration_period": p.get("expiration_period"),
                    }
                    for p in sorted(
                        profile_items,
                        key=lambda x: (
                            str(x.get("category") or ""),
                            str(x.get("name") or ""),
                        ),
                    )
                ],
                "statuses": [
                    {
                        "operation": (
                            ", ".join(str(x) for x in (s.get("operation") or []))
                            if isinstance(s.get("operation"), list)
                            else str(s.get("operation") or "")
                        ),
                        "active": bool(s.get("active")),
                        "profile": s.get("profile"),
                        "description": (s.get("description") or "")[:160],
                    }
                    for s in sorted(
                        status_items,
                        key=lambda x: (0 if x.get("active") else 1, str(x.get("profile") or "")),
                    )
                ],
            }
        except CMClientError as exc:
            out["quorum"] = {"error": str(exc)}

        # Cluster raft / node count
        try:
            cluster = self.get_json("/cluster")
            if isinstance(cluster, dict):
                status = cluster.get("status")
                if isinstance(status, dict):
                    status_text = status.get("description") or status.get("code")
                else:
                    status_text = status
                out["cluster_api"] = {
                    "nodeID": cluster.get("nodeID") or cluster.get("node_id"),
                    "nodeCount": cluster.get("nodeCount") or cluster.get("node_count"),
                    "raftStatus": cluster.get("raftStatus") or cluster.get("raft_status"),
                    "status": status_text,
                }
        except CMClientError as exc:
            out["cluster_api"] = {"error": str(exc)}

        # System properties (Admin Settings > Properties) via /configs/properties
        try:
            props = self.list_resources("/configs/properties", limit=100, max_pages=3)
            items = [
                {
                    "name": r.get("name") or "",
                    "value": "" if r.get("value") is None else str(r.get("value")),
                    "description": (r.get("description") or "")[:240],
                }
                for r in props["resources"]
                if isinstance(r, dict)
            ]
            items.sort(key=lambda x: str(x.get("name") or "").lower())
            out["system_properties"] = {
                "total": props["total"],
                "items": items,
            }
        except CMClientError as exc:
            out["system_properties"] = {"error": str(exc), "total": 0, "items": []}

        # Network interfaces (web/nae/kmip/ssh/snmp) via /configs/interfaces
        try:
            out["interfaces"] = self._fetch_interfaces_snapshot()
        except CMClientError as exc:
            out["interfaces"] = {"error": str(exc), "total": 0, "items": []}

        return out

    def _fetch_interfaces_snapshot(self) -> dict[str, Any]:
        """Normalize /configs/interfaces + resolve trusted CA CNs."""
        ifaces = self.list_resources("/configs/interfaces", limit=100, max_pages=3)
        ca_cn = self._ca_cn_index()

        type_order = {"web": 0, "nae": 1, "kmip": 2, "ssh": 3, "snmp": 4}
        items: list[dict[str, Any]] = []
        by_type: dict[str, int] = {}
        pqc_enabled_count = 0
        enabled_count = 0

        for raw in ifaces["resources"]:
            if not isinstance(raw, dict):
                continue
            itype = str(raw.get("interface_type") or raw.get("name") or "unknown")
            by_type[itype] = by_type.get(itype, 0) + 1
            enabled = bool(raw.get("enabled"))
            if enabled:
                enabled_count += 1

            groups = raw.get("tls_groups") if isinstance(raw.get("tls_groups"), list) else []
            ciphers = raw.get("tls_ciphers") if isinstance(raw.get("tls_ciphers"), list) else []
            # PQC TLS groups/ciphers apply to the Web UI interface only.
            is_web = itype.strip().lower() == "web" or str(raw.get("name") or "").strip().lower() == "web"
            pqc_groups = _pqc_enabled_groups(groups) if is_web else []
            pqc_ciphers = _pqc_enabled_ciphers(ciphers) if is_web else []
            pqc_on = bool(pqc_groups or pqc_ciphers) if is_web else False
            if is_web and pqc_on:
                pqc_enabled_count += 1

            tcas = raw.get("trusted_cas") if isinstance(raw.get("trusted_cas"), dict) else {}
            local_uris = [str(x) for x in (tcas.get("local") or []) if x]
            external_uris = [str(x) for x in (tcas.get("external") or []) if x]

            items.append(
                {
                    "name": raw.get("name") or "",
                    "interface_type": itype,
                    "mode": raw.get("mode") or "—",
                    "enabled": enabled,
                    "port": raw.get("port"),
                    "network_interface": raw.get("network_interface") or "",
                    "minimum_tls_version": _fmt_tls_ver(raw.get("minimum_tls_version")),
                    "maximum_tls_version": _fmt_tls_ver(raw.get("maximum_tls_version")),
                    "pqc_applicable": is_web,
                    "pqc_enabled": pqc_on,
                    "pqc_groups": ", ".join(pqc_groups) if pqc_groups else "",
                    "cert_user_field": raw.get("cert_user_field") or "",
                    "local_trusted_cas": _format_ca_list(local_uris, ca_cn),
                    "external_trusted_cas": _format_ca_list(external_uris, ca_cn),
                    "auto_gen_cn": (
                        (raw.get("local_auto_gen_attributes") or {}).get("cn")
                        if isinstance(raw.get("local_auto_gen_attributes"), dict)
                        else ""
                    )
                    or "",
                }
            )

        items.sort(
            key=lambda x: (
                type_order.get(str(x.get("interface_type") or ""), 99),
                str(x.get("name") or "").lower(),
            )
        )
        return {
            "total": ifaces["total"],
            "enabled": enabled_count,
            "pqc_enabled_interfaces": pqc_enabled_count,
            "by_type": by_type,
            "items": items,
        }

    def _ca_cn_index(self) -> dict[str, str]:
        """Map CA uri/id → CN (from subject) for local + external CAs."""
        index: dict[str, str] = {}
        for path in ("/ca/local-cas", "/ca/external-cas"):
            try:
                data = self.list_resources(path, limit=100, max_pages=5)
            except CMClientError:
                continue
            for r in data["resources"]:
                if not isinstance(r, dict):
                    continue
                cn = _cn_from_subject(r.get("subject")) or (r.get("name") or "")
                if not cn:
                    continue
                for key in (r.get("uri"), r.get("id")):
                    if key:
                        index[str(key)] = cn
                        # Also index bare UUID suffix
                        if ":" in str(key):
                            index[str(key).rsplit(":", 1)[-1]] = cn
        return index

    def ensure_metrics_token(self) -> str:
        """Enable or fetch the Prometheus scrape bearer token."""
        permission_exc: CMClientError | None = None

        def _note_permission(exc: CMClientError) -> None:
            nonlocal permission_exc
            if _is_prometheus_permission_error(exc):
                permission_exc = exc

        # Prefer status if already enabled
        try:
            status = self.get_json("/system/metrics/prometheus/status")
            token = _extract_token(status)
            if token:
                self.metrics_token = token
                return token
        except CMClientError as exc:
            logger.debug("metrics status: %s", exc)
            _note_permission(exc)

        try:
            enabled = self.post_json("/system/metrics/prometheus/enable")
            token = _extract_token(enabled)
            if token:
                self.metrics_token = token
                return token
        except CMClientError as exc:
            # Already enabled may return an error — try status / renew
            logger.info("metrics enable: %s", exc)
            _note_permission(exc)

        try:
            status = self.get_json("/system/metrics/prometheus/status")
            token = _extract_token(status)
            if token:
                self.metrics_token = token
                return token
        except CMClientError as exc:
            _note_permission(exc)

        try:
            renewed = self.post_json("/system/metrics/prometheus/renew-token")
            token = _extract_token(renewed)
            if token:
                self.metrics_token = token
                return token
        except CMClientError as exc:
            _note_permission(exc)
            if permission_exc or _is_prometheus_permission_error(exc):
                raise _prometheus_permission_error(permission_exc or exc) from exc
            raise CMClientError(f"Unable to obtain Prometheus metrics token: {exc}") from exc

        if permission_exc:
            raise _prometheus_permission_error(permission_exc) from permission_exc
        raise CMClientError("Prometheus metrics token not found in CM responses")

    def scrape_metrics(self, metrics_token: str | None = None) -> list[Sample]:
        token = metrics_token or self.metrics_token or self.ensure_metrics_token()
        url = f"{self.base}/system/metrics/prometheus"
        # Keep a longer read budget for large Prometheus dumps unless caller
        # tightened timeout (manual Refresh of possibly-dead hosts).
        scrape_timeout = self.timeout if self.timeout < 30 else max(self.timeout, 60.0)
        resp = self.session.get(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"},
            timeout=scrape_timeout,
        )
        if resp.status_code >= 400:
            # Token may have been rotated — refresh once
            token = self.ensure_metrics_token()
            resp = self.session.get(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"},
                timeout=scrape_timeout,
            )
        if resp.status_code >= 400:
            raise CMClientError(
                f"Metrics scrape failed ({resp.status_code}): {resp.text[:300]}",
                status_code=resp.status_code,
            )
        return parse_prometheus_text(resp.text)

    def list_cluster_nodes(self) -> list[dict[str, Any]]:
        """Discover cluster peers via REST (best-effort across CM versions)."""
        # Prefer /cluster/summary — it includes nodeInfo.publicAddress per member.
        # Plain /cluster only returns this node's raft status (no peer hosts).
        candidates = (
            "/cluster/summary",
            "/cluster/nodes",
            "/system/cluster/nodes",
            "/system/cluster/summary",
            "/cluster",
            "/nodes",
        )
        for path in candidates:
            try:
                data = self.get_json(path)
            except CMClientError:
                continue
            nodes = _normalize_nodes(data)
            if nodes:
                return nodes
        return []

    def discover_cluster_hosts(self, samples: list[Sample] | None = None) -> list[dict[str, Any]]:
        """Combine REST cluster APIs + metrics host labels.

        Prefer publicAddress for scrape targets; keep private host for display.
        """
        nodes = self.list_cluster_nodes()
        by_key: dict[str, dict[str, Any]] = {}
        for node in nodes:
            public = _pick_public_host(node)
            private = _pick_private_host(node)
            host = public or private
            if not host:
                continue
            node_id = (
                node.get("nodeID")
                or node.get("node_id")
                or node.get("id")
                or node.get("uuid")
            )
            key = str(node_id or host).lower()
            by_key[key] = {
                "host": host,
                "public_host": public,
                "private_host": private,
                "node_id": node_id,
                "status": _scalar_status(
                    node.get("status") or node.get("state") or node.get("connection_status")
                ),
                "is_this_node": False,
                "raw": node,
                "source": "api",
            }

        # Mark the node that matches the appliance we connected to
        self_host = (urlparse(self.host).hostname or self.host or "").lower()
        for peer in by_key.values():
            hosts = {
                (peer.get("host") or "").lower(),
                (peer.get("public_host") or "").lower(),
                (peer.get("private_host") or "").lower(),
            }
            if self_host and self_host in hosts:
                peer["is_this_node"] = True
                if peer.get("status") in (None, "ready", "seen_in_metrics"):
                    peer["status"] = "self"

        if samples:
            for sample in samples:
                if not sample.name.startswith("ciphertrust_cluster_"):
                    continue
                host = sample.labels.get("host") or sample.labels.get("node") or sample.labels.get("peer")
                if not host:
                    continue
                # Metrics often label the private cluster IP — only add if unseen
                # and no public address is already known for this private host.
                already = any(
                    (p.get("private_host") or "").lower() == host.lower()
                    or (p.get("host") or "").lower() == host.lower()
                    for p in by_key.values()
                )
                if already:
                    continue
                key = host.lower()
                by_key[key] = {
                    "host": host,
                    "public_host": None,
                    "private_host": host,
                    "node_id": sample.labels.get("node_id") or sample.labels.get("id"),
                    "status": "seen_in_metrics",
                    "is_this_node": False,
                    "source": "metrics",
                }

        # Always include self hostname/IP from configured host if missing
        if self_host:
            already = any(
                (p.get("host") or "").lower() == self_host
                or (p.get("public_host") or "").lower() == self_host
                for p in by_key.values()
            )
            if not already:
                by_key[self_host] = {
                    "host": self_host,
                    "public_host": self_host,
                    "private_host": None,
                    "node_id": None,
                    "status": "self",
                    "is_this_node": True,
                    "source": "self",
                }

        return list(by_key.values())


def _resources_list(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    res = data.get("resources")
    if isinstance(res, list):
        return [x for x in res if isinstance(x, dict)]
    if isinstance(res, dict):
        return [x for x in res.values() if isinstance(x, dict)]
    return []


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:  # noqa: BLE001
        return resp.text


def _extract_token(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("token", "api_token", "prometheus_token", "bearer_token", "metrics_token"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    # nested
    for key in ("data", "result", "status"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            token = _extract_token(nested)
            if token:
                return token
    return None


def _normalize_nodes(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []

    # /v1/cluster/summary: { resources: { <id>: { clusterSummary: { <nodeId>: { nodeInfo: {...} }}}}}
    resources = data.get("resources")
    if isinstance(resources, dict):
        by_id: dict[str, dict[str, Any]] = {}
        for _rid, res in resources.items():
            if not isinstance(res, dict):
                continue
            summary = res.get("clusterSummary") or res.get("cluster_summary") or {}
            if isinstance(summary, dict):
                for nid, entry in summary.items():
                    if not isinstance(entry, dict):
                        continue
                    info = entry.get("nodeInfo") or entry.get("node_info") or entry
                    if not isinstance(info, dict):
                        continue
                    node = dict(info)
                    node.setdefault("nodeID", nid)
                    key = str(node.get("nodeID") or nid)
                    # Prefer entries that include publicAddress when duplicates appear
                    prev = by_id.get(key)
                    if prev is None or (node.get("publicAddress") and not prev.get("publicAddress")):
                        by_id[key] = node
        if by_id:
            return list(by_id.values())

    # Prefer explicit node lists; merge local_node when present.
    local = data.get("local_node") or data.get("this_node") or data.get("self")
    for key in ("nodes", "items", "members", "cluster_nodes", "node_list"):
        val = data.get(key)
        if isinstance(val, list):
            out = [x for x in val if isinstance(x, dict)]
            if isinstance(local, dict):
                local_host = _pick_public_host(local) or _pick_private_host(local)
                if local_host and not any(
                    (_pick_public_host(n) or _pick_private_host(n) or "").lower() == local_host.lower()
                    for n in out
                ):
                    out = [local] + out
            if out:
                return out

    # single node object with address fields
    if any(
        k in data
        for k in (
            "host",
            "hostname",
            "host_name",
            "publicAddress",
            "public_address",
            "url",
            "node_host",
        )
    ):
        return [data]
    if isinstance(local, dict):
        return [local]
    return []


def _host_str(val: Any) -> str | None:
    if isinstance(val, str) and val.strip():
        raw = val.strip()
        if "://" in raw:
            return urlparse(raw).hostname or raw
        return raw
    if isinstance(val, dict):
        return _pick_public_host(val) or _pick_private_host(val)
    return None


def _pick_public_host(node: dict[str, Any]) -> str | None:
    for key in ("publicAddress", "public_address", "public_hostname", "publicHostname"):
        host = _host_str(node.get(key))
        if host:
            return host
    return None


def _is_rfc1918_ipv4(ip: str) -> bool:
    """True for private IPv4 (10/8, 172.16/12, 192.168/16, loopback)."""
    h = (ip or "").strip().lower().split("%")[0].split(":")[0]
    if not h or h == "localhost":
        return True
    if h.startswith("10.") or h.startswith("192.168.") or h.startswith("127."):
        return True
    if h.startswith("172."):
        try:
            second = int(h.split(".")[1])
            return 16 <= second <= 31
        except (IndexError, ValueError):
            return False
    return False


def _pick_private_host(node: dict[str, Any]) -> str | None:
    for key in (
        "host",
        "hostname",
        "host_name",
        "node_host",
        "private_address",
        "privateAddress",
        "cluster_address",
        "address",
        "ip",
        "url",
    ):
        host = _host_str(node.get(key))
        if host:
            return host
    return None


def _pick_host(node: dict[str, Any]) -> str | None:
    """Prefer public address for scrape/connect targets."""
    return _pick_public_host(node) or _pick_private_host(node)


def _scalar_status(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        text = str(value).strip()
        return text or None
    if isinstance(value, dict):
        for key in ("status", "state", "name", "value", "description", "code"):
            nested = value.get(key)
            if isinstance(nested, (str, int, float, bool)) and str(nested).strip():
                # Prefer human description when present
                if key == "code" and isinstance(value.get("description"), str):
                    return str(value["description"]).strip()
                return str(nested).strip()
    return str(value)[:200]


def _is_prometheus_permission_error(exc: CMClientError) -> bool:
    """True when CM rejected metrics enable/status due to insufficient privileges."""
    code = exc.status_code
    if code in {401, 403}:
        return True
    text = str(exc).lower()
    markers = (
        "forbidden",
        "permission",
        "not authorized",
        "unauthorized",
        "access denied",
        "insufficient",
        "read-only",
        "readonly",
        "not allowed",
        "ncerrforbidden",
        "ncerrunauthorized",
    )
    return any(m in text for m in markers)


def _prometheus_permission_error(exc: CMClientError) -> CMClientError:
    message = (
        "This account cannot enable Prometheus metrics (likely read-only). "
        "Ask an admin to enable Prometheus under Admin Settings > Metrics, "
        "then re-add this appliance with a user that can read the metrics token."
    )
    return CMClientError(message, status_code=exc.status_code or 403, payload=exc.payload)


# Post-quantum / hybrid TLS group & cipher name markers (CM tls_groups / tls_ciphers).
_PQC_MARKERS = (
    "mlkem",
    "ml-kem",
    "kyber",
    "dilithium",
    "mldsa",
    "ml-dsa",
    "falcon",
    "sphincs",
    "hqc",
    "bike",
    "frodo",
    "pqc",
)


def _fmt_tls_ver(value: Any) -> str:
    if value is None or value == "":
        return "—"
    text = str(value).strip().lower().replace("-", "_")
    mapping = {
        "tls_1_0": "TLS 1.0",
        "tls_1_1": "TLS 1.1",
        "tls_1_2": "TLS 1.2",
        "tls_1_3": "TLS 1.3",
        "tls1_0": "TLS 1.0",
        "tls1_1": "TLS 1.1",
        "tls1_2": "TLS 1.2",
        "tls1_3": "TLS 1.3",
    }
    return mapping.get(text, str(value))


def _is_pqc_name(name: str) -> bool:
    low = (name or "").lower().replace("_", "").replace("-", "")
    return any(m.replace("-", "") in low for m in _PQC_MARKERS)


def _pqc_enabled_groups(groups: list[Any]) -> list[str]:
    out: list[str] = []
    for g in groups:
        if isinstance(g, dict):
            name = str(g.get("group_name") or g.get("name") or "")
            if g.get("enabled") and name and _is_pqc_name(name):
                out.append(name)
        elif isinstance(g, str) and _is_pqc_name(g):
            out.append(g)
    return out


def _pqc_enabled_ciphers(ciphers: list[Any]) -> list[str]:
    out: list[str] = []
    for c in ciphers:
        if isinstance(c, dict):
            name = str(c.get("cipher_suite") or c.get("name") or "")
            if c.get("enabled") and name and _is_pqc_name(name):
                out.append(name)
        elif isinstance(c, str) and _is_pqc_name(c):
            out.append(c)
    return out


def _cn_from_subject(subject: Any) -> str | None:
    """Extract CN from OpenSSL-style subject string or dict."""
    if isinstance(subject, dict):
        for key in ("CN", "cn", "commonName", "common_name"):
            if subject.get(key):
                return str(subject[key]).strip()
        return None
    if not isinstance(subject, str) or not subject.strip():
        return None
    text = subject.strip().strip("/")
    for part in text.replace(",", "/").split("/"):
        part = part.strip()
        if part.upper().startswith("CN="):
            return part.split("=", 1)[1].strip() or None
    return None


def _format_ca_list(uris: list[str], ca_cn: dict[str, str]) -> str:
    if not uris:
        return "—"
    labels: list[str] = []
    for uri in uris:
        cn = ca_cn.get(uri) or ca_cn.get(uri.rsplit(":", 1)[-1])
        labels.append(cn if cn else uri.rsplit(":", 1)[-1][:12] + "…")
    return ", ".join(labels)
