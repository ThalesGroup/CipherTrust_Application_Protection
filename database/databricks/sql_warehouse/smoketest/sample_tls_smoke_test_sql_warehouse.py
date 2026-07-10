"""
SQL Warehouse-style TLS smoke test for the current thales_databricks_integration package.

Use this from a Python-capable Databricks runtime or a local Python session when
you want to validate the same base64-embedded TLS material model used by the SQL
Warehouse embedded-config deployment path.

This validates:
- explicit properties-override usage
- base64 TLS material presence
- temp-file materialization for CA / client cert / client key
- CA/cert/key loadability via Python ssl
- real protectbulk/revealbulk behavior through the current row-based API
- repeated calls against the same resolved runtime configuration

Notes:
- the `spark_session` argument is accepted for notebook-call compatibility but is
  not required by this smoke test
- this sample now targets the current `thales_databricks_integration` package,
  not the older `thales_databricks_udf` layout
"""

from __future__ import annotations

import base64
import os
import ssl
import sys
import tempfile
from pathlib import Path

repo_src = Path(__file__).resolve().parents[2] / "src"
if str(repo_src) not in sys.path:
    sys.path.insert(0, str(repo_src))

from thales_databricks_integration import IntegrationConfig, protect_rows, reveal_rows


def _bool_value(value: bool) -> str:
    return "true" if value else "false"


def _require_sql_warehouse_tls_properties(properties_override: dict[str, str]) -> None:
    required_keys = [
        "CRDPIP",
        "CRDPPORT",
        "CRDP_SSL_ENABLED",
        "CRDP_SSL_VERIFY_SERVER",
    ]
    missing = [key for key in required_keys if not properties_override.get(key)]
    if missing:
        raise ValueError(
            "SQL Warehouse TLS smoke test requires CRDP host/port/TLS keys. "
            f"Missing keys: {missing}"
        )

    has_b64_bundle = all(
        properties_override.get(key)
        for key in [
            "CRDP_CA_CERT_PEM_B64",
            "CRDP_CLIENT_CERT_PEM_B64",
            "CRDP_CLIENT_KEY_PEM_B64",
        ]
    )
    has_path_bundle = all(
        properties_override.get(key)
        for key in [
            "CRDP_CA_CERT_PATH",
            "CRDP_CLIENT_CERT_PATH",
            "CRDP_CLIENT_KEY_PATH",
        ]
    )
    if not has_b64_bundle and not has_path_bundle:
        raise ValueError(
            "SQL Warehouse TLS smoke test requires either embedded base64 TLS properties or direct TLS file paths."
        )


def _materialize_embedded_tls_files(properties_override: dict[str, str]) -> tuple[dict[str, str], str | None]:
    resolved = dict(properties_override)
    temp_dir = None

    if all(
        resolved.get(key)
        for key in [
            "CRDP_CA_CERT_PEM_B64",
            "CRDP_CLIENT_CERT_PEM_B64",
            "CRDP_CLIENT_KEY_PEM_B64",
        ]
    ):
        temp_dir = tempfile.mkdtemp(prefix="thales_sql_wh_tls_")
        file_specs = [
            ("CRDP_CA_CERT_PEM_B64", "CRDP_CA_CERT_PATH", "crdp-ca.pem"),
            ("CRDP_CLIENT_CERT_PEM_B64", "CRDP_CLIENT_CERT_PATH", "crdp-client-cert.pem"),
            ("CRDP_CLIENT_KEY_PEM_B64", "CRDP_CLIENT_KEY_PATH", "crdp-client-key.pem"),
        ]
        for source_key, target_key, file_name in file_specs:
            target_path = Path(temp_dir) / file_name
            target_path.write_bytes(base64.b64decode(resolved[source_key]))
            resolved[target_key] = str(target_path)

    return resolved, temp_dir



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
        "resolved_ca_cert_size": ca_path.stat().st_size if ca_path and ca_path.exists() else None,
        "resolved_client_cert_size": cert_path.stat().st_size if cert_path and cert_path.exists() else None,
        "resolved_client_key_size": key_path.stat().st_size if key_path and key_path.exists() else None,
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



def _print_runtime_diagnostics() -> None:
    print("Python package import")
    import thales_databricks_integration

    print("package:", getattr(thales_databricks_integration, "__file__", "<unknown>"))
    print("cwd:", os.getcwd())



