# Solution Architecture And Medallion Model

This document explains the Thales Databrick Integration which includes a
higher-level Databricks integration along with a low-level UDF toolkit for
protection of sensitive data.

The main idea is:

- the Python wheel is the primary abstraction layer
- compute-cluster users get a Python-friendly API
- SQL Warehouse and BI users get governed SQL views
- low-level UDFs still exist, but they are no longer the primary end-user
  interface

## Executive Summary

The solution can be described as three layers:

1. `Execution layer`
   The API and runtime surface used by engineers and pipeline authors.

2. `Physical data layer`
   The protected tables and optimized storage shapes used by the platform.

3. `Governed consumption layer`
   The curated SQL views and BI-facing objects used by downstream consumers.

For Databricks-oriented teams, this also maps well to the medallion model:

- `Bronze` = raw landing / ingestion
- `Silver` = standardized protected working data
- `Gold` = governed serving and reveal access

## 1. Execution Layer

This is the layer most developers interact with directly.

### Preferred compute-cluster interface

The recommended interface is the Python helper API from the wheel:

```python
protected_df = protect_dataframe(
    spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)

revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)
```

Parameter descriptions:

- `spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS)`
  The input Spark DataFrame to protect. This is the actual source data being
  read and transformed. `repartition(TARGET_PARTITIONS)` is optional, but it is
  commonly used to shape Spark parallelism for the protect step.

- `spark.table(TARGET_TABLE)`
  The input Spark DataFrame to reveal. In the reveal example, this is usually a
  protected table that was previously written by the protect step.

- `object_name=PROTECTED_OBJECT_NAME`
  The logical protected object key used by the integration. This is one of the
  most important parameters. It is how the wheel finds the object mapping in
  `udfConfig.properties`, for example:
  `protect.object.my_catalog.my_schema.plaintext_protected_internal=...`
  The helper uses this object name to determine which columns are sensitive and
  to resolve per-column profile, datatype, policy type, metadata, and reveal
  behavior. The source table name does not need to appear in the properties
  file.

- `config=config`
  The loaded `IntegrationConfig` object, usually created from
  `udfConfig.properties`. This provides the runtime settings and object/column
  mappings used by the planner and transport layers.

- `options=helper_options`
  Optional per-call overrides for runtime behavior. These are commonly used to
  override things such as transport mode, API version, grouping, request-size
  settings, or reveal-user expression without changing the base properties file.

- `protected_df`
  The returned protected Spark DataFrame. This contains the transformed
  protected values and can be displayed, written to a Delta table, or used in a
  downstream Spark pipeline.

- `revealed_df`
  The returned revealed Spark DataFrame. This contains the reveal result for
  the current querying/runtime user context and can be used for validation,
  downstream processing, or controlled compute-cluster workflows.

Why this is the preferred interface:

- it hides batching and request shaping
- it keeps object/column policy resolution in one place
- it is friendlier for DataFrame-first notebook and job authors
- it is the best current performance path on compute cluster

### Secondary execution surfaces

Other execution surfaces still exist:

- `Java UDFs`
  Best for SQL-shaped compute-cluster ETL, CTAS, and Spark SQL-first teams

- `Pandas UDFs`
  Supported when customers specifically want a Pandas execution surface

- `UC Python UDFs`
  Best for governed SQL Warehouse and shared SQL abstractions

Important positioning:

- UDFs are still supported
- the wheel and helper API are now the main abstraction layer

## 2. Physical Data Layer

This is how protected data is physically stored and served.

There are two important storage shapes:

### A. Row-oriented protected tables

These are the main protected working tables.

Examples:

- `my_catalog.my_schema.plaintext_protected_internal`
- `my_catalog.my_schema.plaintext_protected_external`
- `my_catalog.my_schema.plaintext_protected_none`

These are best for:

- compute-cluster helper execution
- standard pipeline processing
- general protected storage

This should be treated as the primary protected system-of-work layer.

### B. Grouped-array optimized serving tables

These are specialized physical shapes used to improve SQL Warehouse governed
reveal performance.

Example:

- `my_catalog.my_schema.plaintext_protected_internal_arrays`

This table is not the primary universal storage shape.
It is better understood as:

- a serving optimization artifact
- especially useful for the optimized SQL Warehouse rowset reveal path

## 3. Governed Consumption Layer

This is the layer that most SQL users, BI users, and analysts should actually
see.

### Recommended SQL Warehouse / BI pattern

Use standard database views to shield end users from low-level reveal logic.

Example:

```sql
SELECT *
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized;
```

This is the intended experience.

End users should generally not need to write SQL like:

