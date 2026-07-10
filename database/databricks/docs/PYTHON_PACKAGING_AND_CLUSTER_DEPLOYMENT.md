# Python Packaging And Cluster Deployment

This document explains the new packaging model for the helper-first
Databricks integration.

## Main artifact

The main runtime artifact for the new notebook/helper path is a Python wheel,
not a Java UDF jar.

That means the typical deployment flow is:

1. build the wheel into `dist/`
2. copy `udfConfig.properties` to the cluster path used by
   `UDF_CONFIG_VOLUME_PATH`
3. install the wheel on the compute cluster
4. import the helper directly in notebooks

## Repository layout

- source package:
  [src/thales_databricks_integration](E:\codex\work\thales.databricks.integration\src\thales_databricks_integration\__init__.py:1)
- build metadata:
  [pyproject.toml](E:\codex\work\thales.databricks.integration\pyproject.toml:1)
- build helper scripts:
  [python/build_wheel.ps1](E:\codex\work\thales.databricks.integration\python\build_wheel.ps1:1)
  [python/build_wheel.sh](E:\codex\work\thales.databricks.integration\python\build_wheel.sh:1)
- wheel output:
  `dist/`

## Build commands

Windows PowerShell:

```powershell
.\python\build_wheel.ps1
```

Linux/macOS:

```bash
./python/build_wheel.sh
```

Direct build command:

```bash
python -m build --wheel --outdir dist
```

Fallback build command:

```bash
python setup.py bdist_wheel --dist-dir dist
```

## Expected output

The wheel file will look similar to:

```text
dist/thales_databricks_integration-0.1.0-py3-none-any.whl
```

## Databricks usage model

Once installed on the cluster, notebooks use the helper directly:

```python
from thales_databricks_integration import protect_dataframe, reveal_dataframe
```

No Java UDF registration is required for this helper-first path.

## Properties deployment

Your existing cluster init scripts can continue to copy:

- [udfConfig.properties](E:\codex\work\thales.databricks.integration\src\main\resources\udfConfig.properties:1)

to the Databricks path referenced by:

- `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
- `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`

## Real versus stub transport

The helper supports:

- `transport_mode=auto`
- `transport_mode=stub`
- `transport_mode=real`

Recommended behavior for cluster validation:

- use `auto` for flexible smoke testing
- use `real` when you want the notebook to fail fast unless CRDP is correctly configured