def _print_tls_configuration(props: dict[str, str], config: IntegrationConfig, temp_dir: str | None) -> None:
    print("\nCRDP TLS configuration")
    print("CRDPIP:", props.get("CRDPIP"))
    print("CRDPPORT:", props.get("CRDPPORT"))
    print("CRDP_SSL_ENABLED:", props.get("CRDP_SSL_ENABLED"))
    print("CRDP_SSL_VERIFY_SERVER:", props.get("CRDP_SSL_VERIFY_SERVER"))
    print("Has CRDP_CA_CERT_PEM_B64:", bool(props.get("CRDP_CA_CERT_PEM_B64")))
    print("Has CRDP_CLIENT_CERT_PEM_B64:", bool(props.get("CRDP_CLIENT_CERT_PEM_B64")))
    print("Has CRDP_CLIENT_KEY_PEM_B64:", bool(props.get("CRDP_CLIENT_KEY_PEM_B64")))
    print("Resolved CRDP_CA_CERT_PATH:", config.crdp_ca_cert_path)
    print("Resolved CRDP_CLIENT_CERT_PATH:", config.crdp_client_cert_path)
    print("Resolved CRDP_CLIENT_KEY_PATH:", config.crdp_client_key_path)
    print("Materialized temp dir:", temp_dir)
    print("Transport mode:", config.transport_mode)
    print("API version:", config.crdp_api_version)
    print("Verify server:", _bool_value(config.crdp_ssl_verify_server))



def _print_tls_resolution(config: IntegrationConfig) -> None:
    tls_debug = _resolve_tls_debug(config)
    print("\nTLS material resolution")
    for key in [
        "resolved_ca_cert_path",
        "resolved_client_cert_path",
        "resolved_client_key_path",
        "resolved_ca_cert_exists",
        "resolved_client_cert_exists",
        "resolved_client_key_exists",
        "resolved_ca_cert_size",
        "resolved_client_cert_size",
        "resolved_client_key_size",
        "ca_bundle_load_ok",
        "client_cert_chain_load_ok",
        "ca_bundle_load_error",
        "client_cert_chain_load_error",
    ]:
        print(f"{key}: {tls_debug.get(key)}")



def run_sql_warehouse_tls_smoke_test(
    spark_session=None,
    properties_override: dict[str, str] | None = None,
    object_name: str = "my_catalog.my_schema.plaintext_protected_internal",
    reveal_user: str = "admin",
) -> None:
    del spark_session

    if properties_override is None:
        raise ValueError("properties_override is required.")

    _require_sql_warehouse_tls_properties(properties_override)
    resolved_properties, temp_dir = _materialize_embedded_tls_files(properties_override)
    resolved_properties.setdefault("CRDP_TRANSPORT_MODE", "real")
    config = IntegrationConfig.from_dict(resolved_properties)

    _print_runtime_diagnostics()
    _print_tls_configuration(properties_override, config, temp_dir)
    _print_tls_resolution(config)

    if not config.crdp_ssl_enabled:
        print("\nWARNING: CRDP_SSL_ENABLED is false. This is not a TLS runtime configuration.")
    if not config.should_use_real_transport():
        raise ValueError(
            "SQL Warehouse TLS smoke test requires real transport. Update the supplied properties so the runtime resolves to a real CRDP endpoint."
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
        config=config,
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
        config=config,
        reveal_user=reveal_user,
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
            "SQL Warehouse TLS smoke test reveal values did not match the original plaintext values. "
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
            config=config,
        )
        print(f"Run {index + 1} complete: {[row['email'] for row in repeated_result.rows]}")

    print("\nTHALES_SQL_WAREHOUSE_TLS_SMOKE_TEST_FINISHED")


# Example notebook usage:
#
# from sample_tls_smoke_test_sql_warehouse import run_sql_warehouse_tls_smoke_test
# run_sql_warehouse_tls_smoke_test(
#     properties_override={
#         "CRDPIP": "your-crdp-ip",
#         "CRDPPORT": "8091",
#         "CRDP_SSL_ENABLED": "true",
#         "CRDP_SSL_VERIFY_SERVER": "true",
#         "CRDP_CA_CERT_PEM_B64": "<base64-ca-cert>",
#         "CRDP_CLIENT_CERT_PEM_B64": "<base64-client-cert>",
#         "CRDP_CLIENT_KEY_PEM_B64": "<base64-client-key>",
#         "CRDP_API_VERSION": "v2",
#         "CRDP_TRANSPORT_MODE": "real",
#         "COLUMN_PROFILES": "email|tag.char.internal",
#         "TAG.char.internal": "char-internal",
#         "TAG.char.internal.policyType": "internal",
#     },
#     object_name="my_catalog.my_schema.plaintext_protected_internal",
#     reveal_user="admin",
# )
