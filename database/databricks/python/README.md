## Python Packaging Helpers

This directory keeps the deployment-oriented Python packaging helpers for the
new Databricks integration flow.

Important clarification:

- this directory is **not** the source of truth for the Python package
- it only contains helper scripts for building the wheel
- the package source and packaging metadata live at the repository root

The source package lives in:

- `src/thales_databricks_integration/`

The packaging metadata lives in:

- `pyproject.toml`
- `setup.py`

This folder exists so the repository has a familiar shape for teams used to the
older project layout, where packaging and deployment helpers lived alongside a
`dist/` output flow.

Use:

- [build_wheel.ps1](/E:/codex/work/thales.databricks.integration/python/build_wheel.ps1:1) on Windows
- [build_wheel.sh](/E:/codex/work/thales.databricks.integration/python/build_wheel.sh:1) on Linux/macOS

Both scripts run from the repository root and build a wheel into:

- `dist/`

The preferred direct build command is still:

```powershell
python -m build --wheel --no-isolation --outdir dist
```

The helper scripts simply wrap that command and fall back to:

```powershell
python setup.py bdist_wheel --dist-dir dist
```

if the `build` module is not available.
