"""
Compute-cluster TLS smoke test for the packaged Python CRDP helpers.

Use this from a Python-capable Databricks notebook attached to a compute
cluster where the init script has already copied TLS materials into
`/tmp/thales_config`.

This validates:
- runtime property loading from `udfConfig.properties`
- local TLS file presence
- CA/cert/key resolution
- protectbulk/revealbulk behavior
- repeated calls against the same shared Python HTTP session
"""

import os
import sys
from pathlib import Path


def _import_crdp_helpers():
    try:
        import thales_databricks_udf  # type: ignore
        from thales_databricks_udf.crdp_udfs import (  # type: ignore
            debug_tls_materials,
            get_default_properties,
            thales_crdp_python_function_bulk_secure,
        )
        return (
            thales_databricks_udf,
            sys.modules["thales_databricks_udf.crdp_udfs"],
            debug_tls_materials,
            get_default_properties,
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
                    get_default_properties,
                    thales_crdp_python_function_bulk_secure,
                )
                return (
                    thales_databricks_udf,
                    sys.modules["thales_databricks_udf.crdp_udfs"],
                    debug_tls_materials,
                    get_default_properties,
                    thales_crdp_python_function_bulk_secure,
                )
            except ModuleNotFoundError:
                pass

        raise ModuleNotFoundError(
            "Unable to import thales_databricks_udf. Install the built wheel on the cluster "
            "or make the repo's python/ directory available on sys.path before running the TLS smoke test."
        ) from first_error


(
    thales_databricks_udf_package,
    thales_databricks_udf_module,
    debug_tls_materials,
    get_default_properties,
    thales_crdp_python_function_bulk_secure,
) = _import_crdp_helpers()


def _print_runtime_diagnostics(config_path):
    print("Python package import")
    print("package:", getattr(thales_databricks_udf_package, "__file__", "<unknown>"))
    print("module:", getattr(thales_databricks_udf_module, "__file__", "<unknown>"))

    print("\nLocal TLS file checks")
    for path in [
        config_path,
        "/tmp/thales_config/crdp-ca.pem",
        "/tmp/thales_config/databricks-crdp-client-cert.pem",
        "/tmp/thales_config/databricks-crdp-client-key.pem",
    ]:
        print(path, os.path.exists(path))


def _print_tls_configuration(props):
    print("\nCRDP TLS configuration")
    print("CRDPIP:", props.get("CRDPIP"))
    print("CRDPPORT:", props.get("CRDPPORT"))
    print("CRDP_SSL_ENABLED:", props.get("CRDP_SSL_ENABLED"))
    print("CRDP_SSL_VERIFY_SERVER:", props.get("CRDP_SSL_VERIFY_SERVER"))
    print("CRDP_CA_CERT_PATH:", props.get("CRDP_CA_CERT_PATH"))
    print("CRDP_CLIENT_CERT_PATH:", props.get("CRDP_CLIENT_CERT_PATH"))
    print("CRDP_CLIENT_KEY_PATH:", props.get("CRDP_CLIENT_KEY_PATH"))


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
        "ca_bundle_load_ok",
        "client_cert_chain_load_ok",
        "ca_bundle_load_error",
        "client_cert_chain_load_error",
    ]
    for key in interesting_keys:
        print(f"{key}: {tls_debug.get(key)}")


def run_compute_cluster_tls_smoke_test(
    spark_session,
    config_path="/tmp/thales_config/udfConfig.properties",
):
    os.environ["UDF_CONFIG_VOLUME_PATH"] = config_path
    _print_runtime_diagnostics(config_path)

    props = get_default_properties(refresh=True)

    _print_tls_configuration(props)
    _print_tls_resolution(props)

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
        properties=props,
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
        properties=props,
        spark_session=spark_session,
    )

    print("\nRevealed values:")
    for value in revealed_values:
        print(value)

    print("\nReveal matches original:", revealed_values == plaintext_values)

    if revealed_values != plaintext_values:
        raise ValueError(
            "TLS smoke test reveal values did not match the original plaintext values. "
            f"Expected={plaintext_values}, Actual={revealed_values}"
        )

    print("\nRepeated-call sanity check")
    for index in range(3):
        results = thales_crdp_python_function_bulk_secure(
            ["repeat1@example.com", "repeat2@example.com"],
            "protectbulk",
            "char",
            "email",
            properties=props,
            spark_session=spark_session,
        )
        print(f"Run {index + 1} complete: {results}")

    print("\nTHALES_COMPUTE_CLUSTER_TLS_SMOKE_TEST_FINISHED")


# Example notebook usage:
#
# from sample_tls_smoke_test_compute_cluster import run_compute_cluster_tls_smoke_test
# run_compute_cluster_tls_smoke_test(spark)
