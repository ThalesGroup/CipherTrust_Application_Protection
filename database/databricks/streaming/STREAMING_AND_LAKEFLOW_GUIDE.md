# Structured Streaming and Lakeflow Guide

This guide explains how Thales CRDP fits with:

- Structured Streaming
- Delta Live Tables / Lakeflow Declarative Pipelines

## Short answer

Yes, the solution supports Structured Streaming and Lakeflow/DLT patterns.

Recommended usage:

- compute clusters + Java Spark UDFs for high-throughput streaming ETL
- Unity Catalog secured views and UC functions for governed SQL-facing access
- Lakeflow SQL or Python pipelines to build streaming tables and materialized
  views around those governed objects

## Current Databricks support notes

Based on current Databricks documentation:

- Unity Catalog does not add explicit limits to Structured Streaming sources and
  sinks on Databricks
- in Databricks Runtime 14.1 and above, Structured Streaming can read Unity
  Catalog views backed by Delta tables
- Lakeflow Declarative Pipelines supports SQL and Python pipeline definitions
- Lakeflow SQL supports Unity Catalog Python UDFs in SQL queries when defined appropriately

## Recommended patterns

### Pattern 1: compute-cluster streaming ETL

Use when:

- you want high-throughput Spark processing
- you are running controlled jobs on compute clusters
- you want Java UDF execution on executors

Flow:

1. Register Java UDFs on the compute cluster.
2. Read tokenized data with `readStream`.
3. Apply the Java protect/reveal UDFs.
4. Write the result to a Delta target table.

Example file:

- `streaming/structured_streaming_examples.py`

Important note:

- for typical ETL pipelines, the most natural pattern is protect/tokenize during
  ingestion or transformation
- protect operations do not require a runtime reveal user
- direct reveal in streaming jobs is still possible, but protect is usually the
  primary ETL use case

### Pattern 2: stream from a secured Unity Catalog view

Use when:

- you want a stronger governance boundary
- the reveal logic should stay behind a secured view
- you want downstream streaming consumers to read already-governed output

Flow:

1. Create the secured view, for example `main.security.v_customer_reveal`.
2. Use `spark.readStream.table(...)` to stream from that view.
3. Write to a downstream Delta target.

Example file:

- `streaming/structured_streaming_uc_view_example.sql`

Important Databricks limitation:

- streaming reads from Unity Catalog views are supported only for views backed
  by Delta tables
- the supported operators in the source view are limited

Recommended governance note:

- this is the preferred governed streaming pattern when you do not want regular
  users or downstream jobs to call low-level `*_with_user` functions directly

### Pattern 3: Lakeflow / DLT SQL pipeline

Use when:

- you want SQL-defined incremental pipelines
- you want streaming tables and materialized views
- you want SQL-governed transformations around tokenized data

Flow:

1. Create a streaming table from the tokenized source.
2. Create a materialized view or downstream table that reveals data through
   Thales functions.

Example files:

- `streaming/lakeflow_sql_examples.sql`
- `streaming/plaintext_protected_internal_lakeflow_examples.sql`

## Example row-based source shape

```text
main.raw.customer_tokens
+-------------+------------+-----------+-----------------+---------------------+----------------+
| customer_id | first_name | last_name | customer_status | created_ts          | email_token    |
+-------------+------------+-----------+-----------------+---------------------+----------------+
| C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | A9K2...        |
| C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | B1M4...        |
+-------------+------------+-----------+-----------------+---------------------+----------------+
```

## Example revealed row-based result

```text
+-------------+------------+-----------+-----------------+---------------------+-------------------+
| customer_id | first_name | last_name | customer_status | created_ts          | email             |
+-------------+------------+-----------+-----------------+---------------------+-------------------+
| C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | alice@example.com |
| C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | bob@example.com   |
+-------------+------------+-----------+-----------------+---------------------+-------------------+
```

## Example array-based source shape

```text
main.raw.customer_token_arrays
+-------------------+---------------------+----------------------------------------+
| customer_group_id | snapshot_ts         | email_token_array                      |
+-------------------+---------------------+----------------------------------------+
| north-east-001    | 2026-04-07 09:00:00 | ["A9K2...","B1M4...","C7P8..."]        |
| north-east-002    | 2026-04-07 09:00:00 | ["D4Q1...","E6R3..."]                  |
+-------------------+---------------------+----------------------------------------+
```

## Example revealed array-based result

```text
+-------------------+---------------------+----------------------------------------------------------+
| customer_group_id | snapshot_ts         | email_array                                              |
+-------------------+---------------------+----------------------------------------------------------+
| north-east-001    | 2026-04-07 09:00:00 | ["alice@example.com","bob@example.com","carol@example.com"] |
| north-east-002    | 2026-04-07 09:00:00 | ["dave@example.com","erin@example.com"]                  |
+-------------------+---------------------+----------------------------------------------------------+
```

## Recommended customer answer

Yes. The solution supports both Structured Streaming and Lakeflow/DLT-style
pipelines.

- For compute-cluster ETL, use the Java Spark UDF path.
- For governed SQL-facing or downstream-consumer pipelines, use Unity Catalog
  functions and secured views.
- For Lakeflow/DLT, use streaming tables and materialized views that call the
  secured Thales functions or read from secured views.

## Related files

- `streaming/structured_streaming_examples.py`
- `streaming/structured_streaming_uc_view_example.sql`
- `streaming/lakeflow_sql_examples.sql`
- `streaming/plaintext_protected_internal_lakeflow_examples.sql`
- `COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md`
- `sql_warehouse/SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md`
