# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster UDF Registration and Smoke Test
# MAGIC
# MAGIC This notebook registers the Java UDF adapters from the shaded jar and
# MAGIC runs quick scalar and bulk smoke tests on a Databricks compute cluster.
# MAGIC
# MAGIC If `udfConfig.properties` has TLS enabled, this notebook is also the
# MAGIC recommended Java compute-cluster TLS smoke test.
# MAGIC
# MAGIC Before running:
# MAGIC
# MAGIC - Attach `target/thales.databricks.udf-0.0.1-SNAPSHOT-all.jar` or the uploaded jar to the cluster
# MAGIC - Set `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Set `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Ensure the path points to a valid `udfConfig.properties`
# MAGIC - If testing TLS, ensure the init script copied the CA file and PKCS12
# MAGIC   client certificate into `/tmp/thales_config`

# COMMAND ----------

from pathlib import Path

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


def load_batch_size_from_properties(config_path):
    default_batch_size = 1000

    if not config_path:
        return default_batch_size, None, f"UDF_CONFIG_VOLUME_PATH not set; using fallback {default_batch_size}."

    path = Path(config_path)
    if not path.exists():
        return default_batch_size, None, f"Config file not found at {config_path}; using fallback {default_batch_size}."

    raw_batch_size = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "BATCH_SIZE":
            raw_batch_size = value.strip()
            break

    if raw_batch_size is None:
        return default_batch_size, None, f"BATCH_SIZE not present in config file; using fallback {default_batch_size}."

    try:
        parsed_batch_size = int(raw_batch_size)
    except ValueError:
        return default_batch_size, raw_batch_size, (
            f"Invalid BATCH_SIZE '{raw_batch_size}' in config file; using fallback {default_batch_size}."
        )

    if parsed_batch_size <= 0:
        return default_batch_size, raw_batch_size, (
            f"Invalid BATCH_SIZE '{raw_batch_size}' in config file; using fallback {default_batch_size}."
        )

    return parsed_batch_size, raw_batch_size, None


config_batch_size, raw_config_batch_size, batch_size_warning = load_batch_size_from_properties(config_path)
print("Raw BATCH_SIZE setting in config file:", raw_config_batch_size if raw_config_batch_size is not None else "<missing>")
print("Effective BATCH_SIZE used by notebook/runtime:", config_batch_size)
if batch_size_warning:
    print("WARNING:", batch_size_warning)

# COMMAND ----------

# Register scalar UDFs
external_protect_schema = T.StructType(
    [
        T.StructField("protected_value", T.StringType(), True),
        T.StructField("external_header", T.StringType(), True),
    ]
)

spark.udf.registerJavaFunction("thales_protect", "ThalesCrdpProtectUdf", T.StringType())
spark.udf.registerJavaFunction("thales_protect_by_column", "ThalesCrdpProtectByColumnUdf", T.StringType())
spark.udf.registerJavaFunction(
    "thales_protect_integer_by_column",
    "ThalesCrdpProtectIntegerByColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_protect_long_by_column",
    "ThalesCrdpProtectLongByColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_protect_decimal_by_column",
    "ThalesCrdpProtectDecimalByColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column",
    "ThalesCrdpProtectByObjectAndColumnUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_protect_by_column_with_external_header",
    "ThalesCrdpProtectByColumnWithExternalHeaderUdf",
    external_protect_schema,
)
spark.udf.registerJavaFunction(
    "thales_protect_by_object_and_column_with_external_header",
    "ThalesCrdpProtectByObjectAndColumnWithExternalHeaderUdf",
    external_protect_schema,
)
spark.udf.registerJavaFunction("thales_reveal", "ThalesCrdpRevealUdf", T.StringType())
spark.udf.registerJavaFunction("thales_reveal_by_column", "ThalesCrdpRevealByColumnUdf", T.StringType())
spark.udf.registerJavaFunction("thales_reveal_with_user", "ThalesCrdpRevealWithUserUdf", T.StringType())
spark.udf.registerJavaFunction(
    "thales_reveal_integer_by_column_with_user",
    "ThalesCrdpRevealIntegerByColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_long_by_column_with_user",
    "ThalesCrdpRevealLongByColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_decimal_by_column_with_user",
    "ThalesCrdpRevealDecimalByColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_column_with_user",
    "ThalesCrdpRevealByColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_column_with_external_header_and_user",
    "ThalesCrdpRevealByColumnWithExternalHeaderAndUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_object_and_column_with_user",
    "ThalesCrdpRevealByObjectAndColumnWithUserUdf",
    T.StringType(),
)
spark.udf.registerJavaFunction(
    "thales_reveal_by_object_and_column_with_external_header_and_user",
    "ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf",
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
    "thales_protect_bulk_by_object_and_column",
    "ThalesCrdpProtectBulkByObjectAndColumnUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_protect_bulk_by_object_and_column_with_external_header",
    "ThalesCrdpProtectBulkByObjectAndColumnWithExternalHeaderUdf",
    T.ArrayType(external_protect_schema),
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
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_column_with_external_header_and_user",
    "ThalesCrdpRevealBulkByColumnWithExternalHeaderAndUserUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_object_and_column_with_user",
    "ThalesCrdpRevealBulkByObjectAndColumnWithUserUdf",
    T.ArrayType(T.StringType()),
)
spark.udf.registerJavaFunction(
    "thales_reveal_bulk_by_object_and_column_with_external_header_and_user",
    "ThalesCrdpRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf",
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

# Sample source data for smoke tests.
# Keep the legacy/global column-aware examples aligned with columns that exist in
# the active global COLUMN_PROFILES mappings. Object-aware examples later in this
# notebook are the right place to demonstrate per-table profile differences.
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
            T.StructField("ssn", T.StringType(), True),
            T.StructField("email_batch", T.ArrayType(T.StringType()), True),
            T.StructField("ssn_batch", T.ArrayType(T.StringType()), True),
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
    "ssn",
    "thales_protect_by_column(ssn, 'nbr', 'ssn') as ssn_protected_by_column",
)

