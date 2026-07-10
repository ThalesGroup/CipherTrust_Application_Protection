-- Databricks notebook source
-- MAGIC %md
-- MAGIC # plaintext_protected_internal Streaming and Lakeflow Examples
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - show the easiest Lakeflow patterns for the current repo
-- MAGIC - use the demo objects and optimized governed SQL views already created
-- MAGIC - keep the examples aligned with the current SQL Warehouse deployment

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- Pattern 1: stream from the protected base table into a Lakeflow-managed
-- bronze table.
CREATE OR REFRESH STREAMING TABLE plaintext_protected_internal_bronze_stream
AS
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
FROM STREAM my_catalog.my_schema.plaintext_protected_internal;

-- COMMAND ----------

-- Pattern 2: create a governed gold materialized view from the optimized flat
-- reveal view. This should be the easiest customer-facing Lakeflow example.
CREATE OR REFRESH MATERIALIZED VIEW plaintext_protected_internal_reveal_gold
AS
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
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized;

-- COMMAND ----------

-- Pattern 3: if you specifically want the lower-UDF-overhead governed array
-- path, materialize the optimized array reveal view.
CREATE OR REFRESH MATERIALIZED VIEW plaintext_protected_internal_reveal_array_gold
AS
SELECT
  row_id,
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
FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized;

-- COMMAND ----------

-- Validation queries
SELECT * FROM plaintext_protected_internal_bronze_stream LIMIT 10;
SELECT * FROM plaintext_protected_internal_reveal_gold LIMIT 10;
SELECT * FROM plaintext_protected_internal_reveal_array_gold LIMIT 10;
