# Databricks notebook source
# MAGIC %md
# MAGIC # External Pandas UDF Benchmark
# MAGIC
# MAGIC This is the helper-first compute-cluster benchmark for the external/header
# MAGIC path in the new integration. It mirrors the internal helper benchmark, but
# MAGIC validates that protect writes sibling `*_header` columns and reveal uses
# MAGIC those headers automatically.

# COMMAND ----------

import time
from datetime import datetime, timezone

from pyspark.sql import functions as F

from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe_map_in_pandas,
    reveal_dataframe_map_in_pandas,
    resolve_python_helper_tuning,
)

# COMMAND ----------

from math import ceil


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


# COMMAND ----------

# --- 1. RUN CONFIGURATION & AUTO-TUNING ---
CATALOG = "my_catalog"
SCHEMA = "my_schema"
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

ROW_COUNT = 350_000  # 350_000, 5_000_000, 300_000_000
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
    else max(default_parallelism * 2, 8)
)

print_auto_tuning_section("Auto-tuned generation controls:", generate_tuning)
print(f"Initial TARGET_PARTITIONS placeholder: {TARGET_PARTITIONS}")

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_external_pandas_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_pandas_parallelism_diag"
PROTECTED_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_external_pandas_udf_parallelism_diagnostic"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../../utils/perf_metrics_helpers"
LOAD_PATTERN = "external_external_pandas_map_in_pandas_parallelism_diagnostic"
PROTECT_STEP_NAME = "protect_external_table_pandas_udf"

API_VERSION_OVERRIDE = None
TRANSPORT_MODE_OVERRIDE = "real"
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None

# Legacy compatibility overrides.
SPARK_GROUP_SIZE_OVERRIDE = None
V2_MAX_ITEMS_PER_REQUEST_OVERRIDE = None
V2_MAX_POLICY_GROUPS_PER_REQUEST_OVERRIDE = None
V2_ENABLE_MULTI_POLICY_OVERRIDE = None

# Placeholder to allow compilation of early logging scripts
tuning_resolution = None

# COMMAND ----------

# MAGIC %run ../../utils/perf_metrics_helpers

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)

effective_api_version = API_VERSION_OVERRIDE or config.crdp_api_version
effective_transport_mode = TRANSPORT_MODE_OVERRIDE or config.transport_mode
requested_v2_max_items = V2_MAX_ITEMS_PER_REQUEST_OVERRIDE or config.crdp_v2_max_items_per_request
effective_v2_max_policy_groups = (
    V2_MAX_POLICY_GROUPS_PER_REQUEST_OVERRIDE or config.crdp_v2_max_policy_groups_per_request
)
requested_v2_enable_multi_policy = (
    V2_ENABLE_MULTI_POLICY_OVERRIDE
    if V2_ENABLE_MULTI_POLICY_OVERRIDE is not None
    else config.crdp_v2_enable_multi_policy
)


def print_settings_section(title, values):
    print(title)
    for key, value in values.items():
        print(f"  {key}: {value}")


def warn_if_small_batch_size(batch_size):
    if batch_size < 1000:
        print(
            f"WARNING: BATCH_SIZE/CRDP_REQUEST_ITEM_TARGET is set to {batch_size}. "
            "This is valid for testing, but lower than the normal recommended floor of 1000."
        )


warn_if_small_batch_size(config.default_batch_size)

# COMMAND ----------

# --- 3. SOURCE TABLE GENERATION PHASE ---
generate_start = time.time()
generate_start_ts = datetime.now(timezone.utc)

print(f"Generating data using scale-mode partitioning: GENERATE_PARTITIONS = {GENERATE_PARTITIONS}")
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
print(f"Generated and wrote external Pandas diagnostic source Delta table in {generate_end - generate_start:.2f} seconds.")

# --- 4. DYNAMIC PROCESSING TARGET PARTITION SIZING ---
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
helper_execution_tuning = recommend_helper_execution_controls(
    row_count=ROW_COUNT,
    target_partitions=TARGET_PARTITIONS,
    work_unit_multiplier=WORK_UNIT_COUNT_MULTIPLIER,
    max_crdp_request_item_target=AUTO_MAX_CRDP_REQUEST_ITEM_TARGET,
)
EFFECTIVE_WORK_UNIT_COUNT_TARGET = (
    WORK_UNIT_COUNT_TARGET
    if WORK_UNIT_COUNT_TARGET is not None
    else helper_execution_tuning["work_unit_count_target"]
)
EFFECTIVE_CRDP_REQUEST_ITEM_TARGET = (
    CRDP_REQUEST_ITEM_TARGET
    if CRDP_REQUEST_ITEM_TARGET is not None
    else helper_execution_tuning["crdp_request_item_target"]
)
EFFECTIVE_CRDP_MULTI_POLICY_ENABLED = (
    CRDP_MULTI_POLICY_ENABLED
    if CRDP_MULTI_POLICY_ENABLED is not None
    else True
)

