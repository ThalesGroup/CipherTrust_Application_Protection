# Databricks Structured Streaming examples for the current Java UDF path.
#
# Use this path when you want compute-cluster streaming ETL in raw Spark SQL /
# DataFrame style and are comfortable registering session-scoped Java UDFs.
#
# Demo note:
# these examples use `availableNow=True` so they process the currently available
# source rows and then stop. That is much easier to validate with small demo
# tables than an always-on streaming query.

from pyspark.sql import types as T


CATALOG = "my_catalog"
SCHEMA = "my_schema"

SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
PROTECTED_INTERNAL_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_stream_java_udf"
PROTECTED_NONE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_protected_none_stream_java_udf"

INTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
NONE_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_none"

INTERNAL_CHECKPOINT = (
    f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_protected_internal_stream_java_udf"
)
NONE_CHECKPOINT = (
    f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_protected_none_stream_java_udf"
)


spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column",
    "com.thales.databricks.integration.udf.ThalesProtectByObjectAndColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_object_and_column_with_user",
    "com.thales.databricks.integration.udf.ThalesRevealByObjectAndColumnWithUserUdf",
    T.StringType(),
)


# Primary streaming ETL pattern: protect as data lands in the streaming sink.
customer_stream = spark.readStream.table(SOURCE_TABLE)

protected_internal_stream = customer_stream.selectExpr(
    "custid",
    "name",
    "thales_protect_by_object_and_column(address, 'char', "
    f"'{INTERNAL_OBJECT}', 'address') as address",
    "city",
    "state",
    "zip",
    "phone",
    "thales_protect_by_object_and_column(email, 'char', "
    f"'{INTERNAL_OBJECT}', 'email') as email",
    "dob",
    "thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', "
    f"'{INTERNAL_OBJECT}', 'creditcard') as creditcard",
    "thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', "
    f"'{INTERNAL_OBJECT}', 'creditcardcode') as creditcardcode",
    "thales_protect_by_object_and_column(ssn, 'nbr', "
    f"'{INTERNAL_OBJECT}', 'ssn') as ssn",
)

protected_internal_query = (
    protected_internal_stream.writeStream.format("delta")
    .trigger(availableNow=True)
    .outputMode("append")
    .option("checkpointLocation", INTERNAL_CHECKPOINT)
    .toTable(PROTECTED_INTERNAL_TABLE)
)


# Alternate example for the none object mapping.
protected_none_stream = customer_stream.selectExpr(
    "custid",
    "name",
    "thales_protect_by_object_and_column(address, 'char', "
    f"'{NONE_OBJECT}', 'address') as address",
    "city",
    "state",
    "zip",
    "phone",
    "thales_protect_by_object_and_column(email, 'char', "
    f"'{NONE_OBJECT}', 'email') as email",
    "dob",
    "thales_protect_by_object_and_column(CAST(creditcard AS STRING), 'nbr', "
    f"'{NONE_OBJECT}', 'creditcard') as creditcard",
    "thales_protect_by_object_and_column(CAST(creditcardcode AS STRING), 'nbr', "
    f"'{NONE_OBJECT}', 'creditcardcode') as creditcardcode",
    "thales_protect_by_object_and_column(ssn, 'nbr', "
    f"'{NONE_OBJECT}', 'ssn') as ssn",
)

protected_none_query = (
    protected_none_stream.writeStream.format("delta")
    .trigger(availableNow=True)
    .outputMode("append")
    .option("checkpointLocation", NONE_CHECKPOINT)
    .toTable(PROTECTED_NONE_TABLE)
)


# Optional governed reveal pattern:
# instead of calling the low-level reveal UDF inside the streaming transform,
# create a governed UC SQL view and stream from that view downstream.
#
# Example:
# governed_reveal_stream = spark.readStream.table(
#     "my_catalog.my_schema.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized"
# )
# governed_reveal_query = (
#     governed_reveal_stream.writeStream
#     .format("delta")
#     .trigger(availableNow=True)
#     .outputMode("append")
#     .option(
#         "checkpointLocation",
#         f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_reveal_stream_from_uc_view",
#     )
#     .toTable(f"{CATALOG}.{SCHEMA}.plaintext_reveal_stream_from_uc_view")
# )
#
# To stop:
# protected_internal_query.stop()
# protected_none_query.stop()
