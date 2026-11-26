"""SQLite persistence for appliances and metric history."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import Config
from .security import decrypt_text, encrypt_text

_lock = threading.RLock()
_initialized = False


def db_path() -> Path:
    path = Config.DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect(*, timeout: float = 60.0) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path(), timeout=timeout, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 60000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def connect_read(*, timeout: float = 15.0) -> Iterator[sqlite3.Connection]:
    """Read-only style connection — no commit, shorter busy wait for charts."""
    conn = sqlite3.connect(db_path(), timeout=timeout, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    try:
        yield conn
    finally:
        conn.close()


def _retry_locked(fn, *, attempts: int = 12, delay: float = 0.2):
    """Retry a DB write when SQLite reports database is locked.

    Serializes writers via the module lock so Flask requests and the scrape
    loop do not stampede the same SQLite file.
    """
    last: Exception | None = None
    for i in range(attempts):
        try:
            with _lock:
                return fn()
        except sqlite3.OperationalError as exc:
            last = exc
            msg = str(exc).lower()
            if "locked" not in msg and "busy" not in msg:
                raise
            time.sleep(delay * (i + 1))
    assert last is not None
    raise last


def init_db() -> None:
    global _initialized
    with _lock:
        if _initialized:
            return
        with connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS appliances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host TEXT NOT NULL UNIQUE,
                    display_name TEXT,
                    username TEXT NOT NULL,
                    password_enc TEXT NOT NULL,
                    domain TEXT DEFAULT '',
                    jwt TEXT,
                    jwt_expires_at REAL,
                    metrics_token TEXT,
                    cluster_id TEXT,
                    node_id TEXT,
                    node_host TEXT,
                    is_clustered INTEGER DEFAULT 0,
                    is_primary INTEGER DEFAULT 0,
                    enabled INTEGER DEFAULT 1,
                    last_scrape_at REAL,
                    last_error TEXT,
                    last_status TEXT DEFAULT 'pending',
                    sample_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cluster_peers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appliance_id INTEGER NOT NULL,
                    peer_host TEXT NOT NULL,
                    peer_node_id TEXT,
                    peer_status TEXT,
                    source TEXT,
                    discovered_at REAL NOT NULL,
                    UNIQUE(appliance_id, peer_host),
                    FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS metric_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appliance_id INTEGER NOT NULL,
                    fingerprint TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    labels_json TEXT NOT NULL,
                    ts REAL NOT NULL,
                    value REAL NOT NULL,
                    FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_metric_points_lookup
                    ON metric_points(appliance_id, fingerprint, ts);
                CREATE INDEX IF NOT EXISTS idx_metric_points_name
                    ON metric_points(appliance_id, metric_name, ts);
                CREATE INDEX IF NOT EXISTS idx_metric_points_ts
                    ON metric_points(ts);

                CREATE TABLE IF NOT EXISTS scrape_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appliance_id INTEGER NOT NULL,
                    started_at REAL NOT NULL,
                    finished_at REAL,
                    ok INTEGER,
                    source TEXT,
                    sample_count INTEGER DEFAULT 0,
                    error TEXT,
                    FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS fleet_health_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    online INTEGER NOT NULL DEFAULT 0,
                    offline INTEGER NOT NULL DEFAULT 0,
                    other INTEGER NOT NULL DEFAULT 0,
                    total INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_fleet_health_ts
                    ON fleet_health_samples(ts);
                """
            )
            # Also create fleet_health_samples on DBs that predate this table
            # (executescript above is enough on fresh init; this covers partial upgrades).
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fleet_health_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    online INTEGER NOT NULL DEFAULT 0,
                    offline INTEGER NOT NULL DEFAULT 0,
                    other INTEGER NOT NULL DEFAULT 0,
                    total INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_fleet_health_ts ON fleet_health_samples(ts)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS healthcheck_runs (
                    appliance_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'idle',
                    started_at REAL,
                    finished_at REAL,
                    overall TEXT,
                    severity_counts_json TEXT,
                    error TEXT,
                    message TEXT,
                    html_path TEXT,
                    json_path TEXT,
                    analysis_path TEXT,
                    updated_at REAL NOT NULL,
                    FOREIGN KEY (appliance_id) REFERENCES appliances(id) ON DELETE CASCADE
                )
                """
            )
            # Additive columns for CM /v1/system/info (safe on existing DBs).
            for col, typedef in (
                ("cm_name", "TEXT"),
                ("cm_version", "TEXT"),
                ("cm_model", "TEXT"),
                ("cm_vendor", "TEXT"),
                ("cm_crypto_version", "TEXT"),
                ("cm_chassis_serial", "TEXT"),
                ("system_info_at", "REAL"),
                ("parent_appliance_id", "INTEGER"),
                ("cluster_role", "TEXT"),
                ("ops_snapshot_json", "TEXT"),
                ("ops_snapshot_at", "REAL"),
                ("fail_count", "INTEGER DEFAULT 0"),
                ("cluster_display_name", "TEXT"),
                ("public_host", "TEXT"),
                ("private_host", "TEXT"),
                ("location", "TEXT"),
                ("cm_uptime", "TEXT"),
                ("delete_pending", "INTEGER DEFAULT 0"),
            ):
                try:
                    conn.execute(f"ALTER TABLE appliances ADD COLUMN {col} {typedef}")
                except sqlite3.OperationalError:
                    pass
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    appliance_id INTEGER,
                    created_at REAL NOT NULL,
                    dismissed_at REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metric_purge_queue (
                    appliance_id INTEGER PRIMARY KEY,
                    label TEXT,
                    created_at REAL NOT NULL
                )
                """
            )
            # One-time: move legacy cluster titles off primary display_name into cluster_display_name.
            try:
                rows = conn.execute(
                    """
                    SELECT id, display_name FROM appliances
                    WHERE cluster_display_name IS NULL
                      AND (cluster_role = 'primary' OR (is_clustered = 1 AND parent_appliance_id IS NULL))
                      AND display_name IS NOT NULL
                      AND display_name NOT GLOB 'Node [0-9]*'
                      AND display_name NOT GLOB 'Node [0-9][0-9]*'
                    """
                ).fetchall()
                for row in rows:
                    conn.execute(
                        """
                        UPDATE appliances
                        SET cluster_display_name = ?, display_name = 'Node 1', updated_at = ?
                        WHERE id = ?
                        """,
                        (row["display_name"], time.time(), row["id"]),
                    )
            except sqlite3.OperationalError:
                pass
        _initialized = True


