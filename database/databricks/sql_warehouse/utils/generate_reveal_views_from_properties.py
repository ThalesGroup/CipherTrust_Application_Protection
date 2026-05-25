# Databricks notebook source
# MAGIC %md
# MAGIC # SQL Warehouse Reveal View Generator From `protect.object` Properties
# MAGIC
# MAGIC This notebook/script reads object-scoped profile mappings from
# MAGIC `udfConfig.properties`, inspects the referenced table schemas with Spark,
# MAGIC and generates a `.sql` file containing persistent `CREATE OR REPLACE VIEW`
# MAGIC statements that use the appropriate SQL Warehouse / Unity Catalog reveal
# MAGIC function signatures for:
# MAGIC
# MAGIC - internal policies
# MAGIC - external policies with sibling `*_header` columns
# MAGIC - no-version (`none`) policies
# MAGIC
# MAGIC It is intentionally a generator, not an auto-apply tool, so customers can
# MAGIC review the resulting SQL before running it.
# MAGIC
# MAGIC Important:
# MAGIC
# MAGIC - run this from a Python-capable Databricks cluster notebook where `spark`
# MAGIC   can see the target tables
# MAGIC - do not run this inside a SQL Warehouse notebook; SQL Warehouses execute
# MAGIC   SQL cells only and cannot run this Python generator directly
# MAGIC - it is not a standalone local script as written
# MAGIC - the generator depends on live Spark table metadata to determine:
# MAGIC   - full column list
# MAGIC   - column order
# MAGIC   - original data types for cast-back
# MAGIC   - presence of sibling external header columns
# MAGIC
# MAGIC Typical usage:
# MAGIC
# MAGIC - this generator is intended for the SQL Warehouse / Unity Catalog path
# MAGIC - point `PROPERTIES_PATH` at the desired `udfConfig.properties`, or leave it
# MAGIC   as `None` to use `UDF_CONFIG_VOLUME_PATH`
# MAGIC - set `OUTPUT_SQL_PATH` to a writable location such as
# MAGIC   `C:\tmp\generated_sql_warehouse_reveal_views.sql`
# MAGIC - leave `FUNCTION_CATALOG_OVERRIDE` / `FUNCTION_SCHEMA_OVERRIDE` empty if the
# MAGIC   UC Python functions live in the same catalog/schema as the protected tables
# MAGIC - otherwise set those overrides to the catalog/schema that owns the UC
# MAGIC   reveal functions
# MAGIC - run the notebook and review the emitted SQL file before applying it
# MAGIC
# MAGIC Notes:
# MAGIC
# MAGIC - the property file decides which tables/columns are sensitive
# MAGIC - Spark table metadata decides column order and cast-back types
# MAGIC - external-policy views expect sibling header columns such as `email_header`
# MAGIC - the script writes SQL; it does not create or replace views automatically
# MAGIC
# MAGIC Compute-cluster note:
# MAGIC
# MAGIC - compute-cluster Java UDF registrations are session-scoped
# MAGIC - reveal views that depend on those Java UDFs must therefore be session
# MAGIC   `TEMP VIEW`s
# MAGIC - that makes a separate persistent-view generator a poor fit for the
# MAGIC   compute-cluster path
# MAGIC - use the compute-cluster setup notebooks for in-session temp reveal views
# MAGIC - use this generator for persistent SQL Warehouse / Unity Catalog views

# COMMAND ----------

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from pyspark.sql.types import (
    ArrayType,
    BinaryType,
    BooleanType,
    ByteType,
    DataType,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StringType,
    TimestampType,
)

# COMMAND ----------

# Generator settings
GENERATOR_MODE = "sql_warehouse_embedded"
PROPERTIES_PATH = None  # None -> uses UDF_CONFIG_VOLUME_PATH or local udfConfig.properties
OUTPUT_SQL_PATH = r"C:\tmp\generated_reveal_views.sql"

