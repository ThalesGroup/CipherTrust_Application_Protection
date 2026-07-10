from __future__ import annotations

from dataclasses import dataclass
import json
import ssl
from urllib import error as urllib_error
from urllib import request as urllib_request

from .config import IntegrationConfig

from .models import ProtectWorkItem


@dataclass(slots=True)
class ProtectBatchRequest:
    work_item: ProtectWorkItem
    row_indexes: list[int]
    values: list[str]
    external_versions: list[str | None] | None = None


@dataclass(slots=True)
class ProtectBatchResponse:
    protected_values: list[str]


@dataclass(slots=True)
class ProtectMultiBatchRequest:
    requests: list[ProtectBatchRequest]


@dataclass(slots=True)
class ProtectTransportRequest:
    api_version: str
    endpoint: str
    payload: dict
    row_indexes: list[int]
    work_items: list[ProtectWorkItem]
    values_by_column: dict[str, list[str]]


@dataclass(slots=True)
class ProtectTransportResult:
    protected_values_by_column: dict[str, list[str]]
    external_headers_by_column: dict[str, list[str | None]]
    request_trace: dict


class ProtectRequestBuilder:
    def build_request(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportRequest:
        normalized_api_version = (api_version or "v2").lower()
        if normalized_api_version == "v1":
            return self._build_v1_request(request)
        return self._build_v2_request(request)

    def _build_v1_request(self, request: ProtectBatchRequest) -> ProtectTransportRequest:
        payload = {
            "protection_policy_name": request.work_item.profile_name,
            "data_array": list(request.values),
        }
        return ProtectTransportRequest(
            api_version="v1",
            endpoint="/v1/protectbulk",
            payload=payload,
            row_indexes=list(request.row_indexes),
            work_items=[request.work_item],
            values_by_column={request.work_item.column_name: list(request.values)},
        )

    def _build_v2_request(self, request: ProtectBatchRequest) -> ProtectTransportRequest:
        payload = {
            "request_data": [
                {
                    "protection_policy_name": request.work_item.profile_name,
                    "data_array": list(request.values),
                }
            ]
        }
        return ProtectTransportRequest(
            api_version="v2",
            endpoint="/v2/protectbulk",
            payload=payload,
            row_indexes=list(request.row_indexes),
            work_items=[request.work_item],
            values_by_column={request.work_item.column_name: list(request.values)},
        )

    def build_reveal_request(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportRequest:
        normalized_api_version = (api_version or "v2").lower()
        if normalized_api_version == "v1":
            return self._build_v1_reveal_request(request)
        return self._build_v2_reveal_request(request)

    def _build_v1_reveal_request(self, request: ProtectBatchRequest) -> ProtectTransportRequest:
        protected_items = []
        for index, value in enumerate(request.values):
            item = {"protected_data": value}
            if request.work_item.policy_type == "external":
                external_version = _resolve_external_version(request, index)
                if external_version:
                    item["external_version"] = external_version
            protected_items.append(item)
        payload = {
            "protection_policy_name": request.work_item.profile_name,
            "username": request.work_item.reveal_user,
            "protected_data_array": protected_items,
        }
        return ProtectTransportRequest(
            api_version="v1",
            endpoint="/v1/revealbulk",
            payload=payload,
            row_indexes=list(request.row_indexes),
            work_items=[request.work_item],
            values_by_column={request.work_item.column_name: list(request.values)},
        )

    def _build_v2_reveal_request(self, request: ProtectBatchRequest) -> ProtectTransportRequest:
        return self.build_grouped_reveal_request(ProtectMultiBatchRequest(requests=[request]), api_version="v2")

    def build_grouped_request(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportRequest:
        normalized_api_version = (api_version or "v2").lower()
        if normalized_api_version == "v1":
            raise ValueError("Grouped multi-policy requests are only supported on the v2 path.")

        request_data = []
        row_indexes: list[int] = []
        work_items: list[ProtectWorkItem] = []
        values_by_column: dict[str, list[str]] = {}

        for batch_request in request.requests:
            request_data.append(
                {
                    "protection_policy_name": batch_request.work_item.profile_name,
                    "data_array": list(batch_request.values),
                }
            )
            row_indexes.extend(batch_request.row_indexes)
            work_items.append(batch_request.work_item)
            values_by_column[batch_request.work_item.column_name] = list(batch_request.values)

        return ProtectTransportRequest(
            api_version="v2",
            endpoint="/v2/protectbulk",
            payload={"request_data": request_data},
            row_indexes=row_indexes,
            work_items=work_items,
            values_by_column=values_by_column,
        )

    def build_grouped_reveal_request(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportRequest:
        normalized_api_version = (api_version or "v2").lower()
        if normalized_api_version == "v1":
            raise ValueError("Grouped multi-policy reveal requests are only supported on the v2 path.")

        request_data = []
        row_indexes: list[int] = []
        work_items: list[ProtectWorkItem] = []
        values_by_column: dict[str, list[str]] = {}

        for batch_request in request.requests:
            protected_items = []
            for index, value in enumerate(batch_request.values):
                item = {"protected_data": value}
                if batch_request.work_item.policy_type == "external":
                    external_version = _resolve_external_version(batch_request, index)
                    if external_version:
                        item["external_version"] = external_version
                protected_items.append(item)
            request_data.append(
                {
                    "protection_policy_name": batch_request.work_item.profile_name,
                    "protected_data_array": protected_items,
                }
            )
            row_indexes.extend(batch_request.row_indexes)
            work_items.append(batch_request.work_item)
            values_by_column[batch_request.work_item.column_name] = list(batch_request.values)

        payload = {
            "username": _resolve_request_reveal_user(request.requests),
            "request_data": request_data,
        }
        return ProtectTransportRequest(
            api_version="v2",
            endpoint="/v2/revealbulk",
            payload=payload,
            row_indexes=row_indexes,
            work_items=work_items,
            values_by_column=values_by_column,
        )


class StubBulkTransport:
    """
    Bulk-oriented local transport stub.

    The important part is that this receives batches of values for one work
    item, which matches the bulk-first execution model better than row-by-row
    transformation.
    """

    def __init__(self, request_builder: ProtectRequestBuilder | None = None) -> None:
        self._request_builder = request_builder or ProtectRequestBuilder()

    def protect_batch(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportResult:
        transport_request = self._request_builder.build_request(request, api_version)
        column_name = request.work_item.column_name
        protected_values = [
            f"stub:{request.work_item.datatype}:{request.work_item.profile_name or 'unresolved'}:{value}"
            for value in request.values
        ]
        return ProtectTransportResult(
            protected_values_by_column={column_name: protected_values},
            external_headers_by_column={
                column_name: [
                    request.work_item.metadata if request.work_item.policy_type == "external" else None
                    for _ in request.values
                ]
            },
            request_trace={
                "transport_mode": "stub",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_name": column_name,
                "datatype": request.work_item.datatype,
                "profile_name": request.work_item.profile_name,
                "batch_size": len(request.values),
                "payload": transport_request.payload,
            },
        )

    def protect_grouped_batch(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportResult:
        transport_request = self._request_builder.build_grouped_request(request, api_version)
        protected_values_by_column: dict[str, list[str]] = {}

        for batch_request in request.requests:
            protected_values_by_column[batch_request.work_item.column_name] = [
                f"stub:{batch_request.work_item.datatype}:{batch_request.work_item.profile_name or 'unresolved'}:{value}"
                for value in batch_request.values
            ]

        return ProtectTransportResult(
            protected_values_by_column=protected_values_by_column,
            external_headers_by_column={
                batch_request.work_item.column_name: [
                    batch_request.work_item.metadata if batch_request.work_item.policy_type == "external" else None
                    for _ in batch_request.values
                ]
                for batch_request in request.requests
            },
            request_trace={
                "transport_mode": "stub",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_count": len(request.requests),
                "column_names": [batch_request.work_item.column_name for batch_request in request.requests],
                "batch_sizes": {
                    batch_request.work_item.column_name: len(batch_request.values)
                    for batch_request in request.requests
                },
                "payload": transport_request.payload,
            },
        )

    def reveal_batch(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportResult:
        transport_request = self._request_builder.build_reveal_request(request, api_version)
        column_name = request.work_item.column_name
        revealed_values = [_strip_stub_prefix(value) for value in request.values]
        return ProtectTransportResult(
            protected_values_by_column={column_name: revealed_values},
            external_headers_by_column={},
            request_trace={
                "transport_mode": "stub",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_name": column_name,
                "datatype": request.work_item.datatype,
                "profile_name": request.work_item.profile_name,
                "batch_size": len(request.values),
                "payload": transport_request.payload,
            },
        )

    def reveal_grouped_batch(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportResult:
        transport_request = self._request_builder.build_grouped_reveal_request(request, api_version)
        revealed_values_by_column: dict[str, list[str]] = {}
        for batch_request in request.requests:
            revealed_values_by_column[batch_request.work_item.column_name] = [
                _strip_stub_prefix(value) for value in batch_request.values
            ]
        return ProtectTransportResult(
            protected_values_by_column=revealed_values_by_column,
            external_headers_by_column={},
            request_trace={
                "transport_mode": "stub",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_count": len(request.requests),
                "column_names": [batch_request.work_item.column_name for batch_request in request.requests],
                "batch_sizes": {
                    batch_request.work_item.column_name: len(batch_request.values)
                    for batch_request in request.requests
                },
                "payload": transport_request.payload,
            },
        )


class RealCrdpBulkTransport:
    def __init__(
        self,
        config: IntegrationConfig,
        request_builder: ProtectRequestBuilder | None = None,
    ) -> None:
        self._config = config
        self._request_builder = request_builder or ProtectRequestBuilder()

    def protect_batch(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportResult:
        transport_request = self._request_builder.build_request(request, api_version)
        response_payload = self._post_json(transport_request.endpoint, transport_request.payload)
        protected_values_by_column = self._parse_protect_response(transport_request, response_payload)
        return ProtectTransportResult(
            protected_values_by_column=protected_values_by_column,
            external_headers_by_column=self._parse_protect_headers(transport_request, response_payload),
            request_trace={
                "transport_mode": "real",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_name": request.work_item.column_name,
                "datatype": request.work_item.datatype,
                "profile_name": request.work_item.profile_name,
                "batch_size": len(request.values),
                "payload": transport_request.payload,
                "response_status": response_payload.get("status"),
            },
        )

    def protect_grouped_batch(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportResult:
        transport_request = self._request_builder.build_grouped_request(request, api_version)
        response_payload = self._post_json(transport_request.endpoint, transport_request.payload)
        protected_values_by_column = self._parse_protect_response(transport_request, response_payload)
        return ProtectTransportResult(
            protected_values_by_column=protected_values_by_column,
            external_headers_by_column=self._parse_protect_headers(transport_request, response_payload),
            request_trace={
                "transport_mode": "real",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_count": len(request.requests),
                "column_names": [batch_request.work_item.column_name for batch_request in request.requests],
                "batch_sizes": {
                    batch_request.work_item.column_name: len(batch_request.values)
                    for batch_request in request.requests
                },
                "payload": transport_request.payload,
                "response_status": response_payload.get("status"),
            },
        )

    def reveal_batch(self, request: ProtectBatchRequest, api_version: str) -> ProtectTransportResult:
        transport_request = self._request_builder.build_reveal_request(request, api_version)
        response_payload = self._post_json(transport_request.endpoint, transport_request.payload)
        revealed_values_by_column = self._parse_reveal_response(transport_request, response_payload)
        return ProtectTransportResult(
            protected_values_by_column=revealed_values_by_column,
            external_headers_by_column={},
            request_trace={
                "transport_mode": "real",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_name": request.work_item.column_name,
                "datatype": request.work_item.datatype,
                "profile_name": request.work_item.profile_name,
                "batch_size": len(request.values),
                "payload": transport_request.payload,
                "response_status": response_payload.get("status"),
            },
        )

    def reveal_grouped_batch(
        self,
        request: ProtectMultiBatchRequest,
        api_version: str,
    ) -> ProtectTransportResult:
        transport_request = self._request_builder.build_grouped_reveal_request(request, api_version)
        response_payload = self._post_json(transport_request.endpoint, transport_request.payload)
        revealed_values_by_column = self._parse_reveal_response(transport_request, response_payload)
        return ProtectTransportResult(
            protected_values_by_column=revealed_values_by_column,
            external_headers_by_column={},
            request_trace={
                "transport_mode": "real",
                "api_version": transport_request.api_version,
                "endpoint": transport_request.endpoint,
                "column_count": len(request.requests),
                "column_names": [batch_request.work_item.column_name for batch_request in request.requests],
                "batch_sizes": {
                    batch_request.work_item.column_name: len(batch_request.values)
                    for batch_request in request.requests
                },
                "payload": transport_request.payload,
                "response_status": response_payload.get("status"),
            },
        )

    def _post_json(self, endpoint: str, payload: dict) -> dict:
        target_url = _build_url(self._config, endpoint)
        encoded_payload = json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(
            target_url,
            data=encoded_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout_seconds = max(self._config.crdp_connect_timeout_ms, self._config.crdp_read_timeout_ms) / 1000.0
        ssl_context = _build_ssl_context(self._config)
        try:
            with urllib_request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
                response_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise ValueError(
                "CRDP HTTP request failed. "
                f"endpoint={endpoint}, url={target_url}, status={exc.code}, "
                f"payload={json.dumps(payload, ensure_ascii=True)}, "
                f"response_body={error_body}"
            ) from exc
        except Exception as exc:
            raise ValueError(
                "CRDP HTTP request failed before a valid JSON response was received. "
                f"endpoint={endpoint}, url={target_url}, "
                f"payload={json.dumps(payload, ensure_ascii=True)}, error={repr(exc)}"
            ) from exc
        parsed = json.loads(response_body) if response_body else {}
        if not isinstance(parsed, dict):
            raise ValueError("CRDP response was not a JSON object.")
        return parsed

    def _parse_protect_response(
        self,
        transport_request: ProtectTransportRequest,
        response_payload: dict,
    ) -> dict[str, list[str]]:
        if transport_request.api_version == "v1":
            protected_items = response_payload.get("protected_data_array") or []
            if len(transport_request.work_items) != 1:
                raise ValueError("v1 protect parsing expected exactly one work item.")
            return {
                transport_request.work_items[0].column_name: [
                    _require_string(item, "protected_data") for item in protected_items
                ]
            }

        response_groups = response_payload.get("response_data") or []
        if len(response_groups) != len(transport_request.work_items):
            raise ValueError("Unexpected v2 protect response group count.")
        results_by_column: dict[str, list[str]] = {}
        for work_item, response_group in zip(transport_request.work_items, response_groups):
            policy_name = _require_string(response_group, "protection_policy_name")
            if policy_name != work_item.profile_name:
                raise ValueError(
                    "Unexpected protection policy order in CRDP response. "
                    f"Expected {work_item.profile_name}, received {policy_name}."
                )
            protected_items = response_group.get("protected_data_array") or []
            results_by_column[work_item.column_name] = [
                _require_string(item, "protected_data") for item in protected_items
            ]
        return results_by_column

    def _parse_reveal_response(
        self,
        transport_request: ProtectTransportRequest,
        response_payload: dict,
    ) -> dict[str, list[str]]:
        if transport_request.api_version == "v1":
            data_items = response_payload.get("data_array") or []
            if len(transport_request.work_items) != 1:
                raise ValueError("v1 reveal parsing expected exactly one work item.")
            return {
                transport_request.work_items[0].column_name: [
                    _require_string(item, "data") for item in data_items
                ]
            }

        response_groups = response_payload.get("data_array") or []
        if len(response_groups) != len(transport_request.work_items):
            raise ValueError("Unexpected v2 reveal response group count.")
        results_by_column: dict[str, list[str]] = {}
        for work_item, response_group in zip(transport_request.work_items, response_groups):
            results_by_column[work_item.column_name] = [
                _require_string(item, "data") for item in (response_group or [])
            ]
        return results_by_column

    def _parse_protect_headers(
        self,
        transport_request: ProtectTransportRequest,
        response_payload: dict,
    ) -> dict[str, list[str | None]]:
        if transport_request.api_version == "v1":
            if len(transport_request.work_items) != 1:
                raise ValueError("v1 protect header parsing expected exactly one work item.")
            work_item = transport_request.work_items[0]
            if work_item.policy_type != "external":
                return {}
            protected_items = response_payload.get("protected_data_array") or []
            return {
                work_item.column_name: [
                    _optional_string(item, "external_version") for item in protected_items
                ]
            }

        response_groups = response_payload.get("response_data") or []
        if len(response_groups) != len(transport_request.work_items):
            raise ValueError("Unexpected v2 protect response group count.")
        headers_by_column: dict[str, list[str | None]] = {}
        for work_item, response_group in zip(transport_request.work_items, response_groups):
            if work_item.policy_type != "external":
                continue
            protected_items = response_group.get("protected_data_array") or []
            headers_by_column[work_item.column_name] = [
                _optional_string(item, "external_version") for item in protected_items
            ]
        return headers_by_column


def build_transport(config: IntegrationConfig):
    if config.should_use_real_transport():
        return RealCrdpBulkTransport(config)
    return StubBulkTransport()


def _build_url(config: IntegrationConfig, endpoint: str) -> str:
    host = (config.crdp_ip or "").strip()
    if host.startswith("http://") or host.startswith("https://"):
        return f"{host}:{config.crdp_port}{endpoint}"
    scheme = "https" if config.crdp_ssl_enabled else "http"
    return f"{scheme}://{host}:{config.crdp_port}{endpoint}"


def _build_ssl_context(config: IntegrationConfig):
    if not config.crdp_ssl_enabled:
        return None

    if config.crdp_ssl_verify_server:
        ssl_context = ssl.create_default_context(
            cafile=(config.crdp_ca_cert_path or None) if (config.crdp_ca_cert_path or "").strip() else None
        )
    else:
        ssl_context = ssl._create_unverified_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    cert_path = (config.crdp_client_cert_path or "").strip()
    key_path = (config.crdp_client_key_path or "").strip()
    if cert_path:
        ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path or None)
    return ssl_context


def _require_string(item: dict, key: str) -> str:
    if key not in item:
        raise ValueError(f"CRDP response item missing key: {key}")
    return str(item[key])


def _optional_string(item: dict, key: str) -> str | None:
    if key not in item or item[key] is None:
        return None
    value = str(item[key]).strip()
    return value or None


def _resolve_external_version(request: ProtectBatchRequest, index: int) -> str | None:
    if request.external_versions and index < len(request.external_versions):
        value = request.external_versions[index]
        if value is not None and str(value).strip():
            return str(value).strip()
    if request.work_item.metadata and str(request.work_item.metadata).strip():
        return str(request.work_item.metadata).strip()
    return None


def _resolve_request_reveal_user(requests: list[ProtectBatchRequest]) -> str | None:
    for request in requests:
        if request.work_item.reveal_user and str(request.work_item.reveal_user).strip():
            return str(request.work_item.reveal_user).strip()
    return None


def _strip_stub_prefix(value: str) -> str:
    if value.startswith("stub:"):
        parts = value.split(":", 3)
        if len(parts) == 4:
            return parts[3]
    return value