# Consecutive contact failures before an appliance is marked offline and skipped.
OFFLINE_FAIL_THRESHOLD = 5


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def normalize_host(host: str) -> str:
    """Normalize CM host to a scheme://host[:port] URL.

    Bare ``cm.example.com`` → ``https://cm.example.com`` (port 443 implied).
    ``cm.example.com:8443`` / ``https://cm.example.com:8443`` keep the custom HTTPS port.
    """
    from urllib.parse import urlparse

    host = (host or "").strip()
    if not host:
        raise ValueError("host is required")
    if "://" not in host:
        host = f"https://{host}"
    host = host.rstrip("/")
    parsed = urlparse(host)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("host must be an IP, hostname, or http(s) URL")
    # Reject junk like https://host:abc
    if parsed.port is not None and not (1 <= parsed.port <= 65535):
        raise ValueError("host port must be between 1 and 65535")
    return host


def _is_private_host(host: str | None) -> bool:
    h = (host or "").strip().lower().split(":")[0]
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


def _strip_scheme(host: str | None) -> str:
    return (host or "").replace("https://", "").replace("http://", "").strip()


def enrich_appliance_network(item: dict[str, Any]) -> dict[str, Any]:
    """Add display-friendly cm_hostname / public_host / private_host when missing."""
    connect = _strip_scheme(item.get("host"))
    public = _strip_scheme(item.get("public_host")) or None
    private = _strip_scheme(item.get("private_host")) or None
    node = _strip_scheme(item.get("node_host")) or None

    if not private and node and _is_private_host(node):
        private = node
    if not public and connect and not _is_private_host(connect):
        public = connect
    if not private and connect and _is_private_host(connect):
        private = connect
    # If connect is public and node is private, keep both.
    if not public and connect and private and connect != private and not _is_private_host(connect):
        public = connect

    item["cm_hostname"] = (item.get("cm_name") or "").strip() or None
    item["public_host"] = public
    item["private_host"] = private
    return item


def list_appliances(include_secrets: bool = False) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM appliances
            WHERE COALESCE(delete_pending, 0) = 0
            ORDER BY created_at ASC
            """
        ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        if not include_secrets:
            item.pop("password_enc", None)
            item.pop("jwt", None)
            # keep metrics_token out of list responses
            item.pop("metrics_token", None)
        item.pop("ops_snapshot_json", None)
        item["is_clustered"] = bool(item.get("is_clustered"))
        item["is_primary"] = bool(item.get("is_primary"))
        item["enabled"] = bool(item.get("enabled"))
        out.append(enrich_appliance_network(item))
    return out


def list_delete_pending_appliances() -> list[dict[str, Any]]:
    """Appliances mid-async-delete (hidden from normal list)."""
    init_db()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, host, display_name, last_status, last_error, delete_pending
            FROM appliances
            WHERE COALESCE(delete_pending, 0) = 1
            ORDER BY id ASC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def get_appliance(appliance_id: int, include_secrets: bool = False) -> dict[str, Any] | None:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT * FROM appliances WHERE id = ?", (appliance_id,)).fetchone()
    item = _row_to_dict(row)
    if not item:
        return None
    if include_secrets:
        item["password"] = decrypt_text(item["password_enc"])
    else:
        item.pop("password_enc", None)
        item.pop("jwt", None)
        item.pop("metrics_token", None)
    # Keep large REST snapshot out of default appliance payloads
    item.pop("ops_snapshot_json", None)
    item["is_clustered"] = bool(item.get("is_clustered"))
    item["is_primary"] = bool(item.get("is_primary"))
    item["enabled"] = bool(item.get("enabled"))
    return enrich_appliance_network(item)


def get_appliance_auth_tokens(appliance_id: int) -> dict[str, Any]:
    """Return jwt / metrics_token without decrypting the password (for degraded scrapes)."""
    init_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT jwt, jwt_expires_at, metrics_token
            FROM appliances WHERE id = ?
            """,
            (appliance_id,),
        ).fetchone()
    if not row:
        return {}
    return dict(row)


def get_appliance_by_host(host: str, include_secrets: bool = False) -> dict[str, Any] | None:
    host = normalize_host(host)
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT * FROM appliances WHERE host = ?", (host,)).fetchone()
    if not row:
        return None
    return get_appliance(int(row["id"]), include_secrets=include_secrets)


