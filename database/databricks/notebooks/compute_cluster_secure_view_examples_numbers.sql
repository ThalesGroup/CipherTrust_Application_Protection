-- DEPRECATED:
-- Use `databricks_compute_cluster_udf_numbers_smoke_test.py` and
-- `compute_cluster_numbers_setup.sql` instead.
--
-- This file shows the older typed-numeric approach and is no longer the
-- recommended compute-cluster pattern.

CREATE OR REPLACE TEMP VIEW v_account_balances_secure AS
SELECT
  account_id,
  thales_reveal_long_by_column_with_user(balance_token, 'balance', current_user()) AS balance,
  CAST(thales_reveal_by_column_with_user(amount_token, 'nbr', 'amount', current_user()) AS DECIMAL(18,2)) AS amount,
  CAST(thales_reveal_by_column_with_user(fee_token, 'nbr', 'fee', current_user()) AS DECIMAL(18,2)) AS fee
FROM my_catalog.my_schema.account_balance_tokens;

SELECT *
FROM v_account_balances_secure
LIMIT 10;

SELECT
  SUM(amount) AS total_amount,
  AVG(balance) AS avg_balance,
  SUM(fee) AS total_fee
FROM v_account_balances_secure;

-- Example protect query for numeric measure columns.
-- Balance uses the typed LONG adapter.
-- Amount and fee are protected through the string-based nbr path.
CREATE OR REPLACE TEMP VIEW v_account_balances_protected AS
SELECT
  account_id,
  thales_protect_long_by_column(balance, 'balance') AS balance_token,
  thales_protect_by_column(CAST(amount AS STRING), 'nbr', 'amount') AS amount_token,
  thales_protect_by_column(CAST(fee AS STRING), 'nbr', 'fee') AS fee_token
FROM my_catalog.my_schema.account_balance_plaintext;

SELECT *
FROM v_account_balances_protected
LIMIT 10;
