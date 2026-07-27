from __future__ import annotations

from dataclasses import dataclass, field
import base64
import time
from typing import Optional


@dataclass(slots=True)
class ClientConfig:
    base_url: str
    username: str
    password: str
    basic_auth: Optional[str] = None
    labels: list[str] = field(default_factory=lambda: ["myapp", "cli"])
    timeout_seconds: int = 60
    debug: bool = False
    insecure_tls: bool = True
    max_business_requests_per_token: int = 0
    refresh_skew_seconds_override: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.base_url or not self.username or not self.password:
            raise ValueError("base_url, username, and password are required")
        if self.timeout_seconds <= 0:
            self.timeout_seconds = 60
        if self.max_business_requests_per_token < 0:
            self.max_business_requests_per_token = 0
        if self.refresh_skew_seconds_override is not None and self.refresh_skew_seconds_override < 0:
            raise ValueError("refresh_skew_seconds_override must be >= 0")

    @staticmethod
    def encode_basic(username: Optional[str], password: Optional[str]) -> Optional[str]:
        if not username or not password:
            return None
        raw = f"{username}:{password}".encode("utf-8")
        return base64.b64encode(raw).decode("ascii")


@dataclass(slots=True)
class SessionInfo:
    jwt: str
    duration_seconds: int
    expires_at_epoch_ms: int
    refresh_skew_seconds: int

    def is_expiring_soon(self) -> bool:
        refresh_at_ms = self.expires_at_epoch_ms - (self.refresh_skew_seconds * 1000)
        return int(time.time() * 1000) >= refresh_at_ms

    def short_token(self) -> str:
        return self.jwt if len(self.jwt) <= 16 else self.jwt[:16] + "..."