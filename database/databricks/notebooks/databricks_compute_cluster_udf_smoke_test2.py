# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster Smoke Test 2
# MAGIC
# MAGIC This notebook is aligned to `compute_cluster_secure_view_examples_test2.sql`.
# MAGIC It registers the Java UDFs, recreates the secure reveal views, builds the
# MAGIC batched array table, and runs a few smoke-test queries against the objects
# MAGIC in that flow.
# MAGIC
# MAGIC Before running:
# MAGIC
# MAGIC - Attach the desired shaded jar to the compute cluster
# MAGIC - Set `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Set `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Confirm the configured `udfConfig.properties` matches the columns/profiles

# COMMAND ----------

# NOTE:
# Use `compute_cluster_secure_view_examples_test2_castback.py` or
# `compute_cluster_secure_view_examples_test2_castback.sql` for the current
# supported numeric-schema flow. The older non-castback
# `compute_cluster_secure_view_examples_test2.sql` is retained only as a
# legacy/example artifact.

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_arrays"
ROW_REVEAL_VIEW = f"{CATALOG}.{SCHEMA}.v_plaintext_protected_internal_reveal"
ARRAY_REVEAL_VIEW = f"{CATALOG}.{SCHEMA}.v_plaintext_protected_interna_array_reveal"
FINAL_FLAT_VIEW = f"{CATALOG}.{SCHEMA}.v_plaintext_final_reveal_flat"
BATCH_SIZE = 1000

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

def register_thales_java_udfs():
    spark.udf.registerJavaFunction("thales_protect", "ThalesCrdpProtectUdf", T.StringType())
    spark.udf.registerJavaFunction("thales_protect_by_column", "ThalesCrdpProtectByColumnUdf", T.StringType())
    spark.udf.registerJavaFunction("thales_reveal", "ThalesCrdpRevealUdf", T.StringType())
    spark.udf.registerJavaFunction("thales_reveal_by_column", "ThalesCrdpRevealByColumnUdf", T.StringType())
    spark.udf.registerJavaFunction("thales_reveal_with_user", "ThalesCrdpRevealWithUserUdf", T.StringType())
    spark.udf.registerJavaFunction(
        "thales_reveal_by_column_with_user",
        "ThalesCrdpRevealByColumnWithUserUdf",
        T.StringType(),
    )

    spark.udf.registerJavaFunction(
        "thales_protect_bulk",
        "ThalesCrdpProtectBulkUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_protect_bulk_by_column",
        "ThalesCrdpProtectBulkByColumnUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_bulk",
        "ThalesCrdpRevealBulkUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_bulk_with_user",
        "ThalesCrdpRevealBulkWithUserUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_bulk_by_column",
        "ThalesCrdpRevealBulkByColumnUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_bulk_by_column_with_user",
        "ThalesCrdpRevealBulkByColumnWithUserUdf",
        T.ArrayType(T.StringType()),
    )

    spark.udf.registerJavaFunction(
        "thales_bulk_protect_char",
        "ThalesBulkProtectCharUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_bulk_reveal_char",
        "ThalesBulkRevealCharUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_bulk_protect_nbr",
        "ThalesBulkProtectNbrUdf",
        T.ArrayType(T.StringType()),
    )
    spark.udf.registerJavaFunction(
        "thales_bulk_reveal_nbr",
        "ThalesBulkRevealNbrUdf",
        T.ArrayType(T.StringType()),
    )

    spark.udf.registerJavaFunction(
        "thales_protect_integer_by_column",
        "ThalesCrdpProtectIntegerByColumnUdf",
        T.IntegerType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_integer_by_column_with_user",
        "ThalesCrdpRevealIntegerByColumnWithUserUdf",
        T.IntegerType(),
    )
    spark.udf.registerJavaFunction(
        "thales_protect_long_by_column",
        "ThalesCrdpProtectLongByColumnUdf",
        T.LongType(),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_long_by_column_with_user",
        "ThalesCrdpRevealLongByColumnWithUserUdf",
        T.LongType(),
    )
    spark.udf.registerJavaFunction(
        "thales_protect_decimal_by_column",
        "ThalesCrdpProtectDecimalByColumnUdf",
        T.DecimalType(38, 18),
    )
    spark.udf.registerJavaFunction(
        "thales_reveal_decimal_by_column_with_user",
        "ThalesCrdpRevealDecimalByColumnWithUserUdf",
        T.DecimalType(38, 18),
    )

