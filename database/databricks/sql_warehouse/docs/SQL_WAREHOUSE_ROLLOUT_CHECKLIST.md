# SQL Warehouse Rollout Checklist

Use this checklist for the permanent Unity Catalog / SQL Warehouse deployment path.

## Artifacts

- Wheel to upload:
  - `E:\eclipse-workspace\thales.databricks.udf\dist\thales_databricks_udf-0.1.7-py3-none-any.whl`
- Main deployment script for `plaintext_protected_internal`:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
- Optional optimized deployment script:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
- Memory sizing note for the optimized path:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\OPTIMIZED_UDF_MEMORY_GUIDANCE.md`
- Future wheel-includes-properties option:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`
- SQL Warehouse TLS debug helper:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_debug_uc_function.sql`
- Embedded-config generator:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_embedded_config_sql_from_properties.py`

## Target UC volume path

- Upload the wheel to:
  - `/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.7-py3-none-any.whl`

## Deployment steps

1. Upload the wheel to the UC volume path above.
2. Open a Pro or Serverless SQL Warehouse.
3. Open the SQL editor attached to that warehouse.
4. Run:
   - `USE CATALOG my_catalog;`
   - `USE SCHEMA my_schema;`
5. Run the full script:
   - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
6. If you want the lower-overhead bundled array path, also run:
   - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
   - review `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\docs\OPTIMIZED_UDF_MEMORY_GUIDANCE.md` before changing batch size assumptions
7. Replace `your_group` in the script before running the `GRANT` statements.

## TLS-specific rollout notes

- For SQL Warehouse TLS, do not rely on:
  - `/tmp/thales_config/...`
  - `/Volumes/...` cert/key paths passed directly to `requests`
- Use the embedded-config generator to embed:
  - `CRDP_CA_CERT_PEM_B64`
  - `CRDP_CLIENT_CERT_PEM_B64`
  - `CRDP_CLIENT_KEY_PEM_B64`
- Re-run the generator whenever the CA, client cert, or client key changes.
- If `crdp_udfs.py` changes, upload the new wheel version and rerun the SQL
  deployment script.

## What the scripts create

- Main embedded-config objects:
  - `my_catalog.my_schema.thales_reveal_by_object_and_column_uc_embedded`
  - `my_catalog.my_schema.thales_reveal_bulk_by_object_and_column_uc_embedded`
  - `my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded`
  - `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded`
  - `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded`
- Optional optimized bundled-array objects:
  - `my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized`
  - `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized`
  - `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized`

## Validation queries

Run these after deployment:

```sql
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized LIMIT 10;
```

## Optional TLS diagnostics

If SQL Warehouse TLS behavior is unclear, use:

- `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\samples\sample_tls_debug_uc_function.sql`

Paste the same generated TLS `PROPERTIES` block into that sample and run it to
confirm the warehouse runtime can:

- see the embedded base64 TLS properties
- materialize local temp files
- load the CA bundle
- load the client cert/key pair

## Expected behavior

- Internal tokens are treated as complete stored values.
- External policies use `external_version`.
- Numeric token values are revealed as `STRING` in the UC function layer.
- Numeric columns are cast back in the UC view layer, for example:
  - `DECIMAL(25,0)` for `creditcard`
  - `INT` for `creditcardcode`

## Re-deploy checklist after code changes

If `crdp_udfs.py` changes:

1. Rebuild the wheel.
2. Upload the new wheel to the UC volume.
3. Re-run the UC function/view deployment script.
4. Re-test the validation queries.
