ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_US';

--Environment Setup
CREATE DATABASE IF NOT EXISTS NORTHSTAR_ANALYTICS;
CREATE SCHEMA IF NOT EXISTS NORTHSTAR_ANALYTICS.PUBLIC;
USE SCHEMA NORTHSTAR_ANALYTICS.PUBLIC;

-- Employee table with PII
CREATE OR REPLACE TABLE EMPLOYEES (
    EMPLOYEE_ID INT,
    FIRST_NAME VARCHAR,
    LAST_NAME VARCHAR,
    EMAIL VARCHAR,
    SALARY NUMBER
);

-- Clients table with PII
CREATE OR REPLACE TABLE CLIENTS (
    CLIENT_ID INT,
    CLIENT_NAME VARCHAR,
    CONTACT_PERSON VARCHAR,
    EMAIL VARCHAR,
    PHONE VARCHAR
);

-- Feedback table for rating queries
CREATE OR REPLACE TABLE CLIENT_FEEDBACK (
    FEEDBACK_ID INT,
    CLIENT_ID INT,
    CONTACT_PERSON VARCHAR,
    FEEDBACK_TEXT VARCHAR,
    RATING NUMBER
);

-- Insert dummy data
USE SCHEMA NORTHSTAR_ANALYTICS.PUBLIC;

-- 1. Populate EMPLOYEES (10 Records with clear PII)
INSERT INTO EMPLOYEES (EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMAIL, SALARY) VALUES
  (101, 'Sarah', 'Conner', 's.conner@northstar.com', 105000),
  (102, 'Michael', 'Scott', 'm.scott@northstar.com', 88000),
  (103, 'Pam', 'Beesly', 'p.beesly@northstar.com', 62000),
  (104, 'Jim', 'Halpert', 'j.halpert@northstar.com', 92000),
  (105, 'Dwight', 'Schrute', 'd.schrute@northstar.com', 89000),
  (106, 'Angela', 'Martin', 'a.martin@northstar.com', 75000),
  (107, 'Oscar', 'Martinez', 'o.martinez@northstar.com', 82000),
  (108, 'Kevin', 'Malone', 'k.malone@northstar.com', 60000),
  (109, 'Stanley', 'Hudson', 's.hudson@northstar.com', 91000),
  (110, 'Phyllis', 'Vance', 'p.vance@northstar.com', 78000);

-- 2. Populate CLIENTS (10 Records with contact info PII)
INSERT INTO CLIENTS (CLIENT_ID, CLIENT_NAME, CONTACT_PERSON, EMAIL, PHONE) VALUES
  (201, 'Apex Global Systems', 'David Wallace', 'dwallace@apexglobal.com', '212-555-0143'),
  (202, 'Vanguard Dynamics', 'Jan Levinson', 'jlevinson@vanguard.com', '212-555-0188'),
  (203, 'Aperture Science', 'Cave Johnson', 'cjohnson@aperture.com', '503-555-0192'),
  (204, 'Initech Corporation', 'Bill Lumbergh', 'blumbergh@initech.com', '512-555-0104'),
  (205, 'Umbrella Health', 'Albert Wesker', 'awesker@umbrella.com', '312-555-0167'),
  (206, 'Stark Industries', 'Pepper Potts', 'ppotts@starkind.com', '212-555-0111'),
  (207, 'Wayne Enterprises', 'Lucius Fox', 'lfox@wayneent.com', '609-555-0155'),
  (208, 'Cyberdyne Systems', 'Miles Dyson', 'mdyson@cyberdyne.com', '408-555-0120'),
  (209, 'Massive Dynamic', 'Nina Sharp', 'nsharp@massivedynamic.com', '212-555-0133'),
  (210, 'Acme Industrial', 'Wile Coyote', 'wcoyote@acme.com', '602-555-0176');

