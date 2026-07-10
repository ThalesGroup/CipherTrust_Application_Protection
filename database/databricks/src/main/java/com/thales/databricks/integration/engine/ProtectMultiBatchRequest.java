package com.thales.databricks.integration.engine;

import java.util.Collections;
import java.util.List;

public final class ProtectMultiBatchRequest {

    private final List<ProtectBatchRequest> requests;

    public ProtectMultiBatchRequest(List<ProtectBatchRequest> requests) {
        this.requests = requests == null ? List.of() : Collections.unmodifiableList(requests);
    }

    public List<ProtectBatchRequest> getRequests() {
        return requests;
    }
}
