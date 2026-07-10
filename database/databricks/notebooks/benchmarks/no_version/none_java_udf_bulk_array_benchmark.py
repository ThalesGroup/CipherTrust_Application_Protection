# Databricks notebook source
# MAGIC %md
# MAGIC # None Java UDF Bulk Array Benchmark
# MAGIC
# MAGIC This is the Java jar / UDF grouped-array benchmark for the `none` mode.
# MAGIC It is intentionally close to the older `internal_bulk_array_benchmark.py`
# MAGIC so you can compare:
# MAGIC
# MAGIC - the original package
# MAGIC - the new Java jar / UDF path
# MAGIC - the new Python wheel / helper path
# MAGIC
# MAGIC This notebook keeps the same grouped-array workload shape, but auto-tunes generation, target partitions, and grouped-array work units from the final execution shape:
# MAGIC
# MAGIC - group many rows into arrays
# MAGIC - call `thales_protect_bulk_by_object_and_column(...)`
# MAGIC - flatten back to rows
# MAGIC - reveal with the scalar object-aware Java UDF for validation
# MAGIC
# MAGIC Use this notebook when you want to answer:
# MAGIC
# MAGIC - is the new Java jar path in the same range as the old Java path?
# MAGIC - how does the new Java jar path compare to the new Python helper path?
# MAGIC - does grouped Java UDF bulk still behave well for CTAS-style compute-cluster loads?

# COMMAND ----------

import math
import time
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import functions as F

# COMMAND ----------

from math import ceil

from pyspark.sql import functions as F


DEFAULT_AVG_ROW_BYTES = 512
ONE_MB = 1024 * 1024


def _safe_collect_scalar(df, column_name, fallback):
    row = df.collect()
    if not row:
        return fallback
    value = row[0][column_name]
    return fallback if value is None else value


def estimate_average_row_bytes(df, sample_rows=2000, fallback_bytes=DEFAULT_AVG_ROW_BYTES):
    sample_count = max(int(sample_rows), 1)
    sampled = df.limit(sample_count)
    stats_df = sampled.select(
        F.avg(F.length(F.to_json(F.struct(*[F.col(c) for c in df.columns])))).alias("avg_row_bytes")
    )
    return float(_safe_collect_scalar(stats_df, "avg_row_bytes", fallback_bytes))


def recommend_generate_partitions(
    row_count,
    default_parallelism,
    min_partitions=8,
):
    row_count = max(int(row_count), 1)
    default_parallelism = max(int(default_parallelism), 1)

    if row_count <= 1_000_000:
        target_rows_per_partition = 250_000
        partition_floor = default_parallelism * 2
        load_tier = "small"
    elif row_count <= 10_000_000:
        target_rows_per_partition = 500_000
        partition_floor = default_parallelism * 4
        load_tier = "medium"
    else:
        target_rows_per_partition = 1_000_000
        partition_floor = default_parallelism * 4
        load_tier = "large"

    data_based_partitions = ceil(row_count / target_rows_per_partition)
    recommended = max(data_based_partitions, partition_floor, int(min_partitions))

    return {
        "recommended_partitions": recommended,
        "load_tier": load_tier,
        "target_rows_per_partition": target_rows_per_partition,
        "partition_floor": partition_floor,
        "data_based_partitions": data_based_partitions,
        "notes": [
            "Generation partitioning is based on row count plus Spark default parallelism.",
            "The partition floor keeps enough tasks available to occupy the cluster.",
        ],
    }


def recommend_target_partitions(
    row_count,
    default_parallelism,
    dataframe=None,
    avg_row_bytes=None,
    sample_rows=2000,
    min_partitions=8,
    target_partition_size_mb=128,
):
    row_count = max(int(row_count), 1)
    default_parallelism = max(int(default_parallelism), 1)
    min_partitions = max(int(min_partitions), 1)
    target_partition_size_bytes = max(int(target_partition_size_mb), 1) * ONE_MB

    if avg_row_bytes is None:
        if dataframe is not None:
            avg_row_bytes = estimate_average_row_bytes(dataframe, sample_rows=sample_rows)
        else:
            avg_row_bytes = DEFAULT_AVG_ROW_BYTES

    estimated_total_bytes = max(int(row_count * float(avg_row_bytes)), 1)
    size_based_partitions = ceil(estimated_total_bytes / target_partition_size_bytes)

    if estimated_total_bytes <= ONE_MB * 1024:
        partition_floor = default_parallelism
        size_tier = "small"
    elif estimated_total_bytes <= ONE_MB * 1024 * 50:
        partition_floor = default_parallelism * 2
        size_tier = "medium"
    else:
        partition_floor = default_parallelism * 4
        size_tier = "large"

    recommended = max(size_based_partitions, partition_floor, min_partitions)

    return {
        "recommended_partitions": recommended,
        "size_tier": size_tier,
        "avg_row_bytes": float(avg_row_bytes),
        "estimated_total_bytes": estimated_total_bytes,
        "estimated_total_mb": round(estimated_total_bytes / ONE_MB, 2),
        "target_partition_size_mb": target_partition_size_mb,
        "partition_floor": partition_floor,
        "size_based_partitions": size_based_partitions,
        "notes": [
            "Target partitioning is based on sampled row width plus Spark default parallelism.",
            "Estimated output size is divided into roughly even 128 MB target partitions.",
        ],
    }


