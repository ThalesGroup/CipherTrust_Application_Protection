# Databricks notebook source
# MAGIC %md
# MAGIC # Thales Databricks Integration Python Helper Smoke Test
# MAGIC
# MAGIC This notebook is the Python wheel / helper counterpart to
# MAGIC `compute_cluster_java_udf_smoke_test.py`.
# MAGIC
# MAGIC It is meant to validate the new higher-level integration shape:
# MAGIC
# MAGIC - DataFrame-first public API
# MAGIC - bulk-first internals
# MAGIC - object-aware policy resolution from `udfConfig.properties`
# MAGIC - v2 multi-policy request planning when enabled
# MAGIC
# MAGIC Current prototype status:
# MAGIC
# MAGIC - `protect_dataframe(...)` now runs the first Spark-side helper path
# MAGIC - the helper uses the real CRDP protect transport automatically when
# MAGIC   the loaded properties point at a real CRDP endpoint
# MAGIC - otherwise it falls back to the local stub transport for safe
# MAGIC   repository-side validation
# MAGIC - `protect_rows(...)` and `reveal_rows(...)` remain smaller trace/debug paths
# MAGIC - reveal now follows the same helper-first bulk path
# MAGIC - this smoke test is self-contained and does not require `plaintext_setup.sql`

# COMMAND ----------

from pathlib import Path

from pyspark.sql import functions as F
from utils.runtime_diagnostics import (
    print_column_profile_diagnostics,
    print_effective_profile_resolution_diagnostics,
    print_object_mapping_diagnostics,
    print_profile_alias_diagnostics,
    print_runtime_diagnostics,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

# COMMAND ----------

# Adjust this import strategy based on how the helper package is made available
# on the Databricks cluster. For local repository-based experimentation, a wheel
# or workspace sync step would normally provide this package.
from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe,
    protect_rows,
    reveal_dataframe,
    reveal_rows,
)

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)
REQUIRE_REAL_TRANSPORT = False
helper_options = {"transport_mode": "real"} if REQUIRE_REAL_TRANSPORT else None
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

print_runtime_diagnostics(
    spark,
    label="Python helper smoke test runtime diagnostics:",
    config_path=config_path,
    runtime_settings=config.raw_properties,
    include_debug_flag=True,
)


def _infer_policy_mode(mapping_value: str) -> str | None:
    normalized = (mapping_value or "").strip().lower()
    if "external" in normalized:
        return "external"
    if "internal" in normalized:
        return "internal"
    if "none" in normalized:
        return "none"
    return None


def _parse_configured_columns(mapping_value: str) -> list[str]:
    columns: list[str] = []
    for entry in str(mapping_value or "").split(","):
        item = entry.strip()
        if not item or "|" not in item:
            continue
        column_name, _profile_name = item.split("|", 1)
        columns.append(column_name.strip().lower())
    return columns


def _resolve_smoke_test_object(
    raw_properties: dict[str, str],
    mode: str,
    required_columns: list[str] | None = None,
    preferred_object_name: str | None = None,
) -> str:
    required_columns = [
        str(column).strip().lower()
        for column in (required_columns or [])
        if str(column).strip()
    ]
    matches: list[tuple[int, bool, str]] = []
    for key, value in raw_properties.items():
        if not key.startswith("protect.object."):
            continue
        object_name = key[len("protect.object."):].strip()
        if object_name.lower().endswith("_arrays"):
            continue
        if _infer_policy_mode(value) == mode:
            configured_columns = _parse_configured_columns(value)
            column_match_count = sum(1 for column in required_columns if column in configured_columns)
            preferred_name = "plaintext" in object_name.lower()
            matches.append((column_match_count, preferred_name, object_name))
    if not matches:
        if preferred_object_name:
            return preferred_object_name
        raise ValueError(
            f"Could not find a configured non-array protect.object.* mapping for mode={mode!r}."
        )
    if required_columns:
        matching_columns = [match for match in matches if match[0] == len(required_columns)]
        if matching_columns:
            matches = matching_columns
        else:
            partial_matches = [match for match in matches if match[0] > 0]
            if partial_matches:
                matches = partial_matches
            elif preferred_object_name:
                return preferred_object_name
    return sorted(matches, key=lambda item: (-item[0], -int(item[1]), item[2]))[0][2]


