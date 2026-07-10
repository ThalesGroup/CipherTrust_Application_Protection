# External Header Column Guide

This guide explains how external header columns work in this repository, when they are required, and how they are used from both Databricks compute clusters and SQL Warehouse.

## What the external header is

For external CRDP policies, the protected value is often not enough by itself to reveal the original value later. A sibling header column carries the external metadata that CRDP needs during reveal.

Typical pattern:

- protected data column: `email`
- sibling external header column: `email_header`

Example table shape:

```sql
CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_external (
  custid SMALLINT,
  name VARCHAR(107),
  address VARCHAR(107),
  address_header VARCHAR(7),
  city VARCHAR(107),
  state VARCHAR(9),
  zip VARCHAR(17),
  phone VARCHAR(27),
  email VARCHAR(107),
  email_header VARCHAR(7),
  dob TIMESTAMP,
  creditcard DECIMAL(25,0),
  creditcard_header VARCHAR(7),
  creditcardcode INT,
  creditcardcode_header VARCHAR(7),
  ssn VARCHAR(18),
  ssn_header VARCHAR(7)
)
USING DELTA;
```

## Naming convention

The repository uses these configuration settings:

```properties
external_table_header_value=header
external_table_header_delimiter=_
```

That produces names like:

- `address_header`
- `email_header`
- `creditcard_header`
- `creditcardcode_header`
- `ssn_header`

These settings are read from:
- [udfConfig.properties](E:\eclipse-workspace\thales.databricks.udf\src\main\resources\udfConfig.properties)

## Why the header must be passed explicitly in Databricks

A Databricks UDF call does not automatically know the sibling column value from the current row unless the SQL expression passes it in.

So a reveal expression such as:

```sql
thales_reveal_by_column_with_external_header_and_user(
  CAST(email AS STRING),
  CAST(email_header AS STRING),
  'char',
  'email',
  current_user()
)
```

works because the SQL layer explicitly passes both:

- the protected value
- the sibling header value

This is different from the JDBC wrapper model, where a wrapper can inspect the current row and derive sibling column values from a `ResultSet`.

## Compute cluster behavior

### Protect on compute cluster

For external protect on compute clusters, the UDF returns a struct containing:

- `protected_value`
- `external_header`

Relevant functions include:

- `thales_protect_by_column_with_external_header`
- `thales_protect_by_object_and_column_with_external_header`

The return shape is:

```text
STRUCT<protected_value: STRING, external_header: STRING>
```

A common pattern is:

```sql
SELECT
  protected_email.protected_value AS email,
  protected_email.external_header AS email_header
FROM (
  SELECT thales_protect_by_object_and_column_with_external_header(
    CAST(email AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_external',
    'email'
  ) AS protected_email
  FROM my_catalog.my_schema.plaintext_plaintext_external
)
```

This is demonstrated in:
- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)
- [external_scalar_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_with_headers_load.py)

### Reveal on compute cluster

For reveal, the header column must already be present and must be passed into the reveal UDF.

Relevant functions include:

- `thales_reveal_by_column_with_external_header_and_user`
- `thales_reveal_by_object_and_column_with_external_header_and_user`
- `thales_reveal_bulk_by_column_with_external_header_and_user`
- `thales_reveal_bulk_by_object_and_column_with_external_header_and_user`

Example scalar reveal:

```sql
thales_reveal_by_object_and_column_with_external_header_and_user(
  CAST(email AS STRING),
  CAST(email_header AS STRING),
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email',
  current_user()
)
```

Example bulk reveal pattern:

```sql
thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
  transform(email_array, x -> CAST(x AS STRING)),
  transform(email_header_array, x -> CAST(x AS STRING)),
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email',
  current_user()
)
```

## SQL Warehouse behavior

SQL Warehouse uses Python-backed Unity Catalog functions rather than the Java compute-cluster UDF registration flow, but the external-header requirement is the same.

### Protect in SQL Warehouse

The external protect function returns both the protected value and the external header:

- `thales_protect_by_object_and_column_with_external_header_uc_embedded`

This function returns:

```text
STRUCT<protected_value: STRING, external_header: STRING>
```

### Reveal in SQL Warehouse

The reveal function requires the sibling header value to be passed explicitly:

- `thales_reveal_by_object_and_column_with_external_header_uc_embedded`

Example reveal view expression:

```sql
my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
  CAST(email AS STRING),
  CAST(email_header AS STRING),
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email',
  current_user()
)
```

This is implemented in:
- [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql)

## View generation and schema inference

The helper that generates reveal views for SQL Warehouse also understands the sibling header pattern:
- [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)

It uses the configured suffix and delimiter to derive names such as `email_header` and wire those header columns into reveal expressions.

## Recommended table pattern

For external policies, the recommended persisted table shape is:

- one protected value column
- one sibling `*_header` column for each protected external-policy field

That means:

- protect writes both values
- reveal reads both values
- permanent views can expose only the revealed user-facing columns if desired

## Protect vs reveal practical guidance

### Protect

Use the external protect functions when you want Databricks or SQL Warehouse to create:

- the protected token/value
- the sibling external header value

### Reveal

Use the external reveal functions when the table already stores both:

- the protected value
- the sibling external header column

Reveal is usually the simpler long-term operational pattern because the table shape is explicit and stable.

## Where to start in this repo

For compute cluster examples:
- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)
- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)
- [external_scalar_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_with_headers_load.py)

For SQL Warehouse examples:
- [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql)
- [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)

## Operational summary

If you are using an external policy, plan on storing and preserving sibling `*_header` columns alongside the protected data.

That is the common requirement across:

- Databricks compute clusters
- SQL Warehouse
- generated reveal views
- downstream reveal use cases

The main rule is simple:

- external protect should produce both `protected_value` and `external_header`
- external reveal should be given both the protected value and the sibling header column
