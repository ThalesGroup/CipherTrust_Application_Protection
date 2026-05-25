-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Plaintext Customer Table Setup
-- MAGIC
-- MAGIC This setup script creates a customer-style workflow for the main sample table:
-- MAGIC
-- MAGIC - `plaintext_plaintext`
-- MAGIC - `plaintext_protected_internal`
-- MAGIC - `plaintext_protected_external`
-- MAGIC - `plaintext_protected_none`
-- MAGIC - session temp row reveal views for both internal and external protected tables
-- MAGIC - a session temp row reveal view for the no-version protected table
-- MAGIC - a persistent array table plus a session temp array reveal view for the internal path
-- MAGIC - a persistent array table plus a session temp array reveal view for the external path
-- MAGIC - a persistent array table plus a session temp array reveal view for the no-version path
-- MAGIC - a session temp flattened final reveal view for the internal array path
-- MAGIC - a session temp flattened final reveal view for the external array path
-- MAGIC - a session temp flattened final reveal view for the no-version array path
-- MAGIC
-- MAGIC Note:
-- MAGIC - The protected tables are persistent.
-- MAGIC - The reveal views created in this compute-cluster notebook are session TEMP
-- MAGIC   VIEW objects because they depend on session-registered Java UDFs.
-- MAGIC - For persistent governed reveal views, use the SQL Warehouse / Unity
-- MAGIC   Catalog function path instead.
-- MAGIC
-- MAGIC This notebook self-registers the object-aware Java UDFs it needs for the
-- MAGIC current Spark session, so it can be run directly on a configured compute
-- MAGIC cluster without first running a separate smoke-test registration notebook.
-- MAGIC
-- MAGIC Internal-protect flow:
-- MAGIC - protect into `plaintext_protected_internal`
-- MAGIC - store transformed sensitive values as `STRING`
-- MAGIC - reveal from that protected table
-- MAGIC - cast back numeric values in the reveal view
-- MAGIC
-- MAGIC Example row-based source shape:
-- MAGIC
-- MAGIC   main.raw.customer_tokens
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+----------------+
-- MAGIC   | customer_id | first_name | last_name | customer_status | created_ts          | email_token    |
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+----------------+
-- MAGIC   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | A9K2...        |
-- MAGIC   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | B1M4...        |
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+----------------+
-- MAGIC
-- MAGIC Example row-based view result:
-- MAGIC
-- MAGIC   SELECT * FROM v_customer_reveal LIMIT 2;
-- MAGIC
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+-------------------+
-- MAGIC   | customer_id | first_name | last_name | customer_status | created_ts          | email             |
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+-------------------+
-- MAGIC   | C1001       | Alice      | Smith     | ACTIVE          | 2026-04-07 09:00:00 | alice@example.com |
-- MAGIC   | C1002       | Bob        | Jones     | ACTIVE          | 2026-04-07 09:05:00 | bob@example.com   |
-- MAGIC   +-------------+------------+-----------+-----------------+---------------------+-------------------+
-- MAGIC
-- MAGIC Example array-based source shape:
-- MAGIC
-- MAGIC   main.raw.customer_token_arrays
-- MAGIC   +-------------------+---------------------+----------------------------------------+
-- MAGIC   | customer_group_id | snapshot_ts         | email_token_array                      |
-- MAGIC   +-------------------+---------------------+----------------------------------------+
-- MAGIC   | north-east-001    | 2026-04-07 09:00:00 | ["A9K2...","B1M4...","C7P8..."]        |
-- MAGIC   | north-east-002    | 2026-04-07 09:00:00 | ["D4Q1...","E6R3..."]                  |
-- MAGIC   +-------------------+---------------------+----------------------------------------+
-- MAGIC
-- MAGIC Example array-based view result:
-- MAGIC
-- MAGIC   SELECT * FROM v_customer_array_reveal LIMIT 2;
-- MAGIC
-- MAGIC   +-------------------+---------------------+----------------------------------------------------------+
-- MAGIC   | customer_group_id | snapshot_ts         | email_array                                              |
-- MAGIC   +-------------------+---------------------+----------------------------------------------------------+
-- MAGIC   | north-east-001    | 2026-04-07 09:00:00 | ["alice@example.com","bob@example.com","carol@example.com"] |
-- MAGIC   | north-east-002    | 2026-04-07 09:00:00 | ["dave@example.com","erin@example.com"]                  |
-- MAGIC   +-------------------+---------------------+----------------------------------------------------------+
-- MAGIC
-- MAGIC External-protect flow:
-- MAGIC - protect into `plaintext_protected_external`
-- MAGIC - use `thales_protect_by_object_and_column_with_external_header(...)`
-- MAGIC - store both the protected value and returned sibling `*_header` columns
-- MAGIC - reveal through `thales_reveal_by_object_and_column_with_external_header_and_user(...)`
-- MAGIC
-- MAGIC None-protect flow:
-- MAGIC - protect into `plaintext_protected_none`
-- MAGIC - use `thales_protect_by_object_and_column(...)`
-- MAGIC - no sibling header columns are stored
-- MAGIC - reveal through `thales_reveal_by_object_and_column_with_user(...)`

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
-- MAGIC print("Required object-aware Thales Java UDFs registered for plaintext setup.")