# Optional filters. Leave empty to use every protect.object entry in the file.
# Example values:
# INCLUDE_OBJECTS = ["my_catalog.my_schema.plaintext_protected_internal"]
# INCLUDE_OBJECTS = ["my_catalog.my_schema.plaintext_protected_external"]
# INCLUDE_OBJECTS = ["my_catalog.my_schema.account_balance_numbers_protected_internal"]
# INCLUDE_OBJECTS = [
#     "my_catalog.my_schema.plaintext_protected_internal",
#     "my_catalog.my_schema.plaintext_protected_external",
#     "my_catalog.my_schema.account_balance_numbers_protected_internal",
# ]
INCLUDE_OBJECTS = []
EXCLUDE_OBJECTS = []

# If True, emit USE CATALOG / USE SCHEMA and view grants.
INCLUDE_GRANTS = True
DEPLOYER_GROUP = "thales_udf_deployers"
ANALYST_GROUP = "analyst"

# By default the SQL Warehouse generator assumes the UC Python functions live in
# the same catalog/schema as the protected tables. Override if needed.
FUNCTION_CATALOG_OVERRIDE = None
FUNCTION_SCHEMA_OVERRIDE = None

# If source plaintext tables can not be inferred automatically, add overrides.
# Format: protected_object_name -> source_plaintext_object_name
SOURCE_OBJECT_OVERRIDES = {}

# COMMAND ----------

if GENERATOR_MODE != "sql_warehouse_embedded":
    raise ValueError(
        "This generator is now SQL Warehouse focused. "
        "Use GENERATOR_MODE = 'sql_warehouse_embedded'."
    )


def load_properties(path: str | None = None) -> dict[str, str]:
    config_path = path or os.getenv("UDF_CONFIG_VOLUME_PATH") or "udfConfig.properties"
    properties: dict[str, str] = {}
    with open(config_path, "r", encoding="utf-8") as prop_file:
        for raw_line in prop_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            properties[name.strip()] = value.strip()
    return properties


def first_non_blank(*values):
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def normalize_object_name(object_name: str) -> str:
    return object_name.strip().lower()


def normalize_column_name(column_name: str) -> str:
    return column_name.strip().lower()


def parse_object_profiles(properties: dict[str, str]) -> dict[str, dict[str, str]]:
    object_profiles: dict[str, dict[str, str]] = {}
    for key, value in properties.items():
        if not key.startswith("protect.object."):
            continue
        object_name = normalize_object_name(key[len("protect.object."):])
        column_profiles: dict[str, str] = {}
        for entry in value.split(","):
            item = entry.strip()
            if not item:
                continue
            parts = item.split("|", 1)
            column_name = normalize_column_name(parts[0])
            profile_alias = parts[1].strip() if len(parts) > 1 else ""
            column_profiles[column_name] = profile_alias
        object_profiles[object_name] = column_profiles
    return object_profiles


def resolve_profile_alias(properties: dict[str, str], configured_profile: str | None) -> str | None:
    if configured_profile is None or not configured_profile.strip():
        return None
    normalized_tag_key = configured_profile
    if configured_profile.lower().startswith("tag."):
        normalized_tag_key = "TAG." + configured_profile[4:]
    return first_non_blank(properties.get(configured_profile), properties.get(normalized_tag_key), configured_profile)


def infer_policy_type(properties: dict[str, str], configured_profile: str | None) -> str:
    resolved_alias = resolve_profile_alias(properties, configured_profile)
    normalized_tag_key = configured_profile
    if configured_profile and configured_profile.lower().startswith("tag."):
        normalized_tag_key = "TAG." + configured_profile[4:]
    explicit = first_non_blank(
        properties.get(f"{configured_profile}.policyType") if configured_profile else None,
        properties.get(f"{normalized_tag_key}.policyType") if configured_profile else None,
        properties.get(f"{resolved_alias}.policyType") if resolved_alias else None,
    )
    if explicit:
        return explicit.lower()

    inferred_source = first_non_blank(configured_profile, resolved_alias, properties.get("DEFAULTMODE"), "external")
    lowered = str(inferred_source).lower()
    if "none" in lowered:
        return "none"
    if "internal" in lowered:
        return "internal"
    if "external" in lowered:
        return "external"
    return lowered


