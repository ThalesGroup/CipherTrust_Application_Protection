from __future__ import annotations

from .config import IntegrationConfig
from .models import BulkPlan, ColumnPlan, ProtectWorkItem


class BulkPlanner:
    def __init__(self, config: IntegrationConfig) -> None:
        self._config = config

    def plan_protect(self, object_name: str, column_names: list[str]) -> BulkPlan:
        return self._plan(object_name, column_names, mode="protect", runtime_reveal_user=None)

    def plan_reveal(
        self,
        object_name: str,
        column_names: list[str],
        runtime_reveal_user: str | None = None,
    ) -> BulkPlan:
        return self._plan(object_name, column_names, mode="reveal", runtime_reveal_user=runtime_reveal_user)

    def _plan(
        self,
        object_name: str,
        column_names: list[str],
        mode: str,
        runtime_reveal_user: str | None,
    ) -> BulkPlan:
        columns: list[ColumnPlan] = []
        work_items: list[ProtectWorkItem] = []
        for column_name in column_names:
            datatype = self._config.resolve_datatype(object_name, column_name)
            profile_name = self._config.resolve_profile(object_name, column_name, mode=mode)
            policy_type = self._config.resolve_policy_type(object_name, column_name, datatype, mode)
            metadata = self._config.resolve_metadata(object_name, column_name)
            reveal_user = self._config.resolve_reveal_user(object_name, column_name, runtime_reveal_user)
            columns.append(
                ColumnPlan(
                    object_name=object_name,
                    column_name=column_name,
                    datatype=datatype,
                    profile_name=profile_name,
                )
            )
            work_items.append(
                ProtectWorkItem(
                    object_name=object_name,
                    column_name=column_name,
                    datatype=datatype,
                    profile_name=profile_name,
                    policy_type=policy_type,
                    metadata=metadata,
                    reveal_user=reveal_user,
                    external_header_column_name=self._config.resolve_external_header_column_name(column_name),
                    batch_size=self._config.default_batch_size,
                )
            )
        return BulkPlan(
            mode=mode,
            object_name=object_name,
            columns=columns,
            work_items=work_items,
            config=self._config,
            api_version=self._config.crdp_api_version,
            batch_size=self._config.default_batch_size,
            spark_group_size=self._config.spark_group_size,
            v2_max_items_per_request=self._config.crdp_v2_max_items_per_request,
            v2_max_policy_groups_per_request=self._config.crdp_v2_max_policy_groups_per_request,
            v2_enable_multi_policy=self._config.crdp_v2_enable_multi_policy,
        )
