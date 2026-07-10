"""
Standalone CRDP TLS health check helper.

Use this outside Databricks when you want to validate HTTPS/TLS connectivity
to a CRDP health endpoint such as:

    GET https://mycrdp:8443/healthz

This tool is intentionally driver/local only. It does not include Spark
executor-distributed checks.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

repo_src = Path(__file__).resolve().parents[1] / "src"
if str(repo_src) not in sys.path:
    sys.path.insert(0, str(repo_src))

from thales_databricks_integration import IntegrationConfig


def bool_value(value: bool) -> str:
    return "true" if value else "false"


def build_ssl_context(config: IntegrationConfig):
    if not config.crdp_ssl_enabled:
        return None

    if config.crdp_ssl_verify_server:
        ssl_context = ssl.create_default_context(
            cafile=config.crdp_ca_cert_path or None
        )
    else:
        ssl_context = ssl._create_unverified_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    cert_path = (config.crdp_client_cert_path or "").strip()
    key_path = (config.crdp_client_key_path or "").strip()
    if cert_path:
        ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path or None)
    return ssl_context


def resolve_tls_debug(config: IntegrationConfig) -> dict[str, object]:
    ca_path = Path(config.crdp_ca_cert_path) if config.crdp_ca_cert_path else None
    cert_path = Path(config.crdp_client_cert_path) if config.crdp_client_cert_path else None
    key_path = Path(config.crdp_client_key_path) if config.crdp_client_key_path else None

    debug = {
        "resolved_ca_cert_path": str(ca_path) if ca_path else None,
        "resolved_client_cert_path": str(cert_path) if cert_path else None,
        "resolved_client_key_path": str(key_path) if key_path else None,
        "resolved_ca_cert_exists": ca_path.exists() if ca_path else False,
        "resolved_client_cert_exists": cert_path.exists() if cert_path else False,
        "resolved_client_key_exists": key_path.exists() if key_path else False,
        "ca_bundle_load_ok": None,
        "client_cert_chain_load_ok": None,
        "ca_bundle_load_error": None,
        "client_cert_chain_load_error": None,
    }

    if config.crdp_ssl_enabled:
        try:
            if config.crdp_ssl_verify_server:
                ssl.create_default_context(cafile=config.crdp_ca_cert_path or None)
            else:
                insecure_context = ssl._create_unverified_context()
                insecure_context.check_hostname = False
                insecure_context.verify_mode = ssl.CERT_NONE
            debug["ca_bundle_load_ok"] = True
        except Exception as exc:
            debug["ca_bundle_load_ok"] = False
            debug["ca_bundle_load_error"] = repr(exc)

        try:
            if config.crdp_client_cert_path:
                context = ssl.create_default_context()
                context.load_cert_chain(
                    certfile=config.crdp_client_cert_path,
                    keyfile=config.crdp_client_key_path or None,
                )
            debug["client_cert_chain_load_ok"] = True
        except Exception as exc:
            debug["client_cert_chain_load_ok"] = False
            debug["client_cert_chain_load_error"] = repr(exc)
    else:
        debug["ca_bundle_load_ok"] = True
        debug["client_cert_chain_load_ok"] = True

    return debug


def print_tls_configuration(config: IntegrationConfig) -> None:
    print("CRDP TLS configuration from properties")
    print("CRDPIP:", config.crdp_ip)
    print("CRDPPORT:", config.crdp_port)
    print("CRDP_SSL_ENABLED:", bool_value(config.crdp_ssl_enabled))
    print("CRDP_SSL_VERIFY_SERVER:", bool_value(config.crdp_ssl_verify_server))
    print("CRDP_CA_CERT_PATH:", config.crdp_ca_cert_path)
    print("CRDP_CLIENT_CERT_PATH:", config.crdp_client_cert_path)
    print("CRDP_CLIENT_KEY_PATH:", config.crdp_client_key_path)


def fetch_health_url(url: str, timeout_seconds: int, ssl_context) -> dict[str, Any]:
    request = urllib_request.Request(url, method="GET")
    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
            body_bytes = response.read()
            body_text = body_bytes.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "url": url,
                "status_code": response.getcode(),
                "body": body_text,
                "error": None,
            }
    except urllib_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "url": url,
            "status_code": exc.code,
            "body": error_body,
            "error": repr(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "status_code": None,
            "body": None,
            "error": repr(exc),
        }


def run_driver_health_check_tls(
    url: str | None = None,
    timeout_seconds: int = 10,
    config_path: str | None = None,
) -> dict[str, Any]:
    config = IntegrationConfig.from_runtime(config_path)
    print_tls_configuration(config)
    print(json.dumps(resolve_tls_debug(config), indent=2))

    if not config.crdp_ssl_enabled:
        raise ValueError("TLS health check requires CRDP_SSL_ENABLED=true.")

    resolved_url = url or f"https://{config.crdp_ip}:{config.crdp_port}/healthz"
    ssl_context = build_ssl_context(config)
    result = fetch_health_url(resolved_url, timeout_seconds, ssl_context)
    print("CRDP TLS driver health check")
    print(json.dumps(result, indent=2))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone CRDP TLS health check.")
    parser.add_argument(
        "--url",
        default=None,
        help="CRDP TLS health endpoint URL. Defaults to https://<CRDPIP>:<CRDPPORT>/healthz from config.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=10,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--config-path",
        default=None,
        help="Optional explicit path to udfConfig.properties.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_driver_health_check_tls(
        url=args.url,
        timeout_seconds=args.timeout_seconds,
        config_path=args.config_path,
    )
