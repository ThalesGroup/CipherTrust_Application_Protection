from math import ceil

from pyspark.sql import functions as F


DEFAULT_AVG_ROW_BYTES = 512
ONE_MB = 1024 * 1024


def _safe_collect_scalar(df, column_name, fallback):
    row = df.collect()
    if not row:
        return fallback
    value = row[0][column_name]
    return fallback if value is None else value


def estimate_average_row_bytes(df, sample_rows=2000, fallback_bytes=DEFAULT_AVG_ROW_BYTES):
    sample_count = max(int(sample_rows), 1)
    sampled = df.limit(sample_count)
    stats_df = sampled.select(
        F.avg(F.length(F.to_json(F.struct(*[F.col(c) for c in df.columns])))).alias("avg_row_bytes")
    )
    return float(_safe_collect_scalar(stats_df, "avg_row_bytes", fallback_bytes))


def recommend_generate_partitions(
    row_count,
    default_parallelism,
    min_partitions=8,
):
    row_count = max(int(row_count), 1)
    default_parallelism = max(int(default_parallelism), 1)

    if row_count <= 1_000_000:
        target_rows_per_partition = 250_000
        partition_floor = default_parallelism * 2
        load_tier = "small"
    elif row_count <= 10_000_000:
        target_rows_per_partition = 500_000
        partition_floor = default_parallelism * 4
        load_tier = "medium"
    else:
        target_rows_per_partition = 1_000_000
        partition_floor = default_parallelism * 4
        load_tier = "large"

    data_based_partitions = ceil(row_count / target_rows_per_partition)
    recommended = max(data_based_partitions, partition_floor, int(min_partitions))

    return {
        "recommended_partitions": recommended,
        "load_tier": load_tier,
        "target_rows_per_partition": target_rows_per_partition,
        "partition_floor": partition_floor,
        "data_based_partitions": data_based_partitions,
        "notes": [
            "Generation partitioning is based on row count plus Spark default parallelism.",
            "The partition floor keeps enough tasks available to occupy the cluster.",
        ],
    }


def recommend_target_partitions(
    row_count,
    default_parallelism,
    dataframe=None,
    avg_row_bytes=None,
    sample_rows=2000,
    min_partitions=8,
    target_partition_size_mb=128,
):
    row_count = max(int(row_count), 1)
    default_parallelism = max(int(default_parallelism), 1)
    min_partitions = max(int(min_partitions), 1)
    target_partition_size_bytes = max(int(target_partition_size_mb), 1) * ONE_MB

    if avg_row_bytes is None:
        if dataframe is not None:
            avg_row_bytes = estimate_average_row_bytes(dataframe, sample_rows=sample_rows)
        else:
            avg_row_bytes = DEFAULT_AVG_ROW_BYTES

    estimated_total_bytes = max(int(row_count * float(avg_row_bytes)), 1)
    size_based_partitions = ceil(estimated_total_bytes / target_partition_size_bytes)

    if estimated_total_bytes <= ONE_MB * 1024:
        partition_floor = default_parallelism
        size_tier = "small"
    elif estimated_total_bytes <= ONE_MB * 1024 * 50:
        partition_floor = default_parallelism * 2
        size_tier = "medium"
    else:
        partition_floor = default_parallelism * 4
        size_tier = "large"

    recommended = max(size_based_partitions, partition_floor, min_partitions)

    return {
        "recommended_partitions": recommended,
        "size_tier": size_tier,
        "avg_row_bytes": float(avg_row_bytes),
        "estimated_total_bytes": estimated_total_bytes,
        "estimated_total_mb": round(estimated_total_bytes / ONE_MB, 2),
        "target_partition_size_mb": target_partition_size_mb,
        "partition_floor": partition_floor,
        "size_based_partitions": size_based_partitions,
        "notes": [
            "Target partitioning is based on sampled row width plus Spark default parallelism.",
            "Estimated output size is divided into roughly even 128 MB target partitions.",
        ],
    }


def recommend_helper_execution_controls(
    row_count,
    target_partitions,
    work_unit_multiplier=2.0,
    max_crdp_request_item_target=20000,
):
    row_count = max(int(row_count), 1)
    target_partitions = max(int(target_partitions), 1)
    work_unit_multiplier = max(float(work_unit_multiplier), 1.0)

    work_unit_count_target = max(int(ceil(target_partitions * work_unit_multiplier)), 1)
    work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)

    if max_crdp_request_item_target is None:
        crdp_request_item_target = work_unit_row_count
        request_target_strategy = "align_to_work_unit_row_count"
    else:
        capped_target = max(int(max_crdp_request_item_target), 1)
        crdp_request_item_target = min(work_unit_row_count, capped_target)
        request_target_strategy = "min(work_unit_row_count, max_crdp_request_item_target)"

    return {
        "work_unit_count_target": work_unit_count_target,
        "work_unit_row_count": work_unit_row_count,
        "crdp_request_item_target": crdp_request_item_target,
        "work_unit_multiplier": work_unit_multiplier,
        "request_target_strategy": request_target_strategy,
        "notes": [
            "Helper execution controls are anchored to the final target partition count.",
            "The default strategy creates about 2 work units per target partition.",
        ],
    }


