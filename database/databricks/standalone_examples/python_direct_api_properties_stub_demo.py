from pathlib import Path
import sys
from dataclasses import replace

repo_src = Path(__file__).resolve().parents[1] / "src"
if str(repo_src) not in sys.path:
    sys.path.insert(0, str(repo_src))

from thales_databricks_integration import IntegrationConfig, protect_dataframe, protect_rows


class DemoDataFrame:
    def __init__(self, columns):
        self.columns = columns


source_df = DemoDataFrame(["customer_id", "email", "ssn", "city"])
properties_path = Path(__file__).resolve().parents[1] / "src" / "main" / "resources" / "udfConfig.properties"
config_v2 = replace(
    IntegrationConfig.from_properties(properties_path),
    transport_mode="stub",
)
config_v1 = IntegrationConfig.sample_customer_config_v1()
properties_object_name = "my_catalog.my_schema.plaintext_protected_internal"

protected_df = protect_dataframe(
    df=source_df,
    object_name=properties_object_name,
    config=config_v2,
)

print("Properties-based v2 config loaded in stub mode for local execution")
print(protected_df._thales_bulk_plan_summary)

source_rows = [
    {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
    {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
]

row_result_v2 = protect_rows(
    rows=[
        {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
        {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
    ],
    object_name=properties_object_name,
    config=config_v2,
)

row_result_v1 = protect_rows(
    rows=source_rows,
    object_name="my_catalog.my_schema.customer",
    config=config_v1,
)

print("V2 protected rows")
print(row_result_v2.rows)
print("V2 request summary")
print(
    {
        "input_row_count": row_result_v2.input_row_count,
        "transformed_value_count": row_result_v2.transformed_value_count,
        "request_count": row_result_v2.request_count,
        "requests": row_result_v2.requests,
    }
)

print("V1 protected rows")
print(row_result_v1.rows)
print("V1 request summary")
print(
    {
        "input_row_count": row_result_v1.input_row_count,
        "transformed_value_count": row_result_v1.transformed_value_count,
        "request_count": row_result_v1.request_count,
        "requests": row_result_v1.requests,
    }
)

constrained_v2_config = replace(
    config_v2,
    spark_group_size=3,
    crdp_v2_max_items_per_request=2,
    crdp_v2_max_policy_groups_per_request=1,
    crdp_v2_enable_multi_policy=True,
)

large_rows = [
    {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
    {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
    {"customer_id": 3, "email": "carol@example.com", "ssn": "333445555", "city": "Chicago"},
    {"customer_id": 4, "email": "dave@example.com", "ssn": "444556666", "city": "Austin"},
    {"customer_id": 5, "email": "erin@example.com", "ssn": "555667777", "city": "Seattle"},
]

row_result_v2_constrained = protect_rows(
    rows=large_rows,
    object_name=properties_object_name,
    config=constrained_v2_config,
)

print("V2 constrained request summary")
print(
    {
        "input_row_count": row_result_v2_constrained.input_row_count,
        "transformed_value_count": row_result_v2_constrained.transformed_value_count,
        "request_count": row_result_v2_constrained.request_count,
        "requests": row_result_v2_constrained.requests,
    }
)
