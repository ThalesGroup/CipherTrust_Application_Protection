from pathlib import Path


def load_runtime_properties(config_path, defaults=None):
    settings = dict(defaults or {})
    path = Path(config_path)
    if not path.exists():
        if defaults is not None:
            print(f"WARNING: Config file not found at {config_path}; using defaults {settings}")
            return settings
        raise FileNotFoundError(f"Config file not found: {config_path}")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


def print_runtime_diagnostics(
    spark,
    *,
    label,
    config_path,
    runtime_settings,
    include_debug_flag=False,
):
    diagnostics = {
        "config_path": config_path,
        "config_version": runtime_settings.get("CONFIG_VERSION", "<not set>"),
        "config_release_date": runtime_settings.get("CONFIG_RELEASE_DATE", "<not set>"),
        "config_change_ref": runtime_settings.get("CONFIG_CHANGE_REF", "<not set>"),
        "current_catalog": spark.sql("SELECT current_catalog()").first()[0],
        "current_schema": spark.sql("SELECT current_schema()").first()[0],
        "runtime_api_version": runtime_settings.get("CRDP_API_VERSION", "v2"),
        "runtime_transport_mode": runtime_settings.get("CRDP_TRANSPORT_MODE", "auto"),
        "runtime_crdp_ip": runtime_settings.get("CRDPIP", "<not set>"),
        "runtime_crdp_port": runtime_settings.get("CRDPPORT", "<not set>"),
        "runtime_batch_size": runtime_settings.get("BATCH_SIZE", "<not set>"),
        "runtime_request_item_target": runtime_settings.get("CRDP_REQUEST_ITEM_TARGET", "<not set>"),
        "runtime_spark_group_size": runtime_settings.get("SPARK_GROUP_SIZE", "<not set>"),
        "runtime_reveal_fail_open_to_ciphertext": runtime_settings.get(
            "REVEAL_FAIL_OPEN_TO_CIPHERTEXT",
            "<not set>",
        ),
        "runtime_reveal_fail_open_log_level": runtime_settings.get(
            "REVEAL_FAIL_OPEN_LOG_LEVEL",
            "<not set>",
        ),
    }
    if include_debug_flag:
        diagnostics["runtime_debug_log_payload"] = runtime_settings.get("CRDP_DEBUG_LOG_PAYLOAD", "<not set>")
    config_notes = runtime_settings.get("CONFIG_NOTES")
    print(label)
    print(diagnostics)
    if config_notes:
        print("Config notes:")
        print(config_notes)


def print_object_mapping_diagnostics(runtime_settings, object_names):
    print("Object mapping diagnostics:")
    for object_name in object_names:
        mapping_key = f"protect.object.{object_name}"
        print(
            {
                "object_name": object_name,
                "mapping_key": mapping_key,
                "mapping_value": runtime_settings.get(mapping_key, "<not found>"),
            }
        )


def print_profile_alias_diagnostics(runtime_settings, alias_keys):
    print("Profile alias diagnostics:")
    for alias_key in alias_keys:
        print({alias_key: runtime_settings.get(alias_key, "<not found>")})


def print_column_profile_diagnostics(runtime_settings, column_names):
    print("Column profile diagnostics:")
    for column_name in column_names:
        normalized_column = str(column_name).strip().lower()
        camel_key = f"column.{normalized_column}.profile"
        upper_key = f"COLUMN.{normalized_column.upper()}.PROFILE"
        print(
            {
                "column_name": normalized_column,
                "column_profile_key": camel_key,
                "column_profile_value": runtime_settings.get(
                    camel_key,
                    runtime_settings.get(upper_key, "<not found>"),
                ),
            }
        )


def print_effective_profile_resolution_diagnostics(runtime_settings, object_name, column_names):
    print("Effective profile resolution diagnostics:")
    object_mapping = _parse_column_profile_mapping(
        runtime_settings.get(f"protect.object.{object_name}", "")
    )
    global_column_profiles = _parse_column_profile_mapping(
        runtime_settings.get("COLUMN_PROFILES", "")
    )

    for column_name in column_names:
        normalized_column = str(column_name).strip().lower()
        structured_column_profile = _get_structured_column_profile(runtime_settings, normalized_column)

        resolution_source = None
        configured_profile = None

        if normalized_column in object_mapping:
            resolution_source = "protect.object"
            configured_profile = object_mapping.get(normalized_column)
        elif structured_column_profile:
            resolution_source = "column.profile"
            configured_profile = structured_column_profile
        elif normalized_column in global_column_profiles:
            resolution_source = "COLUMN_PROFILES"
            configured_profile = global_column_profiles.get(normalized_column)
        elif runtime_settings.get("protection_profile"):
            resolution_source = "protection_profile"
            configured_profile = runtime_settings.get("protection_profile")
        else:
            resolution_source = "unresolved"

        print(
            {
                "object_name": object_name,
                "column_name": normalized_column,
                "resolution_source": resolution_source,
                "configured_profile": configured_profile or "<not found>",
                "resolved_profile": _resolve_profile_alias(runtime_settings, configured_profile) or "<not found>",
            }
        )


def _get_structured_column_profile(runtime_settings, column_name):
    camel_key = f"column.{column_name}.profile"
    upper_key = f"COLUMN.{column_name.upper()}.PROFILE"
    value = runtime_settings.get(camel_key, runtime_settings.get(upper_key))
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_column_profile_mapping(raw_value):
    parsed = {}
    for entry in str(raw_value or "").split(","):
        item = entry.strip()
        if not item or "|" not in item:
            continue
        column_name, profile_name = item.split("|", 1)
        normalized_column = column_name.strip().lower()
        normalized_profile = profile_name.strip()
        if normalized_column and normalized_profile:
            parsed[normalized_column] = normalized_profile
    return parsed


def _resolve_profile_alias(runtime_settings, configured_profile):
    if not configured_profile:
        return None
    normalized_tag_key = _normalize_tag_key(configured_profile)
    return (
        runtime_settings.get(configured_profile)
        or (runtime_settings.get(normalized_tag_key) if normalized_tag_key else None)
        or configured_profile
    )


def _normalize_tag_key(profile_name):
    normalized = str(profile_name or "").strip()
    if not normalized:
        return None
    parts = [part.strip() for part in normalized.split(".") if part.strip()]
    if not parts:
        return None
    return ".".join(
        part.upper() if index == 0 else part.lower()
        for index, part in enumerate(parts)
    )
