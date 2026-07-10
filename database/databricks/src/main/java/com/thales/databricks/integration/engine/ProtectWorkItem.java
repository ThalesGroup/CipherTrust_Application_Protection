package com.thales.databricks.integration.engine;

public final class ProtectWorkItem {

    private final String objectName;
    private final String columnName;
    private final String datatype;
    private final String profileName;
    private final int batchSize;

    public ProtectWorkItem(
            String objectName,
            String columnName,
            String datatype,
            String profileName,
            int batchSize) {
        this.objectName = objectName;
        this.columnName = columnName;
        this.datatype = datatype;
        this.profileName = profileName;
        this.batchSize = batchSize;
    }

    public String getObjectName() {
        return objectName;
    }

    public String getColumnName() {
        return columnName;
    }

    public String getDatatype() {
        return datatype;
    }

    public String getProfileName() {
        return profileName;
    }

    public int getBatchSize() {
        return batchSize;
    }
}
