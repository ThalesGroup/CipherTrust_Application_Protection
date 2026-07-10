-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog Python UDF Setup - Volume Config Example
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create persistent Unity Catalog Python functions backed by the new wheel
-- MAGIC - use a runtime `config_path` argument that points to `udfConfig.properties`
-- MAGIC - show a simple volume-config example for UC-enabled environments
-- MAGIC
-- MAGIC Important:
-- MAGIC - this is the volume-config example
-- MAGIC - for SQL Warehouse, the embedded-config example is usually the safer primary pattern
-- MAGIC - update the function names, wheel path, and config path placeholders before use

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_uc_protect_by_object_and_column(
  value STRING,
  object_name STRING,
  column_name STRING,
  config_path STRING
)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_protect_by_object_and_column

return uc_protect_by_object_and_column(
    value,
    object_name,
    column_name,
    config_path,
)
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
  value STRING,
  object_name STRING,
  column_name STRING,
  config_path STRING,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_reveal_by_object_and_column

return uc_reveal_by_object_and_column(
    value,
    object_name,
    column_name,
    config_path,
    reveal_user=reveal_user,
)
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_uc_protect_bulk_by_object_and_column(
  values ARRAY<STRING>,
  object_name STRING,
  column_name STRING,
  config_path STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_protect_bulk_by_object_and_column

return uc_protect_bulk_by_object_and_column(
    values,
    object_name,
    column_name,
    config_path,
)
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_uc_reveal_bulk_by_object_and_column(
  values ARRAY<STRING>,
  object_name STRING,
  column_name STRING,
  config_path STRING,
  reveal_user STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
from thales_databricks_integration.uc import uc_reveal_bulk_by_object_and_column

return uc_reveal_bulk_by_object_and_column(
    values,
    object_name,
    column_name,
    config_path,
    reveal_user=reveal_user,
)
$$;

-- COMMAND ----------

-- Replace the config path below with your actual Unity Catalog volume path.
CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc AS
SELECT
  custid,
  name,
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    CAST(address AS STRING),
    'my_catalog.my_schema.plaintext_protected_internal',
    'address',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties',
    session_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    CAST(email AS STRING),
    'my_catalog.my_schema.plaintext_protected_internal',
    'email',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties',
    session_user()
  ) AS email,
  dob,
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    CAST(creditcard AS STRING),
    'my_catalog.my_schema.plaintext_protected_internal',
    'creditcard',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties',
    session_user()
  ) AS creditcard,
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    CAST(creditcardcode AS STRING),
    'my_catalog.my_schema.plaintext_protected_internal',
    'creditcardcode',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties',
    session_user()
  ) AS creditcardcode,
  my_catalog.my_schema.thales_uc_reveal_by_object_and_column(
    CAST(ssn AS STRING),
    'my_catalog.my_schema.plaintext_protected_internal',
    'ssn',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties',
    session_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;

-- COMMAND ----------

SELECT
  custid,
  my_catalog.my_schema.thales_uc_protect_by_object_and_column(
    email,
    'my_catalog.my_schema.plaintext_protected_internal',
    'email',
    '/Volumes/my_catalog/my_schema/volume_forjars/udfConfig.properties'
  ) AS email_token
FROM my_catalog.my_schema.plaintext_plaintext;
