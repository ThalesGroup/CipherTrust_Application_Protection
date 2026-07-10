# Databricks notebook source
# MAGIC %md
# MAGIC # SQL Warehouse Embedded-Config Function Generator
# MAGIC
# MAGIC This notebook/script reads active values from `udfConfig.properties`,
# MAGIC renders them as a Python `PROPERTIES = {...}` block, and stamps that
# MAGIC block into a SQL Warehouse embedded-config deployment script.
# MAGIC
# MAGIC Use this when you want the SQL Warehouse deployment artifact to stay in
# MAGIC sync with the canonical property file instead of hand-editing host, port,
# MAGIC TLS, or policy settings inside multiple `.sql` files.
# MAGIC
# MAGIC Typical usage:
# MAGIC
# MAGIC - run this from a Python-capable Databricks cluster notebook or locally
# MAGIC   with Python
# MAGIC - point `PROPERTIES_PATH` at the desired `udfConfig.properties`, or leave
# MAGIC   it as `None` to use `UDF_CONFIG_VOLUME_PATH`
# MAGIC - choose `TARGET_PRESET` such as `internal`, `none`, or `external`
# MAGIC - optionally override the template or output path directly
# MAGIC - review the generated SQL output before running it in Databricks SQL

# COMMAND ----------

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

# COMMAND ----------

REPO_ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
DEFAULT_PROPERTIES_PATH = REPO_ROOT / "src" / "main" / "resources" / "udfConfig.properties"

TEMPLATE_PRESETS = {
    "internal": "create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql",
    "none": "create_uc_plaintext_protected_none_reveal_functions_and_views_embedded_config.sql",
    "external": "create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql",
}

TARGET_PRESET = "internal"
TEMPLATE_SQL_PATH_OVERRIDE = ""
OUTPUT_SQL_PATH_OVERRIDE = ""

PROPERTIES_PATH = str(DEFAULT_PROPERTIES_PATH)

# Optional dependency override. By default, generated SQL points at the current
# wheel name used by this repository.
WHEEL_DEPENDENCY_PATH_OVERRIDE = "/Volumes/my_catalog/my_schema/volume_forjars/thales_databricks_integration-0.1.0-py3-none-any.whl"

# Optional SQL Warehouse file-path overrides. Use these if the warehouse runtime
# should resolve cert/key files from a UC volume instead of `/tmp/thales_config`.
SQL_WAREHOUSE_CA_CERT_PATH = ""
SQL_WAREHOUSE_CLIENT_CERT_PATH = ""
SQL_WAREHOUSE_CLIENT_KEY_PATH = ""

# Optional PEM source files for SQL Warehouse embedded TLS. If provided, the
# generator embeds base64-encoded file contents directly in the SQL function
# properties and the runtime writes exact bytes to local temp files before
# calling requests.
SQL_WAREHOUSE_CA_CERT_SOURCE_PATH = str(REPO_ROOT / "certs" / "crdp-ca.pem")
SQL_WAREHOUSE_CLIENT_CERT_SOURCE_PATH = str(REPO_ROOT / "certs" / "databricks-crdp-client-cert.pem")
SQL_WAREHOUSE_CLIENT_KEY_SOURCE_PATH = str(REPO_ROOT / "certs" / "databricks-crdp-client-key.pem")

# Optional key allow-list. Leave empty to embed every active property.
INCLUDE_ONLY_KEYS = []

# Optional keys to skip from the embedded Python dictionary.
EXCLUDE_KEYS = []

# COMMAND ----------


def resolve_template_sql_path() -> Path:
    if TEMPLATE_SQL_PATH_OVERRIDE.strip():
        return Path(TEMPLATE_SQL_PATH_OVERRIDE.strip())
    preset = TARGET_PRESET.strip().lower()
    if preset not in TEMPLATE_PRESETS:
        raise ValueError(
            f"Unsupported TARGET_PRESET={TARGET_PRESET!r}. Expected one of: {sorted(TEMPLATE_PRESETS)}"
        )
    return REPO_ROOT / "sql_warehouse" / "deploy" / TEMPLATE_PRESETS[preset]


def resolve_output_sql_path(template_path: Path) -> Path:
    if OUTPUT_SQL_PATH_OVERRIDE.strip():
        return Path(OUTPUT_SQL_PATH_OVERRIDE.strip())
    return template_path.with_name(f"generated_{template_path.name}")


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


def python_string_literal(value: str) -> str:
    if "\r\n" in value or "\n" in value:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        if not normalized.endswith("\n"):
            normalized += "\n"
        escaped = normalized.replace('"""', '\"\"\"')
        return f'"""{escaped}"""'
    return json.dumps(value)


def render_properties_block(properties: dict[str, str]) -> str:
    rendered_lines = ["PROPERTIES = {"]
    for key in sorted(properties):
        rendered_lines.append(f'    "{key}": {python_string_literal(properties[key])},')
    rendered_lines.append("}")
    return "\n".join(rendered_lines)


