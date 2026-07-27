from __future__ import annotations

import json
import threading
import time
from typing import Any, Optional

import requests
import urllib3

from .models import ClientConfig, SessionInfo


class CipherTrustRestSupport:
    @staticmethod
    def build_http_session(config: ClientConfig) -> requests.Session:
        session = requests.Session()
        session.verify = not config.insecure_tls
        session.headers.update({"Accept": "application/json"})
        if config.insecure_tls:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return session

    @staticmethod
    def authenticate(session: requests.Session, config: ClientConfig) -> SessionInfo:
        url = CipherTrustRestSupport._trim_trailing_slash(config.base_url) + "/api/v1/auth/tokens"
        payload = {
            "grant_type": "password",
            "username": config.username,
            "password": config.password,
            "refresh_token_lifetime": 20,
            "refresh_token_revoke_unused_in": 10,
            "labels": config.labels,
        }
        headers = {"Content-Type": "application/json"}
        if config.basic_auth:
            headers["Authorization"] = f"Basic {config.basic_auth}"
        CipherTrustRestSupport._debug(config, f"Authenticating to /api/v1/auth/tokens{' with Basic header.' if config.basic_auth else ' without Basic header.'}")
        response = session.post(url, headers=headers, json=payload, timeout=config.timeout_seconds)
        CipherTrustRestSupport.ensure_success(response, "authenticate")
        body = response.json()
        jwt = body.get("jwt")
        if not jwt:
            raise RuntimeError(f"Unable to locate jwt in response: {response.text}")
        duration = int(body.get("duration", 300))
        skew_seconds = config.refresh_skew_seconds_override
        if skew_seconds is None:
            skew_seconds = min(30, max(5, duration // 10))
        session_info = SessionInfo(
            jwt=jwt,
            duration_seconds=duration,
            expires_at_epoch_ms=int(time.time() * 1000) + (duration * 1000),
            refresh_skew_seconds=skew_seconds,
        )
        CipherTrustRestSupport._debug(config, f"Received token {session_info.short_token()} with duration={duration} seconds and refreshSkewSeconds={skew_seconds}.")
        return session_info

    @staticmethod
    def send_authenticated_json_post(
        session: requests.Session,
        auth_provider: "AuthTokenProvider",
        config: ClientConfig,
        path: str,
        json_body: dict[str, Any],
    ) -> requests.Response:
        token = auth_provider.get_valid_session()
        CipherTrustRestSupport._debug(config, f"POST {path} using token {token.short_token()}")
        response = CipherTrustRestSupport._send_authenticated_json_post_once(session, token.jwt, config, path, json_body)
        if response.status_code == 401 or CipherTrustRestSupport._token_looks_expired(response.text):
            CipherTrustRestSupport._debug(config, f"Received auth-expiry style response for {path}. Refreshing and retrying once.")
            refreshed = auth_provider.force_refresh()
            CipherTrustRestSupport._debug(config, f"Retrying POST {path} using token {refreshed.short_token()}")
            response = CipherTrustRestSupport._send_authenticated_json_post_once(session, refreshed.jwt, config, path, json_body)
        auth_provider.record_business_request_use(path)
        return response

    @staticmethod
    def ensure_success(response: requests.Response, action: str) -> None:
        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(f"Unable to {action}. HTTP {response.status_code}: {response.text}")

    @staticmethod
    def _send_authenticated_json_post_once(
        session: requests.Session,
        jwt: str,
        config: ClientConfig,
        path: str,
        json_body: dict[str, Any],
    ) -> requests.Response:
        url = CipherTrustRestSupport._trim_trailing_slash(config.base_url) + path
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt}",
        }
        return session.post(url, headers=headers, json=json_body, timeout=config.timeout_seconds)

    @staticmethod
    def _token_looks_expired(body: Optional[str]) -> bool:
        lower = (body or "").lower()
        return "token expired" in lower or "jwt expired" in lower or "expired token" in lower

    @staticmethod
    def _trim_trailing_slash(value: str) -> str:
        return value[:-1] if value.endswith("/") else value

    @staticmethod
    def _debug(config: ClientConfig, message: str) -> None:
        if config.debug:
            print(f"[CipherTrustRestSupport] {message}")


class AuthTokenProvider:
    def __init__(self, session: requests.Session, config: ClientConfig) -> None:
        self._session = session
        self._config = config
        self._current_session: Optional[SessionInfo] = None
        self._business_requests_on_current_token = 0
        self._lock = threading.Lock()

    def get_valid_session(self) -> SessionInfo:
        with self._lock:
            if self._current_session is None:
                CipherTrustRestSupport._debug(self._config, "No token cached yet. Authenticating.")
                self._current_session = CipherTrustRestSupport.authenticate(self._session, self._config)
                self._business_requests_on_current_token = 0
                return self._current_session
            if (
                self._config.max_business_requests_per_token > 0
                and self._business_requests_on_current_token >= self._config.max_business_requests_per_token
            ):
                CipherTrustRestSupport._debug(
                    self._config,
                    f"Refreshing token because maxBusinessRequestsPerToken={self._config.max_business_requests_per_token} was reached.",
                )
                self._current_session = CipherTrustRestSupport.authenticate(self._session, self._config)
                self._business_requests_on_current_token = 0
                return self._current_session
            if self._current_session.is_expiring_soon():
                CipherTrustRestSupport._debug(self._config, "Refreshing token proactively because it is nearing expiry.")
                self._current_session = CipherTrustRestSupport.authenticate(self._session, self._config)
                self._business_requests_on_current_token = 0
            return self._current_session

    def force_refresh(self) -> SessionInfo:
        with self._lock:
            CipherTrustRestSupport._debug(self._config, "Refreshing token reactively after auth failure or expiry response.")
            self._current_session = CipherTrustRestSupport.authenticate(self._session, self._config)
            self._business_requests_on_current_token = 0
            return self._current_session

    def record_business_request_use(self, path: str) -> None:
        with self._lock:
            self._business_requests_on_current_token += 1
            CipherTrustRestSupport._debug(
                self._config,
                f"Recorded authenticated business request to {path}. Requests on current token={self._business_requests_on_current_token}.",
            )