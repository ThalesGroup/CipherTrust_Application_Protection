# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Compute Cluster Java UDF Smoke Test
# MAGIC
# MAGIC This notebook validates the new minimal Java UDF surface packaged in:
# MAGIC
# MAGIC - `target/thales-databricks-integration-0.1.0-SNAPSHOT.jar`
# MAGIC
# MAGIC It focuses on the Java capabilities we decided to keep because they best
# MAGIC support CTAS / batch SQL patterns and high-throughput compute-cluster
# MAGIC execution:
# MAGIC
# MAGIC - `thales_protect_by_object_and_column`
# MAGIC - `thales_reveal_by_object_and_column_with_user`
# MAGIC - `thales_protect_by_object_and_column_with_external_header`
# MAGIC - `thales_reveal_by_object_and_column_with_external_header_and_user`
# MAGIC - `thales_protect_bulk_by_object_and_column`
# MAGIC - `thales_reveal_bulk_by_object_and_column_with_user`
# MAGIC - `thales_protect_bulk_by_object_and_column_with_external_header`
# MAGIC - `thales_reveal_bulk_by_object_and_column_with_external_header_and_user`
# MAGIC
# MAGIC Before running:
# MAGIC
# MAGIC - Attach the new jar to the compute cluster
# MAGIC - Set `spark.driverEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Set `spark.executorEnv.UDF_CONFIG_VOLUME_PATH`
# MAGIC - Ensure the path points to a valid `udfConfig.properties`
# MAGIC - If testing TLS, ensure the init script copied the CA file and PKCS12
# MAGIC   client certificate into `/tmp/thales_config`
# MAGIC
# MAGIC This smoke test is self-contained and does not require `plaintext_setup.sql`
# MAGIC to run first.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T
from utils.runtime_diagnostics import (
    print_column_profile_diagnostics,
    print_effective_profile_resolution_diagnostics,
    load_runtime_properties,
    print_object_mapping_diagnostics,
    print_profile_alias_diagnostics,
    print_runtime_diagnostics,
)

# COMMAND ----------

config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running the tests."
    )

def infer_policy_mode(mapping_value):
    normalized = str(mapping_value or "").strip().lower()
    if "external" in normalized:
        return "external"
    if "internal" in normalized:
        return "internal"
    if "none" in normalized:
        return "none"
    return None


def _parse_configured_columns(mapping_value):
    columns = []
    for entry in str(mapping_value or "").split(","):
        item = entry.strip()
        if not item or "|" not in item:
            continue
        column_name, _profile_name = item.split("|", 1)
        columns.append(column_name.strip().lower())
    return columns


def resolve_smoke_test_object(runtime_settings, mode, require_array, required_columns=None):
    required_columns = [str(column).strip().lower() for column in (required_columns or []) if str(column).strip()]
    matches = []
    for key, value in runtime_settings.items():
        if not key.startswith("protect.object."):
            continue
        object_name = key[len("protect.object."):].strip()
        is_array = object_name.lower().endswith("_arrays")
        if is_array != require_array:
            continue
        if infer_policy_mode(value) == mode:
            configured_columns = _parse_configured_columns(value)
            column_match_count = sum(1 for column in required_columns if column in configured_columns)
            preferred_name = "plaintext" in object_name.lower()
            matches.append((column_match_count, preferred_name, object_name))
    if not matches:
        object_type = "array" if require_array else "non-array"
        raise ValueError(
            f"Could not find a configured {object_type} protect.object.* mapping for mode={mode!r}."
        )
    if required_columns:
        matching_columns = [match for match in matches if match[0] == len(required_columns)]
        if matching_columns:
            matches = matching_columns
        else:
            partial_matches = [match for match in matches if match[0] > 0]
            if partial_matches:
                matches = partial_matches
    return sorted(matches, key=lambda item: (-item[0], -int(item[1]), item[2]))[0][2]


runtime_settings = load_runtime_properties(
    config_path,
    defaults={
        "BATCH_SIZE": "1000",
        "CRDP_API_VERSION": "v2",
        "SPARK_GROUP_SIZE": "<not set>",
        "CRDP_V2_MAX_ITEMS_PER_REQUEST": "<not set>",
        "CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST": "<not set>",
        "CRDP_V2_ENABLE_MULTI_POLICY": "<not set>",
    },
)
print_runtime_diagnostics(
    spark,
    label="Java smoke test runtime diagnostics:",
    config_path=config_path,
    runtime_settings=runtime_settings,
    include_debug_flag=True,
)
for key, value in runtime_settings.items():
    print(f"{key}: {value}")

