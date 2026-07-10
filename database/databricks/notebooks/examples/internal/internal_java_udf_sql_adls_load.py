# Databricks notebook source
# MAGIC %md
# MAGIC # Internal Java UDF SQL ADLS Load Example
# MAGIC
# MAGIC This notebook shows the Java SQL/UDF path reading plaintext data from
# MAGIC ADLS Gen2, registering the new Java UDFs, and protecting sensitive
# MAGIC columns through a SQL CTAS pattern.
# MAGIC
# MAGIC Use this pattern when:
# MAGIC
# MAGIC - source data lands in ADLS
# MAGIC - the team prefers SQL / CTAS style ETL
# MAGIC - you want a protected Silver-layer Delta table

# COMMAND ----------

import sys
from pathlib import Path

workspace_notebooks_root = "/Workspace/Users/yoruid/v3-examples/notebooks"
repo_notebooks_root = str(Path.cwd())

for candidate in [workspace_notebooks_root, repo_notebooks_root]:
    if candidate not in sys.path:
        sys.path.append(candidate)

from pyspark.sql import types as T
from utils.runtime_diagnostics import (
    load_runtime_properties,
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

SOURCE_VIEW = "v_internal_adls_source"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_java_from_adls"
TARGET_DELTA_PATH = (
    f"abfss://raw@{STORAGE_ACCOUNT}.dfs.core.windows.net/"
    "databricks/output/plaintext_protected_internal_java_from_adls"
)
PROTECTED_OBJECT_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
PROTECTED_VIEW = "v_internal_adls_protected"
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

runtime_settings = load_runtime_properties(config_path)
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    STORAGE_ACCOUNT_KEY,
)
print_runtime_diagnostics(
    spark,
    label="Internal Java UDF ADLS runtime diagnostics:",
    config_path=config_path,
    runtime_settings=runtime_settings,
    include_debug_flag=True,
)
print_object_mapping_diagnostics(runtime_settings, [PROTECTED_OBJECT_NAME])
print_profile_alias_diagnostics(
    runtime_settings,
    [
        "TAG.char.internal",
        "TAG.nbr.internal",
    ],
)
print_column_profile_diagnostics(
    runtime_settings,
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

# COMMAND ----------

spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column",
    "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnUdf",
    T.StringType(),
)

print("Java UDF registered successfully.")

# COMMAND ----------

reader = spark.read.format(SOURCE_FORMAT)
for key, value in SOURCE_OPTIONS.items():
    reader = reader.option(key, value)

source_df = reader.load(SOURCE_ADLS_PATH)
source_df.createOrReplaceTempView(SOURCE_VIEW)

print("Source schema:")
source_df.printSchema()
display(source_df.limit(10))

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW {PROTECTED_VIEW} AS
SELECT
  custid,
  name,
  thales_protect_by_object_and_column(
    CAST(address AS STRING),
    'char',
    '{PROTECTED_OBJECT_NAME}',
    'address'
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_protect_by_object_and_column(
    CAST(email AS STRING),
    'char',
    '{PROTECTED_OBJECT_NAME}',
    'email'
  ) AS email,
  dob,
  thales_protect_by_object_and_column(
    CAST(creditcard AS STRING),
    'nbr',
    '{PROTECTED_OBJECT_NAME}',
    'creditcard'
  ) AS creditcard,
  thales_protect_by_object_and_column(
    CAST(creditcardcode AS STRING),
    'nbr',
    '{PROTECTED_OBJECT_NAME}',
    'creditcardcode'
  ) AS creditcardcode,
  thales_protect_by_object_and_column(
    CAST(ssn AS STRING),
    'nbr',
    '{PROTECTED_OBJECT_NAME}',
    'ssn'
  ) AS ssn
FROM {SOURCE_VIEW}
""")

protected_df = spark.table(PROTECTED_VIEW)

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
else:
    display(protected_df.limit(10))

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
    "Internal Java UDF ADLS example complete. "
    "This pattern also belongs in the Bronze-to-Silver protection step: raw "
    "ADLS input is transformed into protected Delta output through SQL."
)
