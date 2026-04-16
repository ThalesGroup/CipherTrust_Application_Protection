# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster UDF Registration and Smoke Test
# MAGIC
# MAGIC This notebook registers the Java UDF adapters from the shaded jar and
# MAGIC runs quick scalar and bulk smoke tests on a Databricks compute cluster.
# MAGIC
# MAGIC Before running:
# MAGIC
# MAGIC - Attach `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar` or the uploaded jar to the cluster
# MAGIC - Set `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Set `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Ensure the path points to a valid `udfConfig.properties`

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

# Basic environment visibility
config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running the tests."
    )

# COMMAND ----------

# Register scalar UDFs
spark.udf.registerJavaFunction("thales_protect", "ThalesCrdpProtectUdf", T.StringType())
spark.udf.registerJavaFunction("thales_protect_by_column", "ThalesCrdpProtectByColumnUdf", T.StringType())
spark.udf.registerJavaFunction("thales_reveal", "ThalesCrdpRevealUdf", T.StringType())
spark.udf.registerJavaFunction("thales_reveal_by_column", "ThalesCrdpRevealByColumnUdf", T.StringType())
spark.udf.registerJavaFunction("thales_reveal_with_user", "ThalesCrdpRevealWithUserUdf", T.StringType())
spark.udf.registerJavaFunction(
    "thales_reveal_by_column_with_user",
    "ThalesCrdpRevealByColumnWithUserUdf",
    T.StringType(),
)

# Register generic bulk UDFs
spark.udf.registerJavaFunction(
    "thales_protect_bulk",
    "ThalesCrdpProtectBulkUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_protect_bulk_by_column",
    "ThalesCrdpProtectBulkByColumnUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk",
    "ThalesCrdpRevealBulkUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_with_user",
    "ThalesCrdpRevealBulkWithUserUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_column",
    "ThalesCrdpRevealBulkByColumnUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_column_with_user",
    "ThalesCrdpRevealBulkByColumnWithUserUdf",
    T.ArrayType(T.StringType()),
)

# Register hardcoded convenience bulk UDFs
spark.udf.registerJavaFunction(
    "thales_bulk_protect_char",
    "ThalesBulkProtectCharUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_bulk_reveal_char",
    "ThalesBulkRevealCharUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_bulk_protect_nbr",
    "ThalesBulkProtectNbrUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_bulk_reveal_nbr",
    "ThalesBulkRevealNbrUdf",
    T.ArrayType(T.StringType()),
)

print("Thales Java UDFs registered successfully.")

# COMMAND ----------

# Sample source data for smoke tests
test_df = spark.createDataFrame(
    [
        (
            "alice@example.com",
            "123456789",
            ["alice@example.com", "bob@example.com"],
            ["123456789", "987654321"],
        ),
        (
            "carol@example.com",
            "112233445",
            ["carol@example.com", "dave@example.com"],
            ["112233445", "556677889"],
        ),
    ],
    schema=T.StructType(
        [
            T.StructField("email", T.StringType(), True),
            T.StructField("employee_id", T.StringType(), True),
            T.StructField("email_batch", T.ArrayType(T.StringType()), True),
            T.StructField("employee_batch", T.ArrayType(T.StringType()), True),
        ]
    ),
)

display(test_df)

# COMMAND ----------

# Scalar protect smoke test
scalar_protect_df = test_df.selectExpr(
    "email",
    "thales_protect(email, 'char') as email_protected_legacy",
    "thales_protect_by_column(email, 'char', 'email') as email_protected_by_column",
    "employee_id",
    "thales_protect_by_column(employee_id, 'nbr', 'employee_id') as employee_id_protected_by_column",
)

display(scalar_protect_df)

# COMMAND ----------

# Bulk protect smoke test
bulk_protect_df = test_df.selectExpr(
    "email_batch",
    "thales_bulk_protect_char(email_batch) as email_batch_protected_hardcoded",
    "thales_protect_bulk(email_batch, 'char') as email_batch_protected_legacy",
    "thales_protect_bulk_by_column(email_batch, 'char', 'email') as email_batch_protected_by_column",
    "employee_batch",
    "thales_bulk_protect_nbr(employee_batch) as employee_batch_protected_hardcoded",
    "thales_protect_bulk_by_column(employee_batch, 'nbr', 'employee_id') as employee_batch_protected_by_column",
)

display(bulk_protect_df)

# COMMAND ----------

# Round-trip scalar reveal test for one row.
# Replace the reveal user expression if your secure reveal model expects a
# different user string than the Databricks session identity.
round_trip_scalar_df = (
    test_df.selectExpr(
        "email",
        "thales_protect_by_column(email, 'char', 'email') as email_token",
        "employee_id",
        "thales_protect_by_column(employee_id, 'nbr', 'employee_id') as employee_token",
    )
    .selectExpr(
        "email",
        "email_token",
        "thales_reveal_by_column_with_user(email_token, 'char', 'email', current_user()) as email_revealed",
        "employee_id",
        "employee_token",
        "thales_reveal_by_column_with_user(employee_token, 'nbr', 'employee_id', current_user()) as employee_revealed",
    )
)

display(round_trip_scalar_df)

# COMMAND ----------

# Round-trip bulk reveal test
round_trip_bulk_df = (
    test_df.selectExpr(
        "email_batch",
        "thales_protect_bulk_by_column(email_batch, 'char', 'email') as email_token_batch",
        "employee_batch",
        "thales_protect_bulk_by_column(employee_batch, 'nbr', 'employee_id') as employee_token_batch",
    )
    .selectExpr(
        "email_batch",
        "email_token_batch",
        "thales_reveal_bulk_by_column_with_user(email_token_batch, 'char', 'email', current_user()) as email_revealed_batch",
        "employee_batch",
        "employee_token_batch",
        "thales_reveal_bulk_by_column_with_user(employee_token_batch, 'nbr', 'employee_id', current_user()) as employee_revealed_batch",
    )
)

display(round_trip_bulk_df)

# COMMAND ----------

# Optional SQL examples. Uncomment and run as needed.
#
# spark.sql(\"\"\"
# SELECT thales_protect_by_column('alice@example.com', 'char', 'email') AS email_token
# \"\"\").show(truncate=False)
#
# spark.sql(\"\"\"
# SELECT thales_reveal_by_column_with_user(
#   thales_protect_by_column('alice@example.com', 'char', 'email'),
#   'char',
#   'email',
#   current_user()
# ) AS email_cleartext
# \"\"\").show(truncate=False)

# COMMAND ----------

print(
    "Smoke test notebook completed. Review the displayed results to confirm "
    "protect and reveal round-trips, column-aware policy selection, and bulk behavior."
)
