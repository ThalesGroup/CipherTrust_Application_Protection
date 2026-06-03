# Databricks SQL Warehouse Deployment Guide

This guide packages and deploys the Thales CRDP Databricks Python helpers for
Unity Catalog Python functions on Databricks SQL warehouses.

For the full runtime-by-runtime TLS split, see
[DATABRICKS_TLS_RUNTIME_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\docs\DATABRICKS_TLS_RUNTIME_GUIDE.md).

## When to use this path

Use this deployment model when you want:

- Databricks SQL queries, dashboards, or BI tools to call CRDP functions
- Unity Catalog-governed shared functions
- a warehouse-friendly alternative to Java compute-cluster UDF adapters

Use the compute-cluster Java adapters when your primary workload is high-volume
Spark ETL on all-purpose or job clusters.

Important TLS reminder:

- compute-cluster Java, compute-cluster Python, and SQL Warehouse do not share
  one cert-loading model
- this guide documents the SQL Warehouse pattern only

## Databricks requirements

Based on current Databricks documentation:

- Python scalar UDFs created with `CREATE FUNCTION ... LANGUAGE PYTHON` require
  Unity Catalog
- they are supported on Databricks SQL and Databricks Runtime 14.1 and above
- Python UDFs require a Pro SQL warehouse or a Unity Catalog-enabled compute
  resource
- custom wheel dependencies can be attached with the `ENVIRONMENT` clause

## Artifacts in this project

- Core Python helper:
  - `python/thales_databricks_udf/crdp_udfs.py`
- Active deployment scripts:
  - `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`
  - `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
  - `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
- Sample/reference scripts:
  - `sql_warehouse/samples/sample_create_uc_secure_views.sql`
  - `sql_warehouse/samples/sample_grant_uc_secure_views.sql`
  - `sql_warehouse/samples/sample_thales_crdp_python_udf_imports.py`
  - `sql_warehouse/samples/sample_tls_debug_uc_function.sql`
- Generator utilities:
  - `sql_warehouse/utils/generate_embedded_config_sql_from_properties.py`
  - `sql_warehouse/utils/generate_reveal_views_from_properties.py`
- Legacy reference scripts:
  - `sql_warehouse/legacy/legacy_create_uc_functions_built_wheel.sql`
  - `sql_warehouse/legacy/legacy_thales_crdp_uc_function_templates.sql`

## Secure Python entry points

The Python package supports a production-safe API and a flexible testing API.

Production-safe:

- `thales_crdp_python_function_bulk_secure(...)`
- `thales_crdp_python_function_bulk_secure_legacy(...)`

Testing/flexible:

- `thales_crdp_python_function_bulk(...)`
- `thales_crdp_python_function_bulk_legacy(...)`

Recommended production notebook usage:

```python
from thales_databricks_udf.crdp_udfs import *

results = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
    spark_session=spark,
)
```

How reveal-user resolution works in the secure API:

- it does not accept a caller-provided `reveal_user`
- it first tries `session_user()` / `current_user()` through the provided Spark session
- if `spark_session` is omitted, it tries to find the active Spark session automatically
- if that fails, it tries Databricks notebook context
- only then does it fall back to config/default values

If the fifth positional value is omitted and you call:

```python
results = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
)
```

the function still attempts to find the active Spark session automatically.

If a caller tries something like:

```python
results = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
    "fred",
)
```

the call is rejected because the secure API requires `properties` and
`spark_session` to be passed by keyword. This prevents positional user-override
attempts.

## Script roles

- `create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`
  - keep this for the future path where the wheel itself already includes the packaged properties/config resource
- `create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
  - main current script for the `plaintext_protected_internal` example with embedded admin-managed config
- `create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
  - optimized version of the same table-specific path that reduces Databricks Python UDF calls on the array view
- `sample_create_uc_secure_views.sql` and `sample_grant_uc_secure_views.sql`
  - sample wrapper/grant patterns for teams that already created their UC functions
- `legacy_create_uc_functions_built_wheel.sql`
  - older concrete example with hard-coded names and settings
