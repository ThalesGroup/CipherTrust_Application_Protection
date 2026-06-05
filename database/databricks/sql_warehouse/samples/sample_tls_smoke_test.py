"""
Compatibility wrapper for the split TLS smoke test samples.

Use one of these explicit variants instead:

- notebooks/utils/sample_tls_smoke_test_compute_cluster.py
- sample_tls_smoke_test_sql_warehouse.py

This file keeps the older import path working and defaults to the compute-
cluster implementation.
"""

import importlib.util
from pathlib import Path

from sample_tls_smoke_test_sql_warehouse import run_sql_warehouse_tls_smoke_test


def _load_compute_cluster_runner():
    current_file = Path(__file__).resolve()
    target_path = current_file.parents[2] / "notebooks" / "utils" / "sample_tls_smoke_test_compute_cluster.py"
    spec = importlib.util.spec_from_file_location("sample_tls_smoke_test_compute_cluster", target_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load compute-cluster TLS smoke test from {target_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_compute_cluster_tls_smoke_test


def run_tls_smoke_test(spark_session, config_path="/tmp/thales_config/udfConfig.properties"):
    return _load_compute_cluster_runner()(
        spark_session=spark_session,
        config_path=config_path,
    )


# Backward-compatible notebook usage:
#
# from sample_tls_smoke_test import run_tls_smoke_test
# run_tls_smoke_test(spark)