def create_or_update_appliance(
    host: str,
    username: str,
    password: str,
    display_name: str | None = None,
    domain: str = "",
    location: str | None = None,
) -> dict[str, Any]:
    init_db()
    host = normalize_host(host)
    now = time.time()
    password_enc = encrypt_text(password)
    loc = (location or "").strip() or None
    with connect() as conn:
        existing = conn.execute("SELECT id FROM appliances WHERE host = ?", (host,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE appliances
                SET username = ?, password_enc = ?, display_name = COALESCE(?, display_name),
                    domain = ?, location = COALESCE(?, location),
                    updated_at = ?, enabled = 1, last_error = NULL, last_status = 'pending',
                    fail_count = 0
                WHERE id = ?
                """,
                (username, password_enc, display_name, domain or "", loc, now, existing["id"]),
            )
            appliance_id = int(existing["id"])
        else:
            cur = conn.execute(
                """
                INSERT INTO appliances (
                    host, display_name, username, password_enc, domain, location,
                    created_at, updated_at, enabled, last_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'pending')
                """,
                (
                    host,
                    display_name or host.replace("https://", "").replace("http://", ""),
                    username,
                    password_enc,
                    domain or "",
                    loc,
                    now,
                    now,
                ),
            )
            appliance_id = int(cur.lastrowid)
    return get_appliance(appliance_id)  # type: ignore[return-value]


def update_appliance_auth(
    appliance_id: int,
    *,
    jwt: str | None = None,
    jwt_expires_at: float | None = None,
    metrics_token: str | None = None,
    cluster_id: str | None = None,
    node_id: str | None = None,
    node_host: str | None = None,
    public_host: str | None = None,
    private_host: str | None = None,
    is_clustered: bool | None = None,
    parent_appliance_id: int | None = None,
    clear_parent: bool = False,
    cluster_role: str | None = None,
) -> None:
    init_db()
    fields: list[str] = ["updated_at = ?"]
    values: list[Any] = [time.time()]
    mapping = {
        "jwt": jwt,
        "jwt_expires_at": jwt_expires_at,
        "metrics_token": metrics_token,
        "cluster_id": cluster_id,
        "node_id": node_id,
        "node_host": node_host,
        "public_host": public_host,
        "private_host": private_host,
        "cluster_role": cluster_role,
    }
    for key, value in mapping.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    if is_clustered is not None:
        fields.append("is_clustered = ?")
        values.append(1 if is_clustered else 0)
    if clear_parent:
        fields.append("parent_appliance_id = NULL")
    elif parent_appliance_id is not None:
        fields.append("parent_appliance_id = ?")
        values.append(int(parent_appliance_id))
    values.append(appliance_id)
    with connect() as conn:
        conn.execute(f"UPDATE appliances SET {', '.join(fields)} WHERE id = ?", values)


def update_appliance_system_info(appliance_id: int, info: dict[str, Any] | None) -> None:
    """Persist /v1/system/info fields for Overview (version, model, uptime, etc.)."""
    if not info:
        return
    init_db()
    version = info.get("version") or info.get("cm_version") or info.get("software_version")
    name = info.get("name")
    model = info.get("model")
    vendor = info.get("vendor")
    crypto_version = info.get("crypto_version")
    serial = info.get("chassis_serial_number") or info.get("serial_number")
    uptime = info.get("uptime")
    if uptime is not None:
        uptime = str(uptime).strip() or None
    with connect() as conn:
        conn.execute(
            """
            UPDATE appliances SET
                cm_name = COALESCE(?, cm_name),
                cm_version = COALESCE(?, cm_version),
                cm_model = COALESCE(?, cm_model),
                cm_vendor = COALESCE(?, cm_vendor),
                cm_crypto_version = COALESCE(?, cm_crypto_version),
                cm_chassis_serial = COALESCE(?, cm_chassis_serial),
                cm_uptime = COALESCE(?, cm_uptime),
                system_info_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name,
                version,
                model,
                vendor,
                crypto_version,
                serial,
                uptime,
                time.time(),
                time.time(),
                appliance_id,
            ),
        )


def update_appliance_ops_snapshot(appliance_id: int, snapshot: dict[str, Any] | None) -> None:
    """Persist REST-derived backups/scheduler/cluster snapshot for dashboards."""
    if not snapshot:
        return
    init_db()

    def _do() -> None:
        with connect() as conn:
            conn.execute(
                """
                UPDATE appliances SET
                    ops_snapshot_json = ?,
                    ops_snapshot_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(snapshot), time.time(), time.time(), appliance_id),
            )

    _retry_locked(_do)


def get_appliance_ops_snapshot(appliance_id: int) -> dict[str, Any] | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT ops_snapshot_json, ops_snapshot_at FROM appliances WHERE id = ?",
            (appliance_id,),
        ).fetchone()
    if not row or not row["ops_snapshot_json"]:
        return None
    try:
        data = json.loads(row["ops_snapshot_json"])
    except Exception:  # noqa: BLE001
        return None
    if isinstance(data, dict):
        data.setdefault("fetched_at", row["ops_snapshot_at"])
        return data
    return None


def update_appliance_scrape(
    appliance_id: int,
    *,
    ok: bool,
    sample_count: int = 0,
    error: str | None = None,
    source: str = "live",
    mark_offline: bool = False,
) -> None:
    init_db()
    now = time.time()

    def _do() -> None:
        with connect() as conn:
            row = conn.execute(
                "SELECT fail_count FROM appliances WHERE id = ?",
                (appliance_id,),
            ).fetchone()
            prev_fails = int(row["fail_count"] or 0) if row else 0
            if ok:
                fail_count = 0
                status = "ok"
                err = None
            else:
                if mark_offline:
                    fail_count = max(prev_fails + 1, OFFLINE_FAIL_THRESHOLD)
                else:
                    fail_count = prev_fails + 1
                status = "offline" if fail_count >= OFFLINE_FAIL_THRESHOLD else "error"
                err = error
                if status == "offline" and err:
                    err = f"Offline after {fail_count} failed contacts: {err}"
                elif status == "offline":
                    err = f"Offline after {fail_count} failed contacts"
            conn.execute(
                """
                UPDATE appliances
                SET last_scrape_at = ?, last_error = ?, last_status = ?, sample_count = ?,
                    fail_count = ?, updated_at = ?
                WHERE id = ?
                """,
                (now, err, status, sample_count, fail_count, now, appliance_id),
            )
            conn.execute(
                """
                INSERT INTO scrape_runs (appliance_id, started_at, finished_at, ok, source, sample_count, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (appliance_id, now, now, 1 if ok else 0, source, sample_count, err),
            )

    _retry_locked(_do)


def reset_appliance_failures(appliance_id: int) -> None:
    """Clear fail counter so a scrape is attempted.

    Keep last_status as-is (usually 'offline') until the scrape writes ok/error —
    flipping to 'pending' left appliances stuck when a scrape was interrupted.
    """
    init_db()
    with connect() as conn:
        conn.execute(
            """
            UPDATE appliances
            SET fail_count = 0,
                updated_at = ?
            WHERE id = ?
            """,
            (time.time(), appliance_id),
        )


def recover_stuck_pending(*, max_age_seconds: float = 120.0) -> int:
    """Flip leftover 'pending' rows to error after a crash/restart mid-Refresh."""
    init_db()
    cutoff = time.time() - max_age_seconds
    with connect() as conn:
        cur = conn.execute(
            """
            UPDATE appliances
            SET last_status = 'error',
                last_error = COALESCE(last_error, 'Refresh interrupted — click Refresh to retry'),
                updated_at = ?
            WHERE last_status = 'pending' AND updated_at < ?
            """,
            (time.time(), cutoff),
        )
        return int(cur.rowcount or 0)


def is_appliance_offline(appliance: dict[str, Any] | None) -> bool:
    if not appliance:
        return False
    if appliance.get("last_status") == "offline":
        return True
    return int(appliance.get("fail_count") or 0) >= OFFLINE_FAIL_THRESHOLD


def ensure_offline_status(appliance_id: int) -> None:
    """Keep last_status in sync when fail_count already crossed the threshold."""
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT last_status, fail_count FROM appliances WHERE id = ?",
            (appliance_id,),
        ).fetchone()
        if not row:
            return
        if int(row["fail_count"] or 0) >= OFFLINE_FAIL_THRESHOLD and row["last_status"] != "offline":
            conn.execute(
                "UPDATE appliances SET last_status = 'offline', updated_at = ? WHERE id = ?",
                (time.time(), appliance_id),
            )


