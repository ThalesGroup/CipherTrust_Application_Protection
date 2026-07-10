-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse Reveal CTAS Throughput Benchmark
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - benchmark SQL Warehouse reveal throughput using a materialization pattern
-- MAGIC - use the larger protected compute-cluster benchmark table instead of the 20-row demo table
-- MAGIC - build scenario-specific grouped-array benchmark sources for the optimized rowset path
-- MAGIC - rely on Databricks query history as the source of truth for elapsed time
-- MAGIC
-- MAGIC Recommendation:
-- MAGIC - use this script for throughput/materialization benchmarking
-- MAGIC - use `benchmark_uc_plaintext_protected_internal_reveal_performance.sql` for
-- MAGIC   low-row interactive latency comparisons
-- MAGIC
-- MAGIC How to use:
-- MAGIC - run one CTAS statement at a time
-- MAGIC - capture elapsed time from Databricks query history
-- MAGIC - compare row counts and query durations across scenarios
-- MAGIC
-- MAGIC Source table used here:
-- MAGIC - `my_catalog.my_schema.plaintext_protected_internal_helper_parallelism_diag`
-- MAGIC - expected row count: about `350,000`

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

-- Inspect available source rows first.
SELECT COUNT(*) AS source_row_count
FROM my_catalog.my_schema.plaintext_protected_internal_helper_parallelism_diag;

-- COMMAND ----------

-- Scenario 1 source: grouped-array benchmark source built from the first 10k rows.
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_10k
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_internal_helper_parallelism_diag
  WHERE custid <= 10000
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'dob', dob,
      'creditcard', creditcard,
      'creditcardcode', creditcardcode,
      'ssn', ssn
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.ssn) AS ssn_array
FROM batched_rows
GROUP BY batch_id;

-- COMMAND ----------

SELECT
  COUNT(*) AS grouped_batch_row_count,
  SUM(size(custid_array)) AS total_business_rows,
  MIN(size(custid_array)) AS min_rows_per_batch,
  MAX(size(custid_array)) AS max_rows_per_batch
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_10k;

-- COMMAND ----------

SELECT
  batch_id,
  size(custid_array) AS row_count,
  size(address_array) AS address_count,
  size(email_array) AS email_count,
  size(creditcard_array) AS creditcard_count,
  size(creditcardcode_array) AS creditcardcode_count,
  size(ssn_array) AS ssn_count
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_10k
ORDER BY batch_id
LIMIT 5;

-- COMMAND ----------

-- BENCHMARK: optimized_flat_ctas_10k
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_reveal_flat_10k AS
WITH decrypted_batches AS (
  SELECT
    batch_id,
    custid_array,
    name_array,
    city_array,
    state_array,
    zip_array,
    phone_array,
    dob_array,
    my_catalog.my_schema.thales_reveal_rowset_uc_embedded_v2(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING)),
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      session_user()
    ) AS decrypted
  FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_10k
)
SELECT
  exploded.custid_array AS custid,
  exploded.name_array AS name,
  exploded.address_decrypted AS address,
  exploded.city_array AS city,
  exploded.state_array AS state,
  exploded.zip_array AS zip,
  exploded.phone_array AS phone,
  exploded.email_decrypted AS email,
  exploded.dob_array AS dob,
  CAST(exploded.creditcard_decrypted AS DECIMAL(25,0)) AS creditcard,
  CAST(exploded.creditcardcode_decrypted AS INT) AS creditcardcode,
  exploded.ssn_decrypted AS ssn
FROM (
  SELECT explode(
    arrays_zip(
      custid_array,
      name_array,
      decrypted.address_decrypted,
      city_array,
      state_array,
      zip_array,
      phone_array,
      decrypted.email_decrypted,
      dob_array,
      decrypted.creditcard_decrypted,
      decrypted.creditcardcode_decrypted,
      decrypted.ssn_decrypted
    )
  ) AS exploded
  FROM decrypted_batches
);

-- COMMAND ----------

SELECT COUNT(*) AS output_row_count
FROM my_catalog.my_schema.benchmark_plaintext_reveal_flat_10k;

-- COMMAND ----------

-- Scenario 2 source: grouped-array benchmark source built from the first 100k rows.
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_100k
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_internal_helper_parallelism_diag
  WHERE custid <= 100000
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'dob', dob,
      'creditcard', creditcard,
      'creditcardcode', creditcardcode,
      'ssn', ssn
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.ssn) AS ssn_array
FROM batched_rows
GROUP BY batch_id;

-- COMMAND ----------

SELECT
  COUNT(*) AS grouped_batch_row_count,
  SUM(size(custid_array)) AS total_business_rows,
  MIN(size(custid_array)) AS min_rows_per_batch,
  MAX(size(custid_array)) AS max_rows_per_batch
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_100k;

-- COMMAND ----------

