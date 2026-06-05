# Databricks notebook source
# MAGIC %md
# MAGIC # External Bulk Array Benchmark
# MAGIC
# MAGIC This is the primary high-control benchmark for the external/header-aware
# MAGIC bulk-array path.
# MAGIC
# MAGIC It generates synthetic plaintext data, groups many values into arrays,
# MAGIC and calls
# MAGIC `thales_protect_bulk_by_object_and_column_with_external_header(...)`.
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
# MAGIC The external bulk-protect UDF returns an array of structs with:
# MAGIC - `protected_value`
# MAGIC - `external_header`
# MAGIC
# MAGIC This notebook flattens those grouped results back into a standard
# MAGIC row-oriented external protected table shape so it can be used by the
# MAGIC existing reveal flows and benchmark comparisons.
# MAGIC
# MAGIC This notebook is the external bulk benchmark peer of:
# MAGIC - `internal_bulk_array_benchmark.py`
# MAGIC - `none_bulk_array_benchmark.py`

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

ROW_COUNT = 350_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 32)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 32)

GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_external_bulk_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_bulk_parallelism_diag"
PROTECTED_ARRAY_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_arrays"
ROW_REVEAL_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.thales_perf_test_metrics"
METRICS_CSV_PATH = None
RUN_NAME = "plaintext_external_bulk_udf_parallelism_diagnostic"
CLUSTER_VM_HINT = "Standard_D4ds_v5"
SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_summary"
COMPACT_SUMMARY_VIEW = f"{CATALOG}.{SCHEMA}.v_thales_perf_test_compact"
METRICS_HELPERS_NOTEBOOK_PATH = "../utils/perf_metrics_helpers"
LOAD_PATTERN = "external_bulk_array_parallelism_diagnostic"
PROTECT_STEP_NAME = "protect_external_table_bulk"


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


external_protect_schema = T.ArrayType(
    T.StructType(
        [
            T.StructField("protected_value", T.StringType(), True),
            T.StructField("external_header", T.StringType(), True),
        ]
    )
)

if not spark.catalog.functionExists("thales_protect_bulk_by_object_and_column_with_external_header"):
    spark.udf.registerJavaFunction(
        "thales_protect_bulk_by_object_and_column_with_external_header",
        "ThalesCrdpProtectBulkByObjectAndColumnWithExternalHeaderUdf",
        external_protect_schema,
    )
    print(
        "Registered Java UDF: "
        "thales_protect_bulk_by_object_and_column_with_external_header -> "
        "ThalesCrdpProtectBulkByObjectAndColumnWithExternalHeaderUdf"
    )

if not spark.catalog.functionExists("thales_reveal_by_object_and_column_with_external_header_and_user"):
    spark.udf.registerJavaFunction(
        "thales_reveal_by_object_and_column_with_external_header_and_user",
        "ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf",
        "string",
    )
    print(
        "Registered Java UDF: "
        "thales_reveal_by_object_and_column_with_external_header_and_user -> "
        "ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf"
    )

if not CONFIG_PATH:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

CONFIG_BATCH_SIZE, RAW_CONFIG_BATCH_SIZE, BATCH_SIZE_WARNING = load_batch_size_from_properties(CONFIG_PATH)
group_size, grouping_strategy = resolve_group_size(
    ROW_COUNT,
    CONFIG_BATCH_SIZE,
    GROUP_SIZE_OVERRIDE,
    GROUP_COUNT_OVERRIDE,
    GROUP_SIZE_MULTIPLIER,
)
estimated_group_count = int(math.ceil(float(ROW_COUNT) / float(group_size)))

print("Row count:", ROW_COUNT)
print("Generate partitions:", GENERATE_PARTITIONS)
print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Protected array object mapping:", PROTECTED_ARRAY_OBJECT_NAME)
print("Target partitions:", TARGET_PARTITIONS)
print("Raw BATCH_SIZE setting in config file:", RAW_CONFIG_BATCH_SIZE if RAW_CONFIG_BATCH_SIZE is not None else "<missing>")
print("Effective BATCH_SIZE used by notebook:", CONFIG_BATCH_SIZE)
if BATCH_SIZE_WARNING:
    print("WARNING:", BATCH_SIZE_WARNING)
