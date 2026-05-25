-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Numbers Setup
-- MAGIC
-- MAGIC This setup script creates the shared numeric workflow used by
-- MAGIC `numbers_smoke_test.py` and the numeric cast-back reveal examples.
-- MAGIC
-- MAGIC This notebook self-registers the object-aware Java UDFs it needs for the
-- MAGIC current Spark session, so it can be run directly on a configured compute
-- MAGIC cluster without first running a separate smoke-test registration notebook.
-- MAGIC
-- MAGIC This script creates:
-- MAGIC
-- MAGIC - `account_balance_numbers`
-- MAGIC - `account_balance_numbers_protected_internal`
-- MAGIC - `account_balance_numbers_protected_external`
-- MAGIC - `account_balance_numbers_protected_none`
-- MAGIC - session temp reveal views for both internal and external table shapes
-- MAGIC - a session temp reveal view for the no-version table shape
-- MAGIC - a persistent array table plus a session temp array reveal view for the internal path
-- MAGIC - a persistent array table plus a session temp array reveal view for the external path
-- MAGIC - a persistent array table plus a session temp array reveal view for the no-version path
-- MAGIC
-- MAGIC The sample rows intentionally avoid very short numeric values because the
-- MAGIC older CRDP API on port 8090 can reject protection inputs near the
-- MAGIC sub-2-byte limit.
-- MAGIC
-- MAGIC Internal-protect flow:
-- MAGIC - protect as `STRING`
-- MAGIC - store protected values in the protected table
-- MAGIC - reveal as `STRING`
-- MAGIC - cast back after reveal
-- MAGIC
-- MAGIC External-protect flow:
-- MAGIC - protect through `thales_protect_by_object_and_column_with_external_header`
-- MAGIC - store both the protected value and the returned sibling header column
-- MAGIC - reveal through `thales_reveal_by_object_and_column_with_external_header_and_user`
-- MAGIC
-- MAGIC None-protect flow:
-- MAGIC - protect through `thales_protect_by_object_and_column`
-- MAGIC - no sibling header columns are stored
-- MAGIC - reveal through `thales_reveal_by_object_and_column_with_user`

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql import types as T
-- MAGIC
-- MAGIC config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
-- MAGIC if not config_path:
-- MAGIC     raise ValueError(
-- MAGIC         "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
-- MAGIC         "Configure the driver and executor env vars before running this setup."
-- MAGIC     )
-- MAGIC
-- MAGIC external_protect_schema = T.StructType(
-- MAGIC     [
-- MAGIC         T.StructField("protected_value", T.StringType(), True),
-- MAGIC         T.StructField("external_header", T.StringType(), True),
-- MAGIC     ]
-- MAGIC )
-- MAGIC
-- MAGIC spark.udf.registerJavaFunction("thales_protect_by_object_and_column", "ThalesCrdpProtectByObjectAndColumnUdf", T.StringType())
-- MAGIC spark.udf.registerJavaFunction("thales_protect_by_object_and_column_with_external_header", "ThalesCrdpProtectByObjectAndColumnWithExternalHeaderUdf", external_protect_schema)
-- MAGIC spark.udf.registerJavaFunction("thales_reveal_by_object_and_column_with_user", "ThalesCrdpRevealByObjectAndColumnWithUserUdf", T.StringType())
-- MAGIC spark.udf.registerJavaFunction("thales_reveal_by_object_and_column_with_external_header_and_user", "ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf", T.StringType())
-- MAGIC spark.udf.registerJavaFunction("thales_reveal_bulk_by_object_and_column_with_user", "ThalesCrdpRevealBulkByObjectAndColumnWithUserUdf", T.ArrayType(T.StringType()))
-- MAGIC spark.udf.registerJavaFunction("thales_reveal_bulk_by_object_and_column_with_external_header_and_user", "ThalesCrdpRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf", T.ArrayType(T.StringType()))
-- MAGIC
-- MAGIC print("Required object-aware Thales Java UDFs registered for numeric setup.")

-- COMMAND ----------

-- Base sample table

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers (
  account_id INT NOT NULL,
  balance_long BIGINT,
  amount_decimal DECIMAL(18,2),
  fee_decimal DECIMAL(18,2)
)
USING DELTA;

-- COMMAND ----------