print_auto_tuning_section("Auto-tuned target controls:", target_tuning)
print_auto_tuning_section("Auto-derived helper execution controls:", helper_execution_tuning)
# -----------------------------------------------------

# --- 5. INITIALIZE DYNAMIC TUNING ENGINE ---
tuning_resolution = resolve_python_helper_tuning(
    row_count=ROW_COUNT,
    default_parallelism=default_parallelism,
    config_batch_size=config.default_batch_size,
    spark_group_size=config.spark_group_size,
    v2_max_items_per_request=requested_v2_max_items,
    v2_max_policy_groups_per_request=config.crdp_v2_max_policy_groups_per_request,
    v2_enable_multi_policy=requested_v2_enable_multi_policy,
    generate_partitions=GENERATE_PARTITIONS,
    target_partitions=TARGET_PARTITIONS, 
    spark_group_size_override=SPARK_GROUP_SIZE_OVERRIDE,
    work_unit_count_target=WORK_UNIT_COUNT_TARGET,
    work_unit_count_multiplier=WORK_UNIT_COUNT_MULTIPLIER,
    work_unit_row_count=WORK_UNIT_ROW_COUNT,
    crdp_request_item_target=CRDP_REQUEST_ITEM_TARGET,
    api_version=effective_api_version,
)

effective_spark_group_size = tuning_resolution.work_unit_row_count
effective_v2_max_items = (
    tuning_resolution.effective_crdp_request_item_target
    if effective_api_version.strip().lower() == "v2"
    else requested_v2_max_items
)
effective_v2_enable_multi_policy = EFFECTIVE_CRDP_MULTI_POLICY_ENABLED
ESTIMATED_GROUP_COUNT = tuning_resolution.work_unit_count_target

helper_options = {
    "api_version": effective_api_version,
    "transport_mode": effective_transport_mode,
    "spark_group_size": effective_spark_group_size,
    "batch_size": tuning_resolution.effective_crdp_request_item_target,
    "v2_max_items_per_request": effective_v2_max_items,
    "v2_max_policy_groups_per_request": effective_v2_max_policy_groups,
    "v2_enable_multi_policy": effective_v2_enable_multi_policy,
}
# --------------------------------------------

