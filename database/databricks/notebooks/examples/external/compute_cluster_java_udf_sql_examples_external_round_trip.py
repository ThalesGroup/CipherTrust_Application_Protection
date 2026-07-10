# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Cluster Java UDF SQL Examples (External Round Trip)
# MAGIC
# MAGIC This notebook keeps the Java SQL-shaped examples from the original
# MAGIC compute-cluster notebook, but adds a true external-policy round trip so we
# MAGIC can compare its behavior more directly to `plaintext_setup.sql`.
# MAGIC
# MAGIC Use this notebook when you want to answer:
# MAGIC - does external protect return both `protected_value` and `external_header`?
# MAGIC - can those stored values be revealed successfully in the same session?
# MAGIC - does the behavior differ from the lighter external-header-only demo?

# COMMAND ----------

# MAGIC %run ../../smoke_tests/register_java_udfs

# COMMAND ----------

from utils.runtime_diagnostics import (
    print_column_profile_diagnostics,
    print_effective_profile_resolution_diagnostics,
    load_runtime_properties,
    print_object_mapping_diagnostics,
    print_profile_alias_diagnostics,
    print_runtime_diagnostics,
)

# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
INTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
EXTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"

TEMP_VIEW_NAME = "v_java_udf_internal_protected_demo"
CTAS_TABLE_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_java_udf_ctas_demo"
EXTERNAL_HEADER_ONLY_VIEW_NAME = "v_java_udf_external_header_only_demo"
EXTERNAL_ROUND_TRIP_TABLE_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_java_udf_round_trip_demo"
EXTERNAL_REVEALED_VIEW_NAME = "v_java_udf_external_revealed_demo"

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

props = load_runtime_properties(config_path)
print_runtime_diagnostics(
    spark,
    label="External round-trip runtime diagnostics:",
    config_path=config_path,
    runtime_settings=props,
    include_debug_flag=True,
)
print_object_mapping_diagnostics(
    props,
    [
        INTERNAL_OBJECT,
        EXTERNAL_OBJECT,
    ],
)
print_profile_alias_diagnostics(
    props,
    [
        "TAG.char.internal",
        "TAG.nbr.internal",
        "TAG.char.external",
        "TAG.nbr.external",
    ],
)
print_column_profile_diagnostics(
    props,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)
print_effective_profile_resolution_diagnostics(
    props,
    EXTERNAL_OBJECT,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)

# COMMAND ----------

register_java_udfs()


# COMMAND ----------

display(spark.sql(f"SELECT * FROM {SOURCE_TABLE} LIMIT 5"))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {TEMP_VIEW_NAME} AS
    SELECT
      custid,
      name,
      thales_protect_by_object_and_column(
        address,
        'char',
        '{INTERNAL_OBJECT}',
        'address'
      ) AS address,
      city,
      state,
      zip,
      phone,
      thales_protect_by_object_and_column(
        email,
        'char',
        '{INTERNAL_OBJECT}',
        'email'
      ) AS email,
      dob,
      thales_protect_by_object_and_column(
        CAST(creditcard AS STRING),
        'nbr',
        '{INTERNAL_OBJECT}',
        'creditcard'
      ) AS creditcard,
      thales_protect_by_object_and_column(
        CAST(creditcardcode AS STRING),
        'nbr',
        '{INTERNAL_OBJECT}',
        'creditcardcode'
      ) AS creditcardcode,
      thales_protect_by_object_and_column(
        ssn,
        'nbr',
        '{INTERNAL_OBJECT}',
        'ssn'
      ) AS ssn
    FROM {SOURCE_TABLE}
    """
)

display(spark.sql(f"SELECT * FROM {TEMP_VIEW_NAME} LIMIT 5"))

# COMMAND ----------

print(
    "Skipping persistent VIEW creation. "
    "Session-registered Java UDFs can back TEMP VIEWs and CTAS tables, but not persistent VIEWs."
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {CTAS_TABLE_NAME} AS
    SELECT
      custid,
      name,
      thales_protect_by_object_and_column(
        address,
        'char',
        '{INTERNAL_OBJECT}',
        'address'
      ) AS address,
      city,
      state,
      zip,
      phone,
      thales_protect_by_object_and_column(
        email,
        'char',
        '{INTERNAL_OBJECT}',
        'email'
      ) AS email,
      dob,
      thales_protect_by_object_and_column(
        CAST(creditcard AS STRING),
        'nbr',
        '{INTERNAL_OBJECT}',
        'creditcard'
      ) AS creditcard,
      thales_protect_by_object_and_column(
        CAST(creditcardcode AS STRING),
        'nbr',
        '{INTERNAL_OBJECT}',
        'creditcardcode'
      ) AS creditcardcode,
      thales_protect_by_object_and_column(
        ssn,
        'nbr',
        '{INTERNAL_OBJECT}',
        'ssn'
      ) AS ssn
    FROM {SOURCE_TABLE}
    """
)

display(spark.sql(f"SELECT * FROM {CTAS_TABLE_NAME} LIMIT 5"))

# COMMAND ----------