def build_embedded_properties(source_properties: dict[str, str]) -> dict[str, str]:
    selected = dict(source_properties)

    if INCLUDE_ONLY_KEYS:
        include_set = {item.strip() for item in INCLUDE_ONLY_KEYS if str(item).strip()}
        selected = {key: value for key, value in selected.items() if key in include_set}

    if EXCLUDE_KEYS:
        exclude_set = {item.strip() for item in EXCLUDE_KEYS if str(item).strip()}
        selected = {key: value for key, value in selected.items() if key not in exclude_set}

    if SQL_WAREHOUSE_CA_CERT_PATH.strip():
        selected["CRDP_CA_CERT_PATH"] = SQL_WAREHOUSE_CA_CERT_PATH.strip()
    if SQL_WAREHOUSE_CLIENT_CERT_PATH.strip():
        selected["CRDP_CLIENT_CERT_PATH"] = SQL_WAREHOUSE_CLIENT_CERT_PATH.strip()
    if SQL_WAREHOUSE_CLIENT_KEY_PATH.strip():
        selected["CRDP_CLIENT_KEY_PATH"] = SQL_WAREHOUSE_CLIENT_KEY_PATH.strip()

    if SQL_WAREHOUSE_CA_CERT_SOURCE_PATH.strip():
        selected["CRDP_CA_CERT_PEM_B64"] = base64.b64encode(
            Path(SQL_WAREHOUSE_CA_CERT_SOURCE_PATH.strip()).read_bytes()
        ).decode("ascii")
        selected.pop("CRDP_CA_CERT_PATH", None)
        selected.pop("CRDP_CA_CERT_PEM", None)
    if SQL_WAREHOUSE_CLIENT_CERT_SOURCE_PATH.strip():
        selected["CRDP_CLIENT_CERT_PEM_B64"] = base64.b64encode(
            Path(SQL_WAREHOUSE_CLIENT_CERT_SOURCE_PATH.strip()).read_bytes()
        ).decode("ascii")
        selected.pop("CRDP_CLIENT_CERT_PATH", None)
        selected.pop("CRDP_CLIENT_CERT_PEM", None)
    if SQL_WAREHOUSE_CLIENT_KEY_SOURCE_PATH.strip():
        selected["CRDP_CLIENT_KEY_PEM_B64"] = base64.b64encode(
            Path(SQL_WAREHOUSE_CLIENT_KEY_SOURCE_PATH.strip()).read_bytes()
        ).decode("ascii")
        selected.pop("CRDP_CLIENT_KEY_PATH", None)
        selected.pop("CRDP_CLIENT_KEY_PEM", None)

    if (
        SQL_WAREHOUSE_CA_CERT_SOURCE_PATH.strip()
        or SQL_WAREHOUSE_CLIENT_CERT_SOURCE_PATH.strip()
        or SQL_WAREHOUSE_CLIENT_KEY_SOURCE_PATH.strip()
    ):
        selected.pop("CRDP_CLIENT_PKCS12_PATH", None)
        selected.pop("CRDP_CLIENT_PKCS12_PASSWORD", None)

    if "RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS" in selected:
        selected["returnciphertextforuserwithnokeyaccess"] = selected[
            "RETURNCIPHERTEXTFORUSERWITHNOKEYACCESS"
        ]

    return selected


def replace_properties_blocks(sql_text: str, properties_block: str) -> str:
    pattern = re.compile(r"PROPERTIES = \{\n.*?\n\}", re.DOTALL)
    replaced_text, count = pattern.subn(properties_block, sql_text)
    if count == 0:
        raise ValueError("Did not find any `PROPERTIES = {...}` block to replace in the template SQL.")
    return replaced_text


def replace_dependency_path(sql_text: str, dependency_override: str) -> str:
    if not dependency_override.strip():
        return sql_text
    pattern = re.compile(
        r"dependencies = '\[\"[^\"]+thales_databricks_(?:integration|udf)-[^\"]+\.whl\"\]'"
    )
    dependency_json = f'["{dependency_override.strip()}"]'
    replacement = f"dependencies = '{dependency_json}'"
    return pattern.sub(replacement, sql_text)


def prepend_generation_note(sql_text: str, properties_path: str, template_path: Path) -> str:
    generator_name = "generate_embedded_config_sql_from_properties.py"
    plain_note = (
        f"-- Generated by {generator_name}\n"
        f"-- Source properties: {properties_path}\n"
        f"-- Template SQL: {template_path}\n"
    )
    if f"-- Generated by {generator_name}" in sql_text:
        return sql_text

    notebook_source_line = "-- Databricks notebook source"
    if sql_text.startswith(notebook_source_line):
        magic_md_line = "-- MAGIC %md"
        if magic_md_line in sql_text:
            magic_note = (
                f"-- MAGIC Generated by `{generator_name}`\n"
                f"-- MAGIC Source properties: `{properties_path}`\n"
                f"-- MAGIC Template SQL: `{template_path}`\n"
                "-- MAGIC\n"
            )
            return sql_text.replace(magic_md_line, f"{magic_md_line}\n{magic_note}", 1)

    return plain_note + "\n" + sql_text


# COMMAND ----------

template_path = resolve_template_sql_path()
output_path = resolve_output_sql_path(template_path)
source_properties = load_properties(PROPERTIES_PATH)
embedded_properties = build_embedded_properties(source_properties)
properties_block = render_properties_block(embedded_properties)
template_sql = template_path.read_text(encoding="utf-8")

generated_sql = replace_properties_blocks(template_sql, properties_block)
generated_sql = replace_dependency_path(generated_sql, WHEEL_DEPENDENCY_PATH_OVERRIDE)
generated_sql = prepend_generation_note(
    generated_sql,
    PROPERTIES_PATH or os.getenv("UDF_CONFIG_VOLUME_PATH") or "udfConfig.properties",
    template_path,
)

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(generated_sql, encoding="utf-8")

print(f"Loaded {len(source_properties)} active properties.")
print(f"Embedded {len(embedded_properties)} properties into SQL Warehouse template.")
print(f"Target preset: {TARGET_PRESET}")
print(f"Template: {template_path}")
print(f"Output written to: {output_path}")
print("\nPreview:\n")
print(generated_sql[:8000])
