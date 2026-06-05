"""
SQL Warehouse-style TLS smoke test for the packaged Python CRDP helpers.

Use this from a Python-capable Databricks runtime when you want to validate the
same base64-embedded TLS material model used by the SQL Warehouse deployment
path.

This validates:
- explicit properties override usage
- base64 TLS material presence
- temp-file materialization
- CA/cert/key loadability
- protectbulk/revealbulk behavior
- repeated calls against the same shared Python HTTP session
"""

import sys
from pathlib import Path


def _import_crdp_helpers():
    try:
        import thales_databricks_udf  # type: ignore
        from thales_databricks_udf.crdp_udfs import (  # type: ignore
            debug_tls_materials,
            thales_crdp_python_function_bulk_secure,
        )
        return (
            thales_databricks_udf,
            sys.modules["thales_databricks_udf.crdp_udfs"],
            debug_tls_materials,
            thales_crdp_python_function_bulk_secure,
        )
    except ModuleNotFoundError as first_error:
        current_file = Path(__file__).resolve() if "__file__" in globals() else None
        candidate_python_dir = None if current_file is None else current_file.parents[2] / "python"
        if candidate_python_dir is not None and candidate_python_dir.exists():
            sys.path.insert(0, str(candidate_python_dir))
            try:
                import thales_databricks_udf  # type: ignore
                from thales_databricks_udf.crdp_udfs import (  # type: ignore
                    debug_tls_materials,
                    thales_crdp_python_function_bulk_secure,
                )
                return (
                    thales_databricks_udf,
                    sys.modules["thales_databricks_udf.crdp_udfs"],
                    debug_tls_materials,
                    thales_crdp_python_function_bulk_secure,
                )
            except ModuleNotFoundError:
                pass

        raise ModuleNotFoundError(
            "Unable to import thales_databricks_udf. Install the built wheel before running the SQL Warehouse TLS smoke test."
        ) from first_error


(
    thales_databricks_udf_package,
    thales_databricks_udf_module,
    debug_tls_materials,
    thales_crdp_python_function_bulk_secure,
) = _import_crdp_helpers()


def _print_runtime_diagnostics():
    print("Python package import")
    print("package:", getattr(thales_databricks_udf_package, "__file__", "<unknown>"))
    print("module:", getattr(thales_databricks_udf_module, "__file__", "<unknown>"))


def _require_sql_warehouse_tls_properties(properties_override):
    required_keys = [
        "CRDPIP",
        "CRDPPORT",
        "CRDP_SSL_ENABLED",
        "CRDP_SSL_VERIFY_SERVER",
        "CRDP_CA_CERT_PEM_B64",
        "CRDP_CLIENT_CERT_PEM_B64",
        "CRDP_CLIENT_KEY_PEM_B64",
    ]
    missing = [key for key in required_keys if not properties_override.get(key)]
    if missing:
        raise ValueError(
            "SQL Warehouse TLS smoke test requires base64 TLS properties. "
            f"Missing keys: {missing}"
        )


def _print_tls_configuration(props):
    print("\nCRDP TLS configuration")
    print("CRDPIP:", props.get("CRDPIP"))
    print("CRDPPORT:", props.get("CRDPPORT"))
    print("CRDP_SSL_ENABLED:", props.get("CRDP_SSL_ENABLED"))
    print("CRDP_SSL_VERIFY_SERVER:", props.get("CRDP_SSL_VERIFY_SERVER"))
    print("Has CRDP_CA_CERT_PEM_B64:", bool(props.get("CRDP_CA_CERT_PEM_B64")))
    print("Has CRDP_CLIENT_CERT_PEM_B64:", bool(props.get("CRDP_CLIENT_CERT_PEM_B64")))
    print("Has CRDP_CLIENT_KEY_PEM_B64:", bool(props.get("CRDP_CLIENT_KEY_PEM_B64")))


def _print_tls_resolution(props):
    tls_debug = debug_tls_materials(props)
    print("\nTLS material resolution")
    interesting_keys = [
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
    ]
    for key in interesting_keys:
        print(f"{key}: {tls_debug.get(key)}")


def run_sql_warehouse_tls_smoke_test(spark_session, properties_override):
    _require_sql_warehouse_tls_properties(properties_override)
    _print_runtime_diagnostics()
    _print_tls_configuration(properties_override)
    _print_tls_resolution(properties_override)

    plaintext_values = [
        "alice@example.com",
        "bob@example.com",
        "carol@example.com",
    ]

    protected_values = thales_crdp_python_function_bulk_secure(
        plaintext_values,
        "protectbulk",
        "char",
        "email",
        properties=properties_override,
        spark_session=spark_session,
    )

    print("\nProtected values:")
    for value in protected_values:
        print(value)

    revealed_values = thales_crdp_python_function_bulk_secure(
        protected_values,
        "revealbulk",
        "char",
        "email",
        properties=properties_override,
        spark_session=spark_session,
    )

    print("\nRevealed values:")
    for value in revealed_values:
        print(value)

    print("\nReveal matches original:", revealed_values == plaintext_values)

    if revealed_values != plaintext_values:
        raise ValueError(
            "SQL Warehouse TLS smoke test reveal values did not match the original plaintext values. "
            f"Expected={plaintext_values}, Actual={revealed_values}"
        )

    print("\nRepeated-call sanity check")
    for index in range(3):
        results = thales_crdp_python_function_bulk_secure(
            ["repeat1@example.com", "repeat2@example.com"],
            "protectbulk",
            "char",
            "email",
            properties=properties_override,
            spark_session=spark_session,
        )
        print(f"Run {index + 1} complete: {results}")

    print("\nTHALES_SQL_WAREHOUSE_TLS_SMOKE_TEST_FINISHED")


# Example notebook usage:
#
# from sample_tls_smoke_test_sql_warehouse import run_sql_warehouse_tls_smoke_test
# run_sql_warehouse_tls_smoke_test(
#     spark,
#     {
#         "CRDPIP": "your-crdp-ip",
#         "CRDPPORT": "8091",
#         "CRDP_SSL_ENABLED": "true",
#         "CRDP_SSL_VERIFY_SERVER": "true",
#         "CRDP_CA_CERT_PEM_B64": "<base64-ca-cert>",
#         "CRDP_CLIENT_CERT_PEM_B64": "<base64-client-cert>",
#         "CRDP_CLIENT_KEY_PEM_B64": "<base64-client-key>",
#     },
# )
