from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal


ExecutionPath = Literal["java_grouped_array", "python_helper_v1", "python_helper_v2"]


@dataclass(slots=True)
class TuningResolution:
    execution_path: ExecutionPath
    row_count: int
    default_parallelism: int
    effective_generate_partitions: int
    effective_target_partitions: int
    work_unit_count_target: int
    work_unit_count_strategy: str
    work_unit_row_count: int
    work_unit_row_strategy: str
    effective_crdp_request_item_target: int
    crdp_request_item_strategy: str
    multi_policy_enabled: bool
    notes: list[str]


def default_partitions(default_parallelism: int) -> int:
    return max(int(default_parallelism) * 2, 32)


def resolve_java_grouped_array_tuning(
    *,
    row_count: int,
    default_parallelism: int,
    config_batch_size: int,
    generate_partitions: int | None = None,
    target_partitions: int | None = None,
    group_size_override: int | None = None,
    group_count_override: int | None = None,
    group_size_multiplier: float = 1.0,
    work_unit_count_target: int | None = None,
    work_unit_count_multiplier: float = 2.0,
    work_unit_row_count: int | None = None,
    crdp_request_item_target: int | None = None,
) -> TuningResolution:
    effective_generate_partitions = _resolve_partitions(generate_partitions, default_parallelism)
    effective_target_partitions = _resolve_partitions(target_partitions, default_parallelism)

    notes: list[str] = []

    if work_unit_row_count is not None:
        effective_work_unit_row_count = max(int(work_unit_row_count), 1)
        row_strategy = "work_unit_row_count"
        effective_work_unit_count_target = max(int(math.ceil(float(row_count) / float(effective_work_unit_row_count))), 1)
        count_strategy = "derived_from_work_unit_row_count"
    elif group_size_override is not None:
        effective_work_unit_row_count = max(int(group_size_override), 1)
        row_strategy = "group_size_override"
        effective_work_unit_count_target = max(int(math.ceil(float(row_count) / float(effective_work_unit_row_count))), 1)
        count_strategy = "derived_from_group_size_override"
    else:
        effective_work_unit_count_target, count_strategy = _resolve_work_unit_count_target(
            row_count=row_count,
            target_partitions=effective_target_partitions,
            explicit_work_unit_count_target=work_unit_count_target,
            legacy_group_count_override=group_count_override,
            work_unit_count_multiplier=work_unit_count_multiplier,
        )
        if group_count_override is not None:
            effective_work_unit_row_count = max(int(math.ceil(float(row_count) / float(effective_work_unit_count_target))), 1)
            row_strategy = "group_count_override"
        else:
            effective_work_unit_row_count = max(int(config_batch_size * float(group_size_multiplier)), 1)
            row_strategy = "batch_size_multiplier"
            effective_work_unit_count_target = max(
                int(math.ceil(float(row_count) / float(effective_work_unit_row_count))),
                1,
            )
            count_strategy = "derived_from_batch_size_multiplier"

    if crdp_request_item_target is not None:
        effective_crdp_request_item_target = max(int(crdp_request_item_target), 1)
        crdp_strategy = "explicit_crdp_request_item_target"
    else:
        effective_crdp_request_item_target = min(max(int(config_batch_size), 1), effective_work_unit_row_count)
        crdp_strategy = "min(work_unit_row_count, batch_size)"

    notes.append("Java grouped-array path chunks per column by BATCH_SIZE.")
    notes.append("Java grouped-array path does not yet combine multiple columns into one v2 multi-policy request.")

    return TuningResolution(
        execution_path="java_grouped_array",
        row_count=row_count,
        default_parallelism=default_parallelism,
        effective_generate_partitions=effective_generate_partitions,
        effective_target_partitions=effective_target_partitions,
        work_unit_count_target=effective_work_unit_count_target,
        work_unit_count_strategy=count_strategy,
        work_unit_row_count=effective_work_unit_row_count,
        work_unit_row_strategy=row_strategy,
        effective_crdp_request_item_target=effective_crdp_request_item_target,
        crdp_request_item_strategy=crdp_strategy,
        multi_policy_enabled=False,
        notes=notes,
    )


