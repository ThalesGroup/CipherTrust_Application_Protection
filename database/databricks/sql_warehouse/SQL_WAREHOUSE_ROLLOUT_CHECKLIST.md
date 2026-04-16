# SQL Warehouse Rollout Checklist

Use this checklist for the permanent Unity Catalog / SQL Warehouse deployment path.

## Artifacts

- Wheel to upload:
  - `E:\eclipse-workspace\thales.databricks.udf\dist\thales_databricks_udf-0.1.1-py3-none-any.whl`
- Main deployment script for `plaintext_protected_internal`:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
- Optional optimized deployment script:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
- Memory sizing note for the optimized path:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\OPTIMIZED_UDF_MEMORY_GUIDANCE.md`
- Future wheel-includes-properties option:
  - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`

## Target UC volume path

- Upload the wheel to:
  - `/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl`

## Deployment steps

1. Upload the wheel to the UC volume path above.
2. Open a Pro or Serverless SQL Warehouse.
3. Open the SQL editor attached to that warehouse.
4. Run:
   - `USE CATALOG my_catalog;`
   - `USE SCHEMA my_schema;`
5. Run the full script:
   - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`
6. If you want the lower-overhead bundled array path, also run:
   - `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`
   - review `E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\OPTIMIZED_UDF_MEMORY_GUIDANCE.md` before changing batch size assumptions
7. Replace `your_group` in the script before running the `GRANT` statements.

## What the scripts create

- Main embedded-config objects:
  - `my_catalog.my_schema.thales_reveal_by_column_uc_embedded`
  - `my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded`
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
