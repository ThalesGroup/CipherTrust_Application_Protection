from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Sequence

from .config import IntegrationConfig
from .executor import StubBulkExecutor
from .planner import BulkPlanner


def protect_dataframe(
    df,
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
):
    """
    Phase 1 public API.

    This helper intentionally keeps the notebook author in a row/DataFrame
    mindset. Internally it resolves the protected columns and prepares a bulk
    plan. Phase 1 still returns the source DataFrame unchanged, but now it
    attaches a concrete plan summary so the next execution slice has a stable
    contract to build on.
    """

    if df is None:
        raise ValueError("df is required.")
    if not object_name or not object_name.strip():
        raise ValueError("object_name is required.")

    resolved_config = _apply_options(config or IntegrationConfig(), options)
    resolved_columns = _resolve_sensitive_columns(df, object_name, sensitive_columns, resolved_config, mode="protect")
    plan = BulkPlanner(resolved_config).plan_protect(object_name=object_name, column_names=resolved_columns)
    return _execute_dataframe(df, plan, resolved_config)


def reveal_dataframe(
    df,
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
    reveal_user: str | None = None,
):
    if df is None:
        raise ValueError("df is required.")
    if not object_name or not object_name.strip():
        raise ValueError("object_name is required.")

    resolved_config = _apply_options(config or IntegrationConfig(), options)
    resolved_reveal_user = _resolve_reveal_user(df, resolved_config, options, reveal_user)
    resolved_columns = _resolve_sensitive_columns(df, object_name, sensitive_columns, resolved_config, mode="reveal")
    plan = BulkPlanner(resolved_config).plan_reveal(
        object_name=object_name,
        column_names=resolved_columns,
        runtime_reveal_user=resolved_reveal_user,
    )
    return _execute_dataframe(
        df,
        plan,
        resolved_config,
        extra_summary={
            "resolved_reveal_user": resolved_reveal_user,
            "reveal_user_resolution": _describe_reveal_user_resolution(
                df,
                resolved_config,
                options,
                reveal_user,
            ),
        },
    )


def protect_rows(
    rows: list[dict],
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
):
    if rows is None:
        raise ValueError("rows is required.")
    if not object_name or not object_name.strip():
        raise ValueError("object_name is required.")

    resolved_config = _apply_options(config or IntegrationConfig(), None)
    discovered_columns = _resolve_row_columns(rows)
    resolved_columns = _resolve_sensitive_columns(
        _RowLike(discovered_columns),
        object_name,
        sensitive_columns,
        resolved_config,
        mode="protect",
    )
    plan = BulkPlanner(resolved_config).plan_protect(object_name=object_name, column_names=resolved_columns)
    return StubBulkExecutor().protect_rows(plan, rows)


def reveal_rows(
    rows: list[dict],
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
    reveal_user: str | None = None,
):
    if rows is None:
        raise ValueError("rows is required.")
    if not object_name or not object_name.strip():
        raise ValueError("object_name is required.")

    resolved_config = _apply_options(config or IntegrationConfig(), None)
    discovered_columns = _resolve_row_columns(rows)
    resolved_columns = _resolve_sensitive_columns(
        _RowLike(discovered_columns),
        object_name,
        sensitive_columns,
        resolved_config,
        mode="reveal",
    )
    resolved_reveal_user = reveal_user or resolved_config.default_reveal_user
    plan = BulkPlanner(resolved_config).plan_reveal(
        object_name=object_name,
        column_names=resolved_columns,
        runtime_reveal_user=resolved_reveal_user,
    )
    return StubBulkExecutor().reveal_rows(plan, rows)


def _execute_dataframe(
    df,
    plan,
    resolved_config: IntegrationConfig,
    extra_summary: dict[str, Any] | None = None,
):

    plan_summary = {
        "mode": plan.mode,
        "object_name": plan.object_name,
        "api_version": plan.api_version,
        "transport_mode": resolved_config.transport_mode,
        "real_transport_enabled": resolved_config.should_use_real_transport(),
        "crdp_endpoint_configured": resolved_config.has_crdp_endpoint(),
        "reveal_user_override_allowed": resolved_config.reveal_user_override_allowed,
        "batch_size": plan.batch_size,
        "spark_group_size": plan.spark_group_size,
        "v2_max_items_per_request": plan.v2_max_items_per_request,
        "v2_max_policy_groups_per_request": plan.v2_max_policy_groups_per_request,
        "v2_enable_multi_policy": plan.v2_enable_multi_policy,
        "columns": [asdict(column) for column in plan.columns],
        "work_items": [asdict(work_item) for work_item in plan.work_items],
    }
    if extra_summary:
        plan_summary.update(extra_summary)

    if _is_spark_dataframe(df):
        protected_df = _transform_spark_dataframe(df, plan)
        try:
            setattr(protected_df, "_thales_bulk_plan", plan)
            setattr(protected_df, "_thales_bulk_plan_summary", plan_summary)
        except Exception:
            pass
        return protected_df

    setattr(df, "_thales_bulk_plan", plan)
    setattr(df, "_thales_bulk_plan_summary", plan_summary)
    return df


def _resolve_sensitive_columns(
    df,
    object_name: str,
    sensitive_columns: Sequence[str] | None,
    config: IntegrationConfig,
    mode: str,
) -> list[str]:
    if sensitive_columns:
        return [column for column in sensitive_columns if column]

    if hasattr(df, "columns"):
        df_columns = [str(column) for column in getattr(df, "columns")]
    else:
        df_columns = []

    mapped_columns = config.get_object_columns(object_name, mode=mode)
    if mapped_columns:
        return [column for column in mapped_columns if column in df_columns or not df_columns]

    return df_columns


