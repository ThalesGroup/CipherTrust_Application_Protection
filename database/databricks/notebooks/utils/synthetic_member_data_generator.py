# Databricks notebook source
# MAGIC %md
# MAGIC # Synthetic Member Data Generator
# MAGIC
# MAGIC This notebook generates the same style of synthetic member data used by
# MAGIC the benchmark notebooks, but writes the output to a filesystem path
# MAGIC instead of a managed table.
# MAGIC
# MAGIC Supported output targets:
# MAGIC
# MAGIC - ADLS Gen2 paths such as `abfss://...`
# MAGIC - Databricks paths such as `dbfs:/...`, `/Volumes/...`, `/mnt/...`
# MAGIC - Linux-style local filesystem paths such as `/data/output/...`
# MAGIC - Windows-style local filesystem paths such as `C:\\data\\output\\...`
# MAGIC
# MAGIC Notes:
# MAGIC
# MAGIC - For ADLS output, configure the storage account key below or replace
# MAGIC   that section with your preferred Databricks credential model.
# MAGIC - Windows local paths are normalized to `file:///C:/...` form. They are
# MAGIC   only usable when the Spark environment can actually access that path.

# COMMAND ----------

import re
import time
from datetime import datetime, timezone

from pyspark.sql import functions as F

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

STORAGE_ACCOUNT = "youraccount"
STORAGE_ACCOUNT_KEY = "sdfsdfsdf/sdfsdfsdf/+ASt7ClMLg=="

OUTPUT_DIRECTORY = (
    f"abfss://raw@{STORAGE_ACCOUNT}.dfs.core.windows.net/"
    "databricks/synthetic_member_data"
)

ROW_COUNT = 350_000
OUTPUT_FILE_COUNT = 8
#OUTPUT_DIRECTORY = "dbfs:/tmp/thales/synthetic_member_data"
OUTPUT_FORMAT = "csv"
WRITE_MODE = "overwrite"
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, OUTPUT_FILE_COUNT, 32)

# CSV is the most convenient interchange format for file-based testing.
OUTPUT_OPTIONS = {
    "header": "true",
}

# Optional ADLS support.
#STORAGE_ACCOUNT = None
#STORAGE_ACCOUNT_KEY = None

# COMMAND ----------

SUPPORTED_FORMATS = {"csv", "parquet", "json", "delta"}


def normalize_output_path(path: str) -> str:
    if not path or not path.strip():
        raise ValueError("OUTPUT_DIRECTORY must be a non-empty path.")

    normalized = path.strip()

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", normalized):
        return normalized

    if normalized.startswith("dbfs:/"):
        return normalized

    if normalized.startswith("/Volumes/") or normalized.startswith("/mnt/"):
        return normalized

    if re.match(r"^[A-Za-z]:[\\\\/]", normalized):
        windows_path = normalized.replace("\\", "/")
        return f"file:///{windows_path}"

    if normalized.startswith("/"):
        return f"file://{normalized}"

    raise ValueError(
        "Unsupported OUTPUT_DIRECTORY format. Use abfss://..., dbfs:/..., "
        "/Volumes/..., /mnt/..., a Linux absolute path, or a Windows absolute path."
    )


def configure_storage_if_needed(path: str):
    if path.startswith("abfss://"):
        if not STORAGE_ACCOUNT or not STORAGE_ACCOUNT_KEY:
            raise ValueError(
                "ADLS output selected but STORAGE_ACCOUNT or STORAGE_ACCOUNT_KEY "
                "is not configured."
            )
        spark.conf.set(
            f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
            STORAGE_ACCOUNT_KEY,
        )


def print_settings_section(title, values):
    print(title)
    for key, value in values.items():
        print(f"  {key}: {value}")


if OUTPUT_FORMAT.lower() not in SUPPORTED_FORMATS:
    raise ValueError(
        f"Unsupported OUTPUT_FORMAT '{OUTPUT_FORMAT}'. "
        f"Choose one of: {sorted(SUPPORTED_FORMATS)}"
    )

if ROW_COUNT <= 0:
    raise ValueError("ROW_COUNT must be greater than 0.")

if OUTPUT_FILE_COUNT <= 0:
    raise ValueError("OUTPUT_FILE_COUNT must be greater than 0.")

NORMALIZED_OUTPUT_DIRECTORY = normalize_output_path(OUTPUT_DIRECTORY)
configure_storage_if_needed(NORMALIZED_OUTPUT_DIRECTORY)

# COMMAND ----------

print_settings_section(
    "Synthetic data generator settings:",
    {
        "row_count": ROW_COUNT,
        "generate_partitions": GENERATE_PARTITIONS,
        "output_file_count": OUTPUT_FILE_COUNT,
        "output_directory": OUTPUT_DIRECTORY,
        "normalized_output_directory": NORMALIZED_OUTPUT_DIRECTORY,
        "output_format": OUTPUT_FORMAT,
        "write_mode": WRITE_MODE,
        "output_options": OUTPUT_OPTIONS,
    },
)

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

generate_seconds = time.time() - generate_start
print(f"Generated DataFrame in {generate_seconds:.2f}s")
display(source_df.limit(10))

# COMMAND ----------

write_start = time.time()
write_start_ts = datetime.now(timezone.utc)

writer = (
    source_df.repartition(OUTPUT_FILE_COUNT)
    .write
    .format(OUTPUT_FORMAT)
    .mode(WRITE_MODE)
)

for key, value in OUTPUT_OPTIONS.items():
    writer = writer.option(key, value)

writer.save(NORMALIZED_OUTPUT_DIRECTORY)

write_seconds = time.time() - write_start
write_end_ts = datetime.now(timezone.utc)

print(f"Wrote synthetic data in {write_seconds:.2f}s")
print(f"Output path: {NORMALIZED_OUTPUT_DIRECTORY}")

# COMMAND ----------

reader = spark.read.format(OUTPUT_FORMAT)
for key, value in OUTPUT_OPTIONS.items():
    if OUTPUT_FORMAT.lower() != "delta":
        reader = reader.option(key, value)

written_df = reader.load(NORMALIZED_OUTPUT_DIRECTORY)

print_settings_section(
    "Synthetic data generator results:",
    {
        "generate_start_ts": generate_start_ts,
        "write_start_ts": write_start_ts,
        "write_end_ts": write_end_ts,
        "row_count_written": written_df.count(),
        "output_file_count_target": OUTPUT_FILE_COUNT,
        "output_format": OUTPUT_FORMAT,
        "output_directory": NORMALIZED_OUTPUT_DIRECTORY,
        "generate_seconds": round(generate_seconds, 2),
        "write_seconds": round(write_seconds, 2),
    },
)

display(written_df.limit(10))
