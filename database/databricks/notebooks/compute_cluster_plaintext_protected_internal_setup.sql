-- Databricks notebook source
-- MAGIC %md
-- MAGIC # plaintext_protected_internal Setup
-- MAGIC
-- MAGIC Purpose:
-- MAGIC - create the `my_catalog.my_schema.plaintext_protected_internal` table
-- MAGIC - load a small sample dataset for customer workflow testing
-- MAGIC - provide starter data for loader/JDBC/integration scenarios
-- MAGIC
-- MAGIC Important:
-- MAGIC - this script inserts readable sample values that match the table schema
-- MAGIC - if you want to test reveal workflows, the table contents must first be
-- MAGIC   protected by your loader or another protection step
-- MAGIC - the cast-back reveal examples assume the table contains protected tokens,
-- MAGIC   not raw plaintext

-- COMMAND ----------

USE CATALOG my_catalog;
USE SCHEMA my_schema;

-- COMMAND ----------

CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal (
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

INSERT OVERWRITE my_catalog.my_schema.plaintext_protected_internal
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
FROM my_catalog.my_schema.plaintext_protected_internal
ORDER BY custid;