def resolve_python_helper_tuning(
    *,
    row_count: int,
    default_parallelism: int,
    config_batch_size: int,
    spark_group_size: int,
    v2_max_items_per_request: int,
    v2_max_policy_groups_per_request: int,
    v2_enable_multi_policy: bool,
    generate_partitions: int | None = None,
    target_partitions: int | None = None,
    spark_group_size_override: int | None = None,
    work_unit_count_target: int | None = None,
    work_unit_count_multiplier: float = 2.0,
    work_unit_row_count: int | None = None,
    crdp_request_item_target: int | None = None,
    api_version: str = "v2",
) -> TuningResolution:
    effective_generate_partitions = _resolve_partitions(generate_partitions, default_parallelism)
    effective_target_partitions = _resolve_partitions(target_partitions, default_parallelism)

    notes: list[str] = []

    if work_unit_row_count is not None:
        effective_work_unit_row_count = max(int(work_unit_row_count), 1)
        row_strategy = "work_unit_row_count"
        effective_work_unit_count_target = max(int(math.ceil(float(row_count) / float(effective_work_unit_row_count))), 1)
        count_strategy = "derived_from_work_unit_row_count"
    elif spark_group_size_override is not None:
        effective_work_unit_row_count = max(int(spark_group_size_override), 1)
        row_strategy = "spark_group_size_override"
        effective_work_unit_count_target = max(int(math.ceil(float(row_count) / float(effective_work_unit_row_count))), 1)
        count_strategy = "derived_from_spark_group_size_override"
    elif work_unit_count_target is not None:
        effective_work_unit_count_target, count_strategy = _resolve_work_unit_count_target(
            row_count=row_count,
            target_partitions=effective_target_partitions,
            explicit_work_unit_count_target=work_unit_count_target,
            legacy_group_count_override=None,
            work_unit_count_multiplier=work_unit_count_multiplier,
        )
        effective_work_unit_row_count = max(int(math.ceil(float(row_count) / float(effective_work_unit_count_target))), 1)
        row_strategy = "derived_from_work_unit_count_target"
    else:
        effective_work_unit_row_count = max(int(spark_group_size), 1)
        row_strategy = "config_spark_group_size"
        effective_work_unit_count_target = max(int(math.ceil(float(row_count) / float(effective_work_unit_row_count))), 1)
        count_strategy = "derived_from_spark_group_size"

    if crdp_request_item_target is not None:
        effective_crdp_request_item_target = max(int(crdp_request_item_target), 1)
        crdp_strategy = "explicit_crdp_request_item_target"
    elif str(api_version).strip().lower() == "v2":
        effective_crdp_request_item_target = min(
            effective_work_unit_row_count,
            max(int(v2_max_items_per_request), 1),
        )
        crdp_strategy = "min(work_unit_row_count, v2_max_items_per_request)"
    else:
        effective_crdp_request_item_target = min(
            effective_work_unit_row_count,
            max(int(config_batch_size), 1),
        )
        crdp_strategy = "min(work_unit_row_count, batch_size)"

    if str(api_version).strip().lower() == "v2":
        notes.append(
            "Python helper v2 can combine multiple policy groups into one request up to CRDP_V2_MAX_POLICY_GROUPS_PER_REQUEST."
        )
        notes.append(
            f"Configured v2 max policy groups per request: {max(int(v2_max_policy_groups_per_request), 1)}."
        )
    else:
        notes.append("Python helper v1 behaves as a single-policy bulk path.")

    return TuningResolution(
        execution_path="python_helper_v2" if str(api_version).strip().lower() == "v2" else "python_helper_v1",
        row_count=row_count,
        default_parallelism=default_parallelism,
        effective_generate_partitions=effective_generate_partitions,
        effective_target_partitions=effective_target_partitions,
        work_unit_count_target=effective_work_unit_count_target,
        work_unit_count_strategy=count_strategy,
        work_unit_row_count=effective_work_unit_row_count,
        work_unit_row_strategy=row_strategy,
        effective_crdp_request_item_target=effective_crdp_request_item_target,
        crdp_request_item_strategy=crdp_strategy,
        multi_policy_enabled=bool(v2_enable_multi_policy) if str(api_version).strip().lower() == "v2" else False,
        notes=notes,
    )


def _resolve_partitions(explicit_partitions: int | None, default_parallelism: int) -> int:
    if explicit_partitions is not None:
        return max(int(explicit_partitions), 1)
    return default_partitions(default_parallelism)


def _resolve_work_unit_count_target(
    *,
    row_count: int,
    target_partitions: int,
    explicit_work_unit_count_target: int | None,
    legacy_group_count_override: int | None,
    work_unit_count_multiplier: float,
) -> tuple[int, str]:
    if explicit_work_unit_count_target is not None:
        return max(int(explicit_work_unit_count_target), 1), "work_unit_count_target"
    if legacy_group_count_override is not None:
        return max(int(legacy_group_count_override), 1), "group_count_override"
    derived = max(int(math.ceil(float(target_partitions) * float(work_unit_count_multiplier))), 1)
    return derived, "target_partitions_multiplier"