-- COMMAND ----------

-- Base sample table

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_plaintext (
  custid SMALLINT,
  name VARCHAR(107),
  address VARCHAR(107),
  city VARCHAR(107),
  state VARCHAR(9),
  zip VARCHAR(17),
  phone VARCHAR(27),
  email VARCHAR(107),
  dob TIMESTAMP,
  creditcard DECIMAL(25,0),
  creditcardcode INT,
  ssn VARCHAR(18)
)
USING DELTA;

-- COMMAND ----------

INSERT OVERWRITE my_catalog.my_schema.plaintext_plaintext
SELECT * FROM VALUES
  (1,  'Ava Reynolds',       '128 Cedar Run',       'Nashville',      'TN', '37211-1022', '(615)555-0101', 'ava.reynolds@example.com',       TIMESTAMP('1988-02-14 00:00:00'), CAST(4532100098761234 AS DECIMAL(25,0)), 812, '565-00-9721'),
  (2,  'Liam Carter',        '44 Pine Hollow',      'Denver',         'CO', '80220-4401', '(303)555-0102', 'liam.carter@example.com',        TIMESTAMP('1991-07-09 00:00:00'), CAST(5494101645671502 AS DECIMAL(25,0)), 475, '152-38-2718'),
  (3,  'Mia Sullivan',       '902 Willow Bend',     'Austin',         'TX', '78741-1180', '(512)555-0103', 'mia.sullivan@example.com',       TIMESTAMP('1985-11-23 00:00:00'), CAST(5368843047843345 AS DECIMAL(25,0)), 312, '257-07-4384'),
  (4,  'Noah Bennett',       '17 Juniper Trace',    'Raleigh',        'NC', '27610-3309', '(919)555-0104', 'noah.bennett@example.com',       TIMESTAMP('1993-03-05 00:00:00'), CAST(5109331987586037 AS DECIMAL(25,0)), 465, '560-33-5403'),
  (5,  'Emma Foster',        '775 Lakeview Court',  'Phoenix',        'AZ', '85018-2910', '(602)555-0105', 'emma.foster@example.com',        TIMESTAMP('1987-06-30 00:00:00'), CAST(5436893800866072 AS DECIMAL(25,0)), 772, '544-09-7252'),
  (6,  'James Brooks',       '260 Oak Meadow',      'Columbus',       'OH', '43215-8821', '(614)555-0106', 'james.brooks@example.com',       TIMESTAMP('1990-01-18 00:00:00'), CAST(5251158353866743 AS DECIMAL(25,0)), 948, '583-50-6856'),
  (7,  'Sophia Hayes',       '91 River Glen',       'Orlando',        'FL', '32811-5502', '(407)555-0107', 'sophia.hayes@example.com',       TIMESTAMP('1994-09-12 00:00:00'), CAST(5407153939445792 AS DECIMAL(25,0)), 217, '544-86-4823'),
  (8,  'Benjamin Price',     '503 Birch Point',     'Madison',        'WI', '53704-4011', '(608)555-0108', 'benjamin.price@example.com',     TIMESTAMP('1986-12-04 00:00:00'), CAST(5531093160992295 AS DECIMAL(25,0)), 381, '465-36-8287'),
  (9,  'Olivia Long',        '39 Harbor Street',    'Savannah',       'GA', '31405-1932', '(912)555-0109', 'olivia.long@example.com',        TIMESTAMP('1992-04-27 00:00:00'), CAST(5124361217488168 AS DECIMAL(25,0)), 526, '375-67-4091'),
  (10, 'William Turner',     '640 Aspen Ridge',     'Boise',          'ID', '83705-2207', '(208)555-0110', 'william.turner@example.com',     TIMESTAMP('1989-08-16 00:00:00'), CAST(5514689934713486 AS DECIMAL(25,0)), 243, '635-73-4134'),
  (11, 'Charlotte Perry',    '11 Meadow Lane',      'Birmingham',     'AL', '35209-5006', '(205)555-0111', 'charlotte.perry@example.com',    TIMESTAMP('1995-05-19 00:00:00'), CAST(5428157219011302 AS DECIMAL(25,0)), 770, '482-15-9206'),
  (12, 'Lucas Simmons',      '722 Brookside Ave',   'Kansas City',    'MO', '64110-3399', '(816)555-0112', 'lucas.simmons@example.com',      TIMESTAMP('1984-10-02 00:00:00'), CAST(5204432719984431 AS DECIMAL(25,0)), 654, '291-64-7810'),
  (13, 'Amelia Hughes',      '18 Maple Crest',      'Salt Lake City', 'UT', '84115-1028', '(801)555-0113', 'amelia.hughes@example.com',      TIMESTAMP('1996-01-07 00:00:00'), CAST(5488210021756640 AS DECIMAL(25,0)), 109, '619-42-5508'),
  (14, 'Henry Coleman',      '407 Summit View',     'Richmond',       'VA', '23224-6103', '(804)555-0114', 'henry.coleman@example.com',      TIMESTAMP('1983-07-25 00:00:00'), CAST(5349907712344456 AS DECIMAL(25,0)), 587, '726-11-8432'),
  (15, 'Evelyn Jenkins',     '255 Timber Path',     'Louisville',     'KY', '40214-7100', '(502)555-0115', 'evelyn.jenkins@example.com',     TIMESTAMP('1991-02-28 00:00:00'), CAST(5571036654412298 AS DECIMAL(25,0)), 431, '814-95-2007'),
  (16, 'Alexander Russell',  '970 Orchard Hill',    'Tampa',          'FL', '33607-4818', '(813)555-0116', 'alexander.russell@example.com',  TIMESTAMP('1988-09-03 00:00:00'), CAST(5298173400661901 AS DECIMAL(25,0)), 268, '503-28-6744'),
  (17, 'Harper Griffin',     '62 Crescent Park',    'San Antonio',    'TX', '78218-3105', '(210)555-0117', 'harper.griffin@example.com',     TIMESTAMP('1997-06-11 00:00:00'), CAST(5412758832001147 AS DECIMAL(25,0)), 344, '698-04-1189'),
  (18, 'Daniel Barnes',      '315 Autumn Ridge',    'Omaha',          'NE', '68104-2297', '(402)555-0118', 'daniel.barnes@example.com',      TIMESTAMP('1982-11-09 00:00:00'), CAST(5189047715523320 AS DECIMAL(25,0)), 906, '447-22-8031'),
  (19, 'Ella Powell',        '804 Magnolia Row',    'Charleston',     'SC', '29414-7720', '(843)555-0119', 'ella.powell@example.com',        TIMESTAMP('1990-03-21 00:00:00'), CAST(5466009917784505 AS DECIMAL(25,0)), 158, '572-80-3394'),
  (20, 'Michael Bryant',     '147 Valley Forge',    'Tulsa',          'OK', '74136-1188', '(918)555-0120', 'michael.bryant@example.com',     TIMESTAMP('1986-05-14 00:00:00'), CAST(5311150088129944 AS DECIMAL(25,0)), 623, '689-17-4526')
