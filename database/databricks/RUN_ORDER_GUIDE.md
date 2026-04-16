# Databricks Run Order Guide

This guide gives the recommended file-by-file run order for the two supported
deployment models in this project:

- Databricks SQL Warehouse / Unity Catalog Python functions
- Databricks compute clusters / Java Spark UDFs

## Choose the right path

Use SQL Warehouse when you want:

- Databricks SQL access
- BI/dashboard integration
- Unity Catalog governed shared functions and views

Use compute clusters when you want:

- Spark ETL and batch execution
- executor-parallel Java UDF execution
- notebook/job-driven processing on clusters

## SQL Warehouse run order

1. Build the Python wheel locally.

   File:
   - `pyproject.toml`

   Command:

   ```powershell
   py -m build --no-isolation
   ```

   Expected artifact:
   - `dist/thales_databricks_udf-0.1.1-py3-none-any.whl`

2. Upload the wheel to a Unity Catalog volume.

   Example:
   - `/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl`

3. Review the deployment guide.

   File:
   - `sql_warehouse/SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md`

4. Create the Unity Catalog functions.

   Preferred current file for `plaintext_protected_internal`:
   - `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql`

   Optional optimized companion:
   - `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql`

   Future packaged-config option:
   - `sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_wheel_includes_properties.sql`

   Legacy concrete reference:
   - `sql_warehouse/legacy_create_uc_functions_built_wheel.sql`

   Legacy generic template:
   - `sql_warehouse/legacy_thales_crdp_uc_function_templates.sql`

5. Create the secured wrapper views.

   File:
   - `sql_warehouse/sample_create_uc_secure_views.sql`

6. Apply grants.

   File:
   - `sql_warehouse/sample_grant_uc_secure_views.sql`

7. Validate.

   Example checks:

   ```sql
   SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded LIMIT 10;
   SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded LIMIT 10;
   SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded LIMIT 10;
   ```

## Compute cluster run order

1. Build the shaded jar.

   Command:

   ```powershell
   mvn -DskipTests package
   ```

   Expected artifact:
   - `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar`

2. Attach the jar to the Databricks compute cluster.

3. Configure the cluster init/config settings.

   Required Spark config:

   ```text
   spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
   spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
   ```

   Required environment variables:

   ```text
   UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
   JNAME=zulu11-ca-amd64
   ```

   Required init script:

   ```text
   /Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh
   ```

4. Review the deployment guide.

   File:
   - `COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md`

5. Register the Java UDFs and run smoke tests.

   File:
   - `notebooks/databricks_compute_cluster_udf_smoke_test.py`

6. Run the current customer-table reveal example.

   File:
   - `notebooks/compute_cluster_table_reveal_castback.py`
   - `notebooks/compute_cluster_table_reveal_castback.sql`

7. Apply grants if you created persistent views.

   File:
   - `notebooks/compute_cluster_grant_examples.sql`

8. Validate.

   Example checks:

   ```sql
   SELECT * FROM temp_v_plaintext_protected_internal_reveal LIMIT 10;
   SELECT * FROM temp_v_plaintext_protected_internal_array_reveal LIMIT 10;
   SELECT * FROM temp_v_plaintext_final_reveal_flat LIMIT 10;
   ```

## Simplest recommended production pattern

SQL Warehouse:

- build wheel
- create UC functions
- create secured UC views
- grant users only on the views

Compute cluster:

- build jar
- register Java UDFs
- optionally create persistent views
- grant users only on the views if you created them

## Related files

- `README.md`
- `DEPLOYMENT.md`
- `sql_warehouse/SQL_WAREHOUSE_DEPLOYMENT_GUIDE.md`
- `COMPUTE_CLUSTER_DEPLOYMENT_GUIDE.md`
