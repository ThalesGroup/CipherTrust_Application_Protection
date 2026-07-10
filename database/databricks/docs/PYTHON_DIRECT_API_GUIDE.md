# Python Direct API Guide

This guide explains the direct Python usage pattern for the new helper-first
wheel on a Databricks compute cluster.

## Purpose

This is the new equivalent of the older direct-Python example notebook from the
previous project.

Use this path when you want:

- quick direct validation of the wheel
- controlled Python/admin tests
- direct protect/reveal examples without DataFrame orchestration

## Helper API example

For DataFrame-first usage on a compute cluster, the most common pattern is:

```python
protected_df = protect_dataframe(
    spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)

revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)
```

Parameter descriptions:

- `spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS)`
  The input Spark DataFrame to protect. This is the actual source data. The
  `repartition(...)` call is optional and is commonly used to tune Spark
  parallelism for the protect workload.

- `spark.table(TARGET_TABLE)`
  The input Spark DataFrame to reveal. This is typically a protected table that
  was written by the protect step.

- `object_name=PROTECTED_OBJECT_NAME`
  The logical protected object key used by the integration. This is how the
  wheel finds the mapping in `udfConfig.properties`, such as
  `protect.object.my_catalog.my_schema.plaintext_protected_internal=...`.
  It is used to resolve which columns are sensitive and which profile,
  datatype, policy type, metadata, and reveal behavior apply to each column.
  The source table name does not need to appear in the properties file.

- `config=config`
  The loaded `IntegrationConfig` object, usually built from
  `udfConfig.properties`. This carries the runtime settings and object/column
  mappings used by the helper.

- `options=helper_options`
  Optional per-call overrides. These are commonly used for transport mode, API
  version, grouping, request-size settings, or reveal-user-related behavior
  without changing the base properties file.

- `protected_df`
  The returned protected Spark DataFrame.

- `revealed_df`
  The returned revealed Spark DataFrame.

## Full public API list

The wheel currently exposes the following public Python APIs.

### 1. Primary compute-cluster helper APIs

These are the main general-purpose APIs for compute-cluster jobs and notebooks:

- `protect_dataframe(...)`
- `reveal_dataframe(...)`
- `protect_rows(...)`
- `reveal_rows(...)`

Recommended positioning:

- `protect_dataframe(...)` and `reveal_dataframe(...)`
  Preferred for DataFrame-first pipelines

- `protect_rows(...)` and `reveal_rows(...)`
  Useful for direct Python tests, admin checks, smoke tests, and small
  row-shaped validation flows

### 2. Pandas APIs

These provide Pandas execution surfaces:

- `make_protect_scalar_pandas_udf(...)`
- `make_reveal_scalar_pandas_udf(...)`
- `protect_dataframe_map_in_pandas(...)`
- `reveal_dataframe_map_in_pandas(...)`

Recommended positioning:

- scalar Pandas UDF factories
  Useful when customers explicitly want a Pandas UDF style

- `mapInPandas` helpers
  Better fit when a full rowset Pandas execution shape is desired

### 3. Unity Catalog / SQL Warehouse helper APIs

These support the Unity Catalog Python UDF and governed SQL patterns:

- `uc_protect_by_object_and_column(...)`
- `uc_protect_by_object_and_column_embedded(...)`
- `uc_reveal_by_object_and_column(...)`
- `uc_reveal_by_object_and_column_embedded(...)`
- `uc_protect_bulk_by_object_and_column(...)`
- `uc_protect_bulk_by_object_and_column_embedded(...)`
- `uc_reveal_bulk_by_object_and_column(...)`
- `uc_reveal_bulk_by_object_and_column_embedded(...)`
- `uc_reveal_rowset_embedded(...)`

Recommended positioning:

- these are lower-level building blocks for UC Python functions and governed
  SQL abstractions
- most customers should consume the resulting SQL functions/views rather than
  call these directly from normal notebook code

### 4. Config and tuning exports

These are also part of the public surface:

- `IntegrationConfig`
- `ObjectPolicyConfig`
- `TuningResolution`
- `default_partitions(...)`
- `resolve_java_grouped_array_tuning(...)`
- `resolve_python_helper_tuning(...)`

## `IntegrationConfig` Overview

`IntegrationConfig` is the main Python configuration object used by the helper
APIs.

It carries:

- object-to-column profile mappings
- global column profile mappings
- CRDP transport settings
- API version settings
- request-size and grouping settings
- reveal-user defaults
- raw loaded properties for diagnostics

In most real deployments, it is created from `udfConfig.properties`.

### Common ways to create `IntegrationConfig`

#### 1. `IntegrationConfig.from_properties(path)`

Use this when you already know the exact config file path.

Example:

```python
config = IntegrationConfig.from_properties("/tmp/thales_config/udfConfig.properties")
```

Use this when:

