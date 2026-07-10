# Utils Index

This directory contains shared Databricks utility notebooks, SQL helpers, and
supporting examples used by the compute-cluster and Unity Catalog samples in
this repository.

## Keep At Root

These files are intentionally kept at the `notebooks/utils` root because they
are referenced broadly by active notebooks or are foundational shared helpers.

- `runtime_diagnostics.py`
  Prints runtime configuration, profile resolution, and object-mapping
  diagnostics used across smoke tests and sample notebooks.
- `perf_metrics_helpers.py`
  Shared performance-metrics notebook loaded by benchmark notebooks via
  `%run ../utils/perf_metrics_helpers`.
- `synthetic_member_data_generator.py`
  Spark-based Databricks data generator notebook for producing benchmark/sample
  input datasets.
- `unity_catalog_python_udf_setup.sql`
  Unity Catalog setup notebook for the Python UDF execution path.
- `crdp_health_check_non_tls.py`
  Notebook-oriented non-TLS CRDP health check helper.
- `crdp_health_check_tls.py`
  Notebook-oriented TLS CRDP health check helper.

## Subdirectories

### `examples/`

Lightweight usage examples that demonstrate direct Python APIs without being
core shared runtime helpers.

- `python_crdp_api_examples.py`
- `python_crdp_api_examples_v2.py`

### `diagnostics/`

Validation and troubleshooting notebooks used to inspect runtime behavior,
partitioning, TLS readiness, or Java UDF execution characteristics.

- `java_runtime_context_probe.py`
- `java_udf_keepalive_smoke_test.py`
- `sample_tls_smoke_test_compute_cluster.py`
- `spark_partition_verification.py`

### `sql/`

SQL-only helper content that supports deployment or permissions guidance.

- `grant_examples.sql`

## Guidance

- If a file is `%run`-loaded by many notebooks, prefer leaving it at the root.
- If a file is primarily a standalone demo, example, or troubleshooting aid,
  prefer placing it under a subdirectory.
- When moving notebook files, update any documentation links and inline sample
  references at the same time so Databricks users do not follow stale paths.