def recommend_helper_execution_controls(
    row_count,
    target_partitions,
    work_unit_multiplier=2.0,
    max_crdp_request_item_target=20000,
):
    row_count = max(int(row_count), 1)
    target_partitions = max(int(target_partitions), 1)
    work_unit_multiplier = max(float(work_unit_multiplier), 1.0)

    work_unit_count_target = max(int(ceil(target_partitions * work_unit_multiplier)), 1)
    work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)

    if max_crdp_request_item_target is None:
        crdp_request_item_target = work_unit_row_count
        request_target_strategy = "align_to_work_unit_row_count"
    else:
        capped_target = max(int(max_crdp_request_item_target), 1)
        crdp_request_item_target = min(work_unit_row_count, capped_target)
        request_target_strategy = "min(work_unit_row_count, max_crdp_request_item_target)"

    return {
        "work_unit_count_target": work_unit_count_target,
        "work_unit_row_count": work_unit_row_count,
        "crdp_request_item_target": crdp_request_item_target,
        "work_unit_multiplier": work_unit_multiplier,
        "request_target_strategy": request_target_strategy,
        "notes": [
            "Helper execution controls are anchored to the final target partition count.",
            "The default strategy creates about 2 work units per target partition.",
        ],
    }


def print_auto_tuning_section(title, values):
    print(title)
    for key, value in values.items():
        if key == "notes":
            print("  notes:")
            for note in value:
                print(f"    - {note}")
        else:
            print(f"  {key}: {value}")


def recommend_java_grouped_array_controls(
    row_count,
    target_partitions,
    config_batch_size,
    work_unit_multiplier=2.0,
    max_crdp_request_item_target=20000,
    explicit_work_unit_count_target=None,
    explicit_work_unit_row_count=None,
    legacy_group_count_override=None,
    legacy_group_size_override=None,
    explicit_crdp_request_item_target=None,
):
    row_count = max(int(row_count), 1)
    target_partitions = max(int(target_partitions), 1)
    config_batch_size = max(int(config_batch_size), 1)
    work_unit_multiplier = max(float(work_unit_multiplier), 1.0)

    if explicit_work_unit_row_count is not None:
        work_unit_row_count = max(int(explicit_work_unit_row_count), 1)
        work_unit_row_strategy = "work_unit_row_count"
        work_unit_count_target = max(int(ceil(float(row_count) / float(work_unit_row_count))), 1)
        work_unit_count_strategy = "derived_from_work_unit_row_count"
    elif legacy_group_size_override is not None:
        work_unit_row_count = max(int(legacy_group_size_override), 1)
        work_unit_row_strategy = "group_size_override"
        work_unit_count_target = max(int(ceil(float(row_count) / float(work_unit_row_count))), 1)
        work_unit_count_strategy = "derived_from_group_size_override"
    elif explicit_work_unit_count_target is not None:
        work_unit_count_target = max(int(explicit_work_unit_count_target), 1)
        work_unit_count_strategy = "work_unit_count_target"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "derived_from_work_unit_count_target"
    elif legacy_group_count_override is not None:
        work_unit_count_target = max(int(legacy_group_count_override), 1)
        work_unit_count_strategy = "group_count_override"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "group_count_override"
    else:
        work_unit_count_target = max(int(ceil(float(target_partitions) * float(work_unit_multiplier))), 1)
        work_unit_count_strategy = "target_partitions_multiplier"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "derived_from_target_partitions_multiplier"

    if explicit_crdp_request_item_target is not None:
        recommended_crdp_request_item_target = max(int(explicit_crdp_request_item_target), 1)
        recommended_crdp_request_item_strategy = "explicit_crdp_request_item_target"
    elif max_crdp_request_item_target is None:
        recommended_crdp_request_item_target = work_unit_row_count
        recommended_crdp_request_item_strategy = "align_to_work_unit_row_count"
    else:
        capped_target = max(int(max_crdp_request_item_target), 1)
        recommended_crdp_request_item_target = min(work_unit_row_count, capped_target)
        recommended_crdp_request_item_strategy = "min(work_unit_row_count, max_crdp_request_item_target)"

    effective_runtime_crdp_request_item_target = min(
        work_unit_row_count,
        recommended_crdp_request_item_target,
    )

    return {
        "work_unit_count_target": work_unit_count_target,
        "work_unit_count_strategy": work_unit_count_strategy,
        "work_unit_row_count": work_unit_row_count,
        "work_unit_row_strategy": work_unit_row_strategy,
        "recommended_crdp_request_item_target": recommended_crdp_request_item_target,
        "recommended_crdp_request_item_strategy": recommended_crdp_request_item_strategy,
        "effective_runtime_crdp_request_item_target": effective_runtime_crdp_request_item_target,
        "runtime_request_item_strategy": "min(work_unit_row_count, recommended_crdp_request_item_target)",
        "config_batch_size_limit": config_batch_size,
        "notes": [
            "Java grouped-array controls are anchored to the final target partition count.",
            "This benchmark applies the derived request target through a Spark SQL conf override.",
            "BATCH_SIZE in udfConfig.properties remains the fallback when no runtime override is applied.",
        ],
    }


# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

ROW_COUNT = 350_000
AUTO_TUNING_SAMPLE_ROWS = 2000
AUTO_WORK_UNIT_MULTIPLIER = 2.0
AUTO_MAX_CRDP_REQUEST_ITEM_TARGET = 20000
default_parallelism = spark.sparkContext.defaultParallelism

GENERATE_PARTITIONS_OVERRIDE = None
TARGET_PARTITIONS_OVERRIDE = None

generate_tuning = recommend_generate_partitions(
    row_count=ROW_COUNT,
    default_parallelism=default_parallelism,
)
GENERATE_PARTITIONS = (
    GENERATE_PARTITIONS_OVERRIDE
    if GENERATE_PARTITIONS_OVERRIDE is not None
    else generate_tuning["recommended_partitions"]
)
TARGET_PARTITIONS = (
    TARGET_PARTITIONS_OVERRIDE
    if TARGET_PARTITIONS_OVERRIDE is not None
    else max(default_parallelism * 2, 32)
)

print_auto_tuning_section("Auto-tuned generation controls:", generate_tuning)
print(f"Initial TARGET_PARTITIONS placeholder: {TARGET_PARTITIONS}")

# Logical tuning controls.
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None

# Legacy compatibility controls.
GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_none_java_udf_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_java_udf_parallelism_diag"
PROTECTED_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_arrays"
ROW_REVEAL_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_none_java_udf_bulk_parallelism_diagnostic_auto_tuned"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../../utils/perf_metrics_helpers"
LOAD_PATTERN = "java_udf_bulk_array_parallelism_diagnostic_auto_tuned_none"
PROTECT_STEP_NAME = "protect_none_table_java_udf_bulk"

# COMMAND ----------

# MAGIC %run ../../utils/perf_metrics_helpers

# COMMAND ----------

CONFIG_PATH = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)


def load_runtime_settings(config_path):
    defaults = {
        "BATCH_SIZE": "1000",
        "CRDP_API_VERSION": "v2",
        "CRDP_REQUEST_ITEM_TARGET": "<not set>",
        "CRDP_MULTI_POLICY_ENABLED": "<not set>",
        "WORK_UNIT_ROW_COUNT": "<not set>",
        "SPARK_GROUP_SIZE": "<not set>",
        "CRDP_V2_MAX_ITEMS_PER_REQUEST": "<not set>",
        "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST": "<not set>",
        "CRDP_V2_ENABLE_MULTI_POLICY": "<not set>",
    }

    if not config_path:
        return defaults, f"UDF_CONFIG_VOLUME_PATH not set; using defaults {defaults}."

    path = Path(config_path)
    if not path.exists():
        return defaults, f"Config file not found at {config_path}; using defaults {defaults}."

    settings = dict(defaults)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in settings:
            settings[key] = value.strip()
    return settings, None


def resolve_group_size(row_count, config_batch_size, group_size_override, group_count_override, group_size_multiplier):
    if WORK_UNIT_ROW_COUNT:
        return max(int(WORK_UNIT_ROW_COUNT), 1), "work_unit_row_count"

    if group_size_override:
        return max(int(group_size_override), 1), "group_size_override"

    if WORK_UNIT_COUNT_TARGET:
        return max(int(math.ceil(float(row_count) / float(WORK_UNIT_COUNT_TARGET))), 1), "work_unit_count_target"

    if group_count_override:
        return max(int(math.ceil(float(row_count) / float(group_count_override))), 1), "group_count_override"

    return max(int(config_batch_size * group_size_multiplier), 1), "batch_size_multiplier"


def parse_optional_int(value):
    try:
        if value is None or str(value).strip().startswith("<"):
            return None
        return int(str(value).strip())
    except ValueError:
        return None


def parse_optional_bool(value):
    if value is None or str(value).strip().startswith("<"):
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "yes", "1", "on"}:
        return True
    if normalized in {"false", "no", "0", "off"}:
        return False
    return None


def validate_positive_setting(name, value):
    if value is not None and int(value) <= 0:
        raise ValueError(f"{name} must be a positive integer. Received: {value}")


def warn_if_small_batch_size(batch_size):
    if batch_size is not None and batch_size < 1000:
        print(
            f"WARNING: BATCH_SIZE/CRDP_REQUEST_ITEM_TARGET is set to {batch_size}. "
            "This is valid for testing, but lower than the normal recommended floor of 1000."
        )