- `legacy_thales_crdp_uc_function_templates.sql`
  - older placeholder-based template for manual customization
- `sample_thales_crdp_python_udf_imports.py`
  - tiny sample showing what the Python helper module exports for notebook-level experiments

When deciding between the two legacy files:

- use `legacy_create_uc_functions_built_wheel.sql` if you want a concrete example that already has object names and wheel dependency wiring
- use `legacy_thales_crdp_uc_function_templates.sql` if you want a generic placeholder template to copy for another catalog/schema/policy set

## Deployment overview

1. Build the Python wheel locally.
2. Upload the wheel to a Unity Catalog volume.
3. Choose the SQL deployment script that matches your config strategy.
4. Run the `CREATE OR REPLACE FUNCTION` statements in Databricks SQL.
5. Create the secured wrapper views that inject `session_user()`.
6. Grant consumers access to the secured views.
7. Validate protect and reveal behavior from the SQL warehouse.

## Step 1: Build the wheel

From this workspace root:

```powershell
py -m build --no-isolation
```

Expected output artifact:

- `dist/thales_databricks_udf-0.1.7-py3-none-any.whl`
- `dist/thales_databricks_udf-0.1.1.tar.gz`

If your environment does not already have the build tool:

```powershell
py -m pip install build setuptools wheel
py -m build --no-isolation
```

Windows note:

- in this environment, `py` worked while `python` still resolved to the
  Microsoft Store alias
- `--no-isolation` avoided local virtual-environment permission issues during
  the build

## Step 2: Upload the wheel to Unity Catalog volume storage

Upload the wheel to a Unity Catalog volume path such as:

```text
/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.7-py3-none-any.whl
```

This volume path is referenced by the SQL template using the Python UDF
`ENVIRONMENT` clause.

## Step 3: Choose the SQL deployment script

Recommended current path for the working example table:

- `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`

Use the optimized companion if you want fewer Databricks Python UDF calls on
the array view:

