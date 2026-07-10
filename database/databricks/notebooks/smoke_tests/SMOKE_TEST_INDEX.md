# Smoke Test Index

This directory contains the primary compute-cluster validation notebooks for
the integration project.

## Files

- `register_java_udfs.py`
  Shared helper notebook that registers the full public Java UDF surface for a
  Spark session.
- `compute_cluster_java_udf_smoke_test.py`
  Primary Java UDF smoke test for scalar and bulk protect coverage.
- `compute_cluster_java_udf_smoke_test_bulk_reveal.py`
  Expanded Java UDF smoke test that additionally validates bulk reveal
  behavior.
- `compute_cluster_python_helper_smoke_test.py`
  Python wheel / helper smoke test for the DataFrame-first public API.

## Recommended Order

1. Run `compute_cluster_java_udf_smoke_test.py` for quick Java path validation.
2. Run `compute_cluster_python_helper_smoke_test.py` for helper-path
   validation.
3. Run `compute_cluster_java_udf_smoke_test_bulk_reveal.py` when you need to
   validate the newer Java bulk-reveal functions.

## Notes

- The Java smoke tests now load `register_java_udfs.py` so the registration
  block is defined in one place.
- These notebooks are intended to be self-contained and should not require the
  sample setup notebooks to be run first.
