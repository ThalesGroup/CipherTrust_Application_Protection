# Databricks notebook source
# MAGIC %md
# MAGIC # Register Java UDFs
# MAGIC
# MAGIC Shared helper notebook for registering the public Java UDF surface used by
# MAGIC the compute-cluster smoke tests and Java SQL-shaped example notebooks.

# COMMAND ----------

from pyspark.sql import types as T

# COMMAND ----------

EXTERNAL_PROTECT_SCHEMA = T.StructType(
    [
        T.StructField("protected_value", T.StringType(), True),
        T.StructField("external_header", T.StringType(), True),
    ]
)

BULK_REVEAL_SCHEMA = T.ArrayType(T.StringType())

JAVA_UDF_REGISTRATIONS = [
    (
        "thales_protect_by_object_and_column",
        "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnUdf",
        T.StringType(),
    ),
    (
        "thales_reveal_by_object_and_column_with_user",
        "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithUserUdf",
        T.StringType(),
    ),
    (
        "thales_protect_by_object_and_column_with_external_header",
        "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnWithExternalHeaderUdf",
        EXTERNAL_PROTECT_SCHEMA,
    ),
    (
        "thales_reveal_by_object_and_column_with_external_header_and_user",
        "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithExternalHeaderAndUserUdf",
        T.StringType(),
    ),
    (
        "thales_protect_bulk_by_object_and_column",
        "com.thales.databricks.integration.udf.ThalesProtectBulkByObjectAndColumnUdf",
        T.ArrayType(T.StringType()),
    ),
    (
        "thales_protect_bulk_by_object_and_column_with_external_header",
        "com.thales.databricks.integration.udf.ThalesProtectBulkByObjectAndColumnWithExternalHeaderUdf",
        T.ArrayType(EXTERNAL_PROTECT_SCHEMA),
    ),
    (
        "thales_reveal_bulk_by_object_and_column_with_user",
        "com.thales.databricks.integration.udf.ThalesRevealBulkByObjectAndColumnWithUserUdf",
        BULK_REVEAL_SCHEMA,
    ),
    (
        "thales_reveal_bulk_by_object_and_column_with_external_header_and_user",
        "com.thales.databricks.integration.udf.ThalesRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf",
        BULK_REVEAL_SCHEMA,
    ),
]


def register_java_udfs(include_bulk_reveal: bool = True) -> list[str]:
    registered = []
    for function_name, class_name, return_type in JAVA_UDF_REGISTRATIONS:
        if not include_bulk_reveal and function_name.startswith("thales_reveal_bulk_"):
            continue
        spark.udf.registerJavaFunction(function_name, class_name, return_type)
        registered.append(function_name)
    print("Registered Java UDFs:")
    for name in registered:
        print("-", name)
    return registered


print(
    "register_java_udfs.py loaded. "
    "Call register_java_udfs() or register_java_udfs(include_bulk_reveal=False)."
)
