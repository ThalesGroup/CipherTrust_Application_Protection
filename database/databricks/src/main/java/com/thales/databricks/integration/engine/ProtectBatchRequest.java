package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;

public final class ProtectBatchRequest {

    private final ProtectWorkItem workItem;
    private final List<Integer> rowIndexes;
    private final List<String> values;

    public ProtectBatchRequest(ProtectWorkItem workItem, List<Integer> rowIndexes, List<String> values) {
        this.workItem = workItem;
        this.rowIndexes = rowIndexes == null ? List.of() : Collections.unmodifiableList(rowIndexes);
        this.values = values == null ? List.of() : Collections.unmodifiableList(values);
    }

    public ProtectWorkItem getWorkItem() {
        return workItem;
    }

    public List<Integer> getRowIndexes() {
        return rowIndexes;
    }

    public List<String> getValues() {
        return values;
    }
}
