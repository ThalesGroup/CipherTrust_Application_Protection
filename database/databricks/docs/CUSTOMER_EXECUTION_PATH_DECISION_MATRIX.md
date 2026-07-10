# Customer Execution Path Decision Matrix

This one-page guide helps a customer decide which execution path to use for
Databricks protection and reveal workloads.

It is intentionally simple and customer-safe:

- no environment-specific benchmark dumps
- no cluster identifiers
- no endpoint details
- no internal-only rollout notes

## Executive Summary

Use the `Python helper wheel` when the main goal is compute-cluster throughput
and the team is comfortable working in PySpark DataFrame code.

Use the `Java jar / UDF` path when the team wants SQL-shaped compute-cluster
ETL, such as `CTAS`, `INSERT OVERWRITE`, and Spark SQL notebook workflows.

Use the `Unity Catalog Python UDF` path when the goal is governed SQL access,
shared reveal views, SQL Warehouse access, and BI-tool consumption.

## Quick Decision Table

| If the customer wants... | Recommended path | Why |
|---|---|---|
| Highest compute-cluster throughput | Python helper wheel | Best fit for DataFrame-first bulk orchestration |
| Spark SQL-first ETL on a compute cluster | Java jar / UDF | Best fit for SQL-shaped jobs and familiar UDF expressions |
| SQL Warehouse reveal views for BI users | Unity Catalog Python UDF | Best fit for persistent governed SQL abstractions |
| The simplest notebook API for engineers | Python helper wheel | Highest-level public API in this repo |
| A direct replacement mindset for older Spark SQL UDF usage | Java jar / UDF | Closest operating model to the older UDF-oriented path |

## What Each Path Looks Like

### 1. Python helper wheel

Typical usage shape:

```python
protected_df = protect_dataframe(
    df=source_df,
    object_name="my_catalog.my_schema.customer_protected",
    config=config,
    options=helper_options,
)
```

Best for:

- PySpark DataFrame pipelines
- notebook-first jobs
- performance-first compute-cluster protect/reveal workloads
- teams that want the helper layer to own grouping and CRDP request shaping

Main tradeoff:

- less SQL-shaped than direct Spark SQL UDF usage

### 2. Java jar / UDF

Typical usage shape:

```sql
SELECT
  thales_protect_by_object_and_column(
    email,
    'char',
    'my_catalog.my_schema.customer_protected',
    'email'
  ) AS email
FROM my_catalog.my_schema.customer_plaintext;
```

Best for:

- Spark SQL-first jobs
- `CREATE TABLE AS SELECT`
- `INSERT OVERWRITE`
- teams that want direct SQL expressions on a compute cluster

Main tradeoff:

- less flexible than the helper path for newer helper-driven batching patterns

### 3. Unity Catalog Python UDF

Typical usage shape:

- create persistent Unity Catalog functions
- create governed reveal views
- grant `SELECT` on views or `EXECUTE` on functions
- let BI tools or SQL users consume the resulting abstraction

Best for:

- SQL Warehouse
- governed reveal access
- shared SQL-facing interfaces
- business-user and BI-tool consumption

Main tradeoff:

- not the throughput-first path for large batch processing

## Performance Positioning

The important practical rule is:

- `Python helper wheel`
  strongest current compute-cluster performance-oriented path
- `Java jar / UDF`
  strong compute-cluster option when SQL authoring style matters more
- `Unity Catalog Python UDF`
  strongest governed SQL / BI path, but not the performance-first batch path

That means the customer should not choose the `Unity Catalog Python UDF` path
because it is expected to be faster than compute-cluster execution. It is
usually chosen because it is the better governance and serving model.

## Recommended Customer Positioning

For most organizations, the clean message is:

1. Use the `Python helper wheel` for engineering-owned compute-cluster
   pipelines.
2. Use the `Java jar / UDF` path when compute-cluster jobs are authored mainly
   in Spark SQL.
3. Use the `Unity Catalog Python UDF` path for governed SQL Warehouse views and
   BI-facing access.

## API Documentation

Use these documents for the detailed API surfaces:

- [PYTHON_DIRECT_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/PYTHON_DIRECT_API_GUIDE.md:1)
- [JAVA_UDF_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/JAVA_UDF_API_GUIDE.md:1)
- [UNITY_CATALOG_PYTHON_UDF_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/UNITY_CATALOG_PYTHON_UDF_GUIDE.md:1)

For broader tuning and model guidance, see:

- [PUBLIC_EXECUTION_GUIDELINES_AND_TUNING.md](/E:/codex/work/thales.databricks.integration/docs/PUBLIC_EXECUTION_GUIDELINES_AND_TUNING.md:1)
- [PUBLIC_EXECUTION_MODEL_MATRIX.md](/E:/codex/work/thales.databricks.integration/docs/PUBLIC_EXECUTION_MODEL_MATRIX.md:1)

For the detailed distinction between the two Unity Catalog SQL setup artifacts
and when to use each one, see:

- [UNITY_CATALOG_PYTHON_UDF_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/UNITY_CATALOG_PYTHON_UDF_GUIDE.md:1)