def infer_datatype_token(profile_alias: str | None, column_name: str) -> str:
    lowered = (profile_alias or "").lower()
    if ".nbr." in lowered or "nbr" in lowered:
        return "nbr"
    if ".char." in lowered or "char" in lowered:
        return "char"
    # Safe fallback for common numeric column names.
    if any(token in column_name.lower() for token in ("ssn", "creditcard", "code", "amount", "balance", "fee")):
        return "nbr"
    return "char"


def split_qualified_name(object_name: str) -> tuple[str, str, str]:
    parts = object_name.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected catalog.schema.object but found: {object_name}")
    return parts[0], parts[1], parts[2]


def quote_sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def function_prefix(catalog: str, schema: str) -> str:
    function_catalog = FUNCTION_CATALOG_OVERRIDE or catalog
    function_schema = FUNCTION_SCHEMA_OVERRIDE or schema
    return f"{function_catalog}.{function_schema}."


def derive_view_name(table_name: str) -> str:
    return f"v_{table_name}_revealed"


def derive_header_column_name(base_column_name: str, header_suffix: str, delimiter: str, is_array: bool) -> str:
    suffix = f"{base_column_name}{delimiter}{header_suffix}"
    return f"{suffix}_array" if is_array else suffix


def strip_protected_suffix(table_name: str) -> str:
    suffixes = (
        "_protected_internal_arrays",
        "_protected_external_arrays",
        "_protected_none_arrays",
        "_protected_internal",
        "_protected_external",
        "_protected_none",
    )
    for suffix in suffixes:
        if table_name.endswith(suffix):
            return table_name[: -len(suffix)]
    return table_name


def infer_source_object_name(protected_object_name: str) -> str | None:
    if protected_object_name in SOURCE_OBJECT_OVERRIDES:
        return SOURCE_OBJECT_OVERRIDES[protected_object_name]

    catalog, schema, table_name = split_qualified_name(protected_object_name)
    base_name = strip_protected_suffix(table_name)
    candidates = [
        f"{catalog}.{schema}.{base_name}",
        f"{catalog}.{schema}.{base_name}_plaintext",
    ]
    for candidate in candidates:
        if spark.catalog.tableExists(candidate):
            return candidate
    return None


def sql_cast_type(data_type: DataType) -> str | None:
    if isinstance(data_type, DecimalType):
        return f"DECIMAL({data_type.precision},{data_type.scale})"
    if isinstance(data_type, LongType):
        return "BIGINT"
    if isinstance(data_type, IntegerType):
        return "INT"
    if isinstance(data_type, ShortType):
        return "SMALLINT"
    if isinstance(data_type, ByteType):
        return "TINYINT"
    if isinstance(data_type, FloatType):
        return "FLOAT"
    if isinstance(data_type, DoubleType):
        return "DOUBLE"
    if isinstance(data_type, BooleanType):
        return "BOOLEAN"
    if isinstance(data_type, DateType):
        return "DATE"
    if isinstance(data_type, TimestampType):
        return "TIMESTAMP"
    return None


def build_source_type_lookup(source_object_name: str | None) -> dict[str, DataType]:
    if not source_object_name:
        return {}
    source_schema = spark.table(source_object_name).schema
    return {normalize_column_name(field.name): field.dataType for field in source_schema.fields}


def base_field_name(field_name: str) -> str:
    normalized = normalize_column_name(field_name)
    if normalized.endswith("_array"):
        return normalized[:-6]
    return normalized


def resolve_logical_column_name(
    field_name: str,
    profile_specs: dict[str, dict[str, str]],
) -> str | None:
    normalized_field_name = normalize_column_name(field_name)
    if normalized_field_name in profile_specs:
        return normalized_field_name

    if normalized_field_name.endswith("_array"):
        candidate = normalized_field_name[:-6]
        if candidate in profile_specs:
            return candidate
        normalized_field_name = candidate

    prefix_matches = [
        logical_name
        for logical_name in profile_specs.keys()
        if normalized_field_name.startswith(f"{logical_name}_")
    ]
    if not prefix_matches:
        return None

    prefix_matches.sort(key=len, reverse=True)
    return prefix_matches[0]


