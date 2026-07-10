package com.thales.databricks.integration.service;

public final class ProtectResult {

    private final String protectedValue;
    private final String externalHeader;

    public ProtectResult(String protectedValue, String externalHeader) {
        this.protectedValue = protectedValue;
        this.externalHeader = externalHeader;
    }

    public String getProtectedValue() {
        return protectedValue;
    }

    public String getExternalHeader() {
        return externalHeader;
    }
}