register_thales_java_udfs()
print("Thales Java UDFs registered successfully.")

# COMMAND ----------

source_df = spark.table(SOURCE_TABLE)
print(f"Loaded {SOURCE_TABLE} with {source_df.count()} rows")
display(source_df.limit(10))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {ROW_REVEAL_VIEW} AS
    SELECT
      custid,
      name,
      thales_reveal_by_column_with_user(CAST(address AS STRING), 'char', 'address', current_user()) AS address,
      city,
      state,
      zip,
      phone,
      thales_reveal_by_column_with_user(CAST(email AS STRING), 'char', 'email', current_user()) AS email,
      dob,
      thales_reveal_by_column_with_user(CAST(creditcard AS STRING), 'nbr', 'creditcard', current_user()) AS creditcard,
      thales_reveal_by_column_with_user(CAST(creditcardcode AS STRING), 'nbr', 'creditcardcode', current_user()) AS creditcardcode,
      thales_reveal_by_column_with_user(CAST(ssn AS STRING), 'nbr', 'ssn', current_user()) AS ssn
    FROM {SOURCE_TABLE}
    """
)

print(f"Created or replaced {ROW_REVEAL_VIEW}")
display(spark.table(ROW_REVEAL_VIEW).limit(10))

# COMMAND ----------

# Direct literal round-trip diagnostics to separate current-code behavior
# from any issues in pre-existing protected table data.
spark.sql(
    """
    SELECT
      'alice@example.com' AS original_email,
      thales_protect_by_column(CAST('alice@example.com' AS STRING), 'char', 'email') AS email_token,
      thales_reveal_by_column_with_user(
        thales_protect_by_column(CAST('alice@example.com' AS STRING), 'char', 'email'),
        'char',
        'email',
        current_user()
      ) AS email_round_trip
    """
).show(truncate=False)

spark.sql(
    """
    SELECT
      '123-45-6789' AS original_ssn,
      thales_protect_by_column(CAST('123-45-6789' AS STRING), 'nbr', 'ssn') AS ssn_token,
      thales_reveal_by_column_with_user(
        thales_protect_by_column(CAST('123-45-6789' AS STRING), 'nbr', 'ssn'),
        'nbr',
        'ssn',
        current_user()
      ) AS ssn_round_trip
    """
).show(truncate=False)

spark.sql(
    """
    SELECT
      '4111111111111111' AS original_creditcard,
      thales_protect_by_column(CAST('4111111111111111' AS STRING), 'nbr', 'creditcard') AS creditcard_token,
      thales_reveal_by_column_with_user(
        thales_protect_by_column(CAST('4111111111111111' AS STRING), 'nbr', 'creditcard'),
        'nbr',
        'creditcard',
        current_user()
      ) AS creditcard_round_trip
    """
).show(truncate=False)

# COMMAND ----------

# Typed numeric scalar diagnostics for true measure columns.
spark.sql(
    """
    SELECT
      CAST(1234567890 AS BIGINT) AS original_balance,
      thales_protect_long_by_column(CAST(1234567890 AS BIGINT), 'balance') AS balance_token,
      thales_reveal_long_by_column_with_user(
        thales_protect_long_by_column(CAST(1234567890 AS BIGINT), 'balance'),
        'balance',
        current_user()
      ) AS balance_round_trip
    """
).show(truncate=False)

# COMMAND ----------

window_spec = Window.orderBy("custid")
all_columns = source_df.columns

batched_df = (
    source_df
    .withColumn("row_num", F.row_number().over(window_spec))
    .withColumn("batch_id", F.floor((F.col("row_num") - 1) / F.lit(BATCH_SIZE)))
    .withColumn("row_struct", F.struct(*all_columns))
)

array_df = batched_df.groupBy("batch_id").agg(F.collect_list("row_struct").alias("all_rows")).select(
    F.col("batch_id"),
    F.col("all_rows.custid").alias("custid_array"),
    F.col("all_rows.name").alias("name_array"),
    F.col("all_rows.address").alias("address_array"),
    F.col("all_rows.city").alias("city_array"),
    F.col("all_rows.state").alias("state_array"),
    F.col("all_rows.zip").alias("zip_array"),
    F.col("all_rows.phone").alias("phone_array"),
    F.col("all_rows.email").alias("email_array"),
    F.col("all_rows.dob").alias("dob_array"),
    F.col("all_rows.creditcard").alias("creditcard_array"),
    F.col("all_rows.creditcardcode").alias("creditcardcode_array"),
    F.col("all_rows.ssn").alias("ssn_array"),
)

array_df.write.mode("overwrite").saveAsTable(TARGET_TABLE)
print(f"Created or replaced {TARGET_TABLE} with batch size {BATCH_SIZE}")
display(spark.table(TARGET_TABLE).limit(10))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {ARRAY_REVEAL_VIEW} AS
    SELECT
      batch_id,
      custid_array,
      name_array,
      thales_reveal_bulk_by_column_with_user(transform(address_array, x -> CAST(x AS STRING)), 'char', 'address', current_user()) AS address_decrypted,
      city_array,
      state_array,
      zip_array,
      phone_array,
      thales_reveal_bulk_by_column_with_user(transform(email_array, x -> CAST(x AS STRING)), 'char', 'email', current_user()) AS email_decrypted,
      dob_array,
      thales_reveal_bulk_by_column_with_user(transform(creditcard_array, x -> CAST(x AS STRING)), 'nbr', 'creditcard', current_user()) AS creditcard_decrypted,
      thales_reveal_bulk_by_column_with_user(transform(creditcardcode_array, x -> CAST(x AS STRING)), 'nbr', 'creditcardcode', current_user()) AS creditcardcode_decrypted,
      thales_reveal_bulk_by_column_with_user(transform(ssn_array, x -> CAST(x AS STRING)), 'nbr', 'ssn', current_user()) AS ssn_decrypted
    FROM {TARGET_TABLE}
    """
)

