from __future__ import annotations

import logging

from .models import BulkColumnarExecutionResult, BulkExecutionResult, BulkPlan, ProtectWorkItem
from .transport import ProtectBatchRequest, ProtectMultiBatchRequest, ProtectTransportResult, build_transport


LOGGER = logging.getLogger(__name__)


class StubBulkExecutor:
    """
    Local Phase 1 executor.

    This does not call CRDP yet. It proves the row-shaped execution contract by
    transforming configured sensitive columns deterministically.
    """

    def __init__(self, transport=None) -> None:
        self._transport = transport

    def protect_rows(self, plan: BulkPlan, rows: list[dict]) -> BulkExecutionResult:
        return self._transform_rows(plan, rows, operation="protect")

    def reveal_rows(self, plan: BulkPlan, rows: list[dict]) -> BulkExecutionResult:
        return self._transform_rows(plan, rows, operation="reveal")

    def protect_columns(self, plan: BulkPlan, columns: dict[str, list], row_count: int) -> BulkColumnarExecutionResult:
        return self._transform_columns(plan, columns, row_count, operation="protect")

    def reveal_columns(self, plan: BulkPlan, columns: dict[str, list], row_count: int) -> BulkColumnarExecutionResult:
        return self._transform_columns(plan, columns, row_count, operation="reveal")

    def _transform_rows(self, plan: BulkPlan, rows: list[dict], operation: str) -> BulkExecutionResult:
        transport = self._transport or build_transport(plan.config)
        protected_rows: list[dict] = []
        transformed_value_count = 0
        request_traces: list[dict] = []

        for row in rows:
            protected_rows.append(dict(row))

        if (plan.api_version or "").lower() == "v2" and plan.v2_enable_multi_policy:
            multi_batches = self._build_multi_column_batches(
                plan.work_items,
                protected_rows,
                plan.spark_group_size,
                plan.v2_max_items_per_request,
                plan.v2_max_policy_groups_per_request,
            )
            for multi_batch in multi_batches:
                if operation == "protect":
                    response = transport.protect_grouped_batch(multi_batch, plan.api_version)
                else:
                    try:
                        response = transport.reveal_grouped_batch(multi_batch, plan.api_version)
                    except Exception as exc:
                        if not _should_fail_open_reveal(plan):
                            raise
                        _log_reveal_fail_open(
                            plan,
                            "grouped_rows",
                            [batch_request.work_item for batch_request in multi_batch.requests],
                            exc,
                        )
                        response = _build_grouped_reveal_fallback_response(plan, multi_batch, exc)
                for batch_request in multi_batch.requests:
                    protected_values = response.protected_values_by_column.get(batch_request.work_item.column_name, [])
                    external_headers = response.external_headers_by_column.get(batch_request.work_item.column_name, [])
                    if len(protected_values) != len(batch_request.row_indexes):
                        raise ValueError(
                            "Batch response size did not match request size for column "
                            f"{batch_request.work_item.column_name}."
                        )
                    if (
                        operation == "protect"
                        and batch_request.work_item.policy_type == "external"
                        and (
                        len(external_headers) != len(batch_request.row_indexes)
                        )
                    ):
                        raise ValueError(
                            "Batch external header size did not match request size for column "
                            f"{batch_request.work_item.column_name}."
                        )
                    for batch_index, (row_index, protected_value) in enumerate(
                        zip(batch_request.row_indexes, protected_values)
                    ):
                        protected_rows[row_index][batch_request.work_item.column_name] = protected_value
                        if (
                            operation == "protect"
                            and batch_request.work_item.policy_type == "external"
                            and batch_request.work_item.external_header_column_name
                        ):
                            protected_rows[row_index][
                                batch_request.work_item.external_header_column_name
                            ] = external_headers[batch_index]
                        transformed_value_count += 1
                request_traces.append(response.request_trace)
        else:
            for work_item in plan.work_items:
                column_batches = self._build_column_batches(work_item, protected_rows)
                for batch in column_batches:
                    if operation == "protect":
                        response = transport.protect_batch(batch, plan.api_version)
                    else:
                        try:
                            response = transport.reveal_batch(batch, plan.api_version)
                        except Exception as exc:
                            if not _should_fail_open_reveal(plan):
                                raise
                            _log_reveal_fail_open(plan, "rows", [work_item], exc)
                            response = _build_reveal_fallback_response(plan, batch, exc)
                    protected_values = response.protected_values_by_column.get(work_item.column_name, [])
                    external_headers = response.external_headers_by_column.get(work_item.column_name, [])
                    if len(protected_values) != len(batch.row_indexes):
                        raise ValueError(
                            "Batch response size did not match request size for column "
                            f"{work_item.column_name}."
                        )
                    if (
                        operation == "protect"
                        and work_item.policy_type == "external"
                        and len(external_headers) != len(batch.row_indexes)
                    ):
                        raise ValueError(
                            "Batch external header size did not match request size for column "
                            f"{work_item.column_name}."
                        )
                    for batch_index, (row_index, protected_value) in enumerate(zip(batch.row_indexes, protected_values)):
                        protected_rows[row_index][work_item.column_name] = protected_value
                        if (
                            operation == "protect"
                            and work_item.policy_type == "external"
                            and work_item.external_header_column_name
                        ):
                            protected_rows[row_index][work_item.external_header_column_name] = external_headers[batch_index]
                        transformed_value_count += 1
                    request_traces.append(response.request_trace)

        return BulkExecutionResult(
            plan=plan,
            rows=protected_rows,
            input_row_count=len(rows),
            transformed_value_count=transformed_value_count,
            request_count=len(request_traces),
            requests=request_traces,
        )

    def _transform_columns(
        self,
        plan: BulkPlan,
        columns: dict[str, list],
        row_count: int,
        operation: str,
    ) -> BulkColumnarExecutionResult:
        transport = self._transport or build_transport(plan.config)
        transformed_columns: dict[str, list] = {
            work_item.column_name: self._copy_column(columns.get(work_item.column_name), row_count)
            for work_item in plan.work_items
        }
        if operation == "protect":
            for work_item in plan.work_items:
                if work_item.policy_type == "external" and work_item.external_header_column_name:
                    transformed_columns.setdefault(
                        work_item.external_header_column_name,
                        self._copy_column(columns.get(work_item.external_header_column_name), row_count),
                    )

        transformed_value_count = 0
        request_traces: list[dict] = []

        if (plan.api_version or "").lower() == "v2" and plan.v2_enable_multi_policy:
            multi_batches = self._build_multi_column_batches_from_columns(
                plan.work_items,
                columns,
                row_count,
                plan.spark_group_size,
                plan.v2_max_items_per_request,
                plan.v2_max_policy_groups_per_request,
            )
            for multi_batch in multi_batches:
                if operation == "protect":
                    response = transport.protect_grouped_batch(multi_batch, plan.api_version)
                else:
                    try:
                        response = transport.reveal_grouped_batch(multi_batch, plan.api_version)
                    except Exception as exc:
                        if not _should_fail_open_reveal(plan):
                            raise
                        _log_reveal_fail_open(
                            plan,
                            "grouped_columns",
                            [batch_request.work_item for batch_request in multi_batch.requests],
                            exc,
                        )
                        response = _build_grouped_reveal_fallback_response(plan, multi_batch, exc)
                for batch_request in multi_batch.requests:
                    protected_values = response.protected_values_by_column.get(batch_request.work_item.column_name, [])
                    external_headers = response.external_headers_by_column.get(batch_request.work_item.column_name, [])
                    if len(protected_values) != len(batch_request.row_indexes):
                        raise ValueError(
                            "Batch response size did not match request size for column "
                            f"{batch_request.work_item.column_name}."
                        )
                    if (
                        operation == "protect"
                        and batch_request.work_item.policy_type == "external"
                        and len(external_headers) != len(batch_request.row_indexes)
                    ):
                        raise ValueError(
                            "Batch external header size did not match request size for column "
                            f"{batch_request.work_item.column_name}."
                        )
                    output_column = transformed_columns[batch_request.work_item.column_name]
                    for batch_index, (row_index, protected_value) in enumerate(
                        zip(batch_request.row_indexes, protected_values)
                    ):
                        output_column[row_index] = protected_value
                        if (
                            operation == "protect"
                            and batch_request.work_item.policy_type == "external"
                            and batch_request.work_item.external_header_column_name
                        ):
                            transformed_columns[batch_request.work_item.external_header_column_name][row_index] = (
                                external_headers[batch_index]
                            )
                        transformed_value_count += 1
                request_traces.append(response.request_trace)
        else:
            for work_item in plan.work_items:
                column_batches = self._build_column_batches_from_columns(work_item, columns, row_count)
                output_column = transformed_columns[work_item.column_name]
                for batch in column_batches:
                    if operation == "protect":
                        response = transport.protect_batch(batch, plan.api_version)
                    else:
                        try:
                            response = transport.reveal_batch(batch, plan.api_version)
                        except Exception as exc:
                            if not _should_fail_open_reveal(plan):
                                raise
                            _log_reveal_fail_open(plan, "columns", [work_item], exc)
                            response = _build_reveal_fallback_response(plan, batch, exc)
                    protected_values = response.protected_values_by_column.get(work_item.column_name, [])
                    external_headers = response.external_headers_by_column.get(work_item.column_name, [])
                    if len(protected_values) != len(batch.row_indexes):
                        raise ValueError(
                            "Batch response size did not match request size for column "
                            f"{work_item.column_name}."
                        )
                    if (
                        operation == "protect"
                        and work_item.policy_type == "external"
                        and len(external_headers) != len(batch.row_indexes)
                    ):
                        raise ValueError(
                            "Batch external header size did not match request size for column "
                            f"{work_item.column_name}."
                        )
                    for batch_index, (row_index, protected_value) in enumerate(zip(batch.row_indexes, protected_values)):
                        output_column[row_index] = protected_value
                        if (
                            operation == "protect"
                            and work_item.policy_type == "external"
                            and work_item.external_header_column_name
                        ):
                            transformed_columns[work_item.external_header_column_name][row_index] = external_headers[
                                batch_index
                            ]
                        transformed_value_count += 1
                    request_traces.append(response.request_trace)

        return BulkColumnarExecutionResult(
            plan=plan,
            columns=transformed_columns,
            input_row_count=row_count,
            transformed_value_count=transformed_value_count,
            request_count=len(request_traces),
            requests=request_traces,
        )

    def _build_column_batches(
        self,
        work_item: ProtectWorkItem,
        rows: list[dict],
    ) -> list[ProtectBatchRequest]:
        pending_indexes: list[int] = []
        pending_values: list[str] = []
        pending_external_versions: list[str | None] = []
        requests: list[ProtectBatchRequest] = []

        for row_index, row in enumerate(rows):
            if work_item.column_name not in row:
                continue
            value = row.get(work_item.column_name)
            if value is None:
                continue
            pending_indexes.append(row_index)
            pending_values.append(str(value))
            pending_external_versions.append(self._resolve_external_version(row, work_item))
            if len(pending_values) >= work_item.batch_size:
                requests.append(
                    ProtectBatchRequest(
                        work_item=work_item,
                        row_indexes=list(pending_indexes),
                        values=list(pending_values),
                        external_versions=list(pending_external_versions),
                    )
                )
                pending_indexes.clear()
                pending_values.clear()
                pending_external_versions.clear()

        if pending_values:
            requests.append(
                ProtectBatchRequest(
                    work_item=work_item,
                    row_indexes=list(pending_indexes),
                    values=list(pending_values),
                    external_versions=list(pending_external_versions),
                )
            )
        return requests

    def _build_multi_column_batches(
        self,
        work_items: list[ProtectWorkItem],
        rows: list[dict],
        spark_group_size: int,
        max_items_per_request: int,
        max_policy_groups_per_request: int,
    ) -> list[ProtectMultiBatchRequest]:
        requests: list[ProtectMultiBatchRequest] = []
        effective_group_size = max(spark_group_size, 1)
        effective_max_items = max(max_items_per_request, 1)
        effective_max_policy_groups = max(max_policy_groups_per_request, 1)

        for start in range(0, len(rows), effective_group_size):
            end = min(start + effective_group_size, len(rows))
            column_batches: list[list[ProtectBatchRequest]] = []
            for work_item in work_items:
                row_indexes: list[int] = []
                values: list[str] = []
                external_versions: list[str | None] = []
                requests_for_column: list[ProtectBatchRequest] = []
                for row_index in range(start, end):
                    row = rows[row_index]
                    if work_item.column_name not in row:
                        continue
                    value = row.get(work_item.column_name)
                    if value is None:
                        continue
                    row_indexes.append(row_index)
                    values.append(str(value))
                    external_versions.append(self._resolve_external_version(row, work_item))
                    if len(values) >= effective_max_items:
                        requests_for_column.append(
                            ProtectBatchRequest(
                                work_item=work_item,
                                row_indexes=list(row_indexes),
                                values=list(values),
                                external_versions=list(external_versions),
                            )
                        )
                        row_indexes.clear()
                        values.clear()
                        external_versions.clear()
                if values:
                    requests_for_column.append(
                        ProtectBatchRequest(
                            work_item=work_item,
                            row_indexes=list(row_indexes),
                            values=list(values),
                            external_versions=list(external_versions),
                        )
                    )
                if requests_for_column:
                    column_batches.append(requests_for_column)

            active_batches = [list(batches) for batches in column_batches]
            while active_batches:
                grouped_requests: list[ProtectBatchRequest] = []
                remaining_batches: list[list[ProtectBatchRequest]] = []
                for batches in active_batches:
                    if len(grouped_requests) < effective_max_policy_groups:
                        grouped_requests.append(batches.pop(0))
                    if batches:
                        remaining_batches.append(batches)
                if grouped_requests:
                    requests.append(ProtectMultiBatchRequest(requests=grouped_requests))
                active_batches = remaining_batches

        return requests

    def _build_column_batches_from_columns(
        self,
        work_item: ProtectWorkItem,
        columns: dict[str, list],
        row_count: int,
    ) -> list[ProtectBatchRequest]:
        source_values = columns.get(work_item.column_name) or []
        external_versions_source = (
            columns.get(work_item.external_header_column_name)
            if work_item.external_header_column_name
            else None
        )
        pending_indexes: list[int] = []
        pending_values: list[str] = []
        pending_external_versions: list[str | None] = []
        requests: list[ProtectBatchRequest] = []

        for row_index in range(row_count):
            value = source_values[row_index] if row_index < len(source_values) else None
            if value is None:
                continue
            pending_indexes.append(row_index)
            pending_values.append(str(value))
            pending_external_versions.append(
                self._resolve_external_version_from_column_values(
                    external_versions_source,
                    row_index,
                    work_item,
                )
            )
            if len(pending_values) >= work_item.batch_size:
                requests.append(
                    ProtectBatchRequest(
                        work_item=work_item,
                        row_indexes=list(pending_indexes),
                        values=list(pending_values),
                        external_versions=list(pending_external_versions),
                    )
                )
                pending_indexes.clear()
                pending_values.clear()
                pending_external_versions.clear()

        if pending_values:
            requests.append(
                ProtectBatchRequest(
                    work_item=work_item,
                    row_indexes=list(pending_indexes),
                    values=list(pending_values),
                    external_versions=list(pending_external_versions),
                )
            )
        return requests

    def _build_multi_column_batches_from_columns(
        self,
        work_items: list[ProtectWorkItem],
        columns: dict[str, list],
        row_count: int,
        spark_group_size: int,
        max_items_per_request: int,
        max_policy_groups_per_request: int,
    ) -> list[ProtectMultiBatchRequest]:
        requests: list[ProtectMultiBatchRequest] = []
        effective_group_size = max(spark_group_size, 1)
        effective_max_items = max(max_items_per_request, 1)
        effective_max_policy_groups = max(max_policy_groups_per_request, 1)

        for start in range(0, row_count, effective_group_size):
            end = min(start + effective_group_size, row_count)
            column_batches: list[list[ProtectBatchRequest]] = []
            for work_item in work_items:
                source_values = columns.get(work_item.column_name) or []
                external_versions_source = (
                    columns.get(work_item.external_header_column_name)
                    if work_item.external_header_column_name
                    else None
                )
                row_indexes: list[int] = []
                values: list[str] = []
                external_versions: list[str | None] = []
                requests_for_column: list[ProtectBatchRequest] = []
                for row_index in range(start, end):
                    value = source_values[row_index] if row_index < len(source_values) else None
                    if value is None:
                        continue
                    row_indexes.append(row_index)
                    values.append(str(value))
                    external_versions.append(
                        self._resolve_external_version_from_column_values(
                            external_versions_source,
                            row_index,
                            work_item,
                        )
                    )
                    if len(values) >= effective_max_items:
                        requests_for_column.append(
                            ProtectBatchRequest(
                                work_item=work_item,
                                row_indexes=list(row_indexes),
                                values=list(values),
                                external_versions=list(external_versions),
                            )
                        )
                        row_indexes.clear()
                        values.clear()
                        external_versions.clear()
                if values:
                    requests_for_column.append(
                        ProtectBatchRequest(
                            work_item=work_item,
                            row_indexes=list(row_indexes),
                            values=list(values),
                            external_versions=list(external_versions),
                        )
                    )
                if requests_for_column:
                    column_batches.append(requests_for_column)

            active_batches = [list(batches) for batches in column_batches]
            while active_batches:
                grouped_requests: list[ProtectBatchRequest] = []
                remaining_batches: list[list[ProtectBatchRequest]] = []
                for batches in active_batches:
                    if len(grouped_requests) < effective_max_policy_groups:
                        grouped_requests.append(batches.pop(0))
                    if batches:
                        remaining_batches.append(batches)
                if grouped_requests:
                    requests.append(ProtectMultiBatchRequest(requests=grouped_requests))
                active_batches = remaining_batches

        return requests

    def _resolve_external_version(self, row: dict, work_item: ProtectWorkItem) -> str | None:
        if work_item.policy_type != "external":
            return None
        if work_item.external_header_column_name and work_item.external_header_column_name in row:
            header_value = row.get(work_item.external_header_column_name)
            if header_value is not None and str(header_value).strip():
                return str(header_value).strip()
        if work_item.metadata and str(work_item.metadata).strip():
            return str(work_item.metadata).strip()
        return None

    def _resolve_external_version_from_column_values(
        self,
        external_versions: list | None,
        row_index: int,
        work_item: ProtectWorkItem,
    ) -> str | None:
        if work_item.policy_type != "external":
            return None
        if external_versions is not None and row_index < len(external_versions):
            header_value = external_versions[row_index]
            if header_value is not None and str(header_value).strip():
                return str(header_value).strip()
        if work_item.metadata and str(work_item.metadata).strip():
            return str(work_item.metadata).strip()
        return None

    def _copy_column(self, values: list | None, row_count: int) -> list:
        if values is None:
            return [None] * row_count
        copied = list(values)
        if len(copied) < row_count:
            copied.extend([None] * (row_count - len(copied)))
        elif len(copied) > row_count:
            copied = copied[:row_count]
        return copied