- direct calls to `thales_reveal_bulk_by_object_and_column_uc_embedded_v2(...)`
- direct calls to `thales_reveal_rowset_uc_embedded_v2(...)`
- low-level `transform(...)` and `arrays_zip(...)` plumbing

Those are engineering and deployment patterns, not the target end-user
experience.

### Recommended three-view audience model

For production rollout, the simplest and safest model is to publish separate
views for separate audiences:

- `plaintext` audience view
- `masked` audience view
- `ciphertext` audience view

This is preferred over one master routing view because it gives:

- clearer grants
- more predictable performance
- simpler operational ownership

Important behavior:

- the `plaintext` view uses the optimized reveal path
- the `masked` view does **not** call reveal
- the `ciphertext` view does **not** call reveal

That means the masked and ciphertext audiences do not pay the reveal
transformation cost.

### Recommended production SQL Warehouse view

The primary customer-facing governed view is:

- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized`

The lower-level optimized validation view is:

- `my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized`

Recommendation:

- expose the flat optimized governed view to end users and BI tools
- keep the lower-level array-oriented view mainly for platform and engineering
  validation
- publish separate masked and ciphertext views from the protected base table
  when different audience tiers need different access behavior

## Medallion Mapping

The solution maps naturally to Bronze / Silver / Gold.

## Bronze

Raw or minimally processed landing data.

Typical examples:

- inbound plaintext data before protection
- landing tables from ingestion pipelines
- streaming source tables

Example conceptual table:

- `my_catalog.my_schema.customer_bronze`

Example shape:

```text
customer_id | name | address | email | ssn | creditcard | ingestion_ts
```

## Silver

Standardized, protected, operationally useful data.

This is the best home for:

- row-oriented protected tables
- compute-cluster helper outputs
- main protected working data used by downstream jobs

Examples:

- `my_catalog.my_schema.plaintext_protected_internal`
- `my_catalog.my_schema.plaintext_protected_external`
- `my_catalog.my_schema.plaintext_protected_none`

This is the main protected system-of-work layer.

Example silver flow:

```python
bronze_df = spark.table("my_catalog.my_schema.customer_bronze")

silver_df = protect_dataframe(
    bronze_df,
    object_name="my_catalog.my_schema.customer_protected_internal",
    config=config,
    options=helper_options,
)

