-- LEGACY: Databricks SQL Warehouse deployment script for Thales CRDP v1
--
-- This script is ready to customize with the verified wheel artifact name:
--   thales_databricks_udf-0.1.0-py3-none-any.whl
--
-- Before running:
-- 1. Upload the wheel to a Unity Catalog volume path such as:
--    /Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.0-py3-none-any.whl
-- 2. Replace the example CRDP settings below.
-- 3. Update the example policy mappings to match the target customer profiles.
--
-- Example target namespace used in this script:
--   main.security

CREATE OR REPLACE FUNCTION main.security.thales_crdp_scalar_legacy(
  value STRING,
  mode STRING,
  datatype STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
COMMENT 'Thales CRDP v1 scalar protect/reveal using legacy profile configuration.'
AS $$
import json
import urllib.request
from decimal import Decimal, InvalidOperation

CRDP_IP = "20.221.216.246"
CRDP_PORT = "8090"
PROTECTION_PROFILE = "alpha-external"
KEY_METADATA_LOCATION = "external"
KEYMETADATA = "1001000"
REVEAL_USER = "admin"
RETURN_CIPHERTEXT = True
BADDATATAG = "99999999999"

def check_valid(v, datatype):
    if v is None:
        return BADDATATAG
    s = str(v).strip()
    if not s:
        return BADDATATAG
    if len(s) < 2:
        return BADDATATAG + s
    if datatype.lower() != "char":
        try:
            n = Decimal(s)
            if Decimal(-9) <= n <= Decimal(-1):
                return BADDATATAG
        except (InvalidOperation, ValueError):
            return BADDATATAG
    return s

def post_json(path, payload):
    req = urllib.request.Request(
        f"http://{CRDP_IP}:{CRDP_PORT}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

if value is None:
    return None

normalized = check_valid(value, datatype)

try:
    if mode.lower() == "protect":
        result = post_json("/v1/protect", {
            "protection_policy_name": PROTECTION_PROFILE,
            "data": normalized,
        }).get("protected_data")
        return result

    if mode.lower() != "reveal":
        raise ValueError("mode must be protect or reveal")

    payload = {
        "protection_policy_name": PROTECTION_PROFILE,
        "protected_data": normalized,
        "username": REVEAL_USER,
    }
    if KEY_METADATA_LOCATION.lower() == "external":
        payload["external_version"] = KEYMETADATA

    return post_json("/v1/reveal", payload).get("data")
except Exception:
    if RETURN_CIPHERTEXT:
        return normalized
    raise
$$;

CREATE OR REPLACE FUNCTION main.security.thales_crdp_scalar_by_column(
  value STRING,
  mode STRING,
  datatype STRING,
  column_name STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
COMMENT 'Thales CRDP v1 scalar protect/reveal using column-aware profile mapping.'
AS $$
import json
import urllib.request
from decimal import Decimal, InvalidOperation

CRDP_IP = "20.221.216.246"
CRDP_PORT = "8090"
DEFAULT_METADATA = "1001000"
DEFAULT_REVEAL_USER = "admin"
RETURN_CIPHERTEXT = True
BADDATATAG = "99999999999"

COLUMN_PROFILES = {
    "email": "tag.char.external",
    "ssn": "tag.nbr.external",
    "employee_id": "tag.nbr.internal",
}

PROFILE_ALIASES = {
    "tag.char.external": ("alpha-external", "external"),
    "tag.char.internal": ("plain-alpha-internal", "internal"),
    "tag.nbr.external": ("plain-nbr-ext", "external"),
    "tag.nbr.internal": ("plain-nbr-internal", "internal"),
}

def check_valid(v, datatype):
    if v is None:
        return BADDATATAG
    s = str(v).strip()
    if not s:
        return BADDATATAG
    if len(s) < 2:
        return BADDATATAG + s
    if datatype.lower() != "char":
        try:
            n = Decimal(s)
            if Decimal(-9) <= n <= Decimal(-1):
                return BADDATATAG
        except (InvalidOperation, ValueError):
            return BADDATATAG
    return s

def resolve_profile(datatype, column_name):
    column_key = (column_name or "").strip().lower()
    fallback = "tag.char.external" if datatype.lower() == "char" else "tag.nbr.external"
    alias = COLUMN_PROFILES.get(column_key, fallback)
    return PROFILE_ALIASES[alias]

def post_json(path, payload):
    req = urllib.request.Request(
        f"http://{CRDP_IP}:{CRDP_PORT}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

if value is None:
    return None

normalized = check_valid(value, datatype)
policy_name, policy_type = resolve_profile(datatype, column_name)

try:
    if mode.lower() == "protect":
        result = post_json("/v1/protect", {
            "protection_policy_name": policy_name,
            "data": normalized,
        }).get("protected_data")
        return result

    if mode.lower() != "reveal":
        raise ValueError("mode must be protect or reveal")

    payload = {
        "protection_policy_name": policy_name,
        "protected_data": normalized,
        "username": DEFAULT_REVEAL_USER,
    }
    if policy_type == "external":
        payload["external_version"] = DEFAULT_METADATA

    return post_json("/v1/reveal", payload).get("data")
except Exception:
    if RETURN_CIPHERTEXT:
        return normalized
    raise
$$;

CREATE OR REPLACE FUNCTION main.security.thales_crdp_scalar_by_column_with_user(
  value STRING,
  mode STRING,
  datatype STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS STRING
LANGUAGE PYTHON
NOT DETERMINISTIC
COMMENT 'Thales CRDP v1 scalar protect/reveal using column-aware profile mapping and runtime reveal user.'
AS $$
import json
import urllib.request
from decimal import Decimal, InvalidOperation

CRDP_IP = "20.221.216.246"
CRDP_PORT = "8090"
DEFAULT_METADATA = "1001000"
RETURN_CIPHERTEXT = True
BADDATATAG = "99999999999"

COLUMN_PROFILES = {
    "email": "tag.char.external",
    "ssn": "tag.nbr.external",
    "employee_id": "tag.nbr.internal",
}

PROFILE_ALIASES = {
    "tag.char.external": ("alpha-external", "external"),
    "tag.char.internal": ("plain-alpha-internal", "internal"),
    "tag.nbr.external": ("plain-nbr-ext", "external"),
    "tag.nbr.internal": ("plain-nbr-internal", "internal"),
}

def check_valid(v, datatype):
    if v is None:
        return BADDATATAG
    s = str(v).strip()
    if not s:
        return BADDATATAG
    if len(s) < 2:
        return BADDATATAG + s
    if datatype.lower() != "char":
        try:
            n = Decimal(s)
            if Decimal(-9) <= n <= Decimal(-1):
                return BADDATATAG
        except (InvalidOperation, ValueError):
            return BADDATATAG
    return s

def resolve_profile(datatype, column_name):
    column_key = (column_name or "").strip().lower()
    fallback = "tag.char.external" if datatype.lower() == "char" else "tag.nbr.external"
    alias = COLUMN_PROFILES.get(column_key, fallback)
    return PROFILE_ALIASES[alias]

def post_json(path, payload):
    req = urllib.request.Request(
        f"http://{CRDP_IP}:{CRDP_PORT}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

if value is None:
    return None

normalized = check_valid(value, datatype)
policy_name, policy_type = resolve_profile(datatype, column_name)
effective_reveal_user = (reveal_user or "").strip() or "admin"

try:
    if mode.lower() == "protect":
        result = post_json("/v1/protect", {
            "protection_policy_name": policy_name,
            "data": normalized,
        }).get("protected_data")
        return result

    if mode.lower() != "reveal":
        raise ValueError("mode must be protect or reveal")

    payload = {
        "protection_policy_name": policy_name,
        "protected_data": normalized,
        "username": effective_reveal_user,
    }
    if policy_type == "external":
        payload["external_version"] = DEFAULT_METADATA

    return post_json("/v1/reveal", payload).get("data")
except Exception:
    if RETURN_CIPHERTEXT:
        return normalized
    raise
$$;

CREATE OR REPLACE FUNCTION main.security.thales_crdp_bulk_legacy(
  values ARRAY<STRING>,
  mode STRING,
  datatype STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
COMMENT 'Thales CRDP v1 bulk protect/reveal using legacy profile configuration.'
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk_secure

return thales_crdp_python_function_bulk_secure(values, mode, datatype)
$$;

CREATE OR REPLACE FUNCTION main.security.thales_crdp_bulk_by_column(
  values ARRAY<STRING>,
  mode STRING,
  datatype STRING,
  column_name STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
COMMENT 'Thales CRDP v1 bulk protect/reveal using column-aware profile mapping.'
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk_secure

return thales_crdp_python_function_bulk_secure(values, mode, datatype, column_name)
$$;

CREATE OR REPLACE FUNCTION main.security.thales_crdp_bulk_by_column_with_user(
  values ARRAY<STRING>,
  mode STRING,
  datatype STRING,
  column_name STRING,
  reveal_user STRING
)
RETURNS ARRAY<STRING>
LANGUAGE PYTHON
NOT DETERMINISTIC
ENVIRONMENT (
  dependencies = '["/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_udf-0.1.0-py3-none-any.whl"]',
  environment_version = 'None'
)
COMMENT 'Thales CRDP v1 bulk protect/reveal using column-aware profile mapping and runtime reveal user.'
AS $$
from thales_databricks_udf.crdp_udfs import thales_crdp_python_function_bulk

return thales_crdp_python_function_bulk(values, mode, datatype, column_name, reveal_user)
$$;

-- Smoke tests after deployment:
--
-- SELECT main.security.thales_crdp_scalar_by_column(
--   'alice@example.com', 'protect', 'char', 'email'
-- ) AS protected_email;
--
-- SELECT main.security.thales_crdp_bulk_by_column(
--   array('alice@example.com', 'bob@example.com'),
--   'protectbulk',
--   'char',
--   'email'
-- ) AS protected_emails;
--
-- SELECT main.security.thales_crdp_scalar_by_column_with_user(
--   token_col,
--   'reveal',
--   'char',
--   'email',
--   session_user()
-- )
-- FROM some_table;
