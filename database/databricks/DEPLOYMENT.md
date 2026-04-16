# Databricks deployment notes

## Compute cluster Java UDFs

Build the jar:

```powershell
mvn -DskipTests package
```

Upload the shaded jar:

- `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar`

Set the config path for driver and executors. For the current working
compute-cluster setup, use the init-script-based local copy under
`/tmp/thales_config/udfConfig.properties`.

Example Spark config:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Register Java UDF adapters from a notebook:

```scala
import org.apache.spark.sql.types.DataTypes

spark.udf.registerJava("thales_protect", "ThalesCrdpProtectUdf", DataTypes.StringType)
spark.udf.registerJava("thales_protect_by_column", "ThalesCrdpProtectByColumnUdf", DataTypes.StringType)
spark.udf.registerJava("thales_reveal", "ThalesCrdpRevealUdf", DataTypes.StringType)
spark.udf.registerJava("thales_reveal_by_column", "ThalesCrdpRevealByColumnUdf", DataTypes.StringType)
spark.udf.registerJava("thales_reveal_with_user", "ThalesCrdpRevealWithUserUdf", DataTypes.StringType)
spark.udf.registerJava("thales_reveal_by_column_with_user", "ThalesCrdpRevealByColumnWithUserUdf", DataTypes.StringType)

spark.udf.registerJava(
  "thales_protect_bulk",
  "ThalesCrdpProtectBulkUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
spark.udf.registerJava(
  "thales_protect_bulk_by_column",
  "ThalesCrdpProtectBulkByColumnUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
spark.udf.registerJava(
  "thales_reveal_bulk",
  "ThalesCrdpRevealBulkUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
spark.udf.registerJava(
  "thales_reveal_bulk_with_user",
  "ThalesCrdpRevealBulkWithUserUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
spark.udf.registerJava(
  "thales_reveal_bulk_by_column",
  "ThalesCrdpRevealBulkByColumnUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
spark.udf.registerJava(
  "thales_reveal_bulk_by_column_with_user",
  "ThalesCrdpRevealBulkByColumnWithUserUdf",
  DataTypes.createArrayType(DataTypes.StringType)
)
```

Usage examples:

```scala
df.selectExpr("thales_protect(email, 'char') as email_enc")
df.selectExpr("thales_protect_by_column(email, 'char', 'email') as email_enc")
df.selectExpr("thales_protect_bulk(email_batch, 'char') as email_batch_enc")
df.selectExpr("thales_protect_bulk_by_column(email_batch, 'char', 'email') as email_batch_enc")
```

Secure reveal examples using Databricks session identity:

```sql
SELECT thales_reveal_with_user(token_col, 'char', session_user())
FROM my_table
```

```sql
SELECT thales_reveal_by_column_with_user(token_col, 'char', 'email', session_user())
FROM my_table
```

```sql
SELECT thales_reveal_bulk_by_column_with_user(token_batch, 'char', 'email', session_user())
FROM my_table
```

### Which Java adapter to use

Use the simple hardcoded `UDF1` classes when the UDF name itself implies the
mode and datatype:

- `ThalesBulkProtectCharUdf`
- `ThalesBulkRevealCharUdf`
- `ThalesBulkProtectNbrUdf`
- `ThalesBulkRevealNbrUdf`

These are the easiest to register and are a good fit when:

- the notebook or job always knows the datatype ahead of time
- you want concise SQL such as `thales_bulk_protect_char(my_array_col)`
- you do not need to pass a column name at runtime

Use the generic adapters when you want flexibility:

- `ThalesCrdpProtectBulkUdf`
- `ThalesCrdpRevealBulkUdf`
- `ThalesCrdpProtectBulkByColumnUdf`
- `ThalesCrdpRevealBulkByColumnUdf`

These are better when:

- you want one registration that can work with different datatypes
- you want column-specific profile selection from `COLUMN_PROFILES`
- you want to preserve legacy and new signatures side by side

In general:

- choose hardcoded `UDF1` classes for the simplest cluster SQL experience
- choose generic adapters for reusable notebook/framework integrations
- for reveal operations, prefer the `*_with_user` adapters and pass `session_user()` or `current_user()` from SQL instead of relying on a static username in config

## SQL warehouse Python examples

See:

- `sql_warehouse/sample_thales_crdp_python_udf_imports.py`
- `sql_warehouse/legacy_thales_crdp_uc_function_templates.sql`
- `sql_warehouse/SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md`

That file is a starting point for warehouse-compatible Python functions. The
warehouse deployment model is different from cluster Java UDFs, so keep the
Python code path separate from the Java adapter classes.

## SQL warehouse Unity Catalog function deployment

Use the SQL template file to create warehouse-facing Unity Catalog functions:

- `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
- `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
- `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`
- `sql_warehouse/sample_create_uc_secure_views.sql`

Suggested deployment flow:

1. Upload or install the Python package so `thales_databricks_udf` is available
   to the SQL warehouse runtime.
2. Start with `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`.
3. If needed, use the optimized companion for the array-view path.
4. Run the `CREATE OR REPLACE FUNCTION` statements in Databricks SQL.
5. For secure reveal, wrap the `*_with_user` functions with views or SQL
   statements that inject `session_user()` or `current_user()`.

Recommended governance pattern:

- use legacy functions only for backward compatibility
- use column-aware functions for production rollout
- use `*_with_user` only behind governed SQL objects
- mark reveal paths as `NOT DETERMINISTIC`

Recommended run order for SQL Warehouse:

1. Create the Unity Catalog functions with:
   `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
2. Create the secured wrapper views with:
   `sql_warehouse/sample_create_uc_secure_views.sql`

## Compute cluster smoke-test notebook

Use the notebook below to register the Java UDF adapters and validate the
cluster deployment after attaching the shaded jar:

- `notebooks/databricks_compute_cluster_udf_smoke_test.py`
- `notebooks/compute_cluster_table_reveal_castback.py`
- `notebooks/compute_cluster_table_reveal_castback.sql`
- `COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md`

The notebook covers:

- Java UDF registration from Python
- scalar protect smoke tests
- bulk protect smoke tests
- reveal round-trip tests using `current_user()`

If you also want SQL wrapper views on compute clusters, use:

- `notebooks/compute_cluster_table_reveal_castback.py`
- `notebooks/compute_cluster_table_reveal_castback.sql`

Those examples show how to inject `current_user()` in Spark SQL after the Java
UDFs are registered.
