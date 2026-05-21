# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Scalar Object-Aware Load
# MAGIC
# MAGIC This notebook shows the simplest production-style internal load pattern for
# MAGIC protecting a plaintext table with the scalar/object-aware Java UDFs on a
# MAGIC Databricks compute cluster.
# MAGIC
# MAGIC Architectural note:
# MAGIC - this notebook is the distributed protect/load step
# MAGIC - it is intentionally simpler than the bulk-array benchmark notebooks
# MAGIC - it is not the bronze or silver cleanse layer in a medallion flow
# MAGIC - in a medallion design it is usually closest to the secure-dimension or
# MAGIC   protected-table build step after source data has already been standardized
# MAGIC
# MAGIC Recommended flow:
# MAGIC - run `compute_cluster_udf_smoke_test.py` first to register the Java UDFs
# MAGIC - point this notebook at the customer plaintext table
# MAGIC - choose a reasonable repartition count
# MAGIC - write the protected table using distributed executor-side UDF execution
# MAGIC
# MAGIC Why this is the default pattern:
# MAGIC - simpler than bulk-array protect orchestration
# MAGIC - naturally parallelized by Spark across executors
# MAGIC - keeps the SQL and operational model easy for customers to follow
# MAGIC - useful when the goal is an operational example, not maximum tuning control
# MAGIC
# MAGIC Repartition guidance:
# MAGIC - start with `spark.sparkContext.defaultParallelism`
# MAGIC - increase it if input files are very large and executors are underutilized
# MAGIC - decrease it if tasks are tiny and scheduling overhead dominates
# MAGIC - for numeric values, keep protected columns as `STRING` in the protected table

# COMMAND ----------

from datetime import datetime, timezone

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = globals().get("CATALOG", "my_catalog")
SCHEMA = globals().get("SCHEMA", "my_schema")
SOURCE_TABLE = globals().get("SOURCE_TABLE", f"{CATALOG}.{SCHEMA}.plaintext_plaintext")
TARGET_TABLE = globals().get("TARGET_TABLE", f"{CATALOG}.{SCHEMA}.plaintext_protected_internal")
PROTECTED_OBJECT_NAME = globals().get("PROTECTED_OBJECT_NAME", TARGET_TABLE)
BENCHMARK_MODE = globals().get("BENCHMARK_MODE", False)
EXPECTED_ROW_COUNT = globals().get("EXPECTED_ROW_COUNT", None)

HIGH_THROUGHPUT_LOAD_COMPLETED = False
HIGH_THROUGHPUT_TARGET_COUNT = None

# Use a modest partitions-per-core multiplier for UDF-heavy work.
TARGET_PARTITIONS = globals().get(
    "TARGET_PARTITIONS",
    max(spark.sparkContext.defaultParallelism * 2, 16),
)

# COMMAND ----------

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


def progress(message):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"THALES_PROGRESS [{ts}]: {message}")


external_protect_schema = T.StructType(
    [
        T.StructField("protected_value", T.StringType(), True),
        T.StructField("external_header", T.StringType(), True),
    ]
)

ensure_java_udf_registered(
    "thales_protect_by_object_and_column",
    "ThalesCrdpProtectByObjectAndColumnUdf",
    T.StringType(),
)
ensure_java_udf_registered(
    "thales_protect_by_object_and_column_with_external_header",
    "ThalesCrdpProtectByObjectAndColumnWithExternalHeaderUdf",
    external_protect_schema,
)
ensure_java_udf_registered(
    "thales_reveal_by_object_and_column_with_user",
    "ThalesCrdpRevealByObjectAndColumnWithUserUdf",
    T.StringType(),
)
ensure_java_udf_registered(
    "thales_reveal_by_object_and_column_with_external_header_and_user",
    "ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf",
    T.StringType(),
)
ensure_java_udf_registered(
    "thales_reveal_bulk_by_object_and_column_with_user",
    "ThalesCrdpRevealBulkByObjectAndColumnWithUserUdf",
    T.ArrayType(T.StringType()),
)
ensure_java_udf_registered(
    "thales_reveal_bulk_by_object_and_column_with_external_header_and_user",
    "ThalesCrdpRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf",
    T.ArrayType(T.StringType()),
)

print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Target partitions:", TARGET_PARTITIONS)
print("Benchmark mode:", BENCHMARK_MODE)
progress("starting source table read")

# COMMAND ----------

source_df = spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS)
progress("source table read complete; repartition applied")

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
    # Cast-back pattern:
    # store protected numeric values as STRING in the protected table.
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
progress("protected DataFrame logical plan created")

# COMMAND ----------

progress("starting protected table write")
(
    protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

print(f"Wrote protected internal table: {TARGET_TABLE}")
progress("protected table write complete")

# COMMAND ----------

progress("starting protected target row count validation")
HIGH_THROUGHPUT_TARGET_COUNT = spark.table(TARGET_TABLE).count()
print(f"Protected target row count: {HIGH_THROUGHPUT_TARGET_COUNT}")
progress("protected target row count validation complete")

if EXPECTED_ROW_COUNT is not None and HIGH_THROUGHPUT_TARGET_COUNT != EXPECTED_ROW_COUNT:
    raise ValueError(
        "Protected target row count did not match the expected source row count. "
        f"Expected: {EXPECTED_ROW_COUNT}, Actual: {HIGH_THROUGHPUT_TARGET_COUNT}"
    )

HIGH_THROUGHPUT_LOAD_COMPLETED = True

if not BENCHMARK_MODE:
    spark.sql(f"SELECT COUNT(*) AS row_count FROM {TARGET_TABLE}").show()

if not BENCHMARK_MODE:
    spark.sql(f"SELECT * FROM {TARGET_TABLE} ORDER BY custid LIMIT 10").show(truncate=False)

# COMMAND ----------

if BENCHMARK_MODE:
    print(
        "Internal high-throughput load completed in benchmark mode. "
        "Sample row display was skipped."
    )
else:
    print(
        "Internal high-throughput load completed. Review the Spark UI to confirm "
        "partition count, executor task distribution, and end-to-end runtime."
    )

print("THALES_HIGH_THROUGHPUT_LOAD_FINISHED")

