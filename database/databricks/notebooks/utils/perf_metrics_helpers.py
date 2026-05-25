# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Cluster Performance Metrics Helpers
# MAGIC
# MAGIC Helper functions for recording notebook-level performance runs to a Delta
# MAGIC table and, optionally, to CSV. These helpers are intentionally lightweight
# MAGIC so they can be reused by the load-test and benchmark notebooks.

# COMMAND ----------

import json
from datetime import datetime, timezone

from pyspark.sql import functions as F
from pyspark.sql import Row
from pyspark.sql import types as T

# COMMAND ----------

METRICS_CATALOG = globals().get("CATALOG", "my_catalog")
METRICS_SCHEMA = globals().get("SCHEMA", "my_schema")
METRICS_TABLE = globals().get(
    "METRICS_TABLE",
    f"{METRICS_CATALOG}.{METRICS_SCHEMA}.thales_perf_test_metrics",
)
METRICS_CSV_PATH = globals().get("METRICS_CSV_PATH", None)
COMPACT_SUMMARY_VIEW = globals().get(
    "COMPACT_SUMMARY_VIEW",
    f"{METRICS_CATALOG}.{METRICS_SCHEMA}.v_thales_perf_test_compact",
)


def _safe_conf(name, default=None):
    try:
        return spark.conf.get(name, default)
    except Exception:
        return default


def collect_cluster_context():
    try:
        # Executor memory status includes the driver, so subtract one when possible.
        executor_status = spark.sparkContext._jsc.sc().getExecutorMemoryStatus()
        executor_count = max(int(executor_status.size()) - 1, 0)
    except Exception:
        executor_count = None

    return {
        "cluster_id": _safe_conf("spark.databricks.clusterUsageTags.clusterId"),
        "cluster_name": _safe_conf("spark.databricks.clusterUsageTags.clusterName"),
        "node_type": _safe_conf("spark.databricks.clusterUsageTags.clusterNodeType"),
        "driver_node_type": _safe_conf("spark.databricks.clusterUsageTags.driverNodeType"),
        "worker_count": _safe_conf("spark.databricks.clusterUsageTags.clusterWorkers"),
        "spark_version": _safe_conf("spark.databricks.clusterUsageTags.sparkVersion"),
        "default_parallelism": spark.sparkContext.defaultParallelism,
        "executor_count_estimate": executor_count,
    }


def load_config_batch_size_from_properties(config_path=None):
    config_path = config_path or _safe_conf("spark.driverEnv.UDF_CONFIG_VOLUME_PATH", None)
    if not config_path:
        return None

    try:
        from pathlib import Path

        path = Path(config_path)
        if not path.exists():
            return None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "BATCH_SIZE":
                batch_size = int(value.strip())
                return batch_size if batch_size > 0 else None
    except Exception as exc:
        print(f"Could not read BATCH_SIZE from udfConfig.properties. Reason: {exc}")

    return None


def get_node_timeline_summary(cluster_id, start_ts, end_ts):
    if not cluster_id:
        return {
            "avg_cpu_user_pct": None,
            "avg_cpu_system_pct": None,
            "avg_cpu_wait_pct": None,
            "avg_mem_used_pct": None,
            "avg_mem_swap_pct": None,
        }

    try:
        query = f"""
        SELECT
          AVG(cpu_user_percent) AS avg_cpu_user_pct,
          AVG(cpu_system_percent) AS avg_cpu_system_pct,
          AVG(cpu_wait_percent) AS avg_cpu_wait_pct,
          AVG(mem_used_percent) AS avg_mem_used_pct,
          AVG(mem_swap_percent) AS avg_mem_swap_pct
        FROM system.compute.node_timeline
        WHERE cluster_id = '{cluster_id}'
          AND start_time >= TIMESTAMP '{start_ts.strftime("%Y-%m-%d %H:%M:%S")}'
          AND end_time <= TIMESTAMP '{end_ts.strftime("%Y-%m-%d %H:%M:%S")}'
        """
        row = spark.sql(query).first()
        if row is None:
            raise ValueError("No node_timeline rows returned.")
        return {
            "avg_cpu_user_pct": row["avg_cpu_user_pct"],
            "avg_cpu_system_pct": row["avg_cpu_system_pct"],
            "avg_cpu_wait_pct": row["avg_cpu_wait_pct"],
            "avg_mem_used_pct": row["avg_mem_used_pct"],
            "avg_mem_swap_pct": row["avg_mem_swap_pct"],
        }
    except Exception as exc:
        print("Could not query system.compute.node_timeline for hardware summaries.")
        print(f"Reason: {exc}")
        return {
            "avg_cpu_user_pct": None,
            "avg_cpu_system_pct": None,
            "avg_cpu_wait_pct": None,
            "avg_mem_used_pct": None,
            "avg_mem_swap_pct": None,
        }


