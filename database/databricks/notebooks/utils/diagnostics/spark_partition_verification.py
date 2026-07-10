# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Cluster Partition Verification
# MAGIC
# MAGIC Purpose:
# MAGIC - verify that Spark is partitioning data on a compute cluster
# MAGIC - verify that Java UDF evaluation runs inside executor tasks
# MAGIC - verify that the Python helper/DataFrame path also runs over Spark partitions
# MAGIC - provide a simple repeatable demo for `plaintext_protected_internal`
# MAGIC
# MAGIC What this notebook demonstrates:
# MAGIC 1. the input DataFrame has multiple partitions
# MAGIC 2. rows are distributed across partition IDs
# MAGIC 3. the Java jar / UDF path runs over those partitions
# MAGIC 4. the Python wheel / helper path also runs over those partitions
# MAGIC 5. the Spark UI should show multiple tasks and executor activity

# COMMAND ----------

from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql import types as T

from thales_databricks_integration import IntegrationConfig, reveal_dataframe

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
OBJECT_NAME = SOURCE_TABLE

# Use a visible partition count for demos.
# This notebook intentionally uses repartition(count) without a key so it is
# easy to see multiple tasks in Spark UI. For real customer workloads, a
# well-distributed business key such as custid or account_id is often a better
# repartition key when one exists.
TARGET_PARTITIONS = 8

# Increase row count so the job is easy to see in the Spark UI.
MULTIPLIER = 1000

# Set to "java_udf", "python_helper", or "both".
EXECUTION_MODEL = "both"

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

config = IntegrationConfig.from_properties(config_path)

print(
    {
        "api_version": config.crdp_api_version,
        "transport_mode": config.transport_mode,
        "real_transport_enabled": config.should_use_real_transport(),
        "crdp_endpoint_configured": config.has_crdp_endpoint(),
        "spark_group_size": config.spark_group_size,
    }
)

# COMMAND ----------

# Register only what the Java verification path needs.
spark.udf.registerJavaFunction(
    "thales_reveal_by_object_and_column_with_user",
    "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithUserUdf",
    T.StringType(),
)

print("Registered thales_reveal_by_object_and_column_with_user")

# COMMAND ----------

base_df = spark.table(SOURCE_TABLE)

print("Base row count:", base_df.count())
print("Base partitions:", base_df.rdd.getNumPartitions())

base_df.select("custid", "address", "email", "creditcard", "creditcardcode", "ssn").show(10, truncate=False)

# COMMAND ----------

# Build a larger test set so task distribution is easier to observe in Spark UI.
# This keeps the demo deterministic without needing an already-large customer table.
demo_df = (
    base_df.crossJoin(spark.range(0, MULTIPLIER).toDF("replica_id"))
    .repartition(TARGET_PARTITIONS)
    .withColumn("partition_id", F.spark_partition_id())
)

print("Demo row count:", demo_df.count())
print("Demo partitions:", demo_df.rdd.getNumPartitions())

# COMMAND ----------

partition_distribution_df = demo_df.groupBy("partition_id").count().orderBy("partition_id")
partition_distribution_df.show(TARGET_PARTITIONS, truncate=False)

# COMMAND ----------

if EXECUTION_MODEL in ("java_udf", "both"):
    java_udf_df = demo_df.selectExpr(
        "custid",
        "replica_id",
        "partition_id",
        """thales_reveal_by_object_and_column_with_user(
            CAST(address AS STRING),
            'char',
            'my_catalog.my_schema.plaintext_protected_internal',
            'address',
            current_user()
        ) AS address_revealed"""
    )

    print("Java UDF result partitions:", java_udf_df.rdd.getNumPartitions())
    print("Java UDF row count:", java_udf_df.count())

    java_udf_df.select(
        "custid",
        "replica_id",
        "partition_id",
        "address_revealed",
    ).orderBy("partition_id", "custid").show(25, truncate=False)

    java_udf_partition_summary_df = (
        java_udf_df.groupBy("partition_id").count().orderBy("partition_id")
    )

    java_udf_partition_summary_df.show(TARGET_PARTITIONS, truncate=False)

# COMMAND ----------

if EXECUTION_MODEL in ("python_helper", "both"):
    helper_input_df = demo_df.drop("partition_id")

    helper_revealed_df = reveal_dataframe(
        helper_input_df,
        object_name=OBJECT_NAME,
        config=config,
        options={"transport_mode": "real"},
    ).withColumn("partition_id", F.spark_partition_id())

    print("Python helper result partitions:", helper_revealed_df.rdd.getNumPartitions())
    print("Python helper row count:", helper_revealed_df.count())

    helper_revealed_df.select(
        "custid",
        "replica_id",
        "partition_id",
        "address",
    ).orderBy("partition_id", "custid").show(25, truncate=False)

    helper_partition_summary_df = (
        helper_revealed_df.groupBy("partition_id").count().orderBy("partition_id")
    )

    helper_partition_summary_df.show(TARGET_PARTITIONS, truncate=False)

    print("Python helper plan summary:")
    print(helper_revealed_df._thales_bulk_plan_summary)

# COMMAND ----------

print(
    f"""
How to verify executor-side partitioned execution in Databricks:

1. Open the compute cluster used for this notebook.
2. Open Spark UI.
3. Open the most recent job triggered by the selected execution model.
4. Open the relevant stage.
5. Confirm:
   - the stage has multiple tasks (typically close to TARGET_PARTITIONS)
   - tasks ran on executor IDs, not only on the driver
   - task input/output metrics are distributed across executors

What this notebook proves:
- spark_partition_id() shows the DataFrame was partitioned
- rdd.getNumPartitions() shows the planned partition count
- the Java UDF path runs as part of a Spark action over those partitions
- the Python helper/DataFrame path also runs as part of a Spark action over those partitions

Notes:
- EXECUTION_MODEL controls whether the notebook runs the Java UDF path, the Python helper path, or both
- tiny datasets can still be partitioned, but the Spark UI is easier to read with a larger demo set
- TARGET_PARTITIONS controls how many partitions to demonstrate
- repartition(TARGET_PARTITIONS) is a demo choice, not a claim that protected columns should be used as partition keys
- for real customer loads, prefer repartition(n, "custid") or repartition(n, "account_id") when those keys distribute evenly
- MULTIPLIER controls how much demo data is generated from the source table
"""
)
