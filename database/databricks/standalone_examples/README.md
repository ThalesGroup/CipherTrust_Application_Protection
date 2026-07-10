# Standalone Examples

This directory contains direct-Python examples that are intended to run
outside Databricks.

These files are examples and smoke tests, not reusable operational tools.

## Files

- `python_direct_api_stub_smoke_test.py`
  Easiest offline smoke test. Uses sample in-memory configuration and stub
  transport only.
- `python_direct_api_properties_stub_demo.py`
  Loads the local `udfConfig.properties` file but still forces stub transport.
  Useful for validating profile resolution and properties parsing without a live
  CRDP dependency.
- `python_direct_api_properties_real_demo.py`
  Loads the local `udfConfig.properties` file and forces real transport for a
  lightweight connected CRDP demo outside Databricks.

