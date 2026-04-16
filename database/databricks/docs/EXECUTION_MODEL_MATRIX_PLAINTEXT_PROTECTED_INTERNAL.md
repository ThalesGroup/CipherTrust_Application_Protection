# Databricks Execution Model Matrix - plaintext_protected_internal

This guide shows how the current implementation styles map to the
`my_catalog.my_schema.plaintext_protected_internal` example flow.

## Matrix

| # | Option | Runs on executors | Best use case | Example objects |
|---|---|---|---|---|
| 1 | Java Spark UDF on compute cluster | Yes | Protect/reveal in controlled cluster ETL and notebooks | `thales_reveal_by_column_with_user`, `temp_v_plaintext_protected_internal_reveal` |
| 2 | Python direct helper call | No, normally driver-side | Notebook diagnostics and small direct tests | `thales_crdp_python_function_bulk(...)` |
| 3 | Pandas UDF on compute cluster | Yes, in vectorized Python batches | Higher-volume Python batch processing when a notebook/job must stay Python-first | `pandas_udf`, `thales_crdp_python_function_bulk(...)` |
| 4 | Unity Catalog Python UDF | Managed Databricks SQL/runtime execution | SQL Warehouse and governed reveal access | `thales_reveal_by_column_uc_embedded`, `v_plaintext_protected_internal_reveal_uc_embedded` |
| 5 | Optimized UC Python UDF bundle | Managed Databricks SQL/runtime execution | Lower Databricks UDF overhead for array/batch reveal | `thales_reveal_bundle_by_columns_uc_embedded_optimized`, `v_plaintext_protected_internal_array_reveal_uc_embedded_optimized` |
| 6 | Lakeflow / streaming from secured UC views | Managed pipeline runtime or compute streaming read | Governed downstream consumption | `plaintext_protected_internal_reveal_gold`, `plaintext_protected_internal_reveal_flat_gold` |

## 1. Java Spark UDF on compute cluster

Where it runs:

- on Spark executors across partitions
- registered in the current Spark session

Use when:

- you want compute-cluster ETL or notebook testing
- you are running controlled admin or job workflows
- you want to work directly with session-scoped Java UDFs

Current example files:

- [databricks_compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\databricks_compute_cluster_udf_smoke_test.py)
- [compute_cluster_table_reveal_castback.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_table_reveal_castback.py)
- [compute_cluster_table_reveal_castback.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_table_reveal_castback.sql)

Example:

```sql
CREATE OR REPLACE TEMP VIEW temp_v_plaintext_protected_internal_reveal AS
SELECT
  custid,
  name,
  thales_reveal_by_column_with_user(CAST(address AS STRING), 'char', 'address', current_user()) AS address,
  thales_reveal_by_column_with_user(CAST(email AS STRING), 'char', 'email', current_user()) AS email,
  CAST(
    thales_reveal_by_column_with_user(CAST(creditcard AS STRING), 'nbr', 'creditcard', current_user())
    AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_column_with_user(CAST(creditcardcode AS STRING), 'nbr', 'creditcardcode', current_user())
    AS INT
  ) AS creditcardcode,
  thales_reveal_by_column_with_user(CAST(ssn AS STRING), 'nbr', 'ssn', current_user()) AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;
```

Important:

- these are session-scoped temp views
- they are best for testing, ETL, and controlled cluster use

## 2. Python direct helper call

Where it runs:

- in notebook Python / driver-side Python
- not distributed automatically

Use when:

- you want quick logic checks
- you want to debug one token or one small batch

Example:

```python
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk

result = thales_crdp_python_function_bulk(
    ["1002000950-18-9670"],
    "revealbulk",
    "nbr",
    "ssn",
    properties={
        "CRDPIP": "20.221.216.246",
        "CRDPPORT": "8090",
        "DEFAULTINTERNALNBRNBRPOLICY": "nbr-nbr-internal",
        "COLUMN_PROFILES": "ssn|tag.nbr.internal",
        "TAG.nbr.internal": "nbr-nbr-internal",
        "TAG.nbr.internal.policyType": "internal",
    },
    spark_session=spark,
)
print(result)
```

## 3. Pandas UDF on compute cluster

Where it runs:

- on Spark executors in vectorized Python batches
- still a Python execution model, but with better throughput than row-by-row Python UDFs

Use when:

- you want to stay in Python on the compute cluster
- you want higher-volume batch processing than a simple Python row UDF
- you are doing notebook/job experimentation rather than the primary governed SQL path

Example:

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf

from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk


@pandas_udf("string")
def reveal_ssn_batch(ssn_series: pd.Series) -> pd.Series:
    result = thales_crdp_python_function_bulk(
        ssn_series.tolist(),
        "revealbulk",
        "nbr",
        "ssn",
    )
    return pd.Series(result)


result_df = spark.table("my_catalog.my_schema.plaintext_protected_internal").select(
    "custid",
    reveal_ssn_batch("ssn").alias("ssn_revealed")
)
```

Important:

- this can improve Python batch throughput compared with a row-by-row Python UDF
- on compute clusters, this example assumes the helper loads `udfConfig.properties`
  from the cluster configuration and init-script workflow
- it is still not the main recommended governed access model for end users
- for customer-facing SQL access, the UC view path is still stronger

## 4. Unity Catalog Python UDF

Where it runs:

- in managed Databricks SQL/runtime execution
- persisted in Unity Catalog

Use when:

- you want SQL Warehouse access
- you want durable governed reveal views
- you want BI or downstream SQL consumers to query a stable view

Current example file:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)

Example objects:

- `my_catalog.my_schema.thales_reveal_by_column_uc_embedded`
- `my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded`
- `my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded`
- `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded`
- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded`

Best fit:

- primary governed SQL model
- best choice for SQL Warehouse and reusable views

SQL-Warehouse-style Python example:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
  value STRING,
  datatype STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk

PROPERTIES = {
    "CRDPIP": "20.221.216.246",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "external",
    "BADDATATAG": "999999999",
    "COLUMN_PROFILES": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.internal": "char-internal",
    "TAG.char.internal.policyType": "internal",
    "TAG.nbr.internal": "nbr-nbr-internal",
    "TAG.nbr.internal.policyType": "internal",
}

if value is None:
    return None

result = thales_crdp_python_function_bulk(
    [value],
    "revealbulk",
    datatype,
    column_name=column_name,
    reveal_user=reveal_user,
    properties=PROPERTIES,
)

return result[0] if result else None
$$;
```

Important:

- SQL Warehouse cannot rely on the compute-cluster init-script/local-file config model
- so the current working SQL Warehouse example embeds config in the UC Python function body
- the future alternative is the wheel-includes-properties path

## 5. Optimized UC Python UDF bundle

Where it runs:

- in managed Databricks SQL/runtime execution
- still a UC Python UDF path, but with fewer Databricks-side UDF invocations

Use when:

- you want the array/batch reveal pattern
- the standard UC array reveal view is functionally correct but slower than you want

Current example file:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)

Example objects:

- `my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized`
- `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized`
- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized`

Important:

- this reduces Databricks Python UDF calls
- it still makes one Thales bulk call per protected column inside the bundled function

## 6. Lakeflow / streaming from secured UC views

Where it runs:

- in Lakeflow Declarative Pipelines or streaming jobs that read governed UC views

Use when:

- you want downstream incremental processing on revealed data
- you want the reveal boundary to stay inside governed UC views

Current example file:

- [plaintext_protected_internal_lakeflow_examples.sql](E:\eclipse-workspace\thales.databricks.udf\streaming\plaintext_protected_internal_lakeflow_examples.sql)

Example objects:

- `plaintext_protected_internal_reveal_bronze`
- `plaintext_protected_internal_reveal_gold`
- `plaintext_protected_internal_reveal_flat_gold`

Best fit:

- easiest current way to test Lakeflow with this table
- reuses the SQL Warehouse reveal views that already work

## Simplest recommendation

If you only need one answer:

- for compute-cluster ETL or notebook testing, use the Java Spark UDF cast-back flow
- for durable governed SQL access, use the UC embedded reveal views
- for better SQL Warehouse array-view performance, use the optimized bundled UC view
- for Lakeflow, read from the governed UC reveal views rather than trying to persist cluster-scoped Java UDFs