SELECT
  batch_id,
  size(custid_array) AS row_count,
  size(address_array) AS address_count,
  size(email_array) AS email_count,
  size(creditcard_array) AS creditcard_count,
  size(creditcardcode_array) AS creditcardcode_count,
  size(ssn_array) AS ssn_count
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_100k
ORDER BY batch_id
LIMIT 5;

-- COMMAND ----------

-- BENCHMARK: optimized_flat_ctas_100k
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_reveal_flat_100k AS
WITH decrypted_batches AS (
  SELECT
    batch_id,
    custid_array,
    name_array,
    city_array,
    state_array,
    zip_array,
    phone_array,
    dob_array,
    my_catalog.my_schema.thales_reveal_rowset_uc_embedded_v2(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING)),
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      session_user()
    ) AS decrypted
  FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_100k
)
SELECT
  exploded.custid_array AS custid,
  exploded.name_array AS name,
  exploded.address_decrypted AS address,
  exploded.city_array AS city,
  exploded.state_array AS state,
  exploded.zip_array AS zip,
  exploded.phone_array AS phone,
  exploded.email_decrypted AS email,
  exploded.dob_array AS dob,
  CAST(exploded.creditcard_decrypted AS DECIMAL(25,0)) AS creditcard,
  CAST(exploded.creditcardcode_decrypted AS INT) AS creditcardcode,
  exploded.ssn_decrypted AS ssn
FROM (
  SELECT explode(
    arrays_zip(
      custid_array,
      name_array,
      decrypted.address_decrypted,
      city_array,
      state_array,
      zip_array,
      phone_array,
      decrypted.email_decrypted,
      dob_array,
      decrypted.creditcard_decrypted,
      decrypted.creditcardcode_decrypted,
      decrypted.ssn_decrypted
    )
  ) AS exploded
  FROM decrypted_batches
);

-- COMMAND ----------

SELECT COUNT(*) AS output_row_count
FROM my_catalog.my_schema.benchmark_plaintext_reveal_flat_100k;

-- COMMAND ----------

-- Scenario 3 source: grouped-array benchmark source built from the full 350k-row helper benchmark table.
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_full
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_internal_helper_parallelism_diag
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'dob', dob,
      'creditcard', creditcard,
      'creditcardcode', creditcardcode,
      'ssn', ssn
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.ssn) AS ssn_array
FROM batched_rows
GROUP BY batch_id;

-- COMMAND ----------

SELECT
  COUNT(*) AS grouped_batch_row_count,
  SUM(size(custid_array)) AS total_business_rows,
  MIN(size(custid_array)) AS min_rows_per_batch,
  MAX(size(custid_array)) AS max_rows_per_batch
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_full;

-- COMMAND ----------

SELECT
  batch_id,
  size(custid_array) AS row_count,
  size(address_array) AS address_count,
  size(email_array) AS email_count,
  size(creditcard_array) AS creditcard_count,
  size(creditcardcode_array) AS creditcardcode_count,
  size(ssn_array) AS ssn_count
FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_full
ORDER BY batch_id
LIMIT 5;

-- COMMAND ----------

-- BENCHMARK: optimized_flat_ctas_full
CREATE OR REPLACE TABLE my_catalog.my_schema.benchmark_plaintext_reveal_flat_full AS
WITH decrypted_batches AS (
  SELECT
    batch_id,
    custid_array,
    name_array,
    city_array,
    state_array,
    zip_array,
    phone_array,
    dob_array,
    my_catalog.my_schema.thales_reveal_rowset_uc_embedded_v2(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING)),
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      session_user()
    ) AS decrypted
  FROM my_catalog.my_schema.benchmark_plaintext_protected_internal_helper_arrays_full
)
SELECT
  exploded.custid_array AS custid,
  exploded.name_array AS name,
  exploded.address_decrypted AS address,
  exploded.city_array AS city,
  exploded.state_array AS state,
  exploded.zip_array AS zip,
  exploded.phone_array AS phone,
  exploded.email_decrypted AS email,
  exploded.dob_array AS dob,
  CAST(exploded.creditcard_decrypted AS DECIMAL(25,0)) AS creditcard,
  CAST(exploded.creditcardcode_decrypted AS INT) AS creditcardcode,
  exploded.ssn_decrypted AS ssn
FROM (
  SELECT explode(
    arrays_zip(
      custid_array,
      name_array,
      decrypted.address_decrypted,
      city_array,
      state_array,
      zip_array,
      phone_array,
      decrypted.email_decrypted,
      dob_array,
      decrypted.creditcard_decrypted,
      decrypted.creditcardcode_decrypted,
      decrypted.ssn_decrypted
    )
  ) AS exploded
  FROM decrypted_batches
);

-- COMMAND ----------

SELECT COUNT(*) AS output_row_count
FROM my_catalog.my_schema.benchmark_plaintext_reveal_flat_full;