def append_perf_metrics(run_name, step_name, row_count, duration_seconds, extra_metrics=None):
    extra_metrics = extra_metrics or {}
    cluster_context = collect_cluster_context()
    metric_time = datetime.now(timezone.utc)

    node_summary = get_node_timeline_summary(
        cluster_context["cluster_id"],
        extra_metrics.get("step_start_ts", metric_time),
        extra_metrics.get("step_end_ts", metric_time),
    )

    payload = {
        "metric_ts_utc": metric_time.isoformat(),
        "run_name": run_name,
        "step_name": step_name,
        "row_count": int(row_count) if row_count is not None else None,
        "duration_seconds": float(duration_seconds) if duration_seconds is not None else None,
        "rows_per_second": (
            float(row_count) / float(duration_seconds)
            if row_count is not None and duration_seconds not in (None, 0)
            else None
        ),
        "target_partitions": extra_metrics.get("target_partitions"),
        "generate_partitions": extra_metrics.get("generate_partitions"),
        "raw_file_partitions": extra_metrics.get("raw_file_partitions"),
        "load_pattern": extra_metrics.get("load_pattern"),
        "config_batch_size": extra_metrics.get("config_batch_size"),
        "group_size": extra_metrics.get("group_size"),
        "group_size_multiplier": extra_metrics.get("group_size_multiplier"),
        "benchmark_mode": extra_metrics.get("benchmark_mode"),
        "source_table": extra_metrics.get("source_table"),
        "target_table": extra_metrics.get("target_table"),
        "cluster_vm_hint": extra_metrics.get("cluster_vm_hint", "Standard_D4ds_v5"),
        **cluster_context,
        **node_summary,
        "hardware_metrics_available": any(
            value is not None
            for value in (
                node_summary.get("avg_cpu_user_pct"),
                node_summary.get("avg_cpu_system_pct"),
                node_summary.get("avg_cpu_wait_pct"),
                node_summary.get("avg_mem_used_pct"),
                node_summary.get("avg_mem_swap_pct"),
            )
        ),
        "notes_json": json.dumps(extra_metrics, default=str),
    }

    metrics_schema = T.StructType([
        T.StructField("metric_ts_utc", T.StringType(), True),
        T.StructField("run_name", T.StringType(), True),
        T.StructField("step_name", T.StringType(), True),
        T.StructField("row_count", T.LongType(), True),
        T.StructField("duration_seconds", T.DoubleType(), True),
        T.StructField("rows_per_second", T.DoubleType(), True),
        T.StructField("target_partitions", T.IntegerType(), True),
        T.StructField("generate_partitions", T.IntegerType(), True),
        T.StructField("raw_file_partitions", T.IntegerType(), True),
        T.StructField("load_pattern", T.StringType(), True),
        T.StructField("config_batch_size", T.IntegerType(), True),
        T.StructField("group_size", T.IntegerType(), True),
        T.StructField("group_size_multiplier", T.DoubleType(), True),
        T.StructField("benchmark_mode", T.BooleanType(), True),
        T.StructField("source_table", T.StringType(), True),
        T.StructField("target_table", T.StringType(), True),
        T.StructField("cluster_vm_hint", T.StringType(), True),
        T.StructField("cluster_id", T.StringType(), True),
        T.StructField("cluster_name", T.StringType(), True),
        T.StructField("node_type", T.StringType(), True),
        T.StructField("driver_node_type", T.StringType(), True),
        T.StructField("worker_count", T.StringType(), True),
        T.StructField("spark_version", T.StringType(), True),
        T.StructField("default_parallelism", T.IntegerType(), True),
        T.StructField("executor_count_estimate", T.IntegerType(), True),
        T.StructField("avg_cpu_user_pct", T.DoubleType(), True),
        T.StructField("avg_cpu_system_pct", T.DoubleType(), True),
        T.StructField("avg_cpu_wait_pct", T.DoubleType(), True),
        T.StructField("avg_mem_used_pct", T.DoubleType(), True),
        T.StructField("avg_mem_swap_pct", T.DoubleType(), True),
        T.StructField("hardware_metrics_available", T.BooleanType(), True),
        T.StructField("notes_json", T.StringType(), True),
    ])

    metrics_df = spark.createDataFrame([Row(**payload)], schema=metrics_schema)
    (
        metrics_df.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(METRICS_TABLE)
    )

    if METRICS_CSV_PATH:
        (
            metrics_df.coalesce(1)
            .write
            .mode("append")
            .option("header", "true")
            .csv(METRICS_CSV_PATH)
        )

    print(f"Recorded metrics for step '{step_name}' in {METRICS_TABLE}")


