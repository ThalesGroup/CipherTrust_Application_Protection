"""Background scraper for all registered CipherTrust appliances."""

from __future__ import annotations

import logging
import random
import threading
import time
from typing import Any
from urllib.parse import urlparse

from . import db
from .client import CMClient, CMClientError
from .config import Config
from .parser import parse_prometheus_text
from .store import MetricsStore

logger = logging.getLogger(__name__)


def _is_private_ip(host: str) -> bool:
    h = (host or "").strip().lower()
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


def _is_auto_node_name(name: str) -> bool:
    import re

    n = (name or "").strip()
    if not n:
        return True
    if re.fullmatch(r"Node\s+\d+", n, flags=re.IGNORECASE):
        return True
    if "(discovered)" in n or "(cluster)" in n:
        return True
    return False


def _tcp_reachable(host: str, *, timeout: float = 3.0) -> bool:
    """Fast TCP reachability check (avoids multi-minute blackhole hangs)."""
    import socket

    raw = (host or "").strip()
    if not raw:
        return False
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    hostname = parsed.hostname
    if not hostname:
        return False
    port = parsed.port or (443 if (parsed.scheme or "https") == "https" else 80)
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except OSError:
        return False


# Reuse a compact demo template for optional offline testing
from .scraper_demo import DemoGenerator  # noqa: E402