# Lightweight external check, preserved from the original notebook.
spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {EXTERNAL_HEADER_ONLY_VIEW_NAME} AS
    SELECT
      custid,
      name,
      thales_protect_by_object_and_column_with_external_header(
        address,
        'char',
        '{EXTERNAL_OBJECT}',
        'address'
      ).external_header AS address_header,
      city,
      state,
      zip,
      phone,
      thales_protect_by_object_and_column_with_external_header(
        email,
        'char',
        '{EXTERNAL_OBJECT}',
        'email'
      ).external_header AS email_header,
      dob,
      thales_protect_by_object_and_column_with_external_header(
        CAST(ssn AS STRING),
        'nbr',
        '{EXTERNAL_OBJECT}',
        'ssn'
      ).external_header AS ssn_header
    FROM {SOURCE_TABLE}
    """
)

display(spark.sql(f"SELECT * FROM {EXTERNAL_HEADER_ONLY_VIEW_NAME} LIMIT 5"))

# COMMAND ----------

# Full external protect round trip, closer to plaintext_setup.sql.
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {EXTERNAL_ROUND_TRIP_TABLE_NAME} AS
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
        thales_protect_by_object_and_column_with_external_header(
          CAST(address AS STRING),
          'char',
          '{EXTERNAL_OBJECT}',
          'address'
        ) AS protected_address,
        city,
        state,
        zip,
        phone,
        thales_protect_by_object_and_column_with_external_header(
          CAST(email AS STRING),
          'char',
          '{EXTERNAL_OBJECT}',
          'email'
        ) AS protected_email,
        dob,
        thales_protect_by_object_and_column_with_external_header(
          CAST(creditcard AS STRING),
          'nbr',
          '{EXTERNAL_OBJECT}',
          'creditcard'
        ) AS protected_creditcard,
        thales_protect_by_object_and_column_with_external_header(
          CAST(creditcardcode AS STRING),
          'nbr',
          '{EXTERNAL_OBJECT}',
          'creditcardcode'
        ) AS protected_creditcardcode,
        thales_protect_by_object_and_column_with_external_header(
          CAST(ssn AS STRING),
          'nbr',
          '{EXTERNAL_OBJECT}',
          'ssn'
        ) AS protected_ssn
      FROM {SOURCE_TABLE}
    ) s
    """
)

display(spark.sql(f"SELECT * FROM {EXTERNAL_ROUND_TRIP_TABLE_NAME} LIMIT 5"))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {EXTERNAL_REVEALED_VIEW_NAME} AS
    SELECT
      custid,
      name,
      thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(address AS STRING),
        CAST(address_header AS STRING),
        'char',
        '{EXTERNAL_OBJECT}',
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
        '{EXTERNAL_OBJECT}',
        'email',
        current_user()
      ) AS email,
      dob,
      CAST(
        thales_reveal_by_object_and_column_with_external_header_and_user(
          CAST(creditcard AS STRING),
          CAST(creditcard_header AS STRING),
          'nbr',
          '{EXTERNAL_OBJECT}',
          'creditcard',
          current_user()
        ) AS DECIMAL(25,0)
      ) AS creditcard,
      CAST(
        thales_reveal_by_object_and_column_with_external_header_and_user(
          CAST(creditcardcode AS STRING),
          CAST(creditcardcode_header AS STRING),
          'nbr',
          '{EXTERNAL_OBJECT}',
          'creditcardcode',
          current_user()
        ) AS INT
      ) AS creditcardcode,
      thales_reveal_by_object_and_column_with_external_header_and_user(
        CAST(ssn AS STRING),
        CAST(ssn_header AS STRING),
        'nbr',
        '{EXTERNAL_OBJECT}',
        'ssn',
        current_user()
      ) AS ssn
    FROM {EXTERNAL_ROUND_TRIP_TABLE_NAME}
    """
)

display(spark.sql(f"SELECT * FROM {EXTERNAL_REVEALED_VIEW_NAME} LIMIT 5"))

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW v_java_udf_internal_revealed_demo AS
    SELECT
      custid,
      name,
      thales_reveal_by_object_and_column_with_user(
        address,
        'char',
        '{INTERNAL_OBJECT}',
        'address',
        current_user()
      ) AS address,
      city,
      state,
      zip,
      phone,
      thales_reveal_by_object_and_column_with_user(
        email,
        'char',
        '{INTERNAL_OBJECT}',
        'email',
        current_user()
      ) AS email,
      dob,
      CAST(
        thales_reveal_by_object_and_column_with_user(
          creditcard,
          'nbr',
          '{INTERNAL_OBJECT}',
          'creditcard',
          current_user()
        ) AS DECIMAL(25,0)
      ) AS creditcard,
      CAST(
        thales_reveal_by_object_and_column_with_user(
          creditcardcode,
          'nbr',
          '{INTERNAL_OBJECT}',
          'creditcardcode',
          current_user()
        ) AS INT
      ) AS creditcardcode,
      thales_reveal_by_object_and_column_with_user(
        ssn,
        'nbr',
        '{INTERNAL_OBJECT}',
        'ssn',
        current_user()
      ) AS ssn
    FROM {TEMP_VIEW_NAME}
    """
)

display(spark.sql("SELECT * FROM v_java_udf_internal_revealed_demo LIMIT 5"))

# COMMAND ----------

print(
    "Java UDF SQL external round-trip examples completed. "
    "This notebook demonstrated internal temp views, CTAS, external header-only output, "
    "and a full external protect/reveal round trip."
)
