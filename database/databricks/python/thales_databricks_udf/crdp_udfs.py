import json
import os
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Optional
import urllib.request

__all__ = [
    "BADDATATAG",
    "PROPERTIES",
    "check_valid",
    "demo_bulk_test",
    "load_properties",
    "prepare_reveal_input",
    "resolve_runtime_reveal_user",
    "thales_crdp_python_function_bulk_secure",
    "thales_crdp_python_function_bulk_secure_legacy",
]


_CACHED_PROPERTIES: Optional[dict] = None


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
    payload = {
        "protection_policy_name": protection_policy_name,
        "username": username,
        "protected_data_array": [],
    }
    if str(key_metadata_location).lower() == "external" and external_version:
        payload["protected_data_array"] = [
            {"protected_data": data, "external_version": external_version} for data in protected_data
        ]
    else:
        payload["protected_data_array"] = [{"protected_data": data} for data in protected_data]
    return payload


def normalize_column_key(column_name: Optional[str]) -> Optional[str]:
    return None if column_name is None else column_name.strip().lower()


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


def resolve_profile(properties: dict, datatype: str, column_name: Optional[str] = None):
    column_profiles = parse_column_profiles(properties)
    configured_profile = first_non_blank(
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
    return f"http://{crdp_ip}:{crdp_port}/v1/{mode}"


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


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


def _thales_crdp_python_function_bulk_impl(
    databricks_inputdata,
    mode,
    datatype,
    column_name=None,
    reveal_user=None,
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
    if mode == "protectbulk":
        if str(datatype).lower() != "char":
            normalized_values = [check_valid(value, datatype, get_bad_data_tag(props)) for value in normalized_values]
        else:
            normalized_values = [check_valid(value, datatype, get_bad_data_tag(props)) if value is not None else value for value in normalized_values]
    else:
        normalized_values = [None if value is None else str(value) for value in normalized_values]

    policy_name, policy_type = resolve_profile(props, datatype, column_name)
    url = build_url(props, mode)

    try:
        if mode == "protectbulk":
            payload = {
                "protection_policy_name": policy_name,
                "data_array": normalized_values,
            }
            response_json = post_json(url, payload)
            return [item["protected_data"] for item in response_json.get("protected_data_array", [])]

        payload = prepare_reveal_input(
            normalized_values,
            policy_name,
            key_metadata_location if policy_type != "none" else "none",
            external_version_from_ext_source if policy_type == "external" else None,
            runtime_reveal_user,
        )
        response_json = post_json(url, payload)
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
    *,
    reveal_user=None,
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
        reveal_user=reveal_user,
        properties=properties,
        spark_session=spark_session,
        allow_runtime_reveal_user_override=True,
    )


def thales_crdp_python_function_bulk_secure(
    databricks_inputdata,
    mode,
    datatype,
    column_name=None,
    *,
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
        reveal_user=None,
        properties=properties,
        spark_session=spark_session,
        allow_runtime_reveal_user_override=False,
    )


def thales_crdp_python_function_bulk_legacy(databricks_inputdata, mode, datatype):
    return thales_crdp_python_function_bulk(databricks_inputdata, mode, datatype, None)


def thales_crdp_python_function_bulk_secure_legacy(databricks_inputdata, mode, datatype, *, properties=None, spark_session=None):
    return thales_crdp_python_function_bulk_secure(
        databricks_inputdata,
        mode,
        datatype,
        None,
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
