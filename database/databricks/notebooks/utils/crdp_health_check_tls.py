"""
Compute-cluster CRDP TLS health check helpers.

Use this from a Databricks Python notebook attached to a compute cluster when
you want to validate HTTPS/TLS connectivity to a CRDP health endpoint such as:

    GET https://mycrdp:8443/healthz

This script supports two scopes:

- driver-side notebook check
- executor-side distributed Spark check

It uses `udfConfig.properties` as the source of truth for:

- CRDP_SSL_ENABLED
- CRDP_SSL_VERIFY_SERVER
- CRDP_CA_CERT_PATH
- CRDP_CLIENT_CERT_PATH
- CRDP_CLIENT_KEY_PATH
"""

from __future__ import annotations

import json
import os
import ssl
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from thales_databricks_integration import IntegrationConfig


def _bool_value(value: bool) -> str:
    return "true" if value else "false"


def _build_ssl_context(config: IntegrationConfig):
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


def _resolve_tls_debug(config: IntegrationConfig) -> dict[str, object]:
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


def _print_tls_configuration(config: IntegrationConfig) -> None:
    print("CRDP TLS configuration from properties")
    print("CRDPIP:", config.crdp_ip)
    print("CRDPPORT:", config.crdp_port)
    print("CRDP_SSL_ENABLED:", _bool_value(config.crdp_ssl_enabled))
    print("CRDP_SSL_VERIFY_SERVER:", _bool_value(config.crdp_ssl_verify_server))
    print("CRDP_CA_CERT_PATH:", config.crdp_ca_cert_path)
    print("CRDP_CLIENT_CERT_PATH:", config.crdp_client_cert_path)
    print("CRDP_CLIENT_KEY_PATH:", config.crdp_client_key_path)


def _fetch_health_url(url: str, timeout_seconds: int, ssl_context) -> dict[str, Any]:
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
    """
    Run the TLS health check from the notebook driver only.
    """

    if config_path:
        os.environ["UDF_CONFIG_VOLUME_PATH"] = config_path

    config = IntegrationConfig.from_runtime(config_path)
    _print_tls_configuration(config)
    print(json.dumps(_resolve_tls_debug(config), indent=2))

    if not config.crdp_ssl_enabled:
        raise ValueError("TLS health check requires CRDP_SSL_ENABLED=true.")

    resolved_url = url or f"https://{config.crdp_ip}:{config.crdp_port}/healthz"
    ssl_context = _build_ssl_context(config)
    result = _fetch_health_url(resolved_url, timeout_seconds, ssl_context)
    print("CRDP TLS driver health check")
    print(json.dumps(result, indent=2))
    return result


def run_executor_health_check_tls(
    spark_session,
    url: str | None = None,
    timeout_seconds: int = 10,
    partitions: int = 4,
    config_path: str | None = None,
) -> list[dict[str, Any]]:
    """
    Run the TLS health check from Spark executors using mapPartitions.
    """

    resolved_config_path = (
        config_path
        or os.environ.get("UDF_CONFIG_VOLUME_PATH")
        or os.environ.get("THALES_UDF_CONFIG_PATH")
        or "/tmp/thales_config/udfConfig.properties"
    )

    config = IntegrationConfig.from_runtime(resolved_config_path)
    if not config.crdp_ssl_enabled:
        raise ValueError("TLS executor health check requires CRDP_SSL_ENABLED=true.")

    resolved_url = url or f"https://{config.crdp_ip}:{config.crdp_port}/healthz"
    sc = spark_session.sparkContext

    def check_partition(_):
        import json as _json
        import os as _os
        import ssl as _ssl
        from urllib import error as _urllib_error
        from urllib import request as _urllib_request

        from thales_databricks_integration import IntegrationConfig as _IntegrationConfig

        executor_config = _IntegrationConfig.from_runtime(resolved_config_path)
        if executor_config.crdp_ssl_verify_server:
            ssl_context = _ssl.create_default_context(
                cafile=executor_config.crdp_ca_cert_path or None
            )
        else:
            ssl_context = _ssl._create_unverified_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = _ssl.CERT_NONE

        cert_path = (executor_config.crdp_client_cert_path or "").strip()
        key_path = (executor_config.crdp_client_key_path or "").strip()
        if cert_path:
            ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path or None)

        request = _urllib_request.Request(resolved_url, method="GET")
        host_name = _os.environ.get("SPARK_LOCAL_HOSTNAME") or _os.environ.get("HOSTNAME")
        try:
            with _urllib_request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
                payload = {
                    "ok": True,
                    "url": resolved_url,
                    "status_code": response.getcode(),
                    "body": response.read().decode("utf-8", errors="replace"),
                    "error": None,
                    "executor_host": host_name,
                }
        except _urllib_error.HTTPError as exc:
            payload = {
                "ok": False,
                "url": resolved_url,
                "status_code": exc.code,
                "body": exc.read().decode("utf-8", errors="replace"),
                "error": repr(exc),
                "executor_host": host_name,
            }
        except Exception as exc:
            payload = {
                "ok": False,
                "url": resolved_url,
                "status_code": None,
                "body": None,
                "error": repr(exc),
                "executor_host": host_name,
            }
        return [_json.dumps(payload)]

    raw_results = sc.parallelize(range(partitions), partitions).mapPartitions(check_partition).collect()
    parsed_results = [json.loads(item) for item in raw_results]

    print("CRDP TLS executor health check")
    for item in parsed_results:
        print(json.dumps(item, indent=2))
    return parsed_results


print(
    "crdp_health_check_tls.py loaded. "
    "Run run_driver_health_check_tls(...) or run_executor_health_check_tls(spark, ...)."
)


# COMMAND ----------

try:
    spark_session = spark  # type: ignore[name-defined]
except NameError:
    print(
        "No active Spark session variable named 'spark' was found. "
        "Run this from a Databricks Python notebook or call the functions manually."
    )
else:
    run_driver_health_check_tls("https://mycrdp:8443/healthz")

# COMMAND ----------

try:
    spark_session = spark  # type: ignore[name-defined]
except NameError:
    print(
        "No active Spark session variable named 'spark' was found. "
        "Run this from a Databricks Python notebook or call the functions manually."
    )
else:
    run_executor_health_check_tls(
        spark_session,
        "https://mycrdp:8443/healthz",
        partitions=4,
    )
