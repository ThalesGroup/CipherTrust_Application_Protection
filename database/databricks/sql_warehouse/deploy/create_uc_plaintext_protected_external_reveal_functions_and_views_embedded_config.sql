-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog SQL Warehouse Reveal Functions and Views - plaintext_protected_external Embedded Config
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create persistent Unity Catalog Python functions for external-policy protect and reveal operations
-- MAGIC - preserve sibling `*_header` handling for external policies
-- MAGIC - embed the relevant config directly in the function body
-- MAGIC - avoid runtime reads of `/Volumes/.../udfConfig.properties`
-- MAGIC - create a persistent reveal view for `plaintext_protected_external`
-- MAGIC
-- MAGIC Notes:
-- MAGIC - this script now targets the current `thales_databricks_integration` package
-- MAGIC - the external path is still scalar/view oriented in SQL Warehouse
-- MAGIC - there is not yet a current rowset-style external-header reveal helper in `uc.py`,
-- MAGIC   so this deploy script keeps the external-header logic inline inside the UC Python functions

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
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration import IntegrationConfig, reveal_rows

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "external",
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
    "COLUMN_PROFILES": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_external": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "external_table_header_value": "header",
    "external_table_header_delimiter": "_",
    "TAG.char.external": "char-external",
    "TAG.char.external.policyType": "external",
    "TAG.nbr.external": "test-nbr-nbr-external",
    "TAG.nbr.external.policyType": "external"
}

if value is None:
    return None

config = IntegrationConfig.from_dict(PROPERTIES)
header_column_name = config.resolve_external_header_column_name(column_name)
row = {column_name: value}
if header_column_name and external_header is not None:
    row[header_column_name] = external_header

result = reveal_rows(
    rows=[row],
    object_name=object_name,
    sensitive_columns=[column_name],
    config=config,
    reveal_user=reveal_user,
)

if not result.rows:
    return value
return result.rows[0].get(column_name)
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
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration import IntegrationConfig, protect_rows

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "external",
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
    "COLUMN_PROFILES": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "protect.object.my_catalog.my_schema.plaintext_protected_external": "email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external",
    "external_table_header_value": "header",
    "external_table_header_delimiter": "_",
    "TAG.char.external": "char-external",
    "TAG.char.external.policyType": "external",
    "TAG.nbr.external": "test-nbr-nbr-external",
    "TAG.nbr.external.policyType": "external"
}

if value is None:
    return {"protected_value": None, "external_header": None}

config = IntegrationConfig.from_dict(PROPERTIES)
header_column_name = config.resolve_external_header_column_name(column_name)
result = protect_rows(
    rows=[{column_name: value}],
    object_name=object_name,
    sensitive_columns=[column_name],
    config=config,
)

if not result.rows:
    return {"protected_value": value, "external_header": None}

protected_row = result.rows[0]
return {
    "protected_value": protected_row.get(column_name),
    "external_header": protected_row.get(header_column_name) if header_column_name else None,
}
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