-- 3. Populate CLIENT_FEEDBACK (10 Records mixing high/low ratings and unstructured text)
INSERT INTO CLIENT_FEEDBACK (FEEDBACK_ID, CLIENT_ID, CONTACT_PERSON, FEEDBACK_TEXT, RATING) VALUES
  (301, 201, 'David Wallace', 'Content recommendation engines brilliant. User engagement increased by 40%. We love this solution!', 5),
  (302, 202, 'Jan Levinson', 'The data integration team was extremely professional. Outstanding turnaround time.', 5),
  (303, 203, 'Cave Johnson', 'Platform is helpful but the interface is not user friendly. Poor design choices overall.', 2),
  (304, 204, 'Bill Lumbergh', 'Reporting features are lacking. Need better automated export capabilities.', 2),
  (305, 205, 'Albert Wesker', 'Exceptional security compliance tools. System performance exceeded our expectations.', 5),
  (306, 206, 'Pepper Potts', 'Great implementation team, but initial onboarding took longer than planned.', 3),
  (307, 207, 'Lucius Fox', 'Highly stable infrastructure. Transformed our quarterly reporting pipeline.', 5),
  (308, 208, 'Miles Dyson', 'Encountered several API latency issues during peak processing hours. Needs improvement.', 1),
  (309, 209, 'Nina Sharp', 'Superb analytics capabilities and great customer support from the account manager.', 4),
  (310, 210, 'Wile Coyote', 'Dashboard load times are too slow for large datasets. Customer service was slow to respond.', 2);

  
CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.ENCRYPT_ALL_PII_TABLES(DRY_RUN BOOLEAN DEFAULT TRUE)
RETURNS TABLE (ACTION_STATUS STRING, TARGET_TABLE STRING, GENERATED_SQL STRING)
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    sql_stmt STRING;
    res RESULTSET;
BEGIN
    CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS temp_encryption_results (
        ACTION_STATUS STRING,
        TARGET_TABLE STRING,
        GENERATED_SQL STRING
    );
    DELETE FROM temp_encryption_results;

    LET c1 CURSOR FOR
        WITH tagged_columns AS (
            SELECT
                c.table_catalog AS database_name,
                c.table_schema,
                c.table_name,
                c.column_name,
                c.data_type,
                CASE
                    WHEN LOWER(c.data_type) LIKE '%varchar%'
                         OR LOWER(c.data_type) LIKE '%string%'
                         OR LOWER(c.data_type) LIKE '%text%'
                    THEN 'pii_char'
                    WHEN LOWER(c.data_type) IN ('number', 'numeric', 'integer', 'bigint', 'smallint', 'tinyint', 'float', 'double')
                    THEN 'pii_number'
                    ELSE NULL
                END AS protection_profile
            FROM NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.COLUMNS c
            INNER JOIN TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
                'NORTHSTAR_ANALYTICS.PUBLIC', 'SCHEMA')) t
                ON c.table_name = t.object_name
                AND (c.column_name = t.column_name OR t.domain = 'TABLE')
            WHERE (LOWER(t.tag_name) LIKE '%pii%' OR LOWER(t.tag_value) LIKE '%pii%')
        ),
        column_transformations AS (
            SELECT
                database_name,
                table_schema,
                table_name,
                CASE protection_profile
                    WHEN 'pii_char'
                    THEN column_name || ' = SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR(' || column_name || ')'
                    WHEN 'pii_number'
                    THEN column_name || ' = SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_NBR_CHAR(' || column_name || ')'
                END AS set_expression
            FROM tagged_columns
            WHERE protection_profile IS NOT NULL
        )
        SELECT
            database_name || '.' || table_schema || '.' || table_name AS full_table_name,
            'UPDATE ' || database_name || '.' || table_schema || '.' || table_name
                || ' SET ' || LISTAGG(set_expression, ', ') WITHIN GROUP (ORDER BY set_expression)
                || ';' AS update_stmt
        FROM column_transformations
        GROUP BY database_name, table_schema, table_name;

    FOR rec IN c1 DO
        IF (DRY_RUN = TRUE) THEN
            INSERT INTO temp_encryption_results VALUES ('PREVIEW_ONLY', rec.full_table_name, rec.update_stmt);
        ELSE
            EXECUTE IMMEDIATE rec.update_stmt;
            INSERT INTO temp_encryption_results VALUES ('EXECUTED', rec.full_table_name, rec.update_stmt);
        END IF;
    END FOR;

    res := (SELECT * FROM temp_encryption_results);
    RETURN TABLE(res);
