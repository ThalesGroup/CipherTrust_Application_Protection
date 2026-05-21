# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Bulk Array Benchmark
# MAGIC
# MAGIC This is the primary high-control benchmark for the internal bulk-array path.
# MAGIC It groups many values into arrays and calls
# MAGIC `thales_protect_bulk_by_column(...)`.
# MAGIC
# MAGIC This notebook provides the most control across the three key tuning layers:
# MAGIC
# MAGIC - Spark work shape
# MAGIC   - `ROW_COUNT`
# MAGIC   - `GENERATE_PARTITIONS`
# MAGIC   - `TARGET_PARTITIONS`
# MAGIC - Databricks grouping shape
# MAGIC   - `GROUP_SIZE_OVERRIDE`
# MAGIC   - `GROUP_COUNT_OVERRIDE`
# MAGIC   - `GROUP_SIZE_MULTIPLIER`
# MAGIC - CRDP chunking behavior
# MAGIC   - indirect control through grouped-call size
# MAGIC   - visibility into configured `BATCH_SIZE`
# MAGIC
# MAGIC Use this notebook when you want to answer:
# MAGIC
# MAGIC - what bulk-array shape gives the best throughput?
# MAGIC - does the protect step scale if we create more grouped bulk UDF rows?
# MAGIC - are we limited by `BATCH_SIZE`, by Spark task shape, or by CRDP latency?
# MAGIC
# MAGIC Operator notes:
# MAGIC
# MAGIC - `BATCH_SIZE` is still read from `udfConfig.properties`
# MAGIC - `GROUP_SIZE_OVERRIDE` forces a specific grouped-call size
# MAGIC - `GROUP_COUNT_OVERRIDE` forces an approximate grouped UDF row count
# MAGIC - if both are set, `GROUP_SIZE_OVERRIDE` wins

# COMMAND ----------

import math
import time
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import functions as F

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 350_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)

GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_bulk_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_bulk_parallelism_diag"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_internal_bulk_udf_parallelism_diagnostic"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
#CLUSTER_VM_HINT = "Standard_D8as_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
LOAD_PATTERN = "bulk_array_parallelism_diagnostic"

# COMMAND ----------

# MAGIC %run ../utils/perf_metrics_helpers

# COMMAND ----------

CONFIG_PATH = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)


def load_batch_size_from_properties(config_path):
    if not config_path:
        return 1000

    path = Path(config_path)
    if not path.exists():
        return 1000

    batch_size = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "BATCH_SIZE":
            batch_size = int(value.strip())
            break
    return batch_size if batch_size and batch_size > 0 else 1000


def resolve_group_size(row_count, config_batch_size, group_size_override, group_count_override, group_size_multiplier):
    if group_size_override:
        return max(int(group_size_override), 1), "group_size_override"

    if group_count_override:
        return max(int(math.ceil(float(row_count) / float(group_count_override))), 1), "group_count_override"

    return max(int(config_batch_size * group_size_multiplier), 1), "batch_size_multiplier"


CONFIG_BATCH_SIZE = load_batch_size_from_properties(CONFIG_PATH)
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
print("Generate partitions:", GENERATE_PARTITIONS)
print("Target partitions:", TARGET_PARTITIONS)
print("Configured BATCH_SIZE:", CONFIG_BATCH_SIZE)
print("Group size override:", GROUP_SIZE_OVERRIDE)
print("Group count override:", GROUP_COUNT_OVERRIDE)
print("Group size multiplier:", GROUP_SIZE_MULTIPLIER)
print("Resolved grouping strategy:", GROUPING_STRATEGY)
print("Resolved group size:", GROUP_SIZE)
print("Estimated grouped UDF rows:", ESTIMATED_GROUP_COUNT)
print("Load pattern:", LOAD_PATTERN)
print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Metrics helpers notebook path:", METRICS_HELPERS_NOTEBOOK_PATH)

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
print(f"Generated and wrote diagnostic source Delta table in {generate_end - generate_start:.2f} seconds.")

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
        "grouping_strategy": GROUPING_STRATEGY,
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

if not spark.catalog.functionExists("thales_protect_bulk_by_column"):
    spark.udf.registerJavaFunction(
        "thales_protect_bulk_by_column",
        "ThalesCrdpProtectBulkByColumnUdf",
        "array<string>",
    )
    print("Registered Java UDF: thales_protect_bulk_by_column -> ThalesCrdpProtectBulkByColumnUdf")

# COMMAND ----------

bulk_start = time.time()
bulk_start_ts = datetime.now(timezone.utc)

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
    F.expr("thales_protect_bulk_by_column(address_array, 'char', 'address')").alias("address_array"),
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    F.expr("thales_protect_bulk_by_column(email_array, 'char', 'email')").alias("email_array"),
    "dob_array",
    F.expr("thales_protect_bulk_by_column(creditcard_array, 'nbr', 'creditcard')").alias("creditcard_array"),
    F.expr("thales_protect_bulk_by_column(creditcardcode_array, 'nbr', 'creditcardcode')").alias("creditcardcode_array"),
    F.expr("thales_protect_bulk_by_column(ssn_array, 'nbr', 'ssn')").alias("ssn_array"),
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

bulk_end = time.time()
bulk_end_ts = datetime.now(timezone.utc)
print(f"Bulk parallelism diagnostic completed in {bulk_end - bulk_start:.2f} seconds.")

target_count = spark.table(TARGET_TABLE).count()
print(f"Diagnostic protected target row count: {target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "Diagnostic target row count did not match the expected source row count. "
        f"Expected: {ROW_COUNT}, Actual: {target_count}"
    )

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="protect_internal_table_bulk",
    row_count=ROW_COUNT,
    duration_seconds=bulk_end - bulk_start,
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
        "grouping_strategy": GROUPING_STRATEGY,
        "step_start_ts": bulk_start_ts,
        "step_end_ts": bulk_end_ts,
    },
)

# COMMAND ----------

display(spark.sql(f"SELECT COUNT(*) AS source_count FROM {SOURCE_TABLE}"))
display(spark.sql(f"SELECT COUNT(*) AS protected_count FROM {TARGET_TABLE}"))
display(spark.sql(f"SELECT * FROM {METRICS_TABLE} ORDER BY metric_ts_utc DESC LIMIT 20"))

create_perf_summary_view(SUMMARY_VIEW)
create_perf_compact_view(COMPACT_SUMMARY_VIEW, SUMMARY_VIEW)
display(
    spark.sql(
        f"""
        SELECT
          metric_ts_utc,
          run_name,
          load_pattern,
          step_name,
          row_count,
          duration_seconds,
          rows_per_second,
          target_partitions,
          generate_partitions,
          config_batch_size,
          group_size,
          group_size_multiplier,
          benchmark_mode,
          worker_count,
          executor_count_estimate
        FROM {COMPACT_SUMMARY_VIEW}
        WHERE run_name = '{RUN_NAME}'
        ORDER BY metric_ts_utc DESC, step_name
        """
    )
)

print("THALES_BULK_PARALLELISM_DIAGNOSTIC_FINISHED")

display(spark.sql(f"SELECT * FROM my_catalog.my_schema.thales_perf_test_metrics where step_name = 'protect_internal_table_bulk' and row_count = 350000 ORDER BY duration_seconds LIMIT 20"))


