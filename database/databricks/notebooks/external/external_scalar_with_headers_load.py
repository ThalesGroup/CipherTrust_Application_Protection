# Databricks notebook source
# MAGIC %md
# MAGIC # External Scalar With Headers Load
# MAGIC
# MAGIC This notebook shows the recommended production-style external load pattern
# MAGIC for protecting a plaintext table with the scalar struct-returning Java UDF on
# MAGIC a Databricks compute cluster.
# MAGIC
# MAGIC Recommended flow:
# MAGIC - run `compute_cluster_udf_smoke_test.py` first to register the Java UDFs
# MAGIC - point this notebook at the customer plaintext table
# MAGIC - choose a reasonable repartition count
# MAGIC - write the protected table using distributed executor-side UDF execution
# MAGIC
# MAGIC The external-protect UDF returns a struct with:
# MAGIC - `protected_value`
# MAGIC - `external_header`
# MAGIC
# MAGIC The protected table should persist both values.
# MAGIC
# MAGIC Use this notebook when validating the standard external-table load shape,
# MAGIC not when doing grouped bulk-array tuning.
# MAGIC
# MAGIC Repartition guidance:
# MAGIC - start with `spark.sparkContext.defaultParallelism`
# MAGIC - increase it if input files are very large and executors are underutilized
# MAGIC - decrease it if tasks are tiny and scheduling overhead dominates
# MAGIC - external protect currently uses the scalar struct-returning UDF, not an array-of-struct bulk loader

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"

TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism, 8)

# COMMAND ----------

required_functions = [
    "thales_protect_by_column_with_external_header",
]

missing_functions = [
    function_name for function_name in required_functions
    if not spark.catalog.functionExists(function_name)
]

if missing_functions:
    raise ValueError(
        "Required Java UDFs are not registered in this session. "
        "Run compute_cluster_udf_smoke_test.py first. "
        f"Missing functions: {', '.join(missing_functions)}"
    )

print("Source table:", SOURCE_TABLE)
print("Target table:", TARGET_TABLE)
print("Target partitions:", TARGET_PARTITIONS)

# COMMAND ----------

source_df = spark.table(SOURCE_TABLE).repartition(TARGET_PARTITIONS)

protected_df = (
    source_df.select(
        "custid",
        "name",
        F.expr("thales_protect_by_column_with_external_header(CAST(address AS STRING), 'char', 'address')").alias("protected_address"),
        "city",
        "state",
        "zip",
        "phone",
        F.expr("thales_protect_by_column_with_external_header(CAST(email AS STRING), 'char', 'email')").alias("protected_email"),
        "dob",
        F.expr("thales_protect_by_column_with_external_header(CAST(creditcard AS STRING), 'nbr', 'creditcard')").alias("protected_creditcard"),
        F.expr("thales_protect_by_column_with_external_header(CAST(creditcardcode AS STRING), 'nbr', 'creditcardcode')").alias("protected_creditcardcode"),
        F.expr("thales_protect_by_column_with_external_header(CAST(ssn AS STRING), 'nbr', 'ssn')").alias("protected_ssn"),
    )
    .select(
        "custid",
        "name",
        F.col("protected_address.protected_value").alias("address"),
        F.col("protected_address.external_header").alias("address_header"),
        "city",
        "state",
        "zip",
        "phone",
        F.col("protected_email.protected_value").alias("email"),
        F.col("protected_email.external_header").alias("email_header"),
        "dob",
        F.col("protected_creditcard.protected_value").alias("creditcard"),
        F.col("protected_creditcard.external_header").alias("creditcard_header"),
        F.col("protected_creditcardcode.protected_value").alias("creditcardcode"),
        F.col("protected_creditcardcode.external_header").alias("creditcardcode_header"),
        F.col("protected_ssn.protected_value").alias("ssn"),
        F.col("protected_ssn.external_header").alias("ssn_header"),
    )
)

# COMMAND ----------

(
    protected_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

print(f"Wrote protected external table: {TARGET_TABLE}")

# COMMAND ----------

spark.sql(f"SELECT COUNT(*) AS row_count FROM {TARGET_TABLE}").show()
spark.sql(f"SELECT * FROM {TARGET_TABLE} ORDER BY custid LIMIT 10").show(truncate=False)

# COMMAND ----------

print(
    "External high-throughput load completed. Review the Spark UI to confirm "
    "partition count, executor task distribution, and end-to-end runtime."
)

