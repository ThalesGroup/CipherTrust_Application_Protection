# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Helper DataFrame ADLS Load Example
# MAGIC
# MAGIC This notebook shows the new Python helper API reading plaintext data
# MAGIC directly from ADLS Gen2, protecting sensitive columns, and writing the
# MAGIC result to a Delta table and optional Delta path.
# MAGIC
# MAGIC Use this pattern when:
# MAGIC
# MAGIC - source data lands in ADLS
# MAGIC - you want the higher-level Python helper API
# MAGIC - you want to produce a protected Silver-layer Delta table

# COMMAND ----------

import sys
from pathlib import Path

workspace_notebooks_root = "/Workspace/Users/yoruid/v3-examples/notebooks"
repo_notebooks_root = str(Path.cwd())

for candidate in [workspace_notebooks_root, repo_notebooks_root]:
    if candidate not in sys.path:
        sys.path.append(candidate)

from thales_databricks_integration import IntegrationConfig, protect_dataframe
from utils.runtime_diagnostics import (
    print_column_profile_diagnostics,
    print_object_mapping_diagnostics,
    print_profile_alias_diagnostics,
    print_runtime_diagnostics,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

STORAGE_ACCOUNT = "youraccount"
STORAGE_ACCOUNT_KEY = "sdfsdf/sdfsdf/+ASt7ClMLg=="
SOURCE_ADLS_PATH = (
    f"abfss://raw@{STORAGE_ACCOUNT}.dfs.core.windows.net/"
    "databricks/input/member.csv"
)
SOURCE_FORMAT = "csv"
SOURCE_OPTIONS = {"header": "true"}

TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_from_adls"
TARGET_DELTA_PATH = (
    f"abfss://raw@{STORAGE_ACCOUNT}.dfs.core.windows.net/"
    "databricks/output/plaintext_protected_internal_from_adls"
)
PROTECTED_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"

TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 16)
WRITE_TO_TABLE = True
WRITE_TO_PATH = True

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)
helper_options = {"transport_mode": "real"}

spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    STORAGE_ACCOUNT_KEY,
)

print_runtime_diagnostics(
    spark,
    label="Internal helper ADLS runtime diagnostics:",
    config_path=config_path,
    runtime_settings=config.raw_properties,
    include_debug_flag=True,
)
print_object_mapping_diagnostics(config.raw_properties, [PROTECTED_OBJECT_NAME])
print_profile_alias_diagnostics(
    config.raw_properties,
    [
        "TAG.char.internal",
        "TAG.nbr.internal",
    ],
)
print_column_profile_diagnostics(
    config.raw_properties,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)

print("Source ADLS path:", SOURCE_ADLS_PATH)
print("Target table:", TARGET_TABLE)
print("Target Delta path:", TARGET_DELTA_PATH)
print("Storage account:", STORAGE_ACCOUNT)
print("Protected object name:", PROTECTED_OBJECT_NAME)
print("Target partitions:", TARGET_PARTITIONS)
print("API version:", config.crdp_api_version)
print("Transport mode:", helper_options["transport_mode"])

# COMMAND ----------

reader = spark.read.format(SOURCE_FORMAT)
for key, value in SOURCE_OPTIONS.items():
    reader = reader.option(key, value)

source_df = reader.load(SOURCE_ADLS_PATH)

print("Source schema:")
source_df.printSchema()
display(source_df.limit(10))

# COMMAND ----------

protected_df = protect_dataframe(
    source_df.repartition(TARGET_PARTITIONS),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)

print("Protect DataFrame plan summary:")
print(protected_df._thales_bulk_plan_summary)
display(protected_df.limit(10))

# COMMAND ----------

if WRITE_TO_TABLE:
    (
        protected_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(TARGET_TABLE)
    )
    print(f"Protected Delta table written: {TARGET_TABLE}")
    display(spark.table(TARGET_TABLE).limit(10))

if WRITE_TO_PATH:
    (
        protected_df.write
        .format("delta")
        .mode("overwrite")
        .save(TARGET_DELTA_PATH)
    )
    print(f"Protected Delta path written: {TARGET_DELTA_PATH}")
    display(spark.read.format("delta").load(TARGET_DELTA_PATH).limit(5))

# COMMAND ----------

print(
    "Internal helper ADLS example complete. "
    "This pattern belongs in the Bronze-to-Silver protection step: raw ADLS "
    "input is transformed into protected Delta output."
)
