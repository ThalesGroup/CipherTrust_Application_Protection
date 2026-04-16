-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog SQL Warehouse Reveal Functions and Views - plaintext_protected_internal Embedded Config Optimized
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - keep the existing embedded-config path intact
-- MAGIC - add an optimized array reveal function that decrypts all sensitive arrays in one UC Python UDF call
-- MAGIC - reduce SafeSpark/Python UDF invocations from 5 per batch row to 1 per batch row
-- MAGIC - preserve the same CRDP behavior by still calling the same per-column bulk reveal helper inside Python
-- MAGIC
-- MAGIC Performance model:
-- MAGIC - previous array view: 5 Databricks UC Python UDF calls + 5 CRDP bulk calls per batch row
-- MAGIC - optimized array view: 1 Databricks UC Python UDF call + 5 CRDP bulk calls per batch row
-- MAGIC - this reduces Python/SafeSpark overhead, but still keeps one CRDP revealbulk call per protected column
-- MAGIC
-- MAGIC Memory guidance:
-- MAGIC - the optimized path temporarily holds all bundled input arrays, all decrypted output arrays,
-- MAGIC   and one JSON payload in a single Python invocation
-- MAGIC - keep batch sizes moderate and watch SQL Warehouse query profile metrics such as sandbox peak memory
-- MAGIC - rough sizing rule:
-- MAGIC   peak_bytes ~= batch_size * sum(avg_input_bytes_per_col + avg_output_bytes_per_col) * 3
-- MAGIC - the factor of 3 is only a starting estimate and covers Python/object/JSON overhead loosely
-- MAGIC - if memory grows too much, reduce batch size before changing the reveal logic

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized(
  address_values ARRAY<STRING>,
  email_values ARRAY<STRING>,
  creditcard_values ARRAY<STRING>,
  creditcardcode_values ARRAY<STRING>,
  ssn_values ARRAY<STRING>,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
import json

from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk

PROPERTIES = {
    "CRDPIP": "20.221.216.246",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "external",
    "BADDATATAG": "999999999",
    "RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS": "yes",
    "DEFAULTINTERNALCHARPOLICY": "char-internal",
    "DEFAULTINTERNALNBRNBRPOLICY": "nbr-nbr-internal",
    "DEFAULTEXTERNALCHARPOLICY": "char-external",
    "DEFAULTEXTERNALNBRNBRPOLICY": "test-nbr-nbr-external",
    "COLUMN_PROFILES": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal,balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.external": "char-external",
    "TAG.char.external.policyType": "external",
    "TAG.nbr.external": "test-nbr-nbr-external",
    "TAG.nbr.external.policyType": "external",
    "TAG.char.internal": "char-internal",
    "TAG.char.internal.policyType": "internal",
    "TAG.nbr.internal": "nbr-nbr-internal",
    "TAG.nbr.internal.policyType": "internal",
    "TAG.nbr.none": "nbr-none",
    "TAG.nbr.none.policyType": "none",
    "TAG.char.none": "char-none",
    "TAG.char.none.policyType": "none",
}


def reveal(values, datatype, column_name):
    if values is None:
        return None
    return thales_crdp_python_function_bulk(
        values,
        "revealbulk",
        datatype,
        column_name=column_name,
        reveal_user=reveal_user,
        properties=PROPERTIES,
    )


result = {
    "address_decrypted": reveal(address_values, "char", "address"),
    "email_decrypted": reveal(email_values, "char", "email"),
    "creditcard_decrypted_raw": reveal(creditcard_values, "nbr", "creditcard"),
    "creditcardcode_decrypted_raw": reveal(creditcardcode_values, "nbr", "creditcardcode"),
    "ssn_decrypted": reveal(ssn_values, "nbr", "ssn"),
}

return json.dumps(result)
$$;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized AS
WITH bundled AS (
  SELECT
    batch_id,
    custid_array,
    name_array,
    city_array,
    state_array,
    zip_array,
    phone_array,
    dob_array,
    my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING)),
      session_user()
    ) AS decrypted_payload
  FROM my_catalog.my_schema.plaintext_protected_internal_arrays
),
parsed AS (
  SELECT
    batch_id,
    custid_array,
    name_array,
    city_array,
    state_array,
    zip_array,
    phone_array,
    dob_array,
    from_json(
      decrypted_payload,
      'STRUCT<address_decrypted:ARRAY<STRING>,email_decrypted:ARRAY<STRING>,creditcard_decrypted_raw:ARRAY<STRING>,creditcardcode_decrypted_raw:ARRAY<STRING>,ssn_decrypted:ARRAY<STRING>>'
    ) AS decrypted
  FROM bundled
)
SELECT
  batch_id,
  custid_array,
  name_array,
  decrypted.address_decrypted AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  decrypted.email_decrypted AS email_decrypted,
  dob_array,
  transform(
    decrypted.creditcard_decrypted_raw,
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    decrypted.creditcardcode_decrypted_raw,
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  decrypted.ssn_decrypted AS ssn_decrypted
FROM parsed;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized AS
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
  exploded.creditcard_decrypted AS creditcard,
  exploded.creditcardcode_decrypted AS creditcardcode,
  exploded.ssn_decrypted AS ssn
FROM (
  SELECT explode(
    arrays_zip(
      custid_array,
      name_array,
      address_decrypted,
      city_array,
      state_array,
      zip_array,
      phone_array,
      email_decrypted,
      dob_array,
      creditcard_decrypted,
      creditcardcode_decrypted,
      ssn_decrypted
    )
  ) AS exploded
  FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized
);

-- COMMAND ----------

GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_bundle_by_columns_uc_embedded_optimized TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized TO `thales_udf_deployers`;

-- Analysts should be able to query the governed views, but should not receive
-- direct EXECUTE on the underlying optimized bundled function.
GRANT USE CATALOG ON CATALOG my_catalog TO `analyst`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized TO `analyst`;

-- COMMAND ----------

SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded_optimized LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_optimized LIMIT 10;
