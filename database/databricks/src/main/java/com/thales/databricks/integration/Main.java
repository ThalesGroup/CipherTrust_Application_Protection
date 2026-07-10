package com.thales.databricks.integration;

import java.util.List;
import java.util.Map;
import java.nio.file.Path;

import com.google.gson.Gson;
import com.thales.databricks.integration.config.IntegrationConfig;
import com.thales.databricks.integration.engine.BulkPlan;
import com.thales.databricks.integration.engine.BulkExecutionResult;
import com.thales.databricks.integration.engine.BulkPlanner;
import com.thales.databricks.integration.engine.V2BulkEngineStub;

public final class Main {

    private static final Gson GSON = new Gson();

    private Main() {
    }

    public static void main(String[] args) throws Exception {
        IntegrationConfig config = IntegrationConfig.fromProperties(
                Path.of("src", "main", "resources", "udfConfig.properties"));
        BulkPlan plan = new BulkPlanner(config).planProtect(
                "my_catalog.my_schema.plaintext_protected_internal",
                List.of("email", "ssn"));
        BulkExecutionResult result = new V2BulkEngineStub().protectRows(
                plan,
                List.of(
                        Map.of("customer_id", 1, "email", "alice@example.com", "ssn", "111223333"),
                        Map.of("customer_id", 2, "email", "bob@example.com", "ssn", "222334444")));
        System.out.println(GSON.toJson(result));
    }
}
