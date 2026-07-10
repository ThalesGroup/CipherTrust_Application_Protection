from __future__ import annotations

from dataclasses import asdict
from typing import Any, Sequence

from .api import (
    _apply_options,
    _build_output_schema,
    _resolve_reveal_user,
    _resolve_sensitive_columns,
)
from .config import IntegrationConfig
from .executor import StubBulkExecutor
from .planner import BulkPlanner


def make_protect_scalar_pandas_udf(
    *,
    object_name: str,
    column_name: str,
    datatype: str | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
    return_type: str = "string",
):
    import pandas as pd
    from pyspark.sql.functions import pandas_udf

    resolved_config = _apply_options(config or IntegrationConfig(), options)
    resolved_datatype = datatype or resolved_config.resolve_datatype(object_name, column_name)
    plan = BulkPlanner(resolved_config).plan_protect(object_name=object_name, column_names=[column_name])
    executor = StubBulkExecutor()

    @pandas_udf(return_type)
    def udf(series):
        normalized_values = [_normalize_pandas_value(value) for value in series.tolist()]
        result = executor.protect_columns(plan, {column_name: normalized_values}, len(normalized_values))
        return pd.Series(result.columns.get(column_name, normalized_values), dtype="object")

    udf._thales_object_name = object_name  # type: ignore[attr-defined]
    udf._thales_column_name = column_name  # type: ignore[attr-defined]
    udf._thales_datatype = resolved_datatype  # type: ignore[attr-defined]
    return udf


def make_reveal_scalar_pandas_udf(
    *,
    object_name: str,
    column_name: str,
    spark_session=None,
    datatype: str | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
    reveal_user: str | None = None,
    return_type: str = "string",
):
    import pandas as pd
    from pyspark.sql.functions import pandas_udf

    resolved_config = _apply_options(config or IntegrationConfig(), options)
    resolved_datatype = datatype or resolved_config.resolve_datatype(object_name, column_name)
    runtime_reveal_user = _resolve_reveal_user_from_driver(
        spark_session=spark_session,
        config=resolved_config,
        options=options,
        reveal_user=reveal_user,
    )
    plan = BulkPlanner(resolved_config).plan_reveal(
        object_name=object_name,
        column_names=[column_name],
        runtime_reveal_user=runtime_reveal_user,
    )
    executor = StubBulkExecutor()

    @pandas_udf(return_type)
    def udf(series):
        normalized_values = [_normalize_pandas_value(value) for value in series.tolist()]
        result = executor.reveal_columns(plan, {column_name: normalized_values}, len(normalized_values))
        return pd.Series(result.columns.get(column_name, normalized_values), dtype="object")

    udf._thales_object_name = object_name  # type: ignore[attr-defined]
    udf._thales_column_name = column_name  # type: ignore[attr-defined]
    udf._thales_datatype = resolved_datatype  # type: ignore[attr-defined]
    udf._thales_reveal_user = runtime_reveal_user  # type: ignore[attr-defined]
    return udf


def protect_dataframe_map_in_pandas(
    df,
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
):
    resolved_config = _apply_options(config or IntegrationConfig(), options)
    resolved_columns = _resolve_sensitive_columns(df, object_name, sensitive_columns, resolved_config, mode="protect")
    plan = BulkPlanner(resolved_config).plan_protect(object_name=object_name, column_names=resolved_columns)
    return _map_in_pandas_transform(df, plan, resolved_config)


def reveal_dataframe_map_in_pandas(
    df,
    object_name: str,
    sensitive_columns: Sequence[str] | None = None,
    config: IntegrationConfig | None = None,
    options: dict[str, Any] | None = None,
    reveal_user: str | None = None,
):
    resolved_config = _apply_options(config or IntegrationConfig(), options)
    runtime_reveal_user = _resolve_reveal_user(df, resolved_config, options, reveal_user)
    resolved_columns = _resolve_sensitive_columns(df, object_name, sensitive_columns, resolved_config, mode="reveal")
    plan = BulkPlanner(resolved_config).plan_reveal(
        object_name=object_name,
        column_names=resolved_columns,
        runtime_reveal_user=runtime_reveal_user,
    )
    return _map_in_pandas_transform(
        df,
        plan,
        resolved_config,
        extra_summary={
            "resolved_reveal_user": runtime_reveal_user,
            "execution_model": "mapInPandas",
        },
    )


def _map_in_pandas_transform(df, plan, resolved_config: IntegrationConfig, extra_summary: dict[str, Any] | None = None):
    import pandas as pd
    from pyspark.sql import types as T

    executor = StubBulkExecutor()
    output_schema, output_column_order = _build_output_schema(df.schema, plan, T)

    def transform(iterator):
        for pdf in iterator:
            if pdf.empty:
                yield pd.DataFrame(columns=output_column_order)
                continue

            normalized_columns = {
                column_name: [_normalize_pandas_value(value) for value in pdf[column_name].tolist()]
                for column_name in pdf.columns
            }
            result = (
                executor.protect_columns(plan, normalized_columns, len(pdf.index))
                if plan.mode == "protect"
                else executor.reveal_columns(plan, normalized_columns, len(pdf.index))
            )
            output_pdf = pdf.copy(deep=False)
            for column_name, values in result.columns.items():
                output_pdf[column_name] = values
            for column_name in output_column_order:
                if column_name not in output_pdf.columns:
                    output_pdf[column_name] = None
            yield output_pdf[output_column_order]

    transformed_df = df.mapInPandas(transform, schema=output_schema)

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
        "execution_model": "mapInPandas",
        "columns": [asdict(column) for column in plan.columns],
        "work_items": [asdict(work_item) for work_item in plan.work_items],
    }
    if extra_summary:
        plan_summary.update(extra_summary)

    try:
        setattr(transformed_df, "_thales_bulk_plan", plan)
        setattr(transformed_df, "_thales_bulk_plan_summary", plan_summary)
    except Exception:
        pass

    return transformed_df


def _resolve_reveal_user_from_driver(
    *,
    spark_session,
    config: IntegrationConfig,
    options: dict[str, Any] | None,
    reveal_user: str | None,
) -> str:
    if config.reveal_user_override_allowed and reveal_user and reveal_user.strip():
        return reveal_user.strip()

    if spark_session is not None:
        reveal_user_expr = "current_user()"
        if config.reveal_user_override_allowed and options and options.get("reveal_user_expr"):
            reveal_user_expr = str(options["reveal_user_expr"]).strip()
        try:
            row = spark_session.sql(f"SELECT {reveal_user_expr} AS reveal_user").collect()[0]
            resolved_value = row["reveal_user"]
            if resolved_value is not None and str(resolved_value).strip():
                return str(resolved_value).strip()
        except Exception:
            pass

    return config.default_reveal_user


def _normalize_pandas_value(value):
    if value is None:
        return None
    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except Exception:
        pass
    return value