def resolve_external_header_field_name(
    field_name: str,
    logical_column_name: str,
    header_suffix: str,
    header_delimiter: str,
    is_array: bool,
    normalized_schema_names: set[str],
) -> str:
    physical_base_name = base_field_name(field_name)
    physical_header_name = derive_header_column_name(
        physical_base_name,
        header_suffix,
        header_delimiter,
        is_array,
    )
    if physical_header_name.lower() in normalized_schema_names:
        return physical_header_name

    logical_header_name = derive_header_column_name(
        logical_column_name,
        header_suffix,
        header_delimiter,
        is_array,
    )
    return logical_header_name


def is_header_field_name(field_name: str, header_suffix: str, header_delimiter: str) -> bool:
    normalized = normalize_column_name(field_name)
    scalar_suffix = f"{header_delimiter}{header_suffix}"
    array_suffix = f"{scalar_suffix}_array"
    return normalized.endswith(scalar_suffix) or normalized.endswith(array_suffix)


def cast_expression(expression: str, target_type: str | None, is_array: bool) -> str:
    if target_type is None:
        return expression
    if is_array:
        return f"transform(\n    {expression},\n    x -> CAST(x AS {target_type})\n  )"
    return f"CAST(\n    {expression}\n    AS {target_type}\n  )"


def render_internal_or_none_reveal(
    *,
    field_name: str,
    datatype_token: str,
    object_name: str,
    logical_column_name: str,
    is_array: bool,
    mode: str,
    catalog: str,
    schema: str,
) -> str:
    object_literal = quote_sql_string(object_name)
    column_literal = quote_sql_string(logical_column_name)
    datatype_literal = quote_sql_string(datatype_token)

    if mode == "compute_cluster":
        actor = "current_user()"
        if is_array:
            return (
                "thales_reveal_bulk_by_object_and_column_with_user(\n"
                f"      transform({field_name}, x -> CAST(x AS STRING)),\n"
                f"      {datatype_literal},\n"
                f"      {object_literal},\n"
                f"      {column_literal},\n"
                f"      {actor}\n"
                "    )"
            )
        return (
            "thales_reveal_by_object_and_column_with_user(\n"
            f"      CAST({field_name} AS STRING),\n"
            f"      {datatype_literal},\n"
            f"      {object_literal},\n"
            f"      {column_literal},\n"
            f"      {actor}\n"
            "    )"
        )

    actor = "session_user()"
    prefix = function_prefix(catalog, schema)
    if is_array:
        return (
            f"{prefix}thales_reveal_bulk_by_object_and_column_uc_embedded(\n"
            f"      transform({field_name}, x -> CAST(x AS STRING)),\n"
            f"      {datatype_literal},\n"
            f"      {object_literal},\n"
            f"      {column_literal},\n"
            f"      {actor}\n"
            "    )"
        )
    return (
        f"{prefix}thales_reveal_by_object_and_column_uc_embedded(\n"
        f"      CAST({field_name} AS STRING),\n"
        f"      {datatype_literal},\n"
        f"      {object_literal},\n"
        f"      {column_literal},\n"
        f"      {actor}\n"
        "    )"
    )


def render_external_reveal(
    *,
    field_name: str,
    header_field_name: str,
    datatype_token: str,
    object_name: str,
    logical_column_name: str,
    is_array: bool,
    mode: str,
    catalog: str,
    schema: str,
) -> str:
    object_literal = quote_sql_string(object_name)
    column_literal = quote_sql_string(logical_column_name)
    datatype_literal = quote_sql_string(datatype_token)

    if mode == "compute_cluster":
        actor = "current_user()"
        if is_array:
            return (
                "thales_reveal_bulk_by_object_and_column_with_external_header_and_user(\n"
                f"      transform({field_name}, x -> CAST(x AS STRING)),\n"
                f"      transform({header_field_name}, x -> CAST(x AS STRING)),\n"
                f"      {datatype_literal},\n"
                f"      {object_literal},\n"
                f"      {column_literal},\n"
                f"      {actor}\n"
                "    )"
            )
        return (
            "thales_reveal_by_object_and_column_with_external_header_and_user(\n"
            f"      CAST({field_name} AS STRING),\n"
            f"      CAST({header_field_name} AS STRING),\n"
            f"      {datatype_literal},\n"
            f"      {object_literal},\n"
            f"      {column_literal},\n"
            f"      {actor}\n"
            "    )"
        )

    actor = "session_user()"
    prefix = function_prefix(catalog, schema)
    if is_array:
        return (
            "zip_with(\n"
            f"      transform({field_name}, x -> CAST(x AS STRING)),\n"
            f"      transform({header_field_name}, x -> CAST(x AS STRING)),\n"
            f"      (v, h) -> {prefix}thales_reveal_by_object_and_column_with_external_header_uc_embedded(\n"
            "        v,\n"
            "        h,\n"
            f"        {datatype_literal},\n"
            f"        {object_literal},\n"
            f"        {column_literal},\n"
            f"        {actor}\n"
            "      )\n"
            "    )"
        )
    return (
        f"{prefix}thales_reveal_by_object_and_column_with_external_header_uc_embedded(\n"
        f"      CAST({field_name} AS STRING),\n"
        f"      CAST({header_field_name} AS STRING),\n"
        f"      {datatype_literal},\n"
        f"      {object_literal},\n"
        f"      {column_literal},\n"
        f"      {actor}\n"
        "    )"
    )


