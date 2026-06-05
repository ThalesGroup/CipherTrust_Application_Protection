-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog SQL Warehouse Reveal Functions and Views - plaintext_protected_external Embedded Config
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create persistent Unity Catalog Python functions for external-policy protect and reveal operations
-- MAGIC - pass the sibling `*_header` column value to CRDP as the external metadata/header
-- MAGIC - embed the relevant UDF config directly in the function body
-- MAGIC - avoid runtime reads of `/Volumes/.../udfConfig.properties`
-- MAGIC - create a persistent reveal view for `plaintext_protected_external`
-- MAGIC
-- MAGIC Prerequisite:
-- MAGIC - this script uses the `ENVIRONMENT` clause for a custom wheel dependency
-- MAGIC - that requires a Unity Catalog Python-UDF-capable SQL Warehouse
-- MAGIC - if Databricks throws a syntax error at `ENVIRONMENT`, the warehouse is
-- MAGIC   likely not on a supported SQL Warehouse type/runtime for this feature yet

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
  value STRING,
  external_header STRING,
  datatype STRING,
  object_name STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.7-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk_by_object

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
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
    "COLUMN_PROFILES": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_internal": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.plaintext_protected_external": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_none": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_internal_arrays": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.plaintext_protected_external_arrays": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_none_arrays": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_internal": "balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_external": "balance|tag.nbr.external,amount|tag.nbr.external,fee|tag.nbr.external",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_none": "balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_internal_arrays": "balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_external_arrays": "balance|tag.nbr.external,amount|tag.nbr.external,fee|tag.nbr.external",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_none_arrays": "balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "external_table_header_value": "header",
    "external_table_header_delimiter": "_",
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

if value is None:
    return None

result = thales_crdp_python_function_bulk_by_object(
    [value],
    "revealbulk",
    datatype,
    object_name,
    column_name=column_name,
    reveal_user=reveal_user,
    external_versions=[external_header],
    properties=PROPERTIES,
)

return result[0] if result else None
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_protect_by_object_and_column_with_external_header_uc_embedded(
  value STRING,
  datatype STRING,
  object_name STRING,
  column_name STRING
)
RETURNS STRUCT<protected_value: STRING, external_header: STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.7-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_protect_with_external_header_by_object

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
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
    "COLUMN_PROFILES": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_internal": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.plaintext_protected_external": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_none": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.plaintext_protected_internal_arrays": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.plaintext_protected_external_arrays": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_none_arrays": "email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_internal": "balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_external": "balance|tag.nbr.external,amount|tag.nbr.external,fee|tag.nbr.external",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_none": "balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_internal_arrays": "balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_external_arrays": "balance|tag.nbr.external,amount|tag.nbr.external,fee|tag.nbr.external",
    "protect.object.my_catalog.my_schema.account_balance_numbers_protected_none_arrays": "balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none",
    "external_table_header_value": "header",
    "external_table_header_delimiter": "_",
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

if value is None:
    return {"protected_value": None, "external_header": None}

return thales_crdp_python_protect_with_external_header_by_object(
    value,
    datatype,
    object_name,
    column_name=column_name,
    properties=PROPERTIES,
)
$$;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_external_reveal_uc_embedded AS
SELECT
  custid,
  name,
  my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
    CAST(address AS STRING),
    CAST(address_header AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_external',
    'address',
    session_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
    CAST(email AS STRING),
    CAST(email_header AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_external',
    'email',
    session_user()
  ) AS email,
  dob,
  CAST(
    my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
      CAST(creditcard AS STRING),
      CAST(creditcard_header AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external',
      'creditcard',
      session_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
      CAST(creditcardcode AS STRING),
      CAST(creditcardcode_header AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external',
      'creditcardcode',
      session_user()
    ) AS INT
  ) AS creditcardcode,
  my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded(
    CAST(ssn AS STRING),
    CAST(ssn_header AS STRING),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_external',
    'ssn',
    session_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_external;

-- COMMAND ----------

-- Example external protect pattern:
-- CREATE OR REPLACE TABLE my_catalog.my_schema.some_external_protected_table AS
-- SELECT
--   id,
--   protected_email.protected_value AS email,
--   protected_email.external_header AS email_header
-- FROM (
--   SELECT
--     id,
--     my_catalog.my_schema.thales_protect_by_object_and_column_with_external_header_uc_embedded(
--       CAST(email AS STRING),
--       'char',
--       'my_catalog.my_schema.some_external_protected_table',
--       'email'
--     ) AS protected_email
--   FROM my_catalog.my_schema.some_plaintext_table
-- ) s;

-- COMMAND ----------

GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_protect_by_object_and_column_with_external_header_uc_embedded TO `thales_udf_deployers`;
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_by_object_and_column_with_external_header_uc_embedded TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_external_reveal_uc_embedded TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `analyst`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_external_reveal_uc_embedded TO `analyst`;

-- COMMAND ----------

SELECT *
FROM my_catalog.my_schema.v_plaintext_protected_external_reveal_uc_embedded
ORDER BY custid;
