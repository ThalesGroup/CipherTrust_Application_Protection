create or replace view NORTHSTAR_ANALYTICS.PUBLIC.CLIENTS_VW(
	CLIENT_ID,
	CLIENT_NAME,
	CONTACT_PERSON,
	EMAIL,
	PHONE,
	CONTACT_PERSON_REVEALED,
	EMAIL_REVEALED,
	PHONE_REVEALED
) as SELECT CLIENT_ID, CLIENT_NAME, CONTACT_PERSON, EMAIL, PHONE, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(CONTACT_PERSON) AS CONTACT_PERSON_REVEALED, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(EMAIL) AS EMAIL_REVEALED, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(PHONE) AS PHONE_REVEALED FROM NORTHSTAR_ANALYTICS.PUBLIC.CLIENTS;


create or replace view NORTHSTAR_ANALYTICS.PUBLIC.CLIENT_FEEDBACK_VW(
	FEEDBACK_ID,
	CLIENT_ID,
	CONTACT_PERSON,
	FEEDBACK_TEXT,
	RATING,
	CONTACT_PERSON_REVEALED
) as SELECT FEEDBACK_ID, CLIENT_ID, CONTACT_PERSON, FEEDBACK_TEXT, RATING, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(CONTACT_PERSON) AS CONTACT_PERSON_REVEALED FROM NORTHSTAR_ANALYTICS.PUBLIC.CLIENT_FEEDBACK;


create or replace view NORTHSTAR_ANALYTICS.PUBLIC.EMPLOYEES_VW(
	EMPLOYEE_ID,
	FIRST_NAME,
	LAST_NAME,
	EMAIL,
	SALARY,
	FIRST_NAME_REVEALED,
	LAST_NAME_REVEALED,
	EMAIL_REVEALED,
	SALARY_REVEALED
) as SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMAIL, SALARY, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(FIRST_NAME) AS FIRST_NAME_REVEALED, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(LAST_NAME) AS LAST_NAME_REVEALED, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(EMAIL) AS EMAIL_REVEALED, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_NBR_CHAR(SALARY) AS SALARY_REVEALED FROM NORTHSTAR_ANALYTICS.PUBLIC.EMPLOYEES;

CREATE OR REPLACE FUNCTION NORTHSTAR_ANALYTICS.PUBLIC.EXTRACT_TAGGED_TOKENS("INPUT_TEXT" VARCHAR)
RETURNS VARIANT
LANGUAGE JAVASCRIPT
AS '
    if (!INPUT_TEXT) return [];

    var tokens = [];
    var charPrefix = ''RU5DY2hhcg==-'';
    var nbrPrefix = ''RU5DTmJy-'';
    var pos = 0;

    while (pos < INPUT_TEXT.length) {
        var charIdx = INPUT_TEXT.indexOf(charPrefix, pos);
        var nbrIdx = INPUT_TEXT.indexOf(nbrPrefix, pos);

        // Find the next token (whichever comes first)
        var idx = -1;
        var prefix = '''';
        var tokenType = '''';

        if (charIdx === -1 && nbrIdx === -1) break;
        if (charIdx === -1) { idx = nbrIdx; prefix = nbrPrefix; tokenType = ''nbr''; }
        else if (nbrIdx === -1) { idx = charIdx; prefix = charPrefix; tokenType = ''char''; }
        else if (charIdx < nbrIdx) { idx = charIdx; prefix = charPrefix; tokenType = ''char''; }
        else { idx = nbrIdx; prefix = nbrPrefix; tokenType = ''nbr''; }

        // Parse length (digits after prefix, before colon)
        var afterPrefix = idx + prefix.length;
        var colonIdx = INPUT_TEXT.indexOf('':'', afterPrefix);
        if (colonIdx === -1) { pos = afterPrefix; continue; }

        var lenStr = INPUT_TEXT.substring(afterPrefix, colonIdx);
        var cipherLen = parseInt(lenStr, 10);
        if (isNaN(cipherLen) || cipherLen <= 0) { pos = afterPrefix; continue; }

        // Extract exactly cipherLen characters after the colon
        var cipherStart = colonIdx + 1;
        var cipherEnd = cipherStart + cipherLen;
        if (cipherEnd > INPUT_TEXT.length) { pos = afterPrefix; continue; }

        var cipher = INPUT_TEXT.substring(cipherStart, cipherEnd);
        var fullMatch = INPUT_TEXT.substring(idx, cipherEnd);

        tokens.push({
            full_match: fullMatch,
            cipher: cipher,
            type: tokenType
        });

        pos = cipherEnd;
    }

    return tokens;