def print_settings_section(title, values):
    print(title)
    for key, value in values.items():
        print(f"  {key}: {value}")


runtime_settings, settings_warning = load_runtime_settings(CONFIG_PATH)
CONFIG_BATCH_SIZE = parse_optional_int(runtime_settings.get("BATCH_SIZE"))
if CONFIG_BATCH_SIZE is None:
    CONFIG_BATCH_SIZE = parse_optional_int(runtime_settings.get("CRDP_REQUEST_ITEM_TARGET"))
if CONFIG_BATCH_SIZE is None:
    CONFIG_BATCH_SIZE = 1000
validate_positive_setting("BATCH_SIZE/CRDP_REQUEST_ITEM_TARGET", CONFIG_BATCH_SIZE)
warn_if_small_batch_size(CONFIG_BATCH_SIZE)
RUNTIME_SPARK_GROUP_SIZE = parse_optional_int(runtime_settings.get("SPARK_GROUP_SIZE"))
if RUNTIME_SPARK_GROUP_SIZE is None:
    RUNTIME_SPARK_GROUP_SIZE = parse_optional_int(runtime_settings.get("WORK_UNIT_ROW_COUNT"))
validate_positive_setting("SPARK_GROUP_SIZE/WORK_UNIT_ROW_COUNT", RUNTIME_SPARK_GROUP_SIZE)
RUNTIME_V2_MAX_ITEMS = parse_optional_int(runtime_settings.get("CRDP_V2_MAX_ITEMS_PER_REQUEST"))
if RUNTIME_V2_MAX_ITEMS is None:
    RUNTIME_V2_MAX_ITEMS = parse_optional_int(runtime_settings.get("CRDP_REQUEST_ITEM_TARGET"))
validate_positive_setting("CRDP_V2_MAX_ITEMS_PER_REQUEST/CRDP_REQUEST_ITEM_TARGET", RUNTIME_V2_MAX_ITEMS)
RUNTIME_V2_MAX_POLICY_GROUPS = parse_optional_int(runtime_settings.get("CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST"))
validate_positive_setting("CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST", RUNTIME_V2_MAX_POLICY_GROUPS)
RUNTIME_V2_ENABLE_MULTI_POLICY = parse_optional_bool(runtime_settings.get("CRDP_V2_ENABLE_MULTI_POLICY"))
if RUNTIME_V2_ENABLE_MULTI_POLICY is None:
    RUNTIME_V2_ENABLE_MULTI_POLICY = parse_optional_bool(runtime_settings.get("CRDP_MULTI_POLICY_ENABLED"))
GROUP_SIZE = None
GROUPING_STRATEGY = None
GROUP_COUNT_STRATEGY = None
ESTIMATED_GROUP_COUNT = None
RECOMMENDED_CRDP_REQUEST_ITEM_TARGET = None
EFFECTIVE_CRDP_REQUEST_ITEM_TARGET = None
CRDP_REQUEST_ITEM_STRATEGY = None

# COMMAND ----------

if settings_warning:
    print("WARNING:", settings_warning)

# COMMAND ----------

generate_start = time.time()
generate_start_ts = datetime.now(timezone.utc)

ids = spark.range(1, ROW_COUNT + 1).repartition(GENERATE_PARTITIONS)

source_df = ids.select(
    F.col("id").cast("bigint").alias("custid"),
    F.concat(F.lit("Member "), F.lpad(F.col("id").cast("string"), 8, "0")).alias("name"),
    F.concat(((F.col("id") % 9999) + 1).cast("string"), F.lit(" Test Street")).alias("address"),
    F.when((F.col("id") % 5) == 0, F.lit("Denver"))
     .when((F.col("id") % 5) == 1, F.lit("Phoenix"))
     .when((F.col("id") % 5) == 2, F.lit("Nashville"))
     .when((F.col("id") % 5) == 3, F.lit("Austin"))
     .otherwise(F.lit("Seattle")).alias("city"),
    F.when((F.col("id") % 5) == 0, F.lit("CO"))
     .when((F.col("id") % 5) == 1, F.lit("AZ"))
     .when((F.col("id") % 5) == 2, F.lit("TN"))
     .when((F.col("id") % 5) == 3, F.lit("TX"))
     .otherwise(F.lit("WA")).alias("state"),
    F.format_string("%05d", (F.col("id") % 99999)).alias("zip"),
    F.format_string("555%07d", (F.col("id") % 10000000)).alias("phone"),
    F.concat(F.lit("member"), F.lpad(F.col("id").cast("string"), 8, "0"), F.lit("@samplecu.org")).alias("email"),
    F.expr("timestamp'1980-01-01 00:00:00' + make_interval(0, 0, 0, cast(id % 12000 as int))").alias("dob"),
    F.expr("CAST(concat('45', lpad(cast(id as string), 14, '0')) AS DECIMAL(25,0))").alias("creditcard"),
    ((F.col("id") % 900) + 100).cast("int").alias("creditcardcode"),
    F.format_string("%09d", (F.col("id") % 1000000000)).alias("ssn"),
)

