package com.thales.databricks.integration.engine;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class V2BulkEngineStub implements CrdpBulkEngine {

    private final ProtectTransport transport;

    public V2BulkEngineStub() {
        this(new StubProtectTransport());
    }

    public V2BulkEngineStub(ProtectTransport transport) {
        this.transport = transport;
    }

    @Override
    public BulkExecutionResult protectRows(BulkPlan plan, Iterable<Map<String, Object>> rows) throws Exception {
        List<Map<String, Object>> protectedRows = new ArrayList<>();
        int inputRowCount = 0;
        int transformedValueCount = 0;
        List<Map<String, Object>> requestTraces = new ArrayList<>();

        for (Map<String, Object> row : rows) {
            protectedRows.add(new LinkedHashMap<>(row));
            inputRowCount++;
        }

        if ("v2".equalsIgnoreCase(plan.getApiVersion()) && plan.isV2EnableMultiPolicy()) {
            List<ProtectMultiBatchRequest> requests = buildMultiColumnBatches(
                    plan.getWorkItems(),
                    protectedRows,
                    plan.getSparkGroupSize(),
                    plan.getV2MaxItemsPerRequest(),
                    plan.getV2MaxPolicyGroupsPerRequest());
            for (ProtectMultiBatchRequest request : requests) {
                ProtectTransportResult response = transport.protectGroupedBatch(request, plan.getApiVersion());
                for (ProtectBatchRequest batchRequest : request.getRequests()) {
                    List<String> protectedValues = response.getProtectedValuesByColumn()
                            .getOrDefault(batchRequest.getWorkItem().getColumnName(), List.of());
                    if (protectedValues.size() != batchRequest.getRowIndexes().size()) {
                        throw new IllegalStateException("Batch response size did not match request size for column "
                                + batchRequest.getWorkItem().getColumnName());
                    }
                    for (int i = 0; i < batchRequest.getRowIndexes().size(); i++) {
                        int rowIndex = batchRequest.getRowIndexes().get(i);
                        protectedRows.get(rowIndex).put(
                                batchRequest.getWorkItem().getColumnName(),
                                protectedValues.get(i));
                        transformedValueCount++;
                    }
                }
                requestTraces.add(response.getRequestTrace());
            }
        } else {
            for (ProtectWorkItem workItem : plan.getWorkItems()) {
                List<ProtectBatchRequest> requests = buildColumnBatches(workItem, protectedRows);
                for (ProtectBatchRequest request : requests) {
                    ProtectTransportResult response = transport.protectBatch(request, plan.getApiVersion());
                    List<String> protectedValues = response.getProtectedValuesByColumn()
                            .getOrDefault(workItem.getColumnName(), List.of());
                    if (protectedValues.size() != request.getRowIndexes().size()) {
                        throw new IllegalStateException("Batch response size did not match request size for column "
                                + workItem.getColumnName());
                    }
                    for (int i = 0; i < request.getRowIndexes().size(); i++) {
                        int rowIndex = request.getRowIndexes().get(i);
                        protectedRows.get(rowIndex).put(workItem.getColumnName(), protectedValues.get(i));
                        transformedValueCount++;
                    }
                    requestTraces.add(response.getRequestTrace());
                }
            }
        }

        return new BulkExecutionResult(
                plan,
                protectedRows,
                inputRowCount,
                transformedValueCount,
                requestTraces.size(),
                requestTraces);
    }

    private List<ProtectBatchRequest> buildColumnBatches(
            ProtectWorkItem workItem,
            List<Map<String, Object>> rows) {
        List<ProtectBatchRequest> requests = new ArrayList<>();
        List<Integer> pendingIndexes = new ArrayList<>();
        List<String> pendingValues = new ArrayList<>();

        for (int rowIndex = 0; rowIndex < rows.size(); rowIndex++) {
            Map<String, Object> row = rows.get(rowIndex);
            if (!row.containsKey(workItem.getColumnName())) {
                continue;
            }
            Object value = row.get(workItem.getColumnName());
            if (value == null) {
                continue;
            }
            pendingIndexes.add(rowIndex);
            pendingValues.add(String.valueOf(value));
            if (pendingValues.size() >= workItem.getBatchSize()) {
                requests.add(new ProtectBatchRequest(
                        workItem,
                        new ArrayList<>(pendingIndexes),
                        new ArrayList<>(pendingValues)));
                pendingIndexes.clear();
                pendingValues.clear();
            }
        }

        if (!pendingValues.isEmpty()) {
            requests.add(new ProtectBatchRequest(
                    workItem,
                    new ArrayList<>(pendingIndexes),
                    new ArrayList<>(pendingValues)));
        }
        return requests;
    }

    private List<ProtectMultiBatchRequest> buildMultiColumnBatches(
            List<ProtectWorkItem> workItems,
            List<Map<String, Object>> rows,
            int sparkGroupSize,
            int maxItemsPerRequest,
            int maxPolicyGroupsPerRequest) {
        List<ProtectMultiBatchRequest> requests = new ArrayList<>();
        int effectiveGroupSize = Math.max(sparkGroupSize, 1);
        int effectiveMaxItems = Math.max(maxItemsPerRequest, 1);
        int effectiveMaxPolicyGroups = Math.max(maxPolicyGroupsPerRequest, 1);

        for (int start = 0; start < rows.size(); start += effectiveGroupSize) {
            int end = Math.min(start + effectiveGroupSize, rows.size());
            List<List<ProtectBatchRequest>> columnBatches = new ArrayList<>();

            for (ProtectWorkItem workItem : workItems) {
                List<Integer> rowIndexes = new ArrayList<>();
                List<String> values = new ArrayList<>();
                List<ProtectBatchRequest> requestsForColumn = new ArrayList<>();
                for (int rowIndex = start; rowIndex < end; rowIndex++) {
                    Map<String, Object> row = rows.get(rowIndex);
                    if (!row.containsKey(workItem.getColumnName())) {
                        continue;
                    }
                    Object value = row.get(workItem.getColumnName());
                    if (value == null) {
                        continue;
                    }
                    rowIndexes.add(rowIndex);
                    values.add(String.valueOf(value));
                    if (values.size() >= effectiveMaxItems) {
                        requestsForColumn.add(new ProtectBatchRequest(
                                workItem,
                                new ArrayList<>(rowIndexes),
                                new ArrayList<>(values)));
                        rowIndexes.clear();
                        values.clear();
                    }
                }
                if (!values.isEmpty()) {
                    requestsForColumn.add(new ProtectBatchRequest(
                            workItem,
                            new ArrayList<>(rowIndexes),
                            new ArrayList<>(values)));
                }
                if (!requestsForColumn.isEmpty()) {
                    columnBatches.add(requestsForColumn);
                }
            }

            List<List<ProtectBatchRequest>> activeBatches = new ArrayList<>(columnBatches);
            while (!activeBatches.isEmpty()) {
                List<ProtectBatchRequest> groupedRequests = new ArrayList<>();
                List<List<ProtectBatchRequest>> remainingBatches = new ArrayList<>();
                for (List<ProtectBatchRequest> batches : activeBatches) {
                    if (groupedRequests.size() < effectiveMaxPolicyGroups) {
                        groupedRequests.add(batches.remove(0));
                    }
                    if (!batches.isEmpty()) {
                        remainingBatches.add(batches);
                    }
                }
                if (!groupedRequests.isEmpty()) {
                    requests.add(new ProtectMultiBatchRequest(groupedRequests));
                }
                activeBatches = remainingBatches;
            }
        }

        return requests;
    }
}
