-- Databricks notebook source
-- MAGIC %md
-- MAGIC # plaintext_protected_internal Streaming and Lakeflow Examples
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - show the easiest ways to test the current streaming/Lakeflow guidance
-- MAGIC - use the `plaintext_protected_internal` and related example objects already in this repo
-- MAGIC - keep the examples aligned with the current SQL Warehouse embedded-config functions/views
-- MAGIC
-- MAGIC Recommended easiest test:
-- MAGIC - first create the persistent SQL Warehouse view:
-- MAGIC   `my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded`
-- MAGIC - then use one of the examples below to read from that governed view

-- COMMAND ----------

-- Pattern 1: stream from the secured Unity Catalog reveal view.
-- This is the easiest governed streaming test because it reuses the existing
-- SQL Warehouse deployment work and avoids reimplementing reveal logic in the
-- streaming query itself.
USE CATALOG my_catalog;
USE SCHEMA my_schema;

CREATE OR REFRESH STREAMING TABLE plaintext_protected_internal_reveal_bronze
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
FROM STREAM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded;

-- COMMAND ----------

-- Pattern 2: materialize the current secured view into a downstream table.
-- This is useful if you want a Lakeflow-managed table for downstream reads.

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
FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded;

-- COMMAND ----------

-- Pattern 3: use the optimized array-based secured view if you want to test
-- the lower-UDF-overhead path.

CREATE OR REFRESH MATERIALIZED VIEW plaintext_protected_internal_reveal_flat_gold
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
FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized;

-- COMMAND ----------

-- Validation queries
SELECT * FROM plaintext_protected_internal_reveal_bronze LIMIT 10;
SELECT * FROM plaintext_protected_internal_reveal_gold LIMIT 10;
SELECT * FROM plaintext_protected_internal_reveal_flat_gold LIMIT 10;
