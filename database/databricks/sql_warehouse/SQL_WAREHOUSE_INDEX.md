# SQL Warehouse Index

This folder contains the current SQL Warehouse artifacts for the Thales Databricks Integration project.

## What Is Here

- `deploy`
  Current supported SQL Warehouse deployment templates.
- `benchmarks`
  Benchmark scripts for latency, count, and CTAS-style throughput measurements.
- `diagnostics`
  Engineering diagnostics for isolating Python UDF overhead.
- `smoketest`
  Focused smoke tests for SQL Warehouse and UC Python UDF scenarios.
- `utils`
  Generators for embedded-config SQL and reveal-view SQL.

## Recommended Starting Point

For most customer-facing SQL Warehouse rollouts, start with:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql:1)

That script is the strongest end-to-end reference template for:

- persistent Unity Catalog Python reveal functions
- embedded configuration
- governed reveal views
- the optimized rowset-based reveal pattern

## Supported Deploy Templates

- Internal reveal path:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql:1)
- None-policy reveal path:
  [create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql:1)
- External-policy reveal path:
  [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql:1)

## Benchmarks

- Interactive latency and shape comparison:
  [benchmark_uc_plaintext_protected_internal_reveal_performance.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/benchmarks/benchmark_uc_plaintext_protected_internal_reveal_performance.sql:1)
- Full-processing count benchmark:
  [benchmark_uc_plaintext_protected_internal_reveal_count.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/benchmarks/benchmark_uc_plaintext_protected_internal_reveal_count.sql:1)
- CTAS throughput/materialization benchmark:
  [benchmark_uc_plaintext_protected_internal_reveal_ctas.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/benchmarks/benchmark_uc_plaintext_protected_internal_reveal_ctas.sql:1)

## Diagnostics

- Python UDF overhead isolation:
  [benchmark_uc_python_udf_overhead_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/diagnostics/benchmark_uc_python_udf_overhead_embedded_config.sql:1)

## Smoke Tests

- [sample_tls_smoke_test_sql_warehouse.py](/E:/codex/work/thales.databricks.integration/sql_warehouse/smoketest/sample_tls_smoke_test_sql_warehouse.py:1)
- [sample_tls_debug_uc_function.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/smoketest/sample_tls_debug_uc_function.sql:1)

## Generators

- [generate_embedded_config_sql_from_properties.py](/E:/codex/work/thales.databricks.integration/sql_warehouse/utils/generate_embedded_config_sql_from_properties.py:1)
- [generate_reveal_views_from_properties.py](/E:/codex/work/thales.databricks.integration/sql_warehouse/utils/generate_reveal_views_from_properties.py:1)
