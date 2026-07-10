from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path


@dataclass(slots=True)
class ObjectPolicyConfig:
    object_name: str
    column_profiles: dict[str, str] = field(default_factory=dict)
    column_types: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class IntegrationConfig:
    """
    Minimal Phase 1 config model.

    This mirrors the current project conceptually without importing its whole
    property-file implementation into this repository yet.
    """

    objects: dict[str, ObjectPolicyConfig] = field(default_factory=dict)
    reveal_objects: dict[str, ObjectPolicyConfig] = field(default_factory=dict)
    global_column_profiles: dict[str, str] = field(default_factory=dict)
    global_column_types: dict[str, str] = field(default_factory=dict)
    raw_properties: dict[str, str] = field(default_factory=dict)
    default_batch_size: int = 1000
    crdp_api_version: str = "v2"
    transport_mode: str = "auto"
    crdp_ip: str = ""
    crdp_port: int = 0
    crdp_user: str = ""
    crdp_ssl_enabled: bool = False
    crdp_ssl_verify_server: bool = True
    crdp_ca_cert_path: str = ""
    crdp_client_cert_path: str = ""
    crdp_client_key_path: str = ""
    crdp_connect_timeout_ms: int = 10000
    crdp_read_timeout_ms: int = 30000
    default_reveal_user: str = "admin"
    reveal_user_override_allowed: bool = True
    default_metadata: str = "1001000"
    default_mode: str = "internal"
    external_table_header_value: str = "header"
    external_table_header_delimiter: str = "_"
    spark_group_size: int = 1000
    crdp_v2_max_items_per_request: int = 1000
    crdp_v2_max_policy_groups_per_request: int = 50
    crdp_v2_enable_multi_policy: bool = True
    reveal_fail_open_to_ciphertext: bool = False
    reveal_fail_open_log_level: str = "ERROR"

    @classmethod
    def from_properties(cls, path: str | Path) -> "IntegrationConfig":
        properties = _load_properties(path)
        return cls.from_dict(properties)

    @classmethod
    def from_runtime(
        cls,
        config_path: str | Path | None = None,
    ) -> "IntegrationConfig":
        resolved_path = _resolve_runtime_config_path(config_path)
        return cls.from_properties(resolved_path)

    @classmethod
    def from_dict(cls, properties: dict[str, str]) -> "IntegrationConfig":
        object_mappings = _parse_object_profiles(properties, "protect.object.")
        reveal_object_mappings = _parse_object_profiles(properties, "reveal.object.")
        column_profiles = _parse_column_profiles(properties.get("COLUMN_PROFILES", ""))
        global_column_types = {
            column_name: _infer_datatype(profile_name)
            for column_name, profile_name in column_profiles.items()
        }
        objects: dict[str, ObjectPolicyConfig] = {}
        reveal_objects: dict[str, ObjectPolicyConfig] = {}

        for object_name, object_profiles in object_mappings.items():
            objects[object_name] = ObjectPolicyConfig(
                object_name=object_name,
                column_profiles=object_profiles,
                column_types={
                    column_name: _infer_datatype(profile_name)
                    for column_name, profile_name in object_profiles.items()
                },
            )

        if not objects and column_profiles:
            objects["default"] = ObjectPolicyConfig(
                object_name="default",
                column_profiles=column_profiles,
                column_types=global_column_types,
            )

        for object_name, object_profiles in reveal_object_mappings.items():
            reveal_objects[object_name] = ObjectPolicyConfig(
                object_name=object_name,
                column_profiles=object_profiles,
                column_types={
                    column_name: _infer_datatype(profile_name)
                    for column_name, profile_name in object_profiles.items()
                },
            )

        return cls(
            objects=objects,
            reveal_objects=reveal_objects,
            global_column_profiles=column_profiles,
            global_column_types=global_column_types,
            raw_properties=properties,
            default_batch_size=_parse_positive_int(
                _first_non_blank(
                    properties.get("BATCH_SIZE"),
                    properties.get("CRDP_REQUEST_ITEM_TARGET"),
                ),
                1000,
                property_name="BATCH_SIZE/CRDP_REQUEST_ITEM_TARGET",
            ),
            crdp_api_version=properties.get("CRDP_API_VERSION", "v2"),
            transport_mode=properties.get("CRDP_TRANSPORT_MODE", "auto"),
            crdp_ip=properties.get("CRDPIP", ""),
            crdp_port=_parse_int(properties.get("CRDPPORT"), 0),
            crdp_user=properties.get("CRDPUSER", ""),
            crdp_ssl_enabled=_parse_bool(properties.get("CRDP_SSL_ENABLED"), False),
            crdp_ssl_verify_server=_parse_bool(properties.get("CRDP_SSL_VERIFY_SERVER"), True),
            crdp_ca_cert_path=properties.get("CRDP_CA_CERT_PATH", ""),
            crdp_client_cert_path=properties.get("CRDP_CLIENT_CERT_PATH", ""),
            crdp_client_key_path=properties.get("CRDP_CLIENT_KEY_PATH", ""),
            crdp_connect_timeout_ms=_parse_int(properties.get("CRDP_CONNECT_TIMEOUT_MS"), 10000),
            crdp_read_timeout_ms=_parse_int(properties.get("CRDP_READ_TIMEOUT_MS"), 30000),
            default_reveal_user=_first_non_blank(
                properties.get("DEFAULTREVEALUSER"),
                properties.get("CRDPUSER"),
                properties.get("databricksuser"),
                "admin",
            ),
            reveal_user_override_allowed=_parse_bool(
                _first_non_blank(
                    properties.get("REVEAL_USER_OVERRIDE_ALLOWED"),
                    properties.get("ALLOW_REVEAL_USER_OVERRIDE"),
                ),
                True,
            ),
            default_metadata=_first_non_blank(
                properties.get("DEFAULTMETADATA"),
                properties.get("keymetadata"),
                "1001000",
            ),
            default_mode=_first_non_blank(
                properties.get("DEFAULTMODE"),
                properties.get("keymetadatalocation"),
                "internal",
            ),
            external_table_header_value=_first_non_blank(
                properties.get("external_table_header_value"),
                properties.get("EXTERNAL_TABLE_HEADER_VALUE"),
                "header",
            ),
            external_table_header_delimiter=_first_non_blank(
                properties.get("external_table_header_delimiter"),
                properties.get("EXTERNAL_TABLE_HEADER_DELIMITER"),
                "_",
            ),
            spark_group_size=_parse_positive_int(
                _first_non_blank(
                    properties.get("SPARK_GROUP_SIZE"),
                    properties.get("WORK_UNIT_ROW_COUNT"),
                ),
                1000,
                property_name="SPARK_GROUP_SIZE/WORK_UNIT_ROW_COUNT",
            ),
            crdp_v2_max_items_per_request=_parse_positive_int(
                _first_non_blank(
                    properties.get("CRDP_V2_MAX_ITEMS_PER_REQUEST"),
                    properties.get("CRDP_REQUEST_ITEM_TARGET"),
                ),
                1000,
                property_name="CRDP_V2_MAX_ITEMS_PER_REQUEST/CRDP_REQUEST_ITEM_TARGET",
            ),
            crdp_v2_max_policy_groups_per_request=_parse_positive_int(
                properties.get("CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST"),
                50,
                property_name="CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST",
            ),
            crdp_v2_enable_multi_policy=_parse_bool(
                _first_non_blank(
                    properties.get("CRDP_V2_ENABLE_MULTI_POLICY"),
                    properties.get("CRDP_MULTI_POLICY_ENABLED"),
                ),
                True,
            ),
            reveal_fail_open_to_ciphertext=_parse_bool(
                properties.get("REVEAL_FAIL_OPEN_TO_CIPHERTEXT"),
                False,
            ),
            reveal_fail_open_log_level=_first_non_blank(
                properties.get("REVEAL_FAIL_OPEN_LOG_LEVEL"),
                "ERROR",
            ),
        )

    @classmethod
    def sample_customer_config(cls) -> "IntegrationConfig":
        return cls(
            objects={
                "my_catalog.my_schema.customer": ObjectPolicyConfig(
                    object_name="my_catalog.my_schema.customer",
                    column_profiles={
                        "email": "customer-email-policy",
                        "ssn": "customer-ssn-policy",
                    },
                    column_types={
                        "email": "char",
                        "ssn": "nbr",
                    },
                )
            },
            reveal_objects={},
            raw_properties={},
            default_batch_size=1000,
            crdp_api_version="v2",
            transport_mode="stub",
            default_reveal_user="admin",
            reveal_user_override_allowed=True,
            default_metadata="1001000",
            default_mode="internal",
            spark_group_size=1000,
            crdp_v2_max_items_per_request=1000,
            crdp_v2_max_policy_groups_per_request=50,
            crdp_v2_enable_multi_policy=True,
            reveal_fail_open_to_ciphertext=False,
            reveal_fail_open_log_level="ERROR",
        )

    @classmethod
    def sample_customer_config_v1(cls) -> "IntegrationConfig":
        return cls(
            objects={
                "my_catalog.my_schema.customer": ObjectPolicyConfig(
                    object_name="my_catalog.my_schema.customer",
                    column_profiles={
                        "email": "customer-email-policy",
                        "ssn": "customer-ssn-policy",
                    },
                    column_types={
                        "email": "char",
                        "ssn": "nbr",
                    },
                )
            },
            reveal_objects={},
            raw_properties={},
            default_batch_size=1000,
            crdp_api_version="v1",
            transport_mode="stub",
            default_reveal_user="admin",
            reveal_user_override_allowed=True,
            default_metadata="1001000",
            default_mode="internal",
            spark_group_size=1000,
            crdp_v2_max_items_per_request=1000,
            crdp_v2_max_policy_groups_per_request=50,
            crdp_v2_enable_multi_policy=False,
            reveal_fail_open_to_ciphertext=False,
            reveal_fail_open_log_level="ERROR",
        )

    def get_object_columns(self, object_name: str, mode: str = "protect") -> list[str]:
        ordered_columns: list[str] = []

        object_config = self._get_object_config(object_name, mode)
        if object_config is not None:
            for column_name in object_config.column_profiles.keys():
                if column_name not in ordered_columns:
                    ordered_columns.append(column_name)

        for column_name in self._get_structured_column_profile_columns():
            if column_name not in ordered_columns:
                ordered_columns.append(column_name)

        for column_name in self.global_column_profiles.keys():
            if column_name not in ordered_columns:
                ordered_columns.append(column_name)

        return ordered_columns

    def resolve_profile(self, object_name: str, column_name: str, mode: str = "protect") -> str | None:
        configured_profile = self._get_configured_profile(object_name, column_name, mode)
        if configured_profile is None:
            return None
        return self._resolve_alias(configured_profile) or configured_profile

    def resolve_datatype(self, object_name: str, column_name: str) -> str:
        object_config = self.objects.get(object_name)
        if object_config and column_name in object_config.column_types:
            return object_config.column_types.get(column_name, "char")
        if column_name in self.global_column_types:
            return self.global_column_types.get(column_name, "char")
        default_config = self.objects.get("default")
        if default_config is None:
            return "char"
        return default_config.column_types.get(column_name, "char")

    def resolve_policy_type(self, object_name: str, column_name: str, data_type: str, mode: str) -> str:
        configured_profile = self._get_configured_profile(object_name, column_name, mode)
        explicit_policy_type = _first_non_blank(
            self._get_column_property(column_name, "policyType"),
            self._get_profile_property(configured_profile, "policyType"),
        )
        if explicit_policy_type:
            return explicit_policy_type.strip().lower()

        inferred_policy_type = _infer_policy_type(configured_profile)
        if inferred_policy_type:
            return inferred_policy_type
        inferred_policy_type = _infer_policy_type(self._resolve_alias(configured_profile))
        if inferred_policy_type:
            return inferred_policy_type
        return (self.default_mode or "internal").strip().lower()

    def resolve_metadata(self, object_name: str, column_name: str) -> str:
        return _first_non_blank(
            self._get_column_property(column_name, "metadata"),
            self.default_metadata,
            "1001000",
        )

    def resolve_reveal_user(
        self,
        object_name: str,
        column_name: str,
        runtime_reveal_user: str | None = None,
    ) -> str:
        return _first_non_blank(
            runtime_reveal_user,
            self._get_column_property(column_name, "revealUser"),
            self.default_reveal_user,
            "admin",
        )

    def resolve_external_header_column_name(self, column_name: str) -> str | None:
        if not column_name:
            return None
        return f"{column_name.strip().lower()}{self.external_table_header_delimiter}{self.external_table_header_value}"

    def should_use_real_transport(self) -> bool:
        normalized_mode = (self.transport_mode or "auto").strip().lower()
        if normalized_mode == "stub":
            return False
        if normalized_mode == "real":
            return True
        return self.has_crdp_endpoint()

    def has_crdp_endpoint(self) -> bool:
        host = (self.crdp_ip or "").strip()
        if not host:
            return False
        normalized_host = host.lower()
        if "your-crdp-ip" in normalized_host:
            return False
        return self.crdp_port > 0

    def _get_object_config(self, object_name: str, mode: str) -> ObjectPolicyConfig | None:
        normalized_mode = (mode or "protect").strip().lower()
        if normalized_mode == "reveal" and self.reveal_objects:
            return self.reveal_objects.get(object_name) or self.reveal_objects.get("default")
        return self.objects.get(object_name) or self.objects.get("default")

    def _get_configured_profile(self, object_name: str, column_name: str, mode: str) -> str | None:
        object_config = self._get_object_config(object_name, mode)
        if object_config and column_name in object_config.column_profiles:
            return object_config.column_profiles.get(column_name)
        structured_column_profile = self._get_column_property(column_name, "profile")
        if structured_column_profile:
            return structured_column_profile
        if column_name in self.global_column_profiles:
            return self.global_column_profiles.get(column_name)
        default_config = self._get_object_config("default", mode)
        if default_config and column_name in default_config.column_profiles:
            return default_config.column_profiles.get(column_name)
        legacy_profile = self.raw_properties.get("protection_profile")
        return legacy_profile.strip() if legacy_profile else None

    def _resolve_alias(self, configured_profile: str | None) -> str | None:
        if not configured_profile:
            return None
        normalized_tag_key = _normalize_tag_key(configured_profile)
        return _first_non_blank(
            self.raw_properties.get(configured_profile),
            self.raw_properties.get(normalized_tag_key) if normalized_tag_key else None,
            configured_profile,
        )

    def _get_column_property(self, column_name: str, suffix: str) -> str | None:
        if not column_name:
            return None
        normalized_column = column_name.strip().lower()
        camel_key = f"column.{normalized_column}.{suffix}"
        upper_key = f"COLUMN.{normalized_column.upper()}.{suffix.upper()}"
        return _first_non_blank(
            self.raw_properties.get(camel_key),
            self.raw_properties.get(upper_key),
        )

    def _get_profile_property(self, configured_profile: str | None, suffix: str) -> str | None:
        if not configured_profile:
            return None
        normalized_tag_key = _normalize_tag_key(configured_profile)
        return _first_non_blank(
            self.raw_properties.get(f"{configured_profile}.{suffix}"),
            self.raw_properties.get(f"{normalized_tag_key}.{suffix}") if normalized_tag_key else None,
        )

    def _get_structured_column_profile_columns(self) -> list[str]:
        discovered_columns: list[str] = []
        for key in self.raw_properties.keys():
            normalized_key = key.strip().lower()
            if not normalized_key.startswith("column.") or not normalized_key.endswith(".profile"):
                continue
            column_name = normalized_key[len("column.") : -len(".profile")].strip()
            if column_name and column_name not in discovered_columns:
                discovered_columns.append(column_name)
        return discovered_columns


