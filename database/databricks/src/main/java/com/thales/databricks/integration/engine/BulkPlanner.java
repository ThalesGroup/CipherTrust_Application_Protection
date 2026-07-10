package com.thales.databricks.integration.engine;

import java.util.ArrayList;
import java.util.List;

import com.thales.databricks.integration.config.IntegrationConfig;

public final class BulkPlanner {

    private final IntegrationConfig config;

    public BulkPlanner(IntegrationConfig config) {
        this.config = config;
    }

    public BulkPlan planProtect(String objectName, List<String> columnNames) {
        List<ColumnPlan> plans = new ArrayList<>();
        List<ProtectWorkItem> workItems = new ArrayList<>();
        for (String columnName : columnNames) {
            String datatype = config.resolveDatatype(objectName, columnName);
            String profileName = config.resolveProfile(objectName, columnName);
            plans.add(new ColumnPlan(
                    objectName,
                    columnName,
                    datatype,
                    profileName));
            workItems.add(new ProtectWorkItem(
                    objectName,
                    columnName,
                    datatype,
                    profileName,
                    config.getDefaultBatchSize()));
        }
        return new BulkPlan(
                objectName,
                plans,
                workItems,
                config.getCrdpApiVersion(),
                config.getDefaultBatchSize(),
                config.getSparkGroupSize(),
                config.getCrdpV2MaxItemsPerRequest(),
                config.getCrdpV2MaxPolicyGroupsPerRequest(),
                config.isCrdpV2EnableMultiPolicy());
    }
}