SMOKE_TEST_REQUIRED_COLUMNS = ["email", "ssn"]

INTERNAL_OBJECT = _resolve_smoke_test_object(
    config.raw_properties,
    "internal",
    required_columns=SMOKE_TEST_REQUIRED_COLUMNS,
    preferred_object_name=f"{CATALOG}.{SCHEMA}.plaintext_protected_internal",
)
NONE_OBJECT = _resolve_smoke_test_object(
    config.raw_properties,
    "none",
    required_columns=SMOKE_TEST_REQUIRED_COLUMNS,
    preferred_object_name=f"{CATALOG}.{SCHEMA}.plaintext_protected_none",
)

if REQUIRE_REAL_TRANSPORT and not config.has_crdp_endpoint():
    raise ValueError(
        "REQUIRE_REAL_TRANSPORT is enabled, but udfConfig.properties still does not "
        "point at a real CRDP endpoint."
    )

print("Loaded config summary:")
print(
    {
        "required_columns": SMOKE_TEST_REQUIRED_COLUMNS,
        "internal_object": INTERNAL_OBJECT,
        "none_object": NONE_OBJECT,
        "api_version": config.crdp_api_version,
        "transport_mode": config.transport_mode,
        "real_transport_enabled": config.should_use_real_transport() or REQUIRE_REAL_TRANSPORT,
        "crdp_endpoint_configured": config.has_crdp_endpoint(),
        "reveal_user_override_allowed": config.reveal_user_override_allowed,
        "spark_group_size": config.spark_group_size,
        "v2_max_items_per_request": config.crdp_v2_max_items_per_request,
        "v2_max_policy_groups_per_request": config.crdp_v2_max_policy_groups_per_request,
        "v2_enable_multi_policy": config.crdp_v2_enable_multi_policy,
    }
)
print_object_mapping_diagnostics(
    config.raw_properties,
    [
        INTERNAL_OBJECT,
        NONE_OBJECT,
    ],
)
print_profile_alias_diagnostics(
    config.raw_properties,
    [
        "TAG.char.internal",
        "TAG.nbr.internal",
        "TAG.char.none",
        "TAG.nbr.none",
    ],
)
print_column_profile_diagnostics(
    config.raw_properties,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)
print_effective_profile_resolution_diagnostics(
    config.raw_properties,
    INTERNAL_OBJECT,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)

# COMMAND ----------

# Self-contained source data for the smoke test. This keeps the helper smoke
# test independent from plaintext_setup.sql.
source_df = spark.createDataFrame(
    [
        (
            1,
            "Ava Reynolds",
            "128 Cedar Run",
            "Nashville",
            "TN",
            "37211-1022",
            "(615)555-0101",
            "ava.reynolds@example.com",
            "1988-02-14T00:00:00Z",
            "4532100098761234",
            "812",
            "565-00-9721",
        ),
        (
            2,
            "Liam Carter",
            "44 Pine Hollow",
            "Denver",
            "CO",
            "80220-4401",
            "(303)555-0102",
            "liam.carter@example.com",
            "1991-07-09T00:00:00Z",
            "5494101645671502",
            "475",
            "152-38-2718",
        ),
        (
            3,
            "Mia Sullivan",
            "902 Willow Bend",
            "Austin",
            "TX",
            "78741-1180",
            "(512)555-0103",
            "mia.sullivan@example.com",
            "1985-11-23T00:00:00Z",
            "5368843047843345",
            "312",
            "257-07-4384",
        ),
    ],
    [
        "custid",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "phone",
        "email",
        "dob",
        "creditcard",
        "creditcardcode",
        "ssn",
    ],
).orderBy("custid")
display(source_df.limit(10))

# COMMAND ----------

