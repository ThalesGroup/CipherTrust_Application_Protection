# Java UDF vs Python Wheel Guide

This note explains when to use the Java jar / UDF path versus the Python wheel / helper path on a Databricks compute cluster.

## Short answer

Use `Java UDFs` when the team wants SQL-shaped compute-cluster ETL.

Use the `Python wheel` when the team wants DataFrame-first or notebook-first workflows and wants the helper layer to own batching behavior.

## When Java UDFs are the better fit

- the workload is written primarily in Spark SQL
- the team wants `CREATE VIEW`, `CREATE TABLE AS SELECT`, or `INSERT OVERWRITE` patterns
- the team wants a row-oriented UDF surface that feels close to the older project
- the team wants the easiest apples-to-apples comparison against the original Java implementation
- the team is comfortable deploying a jar to the compute cluster

Typical examples:

- protect sensitive columns during a CTAS load
- create a protected permanent view on a compute cluster
- use Spark SQL notebooks with object-aware protect/reveal calls

Representative notebook:

- [compute_cluster_java_udf_sql_examples.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/internal/compute_cluster_java_udf_sql_examples.py:1)

## When the Python wheel is the better fit

- the workload is written primarily in PySpark DataFrames
- the team wants the simplest public API
- the team wants the helper layer to own grouping and bulk orchestration internally
- the team wants the most forward-looking architecture in this repo
- the team prefers wheel deployment over jar registration

Typical examples:

- notebook-first DataFrame transformations
- helper-driven batch jobs
- object-aware protect/reveal without manually shaping arrays

Representative notebook:

- [compute_cluster_python_helper_smoke_test.py](E:\codex\work\thales.databricks.integration\notebooks\smoke_tests\compute_cluster_python_helper_smoke_test.py:1)

## Performance-oriented interpretation

The practical split is:

- `Java UDFs`
  best for SQL-shaped compute-cluster use cases
- `Python wheel`
  best for helper/DataFrame compute-cluster use cases
- `Unity Catalog Python UDFs`
  best for governed SQL Warehouse / BI-facing use cases

Neither Java nor Python is automatically “better” in every scenario. The execution model and the way the team wants to author jobs usually matter more than the language alone.

## Can Java UDFs create only temp views?

No. On a compute cluster, Java UDFs can be used in:

- temporary views
- global temporary views
- permanent views
- CTAS tables
- `INSERT OVERWRITE` / `MERGE` / standard Spark SQL workflows

Examples:

```sql
CREATE OR REPLACE TEMP VIEW v_demo AS
SELECT
  thales_protect_by_object_and_column(email, 'char', 'my_catalog.my_schema.customer', 'email') AS email
FROM my_catalog.my_schema.customer_plaintext;
```

```sql
CREATE OR REPLACE VIEW my_catalog.my_schema.v_demo AS
SELECT
  thales_protect_by_object_and_column(email, 'char', 'my_catalog.my_schema.customer', 'email') AS email
FROM my_catalog.my_schema.customer_plaintext;
```

```sql
CREATE OR REPLACE TABLE my_catalog.my_schema.customer_protected AS
SELECT
  thales_protect_by_object_and_column(email, 'char', 'my_catalog.my_schema.customer', 'email') AS email
FROM my_catalog.my_schema.customer_plaintext;
```

## Recommended decision rule

If someone says:

- “We want raw SQL on compute cluster”
  use `Java UDFs`
- “We want the cleanest DataFrame or notebook API”
  use the `Python wheel`
- “We want governed SQL for SQL Warehouse or BI tools”
  use `Unity Catalog Python UDFs`

## Related notebooks

- [compute_cluster_java_udf_smoke_test.py](E:\codex\work\thales.databricks.integration\notebooks\smoke_tests\compute_cluster_java_udf_smoke_test.py:1)
- [compute_cluster_java_udf_sql_examples.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/internal/compute_cluster_java_udf_sql_examples.py:1)
- [compute_cluster_python_helper_smoke_test.py](E:\codex\work\thales.databricks.integration\notebooks\smoke_tests\compute_cluster_python_helper_smoke_test.py:1)
- [internal_java_udf_bulk_array_benchmark.py](E:\codex\work\thales.databricks.integration\notebooks\benchmarks\internal\internal_java_udf_bulk_array_benchmark.py:1)
- [internal_helper_dataframe_benchmark.py](E:\codex\work\thales.databricks.integration\notebooks\benchmarks\internal\internal_helper_dataframe_benchmark.py:1)
