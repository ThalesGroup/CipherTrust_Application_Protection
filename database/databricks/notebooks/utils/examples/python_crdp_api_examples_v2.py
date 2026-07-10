# Databricks notebook source
# MAGIC %md
# MAGIC # Thales Databricks Integration Python API Examples v2
# MAGIC
# MAGIC This notebook shows direct Python usage of the new helper-first wheel.
# MAGIC
# MAGIC It is the new-repo counterpart to:
# MAGIC `thales.databricks.udf/notebooks/utils/examples/python_crdp_api_examples.py`
# MAGIC
# MAGIC It demonstrates:
# MAGIC
# MAGIC - runtime config discovery from the deployed compute-cluster path
# MAGIC - direct protect/reveal calls without DataFrame orchestration
# MAGIC - scalar-style usage through single-item row lists
# MAGIC - explicit reveal-user override when needed for admin/testing

# COMMAND ----------

from thales_databricks_integration import IntegrationConfig, protect_rows, reveal_rows

# COMMAND ----------

# Runtime config discovery order:
# 1. explicit config_path passed to IntegrationConfig.from_runtime(...)
# 2. UDF_CONFIG_VOLUME_PATH environment variable
# 3. THALES_UDF_CONFIG_PATH environment variable
# 4. /tmp/thales_config/udfConfig.properties
#
# That last fallback matches the current cluster init script copy target.
config_path = spark.conf.get("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
print("Driver config path:", config_path)

if not config_path:
    raise ValueError(
        "spark.driverEnv.UDF_CONFIG_VOLUME_PATH is not set. "
        "Configure the driver and executor env vars before running this notebook."
    )

config = IntegrationConfig.from_properties(config_path)

print("Resolved config summary:")
print(
    {
        "api_version": config.crdp_api_version,
        "transport_mode": config.transport_mode,
        "crdp_endpoint_configured": config.has_crdp_endpoint(),
        "spark_group_size": config.spark_group_size,
        "v2_max_items_per_request": config.crdp_v2_max_items_per_request,
        "v2_max_policy_groups_per_request": config.crdp_v2_max_policy_groups_per_request,
        "v2_enable_multi_policy": config.crdp_v2_enable_multi_policy,
    }
)

# COMMAND ----------

plaintext_rows = [
    {"email": "alice@example.com"},
    {"email": "bob@example.com"},
]

protected_email_rows = protect_rows(
    rows=plaintext_rows,
    object_name="my_catalog.my_schema.plaintext_protected_internal",
    sensitive_columns=["email"],
    config=config,
)

print("Direct protect results:")
print(protected_email_rows.rows)
print("Protect request summary:")
print(protected_email_rows.requests)

# COMMAND ----------

protected_email_values = protected_email_rows.rows

revealed_email_rows = reveal_rows(
    rows=protected_email_values,
    object_name="my_catalog.my_schema.plaintext_protected_internal",
    sensitive_columns=["email"],
    config=config,
)

print("Direct reveal results:")
print(revealed_email_rows.rows)
print("Reveal request summary:")
print(revealed_email_rows.requests)

# COMMAND ----------

# Scalar-style direct usage uses a single-item row list.
single_plaintext_row = [{"email": "carol@example.com"}]
single_protected_email = protect_rows(
    rows=single_plaintext_row,
    object_name="my_catalog.my_schema.plaintext_protected_internal",
    sensitive_columns=["email"],
    config=config,
).rows[0]["email"]

print("Single-value protect result:")
print(single_protected_email)

# COMMAND ----------

# Explicit reveal-user override remains available for controlled admin/testing
# cases, even though the helper/DataFrame path now resolves runtime identity
# automatically for Spark-side reveal execution.
admin_override_reveal = reveal_rows(
    rows=[{"email": single_protected_email}],
    object_name="my_catalog.my_schema.plaintext_protected_internal",
    sensitive_columns=["email"],
    config=config,
    reveal_user="admin",
)

print("Admin override reveal result:")
print(admin_override_reveal.rows)

# COMMAND ----------

print(
    "Python API example v2 complete. "
    "This notebook validates direct wheel usage and automatic config discovery "
    "from the compute-cluster runtime path."
)