print(f"Created or replaced {ARRAY_REVEAL_VIEW}")
display(spark.table(ARRAY_REVEAL_VIEW).limit(10))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {FINAL_FLAT_VIEW} AS
    SELECT
      exploded.custid_array AS custid,
      exploded.name_array AS name,
      exploded.address_decrypted AS address,
      exploded.city_array AS city,
      exploded.state_array AS state,
      exploded.zip_array AS zip,
      exploded.phone_array AS phone,
      exploded.email_decrypted AS email,
      exploded.dob_array AS dob,
      exploded.creditcard_decrypted AS creditcard,
      exploded.creditcardcode_decrypted AS creditcardcode,
      exploded.ssn_decrypted AS ssn
    FROM (
      SELECT explode(arrays_zip(
        custid_array,
        name_array,
        address_decrypted,
        city_array,
        state_array,
        zip_array,
        phone_array,
        email_decrypted,
        dob_array,
        creditcard_decrypted,
        creditcardcode_decrypted,
        ssn_decrypted
      )) AS exploded
      FROM {ARRAY_REVEAL_VIEW}
    )
    """
)

print(f"Created or replaced {FINAL_FLAT_VIEW}")
display(spark.table(FINAL_FLAT_VIEW).limit(10))

# COMMAND ----------

spark.sql(f"SELECT COUNT(*) AS source_rows FROM {SOURCE_TABLE}").show()
spark.sql(f"SELECT COUNT(*) AS row_reveal_rows FROM {ROW_REVEAL_VIEW}").show()
spark.sql(f"SELECT COUNT(*) AS final_flat_rows FROM {FINAL_FLAT_VIEW}").show()

# COMMAND ----------

spark.sql(
    f"""
    SELECT
      custid,
      name,
      email,
      creditcard,
      ssn
    FROM {FINAL_FLAT_VIEW}
    ORDER BY custid
    LIMIT 20
    """
).show(truncate=False)

# COMMAND ----------

print(
    "Smoke test 2 completed. Review the views and row counts to confirm "
    "UDF registration, secure reveal behavior, batched bulk reveal, and final flat output."
)