def _load_properties(path: str | Path) -> dict[str, str]:
    properties: dict[str, str] = {}
    resolved_path = Path(path)
    for raw_line in resolved_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        properties[key.strip()] = value.strip()
    return properties


def _parse_object_profiles(properties: dict[str, str], prefix: str) -> dict[str, dict[str, str]]:
    parsed: dict[str, dict[str, str]] = {}
    for key, value in properties.items():
        if not key.startswith(prefix):
            continue
        object_name = key[len(prefix):].strip()
        parsed[object_name] = _parse_column_profiles(value)
    return parsed


def _parse_column_profiles(raw_value: str) -> dict[str, str]:
    profiles: dict[str, str] = {}
    for entry in raw_value.split(","):
        item = entry.strip()
        if not item or "|" not in item:
            continue
        column_name, profile_name = item.split("|", 1)
        profiles[column_name.strip()] = profile_name.strip()
    return profiles


def _infer_datatype(profile_name: str | None) -> str:
    normalized = (profile_name or "").lower()
    return "nbr" if ".nbr." in normalized or normalized.startswith("tag.nbr") or "nbr" in normalized else "char"


def _parse_int(raw_value: str | None, default: int) -> int:
    try:
        return int(raw_value) if raw_value is not None else default
    except ValueError:
        return default


