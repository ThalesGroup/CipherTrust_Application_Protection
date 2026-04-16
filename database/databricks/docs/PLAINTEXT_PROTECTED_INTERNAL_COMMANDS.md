# plaintext_protected_internal Command Guide

This file collects the main commands and runnable scripts for the
`my_catalog.my_schema.plaintext_protected_internal` use case in one place.

It is the practical companion to:

- [EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md](/E:/eclipse-workspace/thales.databricks.udf/docs/EXECUTION_MODEL_MATRIX_PLAINTEXT_PROTECTED_INTERNAL.md)

## What This Covers

It includes the current commands/scripts for:

1. compute-cluster smoke testing
2. compute-cluster plaintext table setup
3. compute-cluster reveal temp views
4. compute-cluster pandas UDF example
5. SQL Warehouse embedded-config deployment
6. SQL Warehouse optimized bundled-array deployment
7. SQL Warehouse future wheel-includes-properties deployment
8. Lakeflow examples based on the governed UC views

## 1. Compute Cluster Smoke Test

Use this first because it does not require an existing protected customer table.

Run:

- [databricks_compute_cluster_udf_smoke_test.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/databricks_compute_cluster_udf_smoke_test.py)

Cluster prerequisites are documented here:

- [TEST_RUNBOOK.md](/E:/eclipse-workspace/thales.databricks.udf/TEST_RUNBOOK.md)

Important cluster Spark config:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Important environment variables:

```text
UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
JNAME=zulu11-ca-amd64
```

Required init script:

```text
/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh
```

## 2. Compute Cluster Plaintext Table Setup

Use this to create and load a sample plaintext table for the
`plaintext_protected_internal` schema.

Run:

- [compute_cluster_plaintext_protected_internal_setup.sql](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_plaintext_protected_internal_setup.sql)

This creates:

- `my_catalog.my_schema.plaintext_protected_internal`

Important:

- this loads readable plaintext seed data
- the reveal examples expect protected/tokenized data
- so after loading plaintext, you still need your protection/load process to populate protected values before running reveal examples

## 3. Compute Cluster Reveal Example

Current recommended compute-cluster table/view example:

- [compute_cluster_table_reveal_castback.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_table_reveal_castback.py)
- [compute_cluster_table_reveal_castback.sql](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_table_reveal_castback.sql)

This pattern:

- uses Java Spark UDFs registered in the current session
- creates temp views
- reveals string/numeric protected data
- casts numeric values back after reveal

Main temp views created:

- `temp_v_plaintext_protected_internal_reveal`
- `temp_v_plaintext_protected_internal_array_reveal`
- `temp_v_plaintext_final_reveal_flat`

Representative row-reveal command:

```sql
CREATE OR REPLACE TEMP VIEW temp_v_plaintext_protected_internal_reveal AS
SELECT
  custid,
  name,
  thales_reveal_by_column_with_user(
    CAST(address AS STRING),
    'char',
    'address',
    current_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_reveal_by_column_with_user(
    CAST(email AS STRING),
    'char',
    'email',
    current_user()
  ) AS email,
  dob,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(creditcard AS STRING),
      'nbr',
      'creditcard',
      current_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(creditcardcode AS STRING),
      'nbr',
      'creditcardcode',
      current_user()
    ) AS INT
  ) AS creditcardcode,
  thales_reveal_by_column_with_user(
    CAST(ssn AS STRING),
    'nbr',
    'ssn',
    current_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;
```

## 4. Compute Cluster Pandas UDF Example

If you want a Python-first vectorized example on the compute cluster, use a
Pandas UDF pattern like this:

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

Use this when:

- you want vectorized Python batch processing on the compute cluster
- you want something faster than a row-by-row Python UDF
- you do not need the stronger governed SQL Warehouse access pattern

Important:

- for compute cluster, this example assumes `udfConfig.properties` is already
  available through the cluster config and init script
- it intentionally does not inline a `properties` dictionary

## 5. SQL Warehouse Python UDF Example

For SQL Warehouse, use the embedded-config or wheel-includes-properties model,
not the compute-cluster file-based config model.

Representative current SQL Warehouse example:

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

Use this when:

- you want permanent UC functions and governed views
- you are deploying on SQL Warehouse
- the function must carry its own config because it cannot rely on the compute-cluster init-script model

## 6. Compute Cluster Debug Notebook

If you need deeper troubleshooting for this table-specific workflow, use:

- [databricks_compute_cluster_udf_plaintext_protected_internal_debug.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/databricks_compute_cluster_udf_plaintext_protected_internal_debug.py)

This is a debug notebook, not the main supported customer example.

## 7. SQL Warehouse Embedded-Config Deployment

Current main SQL Warehouse deployment script:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)

Use this when:

- you want permanent Unity Catalog functions and views
- the SQL UDF body embeds the relevant config as a `PROPERTIES` dictionary

Main created objects:

- `my_catalog.my_schema.thales_reveal_by_column_uc_embedded`
- `my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded`
- `my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded`
- `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded`
- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded`

Validation:

```sql
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded LIMIT 10;
```

## 8. SQL Warehouse Optimized Bundled-Array Deployment

Optional performance-oriented SQL Warehouse script:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)

Use this when:

- the standard array reveal view works
- but Databricks Python UDF overhead is too high

Main created objects:

- `my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized`
- `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized`
- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized`

Validation:

```sql
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized LIMIT 10;
```

Memory/performance note:

- [OPTIMIZED_UDF_MEMORY_GUIDANCE.md](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/OPTIMIZED_UDF_MEMORY_GUIDANCE.md)

## 9. SQL Warehouse Future Wheel-Includes-Properties Deployment

Future/optional script:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql)

Use this only when:

- the wheel itself already contains the packaged properties/config resource
- `crdp_udfs.py` can load that packaged config from inside the wheel
- you do not want to embed a `PROPERTIES` dictionary in the SQL UDF body

## 10. Lakeflow / Streaming Example

Lakeflow example using the governed UC reveal views:

- [plaintext_protected_internal_lakeflow_examples.sql](/E:/eclipse-workspace/thales.databricks.udf/streaming/plaintext_protected_internal_lakeflow_examples.sql)

Example pipeline objects:

- `plaintext_protected_internal_reveal_bronze`
- `plaintext_protected_internal_reveal_gold`
- `plaintext_protected_internal_reveal_flat_gold`

## Recommended Run Order

### Compute Cluster

1. Run [databricks_compute_cluster_udf_smoke_test.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/databricks_compute_cluster_udf_smoke_test.py)
2. Run [compute_cluster_plaintext_protected_internal_setup.sql](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_plaintext_protected_internal_setup.sql) if you need sample plaintext input
3. Protect/load the table so it contains tokens
4. Run [compute_cluster_table_reveal_castback.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_table_reveal_castback.py) or [compute_cluster_table_reveal_castback.sql](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_table_reveal_castback.sql)
5. Use [databricks_compute_cluster_udf_plaintext_protected_internal_debug.py](/E:/eclipse-workspace/thales.databricks.udf/notebooks/databricks_compute_cluster_udf_plaintext_protected_internal_debug.py) only if debugging is needed

### SQL Warehouse

1. Upload the wheel to the UC volume
2. Run [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
3. Optionally run [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)
4. Validate the reveal views
5. If later needed, evaluate the wheel-includes-properties variant

## One-Line Summary

If you want one current command family for `plaintext_protected_internal`, use:

- compute cluster: [compute_cluster_table_reveal_castback.sql](/E:/eclipse-workspace/thales.databricks.udf/notebooks/compute_cluster_table_reveal_castback.sql)
- SQL Warehouse: [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
