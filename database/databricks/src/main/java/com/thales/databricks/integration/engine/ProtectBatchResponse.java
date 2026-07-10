package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;

public final class ProtectBatchResponse {

    private final List<String> protectedValues;

    public ProtectBatchResponse(List<String> protectedValues) {
        this.protectedValues = protectedValues == null ? List.of() : Collections.unmodifiableList(protectedValues);
    }

    public List<String> getProtectedValues() {
        return protectedValues;
    }
}