print_settings_section(
    "Active Pandas benchmark controls:",
    {
        "row_count": ROW_COUNT,
        "load_pattern": LOAD_PATTERN,
        "source_table": SOURCE_TABLE,
        "target_table": TARGET_TABLE,
        "protected_object_name": PROTECTED_OBJECT_NAME,
        "metrics_helpers_notebook_path": METRICS_HELPERS_NOTEBOOK_PATH,
        "api_version": effective_api_version,
        "transport_mode": effective_transport_mode,
        "generate_partitions": GENERATE_PARTITIONS,
        "target_partitions": TARGET_PARTITIONS,
        "generate_partitions_override": GENERATE_PARTITIONS_OVERRIDE,
        "target_partitions_override": TARGET_PARTITIONS_OVERRIDE,
        "work_unit_count_target": EFFECTIVE_WORK_UNIT_COUNT_TARGET,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": WORK_UNIT_ROW_COUNT,
        "crdp_request_item_target": EFFECTIVE_CRDP_REQUEST_ITEM_TARGET,
        "crdp_multi_policy_enabled": EFFECTIVE_CRDP_MULTI_POLICY_ENABLED,
        "spark_group_size_override": SPARK_GROUP_SIZE_OVERRIDE,
        "v2_max_items_per_request_override": V2_MAX_ITEMS_PER_REQUEST_OVERRIDE,
        "v2_max_policy_groups_per_request_override": V2_MAX_POLICY_GROUPS_PER_REQUEST_OVERRIDE,
        "v2_enable_multi_policy_override": V2_ENABLE_MULTI_POLICY_OVERRIDE,
    },
)
print_settings_section(
    "Derived effective tuning controls:",
    {
        "effective_generate_partitions": tuning_resolution.effective_generate_partitions,
        "effective_target_partitions": tuning_resolution.effective_target_partitions,
        "work_unit_count_target": tuning_resolution.work_unit_count_target,
        "work_unit_count_strategy": tuning_resolution.work_unit_count_strategy,
        "work_unit_row_count": tuning_resolution.work_unit_row_count,
        "work_unit_row_strategy": tuning_resolution.work_unit_row_strategy,
        "effective_crdp_request_item_target": tuning_resolution.effective_crdp_request_item_target,
        "crdp_request_item_strategy": tuning_resolution.crdp_request_item_strategy,
        "multi_policy_enabled": tuning_resolution.multi_policy_enabled,
        "estimated_pandas_row_groups": ESTIMATED_GROUP_COUNT,
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
        "config_batch_size": config.default_batch_size,
        "group_size": effective_spark_group_size,
        "group_size_multiplier": None,
        "benchmark_mode": True,
        "estimated_group_count": ESTIMATED_GROUP_COUNT,
        "effective_generate_partitions": tuning_resolution.effective_generate_partitions,
        "effective_target_partitions": tuning_resolution.effective_target_partitions,
        "work_unit_count_target": tuning_resolution.work_unit_count_target,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": tuning_resolution.work_unit_row_count,
        "effective_crdp_request_item_target": tuning_resolution.effective_crdp_request_item_target,
        "crdp_api_version": effective_api_version,
        "transport_mode": effective_transport_mode,
        "spark_group_size": effective_spark_group_size,
        "v2_max_items_per_request": effective_v2_max_items,
        "v2_max_policy_groups_per_request": effective_v2_max_policy_groups,
        "v2_enable_multi_policy": effective_v2_enable_multi_policy,
        "step_start_ts": generate_start_ts,
        "step_end_ts": generate_end_ts,
    },
)

# COMMAND ----------

# --- 6. SECURITY PROTECTION PHASE ---
protect_start = time.time()
protect_start_ts = datetime.now(timezone.utc)

protected_df = protect_dataframe_map_in_pandas(
    spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)

(
    protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

protect_end = time.time()
protect_end_ts = datetime.now(timezone.utc)
print(f"External helper DataFrame diagnostic completed in {protect_end - protect_start:.2f} seconds.")

target_count = spark.table(TARGET_TABLE).count()
print(f"External helper diagnostic protected target row count: {target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "External helper diagnostic target row count did not match the expected source row count. "
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
        "config_batch_size": config.default_batch_size,
        "group_size": effective_spark_group_size,
        "group_size_multiplier": None,
        "benchmark_mode": True,
        "estimated_group_count": ESTIMATED_GROUP_COUNT,
        "effective_generate_partitions": tuning_resolution.effective_generate_partitions,
        "effective_target_partitions": tuning_resolution.effective_target_partitions,
        "work_unit_count_target": tuning_resolution.work_unit_count_target,
        "work_unit_count_multiplier": WORK_UNIT_COUNT_MULTIPLIER,
        "work_unit_row_count": tuning_resolution.work_unit_row_count,
        "effective_crdp_request_item_target": tuning_resolution.effective_crdp_request_item_target,
        "crdp_api_version": effective_api_version,
        "transport_mode": effective_transport_mode,
        "spark_group_size": effective_spark_group_size,
        "v2_max_items_per_request": effective_v2_max_items,
        "v2_max_policy_groups_per_request": effective_v2_max_policy_groups,
        "v2_enable_multi_policy": effective_v2_enable_multi_policy,
        "plan_summary": getattr(protected_df, "_thales_bulk_plan_summary", None),
        "step_start_ts": protect_start_ts,
        "step_end_ts": protect_end_ts,
    },
)

# COMMAND ----------

# --- 7. REVEAL & METRICS REPORTING PHASE ---
display(spark.createDataFrame([(ROW_COUNT,)], ["source_count"]))
display(spark.createDataFrame([(target_count,)], ["protected_count"]))
display(spark.sql(f"SELECT * FROM {TARGET_TABLE} LIMIT 5"))

revealed_df = reveal_dataframe_map_in_pandas(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)

revealed_df.createOrReplaceTempView("v_external_helper_parallelism_diag_revealed")

display(spark.sql("SELECT * FROM v_external_helper_parallelism_diag_revealed LIMIT 5"))
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

print("THALES_EXTERNAL_HELPER_DATAFRAME_DIAGNOSTIC_FINISHED")

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

