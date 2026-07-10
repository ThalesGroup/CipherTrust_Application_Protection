# Thales Property File Access Options

This document explains the supported ways Databricks notebooks and Unity
Catalog SQL setup artifacts can access `udfConfig.properties`.

The goal is to make two things clear:

- what the preferred production approach should be
- what alternative access patterns are available for setup, testing, and
  governed SQL deployment

## Preferred Production Path

The preferred production approach for compute-cluster workloads is:

1. store `udfConfig.properties` in a governed location such as a Unity Catalog
   volume
2. use a cluster init script to copy the file to a stable local runtime path,
   such as `/tmp/thales_config/udfConfig.properties`
3. configure the cluster so the driver and executors both know that runtime
   path
4. have notebooks load the config from that explicit configured path

Recommended Databricks Spark configuration entries:

```text
spark.driverEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
spark.executorEnv.UDF_CONFIG_VOLUME_PATH /tmp/thales_config/udfConfig.properties
```

This is the preferred model because:

- it gives Java and Python workloads a consistent runtime contract
- it avoids ambiguity about which config file is active
- it works well for repeatable production deployment
- it is easier to support operationally

## Option 1: Explicit Config Path From Cluster Runtime

This is the clearest compute-cluster notebook pattern.

Representative example:

- [compute_cluster_python_helper_smoke_test.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_python_helper_smoke_test.py:1)

Typical pattern:

```python
config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)
```

Use this when:

- the cluster has already been configured correctly
- you want the active config path to be explicit in notebook output
- you want the same deployment contract across multiple notebooks

## Option 2: Setup Notebook Fallback To A Known Volume Path

Some setup workflows are easier to operate when they can fall back to a known
volume path if the cluster runtime setting is missing.

Representative example:

- [plaintext_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/setup/plaintext_setup.sql:1)

Typical pattern:

```python
DEFAULT_VOLUME_CONFIG_PATH = "/Volumes/my_catalog/my_schema/volume_forjars/config/udfConfig.properties"
config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)

if not config_path and Path(DEFAULT_VOLUME_CONFIG_PATH).exists():
    config_path = DEFAULT_VOLUME_CONFIG_PATH
```

Use this when:

- you are running a setup notebook
- you want setup-time diagnostics to continue even if the cluster env setting
  is not fully wired yet
- the file location on the volume is known and governed

Best-practice note:

- this is a helpful setup fallback
- it should not replace the preferred production runtime contract for
  compute-cluster jobs

## Option 3: Nested Notebook Import Plus Explicit Config Path

Some nested notebooks use a small import bootstrap so they can reliably import
 shared utilities, then still load `udfConfig.properties` from the explicit
 cluster-configured path.

Representative example:

- [internal_helper_dataframe_adls_load.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/internal/internal_helper_dataframe_adls_load.py:1)

This pattern is useful when:

- the notebook lives under a nested folder such as `notebooks/internal`
- workspace and repo execution layouts may differ
- the notebook still wants to keep config loading explicit and predictable

The important point is that the import bootstrap and the config-file access are
two separate concerns:

- the import bootstrap helps Python find shared notebook utilities
- the explicit `config_path` still controls which `udfConfig.properties` file
  is loaded

## Option 4: Direct Config Path In Unity Catalog SQL Setup

Unity Catalog setup artifacts can use a direct config path as part of the SQL
 function contract itself.

Representative example:

- [unity_catalog_python_udf_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/utils/unity_catalog_python_udf_setup.sql:1)

Typical shape:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
  value STRING,
  object_name STRING,
  column_name STRING,
  config_path STRING,
  reveal_user STRING
)
```

And then the view or query supplies a known volume path such as:

```text
/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties
```

Use this when:

- you are creating Unity Catalog Python functions
- you want a reusable function surface
- the deployment model intentionally passes the config path as part of the SQL
  contract

Important note:

- this is more flexible than embedded-config SQL patterns
- it also means the function/view layer still depends on a usable `config_path`

## Recommended Decision Order

For customer deployments, use this order:

1. preferred compute-cluster production path:
   init script plus explicit cluster runtime config path
2. setup notebook fallback to a known volume path when needed
3. nested notebook import bootstrap only when workspace/repo layout requires it
4. direct `config_path` in Unity Catalog SQL when the deployment model is
   intentionally function-driven

## Best-Practice Summary

Recommended production stance for compute clusters:

- use the init-script plus explicit cluster-config path model
- keep the runtime file location stable
- make the active path visible in notebook output when possible

Recommended stance for Unity Catalog SQL setup:

- use a direct `config_path` function contract only when that is part of the
  intended governed SQL design

The key principle is simple:

- production compute-cluster workloads should prefer a stable runtime config
  contract
- setup and governed SQL artifacts may use alternative access patterns when the
  deployment model calls for them
