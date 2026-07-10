-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse Reveal Full-Processing Count Benchmark
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - benchmark how long SQL Warehouse takes to fully process reveal queries
-- MAGIC   without returning a large result set to the client
-- MAGIC - separate "query returns a few rows quickly" from "query actually
-- MAGIC   processed all rows"
-- MAGIC - use the larger protected compute-cluster benchmark table instead of the
-- MAGIC   20-row demo table
-- MAGIC
-- MAGIC Recommendation:
-- MAGIC - use this script when the question is:
-- MAGIC   "how long does the warehouse take to process all rows?"
-- MAGIC - use `benchmark_uc_plaintext_protected_internal_reveal_performance.sql`
-- MAGIC   for small-result interactive latency
-- MAGIC - use `benchmark_uc_plaintext_protected_internal_reveal_ctas.sql` for
-- MAGIC   processing + materialization throughput

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

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

-- BENCHMARK: optimized_flat_count_10k
SELECT COUNT(*) AS processed_row_count
FROM (
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
    exploded.custid_array AS custid
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
  )
) s;

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

-- BENCHMARK: optimized_flat_count_100k
SELECT COUNT(*) AS processed_row_count
FROM (
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
    exploded.custid_array AS custid
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
  )
) s;

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

-- BENCHMARK: optimized_flat_count_full
SELECT COUNT(*) AS processed_row_count
FROM (
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
    exploded.custid_array AS custid
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
  )
) s;
