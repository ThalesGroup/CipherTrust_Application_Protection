package com.thales.databricks.integration.config;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

public final class ObjectPolicyConfig {

    private final String objectName;
    private final Map<String, String> columnProfiles;
    private final Map<String, String> columnTypes;

    public ObjectPolicyConfig(
            String objectName,
            Map<String, String> columnProfiles,
            Map<String, String> columnTypes) {
        this.objectName = objectName;
        this.columnProfiles = columnProfiles == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(columnProfiles));
        this.columnTypes = columnTypes == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(columnTypes));
    }

    public String getObjectName() {
        return objectName;
    }

    public Map<String, String> getColumnProfiles() {
        return columnProfiles;
    }

    public Map<String, String> getColumnTypes() {
        return columnTypes;
    }
}