print("Resolved group size:", group_size)
print("Grouping strategy:", grouping_strategy)
print("Estimated grouped UDF rows:", estimated_group_count)
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
        "group_size": group_size,
        "group_size_multiplier": GROUP_SIZE_MULTIPLIER,
        "benchmark_mode": True,
        "group_count_override": GROUP_COUNT_OVERRIDE,
        "estimated_group_count": estimated_group_count,
        "grouping_strategy": grouping_strategy,
        "step_start_ts": generate_start_ts,
        "step_end_ts": generate_end_ts,
    },
)

# COMMAND ----------

bulk_start = time.time()
bulk_start_ts = datetime.now(timezone.utc)

ordered_df = spark.table(SOURCE_TABLE).orderBy("custid")

grouped_df = (
    ordered_df.withColumn("group_id", F.floor((F.col("custid") - F.lit(1)) / F.lit(group_size)))
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
        f"thales_protect_bulk_by_object_and_column_with_external_header(address_array, 'char', '{PROTECTED_ARRAY_OBJECT_NAME}', 'address')"
    ).alias("address_struct_array"),
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column_with_external_header(email_array, 'char', '{PROTECTED_ARRAY_OBJECT_NAME}', 'email')"
    ).alias("email_struct_array"),
    "dob_array",
    F.expr(
        f"thales_protect_bulk_by_object_and_column_with_external_header(creditcard_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'creditcard')"
    ).alias("creditcard_struct_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column_with_external_header(creditcardcode_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'creditcardcode')"
    ).alias("creditcardcode_struct_array"),
    F.expr(
        f"thales_protect_bulk_by_object_and_column_with_external_header(ssn_array, 'nbr', '{PROTECTED_ARRAY_OBJECT_NAME}', 'ssn')"
    ).alias("ssn_struct_array"),
)

flattened_df = protected_grouped_df.select(
    F.posexplode("custid_array").alias("pos", "custid"),
    "name_array",
    "address_struct_array",
    "city_array",
    "state_array",
    "zip_array",
    "phone_array",
    "email_struct_array",
    "dob_array",
    "creditcard_struct_array",
    "creditcardcode_struct_array",
    "ssn_struct_array",
).select(
    F.col("custid").cast("bigint").alias("custid"),
    F.element_at("name_array", F.col("pos") + 1).alias("name"),
    F.element_at(
        F.transform("address_struct_array", lambda x: x["protected_value"]),
        F.col("pos") + 1,
    ).alias("address"),
    F.element_at(
        F.transform("address_struct_array", lambda x: x["external_header"]),
        F.col("pos") + 1,
    ).alias("address_header"),
    F.element_at("city_array", F.col("pos") + 1).alias("city"),
    F.element_at("state_array", F.col("pos") + 1).alias("state"),
    F.element_at("zip_array", F.col("pos") + 1).alias("zip"),
    F.element_at("phone_array", F.col("pos") + 1).alias("phone"),
    F.element_at(
        F.transform("email_struct_array", lambda x: x["protected_value"]),
        F.col("pos") + 1,
    ).alias("email"),
    F.element_at(
        F.transform("email_struct_array", lambda x: x["external_header"]),
        F.col("pos") + 1,
    ).alias("email_header"),
    F.element_at("dob_array", F.col("pos") + 1).alias("dob"),
    F.element_at(
        F.transform("creditcard_struct_array", lambda x: x["protected_value"]),
        F.col("pos") + 1,
    ).alias("creditcard"),
    F.element_at(
        F.transform("creditcard_struct_array", lambda x: x["external_header"]),
        F.col("pos") + 1,
    ).alias("creditcard_header"),
    F.element_at(
        F.transform("creditcardcode_struct_array", lambda x: x["protected_value"]),
        F.col("pos") + 1,
    ).alias("creditcardcode"),
    F.element_at(
        F.transform("creditcardcode_struct_array", lambda x: x["external_header"]),
        F.col("pos") + 1,
    ).alias("creditcardcode_header"),
    F.element_at(
        F.transform("ssn_struct_array", lambda x: x["protected_value"]),
        F.col("pos") + 1,
    ).alias("ssn"),
    F.element_at(
        F.transform("ssn_struct_array", lambda x: x["external_header"]),
        F.col("pos") + 1,
    ).alias("ssn_header"),
)

