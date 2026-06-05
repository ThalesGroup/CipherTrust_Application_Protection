# Thales Databricks Compute Cluster Test Runbook

This runbook covers the recommended setup and execution order for testing the
Java UDF deployment on a Databricks compute cluster.

## Compute cluster model

| Thing | Compute cluster Java UDF path | Persistent? |
|---|---|---|
| Protected tables | `CREATE TABLE`, `INSERT OVERWRITE` | Yes |
| Java UDF registrations | `spark.udf.registerJavaFunction(...)` | No, session-scoped |
| Reveal views using those Java UDFs | `TEMP VIEW` | No, session-scoped |
| Grants on protected tables | normal catalog grants | Yes |

## Best-practice summary

| Deployment path | Best fit | Why |
|---|---|---|
| Compute cluster Java UDFs | ETL, batch jobs, executor-parallel transforms, session-driven work | good fit for Spark job execution and large-scale transformation workloads |
| SQL Warehouse / Unity Catalog functions | persistent, governed, shareable functions and views | best fit for durable shared access, grants, and analyst-facing reveal views |

## 1. Choose the jar version to test

Use only one active Thales UDF jar on the cluster at a time.

Recommended approach:

- detach or uninstall the older Thales UDF jar from the cluster
- attach only the jar version you want to test
- restart the cluster after changing the attached library set

Important:

- keeping old jars on a Unity Catalog volume is fine
- installing multiple jar versions containing the same classes on the same
  cluster can cause classpath conflicts and unpredictable behavior

## 2. Store `udfConfig.properties`

Recommended source location:

- `/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties`

Why this location is recommended:

- it is a Unity Catalog volume path
- it is a better fit for cluster-accessed shared artifacts than workspace files
- the init script copies it to a local driver/executor path before Spark starts

## 3. Upload the init script

Repo source file:

- [copy_udf_config_init.sh](E:\eclipse-workspace\thales.databricks.udf\cluster_init_scripts\copy_udf_config_init.sh)

Upload the script to the same Unity Catalog volume used for the jar/config, for example:

- `/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh`

Purpose:

- copy `udfConfig.properties` from `/Volumes/...` to `/tmp/thales_config/udfConfig.properties`
- avoid the FUSE `Operation not permitted` issue when Java UDF code reads config from task threads

## 4. Configure cluster Spark settings

On the Databricks compute cluster, open:

- `Advanced options`
- `Spark`

Add these Spark config values:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Important:

- in the Databricks Spark config UI, enter these as key/value pairs
- do not use an `=` sign in that box

These values tell the Java UDF code where to load `udfConfig.properties` for:

- the driver
- the executors

## 5. Configure cluster environment variables

In the cluster environment variables section, add:

```text
UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
JNAME=zulu11-ca-amd64
```

Notes:

- `UDF_CONFIG_VOLUME_PATH` matches the local path created by the init script
- `JNAME=zulu11-ca-amd64` is required in this environment for the working setup you validated

## 6. Configure the init script on the cluster

On the Databricks compute cluster, open:

- `Advanced options`
- `Init Scripts`

Add a new init script with:

- Source: `Volumes`
- File path: `/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh`

## 7. Restart the cluster

Restart the cluster after any of the following changes:

- updating Spark config
- changing environment-variable settings
- changing init scripts
- attaching or detaching the jar
- swapping between old and new jar versions

Recommended practice:

- restart first
- then reattach to the notebook
- then run the smoke test

## 8. Recommended test order

1. confirm only one Thales jar is attached to the cluster
2. confirm `udfConfig.properties` exists on the Unity Catalog volume
3. upload the init script and attach it as a cluster init script
4. set the Spark config values
5. set the environment variables
6. restart the cluster
7. run the generic smoke test notebook
8. if needed, run the debug notebook
9. run the customer table setup or numeric setup scripts
10. optionally run the current table reveal castback example notebook for a smaller walkthrough

## 9. Smoke test notebook

Run first:

- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)

What this notebook does:

- registers the Java UDFs
- validates the config-path environment settings
- runs basic scalar and bulk protect/reveal smoke tests, including external scalar and external bulk reveal
- does not require existing customer tables

Java TLS note:

- if `udfConfig.properties` contains:
  - `CRDP_SSL_ENABLED=true`
  - `CRDP_SSL_VERIFY_SERVER=true`
  - `CRDP_CA_CERT_PATH=/tmp/thales_config/crdp-ca.pem`
  - `CRDP_CLIENT_PKCS12_PATH=/tmp/thales_config/crdp-client.p12`
  - `CRDP_CLIENT_PKCS12_PASSWORD=...`
- then this same notebook is the recommended Java compute-cluster TLS smoke test
- you do not need to pick a random customer-table notebook just to validate the Java HTTPS path

Important:

- this notebook is mainly for validation and troubleshooting
- the setup notebooks now self-register the object-aware Java UDFs they use
- you do not need to run the smoke test first just to make the setup notebooks work

## 10. Optional debug notebook

Run this only if you need deeper troubleshooting against the `plaintext_protected_internal` flow:

- [legacy_internal_debug_reveal_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\legacy_internal_debug_reveal_examples.py)

What this notebook does:

- registers the Java UDFs
- reads the source table
- creates temp reveal views
- creates the batched array table
- runs diagnostic queries against the legacy/debug flow

## 11. Customer-table setup scripts

For the main plaintext customer-table workflow:

- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)

Important:

- this script inserts readable sample plaintext values
- if you want to test reveal workflows, those rows must first be protected by your loader or another protection step
- this notebook self-registers the required object-aware Java UDFs in the current session
- it creates persistent protected tables and session `TEMP VIEW` reveal views

For the numeric-measure workflow:

- [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_setup.sql)

Important:

- this notebook also self-registers the required object-aware Java UDFs in the current session
- it creates persistent protected tables and session `TEMP VIEW` reveal views

## 12. Current supported reveal examples

For the compute-cluster customer-table setup flow:

- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)

For the Python/SQL castback walkthrough:

- [numbers_reveal_castback_examples.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_reveal_castback_examples.py)
- [numbers_reveal_castback_examples.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_reveal_castback_examples.sql)

For numeric measures:

- [numbers_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers_smoke_test.py)

## 13. Objects created by the current customer-table flow

The main setup flow now creates:

- persistent protected Delta tables
- session `TEMP VIEW` reveal views

Example persistent tables:

- `my_catalog.my_schema.plaintext_protected_internal`
- `my_catalog.my_schema.plaintext_protected_external`
- `my_catalog.my_schema.plaintext_protected_internal_arrays`
- `my_catalog.my_schema.plaintext_protected_external_arrays`

Example session temp reveal views:

- `v_plaintext_protected_internal_revealed`
- `v_plaintext_protected_external_revealed`
- `v_plaintext_protected_internal_array_reveal`
- `v_plaintext_protected_external_array_reveal`
- `v_plaintext_final_reveal_flat`
- `v_plaintext_external_final_reveal_flat`

## 14. Expected validation points

After the smoke test and reveal examples run, validate the following:

- the driver prints the configured `UDF_CONFIG_VOLUME_PATH`
- Java UDF registration succeeds without class-not-found errors
- the row-level temp reveal views return data for the current Databricks user
- the arrays table contains batched arrays grouped by `batch_id`
- the bulk reveal views return decrypted or masked arrays as expected
- the final flat views reconstruct row-shaped output from the arrays
- source row count and final flat row count match

## 15. Data type note for Java UDF testing

The Java UDF adapters accept string inputs, so numeric columns are commonly
cast to `STRING` at the UDF boundary.

This is part of the recommended **cast-back pattern**:

- keep the original business table in natural numeric types
- store protected numeric values in a staging/protected table as `STRING`
- reveal from that protected table
- cast the revealed plaintext back to the original numeric type in the reveal view

Important:

- this does not change the original source table schema
- it does change the resulting expression type in a view or query
- if you persist the casted result into a new table, that new table column will be `STRING`

Example:

```sql
SELECT
  CAST(
    thales_reveal_by_column_with_user(
      CAST(amount_decimal AS STRING),
      'nbr',
      'amount',
      current_user()
    )
    AS DECIMAL(18,2)
  ) AS amount
FROM my_catalog.my_schema.account_balance_plaintext_protected_internal
```

Use this pattern for values that must later be averaged or summed.

Why this matters:

- protected numeric values are tokens, not true business numerics
- numeric storage types can normalize or alter the token representation
- that can break reliable reveal if leading zeros, scale, or formatting change

Aggregation example:

```sql
SELECT
  SUM(
    CAST(
      thales_reveal_by_column_with_user(
        CAST(amount_decimal AS STRING),
        'nbr',
        'amount',
        current_user()
      )
      AS DECIMAL(18,2)
    )
  ) AS total_amount,
  AVG(
    CAST(
      thales_reveal_by_column_with_user(
        CAST(balance_long AS STRING),
        'nbr',
        'balance',
        current_user()
      )
      AS DECIMAL(18,2)
    )
  ) AS avg_balance
FROM my_catalog.my_schema.account_balance_plaintext_protected_internal
```

For external-policy numeric tables with sibling header columns, use:

```sql
SELECT
  CAST(
    thales_reveal_by_column_with_external_header_and_user(
      CAST(amount_decimal AS STRING),
      CAST(amount_decimal_header AS STRING),
      'nbr',
      'amount',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS amount
FROM my_catalog.my_schema.account_balance_plaintext_protected_external
```

## 16. Recommended setup summary

Use this setup for the current working cluster configuration:

- one active Thales jar attached to the cluster
- config source file on volume:
  `/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties`
- init script on volume:
  `/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh`
- local config path used by Spark and env vars:
  `/tmp/thales_config/udfConfig.properties`

Spark config:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

Environment variables:

```text
UDF_CONFIG_VOLUME_PATH=/tmp/thales_config/udfConfig.properties
JNAME=zulu11-ca-amd64
```

Init script:

- Source: `Volumes`
- File path: `/Volumes/my_catalog/my_schema/volume_forjars/copy_udf_config_init.sh`

## References

- [Compute-scoped libraries](https://docs.databricks.com/aws/en/libraries/cluster-libraries)
- [Compute configuration reference](https://docs.databricks.com/en/compute/configure.html)
- [Workspace files](https://docs.databricks.com/aws/en/files/workspace)

