# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster Secure View Example - Numeric Cast-Back Pattern
# MAGIC
# MAGIC This notebook shows the recommended compute-cluster reveal pattern when:
# MAGIC - Java UDFs expect string inputs
# MAGIC - some source columns are stored as numeric types in Delta
# MAGIC - revealed values need to match the target schema again
# MAGIC
# MAGIC In this example:
# MAGIC - `creditcard` is cast back to `DECIMAL(25,0)`
# MAGIC - `creditcardcode` is cast back to `INT`
# MAGIC - `ssn` stays as `STRING`
# MAGIC
# MAGIC This notebook is intended for Databricks compute clusters. It registers the
# MAGIC Java UDFs in the current Spark session, validates the config path, creates
# MAGIC temp reveal views, builds the bulk-array table, and flattens the revealed
# MAGIC arrays back into row form.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_arrays"
ROW_REVEAL_VIEW = "v_plaintext_protected_internal_reveal"
ARRAY_REVEAL_VIEW = "v_plaintext_protected_internal_array_reveal"
FINAL_FLAT_VIEW = "v_plaintext_final_reveal_flat"
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

register_thales_java_udfs()
print("Java UDFs registered successfully.")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW {ROW_REVEAL_VIEW} AS
SELECT
  custid,
  name,
  thales_reveal_by_column_with_user(
    CAST(address AS STRING),
    'char',
    'address',
    current_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_reveal_by_column_with_user(
    CAST(email AS STRING),
    'char',
    'email',
    current_user()
  ) AS email,
  dob,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(creditcard AS STRING),
      'nbr',
      'creditcard',
      current_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(creditcardcode AS STRING),
      'nbr',
      'creditcardcode',
      current_user()
    ) AS INT
  ) AS creditcardcode,
  thales_reveal_by_column_with_user(
    CAST(ssn AS STRING),
    'nbr',
    'ssn',
    current_user()
  ) AS ssn
FROM {SOURCE_TABLE}
""")

spark.sql(f"SELECT * FROM {ROW_REVEAL_VIEW} LIMIT 10").show(truncate=False)

# COMMAND ----------

# Load the protected flat data.
df = spark.table(SOURCE_TABLE)

# Assign deterministic batch ids so bulk arrays are stable across runs.
window_spec = Window.orderBy("custid")
df_with_batch = (
    df.withColumn("row_num", F.row_number().over(window_spec))
      .withColumn("batch_id", F.floor((F.col("row_num") - 1) / BATCH_SIZE))
)

# Glue each row together before collecting to keep column values aligned.
all_columns = df.columns
batch_df = (
    df_with_batch.withColumn("row_struct", F.struct(*all_columns))
      .groupBy("batch_id")
      .agg(F.collect_list("row_struct").alias("all_rows"))
)

final_df = batch_df.select(
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
    F.col("all_rows.ssn").alias("ssn_array")
)

final_df.write.mode("overwrite").saveAsTable(TARGET_TABLE)
print(f"Successfully created {TARGET_TABLE} with batches of {BATCH_SIZE}")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW {ARRAY_REVEAL_VIEW} AS
SELECT
  batch_id,
  custid_array,
  name_array,
  thales_reveal_bulk_by_column_with_user(
    transform(address_array, x -> CAST(x AS STRING)),
    'char',
    'address',
    current_user()
  ) AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  thales_reveal_bulk_by_column_with_user(
    transform(email_array, x -> CAST(x AS STRING)),
    'char',
    'email',
    current_user()
  ) AS email_decrypted,
  dob_array,
  transform(
    thales_reveal_bulk_by_column_with_user(
      transform(creditcard_array, x -> CAST(x AS STRING)),
      'nbr',
      'creditcard',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    thales_reveal_bulk_by_column_with_user(
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      'nbr',
      'creditcardcode',
      current_user()
    ),
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  thales_reveal_bulk_by_column_with_user(
    transform(ssn_array, x -> CAST(x AS STRING)),
    'nbr',
    'ssn',
    current_user()
  ) AS ssn_decrypted
FROM {TARGET_TABLE}
""")

spark.sql(f"SELECT * FROM {ARRAY_REVEAL_VIEW} LIMIT 10").show(truncate=False)

# COMMAND ----------

spark.sql(f"""
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
  SELECT explode(
    arrays_zip(
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
    )
  ) AS exploded
  FROM {ARRAY_REVEAL_VIEW}
)
""")

spark.sql(f"SELECT * FROM {FINAL_FLAT_VIEW} LIMIT 10").show(truncate=False)

# COMMAND ----------

source_count = spark.table(SOURCE_TABLE).count()
final_count = spark.sql(f"SELECT COUNT(*) AS row_count FROM {FINAL_FLAT_VIEW}").collect()[0]["row_count"]

print("Source row count:", source_count)
print("Final flat row count:", final_count)
print(
    "Cast-back secure view example completed. Review the temp views to confirm "
    "the revealed numeric columns match the target schema."
)


