# Databricks notebook source
# MAGIC %md
# MAGIC # Java Runtime Context Probe
# MAGIC
# MAGIC Purpose:
# MAGIC - register a tiny standalone Java UDF that reports the runtime context visible inside the Java UDF process
# MAGIC - compare that output with Databricks SQL identity functions such as `current_user()` and `session_user()`
# MAGIC - help determine whether a Java UDF can resolve a trusted end-user identity on its own
# MAGIC
# MAGIC Before running:
# MAGIC - build and attach `target/thales-databricks-integration-0.1.0-SNAPSHOT.jar` or the equivalent current jar
# MAGIC - restart the cluster or reattach the updated jar if needed

# COMMAND ----------

import json

from pyspark.sql import types as T

# COMMAND ----------

PROBE_FUNCTION_NAME = "debug_runtime_context_probe"
PROBE_CLASS_NAME = "com.thales.databricks.integration.udf.DatabricksRuntimeContextProbeUdf"

print("Probe function name:", PROBE_FUNCTION_NAME)
print("Probe class name:", PROBE_CLASS_NAME)

# COMMAND ----------

try:
    spark.udf.registerJavaFunction(
        PROBE_FUNCTION_NAME,
        PROBE_CLASS_NAME,
        T.StringType(),
    )
    print(f"Registered Java UDF: {PROBE_FUNCTION_NAME} -> {PROBE_CLASS_NAME}")
except Exception as exc:
    raise RuntimeError(
        "Failed to register the Java probe UDF. Rebuild the integration jar, attach it to the cluster, "
        "and make sure the cluster is using the updated artifact."
    ) from exc

# COMMAND ----------

identity_df = spark.sql(
    """
    SELECT
      current_user() AS current_user_value,
      session_user() AS session_user_value
    """
)

display(identity_df)

# COMMAND ----------

probe_df = spark.range(1).selectExpr(
    "cast(id as string) as probe_input",
    f"{PROBE_FUNCTION_NAME}(cast(id as string)) as runtime_context_json",
)

display(probe_df)

# COMMAND ----------

probe_json = probe_df.collect()[0]["runtime_context_json"]
print("Raw Java probe JSON:")
print(probe_json)

print("\nPretty printed Java probe JSON:")
print(json.dumps(json.loads(probe_json), indent=2, sort_keys=False))

# COMMAND ----------

comparison_row = spark.sql(
    f"""
    SELECT
      current_user() AS current_user_value,
      session_user() AS session_user_value,
      {PROBE_FUNCTION_NAME}('direct-sql-call') AS runtime_context_json
    """
).collect()[0]

print("Databricks SQL current_user():", comparison_row["current_user_value"])
print("Databricks SQL session_user():", comparison_row["session_user_value"])
print("Java UDF runtime context from direct SQL call:")
print(json.dumps(json.loads(comparison_row["runtime_context_json"]), indent=2, sort_keys=False))

# COMMAND ----------

print("How to use this probe:")
print("1. Run this notebook as user A and save the Java probe JSON output.")
print("2. Run the same notebook as user B or a service principal.")
print("3. Compare whether any Java-visible field changes with the actual Databricks caller identity.")
print("4. If the Java-visible values stay fixed or only show cluster/runtime identity, the Java UDF cannot safely self-resolve the caller.")