def create_perf_summary_view(summary_view_name=None):
    summary_view_name = summary_view_name or f"{METRICS_SCHEMA}.v_thales_perf_test_summary"

    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {summary_view_name} AS
        WITH base AS (
          SELECT
            CAST(metric_ts_utc AS TIMESTAMP) AS metric_ts_utc,
            run_name,
            step_name,
            row_count,
            duration_seconds,
            rows_per_second,
            target_partitions,
            generate_partitions,
            raw_file_partitions,
            load_pattern,
            config_batch_size,
            group_size,
            group_size_multiplier,
            benchmark_mode,
            source_table,
            target_table,
            cluster_vm_hint,
            cluster_id,
            cluster_name,
            node_type,
            driver_node_type,
            worker_count,
            spark_version,
            default_parallelism,
            executor_count_estimate,
            avg_cpu_user_pct,
            avg_cpu_system_pct,
            avg_cpu_wait_pct,
            avg_mem_used_pct,
            avg_mem_swap_pct,
            hardware_metrics_available,
            notes_json,
            ROW_NUMBER() OVER (
              PARTITION BY run_name, step_name, row_count, target_table, source_table
              ORDER BY CAST(metric_ts_utc AS TIMESTAMP) DESC
            ) AS rn
          FROM {METRICS_TABLE}
        )
        SELECT
          metric_ts_utc,
          date(metric_ts_utc) AS metric_date,
          run_name,
          step_name,
          row_count,
          duration_seconds,
          rows_per_second,
          ROUND(rows_per_second / 1000.0, 2) AS rows_per_second_k,
          target_partitions,
          generate_partitions,
          raw_file_partitions,
          load_pattern,
          config_batch_size,
          group_size,
          group_size_multiplier,
          benchmark_mode,
          source_table,
          target_table,
          cluster_vm_hint,
          cluster_id,
          cluster_name,
          node_type,
          driver_node_type,
          worker_count,
          spark_version,
          default_parallelism,
          executor_count_estimate,
          avg_cpu_user_pct,
          avg_cpu_system_pct,
          avg_cpu_wait_pct,
          avg_mem_used_pct,
          avg_mem_swap_pct,
          hardware_metrics_available,
          notes_json
        FROM base
        WHERE rn = 1
        """
    )

    print(f"Created or refreshed summary view {summary_view_name}")
    return summary_view_name


def create_perf_compact_view(compact_view_name=None, summary_view_name=None):
    compact_view_name = compact_view_name or COMPACT_SUMMARY_VIEW
    summary_view_name = summary_view_name or f"{METRICS_CATALOG}.{METRICS_SCHEMA}.v_thales_perf_test_summary"

    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {compact_view_name} AS
        SELECT
          metric_ts_utc,
          metric_date,
          run_name,
          load_pattern,
          step_name,
          row_count,
          duration_seconds,
          rows_per_second,
          rows_per_second_k,
          cluster_vm_hint,
          node_type,
          worker_count,
          executor_count_estimate,
          generate_partitions,
          target_partitions,
          raw_file_partitions,
          config_batch_size,
          group_size,
          group_size_multiplier,
          benchmark_mode,
          hardware_metrics_available
        FROM {summary_view_name}
        """
    )

    print(f"Created or refreshed compact view {compact_view_name}")
    return compact_view_name


def build_perf_comparison_query(summary_view_name, run_name_filter=None):
    run_predicate = (
        f"WHERE run_name = '{run_name_filter}'"
        if run_name_filter
        else ""
    )

    return f"""
    SELECT
      run_name,
      step_name,
      row_count,
      cluster_vm_hint,
      node_type,
      worker_count,
      executor_count_estimate,
      target_partitions,
      generate_partitions,
      raw_file_partitions,
      load_pattern,
      config_batch_size,
      group_size,
      group_size_multiplier,
      benchmark_mode,
      ROUND(AVG(duration_seconds), 2) AS avg_duration_seconds,
      ROUND(AVG(rows_per_second), 2) AS avg_rows_per_second,
      ROUND(AVG(avg_cpu_user_pct), 2) AS avg_cpu_user_pct,
      ROUND(AVG(avg_mem_used_pct), 2) AS avg_mem_used_pct,
      MAX(CASE WHEN hardware_metrics_available THEN 1 ELSE 0 END) AS hardware_metrics_available,
      COUNT(*) AS sample_count
    FROM {summary_view_name}
    {run_predicate}
    GROUP BY
      run_name,
      step_name,
      row_count,
      cluster_vm_hint,
      node_type,
      worker_count,
      executor_count_estimate,
      target_partitions,
      generate_partitions,
      raw_file_partitions,
      load_pattern,
      config_batch_size,
      group_size,
      group_size_multiplier,
      benchmark_mode
    ORDER BY row_count DESC, run_name, step_name
    """
