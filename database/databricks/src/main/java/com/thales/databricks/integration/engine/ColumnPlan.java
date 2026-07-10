package com.thales.databricks.integration.engine;

public final class ColumnPlan {

    private final String objectName;
    private final String columnName;
    private final String datatype;
    private final String profileName;

    public ColumnPlan(String objectName, String columnName, String datatype, String profileName) {
        this.objectName = objectName;
        this.columnName = columnName;
        this.datatype = datatype;
        this.profileName = profileName;
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
}
