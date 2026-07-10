-- Lakeflow Declarative Pipelines / SQL examples for the current integration.
--
-- Recommended governed pattern:
-- - stream from protected Delta tables when you are building bronze/silver
-- - reveal through governed UC functions or governed UC views when you are
--   building gold / consumer-facing objects

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- Example 1: create a streaming table from a protected source table.
CREATE OR REFRESH STREAMING TABLE plaintext_protected_internal_bronze
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


-- Example 2: create a governed gold materialized view from the optimized
-- flattened UC reveal view. This is the preferred customer-facing SQL path.
CREATE OR REFRESH MATERIALIZED VIEW plaintext_internal_reveal_gold
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


-- Example 3: if you want to keep the lower-level array-oriented governed path,
-- materialize from the optimized array reveal view instead.
CREATE OR REFRESH MATERIALIZED VIEW plaintext_internal_reveal_array_gold
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

