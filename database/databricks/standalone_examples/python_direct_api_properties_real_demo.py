from pathlib import Path
import sys
from dataclasses import replace

repo_src = Path(__file__).resolve().parents[1] / "src"
if str(repo_src) not in sys.path:
    sys.path.insert(0, str(repo_src))

from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe,
    protect_rows,
    reveal_rows,
)


class DemoDataFrame:
    def __init__(self, columns):
        self.columns = columns


def print_section(title, payload):
    print(title)
    print(payload)
    print()


source_df = DemoDataFrame(["customer_id", "email", "ssn", "city"])
properties_path = Path(__file__).resolve().parents[1] / "src" / "main" / "resources" / "udfConfig.properties"
config_v2 = replace(
    IntegrationConfig.from_properties(properties_path),
    transport_mode="real",
)
properties_object_name = "my_catalog.my_schema.plaintext_protected_internal"

print("Properties-based real CRDP demo")
print("This example loads the local udfConfig.properties file and forces transport_mode='real'.")
print("It is intended for connected CRDP testing outside Databricks.")
print(f"Properties path: {properties_path}")
print()

protected_df = protect_dataframe(
    df=source_df,
    object_name=properties_object_name,
    config=config_v2,
)

print("DataFrame-style call outside Spark")
print("This uses a lightweight DemoDataFrame, so it shows plan resolution only.")
print("Outside Databricks, the row-based APIs below are what produce live transformed values.")
print_section("Properties-based v2 config loaded in real mode", protected_df._thales_bulk_plan_summary)

source_rows = [
    {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
    {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
]

row_result_v2 = protect_rows(
    rows=source_rows,
    object_name=properties_object_name,
    config=config_v2,
)

print_section("Protected rows (v2 real transport):", row_result_v2.rows)
print_section(
    "Protect request summary (v2 real transport):",
    {
        "input_row_count": row_result_v2.input_row_count,
        "transformed_value_count": row_result_v2.transformed_value_count,
        "request_count": row_result_v2.request_count,
        "requests": row_result_v2.requests,
    },
)

revealed_result_v2 = reveal_rows(
    rows=row_result_v2.rows,
    object_name=properties_object_name,
    config=config_v2,
    reveal_user="admin",
)

print_section("Revealed rows (v2 real transport):", revealed_result_v2.rows)
print_section(
    "Reveal request summary (v2 real transport):",
    {
        "input_row_count": revealed_result_v2.input_row_count,
        "transformed_value_count": revealed_result_v2.transformed_value_count,
        "request_count": revealed_result_v2.request_count,
        "requests": revealed_result_v2.requests,
    },
)
