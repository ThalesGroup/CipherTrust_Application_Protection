# Deployment Guide

This guide describes the current deployment patterns for this project.

It covers:

- compute-cluster Java UDF deployment
- compute-cluster Python helper deployment
- Unity Catalog Python UDF / SQL Warehouse deployment

## Recommended Path By Use Case

Use `Python helper wheel` when:

- the workload is PySpark DataFrame-first
- throughput on a compute cluster is the main goal
- you want the highest-level API in this project

Use `Java jar / UDF` when:

- the workload is Spark SQL-first
- you want `CTAS`, `INSERT OVERWRITE`, or SQL-shaped ETL
- you want object-aware Java UDFs registered into a Spark session

Use `Unity Catalog Python UDF` when:

- the workload is governed SQL
- you want SQL Warehouse or BI-facing reveal views
- you want persistent Unity Catalog functions and views

For the short decision version, see:

- [CUSTOMER_EXECUTION_PATH_DECISION_MATRIX.md](/E:/codex/work/thales.databricks.integration/docs/CUSTOMER_EXECUTION_PATH_DECISION_MATRIX.md:1)

## Build Artifacts

Build the Java jar:

```powershell
mvn -DskipTests package
```

Expected artifacts:

- [target/thales-databricks-integration-0.1.0-SNAPSHOT.jar](/E:/codex/work/thales.databricks.integration/target/thales-databricks-integration-0.1.0-SNAPSHOT.jar)
- [target/thales-databricks-integration-0.1.0-SNAPSHOT-all.jar](/E:/codex/work/thales.databricks.integration/target/thales-databricks-integration-0.1.0-SNAPSHOT-all.jar)

Build the Python wheel:

```powershell
python -m build
```

Expected artifact:

- `dist/thales_databricks_integration-<version>-py3-none-any.whl`

## Compute Cluster Deployment

### 1. Attach the Java jar

Attach the shaded jar to the compute cluster:

- [target/thales-databricks-integration-0.1.0-SNAPSHOT-all.jar](/E:/codex/work/thales.databricks.integration/target/thales-databricks-integration-0.1.0-SNAPSHOT-all.jar)

This is required for the Java UDF path.

### 2. Optionally attach the Python wheel

Attach the wheel if the cluster will run the packaged Python helper APIs, such
as:

- [compute_cluster_python_helper_smoke_test.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_python_helper_smoke_test.py:1)
- [plaintext_setup_python.py](/E:/codex/work/thales.databricks.integration/notebooks/setup/plaintext_setup_python.py:1)

### 3. Make `udfConfig.properties` available at runtime

The preferred compute-cluster model is:

1. store `udfConfig.properties` on a Unity Catalog volume
2. use an init script to copy it to:
   `/tmp/thales_config/udfConfig.properties`
3. set both driver and executor runtime config paths

Recommended Spark config entries:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Required environment variables:

```text
UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
JNAME=zulu11-ca-amd64
```

This same pattern is used by:

- Java UDF runtime loading
- Python helper `IntegrationConfig.from_runtime()`

For more detail on config-path options, see:

- [THALES_PROPERTY_FILE_ACCESS_OPTIONS.md](/E:/codex/work/thales.databricks.integration/docs/THALES_PROPERTY_FILE_ACCESS_OPTIONS.md:1)

### 4. Run compute-cluster smoke tests

For the Python helper path:

- [compute_cluster_python_helper_smoke_test.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_python_helper_smoke_test.py:1)

For the Java UDF path:

- [compute_cluster_java_udf_smoke_test_bulk_reveal.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_java_udf_smoke_test_bulk_reveal.py:1)

### 5. Run setup / example notebooks as needed

Core compute-cluster setup and example notebooks:

- [plaintext_setup_bulk_reveal.sql](/E:/codex/work/thales.databricks.integration/notebooks/setup/plaintext_setup_bulk_reveal.sql:1)
- [compute_cluster_java_udf_sql_examples_external_round_trip.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/external/compute_cluster_java_udf_sql_examples_external_round_trip.py:1)

Recommended interpretation:

- [plaintext_setup_bulk_reveal.sql](/E:/codex/work/thales.databricks.integration/notebooks/setup/plaintext_setup_bulk_reveal.sql:1)
  is the preferred sample customer-table setup notebook. It creates the sample
  protected tables plus the row-based and array-based reveal shapes using the
  current Java UDF surface, including the Java bulk reveal path for array-based
  reveal scenarios.

Recommended interpretation:

