# Java UDF API Guide

This guide explains the public Java UDF surface currently implemented in this
repository for Databricks compute clusters.

## Purpose

Use this path when you want:

- Spark SQL or CTAS-style protect/reveal on a compute cluster
- object-aware profile resolution through `udfConfig.properties`
- Java UDF execution registered into a Spark session
- SQL-friendly bulk protect for array-shaped inputs

This document only describes the Java UDFs that currently exist in this
repository and are registered by:

- [ThalesUdfRegistrar.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/udf/ThalesUdfRegistrar.java)

## Registration Entry Point

The current public Java UDF surface is registered through:

```java
ThalesUdfRegistrar.registerMinimalSurface(spark)
```

That registration adds these Spark SQL function names:

- `thales_protect_by_object_and_column`
- `thales_reveal_by_object_and_column_with_user`
- `thales_protect_by_object_and_column_with_external_header`
- `thales_reveal_by_object_and_column_with_external_header_and_user`
- `thales_protect_bulk_by_object_and_column`
- `thales_protect_bulk_by_object_and_column_with_external_header`
- `thales_reveal_bulk_by_object_and_column_with_user`
- `thales_reveal_bulk_by_object_and_column_with_external_header_and_user`

## Shared Parameter Model

Most Java UDFs in this repository follow the same object-aware model.

Common parameters:

- `value` or `values`
  The source value to protect, or the protected value to reveal. Bulk variants
  take an array/sequence of values.

- `datatype`
  The datatype hint used for profile/policy resolution and CRDP request
  construction. Common values are `char` and `nbr`.

- `object_name`
  The logical protected object key used by the runtime. This is how the UDF
  looks up `protect.object.<object_name>` in `udfConfig.properties` and how it
  participates in the fallback hierarchy to `column.<name>.profile`,
  `COLUMN_PROFILES`, and `protection_profile`.

- `column_name`
  The logical column lookup key. This is used together with `object_name` to
  resolve the effective profile, datatype behavior, policy type, metadata, and
  reveal-user-related settings.

- `reveal_user`
  The reveal identity passed to CRDP for reveal operations. In Spark SQL this
  is commonly supplied as `current_user()` or `session_user()`.

- `external_header`
  The stored external header/version required for external-policy reveal
  operations.

## Full Public Java UDF List

### 1. `thales_protect_by_object_and_column`

Signature:

```sql
thales_protect_by_object_and_column(value, datatype, object_name, column_name)
```

Example:

```sql
thales_protect_by_object_and_column(
  CAST(email AS STRING),
  'char',
  'my_catalog.my_schema.plaintext_protected_internal',
  'email'
)
```

Behavior:

- protects one value
- returns one protected string
- uses object-aware profile resolution

Parameters:

- `value`
  The plaintext value to protect.

- `datatype`
  Usually `char` or `nbr`.

- `object_name`
  The protected object lookup key.

- `column_name`
  The logical sensitive column lookup key.

Return type:

- `STRING`

### 2. `thales_reveal_by_object_and_column_with_user`

Signature:

```sql
thales_reveal_by_object_and_column_with_user(
  protected_value,
  datatype,
  object_name,
  column_name,
  reveal_user
)
```

Example:

```sql
thales_reveal_by_object_and_column_with_user(
  email,
  'char',
  'my_catalog.my_schema.plaintext_protected_internal',
  'email',
  current_user()
)
```

Behavior:

- reveals one protected value
- returns one revealed string
- uses the supplied reveal identity

Parameters:

- `protected_value`
  The protected/ciphertext/token value to reveal.

- `datatype`
  Usually `char` or `nbr`.

- `object_name`
  The protected object lookup key.

- `column_name`
  The logical sensitive column lookup key.

- `reveal_user`
  The identity to send to CRDP for reveal authorization.

Return type:

- `STRING`

### 3. `thales_protect_by_object_and_column_with_external_header`

Signature:

```sql
thales_protect_by_object_and_column_with_external_header(
  value,
  datatype,
  object_name,
  column_name
)
```

Example:

```sql
thales_protect_by_object_and_column_with_external_header(
  CAST(email AS STRING),
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email'
)
```

Behavior:

- protects one value
- returns both:
  - protected value
  - external header/version

Return type:

- `STRUCT<protected_value: STRING, external_header: STRING>`

Typical SQL usage:

```sql
SELECT
  protected_email.protected_value AS email,
  protected_email.external_header AS email_header
FROM (
  SELECT
    thales_protect_by_object_and_column_with_external_header(
      CAST(email AS STRING),
      'char',
      'my_catalog.my_schema.plaintext_protected_external',
      'email'
    ) AS protected_email
  FROM my_catalog.my_schema.plaintext_plaintext
) s
```

### 4. `thales_reveal_by_object_and_column_with_external_header_and_user`

