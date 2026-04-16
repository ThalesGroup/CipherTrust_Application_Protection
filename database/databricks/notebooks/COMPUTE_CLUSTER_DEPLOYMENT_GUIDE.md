# Databricks Compute Cluster Deployment Guide

This guide covers the Java UDF deployment path for Databricks compute clusters.
Use this model when your main workload is Spark ETL, batch processing, or
cluster-based notebooks/jobs rather than Databricks SQL warehouses.

## When to use this path

Use compute-cluster Java UDFs when you want:

- high-throughput Spark execution across executors
- cluster notebook and job integration
- Java-based UDF registration from Spark
- bulk reveal/protect inside ETL pipelines

Use the SQL Warehouse / Unity Catalog Python function path when your main use
case is Databricks SQL, BI tools, or shared governed SQL functions.

## Artifacts in this project

- `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar`
- `src/main/resources/udfConfig.properties`
- `notebooks/databricks_compute_cluster_udf_smoke_test.py`
- `notebooks/compute_cluster_table_reveal_castback.py`
- `notebooks/compute_cluster_table_reveal_castback.sql`
- `notebooks/compute_cluster_grant_examples.sql`
- `cluster_init_scripts/copy_udf_config_init.sh`

## Deployment overview

1. Build the shaded jar.
2. Attach the jar to the Databricks compute cluster.
3. Configure the init script, `UDF_CONFIG_VOLUME_PATH`, and environment variables.
4. Register the Java UDFs.
5. Run smoke tests.
6. Optionally create SQL wrapper views that inject `current_user()`.
7. Grant consumers access to persistent views.

## Step 1: Build the jar

From the workspace root:

```powershell
mvn -DskipTests package
```

Expected artifact:

- `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar`

## Step 2: Attach the jar to the cluster

Upload or reference the shaded jar in the compute cluster libraries UI or your
cluster policy/deployment workflow.

## Step 3: Configure the UDF config path

Use the cluster init script to copy `udfConfig.properties` from the Unity
Catalog volume to a local `/tmp` path before Spark starts, then point both
driver and executors at that local file.

Example:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Environment variables:

```text
UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
JNAME=zulu11-ca-amd64
```

Init script volume path:

```text
/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh
```

## Step 4: Register the Java UDFs

Use:

- `notebooks/databricks_compute_cluster_udf_smoke_test.py`

That notebook registers:

- scalar protect/reveal UDFs
- column-aware UDFs
- reveal-with-user UDFs
- generic bulk UDFs
- hardcoded convenience bulk UDFs
- the current examples use the string-based `nbr` path with cast-back for numeric values

## Step 5: Row-based usage pattern

The most common pattern is still one protected value per row.

Example row-based source shape:

```text
main.raw.customer_tokens
+-------------+------------+-----------+-----------------+---------------------+----------------+
| customer_id | first_name | last_name | customer_status | created_ts          | email_token    |
+-------------+------------+-----------+-----------------+---------------------+----------------+
| C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | A9K2...        |
| C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | B1M4...        |
+-------------+------------+-----------+-----------------+---------------------+----------------+
```

Example cluster SQL wrapper view:

```sql
CREATE OR REPLACE VIEW main.security.v_customer_reveal AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  thales_reveal_by_column_with_user(
    email_token,
    'char',
    'email',
    current_user()
  ) AS email
FROM main.raw.customer_tokens;
```

### Numeric usage guidance

For numeric values, the current examples use the string-based `nbr` path and
cast the revealed value back in the query or view. This avoids token-format
issues with leading zeros and decimal normalization.

Example row-based view result:

```text
SELECT * FROM main.security.v_customer_reveal LIMIT 2;

+-------------+------------+-----------+-----------------+---------------------+-------------------+
| customer_id | first_name | last_name | customer_status | created_ts          | email             |
+-------------+------------+-----------+-----------------+---------------------+-------------------+
| C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | alice@example.com |
| C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | bob@example.com   |
+-------------+------------+-----------+-----------------+---------------------+-------------------+
```

## Step 6: Array-based usage pattern

Use the bulk UDFs only when the source table intentionally stores arrays in a
single row.

Example array-based source shape:

