import json
import os
import hashlib
import tempfile
import base64
import ssl
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Optional
import requests
from requests.adapters import HTTPAdapter

__all__ = [
    "BADDATATAG",
    "PROPERTIES",
    "check_valid",
    "demo_bulk_test",
    "debug_tls_materials",
    "load_properties",
    "prepare_reveal_input",
    "prepare_reveal_input_with_versions",
    "resolve_runtime_reveal_user",
    "thales_crdp_python_protect_with_external_header",
    "thales_crdp_python_protect_with_external_header_by_object",
    "thales_crdp_python_function_bulk_secure",
    "thales_crdp_python_function_bulk_secure_legacy",
    "thales_crdp_python_function_bulk_by_object",
    "thales_crdp_python_function_bulk_secure_by_object",
]


_CACHED_PROPERTIES: Optional[dict] = None
_CACHED_HTTP_SESSION: Optional[requests.Session] = None
_CACHED_HTTP_SESSION_SIGNATURE: Optional[str] = None


def load_properties(path: Optional[str] = None, refresh: bool = False) -> dict:
    global _CACHED_PROPERTIES

    if path is None and _CACHED_PROPERTIES is not None and not refresh:
        return dict(_CACHED_PROPERTIES)

    config_path = path or os.getenv("UDF_CONFIG_VOLUME_PATH") or "udfConfig.properties"
    properties = {}
    with open(config_path, "r", encoding="utf-8") as prop_file:
        for raw_line in prop_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            properties[name.strip()] = value.strip()
    if path is None:
        _CACHED_PROPERTIES = dict(properties)
    return properties


def get_default_properties(refresh: bool = False) -> dict:
    return load_properties(refresh=refresh)


def _parse_boolean_flag(value: Optional[str], default: bool = False) -> bool:
    normalized = first_non_blank(value)
    if normalized is None:
        return default
    return normalized.lower() in {"true", "yes", "y", "1"}


def _parse_positive_int(value: Optional[str], default: int) -> int:
    try:
        parsed = int(str(value).strip())
        return parsed if parsed > 0 else default
    except Exception:
        return default


def is_crdp_ssl_enabled(properties: dict) -> bool:
    explicit = first_non_blank(properties.get("CRDP_SSL_ENABLED"), properties.get("crdp.ssl.enabled"))
    if explicit is not None:
        return _parse_boolean_flag(explicit, False)
    crdp_ip = first_non_blank(properties.get("CRDPIP"), properties.get("crdpip"))
    return crdp_ip is not None and crdp_ip.lower().startswith("https://")


def is_crdp_ssl_verify_server_enabled(properties: dict) -> bool:
    return _parse_boolean_flag(
        first_non_blank(properties.get("CRDP_SSL_VERIFY_SERVER"), properties.get("crdp.ssl.verifyServer")),
        True,
    )