def generate_view_sql_for_object(
    object_name: str,
    column_profiles: dict[str, str],
    properties: dict[str, str],
) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    normalized_object = normalize_object_name(object_name)
    catalog, schema, table_name = split_qualified_name(normalized_object)
    table_df = spark.table(normalized_object)
    schema_fields = list(table_df.schema.fields)
    source_lookup = build_source_type_lookup(infer_source_object_name(normalized_object))

    header_suffix = first_non_blank(properties.get("external_table_header_value"), "header")
    header_delimiter = first_non_blank(properties.get("external_table_header_delimiter"), "_")

    profile_specs = {}
    for logical_column_name, profile_alias in column_profiles.items():
        profile_specs[normalize_column_name(logical_column_name)] = {
            "profile_alias": profile_alias,
            "policy_type": infer_policy_type(properties, profile_alias),
            "datatype_token": infer_datatype_token(profile_alias, logical_column_name),
        }

    select_lines: list[str] = []
    emitted_sensitive_columns = set()
    normalized_schema_names = {normalize_column_name(item.name) for item in schema_fields}

    for field in schema_fields:
        normalized_field_name = normalize_column_name(field.name)
        if is_header_field_name(field.name, header_suffix, header_delimiter):
            continue

        is_array = isinstance(field.dataType, ArrayType)
        logical_column_name = resolve_logical_column_name(field.name, profile_specs)

        if logical_column_name is None:
            select_lines.append(f"  {field.name}")
            continue

        emitted_sensitive_columns.add(logical_column_name)
        spec = profile_specs[logical_column_name]
        policy_type = spec["policy_type"]
        datatype_token = spec["datatype_token"]
        target_source_type = source_lookup.get(base_field_name(field.name))
        if target_source_type is None:
            target_source_type = source_lookup.get(logical_column_name)
        target_sql_type = sql_cast_type(target_source_type) if target_source_type is not None else None

        if policy_type == "external":
            header_field_name = resolve_external_header_field_name(
                field.name,
                logical_column_name,
                header_suffix,
                header_delimiter,
                is_array,
                normalized_schema_names,
            )
            if normalized_field_name == header_field_name.lower():
                continue
            if header_field_name.lower() not in normalized_schema_names:
                warnings.append(
                    f"Skipping {normalized_object}.{field.name} because expected external header column "
                    f"{header_field_name} was not found."
                )
                select_lines.append(f"  {field.name}")
                continue
            reveal_expression = render_external_reveal(
                field_name=field.name,
                header_field_name=header_field_name,
                datatype_token=datatype_token,
                object_name=normalized_object,
                logical_column_name=logical_column_name,
                is_array=is_array,
                mode=GENERATOR_MODE,
                catalog=catalog,
                schema=schema,
            )
        else:
            reveal_expression = render_internal_or_none_reveal(
                field_name=field.name,
                datatype_token=datatype_token,
                object_name=normalized_object,
                logical_column_name=logical_column_name,
                is_array=is_array,
                mode=GENERATOR_MODE,
                catalog=catalog,
                schema=schema,
            )

        final_expression = cast_expression(reveal_expression, target_sql_type, is_array)
        select_lines.append(f"  {final_expression} AS {field.name}")

    missing_columns = sorted(set(profile_specs.keys()) - emitted_sensitive_columns)
    for missing_column in missing_columns:
        warnings.append(
            f"Object mapping for {normalized_object} references sensitive column {missing_column} but it was not found in the table schema."
        )

    if not select_lines:
        warnings.append(f"No columns were emitted for {normalized_object}; skipping view generation.")
        return None, warnings

    view_name = f"{catalog}.{schema}.{derive_view_name(table_name)}"
    sql_lines = [
        f"-- Source table: {normalized_object}",
        f"CREATE OR REPLACE VIEW {view_name} AS",
        "SELECT",
        ",\n".join(select_lines),
        f"FROM {normalized_object};",
        "",
    ]
    return "\n".join(sql_lines), warnings


