-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog SQL Warehouse Reveal Functions and Views - plaintext_protected_none Embedded Config
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create persistent Unity Catalog Python reveal functions for the `none` policy path
-- MAGIC - embed the relevant config directly in the function bodies
-- MAGIC - avoid runtime reads of `/Volumes/.../udfConfig.properties`
-- MAGIC - create persistent views that inject `session_user()`
-- MAGIC - keep the final row-shaped view as the customer-facing artifact
-- MAGIC
-- MAGIC Recommendation:
-- MAGIC - customer-facing view:
-- MAGIC   `my_catalog.my_schema.v_plaintext_final_none_reveal_flat_uc_embedded`
-- MAGIC - lower-level array validation view:
-- MAGIC   `my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded`
-- MAGIC
-- MAGIC Notes:
-- MAGIC - this script now uses the current `thales_databricks_integration` package
-- MAGIC - the array view uses one rowset-style UC Python call per batch row rather than one call per protected column

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
  value STRING,
  datatype STRING,
  object_name STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_reveal_by_object_and_column_embedded

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "none",
    "keymetadatalocation": "none",
    "BATCH_SIZE": "10000",
    "CRDP_API_VERSION": "v2",
    "CRDP_SSL_ENABLED": "false",
    "CRDP_SSL_VERIFY_SERVER": "false",
    "CRDP_CONNECT_TIMEOUT_MS": "10000",
    "CRDP_READ_TIMEOUT_MS": "30000",
    "SPARK_GROUP_SIZE": "1000",
    "CRDP_V2_MAX_ITEMS_PER_REQUEST": "1000",
    "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST": "50",
    "CRDP_V2_ENABLE_MULTI_POLICY": "true",
    "COLUMN_PROFILES": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none,balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none_arrays": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.none": "char-none",
    "TAG.char.none.policyType": "none",
    "TAG.nbr.none": "nbr-none",
    "TAG.nbr.none.policyType": "none"
}

return uc_reveal_by_object_and_column_embedded(
    value,
    object_name,
    column_name,
    PROPERTIES,
    reveal_user=reveal_user,
    transport_mode="real",
)
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_bulk_by_object_and_column_none_uc_embedded(
  values ARRAY<STRING>,
  datatype STRING,
  object_name STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_reveal_bulk_by_object_and_column_embedded

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "none",
    "keymetadatalocation": "none",
    "BATCH_SIZE": "10000",
    "CRDP_API_VERSION": "v2",
    "CRDP_SSL_ENABLED": "false",
    "CRDP_SSL_VERIFY_SERVER": "false",
    "CRDP_CONNECT_TIMEOUT_MS": "10000",
    "CRDP_READ_TIMEOUT_MS": "30000",
    "SPARK_GROUP_SIZE": "1000",
    "CRDP_V2_MAX_ITEMS_PER_REQUEST": "1000",
    "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST": "50",
    "CRDP_V2_ENABLE_MULTI_POLICY": "true",
    "COLUMN_PROFILES": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none,balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none_arrays": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.none": "char-none",
    "TAG.char.none.policyType": "none",
    "TAG.nbr.none": "nbr-none",
    "TAG.nbr.none.policyType": "none"
}

return uc_reveal_bulk_by_object_and_column_embedded(
    values,
    object_name,
    column_name,
    PROPERTIES,
    reveal_user=reveal_user,
    transport_mode="real",
)
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_rowset_none_uc_embedded(
  address_values ARRAY<STRING>,
  email_values ARRAY<STRING>,
  creditcard_values ARRAY<STRING>,
  creditcardcode_values ARRAY<STRING>,
  ssn_values ARRAY<STRING>,
  object_name STRING,
  reveal_user STRING
)
RETURNS STRUCT<
  address_decrypted: ARRAY<STRING>,
  email_decrypted: ARRAY<STRING>,
  creditcard_decrypted: ARRAY<STRING>,
  creditcardcode_decrypted: ARRAY<STRING>,
  ssn_decrypted: ARRAY<STRING>
>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_reveal_rowset_embedded

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "none",
    "keymetadatalocation": "none",
    "BATCH_SIZE": "10000",
    "CRDP_API_VERSION": "v2",
    "CRDP_SSL_ENABLED": "false",
    "CRDP_SSL_VERIFY_SERVER": "false",
    "CRDP_CONNECT_TIMEOUT_MS": "10000",
    "CRDP_READ_TIMEOUT_MS": "30000",
    "SPARK_GROUP_SIZE": "1000",
    "CRDP_V2_MAX_ITEMS_PER_REQUEST": "1000",
    "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST": "50",
    "CRDP_V2_ENABLE_MULTI_POLICY": "true",
    "COLUMN_PROFILES": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none,balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_none_arrays": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.none": "char-none",
    "TAG.char.none.policyType": "none",
    "TAG.nbr.none": "nbr-none",
    "TAG.nbr.none.policyType": "none"
}

return uc_reveal_rowset_embedded(
    {
        "address": address_values,
        "email": email_values,
        "creditcard": creditcard_values,
        "creditcardcode": creditcardcode_values,
        "ssn": ssn_values,
    },
    object_name,
    PROPERTIES,
    reveal_user=reveal_user,
    transport_mode="real",
)
$$;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_none_reveal_uc_embedded AS
SELECT
  custid,
  name,
  my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
    CAST(address AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_none',
    'address',
    session_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
    CAST(email AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_none',
    'email',
    session_user()
  ) AS email,
  dob,
  CAST(
    my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
      CAST(creditcard AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none',
      'creditcard',
      session_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
      CAST(creditcardcode AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none',
      'creditcardcode',
      session_user()
    ) AS INT
  ) AS creditcardcode,
  my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded(
    CAST(ssn AS STRING),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_none',
    'ssn',
    session_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_none;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded AS
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
    my_catalog.my_schema.thales_reveal_rowset_none_uc_embedded(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING)),
      'my_catalog.my_schema.plaintext_protected_none_arrays',
      session_user()
    ) AS decrypted
  FROM my_catalog.my_schema.plaintext_protected_none_arrays
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
  transform(decrypted.creditcard_decrypted, x -> CAST(x AS DECIMAL(25,0))) AS creditcard_decrypted,
  transform(decrypted.creditcardcode_decrypted, x -> CAST(x AS INT)) AS creditcardcode_decrypted,
  decrypted.ssn_decrypted AS ssn_decrypted
FROM decrypted_batches;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_final_none_reveal_flat_uc_embedded AS
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
  FROM my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded
);

-- COMMAND ----------

GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_by_object_and_column_none_uc_embedded TO `thales_udf_deployers`;
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_bulk_by_object_and_column_none_uc_embedded TO `thales_udf_deployers`;
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_rowset_none_uc_embedded TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_none_reveal_uc_embedded TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_none_reveal_flat_uc_embedded TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `analyst`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_none_reveal_uc_embedded TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_none_reveal_flat_uc_embedded TO `analyst`;

-- COMMAND ----------

SELECT * FROM my_catalog.my_schema.v_plaintext_protected_none_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_none_array_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_none_reveal_flat_uc_embedded LIMIT 10;
