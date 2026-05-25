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
  [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)
- customer table reveal example:
  [numbers_reveal_castback_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_reveal_castback_examples.py)
  [numbers_reveal_castback_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_reveal_castback_examples.sql)
- partition/executor verification:
  [spark_partition_verification.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\utils\spark_partition_verification.py)
- numeric measures:
  [numbers_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_smoke_test.py)
  [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_setup.sql)
- sample customer plaintext setup:
  [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)
- compute-cluster setup note:
  these setup notebooks self-register the session Java UDFs they need, create
  persistent protected tables, and create session `TEMP VIEW` reveal views
- high-throughput internal load:
  [internal_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_scalar_object_aware_load.py)
- high-throughput external load:
  [external_scalar_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external_scalar_with_headers_load.py)

Debug / legacy:

- [legacy_internal_debug_reveal_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy_internal_debug_reveal_examples.py)
- [legacy_secure_view_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy_secure_view_examples.sql)

## SQL Warehouse

- [SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md)
- [SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\SQL_WAREHOUSE_ROLLOUT_CHECKLIST.md)

Current SQL Warehouse scripts:

- main embedded-config deployment:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
- optimized bundled-array deployment:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)
- external-policy deployment and reveal-view example:
  [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql)
- generator notebook that can emit reviewable reveal-view SQL from `protect.object` mappings:
  [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)
  This generator creates SQL Warehouse artifacts, but it must be run from a
  Python-capable Databricks cluster notebook rather than from a SQL Warehouse notebook.
- packaged-config deployment option:
[create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql)

Legacy / sample SQL Warehouse files:

- [legacy_create_uc_functions_built_wheel.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy\legacy_create_uc_functions_built_wheel.sql)
- [legacy_thales_crdp_uc_function_templates.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\legacy\legacy_thales_crdp_uc_function_templates.sql)
- [sample_create_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_create_uc_secure_views.sql)
- [sample_grant_uc_secure_views.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_grant_uc_secure_views.sql)
- [sample_thales_crdp_python_udf_imports.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_thales_crdp_python_udf_imports.py)

## Reference material

- [EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md](E:\eclipse-workspace\thales.databricks.udf\docs\EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md)
- [PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md)
- [EXTERNAL_HEADER_COLUMN_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\docs\EXTERNAL_HEADER_COLUMN_GUIDE.md)
  External-header implementation guide for compute clusters and SQL Warehouse
- [PROTECTION_PROFILE_OPTIONS.md](E:\eclipse-workspace\thales.databricks.udf\docs\PROTECTION_PROFILE_OPTIONS.md)
- [PERFORMANCE_CONSIDERATIONS.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PERFORMANCE_CONSIDERATIONS.md)
- [PARTITIONING_GUIDANCE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PARTITIONING_GUIDANCE.md)
- [DELTA_PARTITIONING_GUIDANCE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\DELTA_PARTITIONING_GUIDANCE.md)
- [LOGGING_DESIGN.md](E:\eclipse-workspace\thales.databricks.udf\docs\LOGGING_DESIGN.md)
- [CUSTOMER_ARCHITECTURE.md](E:\eclipse-workspace\thales.databricks.udf\CUSTOMER_ARCHITECTURE.md)
- [FIELD_FAQ.md](E:\eclipse-workspace\thales.databricks.udf\FIELD_FAQ.md)
- [EXECUTION_MODEL_MATRIX.md](E:\eclipse-workspace\thales.databricks.udf\EXECUTION_MODEL_MATRIX.md)
- [STREAMING_AND_LAKEFLOW_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\streaming\docs\STREAMING_AND_LAKEFLOW_GUIDE.md)
- [STREAMING_CAPABILITY_MATRIX.md](E:\eclipse-workspace\thales.databricks.udf\streaming\docs\STREAMING_CAPABILITY_MATRIX.md)


