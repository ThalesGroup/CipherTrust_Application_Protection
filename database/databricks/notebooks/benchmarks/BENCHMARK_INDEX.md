# Benchmark Index

This directory contains the active performance benchmark notebooks for the current Databricks integration project.

The benchmark set is organized by policy mode:

- `internal/`
  Benchmarks for internal-policy workloads.
- `external/`
  Benchmarks for external-policy workloads, including external-header handling.
- `no_version/`
  Benchmarks for no-version / none-policy workloads.

## Current Benchmark Model

The canonical benchmark notebooks in this directory now use the newer auto-tuned execution model:

- generation partitions are derived from row count and Spark parallelism
- target partitions are derived from sampled row width and estimated output size
- helper work-unit sizing is derived from target partitions
- Java grouped-array work-unit sizing is derived from target partitions
- CRDP request-item targets are auto-derived and can still be overridden for testing

This means the primary benchmark notebooks no longer depend on older fixed values such as:

- hard-coded `GENERATE_PARTITIONS = max(...)`
- hard-coded `TARGET_PARTITIONS = max(...)`
- hard-coded `WORK_UNIT_COUNT_TARGET = 64`
- hard-coded `CRDP_REQUEST_ITEM_TARGET = 5469`

## Active Benchmark Notebooks

### Internal

- `internal/internal_helper_dataframe_benchmark.py`
  Python helper / DataFrame benchmark for internal policy mode.
- `internal/internal_java_udf_bulk_array_benchmark.py`
  Java grouped-array UDF benchmark for internal policy mode.
- `internal/internal_pandas_udf_benchmark.py`
  Pandas `mapInPandas` benchmark for internal policy mode.

### External

- `external/external_helper_dataframe_benchmark.py`
  Python helper / DataFrame benchmark for external policy mode.
- `external/external_java_udf_bulk_array_benchmark.py`
  Java grouped-array UDF benchmark for external policy mode, including sibling external-header handling.
- `external/external_pandas_udf_benchmark.py`
  Pandas `mapInPandas` benchmark for external policy mode.

### No Version / None

- `no_version/none_helper_dataframe_benchmark.py`
  Python helper / DataFrame benchmark for no-version / none policy mode.
- `no_version/none_java_udf_bulk_array_benchmark.py`
  Java grouped-array UDF benchmark for no-version / none policy mode.
- `no_version/none_pandas_udf_benchmark.py`
  Pandas `mapInPandas` benchmark for no-version / none policy mode.

## Shared Utility

The benchmark notebooks use the shared tuning helper at:

- `../utils/execution_auto_tuning.py`

That helper contains the common logic for:

- generation partition recommendations
- target partition recommendations
- helper work-unit recommendations
- Java grouped-array work-unit recommendations

## What Stays Outside This Directory

These remain outside the benchmark directory because they are examples, setup flows, or other non-benchmark notebooks:

- ADLS load notebooks
- setup notebooks
- smoke tests
- pandas example notebooks
- other non-performance demo notebooks
