# Databricks notebook source
# MAGIC %md
# MAGIC # Java UDF Keep-Alive Smoke Test
# MAGIC
# MAGIC Purpose:
# MAGIC - validate the Java jar / UDF path on a compute cluster
# MAGIC - observe repeated-call timing behavior for the Java CRDP client
# MAGIC - provide a simple signal that executor-side JVM reuse and HTTP connection reuse are working
# MAGIC
# MAGIC Why this matters:
# MAGIC - `JavaCrdpService` is implemented as a singleton per executor JVM
# MAGIC - that singleton holds a single `HttpClient`
# MAGIC - repeated runs in the same executor should avoid recreating the Java client on every row
# MAGIC - if keep-alive and warm JVM reuse are helping, the later runs should usually be as fast as or faster than the first real run
# MAGIC
# MAGIC This is not a packet-level TCP proof. It is a practical compute-cluster
# MAGIC validation notebook for repeated Java UDF use under realistic Spark execution.

# COMMAND ----------

import time
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
OBJECT_NAME = SOURCE_TABLE

TARGET_PARTITIONS = 8
MULTIPLIER = 250
RUN_COUNT = 4

# Change to "scalar" or "bulk" if you only want one path.
TEST_MODE = "both"

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
executor_config_path = spark.conf.get("spark.executorEnv.UDF_CONFIG_VOLUME_PATH", None)

print("Driver config path:", config_path)
print("Executor config path:", executor_config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

if not Path(config_path).exists():
    raise ValueError(f"Config file not found at {config_path}")

# COMMAND ----------

spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column",
    "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_protect_bulk_by_object_and_column",
    "com.thales.databricks.integration.udf.ThalesProtectBulkByObjectAndColumnUdf",
    T.ArrayType(T.StringType()),
)

print("Registered Java keep-alive test UDFs.")

# COMMAND ----------

base_df = spark.table(SOURCE_TABLE).select("custid", "email")

demo_df = (
    base_df.crossJoin(spark.range(0, MULTIPLIER).toDF("replica_id"))
    .repartition(TARGET_PARTITIONS)
)

print("Demo row count:", demo_df.count())
print("Demo partitions:", demo_df.rdd.getNumPartitions())

# COMMAND ----------

bulk_group_size = max(int(demo_df.count() / TARGET_PARTITIONS), 1)
bulk_source_df = (
    demo_df.orderBy("custid", "replica_id")
    .withColumn(
        "group_id",
        F.floor((F.monotonically_increasing_id()) / F.lit(bulk_group_size)).cast("long"),
    )
    .groupBy("group_id")
    .agg(F.collect_list("email").alias("email_batch"))
    .orderBy("group_id")
)

print("Bulk group row count:", bulk_source_df.count())
display(bulk_source_df.limit(5))

# COMMAND ----------


def run_scalar_once(run_index: int):
    start = time.perf_counter()
    result_df = demo_df.selectExpr(
        "custid",
        "replica_id",
        """thales_protect_by_object_and_column(
            email,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal',
            'email'
        ) as email_token"""
    )
    row_count = result_df.count()
    duration_seconds = time.perf_counter() - start
    return {
        "run_index": run_index,
        "mode": "scalar",
        "row_count": row_count,
        "duration_seconds": duration_seconds,
        "rows_per_second": round(row_count / duration_seconds, 2) if duration_seconds > 0 else None,
    }


def run_bulk_once(run_index: int):
    start = time.perf_counter()
    result_df = bulk_source_df.selectExpr(
        "group_id",
        """thales_protect_bulk_by_object_and_column(
            email_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal_arrays',
            'email'
        ) as email_token_batch"""
    )
    batch_row_count = result_df.count()
    duration_seconds = time.perf_counter() - start
    return {
        "run_index": run_index,
        "mode": "bulk",
        "row_count": batch_row_count,
        "duration_seconds": duration_seconds,
        "rows_per_second": round(batch_row_count / duration_seconds, 2) if duration_seconds > 0 else None,
    }


results = []

for run_index in range(1, RUN_COUNT + 1):
    if TEST_MODE in ("scalar", "both"):
        scalar_metrics = run_scalar_once(run_index)
        print("Scalar run:", scalar_metrics)
        results.append(scalar_metrics)

    if TEST_MODE in ("bulk", "both"):
        bulk_metrics = run_bulk_once(run_index)
        print("Bulk run:", bulk_metrics)
        results.append(bulk_metrics)

# COMMAND ----------

results_df = spark.createDataFrame(results)
display(results_df.orderBy("mode", "run_index"))

# COMMAND ----------

summary_df = (
    results_df.groupBy("mode")
    .agg(
        F.min("duration_seconds").alias("min_duration_seconds"),
        F.max("duration_seconds").alias("max_duration_seconds"),
        F.avg("duration_seconds").alias("avg_duration_seconds"),
        F.min("rows_per_second").alias("min_rows_per_second"),
        F.max("rows_per_second").alias("max_rows_per_second"),
    )
    .orderBy("mode")
)

display(summary_df)

# COMMAND ----------

print(
    f"""
How to interpret this notebook:

1. The first real run includes the most cold-start cost:
   - Spark planning
   - executor-side class loading
   - Java singleton initialization
   - initial HTTP/TLS session setup

2. Later runs are the interesting part.
   If the Java UDF client is being reused effectively, repeated runs should
   usually stay flat or improve.

3. This notebook is a practical warm-run signal, not a packet capture.
   It helps confirm that the Java execution model is not recreating the CRDP
   client for every row.

Current settings:
- TEST_MODE = {TEST_MODE}
- TARGET_PARTITIONS = {TARGET_PARTITIONS}
- MULTIPLIER = {MULTIPLIER}
- RUN_COUNT = {RUN_COUNT}
- bulk_group_size = {bulk_group_size}
"""
)
