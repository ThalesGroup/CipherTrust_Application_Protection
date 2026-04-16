# Documentation Index

Use this index to find the current guide for each deployment path.

## Start here

- [README.md](E:\eclipse-workspace\thales.databricks.udf\README.md)
- [DEPLOYMENT.md](E:\eclipse-workspace\thales.databricks.udf\DEPLOYMENT.md)

## Compute cluster

- [TEST_RUNBOOK.md](E:\eclipse-workspace\thales.databricks.udf\TEST_RUNBOOK.md)
- [COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md)
- [RUN_ORDER_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\RUN_ORDER_GUIDE.md)
- Init script:
  [copy_udf_config_init.sh](E:\eclipse-workspace\thales.databricks.udf\cluster_init_scripts\copy_udf_config_init.sh)

Current compute-cluster notebook flow:

- generic smoke test:
  [databricks_compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\databricks_compute_cluster_udf_smoke_test.py)
- customer table reveal example:
  [compute_cluster_table_reveal_castback.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_table_reveal_castback.py)
  [compute_cluster_table_reveal_castback.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_table_reveal_castback.sql)
- numeric measures:
  [databricks_compute_cluster_udf_numbers_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\databricks_compute_cluster_udf_numbers_smoke_test.py)
  [compute_cluster_numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_numbers_setup.sql)
- sample customer plaintext setup:
  [compute_cluster_plaintext_protected_internal_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_plaintext_protected_internal_setup.sql)

Debug / legacy:

- [databricks_compute_cluster_udf_plaintext_protected_internal_debug.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\databricks_compute_cluster_udf_plaintext_protected_internal_debug.py)
- [legacy_compute_cluster_secure_view_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy_compute_cluster_secure_view_examples.sql)
- [legacy_compute_cluster_secure_view_reference.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy_compute_cluster_secure_view_reference.sql)

## SQL Warehouse

- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)
- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)

Current SQL Warehouse scripts:

- main embedded-config deployment:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
- optimized bundled-array deployment:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)
- future packaged-config option:
[create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql)

Legacy / sample SQL Warehouse files:

- [legacy_create_uc_functions_built_wheel.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy_create_uc_functions_built_wheel.sql)
- [legacy_thales_crdp_uc_function_templates.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy_thales_crdp_uc_function_templates.sql)
- [sample_create_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\sample_create_uc_secure_views.sql)
- [sample_grant_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\sample_grant_uc_secure_views.sql)
- [sample_thales_crdp_python_udf_imports.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\sample_thales_crdp_python_udf_imports.py)

## Reference material

- [EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md](E:\eclipse-workspace\thales.databricks.udf\docs\EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md)
- [PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md](E:\eclipse-workspace\thales.databricks.udf\docs\PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md)
- [CUSTOMER_ARCHITECTURE.md](E:\eclipse-workspace\thales.databricks.udf\CUSTOMER_ARCHITECTURE.md)
- [FIELD_FAQ.md](E:\eclipse-workspace\thales.databricks.udf\FIELD_FAQ.md)
- [EXECUTION_MODEL_MATRIX.md](E:\eclipse-workspace\thales.databricks.udf\EXECUTION_MODEL_MATRIX.md)
- [STREAMING_AND_LAKEFLOW_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\STREAMING_AND_LAKEFLOW_GUIDE.md)
- [STREAMING_CAPABILITY_MATRIX.md](E:\eclipse-workspace\thales.databricks.udf\STREAMING_CAPABILITY_MATRIX.md)
