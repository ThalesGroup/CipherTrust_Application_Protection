-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse Python UDF Overhead Isolation
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - separate UC Python UDF runtime overhead from real CRDP network time
-- MAGIC - compare a no-op Python UDF, a stub rowset reveal, and a real rowset reveal
-- MAGIC - determine whether the remaining slowness is mostly Databricks SQL Python UDF overhead or CRDP connectivity/latency
-- MAGIC
-- MAGIC Operational guidance:
-- MAGIC - this is an engineering diagnostic, not a normal deployment or customer benchmark script
-- MAGIC - run it only when you need to prove whether the bottleneck is:
-- MAGIC   - UC Python UDF runtime overhead
-- MAGIC   - wheel/planner/executor overhead
-- MAGIC   - or real CRDP network time

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_debug_noop_rowset_uc_v2(
  address_values ARRAY<STRING>,
  email_values ARRAY<STRING>,
  creditcard_values ARRAY<STRING>,
  creditcardcode_values ARRAY<STRING>,
  ssn_values ARRAY<STRING>
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
AS $$
return {
    "address_decrypted": address_values,
    "email_decrypted": email_values,
    "creditcard_decrypted": creditcard_values,
    "creditcardcode_decrypted": creditcardcode_values,
    "ssn_decrypted": ssn_values,
}
$$;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_debug_stub_rowset_uc_embedded_v2(
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
    "CRDPIP": "unused-in-stub-mode",
    "CRDPPORT": "8090",
    "CRDPUSER": "admin",
    "DEFAULTREVEALUSER": "admin",
    "DEFAULTMETADATA": "1001000",
    "DEFAULTMODE": "internal",
    "keymetadatalocation": "internal",
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
    "COLUMN_PROFILES": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "protect.object.my_catalog.my_schema.plaintext_protected_internal_arrays": "email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal",
    "column.ssn.metadata": "1002000",
    "column.creditcard.metadata": "1002000",
    "column.creditcardcode.metadata": "1002000",
    "TAG.char.internal": "char-internal",
    "TAG.char.internal.policyType": "internal",
    "TAG.nbr.internal": "nbr-nbr-internal",
    "TAG.nbr.internal.policyType": "internal"
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
    transport_mode="stub",
)
$$;

-- COMMAND ----------

-- No-op Python UDF baseline.
SELECT
  batch_id,
  size(decrypted.email_decrypted) AS email_count
FROM (
  SELECT
    batch_id,
    my_catalog.my_schema.thales_debug_noop_rowset_uc_v2(
      transform(address_array, x -> CAST(x AS STRING)),
      transform(email_array, x -> CAST(x AS STRING)),
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(ssn_array, x -> CAST(x AS STRING))
    ) AS decrypted
  FROM my_catalog.my_schema.plaintext_protected_internal_arrays
  WHERE batch_id = 0
) s;

-- COMMAND ----------

-- Wheel import + planner + executor overhead without CRDP network.
SELECT
  batch_id,
  size(decrypted.email_decrypted) AS email_count
FROM (
  SELECT
    batch_id,
    my_catalog.my_schema.thales_debug_stub_rowset_uc_embedded_v2(
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

-- Full real path.
SELECT
  batch_id,
  size(decrypted.email_decrypted) AS email_count
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
