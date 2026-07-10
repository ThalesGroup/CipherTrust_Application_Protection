package com.thales.databricks.integration.engine;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class StubProtectTransport implements ProtectTransport {

    private final ProtectRequestBuilder requestBuilder;

    public StubProtectTransport() {
        this(new ProtectRequestBuilder());
    }

    public StubProtectTransport(ProtectRequestBuilder requestBuilder) {
        this.requestBuilder = requestBuilder;
    }

    @Override
    public ProtectTransportResult protectBatch(ProtectBatchRequest request, String apiVersion) {
        ProtectTransportRequest transportRequest = requestBuilder.buildRequest(request, apiVersion);
        List<String> protectedValues = new ArrayList<>();
        for (String value : request.getValues()) {
            protectedValues.add("stub:"
                    + request.getWorkItem().getDatatype()
                    + ":"
                    + safe(request.getWorkItem().getProfileName())
                    + ":"
                    + value);
        }
        return new ProtectTransportResult(
                Map.of(request.getWorkItem().getColumnName(), protectedValues),
                Map.of(
                        "api_version", transportRequest.getApiVersion(),
                        "endpoint", transportRequest.getEndpoint(),
                        "column_name", request.getWorkItem().getColumnName(),
                        "datatype", request.getWorkItem().getDatatype(),
                        "profile_name", safe(request.getWorkItem().getProfileName()),
                        "batch_size", request.getValues().size(),
                        "payload", transportRequest.getPayload()));
    }

    @Override
    public ProtectTransportResult protectGroupedBatch(ProtectMultiBatchRequest request, String apiVersion) {
        ProtectTransportRequest transportRequest = requestBuilder.buildGroupedRequest(request, apiVersion);
        Map<String, List<String>> protectedValuesByColumn = new java.util.LinkedHashMap<>();

        for (ProtectBatchRequest batchRequest : request.getRequests()) {
            List<String> protectedValues = new ArrayList<>();
            for (String value : batchRequest.getValues()) {
                protectedValues.add("stub:"
                        + batchRequest.getWorkItem().getDatatype()
                        + ":"
                        + safe(batchRequest.getWorkItem().getProfileName())
                        + ":"
                        + value);
            }
            protectedValuesByColumn.put(batchRequest.getWorkItem().getColumnName(), protectedValues);
        }

        return new ProtectTransportResult(
                protectedValuesByColumn,
                Map.of(
                        "api_version", transportRequest.getApiVersion(),
                        "endpoint", transportRequest.getEndpoint(),
                        "column_count", request.getRequests().size(),
                        "column_names", request.getRequests().stream()
                                .map(batchRequest -> batchRequest.getWorkItem().getColumnName())
                                .toList(),
                        "batch_sizes", request.getRequests().stream().collect(
                                java.util.stream.Collectors.toMap(
                                        batchRequest -> batchRequest.getWorkItem().getColumnName(),
                                        batchRequest -> batchRequest.getValues().size(),
                                        (left, right) -> right,
                                        java.util.LinkedHashMap::new)),
                        "payload", transportRequest.getPayload()));
    }

    private String safe(String value) {
        return value == null ? "unresolved" : value;
    }
}
