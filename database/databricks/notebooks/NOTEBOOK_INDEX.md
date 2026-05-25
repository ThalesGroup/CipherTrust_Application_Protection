# Notebook Index

This guide is the quickest way to choose the right notebook in the
[notebooks](E:\eclipse-workspace\thales.databricks.udf\notebooks) folder.

## Start here

If you are setting up a compute cluster for the first time, begin with:

- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)

Use it to:

- register the Java UDFs
- validate that the core internal and external signatures are working
- confirm the cluster and `udfConfig.properties` are wired correctly

If you need sample plaintext tables for table-based examples, use:

- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)

If you want the notebook-specific tuning and benchmark docs collected in one
place, see:

- [NOTEBOOK_DOCS_INDEX.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\NOTEBOOK_DOCS_INDEX.md)

## Internal notebooks

### Use this for bulk tuning

- [internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py)

This is the primary high-control benchmark for the internal bulk-array path.

Use it when you want:

- the most control over Spark work shape
- the most control over Databricks grouping shape
- visibility into how grouping interacts with `BATCH_SIZE`
- bulk UDF performance tuning
- executor and parallelism experiments

### Use this for a simpler bulk benchmark

- [internal_bulk_array_benchmark_basic.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark_basic.py)

Use it when:

- you want the original simpler bulk benchmark shape
- you do not need `GROUP_COUNT_OVERRIDE`

### Use this for scalar benchmark comparisons

- [internal_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_scalar_object_aware_benchmark.py)

Use it when you want:

- scalar/object-aware benchmark numbers
- comparison against the bulk-array benchmark
- a benchmark without ADLS pipeline overhead

### Use this for the simplest production-style internal load pattern

- [internal_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_scalar_object_aware_load.py)

Use it when you want:

- the clearest distributed internal protect example
- a simple operational pattern to point at a plaintext table
- a customer-friendly scalar/object-aware load example

### Use this for end-to-end pipeline realism

- [internal_pipeline_end_to_end_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_pipeline_end_to_end_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- final protect step timing

This is the best internal notebook when the goal is:

- customer-like pipeline realism

not:

- maximum tuning flexibility

## External notebooks

### Use this for the standard external load pattern

- [external_scalar_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_with_headers_load.py)

Use it when you want:

- the recommended external-table load pattern
- protected value plus sibling external header columns
- the simplest production-style external example

## Numbers notebooks

### Use this to create the numeric sample workflow

- [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_setup.sql)

Use it when you want:

- numeric example tables
- internal, external, and no-version numeric paths
- numeric reveal setup objects

### Use this to validate numeric flows broadly

- [numbers_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_smoke_test.py)

Use it when you want:

- broad numeric smoke coverage
- internal, external, and none-protection numeric checks

### Use this for the focused numeric cast-back examples

- [numbers_reveal_castback_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_reveal_castback_examples.py)
- [numbers_reveal_castback_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_reveal_castback_examples.sql)

Use these when you want:

- the recommended numeric reveal and cast-back pattern
- examples showing reveal-to-string followed by cast back to the target numeric type

## Utility notebooks

### Shared metrics helper

- [perf_metrics_helpers.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\utils\perf_metrics_helpers.py)

Use it when:

- a benchmark notebook needs shared performance-metric helpers

This is intended to be `%run` by other notebooks, not used as the first
standalone entrypoint.

### Spark partition validation

- [spark_partition_verification.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\utils\spark_partition_verification.py)

Use it when you want:

- to verify Spark partition behavior
- to confirm task distribution matches the intended benchmark shape

### Grant examples

- [grant_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\utils\grant_examples.sql)

Use it when you want:

- example permission grants for the sample objects

### Python CRDP API examples

- [python_crdp_api_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\utils\python_crdp_api_examples.py)

Use it when you want:

- direct Python/API examples outside the main Spark benchmark flow

## Legacy / debug notebooks

These are retained for backward reference or troubleshooting, not as the
preferred customer examples.

- [legacy_secure_view_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy\legacy_secure_view_examples.sql)
- [legacy_internal_debug_reveal_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy\legacy_internal_debug_reveal_examples.py)

Use them only when:

- troubleshooting older reveal behavior
- comparing current behavior against older examples
- debugging a legacy flow

## Quick decision guide

If you are unsure which notebook to use:

1. Start with [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)
2. Use [internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py) for the highest-control bulk tuning
3. Use [internal_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_scalar_object_aware_benchmark.py) for scalar comparisons
4. Use [internal_pipeline_end_to_end_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_pipeline_end_to_end_load_test.py) for pipeline realism
5. Use [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_setup.sql) plus the numbers notebooks for numeric examples
