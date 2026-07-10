package com.thales.databricks.integration.engine;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class ProtectRequestBuilder {

    public ProtectTransportRequest buildRequest(ProtectBatchRequest request, String apiVersion) {
        String normalizedApiVersion = apiVersion == null ? "v2" : apiVersion.trim().toLowerCase();
        if ("v1".equals(normalizedApiVersion)) {
            return buildV1Request(request);
        }
        return buildV2Request(request);
    }

    public ProtectTransportRequest buildGroupedRequest(ProtectMultiBatchRequest request, String apiVersion) {
        String normalizedApiVersion = apiVersion == null ? "v2" : apiVersion.trim().toLowerCase();
        if ("v1".equals(normalizedApiVersion)) {
            throw new IllegalArgumentException("Grouped multi-policy requests are only supported on the v2 path.");
        }

        List<Map<String, Object>> requestData = new ArrayList<>();
        List<Integer> rowIndexes = new ArrayList<>();
        List<ProtectWorkItem> workItems = new ArrayList<>();
        Map<String, List<String>> valuesByColumn = new LinkedHashMap<>();

        for (ProtectBatchRequest batchRequest : request.getRequests()) {
            Map<String, Object> group = new LinkedHashMap<>();
            group.put("protection_policy_name", batchRequest.getWorkItem().getProfileName());
            group.put("data_array", new ArrayList<>(batchRequest.getValues()));
            requestData.add(group);
            rowIndexes.addAll(batchRequest.getRowIndexes());
            workItems.add(batchRequest.getWorkItem());
            valuesByColumn.put(batchRequest.getWorkItem().getColumnName(), new ArrayList<>(batchRequest.getValues()));
        }

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("request_data", requestData);
        return new ProtectTransportRequest(
                "v2",
                "/v2/protectbulk",
                payload,
                rowIndexes,
                workItems,
                valuesByColumn);
    }

    private ProtectTransportRequest buildV1Request(ProtectBatchRequest request) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("protection_policy_name", request.getWorkItem().getProfileName());
        payload.put("data_array", new ArrayList<>(request.getValues()));
        return new ProtectTransportRequest(
                "v1",
                "/v1/protectbulk",
                payload,
                new ArrayList<>(request.getRowIndexes()),
                List.of(request.getWorkItem()),
                Map.of(request.getWorkItem().getColumnName(), new ArrayList<>(request.getValues())));
    }

    private ProtectTransportRequest buildV2Request(ProtectBatchRequest request) {
        Map<String, Object> group = new LinkedHashMap<>();
        group.put("protection_policy_name", request.getWorkItem().getProfileName());
        group.put("data_array", new ArrayList<>(request.getValues()));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("request_data", List.of(group));
        return new ProtectTransportRequest(
                "v2",
                "/v2/protectbulk",
                payload,
                new ArrayList<>(request.getRowIndexes()),
                List.of(request.getWorkItem()),
                Map.of(request.getWorkItem().getColumnName(), new ArrayList<>(request.getValues())));
    }
}
