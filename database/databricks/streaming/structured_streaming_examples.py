# Databricks Structured Streaming examples for Thales CRDP
#
# This file focuses on the compute-cluster / Spark streaming model.
# Use this path when you want executor-parallel ETL with Java Spark UDFs.

from pyspark.sql import types as T


# Step 1: register Java UDFs in a controlled admin/deployer notebook or job.
spark.udf.registerJavaFunction(
    "thales_protect_by_column",
    "ThalesCrdpProtectByColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_column_with_user",
    "ThalesCrdpRevealByColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_column_with_user",
    "ThalesCrdpRevealBulkByColumnWithUserUdf",
    T.ArrayType(T.StringType()),
)


# Step 2: read a cleartext Delta table as a stream for ETL protection.
customer_stream = spark.readStream.table("main.raw.customer_cleartext")


# Step 3A: primary ETL pattern: protect row-based data in the streaming query.
protected_customer_stream = customer_stream.selectExpr(
    "customer_id",
    "first_name",
    "last_name",
    "customer_status",
    "created_ts",
    "thales_protect_by_column(email, 'char', 'email') as email_token",
)


# Step 4A: write the protected stream to a Delta target table.
customer_protect_query = (
    protected_customer_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_protect_stream")
    .toTable("main.raw.customer_tokens")
)


# Step 3B: governed reveal pattern for downstream consumption.
# Instead of exposing the low-level reveal call in the stream transform, create
# the secured view in a controlled admin/deployer context and stream from that
# view when reveal is required downstream.
#
# Example prerequisite:
# CREATE OR REPLACE VIEW main.security.v_customer_reveal AS
# SELECT
#   customer_id,
#   first_name,
#   last_name,
#   customer_status,
#   created_ts,
#   thales_reveal_by_column_with_user(
#     email_token,
#     'char',
#     'email',
#     current_user()
#   ) AS email
# FROM main.raw.customer_tokens;
#
# In Databricks Runtime 14.1+ you can stream from a Unity Catalog view backed by
# Delta tables, subject to Databricks view limitations for streaming sources.
governed_customer_stream = spark.readStream.table("main.security.v_customer_reveal")

# Step 4B: write the governed-view stream to a downstream Delta target.
governed_customer_query = (
    governed_customer_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_reveal_stream_from_view")
    .toTable("main.security.customer_reveal_stream_from_view")
)


# Optional array-based protection example.
customer_array_stream = spark.readStream.table("main.raw.customer_cleartext_arrays")

spark.udf.registerJavaFunction(
    "thales_protect_bulk_by_column",
    "ThalesCrdpProtectBulkByColumnUdf",
    T.ArrayType(T.StringType()),
)

protected_customer_array_stream = customer_array_stream.selectExpr(
    "customer_group_id",
    "snapshot_ts",
    "thales_protect_bulk_by_column(email_array, 'char', 'email') as email_token_array",
)

customer_array_protect_query = (
    protected_customer_array_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_array_protect_stream")
    .toTable("main.raw.customer_token_arrays")
)

# Governed array-based alternative:
# governed_customer_array_stream = spark.readStream.table("main.security.v_customer_array_reveal")
# governed_customer_array_query = (
#     governed_customer_array_stream.writeStream
#     .format("delta")
#     .outputMode("append")
#     .option("checkpointLocation", "/Volumes/main/security/checkpoints/customer_array_reveal_stream_from_view")
#     .toTable("main.security.customer_array_reveal_stream_from_view")
# )

# To stop:
# customer_protect_query.stop()
# governed_customer_query.stop()
# customer_array_protect_query.stop()
