# Setup Index

This directory contains the one-time sample-data and sample-table setup
notebooks used to prepare the customer-style demo objects in the repo.

## Files

- `plaintext_setup.sql`
  Original Java-UDF-based customer-table setup notebook.
- `plaintext_setup_bulk_reveal.sql`
  Preferred Java-UDF-based setup notebook when bulk reveal coverage is also
  required.
- `plaintext_setup_python.py`
  Helper-oriented Python counterpart that demonstrates the higher-level wheel
  API against the sample plaintext/protected tables.

## Guidance

- Prefer `plaintext_setup_bulk_reveal.sql` when you want the broadest Java UDF
  sample coverage in one setup flow.
- Use `plaintext_setup.sql` when you want the lighter legacy-compatible setup
  shape.
- Use `plaintext_setup_python.py` when the goal is to demonstrate the newer
  helper/DataFrame execution model rather than the Java SQL-shaped path.