Signature:

```sql
thales_reveal_by_object_and_column_with_external_header_and_user(
  protected_value,
  external_header,
  datatype,
  object_name,
  column_name,
  reveal_user
)
```

Example:

```sql
thales_reveal_by_object_and_column_with_external_header_and_user(
  email,
  email_header,
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email',
  current_user()
)
```

Behavior:

- reveals one external-policy protected value
- uses both the stored protected value and the external header/version

Return type:

- `STRING`

### 5. `thales_protect_bulk_by_object_and_column`

Signature:

```sql
thales_protect_bulk_by_object_and_column(values, datatype, object_name, column_name)
```

Example:

```sql
thales_protect_bulk_by_object_and_column(
  email_array,
  'char',
  'my_catalog.my_schema.plaintext_protected_internal_arrays',
  'email'
)
```

Behavior:

- protects an array of values
- intended for array-shaped rows, not ordinary row-per-record tables

Parameters:

- `values`
  An array/sequence of plaintext values.

- `datatype`
  Usually `char` or `nbr`.

- `object_name`
  The protected object lookup key.

- `column_name`
  The logical sensitive column lookup key.

Return type:

- `ARRAY<STRING>`

### 6. `thales_protect_bulk_by_object_and_column_with_external_header`

Signature:

```sql
thales_protect_bulk_by_object_and_column_with_external_header(
  values,
  datatype,
  object_name,
  column_name
)
```

Example:

```sql
thales_protect_bulk_by_object_and_column_with_external_header(
  email_array,
  'char',
  'my_catalog.my_schema.plaintext_protected_external_arrays',
  'email'
)
```

Behavior:

- protects an array of values
- returns one struct per input item with:
  - protected value
  - external header/version

Return type:

- `ARRAY<STRUCT<protected_value: STRING, external_header: STRING>>`

### 7. `thales_reveal_bulk_by_object_and_column_with_user`

Signature:

```sql
thales_reveal_bulk_by_object_and_column_with_user(
  protected_values,
  datatype,
  object_name,
  column_name,
  reveal_user
)
```

Example:

```sql
thales_reveal_bulk_by_object_and_column_with_user(
  email_token_array,
  'char',
  'my_catalog.my_schema.plaintext_protected_internal_arrays',
  'email',
  current_user()
)
```

Behavior:

- reveals an array of protected values
- intended for array-shaped rows

Return type:

- `ARRAY<STRING>`

### 8. `thales_reveal_bulk_by_object_and_column_with_external_header_and_user`

Signature:

```sql
thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
  protected_values,
  external_headers,
  datatype,
  object_name,
  column_name,
  reveal_user
)
```

Example:

```sql
thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
  email_token_array,
  email_header_array,
  'char',
  'my_catalog.my_schema.plaintext_protected_external_arrays',
  'email',
  current_user()
)
```

Behavior:

- reveals an array of external-policy protected values
- uses the aligned external header/version array

Return type:

- `ARRAY<STRING>`

## Best-Practice Usage Guidance

Use scalar Java UDFs when:

- one protected value is stored per row
- you are building CTAS statements or wrapper views
- you want simple SQL-shaped protect/reveal logic

Use bulk Java protect UDFs when:

- the source row intentionally stores arrays
- you want one outbound CRDP-style bulk protect per array-shaped work unit

Use bulk Java reveal UDFs when:

- protected arrays are already stored in a single row
- you want SQL-shaped reveal over those arrays
- the reveal identity should still be explicit through `current_user()` or
  `session_user()`

Use object-aware keys consistently:

- `object_name` should match the logical protected object being modeled
- `column_name` should match the logical sensitive column
- this keeps resolution behavior predictable when `protect.object...`,
  `column.<name>.profile`, and `COLUMN_PROFILES` are mixed

## Reveal User Guidance

For Java reveal UDFs, best practice is to pass:

- `current_user()`
  or
- `session_user()`

through the `*_with_user` function variants.

Typical example:

```sql
thales_reveal_by_object_and_column_with_user(
  ssn,
  'nbr',
  'my_catalog.my_schema.plaintext_protected_internal',
  'ssn',
  current_user()
)
```

## Related Files

- [ThalesUdfRegistrar.java](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration/udf/ThalesUdfRegistrar.java)
- [compute_cluster_java_udf_smoke_test.py](/E:/codex/work/thales.databricks.integration/notebooks/smoke_tests/compute_cluster_java_udf_smoke_test.py)
- [compute_cluster_java_udf_sql_examples_external_round_trip.py](/E:/codex/work/thales.databricks.integration/notebooks/examples/external/compute_cluster_java_udf_sql_examples_external_round_trip.py)
- [plaintext_setup.sql](/E:/codex/work/thales.databricks.integration/notebooks/setup/plaintext_setup.sql)
