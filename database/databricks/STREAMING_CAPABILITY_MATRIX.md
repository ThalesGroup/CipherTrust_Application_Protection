# Streaming and Lakeflow Capability Matrix

This guide summarizes the main streaming and pipeline patterns supported by the
Thales CRDP Databricks solution.

## Matrix

| # | Option | Where it runs | Best use case | Recommended governance model |
|---|---|---|---|---|
| 1 | Structured Streaming with Java UDFs | Compute-cluster executors | High-throughput streaming ETL | Controlled jobs/admin use |
| 2 | Structured Streaming from secured UC view | Compute cluster reading UC view | Governed downstream streaming consumption | Preferred secured streaming pattern |
| 3 | Lakeflow / DLT SQL with UC functions | Managed SQL/pipeline runtime | SQL-defined incremental pipelines | Strong governed SQL model |
| 4 | Lakeflow / DLT reading secured views | Managed SQL/pipeline runtime | Shared governed pipeline consumption | Strongest boundary for reveal access |

## 1. Structured Streaming with Java UDFs

Setup:

```python
from pyspark.sql import types as T

spark.udf.registerJavaFunction(
    "thales_protect_by_column",
    "ThalesCrdpProtectByColumnUdf",
    T.StringType(),
)
```

Transform:

```python
customer_stream = spark.readStream.table("main.raw.customer_cleartext")

protected_customer_stream = customer_stream.selectExpr(
    "customer_id",
    "first_name",
    "last_name",
    "customer_status",
    "created_ts",
    "thales_protect_by_column(email, 'char', 'email') as email_token",
)
```

Usage:

```python
query = (
    protected_customer_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_protect_stream")
    .toTable("main.raw.customer_tokens")
)
```

Note:

- this is the primary ETL/protect pattern
- no runtime reveal user is required for protect

## 2. Structured Streaming from secured UC view

Setup:

```sql
CREATE OR REPLACE VIEW main.security.v_customer_reveal AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  main.security.thales_crdp_scalar_by_column_with_user(
    email_token,
    'reveal',
    'char',
    'email',
    session_user()
  ) AS email
FROM main.raw.customer_tokens;
```

Transform:

```python
governed_customer_stream = spark.readStream.table("main.security.v_customer_reveal")
```

Usage:

```python
query = (
    governed_customer_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_reveal_stream_from_view")
    .toTable("main.security.customer_reveal_stream_from_view")
)
```

Note:

- this is the preferred governed streaming pattern
- regular users and downstream jobs consume the view, not the low-level function

## 3. Lakeflow / DLT SQL with UC functions

Setup:

```sql
CREATE OR REFRESH STREAMING TABLE customer_tokens_bronze
AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  email_token
FROM STREAM main.raw.customer_tokens;
```

Transform:

```sql
CREATE OR REFRESH MATERIALIZED VIEW customer_reveal_gold
AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  main.security.thales_crdp_scalar_by_column_with_user(
    email_token,
    'reveal',
    'char',
    'email',
    session_user()
  ) AS email
FROM customer_tokens_bronze;
```

Usage:

```sql
SELECT * FROM customer_reveal_gold;
```

## 4. Lakeflow / DLT reading secured views

Setup:

```sql
CREATE OR REPLACE VIEW main.security.v_customer_reveal AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  main.security.thales_crdp_scalar_by_column_with_user(
    email_token,
    'reveal',
    'char',
    'email',
    session_user()
  ) AS email
FROM main.raw.customer_tokens;
```

Transform:

```sql
CREATE OR REFRESH MATERIALIZED VIEW customer_reveal_gold
AS
SELECT *
FROM main.security.v_customer_reveal;
```

Usage:

```sql
SELECT * FROM customer_reveal_gold;
```

Note:

- this gives the strongest governance boundary in the SQL/pipeline model