(
    source_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SOURCE_TABLE)
)

generate_end = time.time()
generate_end_ts = datetime.now(timezone.utc)
print(f"Generated and wrote none Java UDF diagnostic source Delta table in {generate_end - generate_start:.2f} seconds.")

target_tuning = recommend_target_partitions(
    row_count=ROW_COUNT,
    default_parallelism=default_parallelism,
    dataframe=source_df,
    sample_rows=AUTO_TUNING_SAMPLE_ROWS,
)
TARGET_PARTITIONS = (
    TARGET_PARTITIONS_OVERRIDE
    if TARGET_PARTITIONS_OVERRIDE is not None
    else target_tuning["recommended_partitions"]
)
java_execution_tuning = recommend_java_grouped_array_controls(
    row_count=ROW_COUNT,
    target_partitions=TARGET_PARTITIONS,
    config_batch_size=CONFIG_BATCH_SIZE,
    work_unit_multiplier=WORK_UNIT_COUNT_MULTIPLIER,
    max_crdp_request_item_target=AUTO_MAX_CRDP_REQUEST_ITEM_TARGET,
    explicit_work_unit_count_target=WORK_UNIT_COUNT_TARGET,
    explicit_work_unit_row_count=WORK_UNIT_ROW_COUNT,
    legacy_group_count_override=GROUP_COUNT_OVERRIDE,
    legacy_group_size_override=GROUP_SIZE_OVERRIDE,
    explicit_crdp_request_item_target=CRDP_REQUEST_ITEM_TARGET,
)
GROUP_SIZE = java_execution_tuning["work_unit_row_count"]
ESTIMATED_GROUP_COUNT = java_execution_tuning["work_unit_count_target"]
RECOMMENDED_CRDP_REQUEST_ITEM_TARGET = java_execution_tuning["recommended_crdp_request_item_target"]
EFFECTIVE_CRDP_REQUEST_ITEM_TARGET = java_execution_tuning["recommended_crdp_request_item_target"]
GROUPING_STRATEGY = java_execution_tuning["work_unit_row_strategy"]
GROUP_COUNT_STRATEGY = java_execution_tuning["work_unit_count_strategy"]
CRDP_REQUEST_ITEM_STRATEGY = "spark_sql_conf_override"
JAVA_CRDP_REQUEST_ITEM_TARGET_OVERRIDE_CONF = "thales.crdp.request.item.target.override"
spark.conf.set(
    JAVA_CRDP_REQUEST_ITEM_TARGET_OVERRIDE_CONF,
    str(EFFECTIVE_CRDP_REQUEST_ITEM_TARGET),
)

print_auto_tuning_section("Auto-tuned target controls:", target_tuning)
print_auto_tuning_section("Auto-derived Java grouped-array controls:", java_execution_tuning)
print_settings_section(
    "Active Java grouped-array benchmark controls:",
    {
        "row_count": ROW_COUNT,
        "load_pattern": LOAD_PATTERN,
        "source_table": SOURCE_TABLE,
        "target_table": TARGET_TABLE,
        "protected_object_name": PROTECTED_OBJECT_NAME,
        "metrics_helpers_notebook_path": METRICS_HELPERS_NOTEBOOK_PATH,
        "generate_partitions": GENERATE_PARTITIONS,
        "target_partitions": TARGET_PARTITIONS,
        "generate_partitions_override": GENERATE_PARTITIONS_OVERRIDE,
        "target_partitions_override": TARGET_PARTITIONS_OVERRIDE,
        "auto_tuning_sample_rows": AUTO_TUNING_SAMPLE_ROWS,
        "auto_work_unit_multiplier": AUTO_WORK_UNIT_MULTIPLIER,
        "auto_max_crdp_request_item_target": AUTO_MAX_CRDP_REQUEST_ITEM_TARGET,
        "java_request_item_target_override_conf": JAVA_CRDP_REQUEST_ITEM_TARGET_OVERRIDE_CONF,
        "work_unit_count_target": WORK_UNIT_COUNT_TARGET,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": WORK_UNIT_ROW_COUNT,
        "crdp_request_item_target": CRDP_REQUEST_ITEM_TARGET,
        "crdp_multi_policy_enabled": CRDP_MULTI_POLICY_ENABLED,
        "group_size_override": GROUP_SIZE_OVERRIDE,
        "group_count_override": GROUP_COUNT_OVERRIDE,
        "group_size_multiplier": GROUP_SIZE_MULTIPLIER,
        "batch_size": CONFIG_BATCH_SIZE,
    },
)
print_settings_section(
    "Derived effective tuning controls:",
    {
        "effective_generate_partitions": GENERATE_PARTITIONS,
        "effective_target_partitions": TARGET_PARTITIONS,
        "work_unit_count_target": ESTIMATED_GROUP_COUNT,
        "work_unit_count_strategy": GROUP_COUNT_STRATEGY,
        "work_unit_row_count": GROUP_SIZE,
        "work_unit_row_strategy": GROUPING_STRATEGY,
        "recommended_crdp_request_item_target": RECOMMENDED_CRDP_REQUEST_ITEM_TARGET,
        "recommended_crdp_request_item_strategy": java_execution_tuning["recommended_crdp_request_item_strategy"],
        "recommended_crdp_request_item_target": RECOMMENDED_CRDP_REQUEST_ITEM_TARGET,
        "effective_crdp_request_item_target": EFFECTIVE_CRDP_REQUEST_ITEM_TARGET,
        "crdp_request_item_strategy": CRDP_REQUEST_ITEM_STRATEGY,
        "multi_policy_enabled": False,
        "estimated_group_count": ESTIMATED_GROUP_COUNT,
    },
)
print(f"Applied Java runtime CRDP request target override: {JAVA_CRDP_REQUEST_ITEM_TARGET_OVERRIDE_CONF}={EFFECTIVE_CRDP_REQUEST_ITEM_TARGET}")