def _resolve_row_columns(rows: list[dict]) -> list[str]:
    if not rows:
        return []
    return [str(column) for column in rows[0].keys()]


class _RowLike:
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns


def _apply_options(
    config: IntegrationConfig,
    options: dict[str, Any] | None,
) -> IntegrationConfig:
    if not options:
        return config

    updates: dict[str, Any] = {}

    if "api_version" in options and options["api_version"]:
        updates["crdp_api_version"] = str(options["api_version"])
    if "transport_mode" in options and options["transport_mode"]:
        updates["transport_mode"] = str(options["transport_mode"])
    if "spark_group_size" in options and options["spark_group_size"] is not None:
        updates["spark_group_size"] = int(options["spark_group_size"])
    if "v2_max_items_per_request" in options and options["v2_max_items_per_request"] is not None:
        updates["crdp_v2_max_items_per_request"] = int(options["v2_max_items_per_request"])
    if "v2_max_policy_groups_per_request" in options and options["v2_max_policy_groups_per_request"] is not None:
        updates["crdp_v2_max_policy_groups_per_request"] = int(options["v2_max_policy_groups_per_request"])
    if "v2_enable_multi_policy" in options and options["v2_enable_multi_policy"] is not None:
        updates["crdp_v2_enable_multi_policy"] = bool(options["v2_enable_multi_policy"])
    if "batch_size" in options and options["batch_size"] is not None:
        updates["default_batch_size"] = int(options["batch_size"])

    return replace(config, **updates) if updates else config


def _is_spark_dataframe(df) -> bool:
    return hasattr(df, "schema") and hasattr(df, "rdd") and hasattr(df, "sparkSession")


def _resolve_reveal_user(
    df,
    config: IntegrationConfig,
    options: dict[str, Any] | None,
    reveal_user: str | None,
) -> str:
    if config.reveal_user_override_allowed and reveal_user and reveal_user.strip():
        return reveal_user.strip()

    if _is_spark_dataframe(df):
        spark_session = getattr(df, "sparkSession", None)
        if spark_session is not None:
            reveal_user_expr = _resolve_reveal_user_expr(config, options)
            try:
                row = spark_session.sql(f"SELECT {reveal_user_expr} AS reveal_user").collect()[0]
                resolved_value = row["reveal_user"]
                if resolved_value is not None and str(resolved_value).strip():
                    return str(resolved_value).strip()
            except Exception:
                pass

    return config.default_reveal_user


def _resolve_reveal_user_expr(config: IntegrationConfig, options: dict[str, Any] | None) -> str:
    if config.reveal_user_override_allowed and options and options.get("reveal_user_expr"):
        return str(options["reveal_user_expr"]).strip()
    return "current_user()"


def _describe_reveal_user_resolution(
    df,
    config: IntegrationConfig,
    options: dict[str, Any] | None,
    reveal_user: str | None,
) -> str:
    if not config.reveal_user_override_allowed:
        if _is_spark_dataframe(df):
            return "spark_sql_locked:current_user()"
        return "config_default_locked"
    if reveal_user and reveal_user.strip():
        return "explicit"
    if _is_spark_dataframe(df):
        reveal_user_expr = _resolve_reveal_user_expr(config, options)
        return f"spark_sql:{reveal_user_expr}"
    return "config_default"


def _transform_spark_dataframe(df, plan):
    from pyspark.sql import types as T

    executor = StubBulkExecutor()
    output_schema, output_column_order = _build_output_schema(df.schema, plan, T)
    effective_group_size = max(plan.spark_group_size, 1)

    def protect_partition(rows_iter):
        batch = []

        def flush(current_batch):
            if not current_batch:
                return []
            row_dicts = [row.asDict(recursive=True) for row in current_batch]
            result = (
                executor.protect_rows(plan, row_dicts)
                if plan.mode == "protect"
                else executor.reveal_rows(plan, row_dicts)
            )
            return [
                tuple(protected_row.get(column_name) for column_name in output_column_order)
                for protected_row in result.rows
            ]

        for row in rows_iter:
            batch.append(row)
            if len(batch) >= effective_group_size:
                for values in flush(batch):
                    yield values
                batch = []

        if batch:
            for values in flush(batch):
                yield values

    protected_rdd = df.rdd.mapPartitions(protect_partition)
    return df.sparkSession.createDataFrame(protected_rdd, schema=output_schema)


def _build_output_schema(schema, plan, spark_types_module):
    protected_columns = {work_item.column_name for work_item in plan.work_items}
    external_header_columns = {
        work_item.column_name: work_item.external_header_column_name
        for work_item in plan.work_items
        if plan.mode == "protect"
        and work_item.policy_type == "external"
        and work_item.external_header_column_name
    }
    existing_column_names = {field.name for field in schema.fields}

    output_fields = []
    output_column_order: list[str] = []
    for field in schema.fields:
        if field.name in protected_columns:
            output_fields.append(
                spark_types_module.StructField(field.name, spark_types_module.StringType(), True)
            )
        else:
            output_fields.append(field)
        output_column_order.append(field.name)

        header_column_name = external_header_columns.get(field.name)
        if header_column_name and header_column_name not in existing_column_names:
            output_fields.append(
                spark_types_module.StructField(header_column_name, spark_types_module.StringType(), True)
            )
            output_column_order.append(header_column_name)

    return spark_types_module.StructType(output_fields), output_column_order