INSERT OVERWRITE my_catalog.my_schema.account_balance_numbers
SELECT * FROM VALUES
  (101, CAST(1234567890 AS BIGINT), CAST(1250.75 AS DECIMAL(18,2)), CAST(42.50 AS DECIMAL(18,2))),
  (102, CAST(2234567890 AS BIGINT), CAST(9999.99 AS DECIMAL(18,2)), CAST(105.10 AS DECIMAL(18,2))),
  (103, CAST(3234567890 AS BIGINT), CAST(210.99 AS DECIMAL(18,2)), CAST(1000.00 AS DECIMAL(18,2))),
  (104, CAST(4234567890 AS BIGINT), CAST(500000.25 AS DECIMAL(18,2)), CAST(20.01 AS DECIMAL(18,2))),
  (105, CAST(5234567890 AS BIGINT), CAST(77.70 AS DECIMAL(18,2)), CAST(12.34 AS DECIMAL(18,2)))
AS t(account_id, balance_long, amount_decimal, fee_decimal);

SELECT *
FROM my_catalog.my_schema.account_balance_numbers
ORDER BY account_id;

-- COMMAND ----------

-- Internal protected table

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_internal
USING DELTA AS
SELECT
  account_id,
  thales_protect_by_object_and_column(CAST(balance_long AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_internal', 'balance') AS balance_long,
  thales_protect_by_object_and_column(CAST(amount_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_internal', 'amount') AS amount_decimal,
  thales_protect_by_object_and_column(CAST(fee_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_internal', 'fee') AS fee_decimal
FROM my_catalog.my_schema.account_balance_numbers;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_internal
ORDER BY account_id;

-- COMMAND ----------

-- External protected table shape

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_external (
  account_id INT NOT NULL,
  balance_long STRING,
  balance_long_header STRING,
  amount_decimal STRING,
  amount_decimal_header STRING,
  fee_decimal STRING,
  fee_decimal_header STRING
)
USING DELTA;

-- COMMAND ----------

-- External protected table load

INSERT OVERWRITE my_catalog.my_schema.account_balance_numbers_protected_external
SELECT
  account_id,
  protected_balance.protected_value AS balance_long,
  protected_balance.external_header AS balance_long_header,
  protected_amount.protected_value AS amount_decimal,
  protected_amount.external_header AS amount_decimal_header,
  protected_fee.protected_value AS fee_decimal,
  protected_fee.external_header AS fee_decimal_header
FROM (
  SELECT
    account_id,
    thales_protect_by_object_and_column_with_external_header(CAST(balance_long AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_external', 'balance') AS protected_balance,
    thales_protect_by_object_and_column_with_external_header(CAST(amount_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_external', 'amount') AS protected_amount,
    thales_protect_by_object_and_column_with_external_header(CAST(fee_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_external', 'fee') AS protected_fee
  FROM my_catalog.my_schema.account_balance_numbers
) s;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_external
ORDER BY account_id;

-- COMMAND ----------

-- None protected table load

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_none
USING DELTA AS
SELECT
  account_id,
  thales_protect_by_object_and_column(CAST(balance_long AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_none', 'balance') AS balance_long,
  thales_protect_by_object_and_column(CAST(amount_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_none', 'amount') AS amount_decimal,
  thales_protect_by_object_and_column(CAST(fee_decimal AS STRING), 'nbr', 'my_catalog.my_schema.account_balance_numbers_protected_none', 'fee') AS fee_decimal
FROM my_catalog.my_schema.account_balance_numbers;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_none
ORDER BY account_id;

-- COMMAND ----------

-- Internal row reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_internal_revealed AS
SELECT
  account_id,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(balance_long AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal',
      'balance',
      current_user()
    ) AS BIGINT
  ) AS balance_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(amount_decimal AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal',
      'amount',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS amount_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(fee_decimal AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal',
      'fee',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS fee_revealed
FROM my_catalog.my_schema.account_balance_numbers_protected_internal;

SELECT *
FROM v_account_balance_numbers_protected_internal_revealed
ORDER BY account_id;

-- COMMAND ----------

-- External row reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_external_revealed AS
SELECT
  account_id,
  CAST(
    thales_reveal_by_object_and_column_with_external_header_and_user(
      CAST(balance_long AS STRING),
      CAST(balance_long_header AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external',
      'balance',
      current_user()
    ) AS BIGINT
  ) AS balance_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_external_header_and_user(
      CAST(amount_decimal AS STRING),
      CAST(amount_decimal_header AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external',
      'amount',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS amount_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_external_header_and_user(
      CAST(fee_decimal AS STRING),
      CAST(fee_decimal_header AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external',
      'fee',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS fee_revealed
FROM my_catalog.my_schema.account_balance_numbers_protected_external;

SELECT *
FROM v_account_balance_numbers_protected_external_revealed
ORDER BY account_id;

-- COMMAND ----------

-- None row reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_none_revealed AS
SELECT
  account_id,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(balance_long AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none',
      'balance',
      current_user()
    ) AS BIGINT
  ) AS balance_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(amount_decimal AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none',
      'amount',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS amount_revealed,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(fee_decimal AS STRING),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none',
      'fee',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS fee_revealed
FROM my_catalog.my_schema.account_balance_numbers_protected_none;

SELECT *
FROM v_account_balance_numbers_protected_none_revealed
ORDER BY account_id;

-- COMMAND ----------

-- Internal array table

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_internal_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY account_id) AS row_num
  FROM my_catalog.my_schema.account_balance_numbers_protected_internal
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'account_id', account_id,
      'balance_long', balance_long,
      'amount_decimal', amount_decimal,
      'fee_decimal', fee_decimal
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.account_id) AS account_id_array,
  collect_list(row_struct.balance_long) AS balance_long_array,
  collect_list(row_struct.amount_decimal) AS amount_decimal_array,
  collect_list(row_struct.fee_decimal) AS fee_decimal_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_internal_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- External array table

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_external_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY account_id) AS row_num
  FROM my_catalog.my_schema.account_balance_numbers_protected_external
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'account_id', account_id,
      'balance_long', balance_long,
      'balance_long_header', balance_long_header,
      'amount_decimal', amount_decimal,
      'amount_decimal_header', amount_decimal_header,
      'fee_decimal', fee_decimal,
      'fee_decimal_header', fee_decimal_header
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.account_id) AS account_id_array,
  collect_list(row_struct.balance_long) AS balance_long_array,
  collect_list(row_struct.balance_long_header) AS balance_long_header_array,
  collect_list(row_struct.amount_decimal) AS amount_decimal_array,
  collect_list(row_struct.amount_decimal_header) AS amount_decimal_header_array,
  collect_list(row_struct.fee_decimal) AS fee_decimal_array,
  collect_list(row_struct.fee_decimal_header) AS fee_decimal_header_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_external_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- None array table

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_numbers_protected_none_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY account_id) AS row_num
  FROM my_catalog.my_schema.account_balance_numbers_protected_none
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'account_id', account_id,
      'balance_long', balance_long,
      'amount_decimal', amount_decimal,
      'fee_decimal', fee_decimal
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.account_id) AS account_id_array,
  collect_list(row_struct.balance_long) AS balance_long_array,
  collect_list(row_struct.amount_decimal) AS amount_decimal_array,
  collect_list(row_struct.fee_decimal) AS fee_decimal_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.account_balance_numbers_protected_none_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- Internal array reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_internal_array_revealed AS
SELECT
  batch_id,
  account_id_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(balance_long_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal_arrays',
      'balance',
      current_user()
    ),
    x -> CAST(x AS BIGINT)
  ) AS balance_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(amount_decimal_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal_arrays',
      'amount',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS amount_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(fee_decimal_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_internal_arrays',
      'fee',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS fee_revealed_array
FROM my_catalog.my_schema.account_balance_numbers_protected_internal_arrays;

SELECT *
FROM v_account_balance_numbers_protected_internal_array_revealed
ORDER BY batch_id;

-- COMMAND ----------

-- External array reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_external_array_revealed AS
SELECT
  batch_id,
  account_id_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
      transform(balance_long_array, x -> CAST(x AS STRING)),
      transform(balance_long_header_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external_arrays',
      'balance',
      current_user()
    ),
    x -> CAST(x AS BIGINT)
  ) AS balance_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
      transform(amount_decimal_array, x -> CAST(x AS STRING)),
      transform(amount_decimal_header_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external_arrays',
      'amount',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS amount_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
      transform(fee_decimal_array, x -> CAST(x AS STRING)),
      transform(fee_decimal_header_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_external_arrays',
      'fee',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS fee_revealed_array
FROM my_catalog.my_schema.account_balance_numbers_protected_external_arrays;

SELECT *
FROM v_account_balance_numbers_protected_external_array_revealed
ORDER BY batch_id;

-- COMMAND ----------

-- None array reveal view

CREATE OR REPLACE TEMP VIEW v_account_balance_numbers_protected_none_array_revealed AS
SELECT
  batch_id,
  account_id_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(balance_long_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none_arrays',
      'balance',
      current_user()
    ),
    x -> CAST(x AS BIGINT)
  ) AS balance_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(amount_decimal_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none_arrays',
      'amount',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS amount_revealed_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(fee_decimal_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.account_balance_numbers_protected_none_arrays',
      'fee',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(18,2))
  ) AS fee_revealed_array
FROM my_catalog.my_schema.account_balance_numbers_protected_none_arrays;

SELECT *
FROM v_account_balance_numbers_protected_none_array_revealed
ORDER BY batch_id;

-- COMMAND ----------

-- Example aggregate against the internal row reveal view

SELECT
  SUM(amount_revealed) AS total_amount,
  AVG(balance_revealed) AS avg_balance,
  SUM(fee_revealed) AS total_fee
FROM v_account_balance_numbers_protected_internal_revealed;

-- COMMAND ----------

-- Grants
-- Note:
-- - The protected tables are persistent and can be granted.
-- - The reveal views in this compute-cluster notebook are TEMP VIEW objects
--   because they depend on session-registered Java UDFs.
-- - TEMP VIEW objects cannot be granted. For persistent governed reveal views,
--   use the SQL Warehouse / Unity Catalog function path instead.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC grant_statements = [
-- MAGIC     "GRANT USE CATALOG ON CATALOG my_catalog TO `thales_cluster_deployers`",
-- MAGIC     "GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_internal TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_external TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_none TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_internal_arrays TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_external_arrays TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_numbers_protected_none_arrays TO `thales_cluster_deployers`",
-- MAGIC     "GRANT USE CATALOG ON CATALOG my_catalog TO `analyst`",
-- MAGIC     "GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `analyst`",
-- MAGIC ]
-- MAGIC
-- MAGIC for statement in grant_statements:
-- MAGIC     try:
-- MAGIC         spark.sql(statement)
-- MAGIC         print(f\"Applied: {statement}\")
-- MAGIC     except Exception as exc:
-- MAGIC         print(f\"Skipped grant: {statement}\")
-- MAGIC         print(f\"Reason: {exc}\")

-- COMMAND ----------

-- Validation checks
SELECT 'base' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.account_balance_numbers
UNION ALL
SELECT 'internal_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.account_balance_numbers_protected_internal
UNION ALL
SELECT 'external_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.account_balance_numbers_protected_external
UNION ALL
SELECT 'none_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.account_balance_numbers_protected_none
UNION ALL
SELECT 'internal_row_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_internal_revealed
UNION ALL
SELECT 'external_row_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_external_revealed
UNION ALL
SELECT 'none_row_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_none_revealed
UNION ALL
SELECT 'internal_array_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_internal_array_revealed
UNION ALL
SELECT 'external_array_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_external_array_revealed
UNION ALL
SELECT 'none_array_view' AS object_type, COUNT(*) AS row_count FROM v_account_balance_numbers_protected_none_array_revealed
ORDER BY object_type;

-- COMMAND ----------

SELECT *
FROM (
  SELECT 'internal_row' AS example_type, account_id, balance_revealed, amount_revealed, fee_revealed
  FROM v_account_balance_numbers_protected_internal_revealed
  ORDER BY account_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT 'external_row' AS example_type, account_id, balance_revealed, amount_revealed, fee_revealed
  FROM v_account_balance_numbers_protected_external_revealed
  ORDER BY account_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT 'none_row' AS example_type, account_id, balance_revealed, amount_revealed, fee_revealed
  FROM v_account_balance_numbers_protected_none_revealed
  ORDER BY account_id
  LIMIT 5
)
ORDER BY example_type, account_id;

-- COMMAND ----------

SELECT *
FROM (
  SELECT
    'internal_array' AS example_type,
    batch_id,
    size(account_id_array) AS account_count,
    size(balance_revealed_array) AS balance_count,
    size(amount_revealed_array) AS amount_count,
    size(fee_revealed_array) AS fee_count
  FROM v_account_balance_numbers_protected_internal_array_revealed
  ORDER BY batch_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'external_array' AS example_type,
    batch_id,
    size(account_id_array) AS account_count,
    size(balance_revealed_array) AS balance_count,
    size(amount_revealed_array) AS amount_count,
    size(fee_revealed_array) AS fee_count
  FROM v_account_balance_numbers_protected_external_array_revealed
  ORDER BY batch_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'none_array' AS example_type,
    batch_id,
    size(account_id_array) AS account_count,
    size(balance_revealed_array) AS balance_count,
    size(amount_revealed_array) AS amount_count,
    size(fee_revealed_array) AS fee_count
  FROM v_account_balance_numbers_protected_none_array_revealed
  ORDER BY batch_id
  LIMIT 5
)
ORDER BY example_type, batch_id;

