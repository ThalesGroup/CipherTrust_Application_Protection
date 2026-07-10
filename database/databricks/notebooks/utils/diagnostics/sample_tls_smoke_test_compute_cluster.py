"""
Compute-cluster TLS smoke test for the packaged thales_databricks_integration wheel.

Use this from a Python-capable Databricks notebook attached to a compute
cluster where the init script has already copied the runtime configuration and
TLS materials into cluster-visible paths such as `/tmp/thales_config`.

This validates:
- runtime property loading from `udfConfig.properties`
- local TLS file presence using the paths from the properties file
- CA/client certificate resolution
- real `/v2/protectbulk` and `/v2/revealbulk` behavior over TLS
- repeated calls against the same runtime configuration

Important:
- This notebook uses the properties file settings as the source of truth.
- The cluster cannot read local workspace paths like
  `E:\\codex\\work\\thales.databricks.integration\\certs`.
- The TLS paths in `udfConfig.properties` must point to files that exist on the
  Databricks cluster at runtime.
"""

from __future__ import annotations

import os
import ssl
from pathlib import Path

from thales_databricks_integration import IntegrationConfig, protect_rows, reveal_rows


def _bool_value(value: bool) -> str:
    return "true" if value else "false"


def _print_runtime_diagnostics(config_path: Path) -> None:
    print("Python package import")
    import thales_databricks_integration  # imported here for simple path visibility

    print("package:", getattr(thales_databricks_integration, "__file__", "<unknown>"))

    print("\nRuntime config checks")
    print("config_path:", config_path)
    print("config_exists:", config_path.exists())
    print("cwd:", os.getcwd())


def _print_tls_configuration(config: IntegrationConfig) -> None:
    print("\nCRDP TLS configuration from properties")
    print("CRDPIP:", config.crdp_ip)
    print("CRDPPORT:", config.crdp_port)
    print("CRDP_API_VERSION:", config.crdp_api_version)
    print("CRDP_TRANSPORT_MODE:", config.transport_mode)
    print("CRDP_SSL_ENABLED:", _bool_value(config.crdp_ssl_enabled))
    print("CRDP_SSL_VERIFY_SERVER:", _bool_value(config.crdp_ssl_verify_server))
    print("CRDP_CA_CERT_PATH:", config.crdp_ca_cert_path)
    print("CRDP_CLIENT_CERT_PATH:", config.crdp_client_cert_path)
    print("CRDP_CLIENT_KEY_PATH:", config.crdp_client_key_path)


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


def _print_tls_resolution(config: IntegrationConfig) -> None:
    tls_debug = _resolve_tls_debug(config)
    print("\nTLS material resolution")
    interesting_keys = [
        "resolved_ca_cert_path",
        "resolved_client_cert_path",
        "resolved_client_key_path",
        "resolved_ca_cert_exists",
        "resolved_client_cert_exists",
        "resolved_client_key_exists",
        "ca_bundle_load_ok",
        "client_cert_chain_load_ok",
        "ca_bundle_load_error",
        "client_cert_chain_load_error",
    ]
    for key in interesting_keys:
        print(f"{key}: {tls_debug.get(key)}")


def run_compute_cluster_tls_smoke_test(
    spark_session,
    object_name: str = "my_catalog.my_schema.plaintext_protected_internal",
    config_path: str | None = None,
) -> None:
    if config_path:
        os.environ["UDF_CONFIG_VOLUME_PATH"] = config_path

    resolved_config = IntegrationConfig.from_runtime(config_path)
    resolved_config_path = Path(
        config_path
        or os.environ.get("UDF_CONFIG_VOLUME_PATH")
        or os.environ.get("THALES_UDF_CONFIG_PATH")
        or "/tmp/thales_config/udfConfig.properties"
    )

    _print_runtime_diagnostics(resolved_config_path)
    _print_tls_configuration(resolved_config)
    _print_tls_resolution(resolved_config)

    if not resolved_config.crdp_ssl_enabled:
        print("\nWARNING: CRDP_SSL_ENABLED is false. This is not a TLS runtime configuration.")
    if not resolved_config.should_use_real_transport():
        raise ValueError(
            "TLS smoke test requires real transport. Update udfConfig.properties so the "
            "runtime resolves to a real CRDP endpoint."
        )

    plaintext_rows = [
        {"email": "alice@example.com"},
        {"email": "bob@example.com"},
        {"email": "carol@example.com"},
    ]

    protected_result = protect_rows(
        rows=plaintext_rows,
        object_name=object_name,
        sensitive_columns=["email"],
        config=resolved_config,
    )

    protected_values = [row["email"] for row in protected_result.rows]

    print("\nProtect request summary:")
    print(
        {
            "request_count": protected_result.request_count,
            "transformed_value_count": protected_result.transformed_value_count,
            "requests": protected_result.requests,
        }
    )

    print("\nProtected values:")
    for value in protected_values:
        print(value)

    revealed_result = reveal_rows(
        rows=protected_result.rows,
        object_name=object_name,
        sensitive_columns=["email"],
        config=resolved_config,
    )

    revealed_values = [row["email"] for row in revealed_result.rows]
    expected_values = [row["email"] for row in plaintext_rows]

    print("\nReveal request summary:")
    print(
        {
            "request_count": revealed_result.request_count,
            "transformed_value_count": revealed_result.transformed_value_count,
            "requests": revealed_result.requests,
        }
    )

    print("\nRevealed values:")
    for value in revealed_values:
        print(value)

    print("\nReveal matches original:", revealed_values == expected_values)

    if revealed_values != expected_values:
        raise ValueError(
            "TLS smoke test reveal values did not match the original plaintext values. "
            f"Expected={expected_values}, Actual={revealed_values}"
        )

    print("\nRepeated-call sanity check")
    for index in range(3):
        repeated_result = protect_rows(
            rows=[
                {"email": "repeat1@example.com"},
                {"email": "repeat2@example.com"},
            ],
            object_name=object_name,
            sensitive_columns=["email"],
            config=resolved_config,
        )
        print(f"Run {index + 1} complete: {[row['email'] for row in repeated_result.rows]}")

    print("\nTHALES_COMPUTE_CLUSTER_TLS_SMOKE_TEST_FINISHED")


# Example notebook usage:
#
# from diagnostics.sample_tls_smoke_test_compute_cluster import run_compute_cluster_tls_smoke_test
# run_compute_cluster_tls_smoke_test(spark)

print(
    "sample_tls_smoke_test_compute_cluster.py loaded. "
    "Run run_compute_cluster_tls_smoke_test(spark) to execute the compute-cluster TLS smoke test."
)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError:
        print(
            "No active Spark session variable named 'spark' was found. "
            "Run run_compute_cluster_tls_smoke_test(spark) from a Databricks Python notebook."
        )
    else:
        run_compute_cluster_tls_smoke_test(spark_session)