- `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
- `sql_warehouse/docs/OPTIMIZED_UDF_MEMORY_GUIDANCE.md`

Keep this packaged-config script for future use if config is later bundled in
the wheel:

- `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`

Recommended maintenance pattern for embedded config:

- treat the checked-in embedded-config SQL files as reviewed templates/examples
- generate environment-specific copies from `udfConfig.properties` instead of
  hand-editing host, port, TLS, and cert/key settings inside the SQL directly
- use:
  - `sql_warehouse/utils/generate_embedded_config_sql_from_properties.py`

Legacy/manual-customization references:

- `sql_warehouse/legacy/legacy_create_uc_functions_built_wheel.sql`
- `sql_warehouse/legacy/legacy_thales_crdp_uc_function_templates.sql`

## Step 4: Create the functions in Databricks SQL

Run the chosen SQL script in a Databricks SQL editor attached to the target
warehouse.

For the current `plaintext_protected_internal` rollout, use:

- `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`

Optional performance-oriented follow-up:

- `sql_warehouse/deploy/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`

If you want the bundled-array memory sizing guidance and worked example for
`plaintext_protected_internal`, also review:

- `sql_warehouse/docs/OPTIMIZED_UDF_MEMORY_GUIDANCE.md`

### Optional pre-step: Generate an environment-specific embedded-config SQL file

If your SQL Warehouse rollout needs current CRDP host, port, TLS, CA, or
client-cert settings from `udfConfig.properties`, generate a stamped SQL file
first instead of editing the embedded `PROPERTIES` block by hand.

Use:

- `sql_warehouse/utils/generate_embedded_config_sql_from_properties.py`

What it does:

- reads active values from `udfConfig.properties`
- renders a Python `PROPERTIES = {...}` block
- replaces every embedded-config block in the chosen SQL template
- writes a generated `.sql` file for review before execution

Suggested settings in that generator:

- `PROPERTIES_PATH`
  - your canonical property file
- `TEMPLATE_SQL_PATH`
  - the checked-in embedded-config SQL template to stamp
- `OUTPUT_SQL_PATH`
  - a generated output path such as `C:\tmp\generated_...sql`
- `SQL_WAREHOUSE_CA_CERT_SOURCE_PATH`
  - local/source CA PEM file to embed as `CRDP_CA_CERT_PEM_B64`
- `SQL_WAREHOUSE_CLIENT_CERT_SOURCE_PATH`
  - local/source client certificate PEM file to embed as `CRDP_CLIENT_CERT_PEM_B64`
- `SQL_WAREHOUSE_CLIENT_KEY_SOURCE_PATH`
  - local/source client private-key PEM file to embed as `CRDP_CLIENT_KEY_PEM_B64`
- `WHEEL_DEPENDENCY_PATH_OVERRIDE`
  - optional dependency override when you want the generated SQL to point at a
    specific wheel filename/version

Recommended SQL Warehouse pattern:

- do not assume SQL Warehouse can see a compute cluster's `/tmp/thales_config`
- do not assume SQL Warehouse can use `/Volumes/...` TLS file paths directly in
  `requests`
- prefer embedding the config values directly
- for SQL Warehouse TLS, prefer embedding cert material as:
  - `CRDP_CA_CERT_PEM_B64`
  - `CRDP_CLIENT_CERT_PEM_B64`
  - `CRDP_CLIENT_KEY_PEM_B64`
- the Python helper writes those bytes to local temp files at runtime before
  configuring `requests`
- this is the working SQL Warehouse TLS pattern validated in this project

## Step 5: Create secured wrapper views

After the functions exist, create governed reveal views that inject the active
Databricks identity with `session_user()`.

If you want sample secure-view patterns separate from the main deployment
scripts, use:

- `sql_warehouse/samples/sample_create_uc_secure_views.sql`

This pattern is recommended because it:

- hides the `reveal_user` parameter from analysts and BI tools
- centralizes allowed reveal use cases by table and column
- lets you grant access to views instead of direct access to `*_with_user`
  functions

## Roles and grants matrix

| Role | Typical privileges | Why |
|---|---|---|
| `thales_udf_deployers` | `USE CATALOG`, `USE SCHEMA`, `CREATE FUNCTION`, create view capability, `SELECT` on source tables, `EXECUTE` on UC functions for validation | Creates and validates the functions and secured views |
| `pii_consumers` | `USE CATALOG`, `USE SCHEMA`, `SELECT` on secured views | Reads revealed data only through governed views |
| Raw-table owners | ownership or managed `SELECT` on `main.raw.*` | Controls the underlying tokenized source tables |

Recommended least-privilege pattern:

- grant end users `SELECT` on the secured views
- do not grant end users direct `EXECUTE` on the `*_with_user` functions
- keep direct access to `main.raw` tables narrower than view access where possible

## Code visibility

End users typically interact with:

- function names
- view names
- granted SQL objects

For Unity Catalog SQL/Python functions, Databricks metadata commands such as
`DESCRIBE FUNCTION EXTENDED` can show the stored function body. For the wheel-
backed bulk functions in this project, that body is typically just a short
import-and-call wrapper, not the full implementation source.

The underlying Python package source in the wheel is separate from the SQL
function body. In practice, users would generally need access to the wheel
artifact location or other package distribution access to inspect the packaged
module contents directly. This is an inference from the Databricks function
metadata behavior and the fact that the implementation is loaded through the
`ENVIRONMENT` dependency path rather than stored inline in the SQL body.

## Step 6: Grants

Before validation, grant access to the secured views.

If you want sample grant statements separate from the main deployment scripts,
use:

- `sql_warehouse/samples/sample_grant_uc_secure_views.sql`

Recommended least-privilege model:

- grant `USE CATALOG` and `USE SCHEMA` to consumer groups
- grant `SELECT` on the secured views
- do not grant direct `EXECUTE` on the `*_with_user` functions to end users
- allow only deployers/admins to create functions and views

## Step 7: Validate the deployment

Start with protect and reveal smoke tests.

Scalar example:

```sql
SELECT <catalog>.<schema>.thales_crdp_scalar_by_column(
  'alice@example.com',
  'protect',
  'char',
  'email'
) AS protected_email;
```

Bulk example:

```sql
SELECT <catalog>.<schema>.thales_crdp_bulk_by_column(
  array('alice@example.com', 'bob@example.com'),
  'protectbulk',
  'char',
  'email'
) AS protected_batch;
```

Secure reveal example:

```sql
SELECT <catalog>.<schema>.thales_crdp_scalar_by_column_with_user(
  token_col,
  'reveal',
  'char',
  'email',
  session_user()
)
FROM some_table;
```

## Security guidance

Recommended production pattern:

- use `*_with_user` only behind governed views, SQL wrappers, or curated
  semantic objects
- inject `session_user()` or `current_user()` in SQL instead of letting BI
  users pass an arbitrary username
- use column-aware functions for production rollout so policy selection is
  controlled centrally
- treat reveal as non-deterministic because authorization and group membership
  can change over time

## Performance guidance

- use bulk functions where possible instead of row-by-row reveal or protect
- remember CRDP v1 bulk calls must use one protection profile per request
- keep Databricks SQL warehouses network-close to CRDP where possible
- use the Java compute-cluster path for the highest-throughput Spark ETL jobs

## Troubleshooting

If function creation fails:

- verify the warehouse supports Unity Catalog Python UDFs
- verify the target catalog and schema exist
- verify the wheel path is a valid Unity Catalog volume path
- verify the SQL body still contains valid Python indentation after edits

If runtime import fails for bulk functions:

- verify the wheel file was uploaded successfully
- verify `<UC_WHEEL_PATH>` points to the exact wheel filename
- recreate the function after changing dependency paths

If reveal behavior is denied or inconsistent:

- verify the effective Databricks user returned by `session_user()`
- verify CRDP policy membership and reveal-user authorization
- verify external versus internal metadata handling for the selected profile

If SQL Warehouse TLS is being introduced or changed:

- regenerate the embedded-config SQL after updating any cert or key file
- upload a fresh wheel filename/version when `crdp_udfs.py` changes
- prefer the base64-embedded TLS material pattern over `/tmp/...` or
  `/Volumes/...` TLS file paths
- if needed, use:
  - `sql_warehouse/samples/sample_tls_debug_uc_function.sql`
  to confirm the warehouse runtime can:
  - decode the embedded TLS properties
  - write temp files
  - load the CA bundle
  - load the client cert/key pair

## Related files

- `README.md`
- `DEPLOYMENT.md`
- `sql_warehouse/samples/sample_thales_crdp_python_udf_imports.py`
- `sql_warehouse/legacy/legacy_thales_crdp_uc_function_templates.sql`
- `sql_warehouse/legacy/legacy_create_uc_functions_built_wheel.sql`
- `sql_warehouse/samples/sample_create_uc_secure_views.sql`
- `sql_warehouse/samples/sample_grant_uc_secure_views.sql`
- `sql_warehouse/utils/generate_embedded_config_sql_from_properties.py`
- `sql_warehouse/samples/sample_tls_debug_uc_function.sql`
## View generator

If you want help generating persistent reveal-view SQL from
`protect.object.<catalog>.<schema>.<table>` mappings, use:

- [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)

Run-location note:

- this generator produces SQL Warehouse / Unity Catalog view SQL
- but it must be executed from a Python-capable Databricks cluster notebook
- do not run it inside a SQL Warehouse notebook, because SQL Warehouses execute SQL cells only

Why this lives under the SQL Warehouse path:

- SQL Warehouse / Unity Catalog functions are persistent
- the reveal views built on top of them can also be persistent
- by contrast, the compute-cluster Java UDF path uses session-scoped UDF registrations
- reveal views that depend on those Java UDFs must therefore be session `TEMP VIEW`s
- that makes a separate persistent-view generator a poor fit for the compute-cluster path

