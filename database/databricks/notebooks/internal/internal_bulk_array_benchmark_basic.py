# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Bulk Array Benchmark (Basic)
# MAGIC
# MAGIC This notebook benchmarks the internal bulk-array path where many values are
# MAGIC grouped into arrays and sent through `thales_protect_bulk_by_column(...)`.
# MAGIC
# MAGIC It is retained as the simpler predecessor to
# MAGIC `internal_bulk_array_benchmark.py`.
# MAGIC
# MAGIC What sets this notebook apart:
# MAGIC
# MAGIC - it keeps the grouped bulk path simple
# MAGIC - it uses `GROUP_SIZE_OVERRIDE` and `GROUP_SIZE_MULTIPLIER`
# MAGIC - it does not expose `GROUP_COUNT_OVERRIDE`
# MAGIC
# MAGIC Use this when you want to measure:
# MAGIC
# MAGIC - whether CRDP `protectbulk` helps more than the scalar object-aware path
# MAGIC - whether `BATCH_SIZE` materially affects throughput
# MAGIC - whether simpler group-size tuning is enough for the experiment
# MAGIC
# MAGIC Operator notes:
# MAGIC
# MAGIC - `BATCH_SIZE` is read from `udfConfig.properties`
# MAGIC - by default, this notebook uses `GROUP_SIZE ~= BATCH_SIZE`
# MAGIC - for grouped-row fan-out experiments, prefer `internal_bulk_array_benchmark.py`
# MAGIC
# MAGIC Recommended first comparisons:
# MAGIC
# MAGIC - keep `GROUP_SIZE_MULTIPLIER = 1.0` and compare different `BATCH_SIZE` values
# MAGIC - then compare:
# MAGIC   - `GROUP_SIZE_MULTIPLIER = 0.5`
# MAGIC   - `GROUP_SIZE_MULTIPLIER = 1.0`
# MAGIC   - `GROUP_SIZE_MULTIPLIER = 2.0`
# MAGIC
# MAGIC Suggested first `BATCH_SIZE` values for testing:
# MAGIC
# MAGIC - `1000`
# MAGIC - `5000`
# MAGIC - `10000`
# MAGIC
# MAGIC Architectural note:
# MAGIC
# MAGIC - unlike the scalar benchmark notebook, this path gives each UDF call many
# MAGIC   values at once
# MAGIC - that means the Java bulk service and the `BATCH_SIZE` config can have a
# MAGIC   real performance impact here

# COMMAND ----------

import time
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import functions as F

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 100_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
GROUP_SIZE_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_bulk_benchmark"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_bulk_benchmark"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_internal_bulk_udf_benchmark"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
LOAD_PATTERN = "bulk_array"

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


CONFIG_BATCH_SIZE = load_batch_size_from_properties(CONFIG_PATH)
GROUP_SIZE = int(GROUP_SIZE_OVERRIDE) if GROUP_SIZE_OVERRIDE else int(CONFIG_BATCH_SIZE * GROUP_SIZE_MULTIPLIER)
GROUP_SIZE = max(GROUP_SIZE, 1)

# COMMAND ----------

print("Row count:", ROW_COUNT)
print("Generate partitions:", GENERATE_PARTITIONS)
print("Target partitions:", TARGET_PARTITIONS)
print("Configured BATCH_SIZE:", CONFIG_BATCH_SIZE)
print("Group size override:", GROUP_SIZE_OVERRIDE)
print("Group size multiplier:", GROUP_SIZE_MULTIPLIER)
print("Group size:", GROUP_SIZE)
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
print(f"Generated and wrote bulk benchmark source Delta table in {generate_end - generate_start:.2f} seconds.")

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
print(f"Bulk protect benchmark completed in {bulk_end - bulk_start:.2f} seconds.")

target_count = spark.table(TARGET_TABLE).count()
print(f"Bulk benchmark protected target row count: {target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "Bulk benchmark target row count did not match the expected source row count. "
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
display(spark.sql(f"""
SELECT
  metric_ts_utc,
  run_name,
  load_pattern,
  step_name,
  row_count,
  duration_seconds,
  rows_per_second,
  generate_partitions,
  target_partitions,
  config_batch_size,
  group_size,
  group_size_multiplier,
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
  group_size_multiplier,
  hardware_metrics_available
FROM {COMPACT_SUMMARY_VIEW}
WHERE run_name = '{RUN_NAME}'
ORDER BY metric_ts_utc DESC, step_name
"""))
display(spark.sql(build_perf_comparison_query(SUMMARY_VIEW, RUN_NAME)))

# COMMAND ----------

print("THALES_BULK_BENCHMARK_FINISHED")

