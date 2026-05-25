# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Cluster Partition Verification
# MAGIC
# MAGIC Purpose:
# MAGIC - verify that Spark is partitioning data on a compute cluster
# MAGIC - verify that UDF evaluation runs inside executor tasks
# MAGIC - provide a simple repeatable demo for `plaintext_protected_internal`
# MAGIC
# MAGIC What this notebook demonstrates:
# MAGIC 1. the input DataFrame has multiple partitions
# MAGIC 2. rows are distributed across partition IDs
# MAGIC 3. a Java Spark UDF runs over those partitions
# MAGIC 4. the Spark UI should show multiple tasks and executor activity

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"

# Use a visible partition count for demos.
# This notebook intentionally uses repartition(count) without a key so it is
# easy to see multiple tasks in Spark UI. For real customer workloads, a
# well-distributed business key such as custid or account_id is often a better
# repartition key when one exists.
TARGET_PARTITIONS = 8

# Increase row count so the job is easy to see in the Spark UI.
MULTIPLIER = 1000

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

# COMMAND ----------

# Register only what this notebook needs.
spark.udf.registerJavaFunction(
    "thales_reveal_by_column_with_user",
    "ThalesCrdpRevealByColumnWithUserUdf",
    T.StringType(),
)

print("Registered thales_reveal_by_column_with_user")

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

# Show how rows are distributed across partitions.
partition_distribution_df = (
    demo_df.groupBy("partition_id")
    .count()
    .orderBy("partition_id")
)

partition_distribution_df.show(TARGET_PARTITIONS, truncate=False)

# COMMAND ----------

# Run the Java UDF over the partitioned data.
# The count() action forces Spark to execute the plan.
udf_df = demo_df.selectExpr(
    "custid",
    "replica_id",
    "partition_id",
    "thales_reveal_by_column_with_user(CAST(address AS STRING), 'char', 'address', current_user()) AS address_revealed"
)

print("UDF result partitions:", udf_df.rdd.getNumPartitions())
print("UDF row count:", udf_df.count())

# COMMAND ----------

# Materialize a small sample so you can see the partition id next to revealed data.
udf_df.select("custid", "replica_id", "partition_id", "address_revealed").orderBy("partition_id", "custid").show(25, truncate=False)

# COMMAND ----------

# Optional: summarize how many rows per partition made it through the UDF stage.
udf_partition_summary_df = (
    udf_df.groupBy("partition_id")
    .count()
    .orderBy("partition_id")
)

udf_partition_summary_df.show(TARGET_PARTITIONS, truncate=False)

# COMMAND ----------

print(
    """
How to verify executor-side partitioned execution in Databricks:

1. Open the compute cluster used for this notebook.
2. Open Spark UI.
3. Open the most recent job triggered by udf_df.count().
4. Open the relevant stage.
5. Confirm:
   - the stage has multiple tasks (typically close to TARGET_PARTITIONS)
   - tasks ran on executor IDs, not only on the driver
   - task input/output metrics are distributed across executors

What this notebook proves:
- spark_partition_id() shows the DataFrame was partitioned
- rdd.getNumPartitions() shows the planned partition count
- the Java UDF runs as part of a Spark action over those partitions

Notes:
- tiny datasets can still be partitioned, but the Spark UI is easier to read with a larger demo set
- TARGET_PARTITIONS controls how many partitions to demonstrate
- repartition(TARGET_PARTITIONS) is a demo choice, not a claim that protected columns should be used as partition keys
- for real customer loads, prefer repartition(n, "custid") or repartition(n, "account_id") when those keys distribute evenly
- MULTIPLIER controls how much demo data is generated from the source table
"""
)