def get_crdp_ca_cert_path(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CA_CERT_PATH"), properties.get("crdp.ca.cert.path"))


def get_crdp_client_cert_path(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_CERT_PATH"), properties.get("crdp.client.cert.path"))


def get_crdp_client_key_path(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_KEY_PATH"), properties.get("crdp.client.key.path"))


def get_crdp_ca_cert_pem(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CA_CERT_PEM"), properties.get("crdp.ca.cert.pem"))


def get_crdp_client_cert_pem(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_CERT_PEM"), properties.get("crdp.client.cert.pem"))


def get_crdp_client_key_pem(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_KEY_PEM"), properties.get("crdp.client.key.pem"))


def get_crdp_ca_cert_pem_b64(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CA_CERT_PEM_B64"), properties.get("crdp.ca.cert.pem.b64"))


def get_crdp_client_cert_pem_b64(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_CERT_PEM_B64"), properties.get("crdp.client.cert.pem.b64"))


def get_crdp_client_key_pem_b64(properties: dict) -> Optional[str]:
    return first_non_blank(properties.get("CRDP_CLIENT_KEY_PEM_B64"), properties.get("crdp.client.key.pem.b64"))


def get_crdp_connect_timeout_ms(properties: dict) -> int:
    return _parse_positive_int(
        first_non_blank(properties.get("CRDP_CONNECT_TIMEOUT_MS"), properties.get("crdp.connect.timeout.ms")),
        10000,
    )


def get_crdp_read_timeout_ms(properties: dict) -> int:
    return _parse_positive_int(
        first_non_blank(properties.get("CRDP_READ_TIMEOUT_MS"), properties.get("crdp.read.timeout.ms")),
        30000,
    )


def get_crdp_http_pool_maxsize(properties: dict) -> int:
    return _parse_positive_int(
        first_non_blank(properties.get("CRDP_HTTP_POOL_MAXSIZE"), properties.get("crdp.http.pool.maxsize")),
        20,
    )


def get_bad_data_tag(properties: Optional[dict] = None) -> str:
    props = properties or get_default_properties()
    return props.get("BADDATATAG", "99999999999")


def resolve_runtime_reveal_user(
    spark_session=None,
    explicit_reveal_user: Optional[str] = None,
    properties: Optional[dict] = None,
):
    if explicit_reveal_user is not None and str(explicit_reveal_user).strip():
        return str(explicit_reveal_user).strip()

    spark = spark_session
    if spark is None:
        try:
            from pyspark.sql import SparkSession  # type: ignore

            spark = SparkSession.getActiveSession()
        except Exception:
            spark = None

    if spark is not None:
        for sql_text in ("select session_user()", "select current_user()"):
            try:
                value = spark.sql(sql_text).first()[0]
                if value is not None and str(value).strip():
                    return str(value).strip()
            except Exception:
                continue

        try:
            context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()  # type: ignore[name-defined]
            user_name = context.userName().get()
            if user_name is not None and str(user_name).strip():
                return str(user_name).strip()
        except Exception:
            pass

    props = properties or get_default_properties()
    return first_non_blank(props.get("CRDPUSER"), props.get("DEFAULTREVEALUSER"), props.get("databricksuser"), "admin")


PROPERTIES = None
BADDATATAG = "99999999999"


def check_valid(databricks_inputdata, datatype, bad_data_tag: Optional[str] = None):
    invalid_tag = bad_data_tag or BADDATATAG
    if databricks_inputdata is None:
        return invalid_tag

    value = str(databricks_inputdata).strip()
    if not value:
        return invalid_tag
    if len(value) < 2:
        return invalid_tag + value

    if str(datatype).lower() != "char":
        try:
            number = Decimal(value)
            if Decimal(-9) <= number <= Decimal(-1):
                return invalid_tag
        except (InvalidOperation, ValueError):
            return invalid_tag
    return value


def prepare_reveal_input(protected_data, protection_policy_name, key_metadata_location, external_version=None, username="admin"):
    return prepare_reveal_input_with_versions(
        protected_data,
        protection_policy_name,
        key_metadata_location,
        external_versions=None,
        external_version=external_version,
        username=username,
    )


def prepare_reveal_input_with_versions(
    protected_data,
    protection_policy_name,
    key_metadata_location,
    external_versions=None,
    external_version=None,
    username="admin",
):
    payload = {
        "protection_policy_name": protection_policy_name,
        "username": username,
        "protected_data_array": [],
    }
    if str(key_metadata_location).lower() == "external":
        if external_versions is not None:
            payload["protected_data_array"] = []
            for index, data in enumerate(protected_data):
                item = {"protected_data": data}
                item_external_version = external_versions[index] if index < len(external_versions) else None
                item_external_version = first_non_blank(item_external_version, external_version)
                if item_external_version:
                    item["external_version"] = item_external_version
                payload["protected_data_array"].append(item)
        elif external_version:
            payload["protected_data_array"] = [
                {"protected_data": data, "external_version": external_version} for data in protected_data
            ]
        else:
            payload["protected_data_array"] = [{"protected_data": data} for data in protected_data]
    else:
        payload["protected_data_array"] = [{"protected_data": data} for data in protected_data]
    return payload


def normalize_column_key(column_name: Optional[str]) -> Optional[str]:
    return None if column_name is None else column_name.strip().lower()


def normalize_object_key(object_name: Optional[str]) -> Optional[str]:
    return None if object_name is None else object_name.strip().lower()


def first_non_blank(*values):
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def normalize_tag_key(configured_profile: Optional[str]) -> Optional[str]:
    if configured_profile is None:
        return None
    trimmed = configured_profile.strip()
    if trimmed.lower().startswith("tag."):
        return "TAG." + trimmed[4:]
    return trimmed


def infer_policy_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if "external" in normalized:
        return "external"
    if "internal" in normalized:
        return "internal"
    if "none" in normalized:
        return "none"
    return None


def parse_column_profiles(properties: dict) -> dict:
    profiles = {}
    raw = properties.get("COLUMN_PROFILES", "")
    for entry in raw.split(","):
        item = entry.strip()
        if not item:
            continue
        parts = item.split("|", 1)
        column_name = parts[0].strip().lower()
        profile_alias = parts[1].strip() if len(parts) > 1 else ""
        profiles[column_name] = profile_alias
    return profiles


def parse_object_profiles(properties: dict, prefix: str) -> dict:
    object_profiles = {}
    normalized_prefix = prefix.strip()
    for property_name, property_value in properties.items():
        if not property_name.startswith(normalized_prefix):
            continue
        object_name = normalize_object_key(property_name[len(normalized_prefix):])
        if not object_name:
            continue
        column_profiles = {}
        for entry in str(property_value).split(","):
            item = entry.strip()
            if not item:
                continue
            parts = item.split("|", 1)
            column_name = parts[0].strip().lower()
            profile_alias = parts[1].strip() if len(parts) > 1 else ""
            column_profiles[column_name] = profile_alias
        object_profiles[object_name] = column_profiles
    return object_profiles


def resolve_object_profile_alias(
    properties: dict,
    object_name: Optional[str],
    column_name: Optional[str],
    mode: Optional[str] = None,
) -> Optional[str]:
    normalized_object = normalize_object_key(object_name)
    normalized_column = normalize_column_key(column_name)
    if normalized_object is None or normalized_column is None:
        return None

    use_reveal_profiles = str(mode or "").lower().startswith("reveal")
    reveal_profiles = parse_object_profiles(properties, "reveal.object.")
    if use_reveal_profiles:
        configured = reveal_profiles.get(normalized_object, {}).get(normalized_column)
        if configured:
            return configured

    protect_profiles = parse_object_profiles(properties, "protect.object.")
    return protect_profiles.get(normalized_object, {}).get(normalized_column)


def resolve_alias(properties: dict, configured_profile: Optional[str]) -> Optional[str]:
    if configured_profile is None or not configured_profile.strip():
        return None
    return first_non_blank(
        properties.get(configured_profile),
        properties.get(normalize_tag_key(configured_profile)),
        configured_profile,
    )


def resolve_column_property(properties: dict, column_name: Optional[str], suffix: str) -> Optional[str]:
    normalized_column = normalize_column_key(column_name)
    if normalized_column is None:
        return None
    return first_non_blank(
        properties.get(f"column.{normalized_column}.{suffix}"),
        properties.get(f"COLUMN.{normalized_column.upper()}.{suffix.upper()}"),
    )


def resolve_profile(
    properties: dict,
    datatype: str,
    column_name: Optional[str] = None,
    object_name: Optional[str] = None,
    mode: Optional[str] = None,
):
    column_profiles = parse_column_profiles(properties)
    configured_profile = first_non_blank(
        resolve_object_profile_alias(properties, object_name, column_name, mode),
        resolve_column_property(properties, column_name, "profile"),
        column_profiles.get(normalize_column_key(column_name)),
        properties.get("protection_profile"),
    )

    if configured_profile is None:
        normalized_type = str(datatype).lower()
        configured_profile = (
            first_non_blank(properties.get("DEFAULTEXTERNALCHARPOLICY"), properties.get("protection_profile_alpha_ext"))
            if normalized_type == "char"
            else first_non_blank(properties.get("DEFAULTEXTERNALNBRNBRPOLICY"), properties.get("protection_profile_nbr_ext"))
        )

    policy_name = resolve_alias(properties, configured_profile)
    policy_type = first_non_blank(
        resolve_column_property(properties, column_name, "policyType"),
        properties.get(f"{configured_profile}.policyType") if configured_profile else None,
        properties.get(f"{normalize_tag_key(configured_profile)}.policyType") if configured_profile else None,
        infer_policy_type(configured_profile),
        infer_policy_type(policy_name),
        properties.get("DEFAULTMODE"),
        properties.get("keymetadatalocation"),
        "external",
    )
    return policy_name, policy_type.lower()


def build_url(properties: dict, mode: str) -> str:
    crdp_ip = first_non_blank(properties.get("CRDPIP"), properties.get("crdpip"))
    if crdp_ip is None:
        raise ValueError("No CRDPIP found for UDF.")
    crdp_port = first_non_blank(properties.get("CRDPPORT"), properties.get("CRDPIPPORT"), "8090")
    if crdp_ip.startswith("http://") or crdp_ip.startswith("https://"):
        return f"{crdp_ip}:{crdp_port}/v1/{mode}"
    scheme = "https" if is_crdp_ssl_enabled(properties) else "http"
    return f"{scheme}://{crdp_ip}:{crdp_port}/v1/{mode}"


def _hash_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_bytes(value: Optional[bytes]) -> str:
    if not value:
        return ""
    return hashlib.sha256(value).hexdigest()


def _write_tls_pem_temp_file(prefix: str, content: str) -> str:
    tls_dir = os.path.join(tempfile.gettempdir(), "thales_databricks_udf_tls")
    os.makedirs(tls_dir, exist_ok=True)
    file_path = os.path.join(tls_dir, f"{prefix}-{_hash_text(content)}.pem")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8", newline="\n") as pem_file:
            pem_file.write(content)
        try:
            os.chmod(file_path, 0o600)
        except Exception:
            pass
    return file_path


def _decode_base64_content(value: Optional[str]) -> Optional[bytes]:
    if not value:
        return None
    return base64.b64decode(value.encode("ascii"))


def _write_tls_temp_file_bytes(prefix: str, content: bytes, suffix: str = ".pem") -> str:
    tls_dir = os.path.join(tempfile.gettempdir(), "thales_databricks_udf_tls")
    os.makedirs(tls_dir, exist_ok=True)
    file_path = os.path.join(tls_dir, f"{prefix}-{_hash_bytes(content)}{suffix}")
    if not os.path.exists(file_path):
        with open(file_path, "wb") as pem_file:
            pem_file.write(content)
        try:
            os.chmod(file_path, 0o600)
        except Exception:
            pass
    return file_path


def _resolve_tls_material_paths(properties: dict) -> tuple[Optional[str], Optional[str], Optional[str]]:
    ca_cert_pem_b64 = get_crdp_ca_cert_pem_b64(properties)
    client_cert_pem_b64 = get_crdp_client_cert_pem_b64(properties)
    client_key_pem_b64 = get_crdp_client_key_pem_b64(properties)
    ca_cert_pem = get_crdp_ca_cert_pem(properties)
    client_cert_pem = get_crdp_client_cert_pem(properties)
    client_key_pem = get_crdp_client_key_pem(properties)

    ca_cert_path = (
        _write_tls_temp_file_bytes("crdp-ca-cert", _decode_base64_content(ca_cert_pem_b64))
        if ca_cert_pem_b64
        else _write_tls_pem_temp_file("crdp-ca-cert", ca_cert_pem)
        if ca_cert_pem
        else get_crdp_ca_cert_path(properties)
    )
    client_cert_path = (
        _write_tls_temp_file_bytes("crdp-client-cert", _decode_base64_content(client_cert_pem_b64))
        if client_cert_pem_b64
        else _write_tls_pem_temp_file("crdp-client-cert", client_cert_pem)
        if client_cert_pem
        else get_crdp_client_cert_path(properties)
    )
    client_key_path = (
        _write_tls_temp_file_bytes("crdp-client-key", _decode_base64_content(client_key_pem_b64))
        if client_key_pem_b64
        else _write_tls_pem_temp_file("crdp-client-key", client_key_pem)
        if client_key_pem
        else get_crdp_client_key_path(properties)
    )
    return ca_cert_path, client_cert_path, client_key_path

def _build_http_session_signature(properties: dict) -> str:
    return "|".join(
        [
            str(is_crdp_ssl_enabled(properties)),
            str(is_crdp_ssl_verify_server_enabled(properties)),
            _hash_text(get_crdp_ca_cert_pem_b64(properties)),
            _hash_text(get_crdp_client_cert_pem_b64(properties)),
            _hash_text(get_crdp_client_key_pem_b64(properties)),
            _hash_text(get_crdp_ca_cert_pem(properties)),
            _hash_text(get_crdp_client_cert_pem(properties)),
            _hash_text(get_crdp_client_key_pem(properties)),
            get_crdp_ca_cert_path(properties) or "",
            get_crdp_client_cert_path(properties) or "",
            get_crdp_client_key_path(properties) or "",
            str(get_crdp_connect_timeout_ms(properties)),
            str(get_crdp_read_timeout_ms(properties)),
            str(get_crdp_http_pool_maxsize(properties)),
        ]
    )


def _build_http_session(properties: dict) -> requests.Session:
    session = requests.Session()
    pool_maxsize = get_crdp_http_pool_maxsize(properties)
    adapter = HTTPAdapter(pool_connections=pool_maxsize, pool_maxsize=pool_maxsize)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    ca_cert_path, cert_path, key_path = _resolve_tls_material_paths(properties)
    if cert_path and key_path:
        session.cert = (cert_path, key_path)

    verify_server = is_crdp_ssl_verify_server_enabled(properties)
    if not verify_server:
        session.verify = False
    else:
        session.verify = ca_cert_path if ca_cert_path else True

    return session


def get_http_session(properties: dict) -> requests.Session:
    global _CACHED_HTTP_SESSION
    global _CACHED_HTTP_SESSION_SIGNATURE

    signature = _build_http_session_signature(properties)
    if _CACHED_HTTP_SESSION is not None and _CACHED_HTTP_SESSION_SIGNATURE == signature:
        return _CACHED_HTTP_SESSION

    session = _build_http_session(properties)
    _CACHED_HTTP_SESSION = session
    _CACHED_HTTP_SESSION_SIGNATURE = signature
    return session


def post_json(url: str, payload: dict, properties: dict) -> dict:
    session = get_http_session(properties)
    timeout = (
        get_crdp_connect_timeout_ms(properties) / 1000.0,
        get_crdp_read_timeout_ms(properties) / 1000.0,
    )
    response = session.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def debug_tls_materials(properties=None) -> dict:
    props = _validate_properties(properties) or get_default_properties()
    ca_cert_path, client_cert_path, client_key_path = _resolve_tls_material_paths(props)

    result = {
        "ssl_enabled": is_crdp_ssl_enabled(props),
        "verify_server": is_crdp_ssl_verify_server_enabled(props),
        "has_ca_cert_path_property": bool(get_crdp_ca_cert_path(props)),
        "has_client_cert_path_property": bool(get_crdp_client_cert_path(props)),
        "has_client_key_path_property": bool(get_crdp_client_key_path(props)),
        "has_ca_cert_pem_property": bool(get_crdp_ca_cert_pem(props)),
        "has_client_cert_pem_property": bool(get_crdp_client_cert_pem(props)),
        "has_client_key_pem_property": bool(get_crdp_client_key_pem(props)),
        "has_ca_cert_pem_b64_property": bool(get_crdp_ca_cert_pem_b64(props)),
        "has_client_cert_pem_b64_property": bool(get_crdp_client_cert_pem_b64(props)),
        "has_client_key_pem_b64_property": bool(get_crdp_client_key_pem_b64(props)),
        "resolved_ca_cert_path": ca_cert_path,
        "resolved_client_cert_path": client_cert_path,
        "resolved_client_key_path": client_key_path,
        "resolved_ca_cert_exists": bool(ca_cert_path and os.path.exists(ca_cert_path)),
        "resolved_client_cert_exists": bool(client_cert_path and os.path.exists(client_cert_path)),
        "resolved_client_key_exists": bool(client_key_path and os.path.exists(client_key_path)),
        "resolved_ca_cert_size": os.path.getsize(ca_cert_path) if ca_cert_path and os.path.exists(ca_cert_path) else None,
        "resolved_client_cert_size": os.path.getsize(client_cert_path) if client_cert_path and os.path.exists(client_cert_path) else None,
        "resolved_client_key_size": os.path.getsize(client_key_path) if client_key_path and os.path.exists(client_key_path) else None,
    }

    verify_context = ssl.create_default_context()
    try:
        if ca_cert_path:
            verify_context.load_verify_locations(cafile=ca_cert_path)
            result["ca_load_ok"] = True
        else:
            result["ca_load_ok"] = None
    except Exception as ex:
        result["ca_load_ok"] = False
        result["ca_load_error"] = f"{type(ex).__name__}: {ex}"

    try:
        if client_cert_path and client_key_path:
            verify_context.load_cert_chain(certfile=client_cert_path, keyfile=client_key_path)
            result["client_cert_chain_load_ok"] = True
        else:
            result["client_cert_chain_load_ok"] = None
    except Exception as ex:
        result["client_cert_chain_load_ok"] = False
        result["client_cert_chain_load_error"] = f"{type(ex).__name__}: {ex}"

    return result


def _validate_properties(properties: Optional[dict]) -> Optional[dict]:
    if properties is None:
        return None
    if not isinstance(properties, Mapping):
        raise TypeError(
            "properties must be a mapping/dict when provided. "
            "Do not pass a reveal user positionally to the secure API."
        )
    return dict(properties)


def _validate_spark_session(spark_session):
    if spark_session is None:
        return None
    if hasattr(spark_session, "sql"):
        return spark_session
    raise TypeError(
        "spark_session must be a SparkSession-like object with a .sql(...) method."
    )


def thales_crdp_python_protect_with_external_header(
    value,
    datatype,
    column_name=None,
    object_name=None,
    *,
    properties=None,
    spark_session=None,
):
    validated_properties = _validate_properties(properties)
    _validate_spark_session(spark_session)
    props = validated_properties or get_default_properties()

    if value is None:
        return {"protected_value": None, "external_header": None}

    normalized_value = value
    if str(datatype).lower() != "char":
        normalized_value = check_valid(value, datatype, get_bad_data_tag(props))
    else:
        normalized_value = check_valid(value, datatype, get_bad_data_tag(props))

    policy_name, policy_type = resolve_profile(props, datatype, column_name, object_name, "protectbulk")
    url = build_url(props, "protectbulk")
    payload = {
        "protection_policy_name": policy_name,
        "data_array": [normalized_value],
    }
    response_json = post_json(url, payload, props)
    items = response_json.get("protected_data_array", [])
    if not items:
        return {"protected_value": normalized_value, "external_header": None}

    item = items[0]
    return {
        "protected_value": item.get("protected_data"),
        "external_header": item.get("external_version") if policy_type == "external" else None,
    }


def thales_crdp_python_protect_with_external_header_by_object(
    value,
    datatype,
    object_name,
    column_name=None,
    *,
    properties=None,
    spark_session=None,
):
    return thales_crdp_python_protect_with_external_header(
        value,
        datatype,
        column_name=column_name,
        object_name=object_name,
        properties=properties,
        spark_session=spark_session,
    )


def _thales_crdp_python_function_bulk_impl(
    databricks_inputdata,
    mode,
    datatype,
    column_name=None,
    object_name=None,
    reveal_user=None,
    external_versions=None,
    properties=None,
    spark_session=None,
    allow_runtime_reveal_user_override: bool = True,
):
    validated_properties = _validate_properties(properties)
    validated_spark_session = _validate_spark_session(spark_session)
    props = validated_properties or get_default_properties()
    mode = str(mode).lower()
    if mode not in {"protectbulk", "revealbulk"}:
        raise ValueError("mode must be protectbulk or revealbulk")

    return_ciphertext_for_user_without_key_access = (
        first_non_blank(
            props.get("returnciphertextforuserwithnokeyaccess"),
            props.get("RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS"),
            "no",
        ).lower()
        == "yes"
    )

    key_metadata_location = first_non_blank(props.get("keymetadatalocation"), props.get("DEFAULTMODE"), "external")
    external_version_from_ext_source = first_non_blank(props.get("keymetadata"), props.get("DEFAULTMETADATA"), "1001000")
    explicit_reveal_user = reveal_user if allow_runtime_reveal_user_override else None
    runtime_reveal_user = resolve_runtime_reveal_user(validated_spark_session, explicit_reveal_user, props)

    normalized_values = list(databricks_inputdata or [])
    normalized_external_versions = None if external_versions is None else list(external_versions)
    if normalized_external_versions is not None and len(normalized_external_versions) != len(normalized_values):
        raise ValueError("external_versions must have the same length as databricks_inputdata")

    if mode == "protectbulk":
        if str(datatype).lower() != "char":
            normalized_values = [check_valid(value, datatype, get_bad_data_tag(props)) for value in normalized_values]
        else:
            normalized_values = [check_valid(value, datatype, get_bad_data_tag(props)) if value is not None else value for value in normalized_values]
    else:
        normalized_values = [None if value is None else str(value) for value in normalized_values]

    policy_name, policy_type = resolve_profile(props, datatype, column_name, object_name, mode)
    url = build_url(props, mode)

    try:
        if mode == "protectbulk":
            payload = {
                "protection_policy_name": policy_name,
                "data_array": normalized_values,
            }
            response_json = post_json(url, payload, props)
            return [item["protected_data"] for item in response_json.get("protected_data_array", [])]

        payload = prepare_reveal_input(
            normalized_values,
            policy_name,
            key_metadata_location if policy_type != "none" else "none",
            external_version=external_version_from_ext_source if policy_type == "external" else None,
            username=runtime_reveal_user,
        ) if normalized_external_versions is None else prepare_reveal_input_with_versions(
            normalized_values,
            policy_name,
            key_metadata_location if policy_type != "none" else "none",
            external_versions=normalized_external_versions if policy_type == "external" else None,
            external_version=external_version_from_ext_source if policy_type == "external" else None,
            username=runtime_reveal_user,
        )
        response_json = post_json(url, payload, props)
        return [item["data"] for item in response_json.get("data_array", [])]
    except Exception as ex:
        if return_ciphertext_for_user_without_key_access:
            return normalized_values
        raise ex


def thales_crdp_python_function_bulk(
    databricks_inputdata,
    mode,
    datatype,
    column_name=None,
    object_name=None,
    *,
    reveal_user=None,
    external_versions=None,
    properties=None,
    spark_session=None,
):
    """
    Testing/flexible entry point.

    This version allows an explicit reveal_user override and is appropriate for
    testing, diagnostics, or tightly controlled admin workflows.
    """
    return _thales_crdp_python_function_bulk_impl(
        databricks_inputdata,
        mode,
        datatype,
        column_name=column_name,
        object_name=object_name,
        reveal_user=reveal_user,
        external_versions=external_versions,
        properties=properties,
        spark_session=spark_session,
        allow_runtime_reveal_user_override=True,
    )


def thales_crdp_python_function_bulk_secure(
    databricks_inputdata,
    mode,
    datatype,
    column_name=None,
    object_name=None,
    *,
    external_versions=None,
    properties=None,
    spark_session=None,
):
    """
    Production-safe entry point.

    This version never accepts a caller-supplied reveal user. For reveal
    operations it resolves identity from the active Spark session, notebook
    context, or config fallback.
    """
    return _thales_crdp_python_function_bulk_impl(
        databricks_inputdata,
        mode,
        datatype,
        column_name=column_name,
        object_name=object_name,
        reveal_user=None,
        external_versions=external_versions,
        properties=properties,
        spark_session=spark_session,
        allow_runtime_reveal_user_override=False,
    )


def thales_crdp_python_function_bulk_legacy(databricks_inputdata, mode, datatype):
    return thales_crdp_python_function_bulk(databricks_inputdata, mode, datatype, None)


def thales_crdp_python_function_bulk_by_object(
    databricks_inputdata,
    mode,
    datatype,
    object_name,
    column_name=None,
    *,
    reveal_user=None,
    external_versions=None,
    properties=None,
    spark_session=None,
):
    return thales_crdp_python_function_bulk(
        databricks_inputdata,
        mode,
        datatype,
        column_name,
        object_name=object_name,
        reveal_user=reveal_user,
        external_versions=external_versions,
        properties=properties,
        spark_session=spark_session,
    )


def thales_crdp_python_function_bulk_secure_legacy(databricks_inputdata, mode, datatype, *, properties=None, spark_session=None):
    return thales_crdp_python_function_bulk_secure(
        databricks_inputdata,
        mode,
        datatype,
        None,
        properties=properties,
        spark_session=spark_session,
    )


def thales_crdp_python_function_bulk_secure_by_object(
    databricks_inputdata,
    mode,
    datatype,
    object_name,
    column_name=None,
    *,
    external_versions=None,
    properties=None,
    spark_session=None,
):
    return thales_crdp_python_function_bulk_secure(
        databricks_inputdata,
        mode,
        datatype,
        column_name,
        object_name=object_name,
        external_versions=external_versions,
        properties=properties,
        spark_session=spark_session,
    )


def demo_bulk_test(spark, mode="protectbulk", datatype="char", column_name=None, properties=None):
    props = properties or get_default_properties()
    key_metadata_location = first_non_blank(props.get("keymetadatalocation"), props.get("DEFAULTMODE"), "external")

    if datatype == "char":
        query_result = spark.sql("SELECT c_name FROM samples.tpch.customer LIMIT 5")
        values = [row.c_name for row in query_result.collect()]
    else:
        query_result = spark.sql("SELECT c_acctbal FROM samples.tpch.customer WHERE c_acctbal > 1000 LIMIT 5")
        values = [str(row.c_acctbal) for row in query_result.collect()]

    if mode == "protectbulk":
        results = thales_crdp_python_function_bulk(values, mode, datatype, column_name, properties=props, spark_session=spark)
        print("Protected values:", results)
        return results

    if datatype == "char":
        values = (
            ['INlGNUmQ#k6ooUjm2A', 'KAE09OFh#eiQhgLgfI', 'RsqD5rr9#B4spSHZvD', 'HXguI0J5#TVXNJgtS5', 'MIt7SMGA#iuikyynnl']
            if key_metadata_location == "external"
            else ['1001000hhIQGjma#fH5yPPOda', '1001000rXhadmXl#XxRlFW0YU', '1001000BvDFNg8p#NbyCunqpT', '1001000w5U1O9iu#59Ulv2yA8', '1001000CzyGv0KB#mFf9pcKUY']
        )
    else:
        values = (
            ['7080.44', '7382.75', '1971.05', '8044.16', '2361.92']
            if key_metadata_location == "external"
            else ['10020007080.44', '10020007382.75', '10020001971.05', '10020008044.16', '10020002361.92']
        )

    results = thales_crdp_python_function_bulk(values, mode, datatype, column_name, properties=props, spark_session=spark)
    print("Revealed values:", results)
    return results
