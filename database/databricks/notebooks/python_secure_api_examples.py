# Databricks notebook source
# MAGIC %md
# MAGIC # Thales CRDP Python Secure API Examples
# MAGIC
# MAGIC This notebook shows:
# MAGIC
# MAGIC - production-safe direct Python usage
# MAGIC - flexible testing/admin usage
# MAGIC - an invalid positional override example that now fails

# COMMAND ----------

from thales_databricks_udf.crdp_udfs import *
from thales_databricks_udf.crdp_udfs import (
    thales_crdp_python_function_bulk,
    thales_crdp_python_function_bulk_secure,
)

# COMMAND ----------

token_values = [
    "A9K2exampletoken",
    "B1M4exampletoken",
]

# COMMAND ----------

plaintext_values = [
    "alice@example.com",
    "bob@example.com",
]

# COMMAND ----------

# Production-safe bulk protect usage
secure_protect_results = thales_crdp_python_function_bulk_secure(
    plaintext_values,
    "protectbulk",
    "char",
    "email",
    spark_session=spark,
)

print("Secure bulk protect results:", secure_protect_results)

# COMMAND ----------

# Production-safe non-bulk protect example using a single-item list.
# The helper is bulk-oriented, so scalar-style direct Python usage is typically
# done by passing one value in a list and reading back the first result.
single_plaintext_value = ["carol@example.com"]
secure_protect_single_result = thales_crdp_python_function_bulk_secure(
    single_plaintext_value,
    "protectbulk",
    "char",
    "email",
    spark_session=spark,
)[0]

print("Secure single-value protect result:", secure_protect_single_result)

# COMMAND ----------

# Production-safe usage:
# - no reveal_user parameter
# - identity resolves from spark_session, active session, notebook context,
#   or config fallback
secure_reveal_results = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
    spark_session=spark,
)

print("Secure reveal results:", secure_reveal_results)

# COMMAND ----------

# Secure usage without explicitly passing spark_session.
# The code will try SparkSession.getActiveSession() automatically.
secure_reveal_results_auto_session = thales_crdp_python_function_bulk_secure(
    token_values,
    "revealbulk",
    "char",
    "email",
)

print("Secure reveal results with auto session lookup:", secure_reveal_results_auto_session)

# COMMAND ----------

# Flexible testing/admin usage:
# - explicit reveal_user override is allowed here
testing_results = thales_crdp_python_function_bulk(
    token_values,
    "revealbulk",
    "char",
    "email",
    reveal_user="admin",
    spark_session=spark,
)

print("Testing/admin results:", testing_results)

# COMMAND ----------

# Invalid positional override example:
# This now fails because the secure API requires non-business arguments to be
# passed by keyword only.
try:
    invalid_results = thales_crdp_python_function_bulk_secure(
        token_values,
        "revealbulk",
        "char",
        "email",
        "fred",
    )
    print("Unexpected success:", invalid_results)
except TypeError as ex:
    print("Expected failure for invalid positional override:", ex)

# COMMAND ----------

print(
    "Python secure API example notebook completed. "
    "Use the secure entry point for production-safe direct Python access."
)
