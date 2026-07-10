# External Function Datastructure Guide

This guide explains the return formats used by the external-policy protect and
reveal functions, how to consume them from Spark SQL, and how a Java/JDBC
program should work with the returned values.

It is focused on the compute-cluster Java UDF path.

## The main external protect idea

For an external policy, protect does not just return a token. It returns two
pieces of data:

- `protected_value`
- `external_header`

Those two values are normally persisted into sibling columns such as:

- `email`
- `email_header`

## Scalar external protect return format

The scalar object-aware external protect function is:

```sql
thales_protect_by_object_and_column_with_external_header(
  email,
  'char',
  'my_catalog.my_schema.plaintext_protected_external',
  'email'
)
```

It returns a struct with this shape:

```text
STRUCT<protected_value: STRING, external_header: STRING>
```

Conceptually, one row looks like:

```text
{
  protected_value: "1001000SMJ8z@ZXMRoVm.s5Q",
  external_header: "1001000"
}
```

## Spark SQL example

This pattern:

```python
external_round_trip_df = (
    test_df.selectExpr(
        "email",
        "thales_protect_by_object_and_column_with_external_header(email, 'char', 'my_catalog.my_schema.plaintext_protected_external', 'email') as email_external_token"
    )
    .selectExpr(
        "email",
        "email_external_token.protected_value as email_token",
        "email_external_token.external_header as email_header",
        "thales_reveal_by_object_and_column_with_external_header_and_user(email_external_token.protected_value, email_external_token.external_header, 'char', 'my_catalog.my_schema.plaintext_protected_external', 'email', current_user()) as email_revealed"
    )
)
```

does two things:

1. it protects `email` and stores the returned struct in:
   - `email_external_token`

2. it flattens that struct into normal columns:
   - `email_token`
   - `email_header`

and then immediately proves reveal by calling:

- `thales_reveal_by_object_and_column_with_external_header_and_user(...)`

The final row shape is:

```text
email | email_token | email_header | email_revealed
```

## Why object-aware matters

For external tests, prefer the object-aware functions:

- `thales_protect_by_object_and_column_with_external_header(...)`
- `thales_reveal_by_object_and_column_with_external_header_and_user(...)`

because they resolve through:

- `protect.object.<object>`
- `reveal.object.<object>`

That avoids accidental fallback to global internal `COLUMN_PROFILES`.

## Java/JDBC example

The easiest Java pattern is to flatten the struct in SQL and read normal
columns from JDBC.

### SQL

```sql
SELECT
  custid,
  protected_email.protected_value AS email_token,
  protected_email.external_header AS email_header
FROM (
  SELECT
    custid,
    thales_protect_by_object_and_column_with_external_header(
      CAST(email AS STRING),
      'char',
      'my_catalog.my_schema.plaintext_protected_external',
      'email'
    ) AS protected_email
  FROM my_catalog.my_schema.plaintext_plaintext
) s
```

### Java

```java
String sql = """
SELECT
  custid,
  protected_email.protected_value AS email_token,
  protected_email.external_header AS email_header
FROM (
  SELECT
    custid,
    thales_protect_by_object_and_column_with_external_header(
      CAST(email AS STRING),
      'char',
      'my_catalog.my_schema.plaintext_protected_external',
      'email'
    ) AS protected_email
  FROM my_catalog.my_schema.plaintext_plaintext
) s
""";

try (Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery(sql)) {

    while (rs.next()) {
        long custId = rs.getLong("custid");
        String emailToken = rs.getString("email_token");
        String emailHeader = rs.getString("email_header");

        System.out.println(custId + " | " + emailToken + " | " + emailHeader);
    }
}
```

This is the recommended pattern because JDBC handling of nested struct values is
more awkward than ordinary columns.

## Bulk external protect return format

The bulk object-aware external protect function is:

```sql
thales_protect_bulk_by_object_and_column_with_external_header(
  email_array,
  'char',
  'my_catalog.my_schema.plaintext_protected_external_arrays',
  'email'
)
```

It returns:

```text
ARRAY<STRUCT<protected_value: STRING, external_header: STRING>>
```

Conceptually:

```text
[
  { protected_value: "...", external_header: "1001000" },
  { protected_value: "...", external_header: "1001000" }
]
```

## Bulk reveal example

Because the protect result is an array of structs, reveal must split that array
into:

- an array of protected values
- an array of external headers

Example:

```sql
thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
  transform(external_email_token_batch, x -> x.protected_value),
  transform(external_email_token_batch, x -> x.external_header),
  'char',
  'my_catalog.my_schema.plaintext_protected_external_arrays',
  'email',
  current_user()
)
```

What this means:

- `external_email_token_batch` is an array of structs
- `transform(..., x -> x.protected_value)` produces `array<string>` of tokens
- `transform(..., x -> x.external_header)` produces `array<string>` of headers
- the reveal bulk UDF consumes those two arrays together

## How external tables get populated

The config settings:

```properties
external_table_header_value=header
external_table_header_delimiter=_
```

help define the sibling column naming convention:

- `email_header`
- `address_header`
- `creditcard_header`

But those settings do not populate the values by themselves.

The actual values are written because the SQL or notebook code explicitly maps:

- `protected_value -> email`
- `external_header -> email_header`

Example:

```sql
SELECT
  protected_email.protected_value AS email,
  protected_email.external_header AS email_header
```

## Important operational rule

For external policies:

- protect should persist both the token and the header
- reveal should be given both the token and the header

That applies to:

- scalar row-wise external tables
- bulk array-based external tables
- Java/JDBC consumers
- compute-cluster temp reveal views

## Related guides

- [EXTERNAL_HEADER_COLUMN_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\docs\EXTERNAL_HEADER_COLUMN_GUIDE.md)
- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)
- [external_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_scalar_object_aware_load.py)
- [external_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_array_benchmark.py)
