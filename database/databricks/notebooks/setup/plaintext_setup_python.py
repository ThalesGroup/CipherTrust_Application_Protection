# Databricks notebook source
# MAGIC %md
# MAGIC # Plaintext Customer Table Setup v2 Draft
# MAGIC
# MAGIC This notebook is the draft "new style" counterpart to
# MAGIC `plaintext_setup.sql`.
# MAGIC
# MAGIC It keeps the same sample-table intent, but shifts the protection flow
# MAGIC toward the new helper-oriented design:
# MAGIC
# MAGIC - DataFrame-first public API
# MAGIC - object-aware policy resolution from `udfConfig.properties`
# MAGIC - bulk request planning hidden behind the helper
# MAGIC - no manual array choreography in the notebook author experience
# MAGIC
# MAGIC Current prototype status:
# MAGIC
# MAGIC - source and target table setup is fully normal Spark SQL / DataFrame work
# MAGIC - `protect_dataframe(...)` now runs the first Spark-side helper path for
# MAGIC   internal and none object flows
# MAGIC - `protect_rows(...)` and `reveal_rows(...)` provide smaller trace/debug paths
# MAGIC - the helper can fail fast in `real` mode when you want strict CRDP
# MAGIC   validation on a compute cluster

# COMMAND ----------

from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe,
    protect_rows,
    reveal_dataframe,
    reveal_rows,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

PLAINTEXT_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
INTERNAL_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
NONE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"

INTERNAL_OBJECT = INTERNAL_TABLE
NONE_OBJECT = NONE_TABLE

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)
REQUIRE_REAL_TRANSPORT = False
helper_options = {"transport_mode": "real"} if REQUIRE_REAL_TRANSPORT else None

if REQUIRE_REAL_TRANSPORT and not config.has_crdp_endpoint():
    raise ValueError(
        "REQUIRE_REAL_TRANSPORT is enabled, but udfConfig.properties still does not "
        "point at a real CRDP endpoint."
    )

print("Loaded config summary:")
print(
    {
        "api_version": config.crdp_api_version,
        "transport_mode": config.transport_mode,
        "real_transport_enabled": config.should_use_real_transport() or REQUIRE_REAL_TRANSPORT,
        "crdp_endpoint_configured": config.has_crdp_endpoint(),
        "spark_group_size": config.spark_group_size,
        "v2_max_items_per_request": config.crdp_v2_max_items_per_request,
        "v2_max_policy_groups_per_request": config.crdp_v2_max_policy_groups_per_request,
        "v2_enable_multi_policy": config.crdp_v2_enable_multi_policy,
    }
)

# COMMAND ----------

# Source table preview created by plaintext_setup.sql
source_df = spark.table(PLAINTEXT_TABLE).orderBy("custid")
display(source_df.limit(10))

# COMMAND ----------

# Protect flow for the internal target using the new Spark-side helper path.
internal_protected_df = protect_dataframe(
    df=source_df,
    object_name=INTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

print("Internal protected DataFrame preview:")
print(internal_protected_df._thales_bulk_plan_summary)
display(internal_protected_df.limit(10))

(
    internal_protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(INTERNAL_TABLE)
)

print("Internal protected table written:", INTERNAL_TABLE)
display(spark.table(INTERNAL_TABLE).orderBy("custid").limit(10))

# COMMAND ----------

# Protect flow for the none target using the new Spark-side helper path.
none_protected_df = protect_dataframe(
    df=source_df,
    object_name=NONE_OBJECT,
    config=config,
    options=helper_options,
)

print("None protected DataFrame preview:")
print(none_protected_df._thales_bulk_plan_summary)
display(none_protected_df.limit(10))

(
    none_protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(NONE_TABLE)
)

print("None protected table written:", NONE_TABLE)
display(spark.table(NONE_TABLE).orderBy("custid").limit(10))

# COMMAND ----------

# Executable row-shaped prototype for the internal object.
# This is the current proof that the object-aware plan and v2 request builder
# are aligned with the setup tables.
sample_rows = [
    row.asDict(recursive=True)
    for row in source_df.select("custid", "address", "email", "creditcard", "creditcardcode", "ssn", "city")
    .limit(5)
    .collect()
]

internal_row_result = protect_rows(
    rows=sample_rows,
    object_name=INTERNAL_OBJECT,
    config=config,
)

print("Internal row-shaped protect request summary:")
print(
    {
        "input_row_count": internal_row_result.input_row_count,
        "transformed_value_count": internal_row_result.transformed_value_count,
        "request_count": internal_row_result.request_count,
        "requests": internal_row_result.requests,
    }
)

print("Internal protected sample rows:")
for row in internal_row_result.rows:
    print(row)

# COMMAND ----------

# Executable row-shaped prototype for the none object.
none_row_result = protect_rows(
    rows=sample_rows,
    object_name=NONE_OBJECT,
    config=config,
)

print("None row-shaped protect request summary:")
print(
    {
        "input_row_count": none_row_result.input_row_count,
        "transformed_value_count": none_row_result.transformed_value_count,
        "request_count": none_row_result.request_count,
        "requests": none_row_result.requests,
    }
)

# COMMAND ----------

internal_revealed_df = reveal_dataframe(
    df=spark.table(INTERNAL_TABLE).orderBy("custid"),
    object_name=INTERNAL_OBJECT,
    config=config,
    options=helper_options,
)

print("Internal revealed DataFrame preview:")
print(internal_revealed_df._thales_bulk_plan_summary)
display(internal_revealed_df.limit(10))

# COMMAND ----------

internal_reveal_row_result = reveal_rows(
    rows=internal_row_result.rows,
    object_name=INTERNAL_OBJECT,
    config=config,
)

print("Internal row-shaped reveal request summary:")
print(
    {
        "input_row_count": internal_reveal_row_result.input_row_count,
        "transformed_value_count": internal_reveal_row_result.transformed_value_count,
        "request_count": internal_reveal_row_result.request_count,
        "requests": internal_reveal_row_result.requests,
    }
)

print("Internal revealed sample rows:")
for row in internal_reveal_row_result.rows:
    print(row)

# COMMAND ----------

# Current boundary notes:
#
# - internal and none protect table writes now go through the helper path
# - external-header persistence is not implemented yet in the helper
# - reveal_dataframe(...) is now implemented for the same mapped columns
# - strict CRDP validation can be forced with REQUIRE_REAL_TRANSPORT = True
# - external-header persistence still needs a fuller table-flow implementation

# COMMAND ----------

print("Row counts after helper-based writes:")
print("plaintext source:", spark.table(PLAINTEXT_TABLE).count())
print("internal protected:", spark.table(INTERNAL_TABLE).count())
print("none protected:", spark.table(NONE_TABLE).count())

# COMMAND ----------

print(
    "plaintext_setup_v2 draft complete. "
    "This notebook now uses the Spark-side helper path to populate the internal "
    "and none protected tables, and it can now reveal internal protected rows "
    "through the same helper style."
)