display(scalar_protect_df)

# COMMAND ----------

# Bulk protect smoke test
# Note:
# - This section intentionally keeps the legacy column-aware bulk path visible.
# - The object-aware bulk signatures are exercised later in this notebook.
# - `thales_bulk_protect_char(...)` and `thales_bulk_protect_nbr(...)` are
#   legacy hardcoded convenience adapters:
#   - they hardcode the datatype
#   - they do not know the column name
#   - they do not know the object/table name
#   - they therefore resolve policy through the legacy datatype-default path
# - `thales_protect_bulk(...)` is also legacy bulk:
#   - it knows the datatype
#   - it still does not know the column or object
#   - it also resolves policy through the legacy datatype-default path
# - `thales_protect_bulk_by_column(...)` is the older column-aware bulk path:
#   - it knows the datatype and column name
#   - it can resolve through `column.<column>.profile` or `COLUMN_PROFILES`
#   - it still does not use `protect.object.<object>`
bulk_protect_df = test_df.selectExpr(
    "email_batch",
    "thales_bulk_protect_char(email_batch) as email_batch_protected_hardcoded",
    "thales_protect_bulk(email_batch, 'char') as email_batch_protected_legacy",
    "thales_protect_bulk_by_column(email_batch, 'char', 'email') as email_batch_protected_by_column",
    "ssn_batch",
    "thales_bulk_protect_nbr(ssn_batch) as ssn_batch_protected_hardcoded",
    "thales_protect_bulk_by_column(ssn_batch, 'nbr', 'ssn') as ssn_batch_protected_by_column",
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
        "ssn",
        "thales_protect_by_column(ssn, 'nbr', 'ssn') as ssn_token",
    )
    .selectExpr(
        "email",
        "email_token",
        "thales_reveal_by_column_with_user(email_token, 'char', 'email', current_user()) as email_revealed",
        "ssn",
        "ssn_token",
        "thales_reveal_by_column_with_user(ssn_token, 'nbr', 'ssn', current_user()) as ssn_revealed",
    )
)

display(round_trip_scalar_df)

# COMMAND ----------

# External scalar protect/reveal smoke test
# Note:
# - This example uses the object-aware external mapping so it truly exercises
#   the external policy path instead of falling back to global
#   `COLUMN_PROFILES`.
# - A real customer external-table pattern should persist a sibling header
#   column and pass that real row-level value into reveal.
external_round_trip_df = (
    test_df.selectExpr(
        "email",
        "thales_protect_by_object_and_column_with_external_header(email, 'char', 'my_catalog.my_schema.plaintext_protected_external', 'email') as email_external_token"
    )
    .selectExpr(
        "email",
        "email_external_token.protected_value as email_token",
        "email_external_token.external_header as email_header",
        "thales_reveal_by_object_and_column_with_external_header_and_user(email_external_token.protected_value, email_external_token.external_header, 'char', 'my_catalog.my_schema.plaintext_protected_external', 'email', current_user()) as email_revealed"
    )
)

display(external_round_trip_df)

# COMMAND ----------

# Round-trip bulk reveal test
round_trip_bulk_df = (
    test_df.selectExpr(
        "email_batch",
        "thales_protect_bulk_by_column(email_batch, 'char', 'email') as email_token_batch",
        "ssn_batch",
        "thales_protect_bulk_by_column(ssn_batch, 'nbr', 'ssn') as ssn_token_batch",
    )
    .selectExpr(
        "email_batch",
        "email_token_batch",
        "thales_reveal_bulk_by_column_with_user(email_token_batch, 'char', 'email', current_user()) as email_revealed_batch",
        "ssn_batch",
        "ssn_token_batch",
        "thales_reveal_bulk_by_column_with_user(ssn_token_batch, 'nbr', 'ssn', current_user()) as ssn_revealed_batch",
    )
)