def _parse_positive_int(raw_value: str | None, default: int, property_name: str) -> int:
    value = _parse_int(raw_value, default)
    if value <= 0:
        raise ValueError(
            f"{property_name} must be a positive integer. "
            f"Received: {raw_value!r}"
        )
    return value


def _parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"true", "yes", "1", "on"}:
        return True
    if normalized in {"false", "no", "0", "off"}:
        return False
    return default


def _first_non_blank(*values: str | None) -> str | None:
    for value in values:
        if value is not None and value.strip():
            return value.strip()
    return None


def _normalize_tag_key(configured_profile: str | None) -> str | None:
    if configured_profile is None:
        return None
    trimmed = configured_profile.strip()
    if not trimmed:
        return None
    if trimmed.lower().startswith("tag."):
        return "TAG." + trimmed[4:]
    return trimmed


def _infer_policy_type(value: str | None) -> str | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    if "external" in normalized:
        return "external"
    if "internal" in normalized:
        return "internal"
    if "none" in normalized:
        return "none"
    return None


def _resolve_runtime_config_path(config_path: str | Path | None) -> Path:
    candidates: list[Path] = []

    if config_path is not None:
        candidates.append(Path(config_path))

    env_candidates = [
        os.environ.get("UDF_CONFIG_VOLUME_PATH"),
        os.environ.get("THALES_UDF_CONFIG_PATH"),
        "/tmp/thales_config/udfConfig.properties",
    ]
    for candidate in env_candidates:
        if candidate:
            candidates.append(Path(candidate))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates) or "<none>"
    raise FileNotFoundError(
        "Unable to locate udfConfig.properties for runtime loading. "
        f"Searched: {searched}"
    )
