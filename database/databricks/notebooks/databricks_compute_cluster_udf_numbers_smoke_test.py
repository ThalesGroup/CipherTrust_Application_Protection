# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster Secure View Example - Numeric Cast-Back Pattern
# MAGIC
# MAGIC This notebook demonstrates the recommended compute-cluster pattern for
# MAGIC numeric measures.
# MAGIC
# MAGIC Run this notebook first on the compute cluster to register the required
# MAGIC Java UDFs. The companion SQL setup script
# MAGIC `compute_cluster_numbers_setup.sql` assumes these functions
# MAGIC already exist in the current session.
# MAGIC
# MAGIC Protect numeric measures as STRING, reveal as STRING, and cast the
# MAGIC revealed value back to BIGINT / DECIMAL for analytics. This mirrors
# MAGIC the `test2_castback` pattern and avoids leading-zero loss and length
# MAGIC issues in numeric token values.

# COMMAND ----------

from decimal import Decimal

from pyspark.sql import types as T

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
executor_config_path = spark.conf.get("spark.executorEnv.UDF_CONFIG_VOLUME_PATH", None)

print("Driver config path:", config_path)
print("Executor config path:", executor_config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running the tests."
    )

# COMMAND ----------

def register_typed_numeric_udfs():
    spark.udf.registerJavaFunction(
        "thales_protect",
        "ThalesCrdpProtectUdf",
        T.StringType(),
    )
    spark.udf.registerJavaFunction(
        "thales_protect_by_column",
        "ThalesCrdpProtectByColumnUdf",
        T.StringType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal",
        "ThalesCrdpRevealUdf",
        T.StringType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_with_user",
        "ThalesCrdpRevealWithUserUdf",
        T.StringType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_by_column",
        "ThalesCrdpRevealByColumnUdf",
        T.StringType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_by_column_with_user",
        "ThalesCrdpRevealByColumnWithUserUdf",
        T.StringType(),
    )

register_typed_numeric_udfs()
print("Generic scalar Java UDFs registered successfully for the cast-back numeric test.")

# COMMAND ----------

typed_numeric_df = spark.createDataFrame(
    [
        (101, 1234567890, Decimal("1250.75"), Decimal("42.50")),
        (102, 2234567890, Decimal("9999.99"), Decimal("105.10")),
        (103, 3234567890, Decimal("210.99"), Decimal("1000.00")),
    ],
    schema=T.StructType(
        [
            T.StructField("account_id", T.IntegerType(), False),
            T.StructField("balance_long", T.LongType(), True),
            T.StructField("amount_decimal", T.DecimalType(18, 2), True),
            T.StructField("fee_decimal", T.DecimalType(18, 2), True),
        ]
    ),
)

display(typed_numeric_df)

# COMMAND ----------

typed_token_df = typed_numeric_df.selectExpr(
    "account_id",
    "balance_long",
    "thales_protect_by_column(CAST(balance_long AS STRING), 'nbr', 'balance') AS balance_token",
    "amount_decimal",
    "thales_protect_by_column(CAST(amount_decimal AS STRING), 'nbr', 'amount') AS amount_token",
    "fee_decimal",
    "thales_protect_by_column(CAST(fee_decimal AS STRING), 'nbr', 'fee') AS fee_token",
)

display(typed_token_df)

# COMMAND ----------

typed_reveal_df = typed_token_df.selectExpr(
    "account_id",
    "balance_token",
    "amount_token",
    "fee_token",
).selectExpr(
    "account_id",
    "balance_token",
    "CAST(thales_reveal_by_column_with_user(CAST(balance_token AS STRING), 'nbr', 'balance', current_user()) AS BIGINT) AS balance_revealed",
    "amount_token",
    "CAST(thales_reveal_by_column_with_user(CAST(amount_token AS STRING), 'nbr', 'amount', current_user()) AS DECIMAL(18,2)) AS amount_revealed",
    "fee_token",
    "CAST(thales_reveal_by_column_with_user(CAST(fee_token AS STRING), 'nbr', 'fee', current_user()) AS DECIMAL(18,2)) AS fee_revealed",
)

display(typed_reveal_df)

# COMMAND ----------

typed_reveal_df.createOrReplaceTempView("temp_v_typed_numeric_round_trip")

spark.sql(
    """
    SELECT
      SUM(amount_revealed) AS total_amount,
      AVG(balance_revealed) AS avg_balance,
      SUM(fee_revealed) AS total_fee
    FROM temp_v_typed_numeric_round_trip
    """
).show(truncate=False)

# COMMAND ----------

print(
    "Smoke test 3 completed. Review the displayed results to confirm the "
    "string-tokenize plus cast-back pattern for BIGINT and DECIMAL measures. "
    "The sample data intentionally avoids very short numeric values because the "
    "older CRDP 8090 API can reject protection inputs near the sub-2-byte limit."
)

