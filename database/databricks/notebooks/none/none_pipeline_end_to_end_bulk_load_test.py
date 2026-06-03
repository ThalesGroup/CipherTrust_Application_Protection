# Databricks notebook source
# MAGIC %md
# MAGIC # None Pipeline End-to-End Bulk Load Test
# MAGIC
# MAGIC This notebook is the end-to-end none/no-version bulk pipeline example for
# MAGIC a customer-like environment.

# COMMAND ----------

import math
import time
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 15_000_000
RAW_FILE_PARTITIONS = 32
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)

GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0

RAW_ADLS_PATH = "abfss://landing@mydatalake.dfs.core.windows.net/thales/load_test/plaintext_plaintext_none_bulk_raw/"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_none_bulk_load_test"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_bulk_load_test"
ARRAY_TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_bulk_load_test_arrays"
PROTECTED_ARRAY_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_arrays"
ROW_REVEAL_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_none_pipeline_bulk_load_test"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
LOAD_PATTERN = "pipeline_with_adls_bulk_object_aware_none"
PROTECT_STEP_NAME = "protect_none_table_bulk_object_aware"

# COMMAND ----------

# MAGIC %run ../utils/perf_metrics_helpers

# COMMAND ----------

CONFIG_PATH = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)


def load_batch_size_from_properties(config_path):
    default_batch_size = 1000

    if not config_path:
        return default_batch_size, None, f"UDF_CONFIG_VOLUME_PATH not set; using fallback {default_batch_size}."

    path = Path(config_path)
    if not path.exists():
        return default_batch_size, None, f"Config file not found at {config_path}; using fallback {default_batch_size}."

    raw_batch_size = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "BATCH_SIZE":
            raw_batch_size = value.strip()
            break

    if raw_batch_size is None:
        return default_batch_size, None, f"BATCH_SIZE not present in config file; using fallback {default_batch_size}."

    try:
        parsed_batch_size = int(raw_batch_size)
    except ValueError:
        return default_batch_size, raw_batch_size, (
            f"Invalid BATCH_SIZE '{raw_batch_size}' in config file; using fallback {default_batch_size}."
        )

    if parsed_batch_size <= 0:
        return default_batch_size, raw_batch_size, (
            f"Invalid BATCH_SIZE '{raw_batch_size}' in config file; using fallback {default_batch_size}."
        )

    return parsed_batch_size, raw_batch_size, None


def resolve_group_size(row_count, config_batch_size, group_size_override, group_count_override, group_size_multiplier):
    if group_size_override:
        return max(int(group_size_override), 1), "group_size_override"

    if group_count_override:
        return max(int(math.ceil(float(row_count) / float(group_count_override))), 1), "group_count_override"

    return max(int(config_batch_size * group_size_multiplier), 1), "batch_size_multiplier"


CONFIG_BATCH_SIZE, RAW_CONFIG_BATCH_SIZE, BATCH_SIZE_WARNING = load_batch_size_from_properties(CONFIG_PATH)
GROUP_SIZE, GROUPING_STRATEGY = resolve_group_size(
    ROW_COUNT,
    CONFIG_BATCH_SIZE,
    GROUP_SIZE_OVERRIDE,
    GROUP_COUNT_OVERRIDE,
    GROUP_SIZE_MULTIPLIER,
)
ESTIMATED_GROUP_COUNT = int(math.ceil(float(ROW_COUNT) / float(GROUP_SIZE)))

# COMMAND ----------

print("Row count:", ROW_COUNT)
print("Raw file partitions:", RAW_FILE_PARTITIONS)
print("Protect target partitions:", TARGET_PARTITIONS)
print("Raw ADLS path:", RAW_ADLS_PATH)
print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Array target table:", ARRAY_TARGET_TABLE)
print("Protected array object mapping:", PROTECTED_ARRAY_OBJECT_NAME)
print("Raw BATCH_SIZE setting in config file:", RAW_CONFIG_BATCH_SIZE if RAW_CONFIG_BATCH_SIZE is not None else "<missing>")
print("Effective BATCH_SIZE used by notebook:", CONFIG_BATCH_SIZE)
if BATCH_SIZE_WARNING:
    print("WARNING:", BATCH_SIZE_WARNING)
print("Group size override:", GROUP_SIZE_OVERRIDE)
print("Group count override:", GROUP_COUNT_OVERRIDE)
print("Group size multiplier:", GROUP_SIZE_MULTIPLIER)
print("Resolved grouping strategy:", GROUPING_STRATEGY)
print("Resolved group size:", GROUP_SIZE)
print("Estimated grouped UDF rows:", ESTIMATED_GROUP_COUNT)
print("Load pattern:", LOAD_PATTERN)
print("Metrics helpers notebook path:", METRICS_HELPERS_NOTEBOOK_PATH)

# COMMAND ----------

ids = spark.range(1, ROW_COUNT + 1)