print_settings_section(
    "Shared runtime settings (informational):",
    {
        "runtime_settings": runtime_settings,
        "runtime_api_version": runtime_settings.get("CRDP_API_VERSION"),
        "runtime_crdp_request_item_target": runtime_settings.get("CRDP_REQUEST_ITEM_TARGET"),
        "runtime_crdp_multi_policy_enabled": runtime_settings.get("CRDP_MULTI_POLICY_ENABLED"),
        "runtime_work_unit_row_count": runtime_settings.get("WORK_UNIT_ROW_COUNT"),
        "runtime_spark_group_size": RUNTIME_SPARK_GROUP_SIZE,
        "runtime_v2_max_items_per_request": RUNTIME_V2_MAX_ITEMS,
        "runtime_v2_max_policy_groups_per_request": RUNTIME_V2_MAX_POLICY_GROUPS,
        "runtime_v2_enable_multi_policy": RUNTIME_V2_ENABLE_MULTI_POLICY,
        "resolver_notes": [
            "Java grouped-array auto-tuning uses target partitions as the anchor for work-unit sizing.",
            "This benchmark applies the derived request target through spark.conf using thales.crdp.request.item.target.override.",
            "If the patched jar is not deployed, Java falls back to BATCH_SIZE or CRDP_REQUEST_ITEM_TARGET from udfConfig.properties.",
            "Current Java grouped-array benchmark does not yet use Python-style v2 multi-policy grouping as an active runtime knob.",
        ],
    },
)

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="generate_source_delta",
    row_count=ROW_COUNT,
    duration_seconds=generate_end - generate_start,
    extra_metrics={
        "generate_partitions": GENERATE_PARTITIONS,
        "target_partitions": TARGET_PARTITIONS,
        "source_table": SOURCE_TABLE,
        "target_table": TARGET_TABLE,
        "cluster_vm_hint": CLUSTER_VM_HINT,
        "load_pattern": LOAD_PATTERN,
        "config_batch_size": CONFIG_BATCH_SIZE,
        "group_size": GROUP_SIZE,
        "group_size_multiplier": GROUP_SIZE_MULTIPLIER,
        "benchmark_mode": True,
        "group_count_override": GROUP_COUNT_OVERRIDE,
        "estimated_group_count": ESTIMATED_GROUP_COUNT,
        "effective_generate_partitions": GENERATE_PARTITIONS,
        "effective_target_partitions": TARGET_PARTITIONS,
        "work_unit_count_target": ESTIMATED_GROUP_COUNT,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": GROUP_SIZE,
        "recommended_crdp_request_item_target": RECOMMENDED_CRDP_REQUEST_ITEM_TARGET,
        "effective_crdp_request_item_target": EFFECTIVE_CRDP_REQUEST_ITEM_TARGET,
        "grouping_strategy": GROUPING_STRATEGY,
        "crdp_request_item_strategy": CRDP_REQUEST_ITEM_STRATEGY,
        "crdp_api_version": runtime_settings.get("CRDP_API_VERSION"),
        "transport_mode": "java_udf",
        "spark_group_size": RUNTIME_SPARK_GROUP_SIZE,
        "v2_max_items_per_request": RUNTIME_V2_MAX_ITEMS,
        "v2_max_policy_groups_per_request": RUNTIME_V2_MAX_POLICY_GROUPS,
        "v2_enable_multi_policy": RUNTIME_V2_ENABLE_MULTI_POLICY,
        "step_start_ts": generate_start_ts,
        "step_end_ts": generate_end_ts,
    },
)

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this benchmark."
    )

if not spark.catalog.functionExists("thales_protect_bulk_by_object_and_column"):
    spark.udf.registerJavaFunction(
        "thales_protect_bulk_by_object_and_column",
        "com.thales.databricks.integration.udf.ThalesProtectBulkByObjectAndColumnUdf",
        "array<string>",
    )
    print(
        "Registered Java UDF: thales_protect_bulk_by_object_and_column -> "
        "com.thales.databricks.integration.udf.ThalesProtectBulkByObjectAndColumnUdf"
    )