def print_auto_tuning_section(title, values):
    print(title)
    for key, value in values.items():
        if key == "notes":
            print("  notes:")
            for note in value:
                print(f"    - {note}")
        else:
            print(f"  {key}: {value}")


def recommend_java_grouped_array_controls(
    row_count,
    target_partitions,
    config_batch_size,
    work_unit_multiplier=2.0,
    max_crdp_request_item_target=20000,
    explicit_work_unit_count_target=None,
    explicit_work_unit_row_count=None,
    legacy_group_count_override=None,
    legacy_group_size_override=None,
    explicit_crdp_request_item_target=None,
):
    row_count = max(int(row_count), 1)
    target_partitions = max(int(target_partitions), 1)
    config_batch_size = max(int(config_batch_size), 1)
    work_unit_multiplier = max(float(work_unit_multiplier), 1.0)

    if explicit_work_unit_row_count is not None:
        work_unit_row_count = max(int(explicit_work_unit_row_count), 1)
        work_unit_row_strategy = "work_unit_row_count"
        work_unit_count_target = max(int(ceil(float(row_count) / float(work_unit_row_count))), 1)
        work_unit_count_strategy = "derived_from_work_unit_row_count"
    elif legacy_group_size_override is not None:
        work_unit_row_count = max(int(legacy_group_size_override), 1)
        work_unit_row_strategy = "group_size_override"
        work_unit_count_target = max(int(ceil(float(row_count) / float(work_unit_row_count))), 1)
        work_unit_count_strategy = "derived_from_group_size_override"
    elif explicit_work_unit_count_target is not None:
        work_unit_count_target = max(int(explicit_work_unit_count_target), 1)
        work_unit_count_strategy = "work_unit_count_target"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "derived_from_work_unit_count_target"
    elif legacy_group_count_override is not None:
        work_unit_count_target = max(int(legacy_group_count_override), 1)
        work_unit_count_strategy = "group_count_override"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "group_count_override"
    else:
        work_unit_count_target = max(int(ceil(float(target_partitions) * float(work_unit_multiplier))), 1)
        work_unit_count_strategy = "target_partitions_multiplier"
        work_unit_row_count = max(int(ceil(float(row_count) / float(work_unit_count_target))), 1)
        work_unit_row_strategy = "derived_from_target_partitions_multiplier"

    if explicit_crdp_request_item_target is not None:
        recommended_crdp_request_item_target = max(int(explicit_crdp_request_item_target), 1)
        recommended_crdp_request_item_strategy = "explicit_crdp_request_item_target"
    elif max_crdp_request_item_target is None:
        recommended_crdp_request_item_target = work_unit_row_count
        recommended_crdp_request_item_strategy = "align_to_work_unit_row_count"
    else:
        capped_target = max(int(max_crdp_request_item_target), 1)
        recommended_crdp_request_item_target = min(work_unit_row_count, capped_target)
        recommended_crdp_request_item_strategy = "min(work_unit_row_count, max_crdp_request_item_target)"

    effective_runtime_crdp_request_item_target = min(
        work_unit_row_count,
        recommended_crdp_request_item_target,
    )

    return {
        "work_unit_count_target": work_unit_count_target,
        "work_unit_count_strategy": work_unit_count_strategy,
        "work_unit_row_count": work_unit_row_count,
        "work_unit_row_strategy": work_unit_row_strategy,
        "recommended_crdp_request_item_target": recommended_crdp_request_item_target,
        "recommended_crdp_request_item_strategy": recommended_crdp_request_item_strategy,
        "effective_runtime_crdp_request_item_target": effective_runtime_crdp_request_item_target,
        "runtime_request_item_strategy": "min(work_unit_row_count, recommended_crdp_request_item_target)",
        "config_batch_size_limit": config_batch_size,
        "notes": [
            "Java grouped-array controls are anchored to the final target partition count.",
            "Java benchmark notebooks can apply the derived request target at runtime through a Spark SQL conf override.",
            "BATCH_SIZE in udfConfig.properties remains the fallback when no runtime override is applied.",
        ],
    }



