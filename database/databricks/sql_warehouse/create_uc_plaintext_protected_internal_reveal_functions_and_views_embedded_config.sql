-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Unity Catalog SQL Warehouse Reveal Functions and Views - plaintext_protected_internal Embedded Config
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create persistent Unity Catalog Python functions for reveal operations
-- MAGIC - embed the relevant UDF config directly in the function bodies
-- MAGIC - avoid runtime reads of `/Volumes/.../udfConfig.properties`
-- MAGIC - create persistent views that inject `session_user()`
-- MAGIC - cast revealed numeric values back to the target schema where needed
-- MAGIC
-- MAGIC Prerequisites:
-- MAGIC - a Pro or Serverless SQL Warehouse, or a UC-enabled cluster with Python UDF support
-- MAGIC - the wheel uploaded to a UC volume
-- MAGIC - update the dependency path below if your wheel name/version changes

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
  value STRING,
  datatype STRING,
  column_name STRING,
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

if value is None:
    return None

result = thales_crdp_python_function_bulk(
    [value],
    "revealbulk",
    datatype,
    column_name=column_name,
    reveal_user=reveal_user,
    properties=PROPERTIES,
)

return result[0] if result else None
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
  values ARRAY<STRING>,
  datatype STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.1-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
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
$$;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded AS
SELECT
  custid,
  name,
  my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
    CAST(address AS STRING),
    'char',
    'address',
    session_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
    CAST(email AS STRING),
    'char',
    'email',
    session_user()
  ) AS email,
  dob,
  CAST(
    my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
      CAST(creditcard AS STRING),
      'nbr',
      'creditcard',
      session_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
      CAST(creditcardcode AS STRING),
      'nbr',
      'creditcardcode',
      session_user()
    ) AS INT
  ) AS creditcardcode,
  my_catalog.my_schema.thales_reveal_by_column_uc_embedded(
    CAST(ssn AS STRING),
    'nbr',
    'ssn',
    session_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded AS
SELECT
  batch_id,
  custid_array,
  name_array,
  my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
    transform(address_array, x -> CAST(x AS STRING)),
    'char',
    'address',
    session_user()
  ) AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
    transform(email_array, x -> CAST(x AS STRING)),
    'char',
    'email',
    session_user()
  ) AS email_decrypted,
  dob_array,
  transform(
    my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
      transform(creditcard_array, x -> CAST(x AS STRING)),
      'nbr',
      'creditcard',
      session_user()
    ),
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      'nbr',
      'creditcardcode',
      session_user()
    ),
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded(
    transform(ssn_array, x -> CAST(x AS STRING)),
    'nbr',
    'ssn',
    session_user()
  ) AS ssn_decrypted
FROM my_catalog.my_schema.plaintext_protected_internal_arrays;

-- COMMAND ----------

CREATE OR REPLACE VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded AS
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
  FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded
);

-- COMMAND ----------

-- Replace `thales_udf_deployers` with the admin/deployer group that should be
-- able to run both the functions and the views directly.
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_by_column_uc_embedded TO `thales_udf_deployers`;
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.thales_reveal_bulk_by_column_uc_embedded TO `thales_udf_deployers`;

GRANT USE CATALOG ON CATALOG my_catalog TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded TO `thales_udf_deployers`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded TO `thales_udf_deployers`;

-- Analysts should be able to query the governed views, but should not receive
-- direct EXECUTE on the underlying functions.
GRANT USE CATALOG ON CATALOG my_catalog TO `analyst`;
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded TO `analyst`;
GRANT SELECT ON VIEW my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded TO `analyst`;

-- COMMAND ----------

SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_protected_internal_array_reveal_uc_embedded LIMIT 10;
SELECT * FROM my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded LIMIT 10;
