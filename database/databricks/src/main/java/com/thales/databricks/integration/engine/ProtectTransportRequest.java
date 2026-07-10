package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;
import java.util.Map;

public final class ProtectTransportRequest {

    private final String apiVersion;
    private final String endpoint;
    private final Map<String, Object> payload;
    private final List<Integer> rowIndexes;
    private final List<ProtectWorkItem> workItems;
    private final Map<String, List<String>> valuesByColumn;

    public ProtectTransportRequest(
            String apiVersion,
            String endpoint,
            Map<String, Object> payload,
            List<Integer> rowIndexes,
            List<ProtectWorkItem> workItems,
            Map<String, List<String>> valuesByColumn) {
        this.apiVersion = apiVersion;
        this.endpoint = endpoint;
        this.payload = payload == null ? Map.of() : Collections.unmodifiableMap(payload);
        this.rowIndexes = rowIndexes == null ? List.of() : Collections.unmodifiableList(rowIndexes);
        this.workItems = workItems == null ? List.of() : Collections.unmodifiableList(workItems);
        this.valuesByColumn = valuesByColumn == null ? Map.of() : Collections.unmodifiableMap(valuesByColumn);
    }

    public String getApiVersion() {
        return apiVersion;
    }

    public String getEndpoint() {
        return endpoint;
    }

    public Map<String, Object> getPayload() {
        return payload;
    }

    public List<Integer> getRowIndexes() {
        return rowIndexes;
    }

    public List<ProtectWorkItem> getWorkItems() {
        return workItems;
    }

    public Map<String, List<String>> getValuesByColumn() {
        return valuesByColumn;
    }
}
