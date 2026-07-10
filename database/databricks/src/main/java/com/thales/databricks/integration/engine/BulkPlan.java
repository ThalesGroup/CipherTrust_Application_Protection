package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;

public final class BulkPlan {

    private final String objectName;
    private final List<ColumnPlan> columns;
    private final List<ProtectWorkItem> workItems;
    private final String apiVersion;
    private final int batchSize;
    private final int sparkGroupSize;
    private final int v2MaxItemsPerRequest;
    private final int v2MaxPolicyGroupsPerRequest;
    private final boolean v2EnableMultiPolicy;

    public BulkPlan(
            String objectName,
            List<ColumnPlan> columns,
            List<ProtectWorkItem> workItems,
            String apiVersion,
            int batchSize,
            int sparkGroupSize,
            int v2MaxItemsPerRequest,
            int v2MaxPolicyGroupsPerRequest,
            boolean v2EnableMultiPolicy) {
        this.objectName = objectName;
        this.columns = columns == null ? List.of() : Collections.unmodifiableList(columns);
        this.workItems = workItems == null ? List.of() : Collections.unmodifiableList(workItems);
        this.apiVersion = apiVersion;
        this.batchSize = batchSize;
        this.sparkGroupSize = sparkGroupSize;
        this.v2MaxItemsPerRequest = v2MaxItemsPerRequest;
        this.v2MaxPolicyGroupsPerRequest = v2MaxPolicyGroupsPerRequest;
        this.v2EnableMultiPolicy = v2EnableMultiPolicy;
    }

    public String getObjectName() {
        return objectName;
    }

    public List<ColumnPlan> getColumns() {
        return columns;
    }

    public List<ProtectWorkItem> getWorkItems() {
        return workItems;
    }

    public String getApiVersion() {
        return apiVersion;
    }

    public int getBatchSize() {
        return batchSize;
    }

    public int getSparkGroupSize() {
        return sparkGroupSize;
    }

    public int getV2MaxItemsPerRequest() {
        return v2MaxItemsPerRequest;
    }

    public int getV2MaxPolicyGroupsPerRequest() {
        return v2MaxPolicyGroupsPerRequest;
    }

    public boolean isV2EnableMultiPolicy() {
        return v2EnableMultiPolicy;
    }
}
