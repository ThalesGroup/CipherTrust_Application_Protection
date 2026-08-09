"""Application configuration."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _ensure_secret() -> str:
    key = os.getenv("SECRET_KEY", "").strip()
    if key:
        return key
    # Persist a generated key into .env so encrypted passwords survive restarts.
    env_path = ROOT / ".env"
    key = secrets.token_urlsafe(48)
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    # Only treat an active (non-comment) SECRET_KEY= line as present.
    has_active = any(
        line.strip().startswith("SECRET_KEY=") and not line.strip().startswith("#")
        for line in existing.splitlines()
    )
    if not has_active:
        with env_path.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(f"SECRET_KEY={key}\n")
    os.environ["SECRET_KEY"] = key
    return key


class Config:
    SECRET_KEY: str = _ensure_secret()
    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", str(ROOT / "data" / "cm_metrics.db")))
    # TLS verification is always disabled per product requirement for CM connections.
    CM_VERIFY_TLS: bool = False
    SCRAPE_INTERVAL: int = int(os.getenv("SCRAPE_INTERVAL", "60"))
    # REST ops snapshot (users/backups/scheduler) — slower than Prometheus scrapes.
    OPS_SNAPSHOT_INTERVAL: int = int(os.getenv("OPS_SNAPSHOT_INTERVAL", "120"))
    # Keep enough in-memory history for the UI time-range picker (up to 30d).
    HISTORY_SECONDS: int = int(os.getenv("HISTORY_SECONDS", "2592000"))  # 30d default
    HISTORY_KEEP_DAYS: int = int(os.getenv("HISTORY_KEEP_DAYS", "30"))
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5050"))
    FLASK_DEBUG: bool = _bool(os.getenv("FLASK_DEBUG", "true"), True)
    # HTTPS is on by default; self-signed cert/key are created on first start if missing.
    FLASK_HTTPS: bool = _bool(os.getenv("FLASK_HTTPS", "true"), True)
    # Plain HTTP alongside HTTPS (no redirect). Off by default for local; enable on Ubuntu.
    FLASK_HTTP: bool = _bool(os.getenv("FLASK_HTTP", "false"), False)
    FLASK_HTTP_PORT: int = int(os.getenv("FLASK_HTTP_PORT", "80"))
    SSL_CERT_PATH: Path = Path(
        os.getenv("SSL_CERT_PATH", str(ROOT / "data" / "certs" / "cert.pem"))
    )
    SSL_KEY_PATH: Path = Path(
        os.getenv("SSL_KEY_PATH", str(ROOT / "data" / "certs" / "key.pem"))
    )
    DEMO_MODE: bool = _bool(os.getenv("DEMO_MODE", "false"), False)
    JWT_REFRESH_SECONDS: int = int(os.getenv("JWT_REFRESH_SECONDS", "240"))  # CM JWT ~300s
