from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ColumnPlan:
    object_name: str
    column_name: str
    datatype: str
    profile_name: str | None


@dataclass(slots=True)
class ProtectWorkItem:
    object_name: str
    column_name: str
    datatype: str
    profile_name: str | None
    policy_type: str
    metadata: str | None
    reveal_user: str | None
    external_header_column_name: str | None
    batch_size: int


@dataclass(slots=True)
class BulkPlan:
    mode: str
    object_name: str
    columns: list[ColumnPlan]
    work_items: list[ProtectWorkItem]
    config: object
    api_version: str
    batch_size: int
    spark_group_size: int
    v2_max_items_per_request: int
    v2_max_policy_groups_per_request: int
    v2_enable_multi_policy: bool


@dataclass(slots=True)
class BulkExecutionResult:
    plan: BulkPlan
    rows: list[dict]
    input_row_count: int
    transformed_value_count: int
    request_count: int
    requests: list[dict]


@dataclass(slots=True)
class BulkColumnarExecutionResult:
    plan: BulkPlan
    columns: dict[str, list]
    input_row_count: int
    transformed_value_count: int
    request_count: int
    requests: list[dict]