SMOKE_TEST_REQUIRED_COLUMNS = ["email", "ssn"]

INTERNAL_OBJECT = resolve_smoke_test_object(
    runtime_settings, "internal", require_array=False, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)
NONE_OBJECT = resolve_smoke_test_object(
    runtime_settings, "none", require_array=False, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)
EXTERNAL_OBJECT = resolve_smoke_test_object(
    runtime_settings, "external", require_array=False, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)
INTERNAL_ARRAY_OBJECT = resolve_smoke_test_object(
    runtime_settings, "internal", require_array=True, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)
NONE_ARRAY_OBJECT = resolve_smoke_test_object(
    runtime_settings, "none", require_array=True, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)
EXTERNAL_ARRAY_OBJECT = resolve_smoke_test_object(
    runtime_settings, "external", require_array=True, required_columns=SMOKE_TEST_REQUIRED_COLUMNS
)

print("Resolved object mappings:")
print("SMOKE_TEST_REQUIRED_COLUMNS:", SMOKE_TEST_REQUIRED_COLUMNS)
print("INTERNAL_OBJECT:", INTERNAL_OBJECT)
print("NONE_OBJECT:", NONE_OBJECT)
print("EXTERNAL_OBJECT:", EXTERNAL_OBJECT)
print("INTERNAL_ARRAY_OBJECT:", INTERNAL_ARRAY_OBJECT)
print("NONE_ARRAY_OBJECT:", NONE_ARRAY_OBJECT)
print("EXTERNAL_ARRAY_OBJECT:", EXTERNAL_ARRAY_OBJECT)
print_object_mapping_diagnostics(
    runtime_settings,
    [
        INTERNAL_OBJECT,
        NONE_OBJECT,
        EXTERNAL_OBJECT,
        INTERNAL_ARRAY_OBJECT,
        NONE_ARRAY_OBJECT,
        EXTERNAL_ARRAY_OBJECT,
    ],
)
print_profile_alias_diagnostics(
    runtime_settings,
    [
        "TAG.char.internal",
        "TAG.nbr.internal",
        "TAG.char.external",
        "TAG.nbr.external",
        "TAG.char.none",
        "TAG.nbr.none",
    ],
)
print_column_profile_diagnostics(
    runtime_settings,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)
print_effective_profile_resolution_diagnostics(
    runtime_settings,
    INTERNAL_OBJECT,
    [
        "email",
        "address",
        "ssn",
        "creditcard",
        "creditcardcode",
    ],
)

# COMMAND ----------

# MAGIC %run ./register_java_udfs

# COMMAND ----------

register_java_udfs(include_bulk_reveal=True)


# COMMAND ----------

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

# Internal + none scalar round-trip smoke test.
scalar_round_trip_df = (
    test_df.selectExpr(
        "email",
        "ssn",
        f"""thales_protect_by_object_and_column(
            email,
            'char',
            '{INTERNAL_OBJECT}',
            'email'
        ) as internal_email_token""",
        f"""thales_protect_by_object_and_column(
            ssn,
            'nbr',
            '{INTERNAL_OBJECT}',
            'ssn'
        ) as internal_ssn_token""",
        f"""thales_protect_by_object_and_column(
            email,
            'char',
            '{NONE_OBJECT}',
            'email'
        ) as none_email_token""",
    )
    .selectExpr(
        "email",
        "internal_email_token",
        f"""thales_reveal_by_object_and_column_with_user(
            internal_email_token,
            'char',
            '{INTERNAL_OBJECT}',
            'email',
            current_user()
        ) as internal_email_revealed""",
        "ssn",
        "internal_ssn_token",
        f"""thales_reveal_by_object_and_column_with_user(
            internal_ssn_token,
            'nbr',
            '{INTERNAL_OBJECT}',
            'ssn',
            current_user()
        ) as internal_ssn_revealed""",
        "none_email_token",
        f"""thales_reveal_by_object_and_column_with_user(
            none_email_token,
            'char',
            '{NONE_OBJECT}',
            'email',
            current_user()
        ) as none_email_revealed""",
    )
)

display(scalar_round_trip_df)

# COMMAND ----------

