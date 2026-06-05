# SQL Warehouse Index

This guide is the quickest way to choose the right artifact in the
[sql_warehouse](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse) folder.

## Start here

If you want the main SQL Warehouse / Unity Catalog deployment path, start with:

- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)

If you want the rollout sequence and validation checklist, use:

- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)

## Folder layout

### deploy

Primary deployment scripts to run in Databricks SQL / Unity Catalog.

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)
- [create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql)
- [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql)
- [create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql)

Use these when you want:

- the main persistent UC function and view deployment path
- internal or external protected-table SQL Warehouse rollout scripts
- none-table SQL Warehouse rollout scripts

### samples

Reference examples and supporting SQL/Python patterns.

- [sample_create_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_create_uc_secure_views.sql)
- [sample_grant_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_grant_uc_secure_views.sql)
- [sample_thales_crdp_python_udf_imports.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_thales_crdp_python_udf_imports.py)
- [sample_tls_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_smoke_test.py)
- [sample_tls_smoke_test_compute_cluster.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_smoke_test_compute_cluster.py)
- [sample_tls_smoke_test_sql_warehouse.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_smoke_test_sql_warehouse.py)
- [sample_tls_debug_uc_function.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_debug_uc_function.sql)

Use these when you want:

- sample wrapper view patterns
- sample grants
- Python import/reference examples
- TLS smoke testing for the Python wheel path on compute clusters
- SQL Warehouse-style/base64 TLS smoke testing for the Python wheel path
- SQL Warehouse TLS material diagnostics

### utils

Helper and generator artifacts.

- [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)
- [generate_embedded_config_sql_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_embedded_config_sql_from_properties.py)

Use this when you want:

- help generating reveal-view SQL from properties-driven configuration
- stamping embedded-config SQL files from `udfConfig.properties`
- embedding SQL Warehouse TLS cert material as base64 properties

### legacy

Older or manually customized reference artifacts.

- [legacy_create_uc_functions_built_wheel.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy\legacy_create_uc_functions_built_wheel.sql)
- [legacy_thales_crdp_uc_function_templates.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy\legacy_thales_crdp_uc_function_templates.sql)

Use these only when:

- comparing against older deployment approaches
- manually adapting templates for a special case

### docs

Detailed guidance and rollout documents.

- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)
- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)
- [OPTIMIZED_UDF_MEMORY_GUIDANCE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\OPTIMIZED_UDF_MEMORY_GUIDANCE.md)

## Quick decision guide

1. Start with the deployment guide.
2. Choose a script from `deploy/`.
3. Use `samples/` for wrapper and grant examples.
4. Use `utils/` for SQL generation helpers.
5. Use `legacy/` only when you specifically need an older reference path.