def delete_appliance(appliance_id: int) -> bool:
    """Synchronously remove an appliance (used by tests / small DBs).

    Prefer ``begin_appliance_delete`` + background purge for production UIs.
    """
    init_db()

    def _do() -> bool:
        with connect(timeout=60.0) as conn:
            conn.execute(
                """
                UPDATE appliances
                SET parent_appliance_id = NULL,
                    cluster_role = CASE WHEN cluster_role = 'member' THEN NULL ELSE cluster_role END,
                    updated_at = ?
                WHERE parent_appliance_id = ?
                """,
                (time.time(), appliance_id),
            )
            conn.execute("DELETE FROM metric_points WHERE appliance_id = ?", (appliance_id,))
            conn.execute("DELETE FROM scrape_runs WHERE appliance_id = ?", (appliance_id,))
            conn.execute("DELETE FROM cluster_peers WHERE appliance_id = ?", (appliance_id,))
            cur = conn.execute("DELETE FROM appliances WHERE id = ?", (appliance_id,))
            return cur.rowcount > 0

    return bool(_retry_locked(_do))


def begin_appliance_delete(appliance_id: int) -> dict[str, Any] | None:
    """Mark appliance for async delete: hide from UI, wipe creds, stop scraping.

    Returns a label dict for notifications, or None if not found / already gone.
    """
    init_db()
    now = time.time()

    def _do() -> dict[str, Any] | None:
        with connect() as conn:
            row = conn.execute(
                "SELECT id, host, display_name, delete_pending FROM appliances WHERE id = ?",
                (appliance_id,),
            ).fetchone()
            if not row:
                return None
            already = int(row["delete_pending"] or 0) == 1
            # Detach cluster members that pointed at this node.
            conn.execute(
                """
                UPDATE appliances
                SET parent_appliance_id = NULL,
                    cluster_role = CASE WHEN cluster_role = 'member' THEN NULL ELSE cluster_role END,
                    updated_at = ?
                WHERE parent_appliance_id = ?
                """,
                (now, appliance_id),
            )
            # Wipe secrets immediately; keep the row until history is purged.
            blank = encrypt_text("")
            conn.execute(
                """
                UPDATE appliances
                SET delete_pending = 1,
                    enabled = 0,
                    last_status = 'deleting',
                    last_error = NULL,
                    password_enc = ?,
                    jwt = NULL,
                    jwt_expires_at = NULL,
                    metrics_token = NULL,
                    ops_snapshot_json = NULL,
                    updated_at = ?
                WHERE id = ?
                """,
                (blank, now, appliance_id),
            )
            return {
                "id": int(row["id"]),
                "host": row["host"],
                "display_name": row["display_name"],
                "already_deleting": already,
            }

    return _retry_locked(_do)