def _should_fail_open_reveal(plan: BulkPlan) -> bool:
    return plan.mode == "reveal" and bool(getattr(plan.config, "reveal_fail_open_to_ciphertext", False))


def _build_reveal_fallback_response(
    plan: BulkPlan,
    batch: ProtectBatchRequest,
    exc: Exception,
) -> ProtectTransportResult:
    return ProtectTransportResult(
        protected_values_by_column={batch.work_item.column_name: list(batch.values)},
        external_headers_by_column={},
        request_trace={
            "transport_mode": "fallback_ciphertext",
            "mode": "reveal",
            "api_version": plan.api_version,
            "object_name": plan.object_name,
            "column_name": batch.work_item.column_name,
            "batch_size": len(batch.values),
            "fallback_reason": repr(exc),
        },
    )


def _build_grouped_reveal_fallback_response(
    plan: BulkPlan,
    multi_batch: ProtectMultiBatchRequest,
    exc: Exception,
) -> ProtectTransportResult:
    return ProtectTransportResult(
        protected_values_by_column={
            batch_request.work_item.column_name: list(batch_request.values)
            for batch_request in multi_batch.requests
        },
        external_headers_by_column={},
        request_trace={
            "transport_mode": "fallback_ciphertext",
            "mode": "reveal",
            "api_version": plan.api_version,
            "object_name": plan.object_name,
            "column_names": [batch_request.work_item.column_name for batch_request in multi_batch.requests],
            "batch_sizes": {
                batch_request.work_item.column_name: len(batch_request.values)
                for batch_request in multi_batch.requests
            },
            "fallback_reason": repr(exc),
        },
    )


def _log_reveal_fail_open(
    plan: BulkPlan,
    execution_shape: str,
    work_items: list[ProtectWorkItem],
    exc: Exception,
) -> None:
    level_name = str(getattr(plan.config, "reveal_fail_open_log_level", "ERROR") or "ERROR").upper()
    level = getattr(logging, level_name, logging.ERROR)
    raw_properties = getattr(plan.config, "raw_properties", {}) or {}
    LOGGER.log(
        level,
        (
            "Reveal failed open to ciphertext. execution_shape=%s, object_name=%s, "
            "column_names=%s, api_version=%s, transport_mode=%s, config_version=%s, "
            "config_release_date=%s, config_change_ref=%s, error=%r"
        ),
        execution_shape,
        plan.object_name,
        [work_item.column_name for work_item in work_items],
        plan.api_version,
        getattr(plan.config, "transport_mode", "<unknown>"),
        raw_properties.get("CONFIG_VERSION", "<not set>"),
        raw_properties.get("CONFIG_RELEASE_DATE", "<not set>"),
        raw_properties.get("CONFIG_CHANGE_REF", "<not set>"),
        exc,
    )
