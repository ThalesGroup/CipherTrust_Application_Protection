# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Scalar Object-Aware Benchmark
# MAGIC
# MAGIC This notebook isolates the internal scalar/object-aware protect-step
# MAGIC performance by:
# MAGIC
# MAGIC - generating synthetic plaintext data directly into Delta
# MAGIC - skipping raw CSV creation in ADLS Gen2
# MAGIC - running `internal_scalar_object_aware_load.py` against that table
# MAGIC
# MAGIC Use this when you want to measure:
# MAGIC
# MAGIC - Spark partitioning on the scalar/object-aware path
# MAGIC - Java UDF overhead on the scalar/object-aware path
# MAGIC - CRDP protect throughput without grouped bulk-array orchestration
# MAGIC
# MAGIC This is the best scalar benchmark to compare against the bulk-array
# MAGIC benchmark notebooks.

# COMMAND ----------

import time
from datetime import datetime, timezone
from pyspark.sql import functions as F

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 1_000_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_benchmark"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_benchmark"
PROTECTED_OBJECT_NAME = "my_catalog.my_schema.plaintext_protected_internal"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_internal_udf_benchmark"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
HIGH_THROUGHPUT_NOTEBOOK_PATH = "./internal_scalar_object_aware_load"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
BENCHMARK_MODE = True
LOAD_PATTERN = "scalar_object_aware"
EXPECTED_ROW_COUNT = ROW_COUNT

# COMMAND ----------

# MAGIC %run ../utils/perf_metrics_helpers

# COMMAND ----------

print("Row count:", ROW_COUNT)
print("Generate partitions:", GENERATE_PARTITIONS)
print("Protect target partitions:", TARGET_PARTITIONS)
print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
CONFIG_BATCH_SIZE = load_config_batch_size_from_properties()

print("Benchmark mode:", BENCHMARK_MODE)
print("Load pattern:", LOAD_PATTERN)
print("Configured BATCH_SIZE:", CONFIG_BATCH_SIZE)
print("Metrics helpers notebook path:", METRICS_HELPERS_NOTEBOOK_PATH)
print("High-throughput notebook path:", HIGH_THROUGHPUT_NOTEBOOK_PATH)

# COMMAND ----------

generate_start = time.time()
generate_start_ts = datetime.now(timezone.utc)

ids = spark.range(1, ROW_COUNT + 1).repartition(GENERATE_PARTITIONS)

benchmark_df = ids.select(
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
    benchmark_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SOURCE_TABLE)
)

generate_end = time.time()
generate_end_ts = datetime.now(timezone.utc)
print(f"Generated and wrote source Delta table in {generate_end - generate_start:.2f} seconds.")

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
        "benchmark_mode": BENCHMARK_MODE,
        "step_start_ts": generate_start_ts,
        "step_end_ts": generate_end_ts,
    },
)

# COMMAND ----------

# Reuse the high-throughput notebook in the same session with notebook-scoped overrides.
protect_start = time.time()
protect_start_ts = datetime.now(timezone.utc)

# COMMAND ----------

# MAGIC %run ./internal_scalar_object_aware_load

# COMMAND ----------

if not globals().get("HIGH_THROUGHPUT_LOAD_COMPLETED", False):
    raise ValueError(
        "High-throughput protect notebook did not finish cleanly. "
        "Do not trust the protect timing or target table contents from this run. "
        f"Notebook path used: {HIGH_THROUGHPUT_NOTEBOOK_PATH}. "
        f"Expected target table: {TARGET_TABLE}"
    )

actual_target_count = globals().get("HIGH_THROUGHPUT_TARGET_COUNT", None)
if actual_target_count != ROW_COUNT:
    raise ValueError(
        "High-throughput protect notebook completed with an unexpected target row count. "
        f"Expected: {ROW_COUNT}, Actual: {actual_target_count}"
    )

protect_end = time.time()
protect_end_ts = datetime.now(timezone.utc)
print(f"Protect step completed in {protect_end - protect_start:.2f} seconds.")
print(f"FINAL_PROTECT_ROW_COUNT={actual_target_count}")
print("THALES_BENCHMARK_FINISHED")

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="protect_internal_table",
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
        "benchmark_mode": BENCHMARK_MODE,
        "step_start_ts": protect_start_ts,
        "step_end_ts": protect_end_ts,
    },
)

# COMMAND ----------

display(spark.sql(f"SELECT COUNT(*) AS source_count FROM {SOURCE_TABLE}"))
display(spark.sql(f"SELECT COUNT(*) AS protected_count FROM {TARGET_TABLE}"))
display(spark.sql(f"SELECT * FROM {METRICS_TABLE} ORDER BY metric_ts_utc DESC LIMIT 20"))

create_perf_summary_view(SUMMARY_VIEW)
create_perf_compact_view(COMPACT_SUMMARY_VIEW, SUMMARY_VIEW)
display(spark.sql(f"""
SELECT
  metric_ts_utc,
  run_name,
  load_pattern,
  step_name,
  row_count,
  duration_seconds,
  rows_per_second,
  target_partitions,
  executor_count_estimate,
  benchmark_mode,
  hardware_metrics_available,
  cluster_vm_hint,
  avg_cpu_user_pct,
  avg_mem_used_pct
FROM {SUMMARY_VIEW}
WHERE run_name = '{RUN_NAME}'
ORDER BY metric_ts_utc DESC, step_name
"""))
display(spark.sql(f"""
SELECT
  metric_ts_utc,
  run_name,
  load_pattern,
  step_name,
  row_count,
  duration_seconds,
  rows_per_second,
  cluster_vm_hint,
  worker_count,
  executor_count_estimate,
  generate_partitions,
  target_partitions,
  config_batch_size,
  group_size,
  hardware_metrics_available
FROM {COMPACT_SUMMARY_VIEW}
WHERE run_name = '{RUN_NAME}'
ORDER BY metric_ts_utc DESC, step_name
"""))
display(spark.sql(build_perf_comparison_query(SUMMARY_VIEW, RUN_NAME)))

# COMMAND ----------

print(
    "Review Spark UI for task distribution and compare runs at different "
    "ROW_COUNT and TARGET_PARTITIONS settings."
)


