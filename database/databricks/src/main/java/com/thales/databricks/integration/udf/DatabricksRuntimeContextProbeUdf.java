package com.thales.databricks.integration.udf;

import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.spark.SparkEnv;
import org.apache.spark.TaskContext;
import org.apache.spark.sql.api.java.UDF1;

public class DatabricksRuntimeContextProbeUdf implements UDF1<String, String> {

    @Override
    public String call(String input) {
        Map<String, String> values = new LinkedHashMap<>();
        values.put("input", safe(input));
        values.put("system.user.name", safeSystemProperty("user.name"));
        values.put("env.USERNAME", safeEnv("USERNAME"));
        values.put("env.USER", safeEnv("USER"));

        TaskContext taskContext = TaskContext.get();
        values.put("taskContext.present", String.valueOf(taskContext != null));
        if (taskContext != null) {
            values.put("taskContext.stageId", String.valueOf(taskContext.stageId()));
            values.put("taskContext.partitionId", String.valueOf(taskContext.partitionId()));
            values.put("taskContext.attemptNumber", String.valueOf(taskContext.attemptNumber()));
            values.put("taskContext.local.spark.jobGroup.id", safe(taskContext.getLocalProperty("spark.jobGroup.id")));
            values.put("taskContext.local.spark.job.description", safe(taskContext.getLocalProperty("spark.job.description")));
            values.put("taskContext.local.spark.databricks.notebook.path",
                    safe(taskContext.getLocalProperty("spark.databricks.notebook.path")));
            values.put("taskContext.local.spark.databricks.token",
                    safe(taskContext.getLocalProperty("spark.databricks.token")));
            values.put("taskContext.local.user", safe(taskContext.getLocalProperty("user")));
            values.put("taskContext.local.sessionUser", safe(taskContext.getLocalProperty("sessionUser")));
        }

        try {
            SparkEnv env = SparkEnv.get();
            values.put("sparkEnv.present", String.valueOf(env != null));
            if (env != null) {
                values.put("spark.conf.spark.databricks.clusterUsageTags.clusterOwnerId",
                        safe(env.conf().get("spark.databricks.clusterUsageTags.clusterOwnerId", null)));
                values.put("spark.conf.spark.databricks.clusterUsageTags.clusterName",
                        safe(env.conf().get("spark.databricks.clusterUsageTags.clusterName", null)));
                values.put("spark.conf.spark.databricks.workspaceUrl",
                        safe(env.conf().get("spark.databricks.workspaceUrl", null)));
                values.put("spark.conf.spark.databricks.notebook.path",
                        safe(env.conf().get("spark.databricks.notebook.path", null)));
                values.put("spark.conf.spark.databricks.replId",
                        safe(env.conf().get("spark.databricks.replId", null)));
                values.put("spark.conf.spark.databricks.userInfo",
                        safe(env.conf().get("spark.databricks.userInfo", null)));
                values.put("spark.conf.spark.databricks.clusterUsageTags.sparkVersion",
                        safe(env.conf().get("spark.databricks.clusterUsageTags.sparkVersion", null)));
                values.put("spark.conf.spark.databricks.clusterUsageTags.clusterAllTags",
                        safe(env.conf().get("spark.databricks.clusterUsageTags.clusterAllTags", null)));
            }
        } catch (Exception e) {
            values.put("sparkEnv.error", e.toString());
        }

        return toJson(values);
    }

    private static String safe(String value) {
        return value == null ? "<null>" : value;
    }

    private static String safeSystemProperty(String name) {
        try {
            return safe(System.getProperty(name));
        } catch (Exception e) {
            return "<error:" + e.getClass().getSimpleName() + ">";
        }
    }

    private static String safeEnv(String name) {
        try {
            return safe(System.getenv(name));
        } catch (Exception e) {
            return "<error:" + e.getClass().getSimpleName() + ">";
        }
    }

    private static String toJson(Map<String, String> values) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            first = false;
            sb.append("\"").append(escape(entry.getKey())).append("\": ");
            sb.append("\"").append(escape(entry.getValue())).append("\"");
        }
        sb.append("}");
        return sb.toString();
    }

    private static String escape(String value) {
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "\\r")
                .replace("\n", "\\n");
    }
}