```text
main.raw.customer_token_arrays
+-------------------+---------------------+----------------------------------------+
| customer_group_id | snapshot_ts         | email_token_array                      |
+-------------------+---------------------+----------------------------------------+
| north-east-001    | 2026-04-07 09:00:00 | ["A9K2...","B1M4...","C7P8..."]        |
| north-east-002    | 2026-04-07 09:00:00 | ["D4Q1...","E6R3..."]                  |
+-------------------+---------------------+----------------------------------------+
```

Example cluster SQL wrapper view:

```sql
CREATE OR REPLACE VIEW main.security.v_customer_array_reveal AS
SELECT
  customer_group_id,
  snapshot_ts,
  thales_reveal_bulk_by_column_with_user(
    email_token_array,
    'char',
    'email',
    current_user()
  ) AS email_array
FROM main.raw.customer_token_arrays;
```

Example array-based view result:

```text
SELECT * FROM main.security.v_customer_array_reveal LIMIT 2;

+-------------------+---------------------+----------------------------------------------------------+
| customer_group_id | snapshot_ts         | email_array                                              |
+-------------------+---------------------+----------------------------------------------------------+
| north-east-001    | 2026-04-07 09:00:00 | ["alice@example.com","bob@example.com","carol@example.com"] |
| north-east-002    | 2026-04-07 09:00:00 | ["dave@example.com","erin@example.com"]                  |
+-------------------+---------------------+----------------------------------------------------------+
```

## TEMP VIEW versus VIEW

`TEMP VIEW`:

- exists only for the current Spark session
- is useful for notebook testing and quick validation
- disappears when the session or cluster context ends

`VIEW`:

- is persisted in a metastore catalog/schema
- can be reused by other sessions and users with permissions
- is the better choice for shared governed access patterns

Use `TEMP VIEW` in examples when you want low-risk notebook testing. Use
`CREATE OR REPLACE VIEW main.security...` when you want a durable shared object.

## Roles and grants matrix

| Role | Typical privileges | Why |
|---|---|---|
| `thales_cluster_deployers` | `USE CATALOG`, `USE SCHEMA`, create view capability, `SELECT` on source tables | Registers UDFs, creates persistent views, validates cluster behavior |
| `pii_consumers` | `USE CATALOG`, `USE SCHEMA`, `SELECT` on persistent secured views | Reads revealed data only through governed views |
| Raw-table owners | ownership or managed `SELECT` on `main.raw.*` | Controls access to the underlying tokenized source tables |

Recommended least-privilege pattern:

- use `TEMP VIEW` only for testing, not for durable shared access
- if you create persistent `main.security` views from the cluster, grant users
  `SELECT` on those views
- do not treat session-registered Java UDFs as directly user-facing governed
  objects

## Grants

Use:

- `notebooks/compute_cluster_grant_examples.sql`

Recommended model:

- if you create persistent Unity Catalog views from a compute cluster, grant
  consumers `USE CATALOG`, `USE SCHEMA`, and `SELECT` on those views
- do not rely on grants for `TEMP VIEW`s because they are session-scoped
- Java session UDF registrations are not Unity Catalog functions, so there is
  no Unity Catalog `EXECUTE` privilege to grant on them

## Secure reveal guidance

The Java code does not automatically introspect Databricks session identity the
way the Python helper attempts to. For Java UDFs, the recommended secure model
is:

1. use the `*_with_user` Java UDFs
2. inject `current_user()` or `session_user()` in SQL
3. optionally hide that behind views

Important limitation:

- if regular notebook users can directly call the registered Java `*_with_user`
  UDFs, they can also choose how they call them
- that means compute-cluster session UDFs are not the strongest governed model
  for broad end-user self-service access
- for regular production users, prefer SQL Warehouse / Unity Catalog secured
  views as the primary reveal access path
- use compute-cluster Java UDFs mainly for ETL, jobs, and controlled admin
  notebooks

## Related files

- `DEPLOYMENT.md`
- `README.md`
- `notebooks/databricks_compute_cluster_udf_smoke_test.py`
- `notebooks/compute_cluster_table_reveal_castback.py`
- `notebooks/compute_cluster_table_reveal_castback.sql`
- `notebooks/compute_cluster_grant_examples.sql`
