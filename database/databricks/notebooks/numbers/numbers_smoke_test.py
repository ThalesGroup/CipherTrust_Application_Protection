# Databricks notebook source
# MAGIC %md
# MAGIC # Numbers Smoke Test
# MAGIC
# MAGIC This notebook runs the main numeric smoke tests for the compute-cluster
# MAGIC examples, including internal, external, and no-version numeric flows.
# MAGIC
# MAGIC Run `compute_cluster_udf_smoke_test.py` first on the compute
# MAGIC cluster to register the required Java UDFs. The companion SQL setup script
# MAGIC `numbers_setup.sql` assumes these functions already exist in the current
# MAGIC session and creates the permanent tables and views for the numeric sample
# MAGIC workflow.
# MAGIC
# MAGIC Use this notebook when the goal is to validate numeric UDF registration and
# MAGIC round-trip behavior. For the focused cast-back reveal examples, use
# MAGIC `numbers_reveal_castback_examples.py` or `numbers_reveal_castback_examples.sql`.

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

required_functions = [
    "thales_protect_by_object_and_column",
    "thales_protect_by_object_and_column_with_external_header",
    "thales_reveal_by_object_and_column_with_user",
    "thales_reveal_by_object_and_column_with_external_header_and_user",
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

print("Required Java UDFs already exist in this session. Proceeding with numeric validation.")

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
    """thales_protect_by_object_and_column(
        CAST(balance_long AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'balance'
    ) AS balance_token""",
    "amount_decimal",
    """thales_protect_by_object_and_column(
        CAST(amount_decimal AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'amount'
    ) AS amount_token""",
    "fee_decimal",
    """thales_protect_by_object_and_column(
        CAST(fee_decimal AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'fee'
    ) AS fee_token""",
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
    """CAST(thales_reveal_by_object_and_column_with_user(
        CAST(balance_token AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'balance',
        current_user()
    ) AS BIGINT) AS balance_revealed""",
    "amount_token",
    """CAST(thales_reveal_by_object_and_column_with_user(
        CAST(amount_token AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'amount',
        current_user()
    ) AS DECIMAL(18,2)) AS amount_revealed""",
    "fee_token",
    """CAST(thales_reveal_by_object_and_column_with_user(
        CAST(fee_token AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_internal',
        'fee',
        current_user()
    ) AS DECIMAL(18,2)) AS fee_revealed""",
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

external_token_df = typed_numeric_df.selectExpr(
    "account_id",
    """thales_protect_by_object_and_column_with_external_header(
        CAST(balance_long AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'balance'
    ) AS protected_balance""",
    """thales_protect_by_object_and_column_with_external_header(
        CAST(amount_decimal AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'amount'
    ) AS protected_amount""",
    """thales_protect_by_object_and_column_with_external_header(
        CAST(fee_decimal AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'fee'
    ) AS protected_fee""",
).selectExpr(
    "account_id",
    "protected_balance.protected_value AS balance_token",
    "protected_balance.external_header AS balance_header",
    "protected_amount.protected_value AS amount_token",
    "protected_amount.external_header AS amount_header",
    "protected_fee.protected_value AS fee_token",
    "protected_fee.external_header AS fee_header",
)

display(external_token_df)

# COMMAND ----------

external_reveal_df = external_token_df.selectExpr(
    "account_id",
    """CAST(thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(balance_token AS STRING),
        CAST(balance_header AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'balance',
        current_user()
    ) AS BIGINT) AS balance_revealed""",
    """CAST(thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(amount_token AS STRING),
        CAST(amount_header AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'amount',
        current_user()
    ) AS DECIMAL(18,2)) AS amount_revealed""",
    """CAST(thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(fee_token AS STRING),
        CAST(fee_header AS STRING),
        'nbr',
        'my_catalog.my_schema.account_balance_numbers_protected_external',
        'fee',
        current_user()
    ) AS DECIMAL(18,2)) AS fee_revealed""",
)

display(external_reveal_df)

# COMMAND ----------

print(
    "Numeric smoke test completed. Review the displayed results to confirm the "
    "internal cast-back path and the external protect-plus-header reveal path. "
    "The companion SQL setup script creates the permanent tables and views for "
    "this workflow. The sample data intentionally avoids very short numeric "
    "values because the older CRDP 8090 API can reject protection inputs near "
    "the sub-2-byte limit."
)


