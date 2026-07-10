# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Cluster Java UDF SQL Examples
# MAGIC
# MAGIC This notebook shows the Java jar / UDF path in the most SQL-shaped way:
# MAGIC
# MAGIC - temp view creation
# MAGIC - why temp views work but persistent views do not with session-registered Java UDFs
# MAGIC - CTAS table creation
# MAGIC
# MAGIC Use this when a team wants raw Spark SQL on a compute cluster rather than
# MAGIC the Python wheel / helper API.

# COMMAND ----------

# MAGIC %run ../../smoke_tests/register_java_udfs


# COMMAND ----------

CATALOG = "my_catalog"
SCHEMA = "my_schema"

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
INTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
NONE_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"
EXTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"

TEMP_VIEW_NAME = "v_java_udf_internal_protected_demo"
CTAS_TABLE_NAME = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_java_udf_ctas_demo"
EXTERNAL_VIEW_NAME = f"{CATALOG}.{SCHEMA}.v_java_udf_external_protected_demo"

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

# COMMAND ----------

register_java_udfs()


# COMMAND ----------

display(spark.sql(f"SELECT * FROM {SOURCE_TABLE} LIMIT 5"))

# COMMAND ----------

# Temp view example.
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

# Persistent-view note:
#
# `spark.udf.registerJavaFunction(...)` creates a temporary/session-scoped
# function. Spark therefore does not allow a persistent view to reference that
# function.
#
# Practical meaning:
# - TEMP VIEW works
# - CTAS / INSERT OVERWRITE into a physical table works
# - persistent VIEW over a temp Java function does not work
#
# For a persistent governed function/view model, use the Unity Catalog Python
# UDF path instead.
print(
    "Skipping persistent VIEW creation. "
    "Session-registered Java UDFs can back TEMP VIEWs and CTAS tables, but not persistent VIEWs."
)

# COMMAND ----------

# CTAS example.
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

# External temp-view example with sibling header columns.
spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW {EXTERNAL_VIEW_NAME.split('.')[-1]} AS
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

display(spark.sql(f"SELECT * FROM {EXTERNAL_VIEW_NAME.split('.')[-1]} LIMIT 5"))

# COMMAND ----------

# Reveal examples from the temp view.
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
    "Java UDF SQL examples completed. "
    "This notebook demonstrated temp views, CTAS tables, external temp views, and reveal."
)
