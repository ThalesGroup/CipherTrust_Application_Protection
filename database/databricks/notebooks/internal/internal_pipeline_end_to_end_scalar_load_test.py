# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Pipeline End-to-End Scalar Load Test
# MAGIC
# MAGIC This notebook is the end-to-end internal scalar pipeline example for a
# MAGIC customer-like environment.
# MAGIC
# MAGIC It does three things:
# MAGIC
# MAGIC - generates a large synthetic plaintext dataset in the same general shape as
# MAGIC   `plaintext_setup.sql`
# MAGIC - writes raw CSV files to ADLS Gen2
# MAGIC - loads those files into a Delta source table and then runs
# MAGIC   `internal_scalar_object_aware_load.py`
# MAGIC
# MAGIC Use this notebook when pipeline realism matters more than having all of the
# MAGIC fine-grained tuning controls from the bulk benchmark notebook.
# MAGIC
# MAGIC Important notes:
# MAGIC
# MAGIC - the original sample uses `custid SMALLINT`, which cannot hold 15 million
# MAGIC   unique values
# MAGIC - this load-test notebook widens `custid` to `BIGINT`
# MAGIC - for a low-cost first test, reduce `ROW_COUNT` to 1 million before trying
# MAGIC   15 million
# MAGIC - this is not the highest-control tuning notebook; it is the best internal
# MAGIC   end-to-end scalar example

# COMMAND ----------

import time
from datetime import datetime, timezone
from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 15_000_000
RAW_FILE_PARTITIONS = 32
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)

RAW_ADLS_PATH = "abfss://landing@mydatalake.dfs.core.windows.net/thales/load_test/plaintext_plaintext_raw/"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_load_test"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_load_test"
PROTECTED_OBJECT_NAME = "my_catalog.my_schema.plaintext_protected_internal"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_internal_pipeline_load_test"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
HIGH_THROUGHPUT_NOTEBOOK_PATH = "./internal_scalar_object_aware_load"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
BENCHMARK_MODE = True
LOAD_PATTERN = "pipeline_with_adls_scalar_object_aware"
EXPECTED_ROW_COUNT = ROW_COUNT
LOAD_NOTEBOOK_DEFINE_ONLY = True

# COMMAND ----------

# MAGIC %run ../utils/perf_metrics_helpers

# COMMAND ----------

print("Row count:", ROW_COUNT)
print("Raw file partitions:", RAW_FILE_PARTITIONS)
print("Protect target partitions:", TARGET_PARTITIONS)
print("Raw ADLS path:", RAW_ADLS_PATH)
print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
CONFIG_BATCH_SIZE = load_config_batch_size_from_properties()

print("Benchmark mode:", BENCHMARK_MODE)
print("Load pattern:", LOAD_PATTERN)
print("Configured BATCH_SIZE:", CONFIG_BATCH_SIZE)
print("Metrics helpers notebook path:", METRICS_HELPERS_NOTEBOOK_PATH)
print("High-throughput notebook path:", HIGH_THROUGHPUT_NOTEBOOK_PATH)

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
        "benchmark_mode": BENCHMARK_MODE,
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
        "benchmark_mode": BENCHMARK_MODE,
        "raw_adls_path": RAW_ADLS_PATH,
        "step_start_ts": delta_load_start_ts,
        "step_end_ts": delta_load_end_ts,
    },
)

# COMMAND ----------

# The throughput notebook now respects pre-defined SOURCE_TABLE, TARGET_TABLE,
# PROTECTED_OBJECT_NAME, and TARGET_PARTITIONS values from the current notebook context.

protect_start = time.time()
protect_start_ts = datetime.now(timezone.utc)

# COMMAND ----------

# MAGIC %run ./internal_scalar_object_aware_load

# COMMAND ----------

load_result = run_internal_scalar_object_aware_load(
    source_table=SOURCE_TABLE,
    target_table=TARGET_TABLE,
    protected_object_name=PROTECTED_OBJECT_NAME,
    target_partitions=TARGET_PARTITIONS,
    benchmark_mode=BENCHMARK_MODE,
    expected_row_count=EXPECTED_ROW_COUNT,
    validate_target_count=True,
    show_samples=False,
)

if not globals().get("HIGH_THROUGHPUT_LOAD_COMPLETED", False):
    raise ValueError(
        "High-throughput protect notebook did not finish cleanly. "
        "Do not trust the protect timing or target table contents from this run. "
        f"Notebook path used: {HIGH_THROUGHPUT_NOTEBOOK_PATH}. "
        f"Expected target table: {TARGET_TABLE}"
    )

actual_target_count = load_result.get("target_count", None)
if actual_target_count != ROW_COUNT:
    raise ValueError(
        "High-throughput protect notebook completed with an unexpected target row count. "
        f"Expected: {ROW_COUNT}, Actual: {actual_target_count}"
    )

protect_end = time.time()
protect_end_ts = datetime.now(timezone.utc)
print(f"FINAL_PROTECT_ROW_COUNT={actual_target_count}")
print("THALES_PIPELINE_LOAD_TEST_FINISHED")

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="protect_internal_table",
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
        "benchmark_mode": BENCHMARK_MODE,
        "raw_adls_path": RAW_ADLS_PATH,
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
  raw_file_partitions,
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
  raw_file_partitions,
  target_partitions,
  config_batch_size,
  group_size,
  hardware_metrics_available
FROM {COMPACT_SUMMARY_VIEW}
WHERE run_name = '{RUN_NAME}'
ORDER BY metric_ts_utc DESC, step_name
"""))
display(spark.sql(build_perf_comparison_query(SUMMARY_VIEW, RUN_NAME)))
