package com.thales.databricks.integration.engine;

import java.util.Map;

public interface CrdpBulkEngine {

    BulkExecutionResult protectRows(BulkPlan plan, Iterable<Map<String, Object>> rows) throws Exception;
}
