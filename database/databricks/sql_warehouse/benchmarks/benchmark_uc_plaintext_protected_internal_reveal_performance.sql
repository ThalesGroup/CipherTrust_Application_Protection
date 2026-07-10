-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse Reveal Latency And Capability Benchmark
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - compare the reveal query shapes available in SQL Warehouse
-- MAGIC - compare scalar UC Python UDF calls versus per-column bulk versus one-call rowset bulk
-- MAGIC - prove whether the optimized rowset path reduces Python UDF and CRDP fan-out
-- MAGIC - provide a low-row interactive latency comparison, not a throughput benchmark
-- MAGIC
-- MAGIC Expected findings:
-- MAGIC - `v_plaintext_protected_internal_reveal_uc_embedded_v2` is scalar and invokes the Python UDF once per protected column per row
-- MAGIC - `v_plaintext_protected_internal_array_reveal_uc_embedded_v2` is bulk by column, but still invokes the Python UDF once per protected column per batch row
-- MAGIC - `v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized` invokes one Python UDF per batch row and should be the best SQL Warehouse path
-- MAGIC - `v_plaintext_final_reveal_flat_uc_embedded_v2_optimized` should be the recommended customer-facing view
-- MAGIC
-- MAGIC Operational guidance:
-- MAGIC - use this script for interactive/lower-row latency comparisons
-- MAGIC - do not treat `LIMIT 10` or `LIMIT 20` timings as throughput benchmarks
-- MAGIC - do not treat these queries as proof that all source rows were processed
-- MAGIC - use `benchmark_uc_plaintext_protected_internal_reveal_count.sql` when
-- MAGIC   the question is "how long did full processing take without returning a huge result set?"
-- MAGIC - use `benchmark_uc_plaintext_protected_internal_reveal_ctas.sql` for
-- MAGIC   CTAS-style throughput/materialization measurement
-- MAGIC
-- MAGIC Sample measured results:
-- MAGIC - old per-column bulk array view: about 21s
-- MAGIC - optimized array view: 4.38s
-- MAGIC - optimized flat view: 4.52s

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

-- Inspect the batch shape first.
SELECT
  batch_id,
  size(custid_array) AS row_count,
  size(address_array) AS address_count,
  size(email_array) AS email_count,
  size(creditcard_array) AS creditcard_count,
  size(creditcardcode_array) AS creditcardcode_count,
  size(ssn_array) AS ssn_count
FROM my_catalog.my_schema.plaintext_protected_internal_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- Single scalar function call on one literal value.
SELECT my_catalog.my_schema.thales_reveal_by_object_and_column_uc_embedded_v2(
  CAST(email AS STRING),
  'char',
  'my_catalog.my_schema.plaintext_protected_internal',
  'email',
  session_user()
) AS email_revealed
FROM my_catalog.my_schema.plaintext_protected_internal
WHERE custid = 1;

-- COMMAND ----------

-- One per-column bulk call on one batch row.
SELECT
  batch_id,
  size(
    my_catalog.my_schema.thales_reveal_bulk_by_object_and_column_uc_embedded_v2(
      transform(email_array, x -> CAST(x AS STRING)),
      'char',
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      'email',
      session_user()
    )
  ) AS email_revealed_count
FROM my_catalog.my_schema.plaintext_protected_internal_arrays
WHERE batch_id = 0;

-- COMMAND ----------

-- One multi-column rowset bulk call on one batch row.
SELECT
  batch_id,
  size(decrypted.email_decrypted) AS email_revealed_count,
  size(decrypted.address_decrypted) AS address_revealed_count,
  size(decrypted.creditcard_decrypted) AS creditcard_revealed_count,
  size(decrypted.creditcardcode_decrypted) AS creditcardcode_revealed_count,
  size(decrypted.ssn_decrypted) AS ssn_revealed_count
FROM (
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
  WHERE batch_id = 0
) s;

-- COMMAND ----------

-- Capability/latency view timings: run these one at a time and compare runtime.
-- Legacy scalar comparison.
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded_v2 LIMIT 10;

-- COMMAND ----------

-- Legacy per-column bulk comparison.
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2 LIMIT 10;

-- COMMAND ----------

-- Recommended lower-level optimized array view.
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized LIMIT 10;

-- COMMAND ----------

-- Legacy flattened comparison built on the old per-column bulk path.
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2 LIMIT 10;

-- COMMAND ----------

-- Recommended customer-facing optimized flattened view.
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized LIMIT 10;