display(round_trip_bulk_df)

# COMMAND ----------

# External bulk reveal test
# Note:
# - This now uses the true object-aware bulk external protect path so the same
#   object-specific resolution model is exercised for protect and reveal.
external_bulk_round_trip_df = (
    test_df.selectExpr(
        "email_batch",
        """thales_protect_bulk_by_object_and_column_with_external_header(
            email_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_external_arrays',
            'email'
        ) as email_external_batch""",
    )
    .selectExpr(
        "email_batch",
        "transform(email_external_batch, x -> x.protected_value) as email_token_batch",
        "transform(email_external_batch, x -> x.external_header) as email_header_batch",
        """thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
            transform(email_external_batch, x -> x.protected_value),
            transform(email_external_batch, x -> x.external_header),
            'char',
            'my_catalog.my_schema.plaintext_protected_external_arrays',
            'email',
            current_user()
        ) as email_revealed_batch""",
    )
)

display(external_bulk_round_trip_df)

# COMMAND ----------

# Object-aware round-trip smoke test.
#
# Important:
# - The object names below are used as profile-resolution keys only.
# - This cell is not reading from or writing to those real tables.
# - Temporary aliases like `internal_token_preview` are just in-memory DataFrame
#   columns created for the smoke test.
# - In the real setup scripts, those same object names are used because the UDFs
#   are operating on actual protected tables and views.
# - This section depends on the corresponding `protect.object...` mappings being
#   present in `udfConfig.properties`. If those mappings are removed, these
#   object-aware smoke-test cells will fail.
#
# These signatures are used by the setup scripts so internal, external, and
# no-version tables can share the same business column names without depending
# on one global COLUMN_PROFILES mapping.
object_round_trip_df = (
    test_df.selectExpr(
        "email",
        """thales_protect_by_object_and_column(
            email,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal',
            'email'
        ) as internal_token_preview""",
        """thales_protect_by_object_and_column_with_external_header(
            email,
            'char',
            'my_catalog.my_schema.plaintext_protected_external',
            'email'
        ) as external_token_preview""",
        """thales_protect_by_object_and_column(
            email,
            'char',
            'my_catalog.my_schema.plaintext_protected_none',
            'email'
        ) as none_token_preview""",
    )
    .selectExpr(
        "email",
        """thales_reveal_by_object_and_column_with_user(
            internal_token_preview,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal',
            'email',
            current_user()
        ) as internal_email_revealed""",
        """thales_reveal_by_object_and_column_with_external_header_and_user(
            external_token_preview.protected_value,
            external_token_preview.external_header,
            'char',
            'my_catalog.my_schema.plaintext_protected_external',
            'email',
            current_user()
        ) as external_email_revealed""",
        """thales_reveal_by_object_and_column_with_user(
            none_token_preview,
            'char',
            'my_catalog.my_schema.plaintext_protected_none',
            'email',
            current_user()
        ) as none_email_revealed""",
    )
)

display(object_round_trip_df)

# COMMAND ----------

# Object-aware bulk round-trip smoke test for internal, external, and none.
object_bulk_round_trip_df = (
    test_df.selectExpr(
        "email_batch",
        """thales_protect_bulk_by_object_and_column(
            email_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal_arrays',
            'email'
        ) as internal_email_token_batch""",
        """thales_protect_bulk_by_object_and_column_with_external_header(
            email_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_external_arrays',
            'email'
        ) as external_email_token_batch""",
        """thales_protect_bulk_by_object_and_column(
            email_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_none_arrays',
            'email'
        ) as none_email_token_batch""",
    )
    .selectExpr(
        "email_batch",
        """thales_reveal_bulk_by_object_and_column_with_user(
            internal_email_token_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_internal_arrays',
            'email',
            current_user()
        ) as internal_email_revealed_batch""",
        """thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
            transform(external_email_token_batch, x -> x.protected_value),
            transform(external_email_token_batch, x -> x.external_header),
            'char',
            'my_catalog.my_schema.plaintext_protected_external_arrays',
            'email',
            current_user()
        ) as external_email_revealed_batch""",
        """thales_reveal_bulk_by_object_and_column_with_user(
            none_email_token_batch,
            'char',
            'my_catalog.my_schema.plaintext_protected_none_arrays',
            'email',
            current_user()
        ) as none_email_revealed_batch""",
    )
)

display(object_bulk_round_trip_df)

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
