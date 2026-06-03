# Databricks notebook source
# MAGIC %md
# MAGIC # None Scalar Object-Aware Benchmark
# MAGIC
# MAGIC This notebook isolates the none/no-version scalar/object-aware protect-step
# MAGIC performance by generating synthetic plaintext data directly into Delta and
# MAGIC protecting the generated Delta table directly in this notebook.

# COMMAND ----------

import time
from datetime import datetime, timezone

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

ROW_COUNT = 1_000_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_none_benchmark"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_benchmark"
PROTECTED_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"
ROW_REVEAL_OBJECT_NAME = PROTECTED_OBJECT_NAME
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_none_udf_benchmark"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
BENCHMARK_MODE = True
LOAD_PATTERN = "scalar_object_aware_none"
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

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )


def ensure_java_udf_registered(function_name, class_name, return_type):
    if spark.catalog.functionExists(function_name):
        return
    spark.udf.registerJavaFunction(function_name, class_name, return_type)
    print(f"Registered Java UDF: {function_name} -> {class_name}")


ensure_java_udf_registered(
    "thales_protect_by_object_and_column",
    "ThalesCrdpProtectByObjectAndColumnUdf",
    T.StringType(),
)
ensure_java_udf_registered(
    "thales_reveal_by_object_and_column_with_user",
    "ThalesCrdpRevealByObjectAndColumnWithUserUdf",
    T.StringType(),
)

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

protect_start = time.time()
protect_start_ts = datetime.now(timezone.utc)

source_df = spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS)

protected_df = source_df.select(
    "custid",
    "name",
    F.expr(
        f"thales_protect_by_object_and_column(CAST(address AS STRING), 'char', '{PROTECTED_OBJECT_NAME}', 'address')"
    ).alias("address"),
    "city",
    "state",
    "zip",
    "phone",
    F.expr(
        f"thales_protect_by_object_and_column(CAST(email AS STRING), 'char', '{PROTECTED_OBJECT_NAME}', 'email')"
    ).alias("email"),
    "dob",
    F.expr(
        f"thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', '{PROTECTED_OBJECT_NAME}', 'creditcard')"
    ).alias("creditcard"),
    F.expr(
        f"thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', '{PROTECTED_OBJECT_NAME}', 'creditcardcode')"
    ).alias("creditcardcode"),
    F.expr(
        f"thales_protect_by_object_and_column(CAST(ssn AS STRING), 'nbr', '{PROTECTED_OBJECT_NAME}', 'ssn')"
    ).alias("ssn"),
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
print(f"Protect step completed in {protect_end - protect_start:.2f} seconds.")
print("FINAL_PROTECT_ROW_COUNT=validation_skipped")
print("THALES_BENCHMARK_FINISHED")

append_perf_metrics(
    run_name=RUN_NAME,
    step_name="protect_none_table",
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
display(spark.sql(f"SELECT * FROM {TARGET_TABLE} LIMIT 5"))

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW v_none_scalar_benchmark_revealed AS
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

display(spark.sql("SELECT * FROM v_none_scalar_benchmark_revealed LIMIT 5"))
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
