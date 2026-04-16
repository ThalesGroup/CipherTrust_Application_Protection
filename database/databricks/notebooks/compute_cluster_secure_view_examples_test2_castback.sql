-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Thales CRDP Compute Cluster Secure View Example - Numeric Cast-Back Pattern (SQL)
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - use the existing compute-cluster Java UDFs
-- MAGIC - keep the UDF boundary string-based where needed
-- MAGIC - cast revealed values back to the table schema for numeric columns
-- MAGIC
-- MAGIC This is the version to use when the protected table contains columns such as:
-- MAGIC - `creditcard DECIMAL(25,0)`
-- MAGIC - `creditcardcode INT`
-- MAGIC
-- MAGIC In this example:
-- MAGIC - `creditcard` is revealed as string and cast back to `DECIMAL(25,0)`
-- MAGIC - `creditcardcode` is revealed as string and cast back to `INT`
-- MAGIC - `ssn` remains `STRING`

-- COMMAND ----------

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_internal_reveal AS
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
FROM my_catalog.my_schema.plaintext_protected_internal;

SELECT *
FROM v_plaintext_protected_internal_reveal
LIMIT 10;

-- COMMAND ----------

-- MAGIC %python
SOURCE_TABLE = "my_catalog.my_schema.plaintext_protected_internal"
TARGET_TABLE = "my_catalog.my_schema.plaintext_protected_internal_arrays"
BATCH_SIZE = 1000

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Load the protected flat table.
df = spark.table(SOURCE_TABLE)

# Assign deterministic batch ids so the bulk arrays stay aligned.
window_spec = Window.orderBy("custid")
df_with_batch = (
    df.withColumn("row_num", F.row_number().over(window_spec))
      .withColumn("batch_id", F.floor((F.col("row_num") - 1) / BATCH_SIZE))
)

# Glue each row together before collecting so column values remain aligned.
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

-- COMMAND ----------

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_internal_array_reveal AS
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
FROM my_catalog.my_schema.plaintext_protected_internal_arrays;

SELECT *
FROM v_plaintext_protected_internal_array_reveal
LIMIT 10;

-- COMMAND ----------

CREATE OR REPLACE TEMP VIEW v_plaintext_final_reveal_flat AS
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
  FROM v_plaintext_protected_internal_array_reveal
);

SELECT *
FROM v_plaintext_final_reveal_flat
LIMIT 10;

