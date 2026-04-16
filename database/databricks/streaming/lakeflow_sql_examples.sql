-- Lakeflow Declarative Pipelines / DLT-style SQL examples for Thales CRDP
--
-- Recommended governed pattern:
-- - use secured views or UC functions
-- - write into streaming tables or materialized views

-- Example 1: create a streaming table from a tokenized source.
CREATE OR REFRESH STREAMING TABLE customer_tokens_bronze
AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  email_token
FROM STREAM main.raw.customer_tokens;

-- Example 2: create a governed materialized view that reveals email using the
-- secure SQL path.
CREATE OR REFRESH MATERIALIZED VIEW customer_reveal_gold
AS
SELECT
  customer_id,
  first_name,
  last_name,
  customer_status,
  created_ts,
  main.security.thales_crdp_scalar_by_column_with_user(
    email_token,
    'reveal',
    'char',
    'email',
    session_user()
  ) AS email
FROM customer_tokens_bronze;

-- Example 3: array-based pattern.
CREATE OR REFRESH STREAMING TABLE customer_token_arrays_bronze
AS
SELECT
  customer_group_id,
  snapshot_ts,
  email_token_array
FROM STREAM main.raw.customer_token_arrays;

CREATE OR REFRESH MATERIALIZED VIEW customer_array_reveal_gold
AS
SELECT
  customer_group_id,
  snapshot_ts,
  main.security.thales_crdp_bulk_by_column_with_user(
    email_token_array,
    'revealbulk',
    'char',
    'email',
    session_user()
  ) AS email_array
FROM customer_token_arrays_bronze;
