# Notebook Docs Index

This folder contains notebook-specific tuning, benchmarking, execution-model,
and operational guidance for the Databricks compute-cluster path.

The best master frame for the bulk benchmark content is:

1. Spark work shape
2. Databricks grouping shape
3. CRDP chunking

## Master references

- [PERFORMANCE_CONSIDERATIONS.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PERFORMANCE_CONSIDERATIONS.md)
- [BULK_UDF_TUNING_CHEAT_SHEET.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\BULK_UDF_TUNING_CHEAT_SHEET.md)

Use these first when you want the broadest explanation of how the internal
bulk benchmark behaves.

## Spark work shape

These docs are most relevant when the main question is:

- how much Spark work exists?
- how is it partitioned?
- are tasks and writes shaped well?

References:

- [PARTITIONING_GUIDANCE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PARTITIONING_GUIDANCE.md)
- [DELTA_PARTITIONING_GUIDANCE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\DELTA_PARTITIONING_GUIDANCE.md)

## Databricks grouping shape

These docs are most relevant when the main question is:

- how many grouped UDF rows does Spark create?
- how many values go into each grouped bulk-UDF call?
- how much independent CRDP work can be in flight?

References:

- [BULK_UDF_TUNING_CHEAT_SHEET.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\BULK_UDF_TUNING_CHEAT_SHEET.md)
- [PROMETHEUS_CRDP_METRICS_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PROMETHEUS_CRDP_METRICS_GUIDE.md)

## CRDP chunking

These docs are most relevant when the main question is:

- how does `BATCH_SIZE` affect outbound CRDP requests?
- when does CRDP split grouped calls into multiple `/v1/protectbulk` requests?
- how does grouped-call size interact with request-size ceilings?

References:

- [BULK_UDF_TUNING_CHEAT_SHEET.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\BULK_UDF_TUNING_CHEAT_SHEET.md)
- [PERFORMANCE_CONSIDERATIONS.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PERFORMANCE_CONSIDERATIONS.md)
- [PROMETHEUS_CRDP_METRICS_GUIDE.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PROMETHEUS_CRDP_METRICS_GUIDE.md)

## Execution model and diagrams

These references help explain how the compute-cluster Java UDF path works,
even when they are not purely performance docs.

Assets:

- [execution-model-matrix.png](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\execution-model-matrix.png)
- [execution-model-matrix.svg](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\execution-model-matrix.svg)
- [java-udf-executor-flow.png](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\java-udf-executor-flow.png)
- [java-udf-executor-flow.svg](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\java-udf-executor-flow.svg)
- [bulk-cheat-sheet.png](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\bulk-cheat-sheet.png)
- [data-bricks-and-thales-performance-testing-examples.png](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\data-bricks-and-thales-performance-testing-examples.png)

## Operational commands

This content is notebook-related, but it is more operational than performance-focused.

References:

- [PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md](E:\eclipse-workspace\thales.databricks.udf\notebooks\docs\PLAINTEXT_PROTECTED_INTERNAL_COMMANDS.md)