if not spark.catalog.functionExists("thales_reveal_by_object_and_column_with_user"):
    spark.udf.registerJavaFunction(
        "thales_reveal_by_object_and_column_with_user",
        "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithUserUdf",
        "string",
    )
    print(
        "Registered Java UDF: thales_reveal_by_object_and_column_with_user -> "
        "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithUserUdf"
    )

# COMMAND ----------

protect_start = time.time()
protect_start_ts = datetime.now(timezone.utc)

ordered_df = spark.table(SOURCE_TABLE).orderBy("custid")

grouped_df = (
    ordered_df.withColumn("group_id", F.floor((F.col("custid") - F.lit(1)) / F.lit(GROUP_SIZE)))
    .groupBy("group_id")
    .agg(
        F.collect_list("custid").alias("custid_array"),
        F.collect_list("name").alias("name_array"),
        F.collect_list("address").alias("address_array"),
        F.collect_list("city").alias("city_array"),
        F.collect_list("state").alias("state_array"),
        F.collect_list("zip").alias("zip_array"),
        F.collect_list("phone").alias("phone_array"),
        F.collect_list("email").alias("email_array"),
        F.collect_list("dob").alias("dob_array"),
        F.collect_list(F.col("creditcard").cast("string")).alias("creditcard_array"),
        F.collect_list(F.col("creditcardcode").cast("string")).alias("creditcardcode_array"),
        F.collect_list("ssn").alias("ssn_array"),
    )
)

protected_grouped_df = grouped_df.select(
    "group_id",
    "custid_array",
    "name_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column(address_array, 'char', '{PROTECTED_OBJECT_NAME}', 'address')"
    ).alias("address_array"),
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column(email_array, 'char', '{PROTECTED_OBJECT_NAME}', 'email')"
    ).alias("email_array"),
    "dob_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column(creditcard_array, 'nbr', '{PROTECTED_OBJECT_NAME}', 'creditcard')"
    ).alias("creditcard_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column(creditcardcode_array, 'nbr', '{PROTECTED_OBJECT_NAME}', 'creditcardcode')"
    ).alias("creditcardcode_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column(ssn_array, 'nbr', '{PROTECTED_OBJECT_NAME}', 'ssn')"
    ).alias("ssn_array"),
)

flattened_df = protected_grouped_df.select(
    F.posexplode("custid_array").alias("pos", "custid"),
    "name_array",
    "address_array",
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    "email_array",
    "dob_array",
    "creditcard_array",
    "creditcardcode_array",
    "ssn_array",
).select(
    F.col("custid").cast("bigint").alias("custid"),
    F.element_at("name_array", F.col("pos") + 1).alias("name"),
    F.element_at("address_array", F.col("pos") + 1).alias("address"),
    F.element_at("city_array", F.col("pos") + 1).alias("city"),
    F.element_at("state_array", F.col("pos") + 1).alias("state"),
    F.element_at("zip_array", F.col("pos") + 1).alias("zip"),
    F.element_at("phone_array", F.col("pos") + 1).alias("phone"),
    F.element_at("email_array", F.col("pos") + 1).alias("email"),
    F.element_at("dob_array", F.col("pos") + 1).alias("dob"),
    F.element_at("creditcard_array", F.col("pos") + 1).alias("creditcard"),
    F.element_at("creditcardcode_array", F.col("pos") + 1).alias("creditcardcode"),
    F.element_at("ssn_array", F.col("pos") + 1).alias("ssn"),
)

