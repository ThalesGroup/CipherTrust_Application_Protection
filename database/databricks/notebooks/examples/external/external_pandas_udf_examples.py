# Databricks notebook source
# MAGIC %md
# MAGIC # External Pandas UDF Examples
# MAGIC
# MAGIC This notebook shows the Pandas rowset execution path for the external
# MAGIC policy mode. It focuses on `mapInPandas` because the external path needs
# MAGIC to preserve sibling `*_header` columns during protect and then consume
# MAGIC them during reveal.

# COMMAND ----------

from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe_map_in_pandas,
    reveal_dataframe_map_in_pandas,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

EXTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_external_helper_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_pandas_udf_demo"

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)
helper_options = {
    "api_version": "v2",
    "transport_mode": "real",
}

# COMMAND ----------

source_df = spark.table(SOURCE_TABLE).orderBy("custid").limit(20)
display(source_df)

# COMMAND ----------

protected_df = protect_dataframe_map_in_pandas(
    source_df,
    object_name=EXTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

(
    protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

display(spark.table(TARGET_TABLE))

# COMMAND ----------

revealed_df = reveal_dataframe_map_in_pandas(
    spark.table(TARGET_TABLE).orderBy("custid"),
    object_name=EXTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

display(revealed_df)

# COMMAND ----------

print("THALES_EXTERNAL_PANDAS_UDF_EXAMPLES_FINISHED")
