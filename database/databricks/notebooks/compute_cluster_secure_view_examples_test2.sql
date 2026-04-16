-- DEPRECATED:
-- Use `compute_cluster_secure_view_examples_test2_castback.py` or
-- `compute_cluster_secure_view_examples_test2_castback.sql` instead.
--
-- This older example does not implement the final cast-back pattern for
-- numeric schema columns after reveal.

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_internal_reveal AS
SELECT
  custid ,
  name ,
  thales_reveal_by_column_with_user(
    CAST(address AS STRING),
    'char',
    'address',
    current_user()
  ) AS address ,
  city ,
  state ,
    zip ,
  phone ,
  thales_reveal_by_column_with_user(
    CAST(email AS STRING),
    'char',
    'email',
    current_user()
  ) AS email,
    dob ,
  thales_reveal_by_column_with_user(
    CAST(creditcard AS STRING),
    'nbr',
    'creditcard',
    current_user()
  ) as creditcard  ,
  thales_reveal_by_column_with_user(
    CAST(creditcardcode AS STRING),
    'nbr',
    'creditcardcode',
    current_user()
  ) as creditcardcode ,
  thales_reveal_by_column_with_user(
    CAST(ssn AS STRING),
    'nbr',
    'ssn',
    current_user()
  ) as ssn 
  
FROM my_catalog.my_schema.plaintext_protected_internal;

# Configuration variables
SOURCE_TABLE = "my_catalog.my_schema.plaintext_protected_internal"
TARGET_TABLE = "my_catalog.my_schema.plaintext_protected_internal_arrays"
BATCH_SIZE = 1000 # Optimized for Thales bulk processing

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 1. Load the flat data
df = spark.table(SOURCE_TABLE)

# 2. Assign a Batch ID using a Row Number
# We use Window.orderBy("custid") to ensure a stable sort order
window_spec = Window.orderBy("custid")
df_with_batch = df.withColumn("row_num", F.row_number().over(window_spec)) \
                  .withColumn("batch_id", F.floor((F.col("row_num") - 1) / BATCH_SIZE))

# 3. Use Struct to "glue" the row together before collecting
# This prevents columns from getting misaligned in the array
all_columns = df.columns
df_grouped = df_with_batch.withColumn("row_struct", F.struct(*all_columns))

# 4. Aggregate into arrays
batch_df = df_grouped.groupBy("batch_id").agg(
    F.collect_list("row_struct").alias("all_rows")
)

# 5. Extract specific arrays back to top-level columns for the View
# Syntax: all_rows.column_name creates an array of that column
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

# 6. Write to the Data Warehouse
final_df.write.mode("overwrite").saveAsTable(TARGET_TABLE)

print(f"Successfully created {TARGET_TABLE} with batches of {BATCH_SIZE}")

%sql
CREATE OR REPLACE TEMP VIEW v_plaintext_protected_interna_array_reveal AS
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
FROM my_catalog.my_schema.plaintext_protected_internal_arrays;

%sql
-- This view "unzips" the arrays back into standard rows
CREATE OR REPLACE TEMP VIEW v_plaintext_final_reveal_flat AS
SELECT 
  exploded.custid_array as custid,
  exploded.name_array as name,
  exploded.address_decrypted as address,
  exploded.city_array as city,
  exploded.state_array as state,
  exploded.zip_array as zip,
  exploded.phone_array as phone,
  exploded.email_decrypted as email,
  exploded.dob_array as dob,
  exploded.creditcard_decrypted as creditcard,
  exploded.creditcardcode_decrypted as creditcardcode,
  exploded.ssn_decrypted as ssn
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
  FROM v_plaintext_protected_interna_array_reveal
);

-- Test the final result
SELECT * FROM v_plaintext_final_reveal_flat LIMIT 10;

