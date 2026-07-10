# Databricks Lakeflow Declarative Pipelines / Python examples for the concrete
# plaintext_protected_internal demo objects used in this repo.

from pyspark import pipelines as dp


CATALOG = "my_catalog"
SCHEMA = "my_schema"

PROTECTED_INTERNAL_SOURCE = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
GOVERNED_FLAT_REVEAL_VIEW = f"{CATALOG}.{SCHEMA}.v_plaintext_final_reveal_flat_uc_embedded_v2_optimized"
GOVERNED_ARRAY_REVEAL_VIEW = (
    f"{CATALOG}.{SCHEMA}.v_plaintext_protected_internal_array_reveal_uc_embedded_v2_optimized"
)


@dp.table(name="plaintext_protected_internal_bronze_stream_py")
def plaintext_protected_internal_bronze_stream_py():
    return spark.readStream.table(PROTECTED_INTERNAL_SOURCE).select(
        "custid",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "phone",
        "email",
        "dob",
        "creditcard",
        "creditcardcode",
        "ssn",
    )


@dp.materialized_view(name="plaintext_protected_internal_reveal_gold_py")
def plaintext_protected_internal_reveal_gold_py():
    return spark.table(GOVERNED_FLAT_REVEAL_VIEW).select(
        "custid",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "phone",
        "email",
        "dob",
        "creditcard",
        "creditcardcode",
        "ssn",
    )


@dp.materialized_view(name="plaintext_protected_internal_reveal_array_gold_py")
def plaintext_protected_internal_reveal_array_gold_py():
    return spark.table(GOVERNED_ARRAY_REVEAL_VIEW).select(
        "row_id",
        "custid_array",
        "name_array",
        "address_array",
        "city_array",
        "state_array",
        "zip_array",
        "phone_array",
        "email_array",
        "dob_array",
        "creditcard_array",
        "creditcardcode_array",
        "ssn_array",
    )
