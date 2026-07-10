package com.thales.databricks.integration.engine;

public interface ProtectTransport {

    ProtectTransportResult protectBatch(ProtectBatchRequest request, String apiVersion) throws Exception;

    ProtectTransportResult protectGroupedBatch(ProtectMultiBatchRequest request, String apiVersion) throws Exception;
}