def generate_grants(grouped_views: dict[tuple[str, str], list[str]]) -> str:
    if not INCLUDE_GRANTS:
        return ""

    grant_lines: list[str] = ["-- Grants", ""]
    for (catalog, schema), views in sorted(grouped_views.items()):
        grant_lines.append(f"GRANT USE CATALOG ON CATALOG {catalog} TO `{DEPLOYER_GROUP}`;")
        grant_lines.append(f"GRANT USE SCHEMA ON SCHEMA {catalog}.{schema} TO `{DEPLOYER_GROUP}`;")
        for view_name in views:
            grant_lines.append(f"GRANT SELECT ON VIEW {view_name} TO `{DEPLOYER_GROUP}`;")
        grant_lines.append("")
        grant_lines.append(f"GRANT USE CATALOG ON CATALOG {catalog} TO `{ANALYST_GROUP}`;")
        grant_lines.append(f"GRANT USE SCHEMA ON SCHEMA {catalog}.{schema} TO `{ANALYST_GROUP}`;")
        for view_name in views:
            grant_lines.append(f"GRANT SELECT ON VIEW {view_name} TO `{ANALYST_GROUP}`;")
        grant_lines.append("")
    return "\n".join(grant_lines)


# COMMAND ----------

properties = load_properties(PROPERTIES_PATH)
object_profiles = parse_object_profiles(properties)

if INCLUDE_OBJECTS:
    include_set = {normalize_object_name(item) for item in INCLUDE_OBJECTS}
    object_profiles = {name: value for name, value in object_profiles.items() if name in include_set}

if EXCLUDE_OBJECTS:
    exclude_set = {normalize_object_name(item) for item in EXCLUDE_OBJECTS}
    object_profiles = {name: value for name, value in object_profiles.items() if name not in exclude_set}

if not object_profiles:
    raise ValueError("No protect.object mappings found after applying include/exclude filters.")

generated_blocks: list[str] = []
warnings: list[str] = []
views_by_schema: dict[tuple[str, str], list[str]] = defaultdict(list)

for object_name in sorted(object_profiles):
    sql_block, object_warnings = generate_view_sql_for_object(object_name, object_profiles[object_name], properties)
    warnings.extend(object_warnings)
    if sql_block is None:
        continue
    generated_blocks.append(sql_block)
    catalog, schema, table_name = split_qualified_name(object_name)
    views_by_schema[(catalog, schema)].append(f"{catalog}.{schema}.{derive_view_name(table_name)}")

output_lines = [
    f"-- Generated by generate_reveal_views_from_properties.py",
    f"-- Generator mode: {GENERATOR_MODE}",
    "",
]

if warnings:
    output_lines.append("-- Warnings")
    for warning in warnings:
        output_lines.append(f"-- {warning}")
    output_lines.append("")

output_lines.extend(generated_blocks)

grant_sql = generate_grants(views_by_schema)
if grant_sql:
    output_lines.append(grant_sql)

generated_sql = "\n".join(output_lines).strip() + "\n"

output_path = Path(OUTPUT_SQL_PATH)
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(generated_sql, encoding="utf-8")

print(f"Generated reveal SQL for {len(generated_blocks)} object(s).")
print(f"Output written to: {output_path}")
if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f" - {warning}")

print("\nPreview:\n")
print(generated_sql[:8000])