def delete_metric_points_batch(appliance_id: int, batch_size: int = 2_000) -> int:
    """Delete up to ``batch_size`` history rows for one appliance. Returns rows removed.

    Uses a short busy timeout so Add/Connect are not blocked for minutes when a
    purge batch cannot get the write lock quickly.
    """
    init_db()
    last: Exception | None = None
    for i in range(4):
        try:
            conn = sqlite3.connect(str(db_path()), timeout=5.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("PRAGMA busy_timeout = 5000")
                conn.execute("PRAGMA journal_mode = WAL")
                try:
                    cur = conn.execute(
                        "DELETE FROM metric_points WHERE appliance_id = ? LIMIT ?",
                        (appliance_id, batch_size),
                    )
                except sqlite3.OperationalError as exc:
                    if "limit" not in str(exc).lower():
                        raise
                    cur = conn.execute(
                        """
                        DELETE FROM metric_points
                        WHERE rowid IN (
                            SELECT rowid FROM metric_points
                            WHERE appliance_id = ?
                            LIMIT ?
                        )
                        """,
                        (appliance_id, batch_size),
                    )
                n = int(cur.rowcount)
                conn.commit()
                return n
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except sqlite3.OperationalError as exc:
            last = exc
            msg = str(exc).lower()
            if "locked" not in msg and "busy" not in msg:
                raise
            time.sleep(0.4 * (i + 1))
    assert last is not None
    raise last


def detach_appliance_identity(appliance_id: int, label: str | None = None) -> bool:
    """Remove the appliance row immediately without cascading metric history.

    Temporarily disables foreign keys so CASCADE does not wipe millions of
    metric_points in one blocking transaction. History is purged afterward in
    chunks via ``delete_metric_points_batch``. Enqueues the id so a restart can
    resume the purge.
    """
    init_db()
    now = time.time()

    def _do() -> bool:
        with connect(timeout=60.0) as conn:
            row = conn.execute(
                "SELECT id, display_name, host FROM appliances WHERE id = ?",
                (appliance_id,),
            ).fetchone()
            name = label
            if not name and row is not None:
                name = (row["display_name"] or row["host"] or f"#{appliance_id}")
            conn.execute("PRAGMA foreign_keys=OFF")
            try:
                conn.execute("DELETE FROM scrape_runs WHERE appliance_id = ?", (appliance_id,))
                conn.execute("DELETE FROM cluster_peers WHERE appliance_id = ?", (appliance_id,))
                conn.execute("DELETE FROM healthcheck_runs WHERE appliance_id = ?", (appliance_id,))
                cur = conn.execute("DELETE FROM appliances WHERE id = ?", (appliance_id,))
                removed = cur.rowcount > 0
            finally:
                conn.execute("PRAGMA foreign_keys=ON")
            conn.execute(
                """
                INSERT INTO metric_purge_queue (appliance_id, label, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(appliance_id) DO UPDATE SET label = excluded.label
                """,
                (appliance_id, name or f"#{appliance_id}", now),
            )
            return removed or row is not None

    return bool(_retry_locked(_do))


def list_metric_purge_queue() -> list[dict[str, Any]]:
    init_db()
    with connect(timeout=15.0) as conn:
        rows = conn.execute(
            "SELECT appliance_id, label, created_at FROM metric_purge_queue ORDER BY created_at ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def clear_metric_purge_queue(appliance_id: int) -> None:
    init_db()

    def _do() -> None:
        with connect() as conn:
            conn.execute("DELETE FROM metric_purge_queue WHERE appliance_id = ?", (appliance_id,))

    _retry_locked(_do)


def finalize_appliance_delete(appliance_id: int) -> bool:
    """Remove remaining small rows / appliance identity after history purge."""
    init_db()

    def _do() -> bool:
        with connect(timeout=60.0) as conn:
            conn.execute("PRAGMA foreign_keys=OFF")
            try:
                conn.execute("DELETE FROM scrape_runs WHERE appliance_id = ?", (appliance_id,))
                conn.execute("DELETE FROM cluster_peers WHERE appliance_id = ?", (appliance_id,))
                conn.execute("DELETE FROM healthcheck_runs WHERE appliance_id = ?", (appliance_id,))
                cur = conn.execute("DELETE FROM appliances WHERE id = ?", (appliance_id,))
                removed = cur.rowcount > 0
            finally:
                conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("DELETE FROM metric_purge_queue WHERE appliance_id = ?", (appliance_id,))
            return removed

    return bool(_retry_locked(_do))


def mark_appliance_delete_failed(appliance_id: int, error: str) -> None:
    """Surface a failed background delete back in the appliance list."""
    init_db()
    now = time.time()
    msg = (error or "Background delete failed")[:2000]

    def _do() -> None:
        with connect() as conn:
            conn.execute(
                """
                UPDATE appliances
                SET delete_pending = 0,
                    enabled = 0,
                    last_status = 'delete_failed',
                    last_error = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (msg, now, appliance_id),
            )

    _retry_locked(_do)


def add_notification(
    *,
    kind: str,
    title: str,
    message: str,
    appliance_id: int | None = None,
) -> int:
    init_db()
    now = time.time()

    def _do() -> int:
        with connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO notifications (kind, title, message, appliance_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (kind, title, message, appliance_id, now),
            )
            return int(cur.lastrowid)

    return int(_retry_locked(_do))


def list_active_notifications(limit: int = 50) -> list[dict[str, Any]]:
    init_db()
    with connect(timeout=15.0) as conn:
        rows = conn.execute(
            """
            SELECT id, kind, title, message, appliance_id, created_at
            FROM notifications
            WHERE dismissed_at IS NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def dismiss_notification(notification_id: int) -> bool:
    init_db()
    now = time.time()

    def _do() -> bool:
        with connect() as conn:
            cur = conn.execute(
                "UPDATE notifications SET dismissed_at = ? WHERE id = ? AND dismissed_at IS NULL",
                (now, notification_id),
            )
            return cur.rowcount > 0

    return bool(_retry_locked(_do))


def set_appliance_enabled(appliance_id: int, enabled: bool) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE appliances SET enabled = ?, updated_at = ? WHERE id = ?",
            (1 if enabled else 0, time.time(), appliance_id),
        )


def update_appliance_display_name(appliance_id: int, display_name: str) -> dict[str, Any] | None:
    """Rename an appliance node. Empty name falls back to the host without scheme."""
    name = (display_name or "").strip()
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT host FROM appliances WHERE id = ?", (appliance_id,)).fetchone()
        if not row:
            return None
        if not name:
            host = row["host"] or ""
            name = host.replace("https://", "").replace("http://", "")
        conn.execute(
            "UPDATE appliances SET display_name = ?, updated_at = ? WHERE id = ?",
            (name, time.time(), appliance_id),
        )
    return get_appliance(appliance_id)


def update_appliance_location(appliance_id: int, location: str | None) -> dict[str, Any] | None:
    """Set or clear the optional location label for an appliance."""
    loc = (location or "").strip() or None
    init_db()
    with connect() as conn:
        cur = conn.execute(
            "UPDATE appliances SET location = ?, updated_at = ? WHERE id = ?",
            (loc, time.time(), appliance_id),
        )
        if cur.rowcount <= 0:
            return None
    return get_appliance(appliance_id)


def update_appliance_cluster_display_name(appliance_id: int, cluster_display_name: str) -> dict[str, Any] | None:
    """Rename the cluster heading for a primary appliance (does not change node display_name)."""
    name = (cluster_display_name or "").strip()
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT id, host FROM appliances WHERE id = ?", (appliance_id,)).fetchone()
        if not row:
            return None
        if not name:
            host = row["host"] or ""
            name = f"Cluster · {host.replace('https://', '').replace('http://', '')}"
        conn.execute(
            "UPDATE appliances SET cluster_display_name = ?, updated_at = ? WHERE id = ?",
            (name, time.time(), appliance_id),
        )
    return get_appliance(appliance_id)


def _sqlite_text(value: Any) -> str | None:
    """Coerce API values to SQLite-safe text (CM cluster fields are sometimes nested dicts)."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        text = str(value).strip()
        return text or None
    if isinstance(value, dict):
        for key in ("status", "state", "name", "value", "id", "node_id", "uuid", "host", "hostname"):
            nested = value.get(key)
            if isinstance(nested, (str, int, float, bool)) and str(nested).strip():
                return str(nested).strip()
        try:
            return json.dumps(value, separators=(",", ":"), sort_keys=True)[:500]
        except Exception:  # noqa: BLE001
            return str(value)[:500]
    if isinstance(value, (list, tuple)):
        try:
            return json.dumps(value, separators=(",", ":"))[:500]
        except Exception:  # noqa: BLE001
            return str(value)[:500]
    return str(value)[:500]


def replace_cluster_peers(
    appliance_id: int,
    peers: list[dict[str, Any]],
    source: str = "api",
) -> None:
    init_db()
    now = time.time()
    with connect() as conn:
        conn.execute("DELETE FROM cluster_peers WHERE appliance_id = ?", (appliance_id,))
        for peer in peers:
            host = _sqlite_text(peer.get("host") or peer.get("peer_host"))
            if not host:
                continue
            conn.execute(
                """
                INSERT OR REPLACE INTO cluster_peers
                    (appliance_id, peer_host, peer_node_id, peer_status, source, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    appliance_id,
                    host,
                    _sqlite_text(peer.get("node_id") or peer.get("peer_node_id")),
                    _sqlite_text(peer.get("status") or peer.get("peer_status")),
                    _sqlite_text(source) or "api",
                    now,
                ),
            )


def list_cluster_peers(appliance_id: int) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM cluster_peers WHERE appliance_id = ? ORDER BY peer_host",
            (appliance_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# Keep each write transaction short so chart reads are not blocked for minutes
# while a full multi‑appliance scrape flushes tens of thousands of points.
_INSERT_BATCH_SIZE = 2500
_PRUNE_BATCH_SIZE = 50_000


def insert_metric_points(
    appliance_id: int,
    points: list[tuple[str, str, dict[str, str], float, float]],
) -> None:
    """points: (fingerprint, metric_name, labels, ts, value)

    Commits in chunks so concurrent dashboard SELECTs can interleave instead of
    waiting on one giant scrape transaction.

    Does not hold the module ``_lock`` for the whole insert — that starved chart
    reads during scrapes. Run ``vacuum_db`` only with the service stopped.
    """
    if not points:
        return
    init_db()
    rows = [
        (appliance_id, fp, name, json.dumps(labels, sort_keys=True), ts, value)
        for fp, name, labels, ts, value in points
    ]
    sql = """
        INSERT INTO metric_points (appliance_id, fingerprint, metric_name, labels_json, ts, value)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    for start in range(0, len(rows), _INSERT_BATCH_SIZE):
        chunk = rows[start : start + _INSERT_BATCH_SIZE]
        last: Exception | None = None
        for i in range(8):
            try:
                with connect(timeout=30.0) as conn:
                    conn.executemany(sql, chunk)
                break
            except sqlite3.OperationalError as exc:
                last = exc
                msg = str(exc).lower()
                if "locked" not in msg and "busy" not in msg:
                    raise
                time.sleep(0.15 * (i + 1))
        else:
            assert last is not None
            raise last
        # Brief yield between chunks so WAL readers can proceed.
        if start + _INSERT_BATCH_SIZE < len(rows):
            time.sleep(0.01)


def _rows_to_series(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in rows:
        try:
            labels = json.loads(r["labels_json"])
        except (TypeError, ValueError, json.JSONDecodeError):
            labels = {}
        out.append(
            {
                "fingerprint": r["fingerprint"],
                "name": r["metric_name"],
                "labels": labels if isinstance(labels, dict) else {},
                "t": r["ts"],
                "v": r["value"],
            }
        )
    return out


def load_series(
    appliance_id: int,
    fingerprint: str | None = None,
    metric_name: str | None = None,
    since: float | None = None,
    limit: int = 5000,
    *,
    until: float | None = None,
) -> list[dict[str, Any]]:
    """Load metric history for charts.

    For short windows this is a single indexed ``ORDER BY ts DESC LIMIT`` query.
    For longer windows (``since`` older than ~2h) it reads several time slices so
    charts keep coverage across the full range instead of only the newest
    ``limit`` points (important for high-cardinality metrics).
    """
    init_db()
    now = time.time()
    effective_until = float(until) if until is not None else now
    effective_since = float(since) if since is not None else (effective_until - 3600.0)
    window = max(0.0, effective_until - effective_since)

    def _query_slice(lo: float, hi: float, slice_limit: int, conn: Any) -> list[Any]:
        clauses = ["appliance_id = ?", "ts >= ?", "ts <= ?"]
        params: list[Any] = [appliance_id, lo, hi]
        if fingerprint:
            clauses.append("fingerprint = ?")
            params.append(fingerprint)
        if metric_name:
            clauses.append("metric_name = ?")
            params.append(metric_name)
        params.append(slice_limit)
        sql = (
            f"SELECT fingerprint, metric_name, labels_json, ts, value FROM metric_points "
            f"WHERE {' AND '.join(clauses)} ORDER BY ts DESC LIMIT ?"
        )
        return list(reversed(conn.execute(sql, params).fetchall()))

    # Short windows: one fast indexed read.
    # (Do not skip stratification based on ``limit`` alone — small limits on
    # long windows still need time slices or high-cardinality metrics collapse
    # to only the newest seconds.)
    if window <= 7200:
        with connect_read() as conn:
            return _rows_to_series(_query_slice(effective_since, effective_until, limit, conn))

    # Long windows: stratified slices (oldest → newest) for even chart coverage.
    # Keep slice count modest — each slice is a separate indexed query.
    if window <= 6 * 3600:
        n_slices = 3
    elif window <= 24 * 3600:
        n_slices = 4
    else:
        n_slices = 6
    slice_limit = max(80, limit // n_slices)
    slice_width = window / n_slices
    merged: list[Any] = []
    seen: set[tuple[str, float]] = set()
    with connect_read() as conn:
        for i in range(n_slices):
            lo = effective_since + i * slice_width
            hi = effective_until if i == n_slices - 1 else (effective_since + (i + 1) * slice_width)
            for row in _query_slice(lo, hi, slice_limit, conn):
                key = (row["fingerprint"], float(row["ts"]))
                if key in seen:
                    continue
                seen.add(key)
                merged.append(row)

    merged.sort(key=lambda r: float(r["ts"]))
    if len(merged) > limit:
        # Keep evenly spaced points if slices overshot.
        step = len(merged) / limit
        merged = [merged[int(i * step)] for i in range(limit)]
    return _rows_to_series(merged)


def load_latest_samples(appliance_id: int, max_age_seconds: float = 120.0) -> list[dict[str, Any]]:
    """Return one row per fingerprint from the most recent scrape window.

    Uses ``appliances.last_scrape_at`` instead of ``MAX(ts)`` over the full
    metric_points table (which is multi‑GB and extremely slow).
    """
    init_db()
    with connect() as conn:
        meta = conn.execute(
            "SELECT last_scrape_at FROM appliances WHERE id = ?",
            (appliance_id,),
        ).fetchone()
        latest_ts: float | None = None
        if meta and meta["last_scrape_at"] is not None:
            latest_ts = float(meta["last_scrape_at"])
        if latest_ts is None:
            # Rare fallback for rows written before last_scrape_at existed.
            row = conn.execute(
                """
                SELECT ts FROM metric_points
                WHERE appliance_id = ?
                ORDER BY ts DESC
                LIMIT 1
                """,
                (appliance_id,),
            ).fetchone()
            if not row:
                return []
            latest_ts = float(row["ts"])
        # Tight window around the last scrape — not a wide max_age scan.
        lo = latest_ts - min(5.0, max_age_seconds)
        hi = latest_ts + 2.0
        rows = conn.execute(
            """
            SELECT fingerprint, metric_name, labels_json, ts, value
            FROM metric_points
            WHERE appliance_id = ? AND ts >= ? AND ts <= ?
            ORDER BY ts ASC
            """,
            (appliance_id, lo, hi),
        ).fetchall()
    # last value wins per fingerprint
    by_fp: dict[str, dict[str, Any]] = {}
    for r in rows:
        by_fp[r["fingerprint"]] = {
            "fingerprint": r["fingerprint"],
            "name": r["metric_name"],
            "labels": json.loads(r["labels_json"]),
            "t": r["ts"],
            "v": r["value"],
        }
    return list(by_fp.values())


def load_latest_gauge(appliance_id: int, metric_name: str) -> float | None:
    """Latest value for one gauge metric — cheap indexed lookup (no full hydrate)."""
    init_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT value FROM metric_points
            WHERE appliance_id = ? AND metric_name = ?
            ORDER BY ts DESC
            LIMIT 1
            """,
            (appliance_id, metric_name),
        ).fetchone()
    if not row:
        return None
    try:
        return float(row["value"])
    except (TypeError, ValueError):
        return None


def appliance_uptime_seconds(appliance_id: int) -> float | None:
    """Host uptime from latest node_* gauges without hydrating series history."""
    boot = load_latest_gauge(appliance_id, "node_boot_time_seconds")
    if boot is None:
        return None
    now = load_latest_gauge(appliance_id, "node_time_seconds")
    if now is None:
        now = time.time()
    up = float(now) - float(boot)
    return up if up >= 0 else None


def optimize_db() -> None:
    """Cheap SQLite maintenance — refresh query-planner stats after large changes.

    Safe to run while the app is live. Prefer this over ``vacuum_db`` for routine use.
    """
    init_db()

    def _do() -> None:
        with connect() as conn:
            # Bound analysis work on multi‑GB DBs so optimize stays quick.
            conn.execute("PRAGMA analysis_limit=1000")
            conn.execute("PRAGMA optimize")

    _retry_locked(_do)


def vacuum_db() -> dict[str, int]:
    """Full database rewrite to reclaim free pages after large deletes.

    Blocks writers, can take a long time on multi‑GB files, and needs roughly
    as much free disk as the current DB size. Intended for rare manual
    maintenance windows — not the scrape loop. Day-to-day use ``optimize_db``.

    Stop ``cm-metrics`` before running. Inserts intentionally do not hold the
    module write lock for long periods, so a live VACUUM can race scrapes.
    """
    init_db()
    path = db_path()
    before = int(path.stat().st_size)
    last: Exception | None = None

    def _do() -> None:
        # VACUUM must not run inside the normal commit-on-exit helper transaction.
        conn = sqlite3.connect(str(path), timeout=120.0)
        try:
            conn.execute("PRAGMA busy_timeout = 120000")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            conn.execute("VACUUM")
            conn.execute("PRAGMA analysis_limit=1000")
            conn.execute("PRAGMA optimize")
        finally:
            conn.close()

    for i in range(6):
        try:
            with _lock:
                _do()
            break
        except sqlite3.OperationalError as exc:
            last = exc
            msg = str(exc).lower()
            if "locked" not in msg and "busy" not in msg:
                raise
            time.sleep(0.5 * (i + 1))
    else:
        assert last is not None
        raise last

    after = int(path.stat().st_size)
    return {
        "before_bytes": before,
        "after_bytes": after,
        "reclaimed_bytes": before - after,
    }


def prune_old_points(keep_days: int | None = None) -> int:
    """Delete points older than retention.

    Deletes in batches so a multi‑GB history purge cannot hold a write lock for
    the entire table at once (same idea as chunked inserts).
    """
    init_db()
    days = keep_days if keep_days is not None else Config.HISTORY_KEEP_DAYS
    cutoff = time.time() - days * 86400
    batch_size = _PRUNE_BATCH_SIZE
    deleted_total = 0

    while True:
        def _do_batch() -> int:
            with connect() as conn:
                cur = conn.execute(
                    """
                    DELETE FROM metric_points
                    WHERE rowid IN (
                        SELECT rowid FROM metric_points
                        WHERE ts < ?
                        LIMIT ?
                    )
                    """,
                    (cutoff, batch_size),
                )
                return int(cur.rowcount)

        n = int(_retry_locked(_do_batch))
        deleted_total += n
        if n < batch_size:
            break
        time.sleep(0.01)

    def _do_meta() -> None:
        with connect() as conn:
            conn.execute("DELETE FROM scrape_runs WHERE started_at < ?", (cutoff,))
            conn.execute("DELETE FROM fleet_health_samples WHERE ts < ?", (cutoff,))

    try:
        _retry_locked(_do_meta)
    except sqlite3.OperationalError:
        pass

    # Always refresh planner stats after prune (even if 0 rows) — cheap, and
    # keeps indexes honest as the live working set moves forward.
    try:
        optimize_db()
    except sqlite3.OperationalError:
        # Locked / busy — scrape loop will retry prune later.
        pass
    return deleted_total


def _fleet_counts_from_rows(rows: list[Any]) -> dict[str, int]:
    online = offline = other = 0
    for row in rows:
        status = (row["last_status"] if hasattr(row, "keys") else row.get("last_status")) or ""
        if status == "ok":
            online += 1
        elif status in {"offline", "error"}:
            offline += 1
        else:
            other += 1
    return {
        "online": online,
        "offline": offline,
        "other": other,
        "total": online + offline + other,
    }


def record_fleet_health_sample(*, force: bool = False, min_interval: float = 10.0) -> dict[str, int] | None:
    """Snapshot fleet online/offline counts. Skips if a recent sample exists unless force."""
    init_db()
    now = time.time()

    def _do() -> dict[str, int] | None:
        with connect() as conn:
            if not force:
                last = conn.execute(
                    "SELECT ts FROM fleet_health_samples ORDER BY ts DESC LIMIT 1"
                ).fetchone()
                if last and (now - float(last["ts"])) < min_interval:
                    return None
            rows = conn.execute(
                """
                SELECT last_status FROM appliances
                WHERE COALESCE(delete_pending, 0) = 0
                """
            ).fetchall()
            counts = _fleet_counts_from_rows(rows)
            conn.execute(
                """
                INSERT INTO fleet_health_samples (ts, online, offline, other, total)
                VALUES (?, ?, ?, ?, ?)
                """,
                (now, counts["online"], counts["offline"], counts["other"], counts["total"]),
            )
            return counts

    return _retry_locked(_do)


def load_fleet_health_series(since: float | None = None, limit: int = 20_000) -> list[dict[str, Any]]:
    """Return fleet health samples newest-last for charting."""
    init_db()
    with connect() as conn:
        if since is not None:
            rows = conn.execute(
                """
                SELECT ts, online, offline, other, total
                FROM fleet_health_samples
                WHERE ts >= ?
                ORDER BY ts ASC
                LIMIT ?
                """,
                (since, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT ts, online, offline, other, total
                FROM fleet_health_samples
                ORDER BY ts ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [
        {
            "t": float(r["ts"]),
            "online": int(r["online"]),
            "offline": int(r["offline"]),
            "other": int(r["other"]),
            "total": int(r["total"]),
        }
        for r in rows
    ]


def appliance_count() -> int:
    init_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS c FROM appliances
            WHERE COALESCE(delete_pending, 0) = 0
            """
        ).fetchone()
    return int(row["c"]) if row else 0


def upsert_healthcheck_run(
    appliance_id: int,
    *,
    status: str,
    started_at: float | None = None,
    finished_at: float | None = None,
    overall: str | None = None,
    severity_counts: dict[str, Any] | None = None,
    error: str | None = None,
    message: str | None = None,
    html_path: str | None = None,
    json_path: str | None = None,
    analysis_path: str | None = None,
) -> None:
    init_db()
    now = time.time()
    counts_json = json.dumps(severity_counts) if severity_counts is not None else None

    def _write() -> None:
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO healthcheck_runs (
                    appliance_id, status, started_at, finished_at, overall,
                    severity_counts_json, error, message, html_path, json_path,
                    analysis_path, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(appliance_id) DO UPDATE SET
                    status = excluded.status,
                    started_at = COALESCE(excluded.started_at, healthcheck_runs.started_at),
                    finished_at = excluded.finished_at,
                    overall = excluded.overall,
                    severity_counts_json = excluded.severity_counts_json,
                    error = excluded.error,
                    message = excluded.message,
                    html_path = COALESCE(excluded.html_path, healthcheck_runs.html_path),
                    json_path = COALESCE(excluded.json_path, healthcheck_runs.json_path),
                    analysis_path = COALESCE(excluded.analysis_path, healthcheck_runs.analysis_path),
                    updated_at = excluded.updated_at
                """,
                (
                    appliance_id,
                    status,
                    started_at,
                    finished_at,
                    overall,
                    counts_json,
                    error,
                    message,
                    html_path,
                    json_path,
                    analysis_path,
                    now,
                ),
            )

    _retry_locked(_write)


def get_healthcheck_run(appliance_id: int) -> dict[str, Any] | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM healthcheck_runs WHERE appliance_id = ?",
            (appliance_id,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    raw = item.pop("severity_counts_json", None)
    try:
        item["severity_counts"] = json.loads(raw) if raw else None
    except Exception:  # noqa: BLE001
        item["severity_counts"] = None
    return item


def delete_healthcheck_run(appliance_id: int) -> None:
    init_db()

    def _write() -> None:
        with connect() as conn:
            conn.execute(
                "DELETE FROM healthcheck_runs WHERE appliance_id = ?",
                (appliance_id,),
            )

    _retry_locked(_write)
