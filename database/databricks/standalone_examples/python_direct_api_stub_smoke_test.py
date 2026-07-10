from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

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
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns


def print_section(title: str, payload) -> None:
    print(title)
    print(payload)
    print()


def main() -> None:
    print("Offline Python direct API smoke test")
    print("This example uses stub transport only and does not require Databricks.")
    print()

    source_df = DemoDataFrame(["customer_id", "email", "ssn", "city"])
    source_rows = [
        {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
        {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
    ]

    config_v2 = IntegrationConfig.sample_customer_config()
    config_v1 = IntegrationConfig.sample_customer_config_v1()
    object_name = "my_catalog.my_schema.customer"

    protected_df = protect_dataframe(
        df=source_df,
        object_name=object_name,
        config=config_v2,
    )
    print_section("DataFrame plan summary (v2 stub):", protected_df._thales_bulk_plan_summary)

    protected_rows_v2 = protect_rows(
        rows=source_rows,
        object_name=object_name,
        config=config_v2,
    )
    print_section("Protected rows (v2 stub):", protected_rows_v2.rows)
    print_section(
        "Protect request summary (v2 stub):",
        {
            "input_row_count": protected_rows_v2.input_row_count,
            "transformed_value_count": protected_rows_v2.transformed_value_count,
            "request_count": protected_rows_v2.request_count,
            "requests": protected_rows_v2.requests,
        },
    )

    revealed_rows_v2 = reveal_rows(
        rows=protected_rows_v2.rows,
        object_name=object_name,
        config=config_v2,
        reveal_user="admin",
    )
    print_section("Revealed rows (v2 stub):", revealed_rows_v2.rows)

    protected_rows_v1 = protect_rows(
        rows=source_rows,
        object_name=object_name,
        config=config_v1,
    )
    print_section("Protected rows (v1 stub):", protected_rows_v1.rows)
    print_section(
        "Protect request summary (v1 stub):",
        {
            "input_row_count": protected_rows_v1.input_row_count,
            "transformed_value_count": protected_rows_v1.transformed_value_count,
            "request_count": protected_rows_v1.request_count,
            "requests": protected_rows_v1.requests,
        },
    )

    constrained_v2_config = replace(
        config_v2,
        spark_group_size=3,
        crdp_v2_max_items_per_request=2,
        crdp_v2_max_policy_groups_per_request=1,
        crdp_v2_enable_multi_policy=True,
    )

    larger_row_set = [
        {"customer_id": 1, "email": "alice@example.com", "ssn": "111223333", "city": "Boston"},
        {"customer_id": 2, "email": "bob@example.com", "ssn": "222334444", "city": "New York"},
        {"customer_id": 3, "email": "carol@example.com", "ssn": "333445555", "city": "Chicago"},
        {"customer_id": 4, "email": "dave@example.com", "ssn": "444556666", "city": "Austin"},
        {"customer_id": 5, "email": "erin@example.com", "ssn": "555667777", "city": "Seattle"},
    ]

    constrained_result = protect_rows(
        rows=larger_row_set,
        object_name=object_name,
        config=constrained_v2_config,
    )
    print_section(
        "Constrained v2 request summary (shows grouping/chunking behavior):",
        {
            "input_row_count": constrained_result.input_row_count,
            "transformed_value_count": constrained_result.transformed_value_count,
            "request_count": constrained_result.request_count,
            "requests": constrained_result.requests,
        },
    )

    print("Smoke test complete.")


if __name__ == "__main__":
    main()
