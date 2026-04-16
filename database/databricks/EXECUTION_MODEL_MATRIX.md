# Databricks Execution Model Matrix

This guide clarifies where each implementation style runs and when to use it.

## Matrix

| # | Option | Runs on executors | Best use case | Notes |
|---|---|---|---|---|
| 1 | Java Spark UDF (`UDF1`/`UDF2`/etc.) | Yes | High-performance compute-cluster ETL | Lowest overhead, strongest Spark fit in this project |
| 2 | Python direct helper call | No, normally driver-side | Notebook testing, controlled Python workflows, small direct calls | Not distributed by itself |
| 3 | Python Spark UDF | Yes | Cluster notebooks/jobs when Python implementation is preferred | Easier to write than Java, higher overhead |
| 4 | Pandas UDF | Yes | Higher-volume Python batch/vectorized processing | Vectorized, often better than row-by-row Python UDFs |
| 5 | Unity Catalog Python UDF | Managed Databricks SQL/runtime execution | SQL Warehouse, governed SQL access, views, BI, DLT/Lakeflow | Best governed database-style model |

## 1. Java Spark UDF

Where it runs:

- on Spark executors across partitions
- registered once, then invoked by Spark SQL or DataFrame operations

Use when:

- you want the strongest cluster ETL performance
- you want Spark-native parallel execution

Example:

```python
from pyspark.sql import types as T

# Step 1: register the Java UDF.
spark.udf.registerJavaFunction(
    "thales_protect_by_column",
    "ThalesCrdpProtectByColumnUdf",
    T.StringType(),
)

# Step 2: use it in a DataFrame transformation for ETL protection.
source_df = spark.table("main.raw.customer_cleartext")
result_df = source_df.selectExpr(
    "customer_id",
    "first_name",
    "last_name",
    "customer_status",
    "created_ts",
    "thales_protect_by_column(email, 'char', 'email') as email_token"
)

# Step 3: write the protected result.
result_df.write.mode("overwrite").saveAsTable("main.raw.customer_tokens")
```

ETL note:

- this is the strongest compute-cluster fit in the project
- especially appropriate for protect/tokenize pipelines where no runtime user
  parameter is required

## 2. Python direct helper call

Where it runs:

- in the notebook Python process or driver-side Python context
- not distributed across executors unless you explicitly embed it in distributed work

Use when:

- you want quick notebook testing
- you want a small direct Python call
- you want to validate logic before using a governed SQL or Spark path

Example:

```python
from thales_databricks_udf.crdp_udfs import *

# Step 1: prepare input values in Python.
token_values = ["A9K2exampletoken", "B1M4exampletoken"]

# Step 2: call the secure helper directly.
secure_reveal_results = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
    spark_session=spark,
)

# Step 3: use the returned Python values.
print(secure_reveal_results)
```

Important:

- `spark_session=spark` is used for identity lookup
- it does not automatically make the call executor-distributed

## 3. Python Spark UDF

Where it runs:

- on executors as part of Spark execution

Use when:

- you want Python implementation inside distributed Spark jobs
- Java is not required and extra overhead is acceptable

Conceptual example:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Step 1: define the Python function.
def protect_email(email):
    return thales_crdp_python_function_bulk_secure(
        [email],
        "protectbulk",
        "char",
        "email",
        spark_session=spark,
    )[0]

# Step 2: register the Spark UDF.
protect_email_udf = udf(protect_email, StringType())

# Step 3: use it in a DataFrame transformation.
result_df = spark.table("main.raw.customer_cleartext").withColumn("email_token", protect_email_udf("email"))
```

Note:

- this is conceptually possible, but in practice be careful with session access
  patterns and per-row overhead
- in this project, Java UDFs or UC Python functions are usually better

## 4. Pandas UDF

Where it runs:

- on executors in vectorized batches

Use when:

- you want Python batch processing with vectorized semantics
- you need better throughput than row-by-row Python UDFs

Conceptual example:

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf

# Step 1: define the vectorized Pandas UDF.
@pandas_udf("string")
def protect_email_batch(email_series: pd.Series) -> pd.Series:
    protected = thales_crdp_python_function_bulk_secure(
        email_series.tolist(),
        "protectbulk",
        "char",
        "email",
    )
    return pd.Series(protected)

# Step 2: use it in a DataFrame transformation.
result_df = spark.table("main.raw.customer_cleartext").withColumn("email_token", protect_email_batch("email"))
```

Note:

- this is more efficient than a row UDF, but still a Python-distributed model
- governance is usually weaker than the secured SQL view pattern

## 5. Unity Catalog Python UDF

Where it runs:

- in managed Databricks SQL/runtime execution for the function
- SQL-facing, not the same as a direct notebook helper call

Use when:

- you want SQL Warehouse support
- you want BI-friendly SQL objects
- you want secured views and grants as the primary access model

Example:

```sql
-- Step 1: create the Unity Catalog Python function.
CREATE OR REPLACE FUNCTION main.security.thales_crdp_bulk_by_column(
  values ARRAY<STRING>,
  mode STRING,
  datatype STRING,
  column_name STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
ENVIRONMENT (
dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk_secure
return thales_crdp_python_function_bulk_secure(values, mode, datatype, column_name)
$$;

-- Step 2: create a secured view.
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

-- Step 3: end users query the view.
SELECT customer_id, email
FROM main.security.v_customer_reveal;
```

## Simplest recommendation

If you only need one answer:

- for compute-cluster ETL, use Java Spark UDFs
- for SQL Warehouse and governed BI access, use Unity Catalog Python UDFs plus secured views
- for quick Python testing, use the secure direct Python helper on the driver

## Important security clarification

If you do not want regular users to choose or influence the reveal identity:

- do not expose direct `*_with_user` function calls as the user-facing API
- do not rely on notebook users to call `current_user()` correctly
- use secured views as the supported access path

In practice:

- SQL Warehouse / Unity Catalog is the strongest governed model for this
- compute-cluster direct Java UDFs are best treated as ETL/admin tooling unless
  you put a tighter governed layer in front of them