- [compute_cluster_java_udf_sql_examples_external_round_trip.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/external/compute_cluster_java_udf_sql_examples_external_round_trip.py:1)
  is the preferred SQL-shaped Java UDF example notebook. It demonstrates temp
  views, CTAS, and external-policy protect plus reveal round trip behavior so
  the stored `protected_value` and `external_header` can be validated together.


## Current Java UDF Surface

The current registered Java UDF surface is:

- `thales_protect_by_object_and_column`
- `thales_reveal_by_object_and_column_with_user`
- `thales_protect_by_object_and_column_with_external_header`
- `thales_reveal_by_object_and_column_with_external_header_and_user`
- `thales_protect_bulk_by_object_and_column`
- `thales_protect_bulk_by_object_and_column_with_external_header`
- `thales_reveal_bulk_by_object_and_column_with_user`
- `thales_reveal_bulk_by_object_and_column_with_external_header_and_user`

Use:

- `current_user()` or `session_user()` for reveal-user injection
- wrapper views when you want a cleaner SQL surface

Full details are in:

- [JAVA_UDF_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/JAVA_UDF_API_GUIDE.md:1)

## Current Python Helper Surface

The main compute-cluster Python helper APIs are:

- `protect_dataframe(...)`
- `reveal_dataframe(...)`
- `protect_rows(...)`
- `reveal_rows(...)`

Full details are in:

- [PYTHON_DIRECT_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/PYTHON_DIRECT_API_GUIDE.md:1)

## Unity Catalog / SQL Warehouse Deployment

There are two main SQL setup shapes in this project.

### Volume-config Unity Catalog function setup

Use:

- [unity_catalog_python_udf_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/utils/unity_catalog_python_udf_setup.sql:1)

This path:

- creates persistent Unity Catalog Python functions
- passes `config_path` as part of the SQL contract
- is better for engineering experiments and reusable function building blocks

### Embedded-config SQL Warehouse setup

Use the SQL Warehouse index as the main entry point:

- [sql_warehouse/SQL_WAREHOUSE_INDEX.md](/E:/codex/work/thales.databricks.integration/sql_warehouse/SQL_WAREHOUSE_INDEX.md:1)

Supported embedded-config deploy templates:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql:1)
- [create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql:1)
- [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](/E:/codex/work/thales.databricks.integration/sql_warehouse/deploy/create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql:1)

This path:

- embeds the config directly in the Python function body
- creates governed SQL Warehouse reveal functions and views
- is the better production-style SQL Warehouse rollout model

Recommended interpretation:

- the internal deploy template is the strongest and most complete reference pattern
- the none deploy template follows the same current embedded-config and rowset-oriented design
- the external deploy template is current and supported, but remains more scalar and header-oriented because external-header behavior still requires sibling header handling

For the detailed distinction between these two models, see:

- [UNITY_CATALOG_PYTHON_UDF_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/UNITY_CATALOG_PYTHON_UDF_GUIDE.md:1)

## Profile Configuration

The runtime resolves profiles in this order:

1. `protect.object.<object_name>`
2. `column.<column_name>.profile`
3. `COLUMN_PROFILES`
4. `protection_profile`

Use:

- `column.<name>.profile` when the same logical column should resolve the same
  way broadly
- `protect.object.<object_name>` when a specific protected object needs to
  override the broader column default

See:

- [PROTECTION_PROFILE_OPTIONS.md](/E:/codex/work/thales.databricks.integration/docs/PROTECTION_PROFILE_OPTIONS.md:1)
- [PROFILE_RESOLUTION_ORDER.md](/E:/codex/work/thales.databricks.integration/docs/PROFILE_RESOLUTION_ORDER.md:1)

## Deployment Checklist

For compute cluster:

1. Build the jar.
2. Build the wheel if Python helper notebooks will be used.
3. Attach the jar to the cluster.
4. Attach the wheel if needed.
5. Make `udfConfig.properties` available at `/tmp/thales_config/udfConfig.properties`.
6. Set the driver and executor config-path Spark settings.
7. Run the appropriate smoke test notebook.
8. Run setup notebooks or example notebooks as needed.

For Unity Catalog / SQL Warehouse:

1. Upload the wheel to a Unity Catalog volume.
2. Choose either the volume-config or embedded-config SQL deployment model.
3. Create the Unity Catalog Python functions.
4. Create governed reveal views as needed.
5. Grant `EXECUTE` on functions or `SELECT` on views as appropriate.