silver_df.write.mode("overwrite").saveAsTable("my_catalog.my_schema.customer_silver_protected")
```

## Gold

Curated serving and governed access layer.

This is the best home for:

- curated reveal views
- SQL Warehouse serving patterns
- BI-facing datasets
- optional grouped-array serving optimizations
- Lakeflow materialized views

Examples:

- `my_catalog.my_schema.plaintext_protected_internal_arrays`
  Gold-serving optimization artifact

- `my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized`
  Gold governed reveal view

- downstream BI-facing materialized outputs

Important nuance:

The grouped-array table is not usually the final business-facing gold object.
It is more accurate to think of it as:

- `gold-serving internal optimization`

while the flat reveal view is:

- the actual business-facing `gold` abstraction

## Example Rollout Pattern

A practical organizational rollout can look like this.

### Platform / security / architecture team

Responsibilities:

- define protection and reveal standards
- package and publish the wheel
- deploy UC Python functions
- create optimized governed reveal views
- define grants and access boundaries

### Data engineering team

Responsibilities:

- ingest bronze data
- create silver protected tables using the helper API
- build optional optimized serving tables when SQL Warehouse performance matters

### BI / analytics / downstream consumers

Responsibilities:

- query curated gold views
- use BI tools against governed reveal views
- avoid direct low-level transformation logic

## Example Deployment Patterns

### Pattern A: Performance-first compute cluster

Use when:

- throughput matters most
- jobs are DataFrame-first

Pattern:

1. bronze plaintext ingestion
2. helper API creates silver protected tables
3. downstream compute jobs continue from silver

### Pattern B: Governed SQL Warehouse serving

Use when:

- BI tools need access
- shared SQL access must be governed

Pattern:

1. create silver protected row tables
2. create optional grouped-array serving tables for performance
3. create three audience-tier views:
   - plaintext
   - masked
   - ciphertext
4. grant BI users access to the appropriate view only

### Pattern C: SQL-shaped compute-cluster ETL

Use when:

- a team strongly prefers Spark SQL / CTAS style

Pattern:

1. use Java UDFs in compute-cluster SQL jobs
2. write protected silver tables
3. optionally publish governed gold reveal views separately

## SQL Warehouse Reveal Recommendation

For real deployment:

- build the optimized rowset-based path
- expose the optimized flat governed view

Summarized example:

1. Build or maintain the grouped-array serving table used by the optimized
   reveal path.

   Example concept:

   ```sql
   CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal_arrays AS
   SELECT
     batch_id,
     custid_array,
     name_array,
     address_array,
     city_array,
     state_array,
     zip_array,
     phone_array,
     email_array,
     dob_array,
     creditcard_array,
     creditcardcode_array,
     ssn_array
   FROM ...
   ```

2. Reveal the grouped batches through the optimized rowset function.

   Example concept:

   ```sql
   SELECT
     batch_id,
     my_catalog.my_schema.thales_reveal_rowset_uc_embedded_v2(
       transform(address_array, x -> CAST(x AS STRING)),
       transform(email_array, x -> CAST(x AS STRING)),
       transform(creditcard_array, x -> CAST(x AS STRING)),
       transform(creditcardcode_array, x -> CAST(x AS STRING)),
       transform(ssn_array, x -> CAST(x AS STRING)),
       'my_catalog.my_schema.plaintext_protected_internal_arrays',
       session_user()
     ) AS decrypted
   FROM my_catalog.my_schema.plaintext_protected_internal_arrays
   ```

3. Expose a flat governed reveal view on top of that optimized rowset result.

   Example concept:

   ```sql
   CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized AS
   SELECT ...
   FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized
   ```

This means BI users and downstream SQL users should normally query the final
flat governed view, not write the rowset function call themselves.

### Recommended audience-tier view examples

#### 1. Plaintext audience view

This is the only audience tier that should use the optimized reveal
transformation path.

Important behavior:

- this view is dynamic, not pre-materialized revealed data
- when a user queries it, the underlying optimized reveal path evaluates the
  current SQL identity through `session_user()`
- that means the reveal behavior is determined at query time for the querying
  user, not fixed at table-build time

```sql
CREATE OR REPLACE VIEW my_catalog.my_schema.v_customer_plaintext AS
SELECT *
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized;
```

#### 2. Masked audience view

This view reads directly from the protected base table and applies masking
logic. It does **not** use the reveal transformation path.

Example masking approach:

- character-like fields become a generic mask such as `'pii_masked'`
- numeric-like fields become a generic masked numeric such as `999`

```sql
CREATE OR REPLACE VIEW my_catalog.my_schema.v_customer_masked AS
SELECT
  custid,
  name,
  'pii_masked' AS address,
  city,
  state,
  zip,
  phone,
  'pii_masked' AS email,
  dob,
  CAST(999 AS DECIMAL(25,0)) AS creditcard,
  CAST(999 AS INT) AS creditcardcode,
  'pii_masked' AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;
```

#### 3. Ciphertext audience view

This view also reads directly from the protected base table and simply exposes
the protected values. It does **not** use the reveal transformation path.

```sql
CREATE OR REPLACE VIEW my_catalog.my_schema.v_customer_ciphertext AS
SELECT
  custid,
  name,
  address,
  city,
  state,
  zip,
  phone,
  email,
  dob,
  creditcard,
  creditcardcode,
  ssn
FROM my_catalog.my_schema.plaintext_protected_internal;
```

### Group-to-view mapping

Recommended operational model:

- grant the plaintext audience group access to `v_customer_plaintext`
- grant the masked audience group access to `v_customer_masked`
- grant the ciphertext audience group access to `v_customer_ciphertext`

This is better than expecting end users to write filters such as:

```sql
SELECT * FROM my_catalog.my_schema.v_customer_masked
WHERE NOT is_account_group_member('pii_plaintext')
  AND is_account_group_member('pii_masked')
```

or:

```sql
SELECT * FROM my_catalog.my_schema.v_customer_ciphertext
WHERE NOT is_account_group_member('pii_plaintext')
  AND NOT is_account_group_member('pii_masked')
```

Those predicates can work technically, but they should not be part of the
normal end-user query experience. The preferred model is:

- separate views
- separate grants
- no user-authored routing logic

The older scalar and per-column bulk SQL shapes should remain only for:

- comparison
- troubleshooting
- engineering validation

Production recommendation:

- `do build`
  - protected silver row tables
  - optimized grouped-array serving tables when needed
  - optimized flat governed plaintext reveal views
  - separate masked and ciphertext views on the protected base table

- `do not lead with`
  - old scalar reveal views
  - old per-column bulk reveal views
  - direct low-level function SQL for end users

## Best-Practice Summary

- The wheel as the main abstraction layer.
- The helper API as the preferred compute-cluster interface.
- Java UDFs as a specialized SQL-shaped execution option.
- SQL Warehouse governed reveal views as the preferred BI/user-facing interface.
- Low-level reveal SQL and low-level UDFs behind platform or engineering-owned layers.
