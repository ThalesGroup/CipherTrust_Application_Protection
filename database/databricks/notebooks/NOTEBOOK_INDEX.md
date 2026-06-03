# Notebook Index

This guide is the quickest way to choose the right notebook in the
[notebooks](E:\eclipse-workspace\thales.databricks.udf\notebooks) folder.

## Start here

If you are setting up a compute cluster for the first time, begin with:

- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)

Use it to:

- register the Java UDFs
- validate that the core internal and external signatures are working
- validate the new object-aware bulk protect and reveal signatures for internal, external, and none
- confirm the cluster and `udfConfig.properties` are wired correctly
- serve as the recommended Java compute-cluster TLS smoke test when TLS is enabled in `udfConfig.properties`

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

- [internal_pipeline_end_to_end_scalar_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_pipeline_end_to_end_scalar_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- final protect step timing

This is the best internal notebook when the goal is:

- customer-like pipeline realism

not:

- maximum tuning flexibility

### Use this for end-to-end pipeline realism with bulk protect

- [internal_pipeline_end_to_end_bulk_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_pipeline_end_to_end_bulk_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- grouped array preparation
- final bulk protect step timing

This is the best internal notebook when the goal is:

- customer-like pipeline realism plus bulk protect throughput

not:

- the simplest scalar demo path

## External notebooks

### Use this for scalar benchmark comparisons

- [external_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_object_aware_benchmark.py)

Use it when you want:

- scalar/object-aware external benchmark numbers
- comparison against the external bulk-array benchmark
- a benchmark without ADLS pipeline overhead

### Use this for the simplest production-style external load pattern

- [external_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_object_aware_load.py)

Use it when you want:

- the clearest distributed external protect example
- protected value plus sibling external header columns
- a customer-friendly scalar/object-aware load example

### Use this for the external bulk benchmark path

- [external_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_array_benchmark.py)

Use it when you want:

- grouped bulk external protect
- object-aware external array mapping resolution
- a generated high-row-count benchmark like the internal and none bulk notebooks
- protected value plus sibling external header columns written back to the standard row table shape

Backward-compatible wrapper:

- [external_bulk_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_with_headers_load.py)

This wrapper is retained only so older references keep working. New runs should
go directly to:

- [external_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_array_benchmark.py)

### Use this for end-to-end pipeline realism

- [external_pipeline_end_to_end_scalar_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_pipeline_end_to_end_scalar_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- final scalar protect step timing

### Use this for end-to-end pipeline realism with bulk protect

- [external_pipeline_end_to_end_bulk_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_pipeline_end_to_end_bulk_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- grouped array preparation
- final bulk protect step timing

## None notebooks

### Use this for scalar benchmark comparisons

- [none_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_scalar_object_aware_benchmark.py)

Use it when you want:

- scalar/object-aware none benchmark numbers
- comparison against the none bulk-array benchmark
- a benchmark without ADLS pipeline overhead

### Use this for the simplest production-style none load pattern

- [none_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_scalar_object_aware_load.py)

Use it when you want:

- the clearest distributed none protect example
- a customer-friendly scalar/object-aware load example

### Use this for the none-table benchmark path

- [none_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_bulk_array_benchmark.py)

Use it when you want:

- a true bulk benchmark targeting `plaintext_protected_none`
- object-aware none-table protection behavior
- grouped-array materialization diagnostics for the none path

### Use this for end-to-end pipeline realism

- [none_pipeline_end_to_end_scalar_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_pipeline_end_to_end_scalar_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- final scalar protect step timing

### Use this for end-to-end pipeline realism with bulk protect

- [none_pipeline_end_to_end_bulk_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_pipeline_end_to_end_bulk_load_test.py)

Use it when you want:

- raw file generation
- ADLS landing
- Delta load
- grouped array preparation
- final bulk protect step timing

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
2. Use [internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py), [external_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_array_benchmark.py), or [none_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_bulk_array_benchmark.py) for bulk benchmarking
3. Use the matching scalar benchmark for the policy type you want to compare:
   [internal_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_scalar_object_aware_benchmark.py),
   [external_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_object_aware_benchmark.py),
   or [none_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_scalar_object_aware_benchmark.py)
4. Use the matching scalar ADLS-backed batch-ingest example when you want end-to-end realism without grouped bulk orchestration
5. Use the matching bulk ADLS-backed batch-ingest example when you want end-to-end realism plus bulk protect throughput
6. Use the matching scalar load notebook when you want the simplest row-wise demo pattern
7. Use [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_setup.sql) plus the numbers notebooks for numeric examples