# External scalar round-trip smoke test.
external_scalar_round_trip_df = (
    test_df.selectExpr(
        "email",
        f"""thales_protect_by_object_and_column_with_external_header(
            email,
            'char',
            '{EXTERNAL_OBJECT}',
            'email'
        ) as external_email_token""",
    )
    .selectExpr(
        "email",
        "external_email_token.protected_value as email_token",
        "external_email_token.external_header as email_header",
        f"""thales_reveal_by_object_and_column_with_external_header_and_user(
            external_email_token.protected_value,
            external_email_token.external_header,
            'char',
            '{EXTERNAL_OBJECT}',
            'email',
            current_user()
        ) as external_email_revealed""",
    )
)

display(external_scalar_round_trip_df)

# COMMAND ----------

# Internal + none bulk protect + reveal smoke test.
bulk_round_trip_df = test_df.selectExpr(
    "email_batch",
    f"""thales_protect_bulk_by_object_and_column(
        email_batch,
        'char',
        '{INTERNAL_ARRAY_OBJECT}',
        'email'
    ) as internal_email_token_batch""",
    f"""thales_protect_bulk_by_object_and_column(
        email_batch,
        'char',
        '{NONE_ARRAY_OBJECT}',
        'email'
    ) as none_email_token_batch""",
    "ssn_batch",
    f"""thales_protect_bulk_by_object_and_column(
        ssn_batch,
        'nbr',
        '{INTERNAL_ARRAY_OBJECT}',
        'ssn'
    ) as internal_ssn_token_batch""",
).selectExpr(
    "email_batch",
    "internal_email_token_batch",
    f"""thales_reveal_bulk_by_object_and_column_with_user(
        internal_email_token_batch,
        'char',
        '{INTERNAL_ARRAY_OBJECT}',
        'email',
        current_user()
    ) as internal_email_revealed_batch""",
    "none_email_token_batch",
    f"""thales_reveal_bulk_by_object_and_column_with_user(
        none_email_token_batch,
        'char',
        '{NONE_ARRAY_OBJECT}',
        'email',
        current_user()
    ) as none_email_revealed_batch""",
    "ssn_batch",
    "internal_ssn_token_batch",
    f"""thales_reveal_bulk_by_object_and_column_with_user(
        internal_ssn_token_batch,
        'nbr',
        '{INTERNAL_ARRAY_OBJECT}',
        'ssn',
        current_user()
    ) as internal_ssn_revealed_batch""",
)

display(bulk_round_trip_df)

# COMMAND ----------

# External bulk protect + reveal smoke test.
external_bulk_round_trip_df = test_df.selectExpr(
    "email_batch",
    f"""thales_protect_bulk_by_object_and_column_with_external_header(
        email_batch,
        'char',
        '{EXTERNAL_ARRAY_OBJECT}',
        'email'
    ) as external_email_token_batch""",
).selectExpr(
    "email_batch",
    "transform(external_email_token_batch, x -> x.protected_value) as email_token_batch",
    "transform(external_email_token_batch, x -> x.external_header) as email_header_batch",
    f"""thales_reveal_bulk_by_object_and_column_with_external_header_and_user(
        transform(external_email_token_batch, x -> x.protected_value),
        transform(external_email_token_batch, x -> x.external_header),
        'char',
        '{EXTERNAL_ARRAY_OBJECT}',
        'email',
        current_user()
    ) as external_email_revealed_batch""",
)

display(
    external_bulk_round_trip_df.select(
        "email_batch",
        "email_token_batch",
        "email_header_batch",
        "external_email_revealed_batch",
    )
)

# COMMAND ----------

# Optional CTAS-style examples.
#
# spark.sql(\"\"\"
# CREATE OR REPLACE TEMP VIEW v_java_udf_internal_ctas_demo AS
# SELECT
#   thales_protect_by_object_and_column(
#     email,
#     'char',
#     INTERNAL_OBJECT,
#     'email'
#   ) AS email,
#   thales_protect_by_object_and_column(
#     ssn,
#     'nbr',
#     INTERNAL_OBJECT,
#     'ssn'
#   ) AS ssn
# FROM source_table
# \"\"\")
#
# spark.sql(\"\"\"
# SELECT *
# FROM v_java_udf_internal_ctas_demo
# LIMIT 10
# \"\"\").show(truncate=False)

# COMMAND ----------

print(
    "Java smoke test completed. Review the displayed results to confirm the "
    "new minimal Java UDF surface for internal, external, none, and bulk reveal/protect."
)
