from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
from pathlib import Path

from .api import protect_rows, reveal_rows
from .config import IntegrationConfig


def uc_protect_by_object_and_column(
    value: str | None,
    object_name: str,
    column_name: str,
    config_path: str,
    transport_mode: str = "real",
) -> str | None:
    if value is None:
        return None
    config = _load_config(config_path, transport_mode)
    result = protect_rows(
        rows=[{column_name: value}],
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
    )
    if not result.rows:
        return value
    return result.rows[0].get(column_name)


def uc_protect_by_object_and_column_embedded(
    value: str | None,
    object_name: str,
    column_name: str,
    properties: dict[str, str],
    transport_mode: str = "real",
) -> str | None:
    if value is None:
        return None
    config = _load_embedded_config(properties, transport_mode)
    result = protect_rows(
        rows=[{column_name: value}],
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
    )
    if not result.rows:
        return value
    return result.rows[0].get(column_name)


def uc_reveal_by_object_and_column(
    value: str | None,
    object_name: str,
    column_name: str,
    config_path: str,
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> str | None:
    if value is None:
        return None
    config = _load_config(config_path, transport_mode)
    result = reveal_rows(
        rows=[{column_name: value}],
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
        reveal_user=reveal_user,
    )
    if not result.rows:
        return value
    return result.rows[0].get(column_name)


def uc_reveal_by_object_and_column_embedded(
    value: str | None,
    object_name: str,
    column_name: str,
    properties: dict[str, str],
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> str | None:
    if value is None:
        return None
    config = _load_embedded_config(properties, transport_mode)
    result = reveal_rows(
        rows=[{column_name: value}],
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
        reveal_user=reveal_user,
    )
    if not result.rows:
        return value
    return result.rows[0].get(column_name)


def uc_protect_bulk_by_object_and_column(
    values: list[str] | None,
    object_name: str,
    column_name: str,
    config_path: str,
    transport_mode: str = "real",
) -> list[str] | None:
    if values is None:
        return None
    config = _load_config(config_path, transport_mode)
    rows = [{column_name: value} for value in values]
    result = protect_rows(
        rows=rows,
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
    )
    return [row.get(column_name) for row in result.rows]


def uc_protect_bulk_by_object_and_column_embedded(
    values: list[str] | None,
    object_name: str,
    column_name: str,
    properties: dict[str, str],
    transport_mode: str = "real",
) -> list[str] | None:
    if values is None:
        return None
    config = _load_embedded_config(properties, transport_mode)
    rows = [{column_name: value} for value in values]
    result = protect_rows(
        rows=rows,
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
    )
    return [row.get(column_name) for row in result.rows]


def uc_reveal_bulk_by_object_and_column(
    values: list[str] | None,
    object_name: str,
    column_name: str,
    config_path: str,
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> list[str] | None:
    if values is None:
        return None
    config = _load_config(config_path, transport_mode)
    rows = [{column_name: value} for value in values]
    result = reveal_rows(
        rows=rows,
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
        reveal_user=reveal_user,
    )
    return [row.get(column_name) for row in result.rows]


def uc_reveal_bulk_by_object_and_column_embedded(
    values: list[str] | None,
    object_name: str,
    column_name: str,
    properties: dict[str, str],
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> list[str] | None:
    if values is None:
        return None
    config = _load_embedded_config(properties, transport_mode)
    rows = [{column_name: value} for value in values]
    result = reveal_rows(
        rows=rows,
        object_name=object_name,
        sensitive_columns=[column_name],
        config=config,
        reveal_user=reveal_user,
    )
    return [row.get(column_name) for row in result.rows]


def uc_reveal_rowset_embedded(
    column_values: dict[str, list[str] | None] | None,
    object_name: str,
    properties: dict[str, str],
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> dict[str, list[str] | None]:
    if not column_values:
        return {}

    config = _load_embedded_config(properties, transport_mode)
    normalized_columns = [str(column_name) for column_name in column_values.keys()]
    normalized_values = {
        str(column_name): value_list
        for column_name, value_list in column_values.items()
    }

    row_count = _resolve_rowset_size(normalized_values)
    rows: list[dict[str, str | None]] = []
    for row_index in range(row_count):
        row: dict[str, str | None] = {}
        for column_name, value_list in normalized_values.items():
            row[column_name] = value_list[row_index] if value_list is not None else None
        rows.append(row)

    result = reveal_rows(
        rows=rows,
        object_name=object_name,
        sensitive_columns=normalized_columns,
        config=config,
        reveal_user=reveal_user,
    )
    return {
        f"{column_name}_decrypted": [row.get(column_name) for row in result.rows]
        for column_name in normalized_columns
    }


def uc_protect_row(
    values: dict[str, str | None],
    object_name: str,
    config_path: str,
    transport_mode: str = "real",
) -> dict[str, str | None]:
    if values is None:
        return {}
    config = _load_config(config_path, transport_mode)
    result = protect_rows(
        rows=[dict(values)],
        object_name=object_name,
        config=config,
    )
    return result.rows[0] if result.rows else dict(values)


def uc_reveal_row(
    values: dict[str, str | None],
    object_name: str,
    config_path: str,
    reveal_user: str | None = None,
    transport_mode: str = "real",
) -> dict[str, str | None]:
    if values is None:
        return {}
    config = _load_config(config_path, transport_mode)
    result = reveal_rows(
        rows=[dict(values)],
        object_name=object_name,
        config=config,
        reveal_user=reveal_user,
    )
    return result.rows[0] if result.rows else dict(values)


@lru_cache(maxsize=16)
def _cached_config(config_path: str) -> IntegrationConfig:
    return IntegrationConfig.from_properties(Path(config_path))


def _load_config(config_path: str, transport_mode: str) -> IntegrationConfig:
    base_config = _cached_config(config_path)
    return replace(base_config, transport_mode=transport_mode)


def _load_embedded_config(properties: dict[str, str], transport_mode: str) -> IntegrationConfig:
    base_config = IntegrationConfig.from_dict({str(key): str(value) for key, value in properties.items()})
    return replace(base_config, transport_mode=transport_mode)


def _resolve_rowset_size(column_values: dict[str, list[str] | None]) -> int:
    lengths = {len(value_list) for value_list in column_values.values() if value_list is not None}
    if not lengths:
        return 0
    if len(lengths) != 1:
        raise ValueError("All rowset arrays must have the same length.")
    return next(iter(lengths))