';

CREATE OR REPLACE FUNCTION NORTHSTAR_ANALYTICS.PUBLIC.REPLACE_ALL_PII("INPUT_TEXT" VARCHAR, "FIND_VALUES" ARRAY, "REPLACE_VALUES" ARRAY)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS '
    var result = INPUT_TEXT;
    if (!result || !FIND_VALUES || !REPLACE_VALUES) return result;
    for (var i = 0; i < FIND_VALUES.length; i++) {
        if (FIND_VALUES[i] && REPLACE_VALUES[i]) {
            result = result.split(FIND_VALUES[i]).join(REPLACE_VALUES[i]);
        }
    }
    return result;
';

CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.CREATE_ALL_PII_REVEAL_VIEWS("DRY_RUN" BOOLEAN DEFAULT TRUE)
RETURNS TABLE ("ACTION_STATUS" VARCHAR, "TARGET_VIEW" VARCHAR, "GENERATED_DDL" VARCHAR)
LANGUAGE SQL
EXECUTE AS CALLER
AS '
DECLARE
    res RESULTSET;
    v_view STRING;
    v_ddl STRING;
BEGIN
    USE DATABASE NORTHSTAR_ANALYTICS;
    USE SCHEMA PUBLIC;

    CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS temp_view_results (
        ACTION_STATUS STRING,
        TARGET_VIEW STRING,
        GENERATED_DDL STRING
    );
    DELETE FROM temp_view_results;

    LET c1 CURSOR FOR
        WITH all_tags AS (
            SELECT OBJECT_NAME AS OBJ_NAME, COLUMN_NAME AS COL_NAME, TAG_NAME, DOMAIN
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.EMPLOYEES'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
            UNION ALL
            SELECT OBJECT_NAME, COLUMN_NAME, TAG_NAME, DOMAIN
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.CLIENTS'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
            UNION ALL
            SELECT OBJECT_NAME, COLUMN_NAME, TAG_NAME, DOMAIN
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.CLIENT_FEEDBACK'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
        ),
        deduped_columns_mapped AS (
            SELECT
                c.table_catalog AS database_name,
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                t.TAG_NAME,
                c.column_name AS original_column_expression,
                CASE
                    WHEN t.TAG_NAME IS NOT NULL
                         AND (LOWER(c.data_type) LIKE ''%varchar%''
                              OR LOWER(c.data_type) LIKE ''%string%''
                              OR LOWER(c.data_type) LIKE ''%text%'')
                    THEN ''SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR('' || c.column_name || '') AS '' || c.column_name || ''_REVEALED''
                    WHEN t.TAG_NAME IS NOT NULL
                         AND (LOWER(c.data_type) IN (''number'', ''numeric'', ''integer'', ''bigint'', ''smallint'', ''tinyint'', ''float'', ''double''))
                    THEN ''SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_NBR_CHAR('' || c.column_name || '') AS '' || c.column_name || ''_REVEALED''
                    ELSE NULL
                END AS revealed_column_expression,
                MAX(CASE WHEN t.TAG_NAME IS NOT NULL THEN 1 ELSE 0 END)
                    OVER (PARTITION BY c.table_catalog, c.table_schema, c.table_name) AS has_pii
            FROM NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN all_tags t
                ON c.table_name = t.OBJ_NAME
                AND c.column_name = t.COL_NAME
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY c.table_catalog, c.table_schema, c.table_name, c.column_name
                ORDER BY t.TAG_NAME NULLS LAST
            ) = 1
        ),
        table_view_expressions AS (
            SELECT
                database_name,
                table_schema,
                table_name,
                has_pii,
                LISTAGG(original_column_expression, '', '') WITHIN GROUP (ORDER BY ordinal_position) AS original_cols_list,
                LISTAGG(revealed_column_expression, '', '') WITHIN GROUP (ORDER BY ordinal_position) AS revealed_cols_list
            FROM deduped_columns_mapped
            GROUP BY database_name, table_schema, table_name, has_pii
        )
        SELECT
            database_name || ''.'' || table_schema || ''.'' || table_name || ''_VW'' AS VW_NAME,
            ''CREATE OR REPLACE VIEW '' || database_name || ''.'' || table_schema || ''.'' || table_name || ''_VW AS SELECT ''
                || original_cols_list
                || IFF(revealed_cols_list IS NOT NULL AND revealed_cols_list != '''', '', '' || revealed_cols_list, '''')
                || '' FROM '' || database_name || ''.'' || table_schema || ''.'' || table_name || '';'' AS DDL_STMT
        FROM table_view_expressions
        WHERE has_pii = 1;

    FOR rec IN c1 DO
        v_view := rec.VW_NAME;
        v_ddl := rec.DDL_STMT;
        IF (:DRY_RUN = TRUE) THEN
            INSERT INTO temp_view_results VALUES (''PREVIEW_ONLY'', :v_view, :v_ddl);
        ELSE
            EXECUTE IMMEDIATE :v_ddl;
            INSERT INTO temp_view_results VALUES (''EXECUTED'', :v_view, :v_ddl);
        END IF;
    END FOR;

    res := (SELECT * FROM temp_view_results);
    RETURN TABLE(res);
END;
';

CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.ENCRYPT_ALL_PII_TABLES("DRY_RUN" BOOLEAN DEFAULT TRUE)
RETURNS TABLE ("ACTION_STATUS" VARCHAR, "TARGET_TABLE" VARCHAR, "GENERATED_SQL" VARCHAR)
LANGUAGE SQL
EXECUTE AS CALLER
AS '
DECLARE
    res RESULTSET;
    v_table STRING;
    v_sql STRING;
BEGIN
    USE DATABASE NORTHSTAR_ANALYTICS;
    USE SCHEMA PUBLIC;

    CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS temp_encryption_results (
        ACTION_STATUS STRING,
        TARGET_TABLE STRING,
        GENERATED_SQL STRING
    );
    DELETE FROM temp_encryption_results;

    LET c1 CURSOR FOR
        WITH all_tags AS (
            SELECT OBJECT_NAME AS OBJ_NAME, COLUMN_NAME AS COL_NAME, TAG_NAME, TAG_VALUE
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.EMPLOYEES'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
            UNION ALL
            SELECT OBJECT_NAME, COLUMN_NAME, TAG_NAME, TAG_VALUE
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.CLIENTS'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
            UNION ALL
            SELECT OBJECT_NAME, COLUMN_NAME, TAG_NAME, TAG_VALUE
            FROM TABLE(NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(''NORTHSTAR_ANALYTICS.PUBLIC.CLIENT_FEEDBACK'', ''TABLE''))
            WHERE TAG_NAME = ''PRIVACY_CATEGORY''
        ),
        tagged_columns AS (
            SELECT
                c.table_catalog AS database_name,
                c.table_schema,
                c.table_name,
                c.column_name,
                c.data_type,
                CASE
                    WHEN LOWER(c.data_type) LIKE ''%varchar%''
                         OR LOWER(c.data_type) LIKE ''%string%''
                         OR LOWER(c.data_type) LIKE ''%text%''
                    THEN ''pii_char''
                    WHEN LOWER(c.data_type) IN (''number'', ''numeric'', ''integer'', ''bigint'', ''smallint'', ''tinyint'', ''float'', ''double'')
                    THEN ''pii_number''
                    ELSE NULL
                END AS protection_profile
            FROM NORTHSTAR_ANALYTICS.INFORMATION_SCHEMA.COLUMNS c
            INNER JOIN all_tags t
                ON c.table_name = t.OBJ_NAME
                AND c.column_name = t.COL_NAME
        ),
        column_transformations AS (
            SELECT DISTINCT
                database_name,
                table_schema,
                table_name,
                column_name,
                CASE protection_profile
                    WHEN ''pii_char''
                    THEN column_name || '' = SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR('' || column_name || '')''
                    WHEN ''pii_number''
                    THEN column_name || '' = SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_NBR_CHAR('' || column_name || '')''
                END AS set_expression
            FROM tagged_columns
            WHERE protection_profile IS NOT NULL
        )
        SELECT
            database_name || ''.'' || table_schema || ''.'' || table_name AS TBL,
            ''UPDATE '' || database_name || ''.'' || table_schema || ''.'' || table_name
                || '' SET '' || LISTAGG(set_expression, '', '') WITHIN GROUP (ORDER BY set_expression) AS STMT
        FROM column_transformations
        GROUP BY database_name, table_schema, table_name;

    FOR rec IN c1 DO
        v_table := rec.TBL;
        v_sql := rec.STMT;
        IF (:DRY_RUN = TRUE) THEN
            INSERT INTO temp_encryption_results VALUES (''PREVIEW_ONLY'', :v_table, :v_sql);
        ELSE
            EXECUTE IMMEDIATE :v_sql;
            INSERT INTO temp_encryption_results VALUES (''EXECUTED'', :v_table, :v_sql);
        END IF;
    END FOR;

    res := (SELECT * FROM temp_encryption_results);
    RETURN TABLE(res);
END;
';

CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.PROCESS_AND_TOKENIZE_DOCS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS '
BEGIN
    USE DATABASE NORTHSTAR_ANALYTICS;
    USE SCHEMA PUBLIC;

    -- 1. Parse documents from the DOCS stage
    CREATE OR REPLACE TEMPORARY TABLE TEMP_PARSED_CHUNKS AS
    SELECT
        RELATIVE_PATH AS FILE_NAME,
        SNOWFLAKE.CORTEX.PARSE_DOCUMENT(
            ''@NORTHSTAR_ANALYTICS.PUBLIC.DOCS'', RELATIVE_PATH, {''mode'': ''LAYOUT''}
        ):content::STRING AS RAW_TEXT
    FROM DIRECTORY(''@NORTHSTAR_ANALYTICS.PUBLIC.DOCS'');

    -- 2. Extract PII entities using Cortex LLM
    CREATE OR REPLACE TEMPORARY TABLE TEMP_EXTRACTED_ENTITIES AS
    SELECT
        FILE_NAME,
        RAW_TEXT,
        SNOWFLAKE.CORTEX.COMPLETE(
            ''mistral-large3'',
            CONCAT(
                ''Extract all PII entities (email, phone, name, salary digits) from the text. '',
                ''Return ONLY a JSON object with key "entities" containing an array of objects with: '',
                ''1. "entity_value": raw extracted text '',
                ''2. "detected_type": "number" if pure digits/numeric (like 105000 or 88000), otherwise "char" (like emails or names or formatted phone numbers). '',
                ''Do NOT wrap the response in markdown code fences. Return raw JSON only. '',
                ''Text: '',
                RAW_TEXT
            )
        ) AS EXTRACTED_JSON
    FROM TEMP_PARSED_CHUNKS;

    -- 3. Flatten entities and apply Thales protection with new tag format
    --    Format: {Base64Tag}-{length}:{ciphertext}
    CREATE OR REPLACE TEMPORARY TABLE TEMP_PII_MAPPINGS AS
    SELECT
        f.FILE_NAME,
        f.RAW_TEXT,
        p.value:entity_value::STRING AS RAW_VALUE,
        p.value:detected_type::STRING AS DETECTED_TYPE,
        CASE
            WHEN LOWER(p.value:detected_type::STRING) = ''number''
                 OR REGEXP_LIKE(p.value:entity_value::STRING, ''^[0-9]+$'')
            THEN ''RU5DTmJy-'' || LENGTH(SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_NBR_CHAR(p.value:entity_value::STRING))::STRING || '':'' || SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_NBR_CHAR(p.value:entity_value::STRING)
            ELSE ''RU5DY2hhcg==-'' || LENGTH(SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR(p.value:entity_value::STRING))::STRING || '':'' || SF_TUTS.PUBLIC.THALES_CRDP_SCS_PROTECTBULK_CHAR(p.value:entity_value::STRING)
        END AS TAGGED_PROTECTED_VALUE
    FROM TEMP_EXTRACTED_ENTITIES f,
    LATERAL FLATTEN(input => PARSE_JSON(
        REGEXP_REPLACE(f.EXTRACTED_JSON, ''^```[a-z]*\\\\n?|\\\\n?```$'', '''')
    ):entities) p;

    -- 4. Replace PII in text with tagged tokens, then vectorize
    CREATE OR REPLACE TABLE NORTHSTAR_ANALYTICS.PUBLIC.PROCESSED_DOCUMENTS_RAG AS
    SELECT
        FILE_NAME,
        NORTHSTAR_ANALYTICS.PUBLIC.REPLACE_ALL_PII(
            RAW_TEXT,
            ARRAY_AGG(RAW_VALUE),
            ARRAY_AGG(TAGGED_PROTECTED_VALUE)
        ) AS SANITIZED_TEXT,
        SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            ''e5-base-v2'',
            NORTHSTAR_ANALYTICS.PUBLIC.REPLACE_ALL_PII(
                RAW_TEXT,
                ARRAY_AGG(RAW_VALUE),
                ARRAY_AGG(TAGGED_PROTECTED_VALUE)
            )
        ) AS TEXT_VECTOR
    FROM TEMP_PII_MAPPINGS
    GROUP BY FILE_NAME, RAW_TEXT;

    -- Cleanup
    DROP TABLE IF EXISTS TEMP_PARSED_CHUNKS;
    DROP TABLE IF EXISTS TEMP_EXTRACTED_ENTITIES;
    DROP TABLE IF EXISTS TEMP_PII_MAPPINGS;

    RETURN ''SUCCESS: Documents parsed, PII tagged/tokenized with length-prefixed format, and vectorized into PROCESSED_DOCUMENTS_RAG.'';
END;
';

CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.RAG_QUERY_WITH_RETRY("QUESTION" VARCHAR, "TARGET_TABLE" VARCHAR DEFAULT 'NORTHSTAR_ANALYTICS.PUBLIC.RAG_RESPONSE')
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS '
DECLARE
    v_response STRING;
    v_attempt INT DEFAULT 0;
    v_max_attempts INT DEFAULT 3;
    v_has_corruption BOOLEAN DEFAULT TRUE;
    v_prompt STRING;
BEGIN
    USE DATABASE NORTHSTAR_ANALYTICS;
    USE SCHEMA PUBLIC;

    v_prompt := ''CRITICAL INSTRUCTION: The context contains encrypted tokens that start with EXACTLY "Y2hhciM=$" (for text) or "bmJyIw==$" (for numbers). Rules: 1) Copy each token EXACTLY as one continuous string - never split the prefix from the payload. 2) Use ONLY ASCII characters. 3) Do NOT wrap tokens in backticks, code blocks, or any markdown formatting. 4) A single character change breaks decryption. Answer the question using ONLY the provided context. Context: '';

    WHILE (v_has_corruption AND v_attempt < v_max_attempts) DO
        v_attempt := v_attempt + 1;

        SELECT SNOWFLAKE.CORTEX.COMPLETE(''mistral-large3'',
            CONCAT(:v_prompt, SANITIZED_TEXT, '' Question: '', :QUESTION)
        ) INTO v_response
        FROM (
            SELECT SANITIZED_TEXT
            FROM NORTHSTAR_ANALYTICS.PUBLIC.PROCESSED_DOCUMENTS_RAG
            ORDER BY VECTOR_COSINE_SIMILARITY(
                TEXT_VECTOR,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(''e5-base-v2'', :QUESTION)
            ) DESC
            LIMIT 1
        );

        IF (
            REGEXP_LIKE(v_response, ''.*Y2[^h][^h]ciM=.*'') OR
            REGEXP_LIKE(v_response, ''.*bmJy[^I][^w]=.*'') OR
            REGEXP_LIKE(v_response, ''.*[^\\\\x00-\\\\x7F].*ciM=.*'')
        ) THEN
            v_has_corruption := TRUE;
        ELSE
            v_has_corruption := FALSE;
        END IF;
    END WHILE;

    EXECUTE IMMEDIATE ''CREATE OR REPLACE TABLE '' || :TARGET_TABLE || '' AS SELECT '''''' || REPLACE(v_response, '''''''', '''''''''''') || '''''' AS PROTECTED_RAG_RESPONSE'';

    IF (v_has_corruption) THEN
        RETURN ''WARNING: Token corruption detected after '' || v_attempt || '' attempts. Response stored but may have degraded tokens.'';
    ELSE
        RETURN ''SUCCESS: Clean response generated on attempt '' || v_attempt || '' of '' || v_max_attempts || ''.'';
    END IF;
END;
';

CREATE OR REPLACE PROCEDURE NORTHSTAR_ANALYTICS.PUBLIC.REVEAL_TAGGED_TEXT("INPUT_TEXT" VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS '
DECLARE
    v_result STRING;
    v_full_match STRING;
    v_revealed STRING;
BEGIN
    USE DATABASE NORTHSTAR_ANALYTICS;
    USE SCHEMA PUBLIC;

    v_result := :INPUT_TEXT;

    IF (v_result IS NULL OR v_result = '''') THEN
        RETURN v_result;
    END IF;

    -- Extract all tokens using the deterministic parser
    CREATE OR REPLACE TEMPORARY TABLE temp_tokens AS
    SELECT
        f.value:full_match::STRING AS full_match,
        f.value:cipher::STRING AS cipher,
        f.value:type::STRING AS token_type
    FROM TABLE(FLATTEN(
        NORTHSTAR_ANALYTICS.PUBLIC.EXTRACT_TAGGED_TOKENS(:v_result)
    )) f;

    -- Reveal char tokens
    LET c1 CURSOR FOR
        SELECT full_match AS FM, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_CHAR(cipher) AS RV
        FROM temp_tokens WHERE token_type = ''char'';

    FOR rec IN c1 DO
        v_full_match := rec.FM;
        v_revealed := rec.RV;
        v_result := REPLACE(:v_result, :v_full_match, :v_revealed);
    END FOR;

    -- Reveal number tokens
    LET c2 CURSOR FOR
        SELECT full_match AS FM, SF_TUTS.PUBLIC.THALES_CRDP_SCS_REVEALBULK_NBR_CHAR(cipher) AS RV
        FROM temp_tokens WHERE token_type = ''nbr'';

    FOR rec IN c2 DO
        v_full_match := rec.FM;
        v_revealed := rec.RV;
        v_result := REPLACE(:v_result, :v_full_match, :v_revealed);
    END FOR;

    DROP TABLE IF EXISTS temp_tokens;

    RETURN v_result;
END;
';
