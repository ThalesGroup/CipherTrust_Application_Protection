package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;
import java.util.Map;

public final class ProtectTransportResult {

    private final Map<String, List<String>> protectedValuesByColumn;
    private final Map<String, Object> requestTrace;

    public ProtectTransportResult(
            Map<String, List<String>> protectedValuesByColumn,
            Map<String, Object> requestTrace) {
        this.protectedValuesByColumn = protectedValuesByColumn == null
                ? Map.of()
                : Collections.unmodifiableMap(protectedValuesByColumn);
        this.requestTrace = requestTrace == null ? Map.of() : Collections.unmodifiableMap(requestTrace);
    }

    public Map<String, List<String>> getProtectedValuesByColumn() {
        return protectedValuesByColumn;
    }

    public Map<String, Object> getRequestTrace() {
        return requestTrace;
    }
}