synthetic_df = ids.select(
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

# COMMAND ----------

raw_write_start = time.time()
raw_write_start_ts = datetime.now(timezone.utc)

(
    synthetic_df.repartition(RAW_FILE_PARTITIONS)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(RAW_ADLS_PATH)
)

raw_write_end = time.time()
raw_write_end_ts = datetime.now(timezone.utc)

print("Raw CSV files written to ADLS Gen2 path.")

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="write_raw_csv_to_adls",
    row_count=ROW_COUNT,
    duration_seconds=raw_write_end - raw_write_start,
    extra_metrics={
        "raw_file_partitions": RAW_FILE_PARTITIONS,
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
        "grouping_strategy": GROUPING_STRATEGY,
        "raw_adls_path": RAW_ADLS_PATH,
        "step_start_ts": raw_write_start_ts,
        "step_end_ts": raw_write_end_ts,
    },
)

# COMMAND ----------

source_schema = T.StructType([
    T.StructField("custid", T.LongType(), True),
    T.StructField("name", T.StringType(), True),
    T.StructField("address", T.StringType(), True),
    T.StructField("city", T.StringType(), True),
    T.StructField("state", T.StringType(), True),
    T.StructField("zip", T.StringType(), True),
    T.StructField("phone", T.StringType(), True),
    T.StructField("email", T.StringType(), True),
    T.StructField("dob", T.TimestampType(), True),
    T.StructField("creditcard", T.DecimalType(25, 0), True),
    T.StructField("creditcardcode", T.IntegerType(), True),
    T.StructField("ssn", T.StringType(), True),
])

delta_load_start = time.time()
delta_load_start_ts = datetime.now(timezone.utc)

loaded_df = (
    spark.read.schema(source_schema)
    .option("header", "true")
    .csv(RAW_ADLS_PATH)
)

(
    loaded_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SOURCE_TABLE)
)

print("Source Delta table created from ADLS raw files.")

delta_load_end = time.time()
delta_load_end_ts = datetime.now(timezone.utc)

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="load_raw_csv_into_delta",
    row_count=ROW_COUNT,
    duration_seconds=delta_load_end - delta_load_start,
    extra_metrics={
        "raw_file_partitions": RAW_FILE_PARTITIONS,
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
        "grouping_strategy": GROUPING_STRATEGY,
        "raw_adls_path": RAW_ADLS_PATH,
        "step_start_ts": delta_load_start_ts,
        "step_end_ts": delta_load_end_ts,
    },
)

# COMMAND ----------

if not spark.catalog.functionExists("thales_protect_bulk_by_object_and_column"):
    spark.udf.registerJavaFunction(
        "thales_protect_bulk_by_object_and_column",
        "ThalesCrdpProtectBulkByObjectAndColumnUdf",
        "array<string>",
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
        f"thales_protect_bulk_by_object_and_column(address_array, 'char', '{PROTECTED_ARRAY_OBJECT_NAME}', 'address')"
    ).alias("address_array"),
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column(email_array, 'char', '{PROTECTED_ARRAY_OBJECT_NAME}', 'email')"
    ).alias("email_array"),
    "dob_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column(creditcard_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'creditcard')"
    ).alias("creditcard_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column(creditcardcode_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'creditcardcode')"
    ).alias("creditcardcode_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column(ssn_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'ssn')"
    ).alias("ssn_array"),
)

protected_df = protected_grouped_df.select(
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
    protected_df.repartition(TARGET_PARTITIONS).write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

(
    protected_grouped_df.select(
        F.col("group_id").cast("bigint").alias("batch_id"),
        "custid_array",
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
    ).write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(ARRAY_TARGET_TABLE)
)

protect_end = time.time()
protect_end_ts = datetime.now(timezone.utc)

target_count = spark.table(TARGET_TABLE).count()
print(f"FINAL_PROTECT_ROW_COUNT={target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "Protected target row count did not match the expected source row count. "
        f"Expected: {ROW_COUNT}, Actual: {target_count}"
    )

print("THALES_PIPELINE_BULK_LOAD_TEST_FINISHED")

append_perf_metrics(
    run_name=RUN_NAME,
    step_name=PROTECT_STEP_NAME,
    row_count=ROW_COUNT,
    duration_seconds=protect_end - protect_start,
    extra_metrics={
        "raw_file_partitions": RAW_FILE_PARTITIONS,
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
        "grouping_strategy": GROUPING_STRATEGY,
        "raw_adls_path": RAW_ADLS_PATH,
        "step_start_ts": protect_start_ts,
        "step_end_ts": protect_end_ts,
    },
)

# COMMAND ----------

display(spark.createDataFrame([(ROW_COUNT,)], ["source_count"]))
display(spark.createDataFrame([(target_count,)], ["protected_count"]))
display(spark.sql(f"SELECT * FROM {METRICS_TABLE} ORDER BY metric_ts_utc DESC LIMIT 20"))

create_perf_summary_view(SUMMARY_VIEW)
create_perf_compact_view(COMPACT_SUMMARY_VIEW, SUMMARY_VIEW)
display(spark.sql(build_perf_comparison_query(SUMMARY_VIEW, RUN_NAME)))
