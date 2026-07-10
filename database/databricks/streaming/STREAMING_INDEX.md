# Streaming and Lakeflow Examples

This folder contains the modernized streaming and Lakeflow examples for the
current integration project.

## Run Order

Use this order to avoid missing-object or wrong-runtime issues:

1. Create the base demo/source tables first.
   Typical starting points in this repo are:
   - [plaintext_setup.sql](E:\codex\work\thales.databricks.integration\notebooks\setup\plaintext_setup.sql:1)
   - [plaintext_setup_v2.py](E:\codex\work\thales.databricks.integration\notebooks\plaintext_setup_v2.py:1)

2. If you want governed reveal examples, deploy the UC Python functions/views
   first.
   Run:
   - [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\codex\work\thales.databricks.integration\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql:1)

3. For compute-cluster streaming ETL examples, run the streaming producer
   examples next on a compute cluster.
   Use:
   - [structured_streaming_java_udf_examples.py](E:\codex\work\thales.databricks.integration\streaming\structured_streaming_java_udf_examples.py:1)
   - [structured_streaming_python_helper_foreachbatch.py](E:\codex\work\thales.databricks.integration\streaming\structured_streaming_python_helper_foreachbatch.py:1)

4. After the protected source tables and/or governed reveal views exist, use
   the Lakeflow examples.
   Use:
   - [lakeflow_sql_examples.sql](E:\codex\work\thales.databricks.integration\streaming\lakeflow_sql_examples.sql:1)
   - [lakeflow_python_examples.py](E:\codex\work\thales.databricks.integration\streaming\lakeflow_python_examples.py:1)
   - [plaintext_protected_internal_lakeflow_examples.sql](E:\codex\work\thales.databricks.integration\streaming\plaintext_protected_internal_lakeflow_examples.sql:1)
   - [plaintext_protected_internal_lakeflow_python_examples.py](E:\codex\work\thales.databricks.integration\streaming\plaintext_protected_internal_lakeflow_python_examples.py:1)

## Where To Run

- `structured_streaming_*.py`
  Run on a compute cluster.

- `lakeflow_sql_examples.sql`
  Use as a Lakeflow / Declarative Pipelines SQL definition, not as a normal SQL
  Warehouse ad hoc script.

- `lakeflow_python_examples.py`
  Use as a Lakeflow / Declarative Pipelines Python definition.

- SQL Warehouse is still important for the governed UC setup step because that
  is where the persistent UC Python functions and optimized reveal views are
  created.

## Runtime Compatibility Notes

- The governed Lakeflow examples depend on the UC Python UDFs created in:
  [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\codex\work\thales.databricks.integration\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql:1)

- Those UC Python functions use `ENVIRONMENT.dependencies` to load the wheel.
  Databricks requires newer runtime support for that feature than the
  `14.3.x` compute cluster used in the benchmark work.

- Practical guidance:
  - On `DBR 14.3` compute clusters, use the compute-cluster streaming examples:
    - [structured_streaming_java_udf_examples.py](E:\codex\work\thales.databricks.integration\streaming\structured_streaming_java_udf_examples.py:1)
    - [structured_streaming_python_helper_foreachbatch.py](E:\codex\work\thales.databricks.integration\streaming\structured_streaming_python_helper_foreachbatch.py:1)
  - For the governed Lakeflow / UC reveal examples, use a compatible newer
    Databricks environment such as `DBR 16.2+` or a supported SQL/serverless
    environment.

Files:

- `structured_streaming_java_udf_examples.py`
  Compute-cluster Structured Streaming with stable scalar Java UDFs.
  Safe on the current `DBR 14.3` benchmark cluster.
- `structured_streaming_python_helper_foreachbatch.py`
  Compute-cluster Structured Streaming using the Python helper path through
  `foreachBatch`.
  Safe on the current `DBR 14.3` benchmark cluster.
- `lakeflow_sql_examples.sql`
  General governed Lakeflow SQL patterns using Unity Catalog functions/views.
  Not for the current `DBR 14.3` benchmark cluster when using the current UC
  Python UDF deployment with `ENVIRONMENT.dependencies`.
- `lakeflow_python_examples.py`
  General governed Lakeflow Python pipeline patterns.
  Not for the current `DBR 14.3` benchmark cluster when using the current UC
  Python UDF deployment with `ENVIRONMENT.dependencies`.
- `plaintext_protected_internal_lakeflow_examples.sql`
  Concrete Lakeflow SQL examples using the demo objects and optimized governed
  reveal views already created in this repo.
  Not for the current `DBR 14.3` benchmark cluster when using the current UC
  Python UDF deployment with `ENVIRONMENT.dependencies`.
- `plaintext_protected_internal_lakeflow_python_examples.py`
  Concrete Lakeflow Python examples using the demo objects and optimized
  governed reveal views already created in this repo.
  Not for the current `DBR 14.3` benchmark cluster when using the current UC
  Python UDF deployment with `ENVIRONMENT.dependencies`.
