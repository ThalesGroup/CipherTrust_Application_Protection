-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse TLS Debug Function Sample
-- MAGIC
-- MAGIC Use this sample to inspect what the SQL Warehouse Python UDF runtime is
-- MAGIC actually loading for TLS materials before making a CRDP request.
-- MAGIC
-- MAGIC It returns a JSON string with fields such as:
-- MAGIC - whether CA/client PEM base64 properties are present
-- MAGIC - whether temp files were written
-- MAGIC - whether Python `ssl` can load the CA bundle
-- MAGIC - whether Python `ssl` can load the client cert/key pair
-- MAGIC
-- MAGIC Replace the `PROPERTIES = {...}` block with the same generated TLS
-- MAGIC properties used by your embedded reveal functions.

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE FUNCTION my_catalog.my_schema.thales_tls_debug_uc_embedded()
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.7-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
import json

from thales_databricks_udf.crdp_udfs import debug_tls_materials

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8091",
    "CRDP_SSL_ENABLED": "true",
    "CRDP_SSL_VERIFY_SERVER": "true",
    "RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS": "no"
    # Paste the generated TLS properties here, especially:
    # - CRDP_CA_CERT_PEM_B64
    # - CRDP_CLIENT_CERT_PEM_B64
    # - CRDP_CLIENT_KEY_PEM_B64
}

return json.dumps(debug_tls_materials(properties=PROPERTIES), sort_keys=True)
$$;

-- COMMAND ----------

SELECT my_catalog.my_schema.thales_tls_debug_uc_embedded();
