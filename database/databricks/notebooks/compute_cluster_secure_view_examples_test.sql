-- DEPRECATED:
-- Use `compute_cluster_secure_view_examples_test2_castback.py` or
-- `compute_cluster_secure_view_examples_test2_castback.sql` instead.
--
-- This is an earlier example script and does not reflect the final cast-back
-- numeric handling pattern used for the supported compute-cluster flow.
--
-- Databricks compute-cluster SQL examples for governed reveal wrappers
--
-- Purpose:
-- - wrap Java UDF registrations with SQL views
-- - inject current_user() or session_user() in SQL
-- - avoid exposing reveal_user as a free-form parameter in analyst queries
--
-- Assumptions:
-- - the Java UDFs have already been registered in the current Spark session
-- - source tokenized tables are available in the metastore
--
-- TEMP VIEW versus VIEW:
-- - TEMP VIEW exists only for the current Spark session/cluster session
-- - VIEW is persisted in a catalog/schema and can be reused later
-- - use TEMP VIEW for quick notebook testing
-- - use CREATE OR REPLACE VIEW for shared governed objects
--
-- Example row-based source shape:
--
--   main.raw.customer_tokens
--   +-------------+------------+-----------+-----------------+---------------------+----------------+
--   | customer_id | first_name | last_name | customer_status | created_ts          | email_token    |
--   +-------------+------------+-----------+-----------------+---------------------+----------------+
--   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | A9K2...        |
--   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | B1M4...        |
--   +-------------+------------+-----------+-----------------+---------------------+----------------+
--
-- Example row-based view result:
--
--   SELECT * FROM v_customer_reveal LIMIT 2;
--
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+
--   | customer_id | first_name | last_name | customer_status | created_ts          | email             |
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+
--   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | alice@example.com |
--   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | bob@example.com   |
--   +-------------+------------+-----------+-----------------+---------------------+-------------------+
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
--   SELECT * FROM v_customer_array_reveal LIMIT 2;
--
--   +-------------------+---------------------+----------------------------------------------------------+
--   | customer_group_id | snapshot_ts         | email_array                                              |
--   +-------------------+---------------------+----------------------------------------------------------+
--   | north-east-001    | 2026-04-07 09:00:00 | ["alice@example.com","bob@example.com","carol@example.com"] |
--   | north-east-002    | 2026-04-07 09:00:00 | ["dave@example.com","erin@example.com"]                  |
--   +-------------------+---------------------+----------------------------------------------------------+

CREATE OR REPLACE TEMP VIEW my_catalog.my_schema.v_plaintext_protected_internal_reveal AS
SELECT
  custid ,
  name ,
  thales_reveal_by_column_with_user(
    address,
    'char',
    'address',
    current_user()
  ) AS address ,
  city ,
  state ,
    zip ,
  phone ,
  thales_reveal_by_column_with_user(
    email,
    'char',
    'email',
    current_user()
  ) AS email,
    dob ,
  thales_reveal_by_column_with_user(
    creditcard,
    'nbr',
    'creditcard',
    current_user()
  ) as creditcard  ,
  thales_reveal_by_column_with_user(
    creditcardcode,
    'nbr',
    'creditcardcode',
    current_user()
  ) as creditcardcode ,
  thales_reveal_by_column_with_user(
    ssn,
    'nbr',
    'ssn',
    current_user()
  ) as ssn 
  
FROM my_catalog.my_schema.plaintext_protected_internal;



//thales_reveal_bulk_by_column_with_user
CREATE OR REPLACE TEMP VIEW my_catalog.my_schema.v_plaintext_protected_interna_array_reveal AS
SELECT
SELECT
  custid ,
  name ,
  thales_reveal_bulk_by_column_with_user(
    address_array,
    'char',
    'address',
    current_user()
  ) AS address ,
  city ,
  state ,
    zip ,
  phone ,
  thales_reveal_bulk_by_column_with_user(
    email_array,
    'char',
    'char',
    'email',
    current_user()
  ) AS email,
    dob ,
  thales_reveal_bulk_by_column_with_user(
    creditcard_array,
    'nbr',
    'creditcard',
    current_user()
  ) as creditcard  ,
  thales_reveal_bulk_by_column_with_user(
    creditcardcode_array,
    'nbr',
    'creditcardcode',
    current_user()
  ) as creditcardcode ,
  thales_reveal_bulk_by_column_with_user(
    ssn_array,
    'nbr',
    'ssn',
    current_user()
  ) as ssn 
FROM my_catalog.my_schema.plaintext_protected_internal_arrays;

CREATE OR REPLACE TEMP VIEW v_employee_reveal AS
SELECT
  employee_id,
  employee_name,
  department_name,
  hire_ts,
  thales_reveal_by_column_with_user(
    work_email_token,
    'char',
    'work_email',
    current_user()
  ) AS work_email,
  thales_reveal_by_column_with_user(
    national_id_token,
    'nbr',
    'national_id',
    current_user()
  ) AS national_id
FROM main.raw.employee_tokens;

-- For persistent cluster-backed views in a metastore schema, replace TEMP VIEW
-- with CREATE OR REPLACE VIEW and choose the desired target schema.
