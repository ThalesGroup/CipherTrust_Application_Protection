-- Databricks notebook source
-- MAGIC %md
-- MAGIC # SQL Warehouse TLS Debug Function Sample
-- MAGIC
-- MAGIC Use this sample to inspect what the SQL Warehouse Python UDF runtime is
-- MAGIC actually loading for TLS materials before making a CRDP request.
-- MAGIC
-- MAGIC This current version is self-contained and aligned to the
-- MAGIC `thales_databricks_integration` project. It does not depend on the old
-- MAGIC `thales_databricks_udf.crdp_udfs.debug_tls_materials` helper.
-- MAGIC
-- MAGIC It returns a JSON string with fields such as:
-- MAGIC - whether CA/client PEM base64 properties are present
-- MAGIC - whether temp files were written from embedded base64 content
-- MAGIC - whether Python `ssl` can load the CA bundle
-- MAGIC - whether Python `ssl` can load the client cert/key pair
-- MAGIC - resolved temp file paths and sizes
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
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
AS $$
import base64
import json
import ssl
import tempfile
from pathlib import Path

PROPERTIES = {
    "CRDPIP": "your-crdp-ip",
    "CRDPPORT": "8091",
    "CRDP_SSL_ENABLED": "true",
    "CRDP_SSL_VERIFY_SERVER": "true",
    "RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS": "no",
    # Paste the generated TLS properties here, especially:
    # - CRDP_CA_CERT_PEM_B64
    # - CRDP_CLIENT_CERT_PEM_B64
    # - CRDP_CLIENT_KEY_PEM_B64
}


def _as_bool(value, default=False):
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    return default



def _materialize_if_needed(props):
    debug = {
        "has_ca_cert_pem_b64": bool(props.get("CRDP_CA_CERT_PEM_B64")),
        "has_client_cert_pem_b64": bool(props.get("CRDP_CLIENT_CERT_PEM_B64")),
        "has_client_key_pem_b64": bool(props.get("CRDP_CLIENT_KEY_PEM_B64")),
        "materialized_temp_dir": None,
    }

    resolved = dict(props)
    if all(
        resolved.get(key)
        for key in [
            "CRDP_CA_CERT_PEM_B64",
            "CRDP_CLIENT_CERT_PEM_B64",
            "CRDP_CLIENT_KEY_PEM_B64",
        ]
    ):
        temp_dir = tempfile.mkdtemp(prefix="thales_sql_wh_tls_")
        debug["materialized_temp_dir"] = temp_dir
        file_specs = [
            ("CRDP_CA_CERT_PEM_B64", "CRDP_CA_CERT_PATH", "crdp-ca.pem"),
            ("CRDP_CLIENT_CERT_PEM_B64", "CRDP_CLIENT_CERT_PATH", "crdp-client-cert.pem"),
            ("CRDP_CLIENT_KEY_PEM_B64", "CRDP_CLIENT_KEY_PATH", "crdp-client-key.pem"),
        ]
        for source_key, target_key, file_name in file_specs:
            target_path = Path(temp_dir) / file_name
            target_path.write_bytes(base64.b64decode(resolved[source_key]))
            resolved[target_key] = str(target_path)

    return resolved, debug



def _tls_debug(props):
    resolved, debug = _materialize_if_needed(props)
    ssl_enabled = _as_bool(resolved.get("CRDP_SSL_ENABLED"), False)
    verify_server = _as_bool(resolved.get("CRDP_SSL_VERIFY_SERVER"), True)

    ca_path = Path(resolved["CRDP_CA_CERT_PATH"]) if resolved.get("CRDP_CA_CERT_PATH") else None
    cert_path = Path(resolved["CRDP_CLIENT_CERT_PATH"]) if resolved.get("CRDP_CLIENT_CERT_PATH") else None
    key_path = Path(resolved["CRDP_CLIENT_KEY_PATH"]) if resolved.get("CRDP_CLIENT_KEY_PATH") else None

    debug.update(
        {
            "CRDPIP": resolved.get("CRDPIP"),
            "CRDPPORT": resolved.get("CRDPPORT"),
            "CRDP_SSL_ENABLED": ssl_enabled,
            "CRDP_SSL_VERIFY_SERVER": verify_server,
            "resolved_ca_cert_path": str(ca_path) if ca_path else None,
            "resolved_client_cert_path": str(cert_path) if cert_path else None,
            "resolved_client_key_path": str(key_path) if key_path else None,
            "resolved_ca_cert_exists": ca_path.exists() if ca_path else False,
            "resolved_client_cert_exists": cert_path.exists() if cert_path else False,
            "resolved_client_key_exists": key_path.exists() if key_path else False,
            "resolved_ca_cert_size": ca_path.stat().st_size if ca_path and ca_path.exists() else None,
            "resolved_client_cert_size": cert_path.stat().st_size if cert_path and cert_path.exists() else None,
            "resolved_client_key_size": key_path.stat().st_size if key_path and key_path.exists() else None,
            "ca_bundle_load_ok": None,
            "client_cert_chain_load_ok": None,
            "ca_bundle_load_error": None,
            "client_cert_chain_load_error": None,
        }
    )

    if ssl_enabled:
        try:
            if verify_server:
                ssl.create_default_context(cafile=str(ca_path) if ca_path else None)
            else:
                insecure_context = ssl._create_unverified_context()
                insecure_context.check_hostname = False
                insecure_context.verify_mode = ssl.CERT_NONE
            debug["ca_bundle_load_ok"] = True
        except Exception as exc:
            debug["ca_bundle_load_ok"] = False
            debug["ca_bundle_load_error"] = repr(exc)

        try:
            if cert_path:
                context = ssl.create_default_context()
                context.load_cert_chain(
                    certfile=str(cert_path),
                    keyfile=str(key_path) if key_path else None,
                )
            debug["client_cert_chain_load_ok"] = True
        except Exception as exc:
            debug["client_cert_chain_load_ok"] = False
            debug["client_cert_chain_load_error"] = repr(exc)
    else:
        debug["ca_bundle_load_ok"] = True
        debug["client_cert_chain_load_ok"] = True

    return debug


return json.dumps(_tls_debug(PROPERTIES), sort_keys=True)
$$;

-- COMMAND ----------

SELECT my_catalog.my_schema.thales_tls_debug_uc_embedded();