(
    flattened_df.repartition(TARGET_PARTITIONS).write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

protect_end = time.time()
protect_end_ts = datetime.now(timezone.utc)
print(f"Java UDF bulk array diagnostic completed in {protect_end - protect_start:.2f} seconds.")

target_count = spark.table(TARGET_TABLE).count()
print(f"Java UDF diagnostic protected target row count: {target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "Java UDF diagnostic target row count did not match the expected source row count. "
        f"Expected: {ROW_COUNT}, Actual: {target_count}"
    )

append_perf_metrics(
    run_name=RUN_NAME,
    step_name=PROTECT_STEP_NAME,
    row_count=ROW_COUNT,
    duration_seconds=protect_end - protect_start,
    extra_metrics={
        "generate_partitions": GENERATE_PARTITIONS,
        "target_partitions": TARGET_PARTITIONS,
        "source_table": SOURCE_TABLE,
        "target_table": TARGET_TABLE,
        "cluster_vm_hint": CLUSTER_VM_HINT,
        "load_pattern": LOAD_PATTERN,
        "config_batch_size": CONFIG_BATCH_SIZE,
        "group_size": GROUP_SIZE,
        "group_size_multiplier": GROUP_SIZE_MULTIPLIER,
        "benchmark_mode": True,
        "group_count_override": GROUP_COUNT_OVERRIDE,
        "estimated_group_count": ESTIMATED_GROUP_COUNT,
        "effective_generate_partitions": GENERATE_PARTITIONS,
        "effective_target_partitions": TARGET_PARTITIONS,
        "work_unit_count_target": ESTIMATED_GROUP_COUNT,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": GROUP_SIZE,
        "recommended_crdp_request_item_target": RECOMMENDED_CRDP_REQUEST_ITEM_TARGET,
        "effective_crdp_request_item_target": EFFECTIVE_CRDP_REQUEST_ITEM_TARGET,
        "grouping_strategy": GROUPING_STRATEGY,
        "crdp_request_item_strategy": CRDP_REQUEST_ITEM_STRATEGY,
        "crdp_api_version": runtime_settings.get("CRDP_API_VERSION"),
        "transport_mode": "java_udf",
        "spark_group_size": RUNTIME_SPARK_GROUP_SIZE,
        "v2_max_items_per_request": RUNTIME_V2_MAX_ITEMS,
        "v2_max_policy_groups_per_request": RUNTIME_V2_MAX_POLICY_GROUPS,
        "v2_enable_multi_policy": RUNTIME_V2_ENABLE_MULTI_POLICY,
        "step_start_ts": protect_start_ts,
        "step_end_ts": protect_end_ts,
    },
)

# COMMAND ----------

display(spark.createDataFrame([(ROW_COUNT,)], ["source_count"]))
display(spark.createDataFrame([(target_count,)], ["protected_count"]))
display(spark.sql(f"SELECT * FROM {TARGET_TABLE} LIMIT 5"))

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW v_internal_java_udf_parallelism_diag_revealed AS
    SELECT
      custid,
      name,
      thales_reveal_by_object_and_column_with_user(
        CAST(address AS STRING),
        'char',
        '{ROW_REVEAL_OBJECT_NAME}',
        'address',
        current_user()
      ) AS address,
      city,
      state,
      zip,
      phone,
      thales_reveal_by_object_and_column_with_user(
        CAST(email AS STRING),
        'char',
        '{ROW_REVEAL_OBJECT_NAME}',
        'email',
        current_user()
      ) AS email,
      dob,
      CAST(
        thales_reveal_by_object_and_column_with_user(
          CAST(creditcard AS STRING),
          'nbr',
          '{ROW_REVEAL_OBJECT_NAME}',
          'creditcard',
          current_user()
        ) AS DECIMAL(25,0)
      ) AS creditcard,
      CAST(
        thales_reveal_by_object_and_column_with_user(
          CAST(creditcardcode AS STRING),
          'nbr',
          '{ROW_REVEAL_OBJECT_NAME}',
          'creditcardcode',
          current_user()
        ) AS INT
      ) AS creditcardcode,
      thales_reveal_by_object_and_column_with_user(
        CAST(ssn AS STRING),
        'nbr',
        '{ROW_REVEAL_OBJECT_NAME}',
        'ssn',
        current_user()
      ) AS ssn
    FROM {TARGET_TABLE}
    """
)

display(spark.sql("SELECT * FROM v_internal_java_udf_parallelism_diag_revealed LIMIT 5"))
display(spark.sql(f"SELECT * FROM {METRICS_TABLE} ORDER BY metric_ts_utc DESC LIMIT 20"))

create_perf_summary_view(SUMMARY_VIEW)
create_perf_compact_view(COMPACT_SUMMARY_VIEW, SUMMARY_VIEW)

display(
    spark.sql(
        build_compact_metrics_query(
            COMPACT_SUMMARY_VIEW,
            RUN_NAME,
            extra_columns=[
                "crdp_api_version",
                "transport_mode",
                "spark_group_size",
                "v2_max_items_per_request",
                "v2_max_policy_groups_per_request",
                "v2_enable_multi_policy",
            ],
        )
    )
)

print("THALES_JAVA_UDF_BULK_ARRAY_DIAGNOSTIC_AUTO_TUNED_FINISHED")

display(
    spark.sql(
        f"""
        SELECT *
        FROM {METRICS_TABLE}
        WHERE step_name = '{PROTECT_STEP_NAME}'
          AND row_count = {ROW_COUNT}
        ORDER BY duration_seconds
        LIMIT 20
        """
    )
)




# COMMAND ----------

# Inspect CRDP request sizing details captured inside notes_json.
display(
    spark.sql(
        f"""
        SELECT
          metric_ts_utc,
          step_name,
          row_count,
          duration_seconds,
          rows_per_second,
          group_size,
          get_json_object(notes_json, '$.effective_crdp_request_item_target') AS effective_crdp_request_item_target,
          get_json_object(notes_json, '$.recommended_crdp_request_item_target') AS recommended_crdp_request_item_target,
          get_json_object(notes_json, '$.crdp_request_item_strategy') AS crdp_request_item_strategy
        FROM {METRICS_TABLE}
        WHERE run_name = '{RUN_NAME}'
        ORDER BY metric_ts_utc DESC
        LIMIT 20
        """
    )
)