# COMMAND ----------

(
    flattened_df.repartition(TARGET_PARTITIONS).write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

bulk_end = time.time()
bulk_end_ts = datetime.now(timezone.utc)
print(f"Wrote protected external table with bulk object-aware protect in {bulk_end - bulk_start:.2f} seconds: {TARGET_TABLE}")

target_count = spark.table(TARGET_TABLE).count()
print(f"Protected external target row count: {target_count}")
if target_count != ROW_COUNT:
    raise ValueError(
        "Protected external target row count did not match the expected source row count. "
        f"Expected: {ROW_COUNT}, Actual: {target_count}"
    )

append_perf_metrics(
    run_name=RUN_NAME,
    step_name=PROTECT_STEP_NAME,
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
        "group_size": group_size,
        "group_size_multiplier": GROUP_SIZE_MULTIPLIER,
        "benchmark_mode": True,
        "group_count_override": GROUP_COUNT_OVERRIDE,
        "estimated_group_count": estimated_group_count,
        "grouping_strategy": grouping_strategy,
        "step_start_ts": bulk_start_ts,
        "step_end_ts": bulk_end_ts,
    },
)

# COMMAND ----------

display(spark.createDataFrame([(ROW_COUNT,)], ["source_count"]))
display(spark.createDataFrame([(target_count,)], ["protected_count"]))
display(spark.sql(f"SELECT * FROM {TARGET_TABLE} LIMIT 5"))

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW v_external_bulk_parallelism_diag_revealed AS
    SELECT
      custid,
      name,
      thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(address AS STRING),
        CAST(address_header AS STRING),
        'char',
        '{ROW_REVEAL_OBJECT_NAME}',
        'address',
        current_user()
      ) AS address,
      city,
      state,
      zip,
      phone,
      thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(email AS STRING),
        CAST(email_header AS STRING),
        'char',
        '{ROW_REVEAL_OBJECT_NAME}',
        'email',
        current_user()
      ) AS email,
      dob,
      CAST(
        thales_reveal_by_object_and_column_with_external_header_and_user(
          CAST(creditcard AS STRING),
          CAST(creditcard_header AS STRING),
          'nbr',
          '{ROW_REVEAL_OBJECT_NAME}',
          'creditcard',
          current_user()
        ) AS DECIMAL(25,0)
      ) AS creditcard,
      CAST(
        thales_reveal_by_object_and_column_with_external_header_and_user(
          CAST(creditcardcode AS STRING),
          CAST(creditcardcode_header AS STRING),
          'nbr',
          '{ROW_REVEAL_OBJECT_NAME}',
          'creditcardcode',
          current_user()
        ) AS INT
      ) AS creditcardcode,
      thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(ssn AS STRING),
        CAST(ssn_header AS STRING),
        'nbr',
        '{ROW_REVEAL_OBJECT_NAME}',
        'ssn',
        current_user()
      ) AS ssn
    FROM {TARGET_TABLE}
    """
)

display(spark.sql("SELECT * FROM v_external_bulk_parallelism_diag_revealed LIMIT 5"))
display(spark.sql(f"SELECT * FROM {METRICS_TABLE} ORDER BY metric_ts_utc DESC LIMIT 20"))

# COMMAND ----------

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

print(
    "External bulk benchmark completed. Review the Spark UI to confirm grouped bulk "
    "shape, executor task distribution, and end-to-end runtime."
)

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

