# Thales Databricks Integration

This project provides a Databricks-focused integration layer for protecting and
revealing sensitive data through three execution paths:

- `Python helper wheel`
  for DataFrame-first compute-cluster pipelines
- `Java jar / UDF`
  for Spark SQL-shaped compute-cluster ETL
- `Unity Catalog Python UDF`
  for governed SQL Warehouse functions and views

## Project Focus

Use this project when you want:

- compute-cluster protection and reveal APIs that are easier to use than
  low-level UDF-by-UDF orchestration
- Java UDFs for SQL-shaped ETL and CTAS workflows
- Unity Catalog Python functions and governed reveal views for SQL Warehouse
- object-aware protection profile resolution from `udfConfig.properties`
- CRDP v2-oriented bulk execution and tuning controls

## Quick Decision Guide

The simplest recommendation is:

- choose the `Python helper wheel` for performance-first compute-cluster
  pipelines
- choose the `Java jar / UDF` path for Spark SQL-first compute-cluster jobs
- choose the `Unity Catalog Python UDF` path for governed SQL Warehouse and
  BI-facing access

Start with:

- [CUSTOMER_EXECUTION_PATH_DECISION_MATRIX.md](/E:/codex/work/thales.databricks.integration/docs/CUSTOMER_EXECUTION_PATH_DECISION_MATRIX.md:1)

## Main Artifacts

- Python wheel source:
  [src/thales_databricks_integration](/E:/codex/work/thales.databricks.integration/src/thales_databricks_integration)
- Java runtime source:
  [src/main/java/com/thales/databricks/integration](/E:/codex/work/thales.databricks.integration/src/main/java/com/thales/databricks/integration)
- Python packaging:
  [pyproject.toml](/E:/codex/work/thales.databricks.integration/pyproject.toml:1)
- Java packaging:
  [pom.xml](/E:/codex/work/thales.databricks.integration/pom.xml:1)
- Example notebooks:
  [notebooks](/E:/codex/work/thales.databricks.integration/notebooks)
- SQL Warehouse artifacts:
  [sql_warehouse/SQL_WAREHOUSE_INDEX.md](/E:/codex/work/thales.databricks.integration/sql_warehouse/SQL_WAREHOUSE_INDEX.md:1)

## Documentation

For the curated documentation set, start with:

- [docs/INDEX.md](/E:/codex/work/thales.databricks.integration/docs/INDEX.md:1)

Key references:

- [DEPLOYMENT.md](/E:/codex/work/thales.databricks.integration/docs/DEPLOYMENT.md:1)
- [JAVA_UDF_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/JAVA_UDF_API_GUIDE.md:1)
- [PYTHON_DIRECT_API_GUIDE.md](/E:/codex/work/thales.databricks.integration/docs/PYTHON_DIRECT_API_GUIDE.md:1)
- [PROTECTION_PROFILE_OPTIONS.md](/E:/codex/work/thales.databricks.integration/docs/PROTECTION_PROFILE_OPTIONS.md:1)
- [PROFILE_RESOLUTION_ORDER.md](/E:/codex/work/thales.databricks.integration/docs/PROFILE_RESOLUTION_ORDER.md:1)
- [PUBLIC_EXECUTION_MODEL_MATRIX.md](/E:/codex/work/thales.databricks.integration/docs/PUBLIC_EXECUTION_MODEL_MATRIX.md:1)

## Build

Build the Java jar:

```powershell
mvn -DskipTests package
```

Build the Python wheel:

```powershell
python -m build
```

For actual deployment steps, configuration, and smoke-test order, use:

- [DEPLOYMENT.md](/E:/codex/work/thales.databricks.integration/docs/DEPLOYMENT.md:1)