END;
$$;


CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.CREATE_ALL_PII_REVEAL_VIEWS(DRY_RUN BOOLEAN DEFAULT TRUE)
RETURNS TABLE (ACTION_STATUS STRING, TARGET_VIEW STRING, GENERATED_DDL STRING)
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    res RESULTSET;
BEGIN
    CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS temp_view_results (
        ACTION_STATUS STRING,
        TARGET_VIEW STRING,
        GENERATED_DDL STRING
    );
    DELETE FROM temp_view_results;

    LET c1 CURSOR FOR
        WITH tagged_objects AS (
            SELECT object_database, object_schema, object_name, column_name, domain, tag_name, tag_value
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
                'NORTHSTAR_ANALYTICS.PUBLIC', 'SCHEMA'))
            WHERE (LOWER(tag_name) LIKE '%pii%' OR LOWER(tag_value) LIKE '%pii%')
        ),
        deduped_columns_mapped AS (
            SELECT
                c.table_catalog AS database_name,
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                t.tag_name,
                c.column_name AS original_column_expression,
                CASE
                    WHEN t.tag_name IS NOT NULL
                         AND (LOWER(c.data_type) LIKE '%varchar%'
                              OR LOWER(c.data_type) LIKE '%string%'
                              OR LOWER(c.data_type) LIKE '%text%')
                    THEN 'SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(' || c.column_name || ') AS ' || c.column_name || '_REVEALED'
                    WHEN t.tag_name IS NOT NULL
                         AND (LOWER(c.data_type) IN ('number', 'numeric', 'integer', 'bigint', 'smallint', 'tinyint', 'float', 'double'))
                    THEN 'SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_NBR_CHAR(' || c.column_name || ') AS ' || c.column_name || '_REVEALED'
                    ELSE NULL
                END AS revealed_column_expression,
                MAX(CASE WHEN t.tag_name IS NOT NULL THEN 1 ELSE 0 END)
                    OVER (PARTITION BY c.table_catalog, c.table_schema, c.table_name) AS has_pii
            FROM NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN tagged_objects t
                ON c.table_name = t.object_name
                AND (c.column_name = t.column_name OR t.domain = 'TABLE')
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY c.table_catalog, c.table_schema, c.table_name, c.column_name
                ORDER BY t.tag_name NULLS LAST
            ) = 1
        ),
        table_view_expressions AS (
            SELECT
                database_name,
                table_schema,
                table_name,
                has_pii,
                LISTAGG(original_column_expression, ', ') WITHIN GROUP (ORDER BY ordinal_position) AS original_cols_list,
                LISTAGG(revealed_column_expression, ', ') WITHIN GROUP (ORDER BY ordinal_position) AS revealed_cols_list
            FROM deduped_columns_mapped
            GROUP BY database_name, table_schema, table_name, has_pii
        )
        SELECT
            database_name || '.' || table_schema || '.' || table_name || '_VW' AS view_name,
            'CREATE OR REPLACE VIEW ' || database_name || '.' || table_schema || '.' || table_name || '_VW AS SELECT '
                || original_cols_list
                || IFF(revealed_cols_list IS NOT NULL AND revealed_cols_list != '', ', ' || revealed_cols_list, '')
                || ' FROM ' || database_name || '.' || table_schema || '.' || table_name || ';' AS create_view_ddl
        FROM table_view_expressions
        WHERE has_pii = 1;

    FOR rec IN c1 DO
        IF (DRY_RUN = TRUE) THEN
            INSERT INTO temp_view_results VALUES ('PREVIEW_ONLY', rec.view_name, rec.create_view_ddl);
        ELSE
            EXECUTE IMMEDIATE rec.create_view_ddl;
            INSERT INTO temp_view_results VALUES ('EXECUTED', rec.view_name, rec.create_view_ddl);
        END IF;
    END FOR;

    res := (SELECT * FROM temp_view_results);
    RETURN TABLE(res);
END;
$$;


