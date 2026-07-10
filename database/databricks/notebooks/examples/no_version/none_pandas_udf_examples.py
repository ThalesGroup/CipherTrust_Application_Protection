# Databricks notebook source
# MAGIC %md
# MAGIC # None Pandas UDF Examples
# MAGIC
# MAGIC This notebook shows both Pandas execution surfaces for the no-version
# MAGIC (`none`) path:
# MAGIC
# MAGIC - scalar Pandas UDF for a single protected column
# MAGIC - rowset `mapInPandas` for the full object

# COMMAND ----------

from thales_databricks_integration import (
    IntegrationConfig,
    make_protect_scalar_pandas_udf,
    make_reveal_scalar_pandas_udf,
    protect_dataframe_map_in_pandas,
    reveal_dataframe_map_in_pandas,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

NONE_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext_none_helper_parallelism_diag"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_pandas_udf_demo"

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

protect_email_udf = make_protect_scalar_pandas_udf(
    object_name=NONE_OBJECT,
    column_name="email",
    datatype="char",
    config=config,
    options=helper_options,
)

reveal_email_udf = make_reveal_scalar_pandas_udf(
    object_name=NONE_OBJECT,
    column_name="email",
    datatype="char",
    spark_session=spark,
    config=config,
    options=helper_options,
)

scalar_demo_df = (
    source_df
    .select(
        "custid",
        "email",
        protect_email_udf("email").alias("email_protected"),
    )
    .withColumn("email_revealed", reveal_email_udf("email_protected"))
)

display(scalar_demo_df)

# COMMAND ----------

protected_df = protect_dataframe_map_in_pandas(
    source_df,
    object_name=NONE_OBJECT,
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
    object_name=NONE_OBJECT,
    config=config,
    options=helper_options,
)

display(revealed_df)

# COMMAND ----------

print("THALES_NONE_PANDAS_UDF_EXAMPLES_FINISHED")