# DataFrame-first protect smoke test.
#
# This now executes the first Spark-side helper path. Whether the underlying
# transport is real CRDP or the stub fallback depends on the loaded config.
internal_protected_df = protect_dataframe(
    df=source_df,
    object_name=INTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

print("Internal protect DataFrame plan summary:")
print(internal_protected_df._thales_bulk_plan_summary)
display(internal_protected_df.limit(10))

# COMMAND ----------

none_protected_df = protect_dataframe(
    df=source_df,
    object_name=NONE_OBJECT,
    config=config,
    options=helper_options,
)

print("None protect DataFrame plan summary:")
print(none_protected_df._thales_bulk_plan_summary)
display(none_protected_df.limit(10))

# COMMAND ----------

internal_revealed_df = reveal_dataframe(
    df=internal_protected_df.orderBy("custid"),
    object_name=INTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

print("Internal reveal DataFrame plan summary:")
print(internal_revealed_df._thales_bulk_plan_summary)
display(internal_revealed_df.limit(10))

# COMMAND ----------

# Row-shaped executable smoke test.
#
# Until the Spark execution path is implemented, this is the real local proof of
# behavior. We collect a small sample and run it through the same object-aware
# plan and v2 request builder path.
sample_rows = [
    row.asDict(recursive=True)
    for row in source_df
    .select("custid", "email", "ssn", "city")
    .orderBy("custid")
    .limit(5)
    .collect()
]

internal_row_result = protect_rows(
    rows=sample_rows,
    object_name=INTERNAL_OBJECT,
    config=config,
)

print("Internal v2 row-shape request summary:")
print(
    {
        "input_row_count": internal_row_result.input_row_count,
        "transformed_value_count": internal_row_result.transformed_value_count,
        "request_count": internal_row_result.request_count,
        "requests": internal_row_result.requests,
    }
)

print("Internal protected rows:")
for row in internal_row_result.rows:
    print(row)

# COMMAND ----------

internal_reveal_row_result = reveal_rows(
    rows=internal_row_result.rows,
    object_name=INTERNAL_OBJECT,
    config=config,
)

print("Internal v2 row-shape reveal summary:")
print(
    {
        "input_row_count": internal_reveal_row_result.input_row_count,
        "transformed_value_count": internal_reveal_row_result.transformed_value_count,
        "request_count": internal_reveal_row_result.request_count,
        "requests": internal_reveal_row_result.requests,
    }
)

print("Internal revealed rows:")
for row in internal_reveal_row_result.rows:
    print(row)

# COMMAND ----------

# Constrained planner example to show the new v2 properties changing request
# shapes materially.
constrained_config = IntegrationConfig(
    objects=config.objects,
    default_batch_size=config.default_batch_size,
    crdp_api_version="v2",
    spark_group_size=3,
    crdp_v2_max_items_per_request=2,
    crdp_v2_max_policy_groups_per_request=1,
    crdp_v2_enable_multi_policy=True,
)

constrained_result = protect_rows(
    rows=sample_rows,
    object_name=INTERNAL_OBJECT,
    config=constrained_config,
)

print("Constrained v2 request summary:")
print(
    {
        "input_row_count": constrained_result.input_row_count,
        "transformed_value_count": constrained_result.transformed_value_count,
        "request_count": constrained_result.request_count,
        "requests": constrained_result.requests,
    }
)

# COMMAND ----------

# Reveal now auto-resolves the runtime user for Spark DataFrame execution using
# `current_user()` by default.
#
# Development / test mode:
#
# options={"reveal_user_expr": "session_user()"}
#
# or pass `reveal_user="some_user"` directly when you need explicit control.
#
# Production lock mode:
# set `REVEAL_USER_OVERRIDE_ALLOWED=false` in `udfConfig.properties`
# and the helper will always resolve `current_user()` for Spark DataFrames,
# ignoring `reveal_user_expr` and `reveal_user`.

# COMMAND ----------

print(
    "Python helper smoke test complete. "
    "This notebook exercises Spark-side helper protect and reveal paths and will "
    "use the real CRDP client automatically when the CRDP properties are "
    "pointed at a live endpoint."
)
