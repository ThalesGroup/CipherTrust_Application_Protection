-- Databricks SQL Warehouse secure reveal view templates for Thales CRDP v1
--
-- Purpose:
-- - hide the reveal_user parameter from end users
-- - inject Databricks session identity with session_user()
-- - expose curated reveal views for BI, dashboards, and analysts
--
-- Assumptions:
-- - the Unity Catalog functions already exist in main.security
-- - source tokenized tables exist in main.raw
-- - the most common pattern is one protected value per row, not arrays
--
-- Update table names, column names, and namespaces to match the target
-- environment before running.
--
-- Example row-based source shape:
--
--   main.raw.customer_tokens
--   +-------------+------------+-----------+-----------------+---------------------+----------------+-------------+
--   | customer_id | first_name | last_name | customer_status | created_ts          | email_token    | ssn_token   |
--   +-------------+------------+-----------+-----------------+---------------------+----------------+-------------+
--   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | A9K2...        | N5P1...     |
--   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | B1M4...        | Q4R8...     |
--   +-------------+------------+-----------+-----------------+---------------------+----------------+-------------+
--
-- Example row-based view result:
--
--   SELECT * FROM main.security.v_customer_reveal LIMIT 2;
--
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+-------------+
--   | customer_id | first_name | last_name | customer_status | created_ts          | email             | ssn         |
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+-------------+
--   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | alice@example.com | 123456789   |
--   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | bob@example.com   | 987654321   |
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+-------------+
--
-- Example array-based source shape:
--
--   main.raw.customer_token_arrays
--   +-------------------+---------------------+----------------------------------------+
--   | customer_group_id | snapshot_ts         | email_token_array                      |
--   +-------------------+---------------------+----------------------------------------+
--   | north-east-001    | 2026-04-07 09:00:00 | ["A9K2...","B1M4...","C7P8..."]        |
--   | north-east-002    | 2026-04-07 09:00:00 | ["D4Q1...","E6R3..."]                  |
--   +-------------------+---------------------+----------------------------------------+
--
-- Example array-based view result:
--
--   SELECT * FROM main.security.v_customer_array_reveal LIMIT 2;
--
--   +-------------------+---------------------+----------------------------------------------------------+
--   | customer_group_id | snapshot_ts         | email_array                                              |
--   +-------------------+---------------------+----------------------------------------------------------+
--   | north-east-001    | 2026-04-07 09:00:00 | ["alice@example.com","bob@example.com","carol@example.com"] |
--   | north-east-002    | 2026-04-07 09:00:00 | ["dave@example.com","erin@example.com"]                  |
--   +-------------------+---------------------+----------------------------------------------------------+

CREATE OR REPLACE VIEW main.security.v_customer_reveal AS
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
  ) AS email,
  main.security.thales_crdp_scalar_by_column_with_user(
    ssn_token,
    'reveal',
    'nbr',
    'ssn',
    session_user()
  ) AS ssn
FROM main.raw.customer_tokens;

CREATE OR REPLACE VIEW main.security.v_employee_reveal AS
SELECT
  employee_id,
  employee_name,
  department_name,
  hire_ts,
  main.security.thales_crdp_scalar_by_column_with_user(
    work_email_token,
    'reveal',
    'char',
    'work_email',
    session_user()
  ) AS work_email,
  main.security.thales_crdp_scalar_by_column_with_user(
    national_id_token,
    'reveal',
    'nbr',
    'national_id',
    session_user()
  ) AS national_id
FROM main.raw.employee_tokens;

-- Optional array-based example for tables that intentionally store batches in a
-- single ARRAY<STRING> column. This is less common for BI-facing tables.

CREATE OR REPLACE VIEW main.security.v_customer_array_reveal AS
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
FROM main.raw.customer_token_arrays;

-- Optional validation queries:
--
-- SELECT * FROM main.security.v_customer_reveal LIMIT 10;
-- SELECT * FROM main.security.v_employee_reveal LIMIT 10;
-- SELECT * FROM main.security.v_customer_array_reveal LIMIT 10;

-- Recommended governance notes:
--
-- 1. Grant BI users access to the secured views instead of direct access to
--    the *_with_user functions.
-- 2. Keep the source token tables in a more restricted schema if possible.
-- 3. Use one view per business-safe reveal use case so column/profile choices
--    remain explicit and governed.
-- 4. For normal row-based tables, select the business columns you want to
--    preserve and only replace the token columns with revealed outputs.
-- SAMPLE: secure view patterns layered on top of previously created UC functions
