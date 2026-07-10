# Unity Catalog Python UDF Guide

This guide explains the first Unity Catalog Python UDF surface for the new
helper-first integration.

## Purpose

The compute-cluster helper path is already implemented in this repository.
This guide adds the SQL-governed path so the same wheel can be used for:

- SQL Warehouse
- governed BI access
- secured reveal views
- Unity Catalog function-based usage

## What is implemented

The wheel now exposes UC-friendly Python functions in
[uc.py](E:\codex\work\thales.databricks.integration\src\thales_databricks_integration\uc.py:1):

- `uc_protect_by_object_and_column(...)`
- `uc_reveal_by_object_and_column(...)`
- `uc_protect_bulk_by_object_and_column(...)`
- `uc_reveal_bulk_by_object_and_column(...)`

These functions are designed to be called from Unity Catalog Python functions.

## SQL setup artifact

The initial SQL setup script is:

- [unity_catalog_python_udf_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/utils/unity_catalog_python_udf_setup.sql:1)

It defines:

- scalar protect
- scalar reveal
- bulk protect
- bulk reveal
- a sample secured reveal view

For the current SQL Warehouse deployment set, see:

- [sql_warehouse/SQL_WAREHOUSE_INDEX.md](/E:/codex/work/thales.databricks.integration/sql_warehouse/SQL_WAREHOUSE_INDEX.md:1)

## Which Script Goes With Which Runtime Model

These two scripts are related, but they target different deployment models.

| Script | Typical place you run the setup | Typical place the resulting functions/views are consumed | Config model | Best fit |
|---|---|---|---|---|
| `unity_catalog_python_udf_setup.sql` | Compute cluster notebook or UC-enabled engineering setup workflow | Unity Catalog SQL consumers that can tolerate a `config_path`-driven function contract | Runtime `config_path` argument points to `udfConfig.properties` on a volume | Engineering experiments, reusable building blocks, configurable UC function surface |
| `create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql` | SQL Warehouse or serverless-oriented deployment workflow | SQL Warehouse, governed views, BI users, shared production reveal views | Config is embedded directly in the Python function body | Production-style governed SQL serving where config-path dependency should be hidden |
| `create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql` | SQL Warehouse or serverless-oriented deployment workflow | SQL Warehouse, governed none-policy reveal views | Config is embedded directly in the Python function body | Production-style none-policy rollout |
| `create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql` | SQL Warehouse or serverless-oriented deployment workflow | SQL Warehouse, governed external-policy reveal views with sibling header handling | Config is embedded directly in the Python function body | Production-style external-policy rollout where header columns must be preserved |

Important clarification:

- both scripts create persistent Unity Catalog functions
- both scripts can create persistent Unity Catalog views
- both resulting views are still just normal Unity Catalog views from the
  consumer perspective

The real difference is not "view versus non-view." The real difference is what
the underlying function depends on:

- `unity_catalog_python_udf_setup.sql`
  depends on a function signature that still accepts `config_path`
- `embedded_config`
  depends on a function whose config is already baked into the function body

That means:

- the `unity_catalog_python_udf_setup.sql` path is more flexible
- the `embedded_config` path is more self-contained

## Practical Interpretation

If a team says:

- "We want a reusable UC Python function surface that engineering can adapt"
  use `unity_catalog_python_udf_setup.sql`
- "We want a finished governed SQL Warehouse artifact for analysts and BI
  tools"
  use the embedded-config deployment script

For most production BI-facing rollouts, the embedded-config pattern is the more
natural published artifact because downstream users do not need to know about:

- `config_path`
- properties-file location
- volume layout
- runtime config plumbing

## Current design shape

This first UC path is object-aware and config-driven:

- SQL passes `object_name`
- SQL passes `column_name`
- SQL passes the `config_path` to the properties file on a UC volume
- reveal also passes `session_user()` for governed identity resolution

## Recommended deployment model

1. Upload the wheel to a Unity Catalog volume.
2. For compute-cluster or volume-config experiments, upload `udfConfig.properties` to a Unity Catalog volume.
3. For SQL Warehouse, use the current deployment set in:
   [sql_warehouse/SQL_WAREHOUSE_INDEX.md](/E:/codex/work/thales.databricks.integration/sql_warehouse/SQL_WAREHOUSE_INDEX.md:1)
4. For compute-cluster UC function experiments, use:
   [unity_catalog_python_udf_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/utils/unity_catalog_python_udf_setup.sql:1)
5. Grant `EXECUTE` on the functions or `SELECT` on secured views as needed.

## SQL Warehouse recommendation

For SQL Warehouse, the recommended reveal surface is now:

- primary customer-facing view:
  `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized`
- lower-level validation view:
  `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized`

Why:

- the older scalar and per-column bulk views pay too much UC Python UDF fan-out cost
- the optimized rowset-based views are materially faster
- the optimized flattened view keeps the customer-friendly row shape without reintroducing the old per-column penalty

Measured internal sample results are summarized in:

- [SQL_WAREHOUSE_REVEAL_PERFORMANCE_NOTES.md](E:\codex\work\thales.databricks.integration\docs\SQL_WAREHOUSE_REVEAL_PERFORMANCE_NOTES.md:1)

Recommended benchmark split:

- latency/capability comparison:
  [benchmark_uc_plaintext_protected_internal_reveal_performance.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/benchmarks/benchmark_uc_plaintext_protected_internal_reveal_performance.sql:1)
- throughput/materialization comparison:
  [benchmark_uc_plaintext_protected_internal_reveal_ctas.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/benchmarks/benchmark_uc_plaintext_protected_internal_reveal_ctas.sql:1)
- engineering-only overhead isolation:
  [benchmark_uc_python_udf_overhead_embedded_config.sql](E:\codex\work\thales.databricks.integration\sql_warehouse\diagnostics\benchmark_uc_python_udf_overhead_embedded_config.sql:1)

## Current limitations

- External-header support exists for SQL Warehouse through the dedicated embedded-config external deployment path, but a higher-level generic rowset-style external-header helper abstraction is not yet implemented in `uc.py`.
- The SQL surface is currently column-oriented rather than a full table-transform SQL abstraction.

## Why this is still the right next step

This closes the most important remaining execution-model gap after the
compute-cluster helper path:

- governed SQL access
- BI-facing usage
- Unity Catalog deployment

That makes it the strongest next parity step after compute-cluster notebook
execution.
