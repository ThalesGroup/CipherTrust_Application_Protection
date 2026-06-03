# Databricks notebook source
# MAGIC %md
# MAGIC # None Scalar Object-Aware Load
# MAGIC
# MAGIC This notebook shows the simplest production-style none/no-version load
# MAGIC pattern for protecting a plaintext table with the scalar/object-aware Java
# MAGIC UDFs on a Databricks compute cluster.

# COMMAND ----------

from datetime import datetime, timezone

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = globals().get("CATALOG", "my_catalog")
SCHEMA = globals().get("SCHEMA", "my_schema")
SOURCE_TABLE = globals().get("SOURCE_TABLE", f"{CATALOG}.{SCHEMA}.plaintext_plaintext")
TARGET_TABLE = globals().get("TARGET_TABLE", f"{CATALOG}.{SCHEMA}.plaintext_protected_none")
PROTECTED_OBJECT_NAME = globals().get("PROTECTED_OBJECT_NAME", TARGET_TABLE)
BENCHMARK_MODE = globals().get("BENCHMARK_MODE", False)
EXPECTED_ROW_COUNT = globals().get("EXPECTED_ROW_COUNT", None)
LOAD_NOTEBOOK_DEFINE_ONLY = globals().get("LOAD_NOTEBOOK_DEFINE_ONLY", False)

HIGH_THROUGHPUT_LOAD_COMPLETED = False
HIGH_THROUGHPUT_TARGET_COUNT = None

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

print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Target partitions:", TARGET_PARTITIONS)
print("Benchmark mode:", BENCHMARK_MODE)

# COMMAND ----------


def build_none_protected_df(source_df, protected_object_name):
    return source_df.select(
        "custid",
        "name",
        F.expr(
            f"thales_protect_by_object_and_column(CAST(address AS STRING), 'char', '{protected_object_name}', 'address')"
        ).alias("address"),
        "city",
        "state",
        "zip",
        "phone",
        F.expr(
            f"thales_protect_by_object_and_column(CAST(email AS STRING), 'char', '{protected_object_name}', 'email')"
        ).alias("email"),
        "dob",
        F.expr(
            f"thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', '{protected_object_name}', 'creditcard')"
        ).alias("creditcard"),
        F.expr(
            f"thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', '{protected_object_name}', 'creditcardcode')"
        ).alias("creditcardcode"),
        F.expr(
            f"thales_protect_by_object_and_column(CAST(ssn AS STRING), 'nbr', '{protected_object_name}', 'ssn')"
        ).alias("ssn"),
    )


def run_none_scalar_object_aware_load(
    source_table=None,
    target_table=None,
    protected_object_name=None,
    target_partitions=None,
    benchmark_mode=None,
    expected_row_count=None,
    validate_target_count=True,
    show_samples=None,
):
    global HIGH_THROUGHPUT_LOAD_COMPLETED
    global HIGH_THROUGHPUT_TARGET_COUNT

    resolved_source_table = source_table or SOURCE_TABLE
    resolved_target_table = target_table or TARGET_TABLE
    resolved_object_name = protected_object_name or PROTECTED_OBJECT_NAME
    resolved_target_partitions = target_partitions or TARGET_PARTITIONS
    resolved_benchmark_mode = BENCHMARK_MODE if benchmark_mode is None else benchmark_mode
    resolved_expected_row_count = EXPECTED_ROW_COUNT if expected_row_count is None else expected_row_count
    resolved_show_samples = (not resolved_benchmark_mode) if show_samples is None else show_samples

    progress("starting source table read")
    source_df = spark.table(resolved_source_table).repartition(resolved_target_partitions)
    progress("source table read complete; repartition applied")

    protected_df = build_none_protected_df(source_df, resolved_object_name)
    progress("protected DataFrame logical plan created")

    progress("starting protected table write")
    (
        protected_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(resolved_target_table)
    )

    print(f"Wrote protected none table: {resolved_target_table}")
    progress("protected table write complete")

    actual_target_count = None
    if validate_target_count:
        progress("starting protected target row count validation")
        actual_target_count = spark.table(resolved_target_table).count()
        print(f"Protected target row count: {actual_target_count}")
        progress("protected target row count validation complete")

        if (
            resolved_expected_row_count is not None
            and actual_target_count != resolved_expected_row_count
        ):
            raise ValueError(
                "Protected target row count did not match the expected source row count. "
                f"Expected: {resolved_expected_row_count}, Actual: {actual_target_count}"
            )

    HIGH_THROUGHPUT_TARGET_COUNT = actual_target_count
    HIGH_THROUGHPUT_LOAD_COMPLETED = True

    if resolved_show_samples:
        spark.sql(f"SELECT COUNT(*) AS row_count FROM {resolved_target_table}").show()
        spark.sql(f"SELECT * FROM {resolved_target_table} ORDER BY custid LIMIT 10").show(truncate=False)

    return {
        "source_table": resolved_source_table,
        "target_table": resolved_target_table,
        "target_count": actual_target_count,
        "benchmark_mode": resolved_benchmark_mode,
        "validate_target_count": validate_target_count,
    }


if not LOAD_NOTEBOOK_DEFINE_ONLY:
    run_result = run_none_scalar_object_aware_load()

    if run_result["benchmark_mode"]:
        print(
            "None high-throughput load completed in benchmark mode. "
            "Sample row display was skipped."
        )
    else:
        print(
            "None high-throughput load completed. Review the Spark UI to confirm "
            "partition count, executor task distribution, and end-to-end runtime."
        )

    print("THALES_HIGH_THROUGHPUT_LOAD_FINISHED")