- you want explicit control over the config file path
- you are outside Databricks
- you want the active config source to be obvious in the code

#### 2. `IntegrationConfig.from_runtime()`

Use this when you want the wheel to discover the runtime properties file.

Example:

```python
config = IntegrationConfig.from_runtime()
```

This resolves `udfConfig.properties` in this order:

1. explicit path passed to `from_runtime(...)`
2. `UDF_CONFIG_VOLUME_PATH`
3. `THALES_UDF_CONFIG_PATH`
4. `/tmp/thales_config/udfConfig.properties`

Use this when:

- you are on a Databricks compute cluster
- the init script or cluster setup already puts the file in the expected place
- you want notebook code to stay concise

#### 3. `IntegrationConfig.sample_customer_config()`

This creates an in-memory sample configuration for the direct Python APIs.

Important characteristics:

- uses `v2`
- uses `transport_mode = "stub"`
- does not require a real CRDP endpoint
- defines a simple sample object:
  - `my_catalog.my_schema.customer`
- includes sample profile mappings for:
  - `email`
  - `ssn`

Example:

```python
config = IntegrationConfig.sample_customer_config()
```

Use this when:

- you want an offline smoke test
- you want a simple outside-Databricks direct Python example
- you want to demonstrate request shaping without calling a live CRDP service

#### 4. `IntegrationConfig.sample_customer_config_v1()`

This is the same style of in-memory sample config, but forced to the `v1` API
shape.

Important characteristics:

- uses `v1`
- uses `transport_mode = "stub"`
- does not require a real CRDP endpoint
- defines the same simple sample object:
  - `my_catalog.my_schema.customer`

Example:

```python
config_v1 = IntegrationConfig.sample_customer_config_v1()
```

Use this when:

- you want to compare `v1` versus `v2` request behavior offline
- you want a local example that does not depend on real runtime properties

### Practical recommendation

Recommended usage by scenario:

- Databricks notebook or compute-cluster job:
  - `IntegrationConfig.from_runtime()`

- Direct Python with a known config file:
  - `IntegrationConfig.from_properties(path)`

- Offline smoke test or standalone API demo:
  - `IntegrationConfig.sample_customer_config()`
  - or `IntegrationConfig.sample_customer_config_v1()`

## Standalone Example Files

These example files are intended to run outside Databricks.

### 1. Pure offline stub smoke test

File:

- [python_direct_api_stub_smoke_test.py](E:\codex\work\thales.databricks.integration\standalone_examples\python_direct_api_stub_smoke_test.py:1)

Purpose:

- simplest direct Python smoke test
- no Databricks required
- no `udfConfig.properties` required
- no real CRDP endpoint required
- demonstrates `protect_rows(...)`, `reveal_rows(...)`, and `v1` versus `v2` behavior

### 2. Properties-based local stub demo

File:

- [python_direct_api_properties_stub_demo.py](E:\codex\work\thales.databricks.integration\standalone_examples\python_direct_api_properties_stub_demo.py:1)

Purpose:

- loads the real local `udfConfig.properties`
- validates object/profile resolution against that file
- forces `transport_mode = "stub"` for local execution
- useful when you want to validate local config behavior without making live CRDP calls

### 3. Properties-based real CRDP demo

File:

- [python_direct_api_properties_real_demo.py](E:\codex\work\thales.databricks.integration\standalone_examples\python_direct_api_properties_real_demo.py:1)

Purpose:

- loads the real local `udfConfig.properties`
- forces `transport_mode = "real"`
- attempts live CRDP connectivity outside Databricks
- useful when you want a lightweight connected direct-Python test

Important note:

- this example depends on the local properties file containing a reachable CRDP endpoint and any required local TLS certificate files

## Example notebook

See:

- [python_crdp_api_examples_v2.py](E:\codex\work\thales.databricks.integration\notebooks\utils\examples\python_crdp_api_examples_v2.py:1)

## Runtime config discovery

The new wheel now supports:

```python
IntegrationConfig.from_runtime()
```

This resolves `udfConfig.properties` in this order:

1. explicit path passed to `from_runtime(...)`
2. `UDF_CONFIG_VOLUME_PATH`
3. `THALES_UDF_CONFIG_PATH`
4. `/tmp/thales_config/udfConfig.properties`

That last fallback matches the current compute-cluster init-script copy target.

## Important clarification about the init script

Your current init script copies:

- `/Volumes/.../udfConfig.properties`

to:

- `/tmp/thales_config/udfConfig.properties`

The script shown so far does **not** itself export `UDF_CONFIG_VOLUME_PATH`.

That means:

- yes, the new wheel can now find the copied config automatically from the
  `/tmp/thales_config/udfConfig.properties` fallback
- no, it does not depend on the init script explicitly exporting the env var

If your cluster configuration also sets:

- `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
- `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`

that will still work too.