AS t(custid, name, address, city, state, zip, phone, email, dob, creditcard, creditcardcode, ssn);

-- COMMAND ----------

SELECT *
FROM my_catalog.my_schema.plaintext_plaintext
ORDER BY custid;

-- COMMAND ----------

-- Internal protected table shape

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal (
  custid SMALLINT,
  name VARCHAR(107),
  address STRING,
  city VARCHAR(107),
  state VARCHAR(9),
  zip VARCHAR(17),
  phone VARCHAR(27),
  email STRING,
  dob TIMESTAMP,
  creditcard STRING,
  creditcardcode STRING,
  ssn STRING
)
USING DELTA;

-- COMMAND ----------

-- Internal protected table load

INSERT OVERWRITE my_catalog.my_schema.plaintext_protected_internal
SELECT
  custid,
  name,
  thales_protect_by_object_and_column(CAST(address AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_internal', 'address') AS address,
  city,
  state,
  zip,
  phone,
  thales_protect_by_object_and_column(CAST(email AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_internal', 'email') AS email,
  dob,
  thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_internal', 'creditcard') AS creditcard,
  thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_internal', 'creditcardcode') AS creditcardcode,
  thales_protect_by_object_and_column(CAST(ssn AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_internal', 'ssn') AS ssn
FROM my_catalog.my_schema.plaintext_plaintext;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_internal
ORDER BY custid;

-- COMMAND ----------

-- External protected table shape

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_external (
  custid SMALLINT,
  name VARCHAR(107),
  address STRING,
  address_header STRING,
  city VARCHAR(107),
  state VARCHAR(9),
  zip VARCHAR(17),
  phone VARCHAR(27),
  email STRING,
  email_header STRING,
  dob TIMESTAMP,
  creditcard STRING,
  creditcard_header STRING,
  creditcardcode STRING,
  creditcardcode_header STRING,
  ssn STRING,
  ssn_header STRING
)
USING DELTA;

-- COMMAND ----------

-- None protected table shape

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_none (
  custid SMALLINT,
  name VARCHAR(107),
  address STRING,
  city VARCHAR(107),
  state VARCHAR(9),
  zip VARCHAR(17),
  phone VARCHAR(27),
  email STRING,
  dob TIMESTAMP,
  creditcard STRING,
  creditcardcode STRING,
  ssn STRING
)
USING DELTA;

-- COMMAND ----------

-- External protected table load

INSERT OVERWRITE my_catalog.my_schema.plaintext_protected_external
SELECT
  custid,
  name,
  protected_address.protected_value AS address,
  protected_address.external_header AS address_header,
  city,
  state,
  zip,
  phone,
  protected_email.protected_value AS email,
  protected_email.external_header AS email_header,
  dob,
  protected_creditcard.protected_value AS creditcard,
  protected_creditcard.external_header AS creditcard_header,
  protected_creditcardcode.protected_value AS creditcardcode,
  protected_creditcardcode.external_header AS creditcardcode_header,
  protected_ssn.protected_value AS ssn,
  protected_ssn.external_header AS ssn_header
FROM (
  SELECT
    custid,
    name,
    thales_protect_by_object_and_column_with_external_header(CAST(address AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_external', 'address') AS protected_address,
    city,
    state,
    zip,
    phone,
    thales_protect_by_object_and_column_with_external_header(CAST(email AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_external', 'email') AS protected_email,
    dob,
    thales_protect_by_object_and_column_with_external_header(CAST(creditcard AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_external', 'creditcard') AS protected_creditcard,
    thales_protect_by_object_and_column_with_external_header(CAST(creditcardcode AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_external', 'creditcardcode') AS protected_creditcardcode,
    thales_protect_by_object_and_column_with_external_header(CAST(ssn AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_external', 'ssn') AS protected_ssn
  FROM my_catalog.my_schema.plaintext_plaintext
) s;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_external
ORDER BY custid;

-- COMMAND ----------

-- None protected table load

INSERT OVERWRITE my_catalog.my_schema.plaintext_protected_none
SELECT
  custid,
  name,
  thales_protect_by_object_and_column(CAST(address AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_none', 'address') AS address,
  city,
  state,
  zip,
  phone,
  thales_protect_by_object_and_column(CAST(email AS STRING), 'char', 'my_catalog.my_schema.plaintext_protected_none', 'email') AS email,
  dob,
  thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_none', 'creditcard') AS creditcard,
  thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_none', 'creditcardcode') AS creditcardcode,
  thales_protect_by_object_and_column(CAST(ssn AS STRING), 'nbr', 'my_catalog.my_schema.plaintext_protected_none', 'ssn') AS ssn
FROM my_catalog.my_schema.plaintext_plaintext;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_none
ORDER BY custid;

-- COMMAND ----------

-- Internal row reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_internal_revealed AS
SELECT
  custid,
  name,
  thales_reveal_by_object_and_column_with_user(
    CAST(address AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_internal',
    'address',
    current_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_reveal_by_object_and_column_with_user(
    CAST(email AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_internal',
    'email',
    current_user()
  ) AS email,
  dob,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(creditcard AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_internal',
      'creditcard',
      current_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(creditcardcode AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_internal',
      'creditcardcode',
      current_user()
    ) AS INT
  ) AS creditcardcode,
  thales_reveal_by_object_and_column_with_user(
    CAST(ssn AS STRING),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_internal',
    'ssn',
    current_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_internal;

SELECT *
FROM v_plaintext_protected_internal_revealed
ORDER BY custid;

-- COMMAND ----------

-- External row reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_external_revealed AS
SELECT
  custid,
  name,
  thales_reveal_by_object_and_column_with_external_header_and_user(
    CAST(address AS STRING),
    CAST(address_header AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_external',
    'address',
    current_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_reveal_by_object_and_column_with_external_header_and_user(
    CAST(email AS STRING),
    CAST(email_header AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_external',
    'email',
    current_user()
  ) AS email,
  dob,
  CAST(
    thales_reveal_by_object_and_column_with_external_header_and_user(
      CAST(creditcard AS STRING),
      CAST(creditcard_header AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external',
      'creditcard',
      current_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_object_and_column_with_external_header_and_user(
      CAST(creditcardcode AS STRING),
      CAST(creditcardcode_header AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external',
      'creditcardcode',
      current_user()
    ) AS INT
  ) AS creditcardcode,
  thales_reveal_by_object_and_column_with_external_header_and_user(
    CAST(ssn AS STRING),
    CAST(ssn_header AS STRING),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_external',
    'ssn',
    current_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_external;

SELECT *
FROM v_plaintext_protected_external_revealed
ORDER BY custid;

-- COMMAND ----------

-- None row reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_none_revealed AS
SELECT
  custid,
  name,
  thales_reveal_by_object_and_column_with_user(
    CAST(address AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_none',
    'address',
    current_user()
  ) AS address,
  city,
  state,
  zip,
  phone,
  thales_reveal_by_object_and_column_with_user(
    CAST(email AS STRING),
    'char',
    'my_catalog.my_schema.plaintext_protected_none',
    'email',
    current_user()
  ) AS email,
  dob,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(creditcard AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none',
      'creditcard',
      current_user()
    ) AS DECIMAL(25,0)
  ) AS creditcard,
  CAST(
    thales_reveal_by_object_and_column_with_user(
      CAST(creditcardcode AS STRING),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none',
      'creditcardcode',
      current_user()
    ) AS INT
  ) AS creditcardcode,
  thales_reveal_by_object_and_column_with_user(
    CAST(ssn AS STRING),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_none',
    'ssn',
    current_user()
  ) AS ssn
FROM my_catalog.my_schema.plaintext_protected_none;

SELECT *
FROM v_plaintext_protected_none_revealed
ORDER BY custid;

-- COMMAND ----------

-- Internal array table

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_internal
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'dob', dob,
      'creditcard', creditcard,
      'creditcardcode', creditcardcode,
      'ssn', ssn
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.ssn) AS ssn_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_internal_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- External array table

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_external_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_external
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'address_header', address_header,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'email_header', email_header,
      'dob', dob,
      'creditcard', creditcard,
      'creditcard_header', creditcard_header,
      'creditcardcode', creditcardcode,
      'creditcardcode_header', creditcardcode_header,
      'ssn', ssn,
      'ssn_header', ssn_header
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.address_header) AS address_header_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.email_header) AS email_header_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcard_header) AS creditcard_header_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.creditcardcode_header) AS creditcardcode_header_array,
  collect_list(row_struct.ssn) AS ssn_array,
  collect_list(row_struct.ssn_header) AS ssn_header_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_external_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- None array table

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_none_arrays
USING DELTA AS
WITH ordered_rows AS (
  SELECT
    *,
    row_number() OVER (ORDER BY custid) AS row_num
  FROM my_catalog.my_schema.plaintext_protected_none
),
batched_rows AS (
  SELECT
    CAST(FLOOR((row_num - 1) / 1000) AS INT) AS batch_id,
    named_struct(
      'custid', custid,
      'name', name,
      'address', address,
      'city', city,
      'state', state,
      'zip', zip,
      'phone', phone,
      'email', email,
      'dob', dob,
      'creditcard', creditcard,
      'creditcardcode', creditcardcode,
      'ssn', ssn
    ) AS row_struct
  FROM ordered_rows
)
SELECT
  batch_id,
  collect_list(row_struct.custid) AS custid_array,
  collect_list(row_struct.name) AS name_array,
  collect_list(row_struct.address) AS address_array,
  collect_list(row_struct.city) AS city_array,
  collect_list(row_struct.state) AS state_array,
  collect_list(row_struct.zip) AS zip_array,
  collect_list(row_struct.phone) AS phone_array,
  collect_list(row_struct.email) AS email_array,
  collect_list(row_struct.dob) AS dob_array,
  collect_list(row_struct.creditcard) AS creditcard_array,
  collect_list(row_struct.creditcardcode) AS creditcardcode_array,
  collect_list(row_struct.ssn) AS ssn_array
FROM batched_rows
GROUP BY batch_id;

SELECT *
FROM my_catalog.my_schema.plaintext_protected_none_arrays
ORDER BY batch_id;

-- COMMAND ----------

-- Internal array reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_internal_array_reveal AS
SELECT
  batch_id,
  custid_array,
  name_array,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(address_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_internal_arrays',
    'address',
    current_user()
  ) AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(email_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_internal_arrays',
    'email',
    current_user()
  ) AS email_decrypted,
  dob_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(creditcard_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      'creditcard',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_internal_arrays',
      'creditcardcode',
      current_user()
    ),
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(ssn_array, x -> CAST(x AS STRING)),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_internal_arrays',
    'ssn',
    current_user()
  ) AS ssn_decrypted
FROM my_catalog.my_schema.plaintext_protected_internal_arrays;

SELECT *
FROM v_plaintext_protected_internal_array_reveal
ORDER BY batch_id;

-- COMMAND ----------

-- External array reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_external_array_reveal AS
SELECT
  batch_id,
  custid_array,
  name_array,
  thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
    transform(address_array, x -> CAST(x AS STRING)),
    transform(address_header_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_external_arrays',
    'address',
    current_user()
  ) AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
    transform(email_array, x -> CAST(x AS STRING)),
    transform(email_header_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_external_arrays',
    'email',
    current_user()
  ) AS email_decrypted,
  dob_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
      transform(creditcard_array, x -> CAST(x AS STRING)),
      transform(creditcard_header_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external_arrays',
      'creditcard',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      transform(creditcardcode_header_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_external_arrays',
      'creditcardcode',
      current_user()
    ),
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
    transform(ssn_array, x -> CAST(x AS STRING)),
    transform(ssn_header_array, x -> CAST(x AS STRING)),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_external_arrays',
    'ssn',
    current_user()
  ) AS ssn_decrypted
FROM my_catalog.my_schema.plaintext_protected_external_arrays;

SELECT *
FROM v_plaintext_protected_external_array_reveal
ORDER BY batch_id;

-- COMMAND ----------

-- None array reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_protected_none_array_reveal AS
SELECT
  batch_id,
  custid_array,
  name_array,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(address_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_none_arrays',
    'address',
    current_user()
  ) AS address_decrypted,
  city_array,
  state_array,
  zip_array,
  phone_array,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(email_array, x -> CAST(x AS STRING)),
    'char',
    'my_catalog.my_schema.plaintext_protected_none_arrays',
    'email',
    current_user()
  ) AS email_decrypted,
  dob_array,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(creditcard_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none_arrays',
      'creditcard',
      current_user()
    ),
    x -> CAST(x AS DECIMAL(25,0))
  ) AS creditcard_decrypted,
  transform(
    thales_reveal_bulk_by_object_and_column_with_user(
      transform(creditcardcode_array, x -> CAST(x AS STRING)),
      'nbr',
      'my_catalog.my_schema.plaintext_protected_none_arrays',
      'creditcardcode',
      current_user()
    ),
    x -> CAST(x AS INT)
  ) AS creditcardcode_decrypted,
  thales_reveal_bulk_by_object_and_column_with_user(
    transform(ssn_array, x -> CAST(x AS STRING)),
    'nbr',
    'my_catalog.my_schema.plaintext_protected_none_arrays',
    'ssn',
    current_user()
  ) AS ssn_decrypted
FROM my_catalog.my_schema.plaintext_protected_none_arrays;

SELECT *
FROM v_plaintext_protected_none_array_reveal
ORDER BY batch_id;

-- COMMAND ----------

-- Internal flattened array reveal view

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
ORDER BY custid;

-- COMMAND ----------

-- External flattened array reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_external_final_reveal_flat AS
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
  FROM v_plaintext_protected_external_array_reveal
);

SELECT *
FROM v_plaintext_external_final_reveal_flat
ORDER BY custid;

-- COMMAND ----------

-- None flattened array reveal view

CREATE OR REPLACE TEMP VIEW v_plaintext_none_final_reveal_flat AS
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
  FROM v_plaintext_protected_none_array_reveal
);

SELECT *
FROM v_plaintext_none_final_reveal_flat
ORDER BY custid;

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
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_plaintext TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_internal TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_external TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_none TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_internal_arrays TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_external_arrays TO `thales_cluster_deployers`",
-- MAGIC     "GRANT SELECT ON TABLE my_catalog.my_schema.plaintext_protected_none_arrays TO `thales_cluster_deployers`",
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
SELECT 'base' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.plaintext_plaintext
UNION ALL
SELECT 'internal_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.plaintext_protected_internal
UNION ALL
SELECT 'external_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.plaintext_protected_external
UNION ALL
SELECT 'none_table' AS object_type, COUNT(*) AS row_count FROM my_catalog.my_schema.plaintext_protected_none
UNION ALL
SELECT 'internal_row_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_internal_revealed
UNION ALL
SELECT 'external_row_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_external_revealed
UNION ALL
SELECT 'none_row_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_none_revealed
UNION ALL
SELECT 'internal_array_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_internal_array_reveal
UNION ALL
SELECT 'external_array_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_external_array_reveal
UNION ALL
SELECT 'none_array_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_protected_none_array_reveal
UNION ALL
SELECT 'internal_flat_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_final_reveal_flat
UNION ALL
SELECT 'external_flat_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_external_final_reveal_flat
UNION ALL
SELECT 'none_flat_view' AS object_type, COUNT(*) AS row_count FROM v_plaintext_none_final_reveal_flat
ORDER BY object_type;

-- COMMAND ----------

SELECT *
FROM (
  SELECT
    'internal_row' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_protected_internal_revealed
  ORDER BY custid
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'external_row' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_protected_external_revealed
  ORDER BY custid
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'none_row' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_protected_none_revealed
  ORDER BY custid
  LIMIT 5
)
ORDER BY example_type, custid;

-- COMMAND ----------

SELECT *
FROM (
  SELECT
    'internal_array' AS example_type,
    batch_id,
    size(custid_array) AS row_count,
    size(address_decrypted) AS address_count,
    size(email_decrypted) AS email_count,
    size(ssn_decrypted) AS ssn_count
  FROM v_plaintext_protected_internal_array_reveal
  ORDER BY batch_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'external_array' AS example_type,
    batch_id,
    size(custid_array) AS row_count,
    size(address_decrypted) AS address_count,
    size(email_decrypted) AS email_count,
    size(ssn_decrypted) AS ssn_count
  FROM v_plaintext_protected_external_array_reveal
  ORDER BY batch_id
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'none_array' AS example_type,
    batch_id,
    size(custid_array) AS row_count,
    size(address_decrypted) AS address_count,
    size(email_decrypted) AS email_count,
    size(ssn_decrypted) AS ssn_count
  FROM v_plaintext_protected_none_array_reveal
  ORDER BY batch_id
  LIMIT 5
)
ORDER BY example_type, batch_id;

-- COMMAND ----------

SELECT *
FROM (
  SELECT
    'internal_flat' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_final_reveal_flat
  ORDER BY custid
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'external_flat' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_external_final_reveal_flat
  ORDER BY custid
  LIMIT 5
)
UNION ALL
SELECT *
FROM (
  SELECT
    'none_flat' AS example_type,
    custid,
    name,
    address,
    email,
    CAST(creditcard AS STRING) AS creditcard,
    CAST(creditcardcode AS STRING) AS creditcardcode,
    ssn
  FROM v_plaintext_none_final_reveal_flat
  ORDER BY custid
  LIMIT 5
)
ORDER BY example_type, custid;
