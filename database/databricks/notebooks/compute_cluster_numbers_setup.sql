-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Smoke Test 3 Setup - Numeric Measure Tables
-- MAGIC
-- MAGIC This setup script creates a small plaintext table and sample rows for the
-- MAGIC `databricks_compute_cluster_udf_numbers_smoke_test.py` use case.
-- MAGIC
-- MAGIC Run `databricks_compute_cluster_udf_numbers_smoke_test.py` first in the same
-- MAGIC compute-cluster session. That notebook registers the Java UDFs this setup
-- MAGIC script uses.
-- MAGIC
-- MAGIC This script also includes an optional token table build step that assumes
-- MAGIC the Java UDFs are already registered in the current session.
-- MAGIC
-- MAGIC The sample rows intentionally avoid very short numeric values because the
-- MAGIC older CRDP API on port 8090 can reject protection inputs near the
-- MAGIC sub-2-byte limit.
-- MAGIC
-- MAGIC Numeric tokens are stored as strings and cast back after reveal. This
-- MAGIC mirrors the `test2_castback` pattern and is safer than typed numeric
-- MAGIC token UDFs because it preserves leading zeros.

-- COMMAND ----------

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_plaintext (
  account_id INT NOT NULL,
  balance_long BIGINT,
  amount_decimal DECIMAL(18,2),
  fee_decimal DECIMAL(18,2)
)
USING DELTA;

-- COMMAND ----------

INSERT OVERWRITE my_catalog.my_schema.account_balance_plaintext
SELECT * FROM VALUES
  (101, CAST(1234567890 AS BIGINT), CAST(1250.75 AS DECIMAL(18,2)), CAST(42.50 AS DECIMAL(18,2))),
  (102, CAST(2234567890 AS BIGINT), CAST(9999.99 AS DECIMAL(18,2)), CAST(105.10 AS DECIMAL(18,2))),
  (103, CAST(3234567890 AS BIGINT), CAST(210.99 AS DECIMAL(18,2)), CAST(1000.00 AS DECIMAL(18,2))),
  (104, CAST(4234567890 AS BIGINT), CAST(500000.25 AS DECIMAL(18,2)), CAST(20.01 AS DECIMAL(18,2))),
  (105, CAST(5234567890 AS BIGINT), CAST(77.70 AS DECIMAL(18,2)), CAST(12.34 AS DECIMAL(18,2)))
AS t(account_id, balance_long, amount_decimal, fee_decimal);

SELECT *
FROM my_catalog.my_schema.account_balance_plaintext
ORDER BY account_id;

-- COMMAND ----------

-- Optional: build a token table from the plaintext table.
-- Assumes these UDFs are already registered in the current cluster session
-- by `databricks_compute_cluster_udf_numbers_smoke_test.py`:
--   thales_protect_by_column
--   thales_reveal_by_column_with_user

CREATE OR REPLACE TABLE my_catalog.my_schema.account_balance_tokens
USING DELTA AS
SELECT
  account_id,
  thales_protect_by_column(CAST(balance_long AS STRING), 'nbr', 'balance') AS balance_token,
  thales_protect_by_column(CAST(amount_decimal AS STRING), 'nbr', 'amount') AS amount_token,
  thales_protect_by_column(CAST(fee_decimal AS STRING), 'nbr', 'fee') AS fee_token
FROM my_catalog.my_schema.account_balance_plaintext;

SELECT *
FROM my_catalog.my_schema.account_balance_tokens
ORDER BY account_id;

-- COMMAND ----------

-- Optional: reveal the token table back to numeric values.
-- TEMP VIEW naming note:
-- - this view is session-scoped, so the `temp_` prefix makes that clearer
CREATE OR REPLACE TEMP VIEW temp_v_account_balance_tokens_revealed AS
SELECT
  account_id,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(balance_token AS STRING),
      'nbr',
      'balance',
      current_user()
    ) AS BIGINT
  ) AS balance_revealed,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(amount_token AS STRING),
      'nbr',
      'amount',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS amount_revealed,
  CAST(
    thales_reveal_by_column_with_user(
      CAST(fee_token AS STRING),
      'nbr',
      'fee',
      current_user()
    ) AS DECIMAL(18,2)
  ) AS fee_revealed
FROM my_catalog.my_schema.account_balance_tokens;

SELECT *
FROM temp_v_account_balance_tokens_revealed
ORDER BY account_id;

-- COMMAND ----------

SELECT
  SUM(amount_revealed) AS total_amount,
  AVG(balance_revealed) AS avg_balance,
  SUM(fee_revealed) AS total_fee
FROM temp_v_account_balance_tokens_revealed;