class MetricsScraper:
    def __init__(self, store: MetricsStore) -> None:
        self.store = store
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._clients: dict[int, CMClient] = {}
        self._demo = DemoGenerator()
        self._lock = threading.RLock()
        # Serialize scrapes per appliance so UI Refresh + background loop never overlap.
        self._scrape_locks: dict[int, threading.Lock] = {}
        # Manual Refresh job (survives browser reload / tab switches).
        self._force_lock = threading.Lock()
        self._force_thread: threading.Thread | None = None
        self._force_status: dict[str, Any] = {
            "running": False,
            "started_at": None,
            "finished_at": None,
            "ok": 0,
            "failed": 0,
            "total": 0,
            "error": None,
        }

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="cm-multi-scraper", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def force_refresh_status(self) -> dict[str, Any]:
        """Snapshot of the in-flight / last manual Refresh job."""
        with self._force_lock:
            return dict(self._force_status)

    def start_force_refresh(self) -> dict[str, Any]:
        """Kick off a fleet force-scrape on a daemon thread; return immediately.

        Safe across browser reloads — work lives in the server process.
        If a force refresh is already running, returns the current status.
        """
        with self._force_lock:
            if self._force_thread and self._force_thread.is_alive():
                return {"accepted": False, "already_running": True, **dict(self._force_status)}
            self._force_status = {
                "running": True,
                "started_at": time.time(),
                "finished_at": None,
                "ok": 0,
                "failed": 0,
                "total": 0,
                "error": None,
            }
            self._force_thread = threading.Thread(
                target=self._run_force_refresh,
                name="cm-force-refresh",
                daemon=True,
            )
            self._force_thread.start()
            return {"accepted": True, "already_running": False, **dict(self._force_status)}

    def _run_force_refresh(self) -> None:
        try:
            results = self.scrape_all(force=True)
            ok = sum(1 for r in results if r.get("ok"))
            failed = sum(1 for r in results if not r.get("ok") and not r.get("skipped"))
            with self._force_lock:
                self._force_status.update(
                    {
                        "running": False,
                        "finished_at": time.time(),
                        "ok": ok,
                        "failed": failed,
                        "total": len(results),
                        "error": None,
                    }
                )
            logger.info(
                "Force refresh finished: %s ok, %s failed, %s total",
                ok,
                failed,
                len(results),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Force refresh crashed")
            with self._force_lock:
                self._force_status.update(
                    {
                        "running": False,
                        "finished_at": time.time(),
                        "error": str(exc),
                    }
                )

    def _get_client(self, appliance: dict[str, Any]) -> CMClient:
        aid = int(appliance["id"])
        with self._lock:
            client = self._clients.get(aid)
            if client is None:
                # Prefer already-decrypted password from caller when present
                if appliance.get("password"):
                    full = appliance
                else:
                    full = db.get_appliance(aid, include_secrets=True)
                if not full:
                    raise CMClientError("Appliance not found")
                client = CMClient(
                    host=full["host"],
                    username=full["username"],
                    password=full["password"],
                    domain=full.get("domain") or "",
                )
                if full.get("jwt") and full.get("jwt_expires_at"):
                    client.jwt = full["jwt"]
                    client.jwt_expires_at = float(full["jwt_expires_at"])
                if full.get("metrics_token"):
                    client.metrics_token = full["metrics_token"]
                self._clients[aid] = client
            return client

    def invalidate_client(self, appliance_id: int) -> None:
        with self._lock:
            self._clients.pop(appliance_id, None)

    def connect_appliance(
        self,
        host: str,
        username: str,
        password: str,
        display_name: str | None = None,
        domain: str = "",
        discover_cluster: bool = True,
        location: str | None = None,
    ) -> dict[str, Any]:
        """Login, enable metrics, persist appliance, optionally auto-add cluster peers.

        Returns as soon as the appliance is reachable and registered. Metric history
        insert runs in a background thread so Add Appliance is not blocked behind a
        multi‑second SQLite write (especially while an old delete purge is running).
        """
        from . import appliance_delete

        appliance_delete.pause_purges()
        persist_store = None
        try:
            result, persist_store = self._connect_appliance_core(
                host=host,
                username=username,
                password=password,
                display_name=display_name,
                domain=domain,
                discover_cluster=discover_cluster,
                location=location,
            )
        except Exception:
            appliance_delete.resume_purges()
            raise

        def _bg_persist() -> None:
            try:
                if persist_store is not None:
                    persist_store.persist_last_ingest()
            except Exception:  # noqa: BLE001
                logger.warning("Background persist after connect failed", exc_info=True)
            finally:
                appliance_delete.resume_purges()

        threading.Thread(target=_bg_persist, name="cm-connect-persist", daemon=True).start()
        return result

    def _connect_appliance_core(
        self,
        host: str,
        username: str,
        password: str,
        display_name: str | None = None,
        domain: str = "",
        discover_cluster: bool = True,
        location: str | None = None,
    ) -> tuple[dict[str, Any], Any]:
        client = CMClient(host=host, username=username, password=password, domain=domain)
        client.login()
        metrics_token = client.ensure_metrics_token()
        info = {}
        try:
            info = client.system_info()
        except CMClientError:
            pass

        appliance = db.create_or_update_appliance(
            host=client.host,
            username=username,
            password=password,
            display_name=display_name,
            domain=domain,
            location=location,
        )
        aid = int(appliance["id"])
        db.update_appliance_auth(
            aid,
            jwt=client.jwt,
            jwt_expires_at=client.jwt_expires_at,
            metrics_token=metrics_token,
            node_host=urlparse(client.host).hostname,
        )
        if info:
            db.update_appliance_system_info(aid, info)
        try:
            # Standalone private IP from NIC config (no-op if clustered / already set).
            self._maybe_fill_standalone_private_ip(aid, db.get_appliance(aid) or appliance, client)
        except CMClientError:
            pass
        try:
            snap = client.fetch_ops_snapshot()
            if snap:
                db.update_appliance_ops_snapshot(aid, snap)
        except CMClientError:
            pass
        self.invalidate_client(aid)
        self._clients[aid] = client

        # Initial scrape into memory + status; SQLite history flush is deferred.
        samples = client.scrape_metrics(metrics_token)
        store = self.store.for_appliance(aid, hydrate=False)
        store.ingest(samples, source="live", persist=False)
        db.update_appliance_scrape(aid, ok=True, sample_count=len(samples), source="live")

        # Prefetch ksctl from this CM's public /downloads zip (no auth) for healthcheck.
        try:
            from . import healthcheck_runner

            healthcheck_runner.ensure_ksctl_async(client.host)
        except Exception:  # noqa: BLE001
            logger.debug("ksctl prefetch schedule failed", exc_info=True)

        peers: list[dict[str, Any]] = []
        added_peers: list[dict[str, Any]] = []
        try:
            peers = client.discover_cluster_hosts(samples)
            db.replace_cluster_peers(aid, peers, source="api+metrics")
            clustered = len([p for p in peers if p.get("source") != "self"]) > 0
            db.update_appliance_auth(aid, is_clustered=clustered)
            if discover_cluster and clustered:
                added_peers = self._auto_add_peers(appliance, peers, username, password, domain)
        except CMClientError as exc:
            logger.warning("Cluster discovery failed for %s: %s", client.host, exc)

        appliance = db.get_appliance(aid)
        try:
            db.record_fleet_health_sample(force=True)
        except Exception:  # noqa: BLE001
            logger.debug("fleet health sample after connect failed", exc_info=True)
        return (
            {
                "appliance": appliance,
                "sample_count": len(samples),
                "system_info": info,
                "cluster_peers": peers,
                "auto_added": added_peers,
            },
            store,
        )

    def _auto_add_peers(
        self,
        source_appliance: dict[str, Any],
        peers: list[dict[str, Any]],
        username: str,
        password: str,
        domain: str,
    ) -> list[dict[str, Any]]:
        """Register discovered peer hosts.

        Handles both cases:
        - nodeInfo.publicAddress present → scrape via public IP
        - no publicAddress → try private host (may work on same network; else stays as error member)
        """
        # Members must never re-parent the cluster (avoids primary flipping on scrape).
        if source_appliance.get("parent_appliance_id"):
            return []

        added: list[dict[str, Any]] = []
        parent_id = int(source_appliance["id"])
        source_host = (urlparse(source_appliance["host"]).hostname or "").lower()
        db.update_appliance_auth(
            parent_id,
            is_clustered=True,
            cluster_role="primary",
            clear_parent=True,
        )

        # Build ordered node list: self first, then peers by host (stable Node 1..N naming)
        nodes: list[dict[str, Any]] = []
        for peer in peers:
            public = (peer.get("public_host") or "").strip() or None
            private = (peer.get("private_host") or "").strip() or None
            scrape_host = public or (peer.get("host") or "").strip() or private
            if not scrape_host:
                continue
            nodes.append({**peer, "public_host": public, "private_host": private, "scrape_host": scrape_host})

        def _sort_key(p: dict[str, Any]) -> tuple[int, str]:
            h = (p.get("scrape_host") or "").lower()
            is_self = h == source_host or bool(p.get("is_this_node"))
            return (0 if is_self else 1, h)

        nodes.sort(key=_sort_key)

        # Ensure primary keeps the cluster title; members get Node 2..N
        for index, peer in enumerate(nodes, start=1):
            scrape_host = peer["scrape_host"]
            private_host = peer.get("private_host") or ""
            public_host = peer.get("public_host") or ""

            # Self node = the appliance we already have (cluster heading / primary)
            if scrape_host.lower() == source_host:
                db.update_appliance_auth(
                    parent_id,
                    is_clustered=True,
                    cluster_role="primary",
                    node_id=peer.get("node_id"),
                    node_host=private_host or scrape_host,
                    public_host=public_host or scrape_host,
                    private_host=private_host or None,
                    clear_parent=True,
                )
                added.append(db.get_appliance(parent_id) or source_appliance)
                continue

            existing = db.get_appliance_by_host(scrape_host)
            if not existing and private_host:
                existing = db.get_appliance_by_host(private_host)
            if not existing and public_host:
                existing = db.get_appliance_by_host(public_host)

            auto_name = f"Node {index}"

            if existing:
                eid = int(existing["id"])
                if eid == parent_id:
                    continue
                db.update_appliance_auth(
                    eid,
                    parent_appliance_id=parent_id,
                    cluster_role="member",
                    is_clustered=True,
                    node_id=peer.get("node_id"),
                    node_host=private_host or scrape_host,
                    public_host=public_host or scrape_host,
                    private_host=private_host or None,
                )
                name = (existing.get("display_name") or "").strip()
                if _is_auto_node_name(name):
                    db.update_appliance_display_name(eid, auto_name)
                added.append(db.get_appliance(eid) or existing)
                continue

            # Prefer public scrape host; private-only is still attempted (same LAN / VPN).
            try:
                result = self.connect_appliance(
                    host=scrape_host,
                    username=username,
                    password=password,
                    display_name=auto_name,
                    domain=domain,
                    discover_cluster=False,
                )
                child = result["appliance"]
                db.update_appliance_auth(
                    int(child["id"]),
                    parent_appliance_id=parent_id,
                    cluster_role="member",
                    is_clustered=True,
                    node_id=peer.get("node_id"),
                    node_host=private_host or scrape_host,
                    public_host=public_host or scrape_host,
                    private_host=private_host or None,
                )
                db.update_appliance_display_name(int(child["id"]), auto_name)
                added.append(db.get_appliance(int(child["id"])) or child)
            except Exception as exc:  # noqa: BLE001
                logger.info("Could not auto-add peer %s: %s", scrape_host, exc)
                db.create_or_update_appliance(
                    host=scrape_host,
                    username=username,
                    password=password,
                    display_name=auto_name,
                    domain=domain,
                )
                discovered = db.get_appliance_by_host(scrape_host)
                if discovered:
                    db.update_appliance_auth(
                        int(discovered["id"]),
                        parent_appliance_id=parent_id,
                        cluster_role="member",
                        is_clustered=True,
                        node_id=peer.get("node_id"),
                        node_host=private_host or scrape_host,
                        public_host=public_host or scrape_host,
                        private_host=private_host or None,
                    )
                    db.update_appliance_display_name(int(discovered["id"]), auto_name)
                    db.update_appliance_scrape(
                        int(discovered["id"]),
                        ok=False,
                        error=f"Cluster peer unreachable via {scrape_host}: {exc}",
                        source="discovery",
                    )
                    added.append(db.get_appliance(int(discovered["id"])) or discovered)

        return added

    def _scrape_with_metrics_token(
        self, appliance: dict[str, Any], *, timeout: float | None = None
    ) -> list[Any]:
        """Scrape using stored Prometheus token only (no password/JWT needed)."""
        token = appliance.get("metrics_token")
        if not token:
            raise CMClientError("No metrics token stored; reconnect the appliance")
        client = CMClient(
            host=appliance["host"],
            username=appliance.get("username") or "metrics",
            password="",
            timeout=timeout or 30.0,
        )
        client.metrics_token = token
        return client.scrape_metrics(token)

    def _client_from_stored_jwt(self, appliance: dict[str, Any]) -> CMClient | None:
        """Build a client that can call REST using a still-valid stored JWT (no password)."""
        jwt = appliance.get("jwt")
        expires = float(appliance.get("jwt_expires_at") or 0)
        if not jwt or time.time() >= expires:
            return None
        client = CMClient(
            host=appliance["host"],
            username=appliance.get("username") or "metrics",
            password="",
        )
        client.jwt = jwt
        client.jwt_expires_at = expires
        if appliance.get("metrics_token"):
            client.metrics_token = appliance["metrics_token"]
        return client

    def _refresh_system_info(
        self,
        appliance_id: int,
        appliance: dict[str, Any],
        client: CMClient,
        *,
        force: bool = False,
    ) -> None:
        needs_info = not appliance.get("cm_version")
        last_info = float(appliance.get("system_info_at") or 0)
        if force or needs_info or (time.time() - last_info) > 900:
            info = client.system_info()
            if info:
                db.update_appliance_system_info(appliance_id, info)
        # Standalone private IP: cheap NIC lookup; run even when system_info is fresh.
        self._maybe_fill_standalone_private_ip(appliance_id, appliance, client)

    def _maybe_fill_standalone_private_ip(
        self,
        appliance_id: int,
        appliance: dict[str, Any],
        client: CMClient,
    ) -> None:
        """Populate private_host for non-clustered appliances via /system/network/interfaces.

        Does not change host (connect URL), public_host, or scrape target.
        Skips clustered nodes (they already have private from cluster API).
        """
        if appliance.get("is_clustered") or appliance.get("parent_appliance_id"):
            return
        if (appliance.get("private_host") or "").strip():
            return
        try:
            private_ip = client.pick_private_ip_from_interfaces()
        except CMClientError as exc:
            logger.debug("network interfaces lookup failed for %s: %s", appliance_id, exc)
            return
        if not private_ip:
            return
        # Also set public_host from connect URL when it looks public and is unset.
        connect = (appliance.get("host") or "").replace("https://", "").replace("http://", "").strip()
        connect_host = connect.split("/")[0].split(":")[0]
        public = (appliance.get("public_host") or "").strip() or None
        kwargs: dict[str, Any] = {"private_host": private_ip}
        if not public and connect_host and connect_host != private_ip:
            # Hostname or public IP used to connect — keep as public display.
            from .client import _is_rfc1918_ipv4

            if not _is_rfc1918_ipv4(connect_host):
                kwargs["public_host"] = connect_host
        db.update_appliance_auth(appliance_id, **kwargs)
        logger.info(
            "Standalone appliance %s private_host=%s (from /system/network/interfaces)",
            appliance_id,
            private_ip,
        )

    def _refresh_ops_snapshot(
        self,
        appliance_id: int,
        appliance: dict[str, Any],
        client: CMClient,
        *,
        force: bool = False,
    ) -> None:
        last = float(appliance.get("ops_snapshot_at") or 0)
        # Full REST snapshot is heavier than Prometheus; refresh on its own cadence
        # (or immediately on manual Refresh / first fetch).
        min_age = max(30, int(Config.OPS_SNAPSHOT_INTERVAL))
        if not force and last and (time.time() - last) < min_age:
            return
        snap = client.fetch_ops_snapshot()
        if snap:
            db.update_appliance_ops_snapshot(appliance_id, snap)

    def _appliance_scrape_lock(self, appliance_id: int) -> threading.Lock:
        with self._lock:
            lock = self._scrape_locks.get(appliance_id)
            if lock is None:
                lock = threading.Lock()
                self._scrape_locks[appliance_id] = lock
            return lock

    def scrape_appliance(self, appliance_id: int, *, force: bool = False) -> dict[str, Any]:
        lock = self._appliance_scrape_lock(appliance_id)
        # Non-forced (background) scrapes skip if a scrape is already running.
        # Forced (manual Refresh) waits briefly for the in-flight scrape, then runs.
        if force:
            if not lock.acquire(timeout=45.0):
                return {
                    "ok": False,
                    "skipped": True,
                    "error": "timed out waiting for in-flight scrape",
                    "appliance_id": appliance_id,
                }
        elif not lock.acquire(blocking=False):
            return {
                "ok": False,
                "skipped": True,
                "error": "scrape already in progress",
                "appliance_id": appliance_id,
            }
        try:
            return self._scrape_appliance_locked(appliance_id, force=force)
        finally:
            lock.release()

    def _scrape_appliance_locked(self, appliance_id: int, *, force: bool = False) -> dict[str, Any]:
        decrypt_error: str | None = None
        try:
            appliance = db.get_appliance(appliance_id, include_secrets=True)
        except ValueError as exc:
            decrypt_error = str(exc)
            appliance = db.get_appliance(appliance_id, include_secrets=False)
            if appliance:
                # Metrics token + JWT without decrypting password
                tokens = db.get_appliance_auth_tokens(appliance_id)
                appliance.update({k: v for k, v in tokens.items() if v is not None})

        if not appliance:
            return {"ok": False, "error": "not found"}
        if int(appliance.get("delete_pending") or 0) == 1 or (
            appliance.get("last_status") or ""
        ).lower() in {"deleting"}:
            return {"ok": False, "skipped": True, "error": "deleting", "appliance_id": appliance_id}
        if not appliance.get("enabled"):
            return {"ok": False, "error": "disabled"}

        # After enough consecutive failures, skip auto-scrapes until the user refreshes.
        if not force and db.is_appliance_offline(appliance):
            db.ensure_offline_status(appliance_id)
            return {
                "ok": False,
                "skipped": True,
                "error": "offline",
                "appliance_id": appliance_id,
                "fail_count": int(appliance.get("fail_count") or 0),
            }
        # Capture before reset — used to apply a short connect budget only for retries.
        was_unreachable = (appliance.get("last_status") or "") in {
            "offline",
            "pending",
            "error",
        } or db.is_appliance_offline(appliance)
        if force:
            db.reset_appliance_failures(appliance_id)

        # Fast-fail blackholed / firewalled hosts before HTTP (which can hang far
        # longer than requests' timeout on some kernels when SYNs are dropped).
        host_up = True
        if force and was_unreachable:
            host_up = _tcp_reachable(str(appliance.get("host") or ""), timeout=3.0)
            if not host_up:
                err = f"TCP unreachable: {appliance.get('host')}"
                logger.warning("Scrape probe failed for appliance %s: %s", appliance_id, err)
                self.invalidate_client(appliance_id)
                try:
                    db.update_appliance_scrape(
                        appliance_id,
                        ok=False,
                        sample_count=0,
                        error=err,
                        source="error",
                        mark_offline=True,
                    )
                except Exception:  # noqa: BLE001
                    logger.warning(
                        "Could not persist probe failure for appliance %s",
                        appliance_id,
                        exc_info=True,
                    )
                return {"ok": False, "source": "error", "error": err, "appliance_id": appliance_id}

        try:
            samples: list[Any]
            if decrypt_error:
                samples = self._scrape_with_metrics_token(
                    appliance,
                    timeout=10.0 if (force and was_unreachable and not host_up) else 30.0,
                )
            else:
                client = self._get_client(appliance)
                # Unreachable (TCP down) already returned above. Reachable hosts —
                # even ones previously marked offline — get a normal timeout.
                client.set_timeout(30.0)
                # Refresh JWT periodically
                if not client.jwt or time.time() >= client.jwt_expires_at:
                    client.login()
                    db.update_appliance_auth(
                        appliance_id,
                        jwt=client.jwt,
                        jwt_expires_at=client.jwt_expires_at,
                    )
                # Always re-read the Prometheus bearer from CM status. A cached
                # token can still return HTTP 200 while reflecting stale scrapes
                # after cluster/token rotation — manual reconnect looked "fixed"
                # only because it obtained a fresh token.
                token = client.ensure_metrics_token()
                if token and token != appliance.get("metrics_token"):
                    db.update_appliance_auth(appliance_id, metrics_token=token)
                samples = client.scrape_metrics(token)

            store = self.store.for_appliance(appliance_id, hydrate=False)
            store.ingest(samples, source="live", persist=False)
            # Persist status BEFORE the heavy metric insert so Refresh/UI is not
            # blocked for minutes behind SQLite writes on large history DBs.
            try:
                db.update_appliance_scrape(
                    appliance_id, ok=True, sample_count=len(samples), source="live"
                )
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Could not persist scrape success for appliance %s (DB busy)",
                    appliance_id,
                    exc_info=True,
                )
            try:
                store.persist_last_ingest()
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Could not persist metric points for appliance %s (DB busy)",
                    appliance_id,
                    exc_info=True,
                )

            # Refresh cluster peers + system info when we have a REST client.
            # If a cluster is created later, new peers are auto-added here (same creds).
            # Only the cluster primary (no parent) may discover/add peers.
            if not decrypt_error:
                try:
                    client = self._get_client(appliance)
                    peers = client.discover_cluster_hosts(samples)
                    if peers:
                        db.replace_cluster_peers(appliance_id, peers)
                        clustered = len([p for p in peers if not p.get("is_this_node")]) > 0
                        if not appliance.get("parent_appliance_id"):
                            db.update_appliance_auth(
                                appliance_id,
                                is_clustered=clustered or bool(appliance.get("is_clustered")),
                                cluster_role="primary" if clustered else appliance.get("cluster_role"),
                            )
                            if clustered and appliance.get("password"):
                                self._auto_add_peers(
                                    appliance,
                                    peers,
                                    appliance.get("username") or "",
                                    appliance["password"],
                                    appliance.get("domain") or "",
                                )
                        else:
                            # Member: refresh peer list only; keep parent linkage
                            db.update_appliance_auth(appliance_id, is_clustered=True, cluster_role="member")
                except CMClientError:
                    pass
                try:
                    self._refresh_system_info(
                        appliance_id,
                        appliance,
                        self._get_client(appliance),
                        force=force,
                    )
                except CMClientError:
                    pass
                try:
                    self._refresh_ops_snapshot(
                        appliance_id,
                        appliance,
                        self._get_client(appliance),
                        force=force,
                    )
                except CMClientError:
                    pass
            else:
                # Still extract peers from metrics labels without REST login
                try:
                    client = CMClient(host=appliance["host"], username="x", password="x")
                    peers = client.discover_cluster_hosts(samples)
                    if peers:
                        db.replace_cluster_peers(appliance_id, peers, source="metrics")
                        clustered = len([p for p in peers if p.get("source") != "self"]) > 0
                        db.update_appliance_auth(appliance_id, is_clustered=clustered)
                except Exception:  # noqa: BLE001
                    pass
                # /v1/system/info via stored JWT when password decrypt failed
                try:
                    jwt_client = self._client_from_stored_jwt(appliance)
                    if jwt_client:
                        self._refresh_system_info(appliance_id, appliance, jwt_client)
                except CMClientError as exc:
                    logger.info(
                        "system/info skipped for appliance %s (reconnect to refresh): %s",
                        appliance_id,
                        exc,
                    )

            return {"ok": True, "source": "live", "count": len(samples), "appliance_id": appliance_id}
        except Exception as exc:  # noqa: BLE001
            # Connection timeouts are expected for dead hosts — avoid full stack traces.
            err_l = str(exc).lower()
            if "timeout" in err_l or "max retries" in err_l or "connection" in err_l:
                logger.warning("Scrape failed for appliance %s: %s", appliance_id, exc)
            else:
                logger.exception("Scrape failed for appliance %s", appliance_id)
            self.invalidate_client(appliance_id)
            if Config.DEMO_MODE:
                samples = parse_prometheus_text(self._demo.tick())
                self.store.for_appliance(appliance_id, hydrate=False).ingest(
                    samples, source="demo", error=str(exc)
                )
                db.update_appliance_scrape(
                    appliance_id, ok=False, sample_count=len(samples), error=str(exc), source="demo"
                )
                return {
                    "ok": False,
                    "source": "demo",
                    "error": str(exc),
                    "count": len(samples),
                    "appliance_id": appliance_id,
                }
            self.store.for_appliance(appliance_id, hydrate=False).ingest(
                [], source="error", error=str(exc)
            )
            try:
                # Force-retry of a previously unreachable host: one hard fail → offline
                # so the background loop stops hammering it and blocking Refresh.
                db.update_appliance_scrape(
                    appliance_id,
                    ok=False,
                    sample_count=0,
                    error=str(exc),
                    source="error",
                    mark_offline=bool(force and was_unreachable),
                )
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Could not persist scrape failure for appliance %s (DB busy)",
                    appliance_id,
                    exc_info=True,
                )
            return {"ok": False, "source": "error", "error": str(exc), "appliance_id": appliance_id}

    def scrape_all(self, *, force: bool = False) -> list[dict[str, Any]]:
        """Scrape every enabled appliance.

        Background loop uses force=False and skips known-offline hosts.
        Manual Refresh uses force=True so offline appliances are retried in parallel.
        """
        enabled = [a for a in db.list_appliances() if a.get("enabled")]
        results: list[dict[str, Any]] = []

        if not force:
            for appliance in enabled:
                status = (appliance.get("last_status") or "").lower()
                # Background loop only keeps healthy hosts fresh. Offline/error/
                # pending are retried on manual Refresh (force=True) so a sick
                # peer cannot hold scrape locks / DB writers for minutes.
                if status in {
                    "offline",
                    "error",
                    "pending",
                    "deleting",
                    "delete_failed",
                } or db.is_appliance_offline(appliance):
                    if status != "offline" and db.is_appliance_offline(appliance):
                        db.ensure_offline_status(int(appliance["id"]))
                    results.append(
                        {
                            "ok": False,
                            "skipped": True,
                            "error": status or "offline",
                            "appliance_id": int(appliance["id"]),
                            "fail_count": int(appliance.get("fail_count") or 0),
                        }
                    )
                    continue
                results.append(self.scrape_appliance(int(appliance["id"]), force=False))
                # Small stagger between appliances to avoid thundering-herd on CM/SQLite.
                time.sleep(0.5)
        else:
            # Force: scrape sequentially, but previously-unreachable hosts are
            # TCP-probed and fail in a few seconds so they cannot block the fleet.
            # (Parallel force scrapes contended on the large SQLite DB and hung.)
            for appliance in enabled:
                results.append(self.scrape_appliance(int(appliance["id"]), force=True))
                time.sleep(0.15)

        if not results and Config.DEMO_MODE:
            # Seed a demo appliance so UI is usable offline
            demo = db.create_or_update_appliance(
                host="https://demo-cm.local",
                username="demo",
                password="demo",
                display_name="Demo Appliance",
            )
            samples = parse_prometheus_text(self._demo.tick())
            store = self.store.for_appliance(int(demo["id"]), hydrate=False)
            store.ingest(samples, source="demo", persist=False)
            db.update_appliance_scrape(int(demo["id"]), ok=True, sample_count=len(samples), source="demo")
            try:
                store.persist_last_ingest()
            except Exception:  # noqa: BLE001
                logger.warning("Could not persist demo metric points (DB busy)", exc_info=True)
            results.append({"ok": True, "source": "demo", "count": len(samples), "appliance_id": demo["id"]})
        # Fleet online/offline history for the Appliances tab chart.
        try:
            db.record_fleet_health_sample(force=force)
        except Exception:  # noqa: BLE001
            logger.debug("fleet health sample failed", exc_info=True)
        return results

    def _loop(self) -> None:
        db.init_db()
        try:
            n = db.recover_stuck_pending(max_age_seconds=30.0)
            if n:
                logger.info("Cleared %s stuck pending appliance status(es) on startup", n)
        except Exception:  # noqa: BLE001
            logger.debug("recover_stuck_pending failed", exc_info=True)
        # quick initial pass
        try:
            self.scrape_all()
        except Exception:  # noqa: BLE001
            logger.exception("Initial scrape failed")
        while not self._stop.wait(Config.SCRAPE_INTERVAL):
            try:
                try:
                    db.recover_stuck_pending(max_age_seconds=180.0)
                except Exception:  # noqa: BLE001
                    pass
                self.scrape_all()
                # ~5% of scrape cycles: drop points older than HISTORY_KEEP_DAYS,
                # then PRAGMA optimize (cheap planner refresh — not a full VACUUM).
                if random.random() < 0.05:
                    deleted = db.prune_old_points()
                    if deleted:
                        logger.info(
                            "Pruned %s old metric_points (keep_days=%s); PRAGMA optimize ran",
                            deleted,
                            Config.HISTORY_KEEP_DAYS,
                        )
                    else:
                        logger.debug(
                            "Prune found nothing older than %s days; PRAGMA optimize ran",
                            Config.HISTORY_KEEP_DAYS,
                        )
            except Exception:  # noqa: BLE001
                logger.exception("Scrape loop error")
