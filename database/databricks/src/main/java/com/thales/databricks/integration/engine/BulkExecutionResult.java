package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;
import java.util.Map;

public final class BulkExecutionResult {

    private final BulkPlan plan;
    private final List<Map<String, Object>> rows;
    private final int inputRowCount;
    private final int transformedValueCount;
    private final int requestCount;
    private final List<Map<String, Object>> requests;

    public BulkExecutionResult(
            BulkPlan plan,
            List<Map<String, Object>> rows,
            int inputRowCount,
            int transformedValueCount,
            int requestCount,
            List<Map<String, Object>> requests) {
        this.plan = plan;
        this.rows = rows == null ? List.of() : Collections.unmodifiableList(rows);
        this.inputRowCount = inputRowCount;
        this.transformedValueCount = transformedValueCount;
        this.requestCount = requestCount;
        this.requests = requests == null ? List.of() : Collections.unmodifiableList(requests);
    }

    public BulkPlan getPlan() {
        return plan;
    }

    public List<Map<String, Object>> getRows() {
        return rows;
    }

    public int getInputRowCount() {
        return inputRowCount;
    }

    public int getTransformedValueCount() {
        return transformedValueCount;
    }

    public int getRequestCount() {
        return requestCount;
    }

    public List<Map<String, Object>> getRequests() {
        return requests;
    }
}
