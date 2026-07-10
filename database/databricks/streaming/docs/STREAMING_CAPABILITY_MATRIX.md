# Streaming and Lakeflow Capability Matrix

This guide summarizes the main streaming and pipeline patterns supported by the
Thales CRDP Databricks solution.

## Matrix

| # | Option | Where it runs | Best use case | Recommended governance model |
|---|---|---|---|---|
| 1 | Structured Streaming with Java UDFs | Compute-cluster executors | High-throughput streaming ETL | Controlled jobs/admin use |
| 2 | Structured Streaming from secured UC view | Compute cluster reading UC view | Governed downstream streaming consumption | Preferred secured streaming pattern |
| 3 | Lakeflow / Declarative Pipelines with UC reveal views | Managed pipeline runtime | SQL-defined incremental pipelines around revealed data | Strong governed SQL model |
| 4 | Lakeflow / Declarative Pipelines reading optimized secured views | Managed pipeline runtime | Shared governed pipeline consumption with lower Databricks UDF overhead | Strongest boundary for reveal access |

## 1. Structured Streaming with Java UDFs

Setup:

```python
from pyspark.sql import types as T

spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column",
    "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnUdf",
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
    "thales_protect_by_object_and_column(email, 'char', "
    "'my_catalog.my_schema.plaintext_protected_internal', 'email') as email_token",
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
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    email_token,
    'my_catalog.my_schema.plaintext_protected_internal',
    'email',
    '/Volumes/my_catalog/my_schema/volume_forjars/config/udfConfig.properties',
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

## 3. Lakeflow / Declarative Pipelines with UC reveal views

Setup:

```sql
CREATE OR REFRESH STREAMING TABLE plaintext_protected_internal_reveal_bronze
AS
SELECT
  custid,
  name,
  address,
  city,
  state,
  zip,
  phone,
  email,
  dob,
  creditcard,
  creditcardcode,
  ssn
FROM STREAM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded;
```

Transform:

```sql
CREATE OR REFRESH MATERIALIZED VIEW plaintext_protected_internal_reveal_gold
AS
SELECT
  *
FROM plaintext_protected_internal_reveal_bronze;
```

Usage:

```sql
SELECT * FROM plaintext_protected_internal_reveal_gold;
```

Note:

- this is the easiest Lakeflow test path if you already deployed the governed
  Unity Catalog reveal views
- it keeps reveal logic behind governed UC views

## 4. Lakeflow / Declarative Pipelines reading optimized secured views

Setup:

```sql
CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized AS
SELECT
  custid,
  name,
  address,
  city,
  state,
  zip,
  phone,
  email,
  dob,
  creditcard,
  creditcardcode,
  ssn
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized;
```

Transform:

```sql
CREATE OR REFRESH MATERIALIZED VIEW plaintext_protected_internal_reveal_flat_gold
AS
SELECT *
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized;
```

Usage:

```sql
SELECT * FROM plaintext_protected_internal_reveal_flat_gold;
```

Note:

- this gives the strongest governance boundary in the SQL/pipeline model
- it also reuses the optimized bundled-array SQL Warehouse path

## Easiest way to test with `plaintext_protected_internal`

Recommended order:

1. deploy the embedded SQL Warehouse functions/views
2. validate:
   - `my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded`
3. optionally deploy the optimized SQL Warehouse views
4. run:
   - `streaming/plaintext_protected_internal_lakeflow_examples.sql`

Why this is the easiest path:

- it reuses the working SQL Warehouse reveal logic
- it avoids trying to make cluster-scoped Java UDF registrations durable inside
  Lakeflow
- it gives you a governed boundary first, then a pipeline test on top of that


## Current repo examples

- `streaming/structured_streaming_java_udf_examples.py`
- `streaming/structured_streaming_python_helper_foreachbatch.py`
- `streaming/lakeflow_sql_examples.sql`
- `streaming/lakeflow_python_examples.py`
- `streaming/plaintext_protected_internal_lakeflow_examples.sql`
- `streaming/plaintext_protected_internal_lakeflow_python_examples.py`
