# Tuning Model And Use Case Matrix

This document explains the current tuning model for the newer benchmark scripts in this repo.

It focuses on the logical controls that now matter most across the benchmark2-style paths:

- `ROW_COUNT`
- `GENERATE_PARTITIONS`
- `TARGET_PARTITIONS`
- `WORK_UNIT_COUNT_TARGET`
- `WORK_UNIT_COUNT_MULTIPLIER`
- `WORK_UNIT_ROW_COUNT`
- `CRDP_REQUEST_ITEM_TARGET`
- `CRDP_MULTI_POLICY_ENABLED`

## Executive Summary

The simplest correct mental model is:

1. Spark parallelism decides how much scheduled work exists.
2. Work-unit shaping decides how many business rows move together.
3. CRDP request shaping decides how many protected values go into one outbound request chunk.

For the newer benchmark notebooks, both the Python helper path and the Java benchmark2 path are now explained with the same logical tuning surface:

- `WORK_UNIT_COUNT_TARGET`
- `WORK_UNIT_COUNT_MULTIPLIER`
- `WORK_UNIT_ROW_COUNT`
- `CRDP_REQUEST_ITEM_TARGET`

The internal implementations are still different, but the tuning model is now close enough that teams can reason about both paths the same way.

## The Three Control Layers

### 1. Spark / Databricks parallelism

These settings control how much Spark work exists and how it is distributed:

- `ROW_COUNT`
- `GENERATE_PARTITIONS`
- `TARGET_PARTITIONS`

What this affects:

- total workload size
- number of Spark tasks
- executor utilization
- read/write parallelism

### 2. Work-unit shaping

These settings control how many business rows are grouped into one logical unit of work:

- `WORK_UNIT_COUNT_TARGET`
- `WORK_UNIT_COUNT_MULTIPLIER`
- `WORK_UNIT_ROW_COUNT`

What this affects:

- how many grouped work units the job creates
- how many rows travel together through the protect/reveal engine
- how much work can be in flight at once

### 3. CRDP request shaping

These settings control how large each outbound CRDP request becomes:

- `CRDP_REQUEST_ITEM_TARGET`
- `CRDP_MULTI_POLICY_ENABLED`

What this affects:

- values per `protectbulk` or `revealbulk` call
- request count
- whether the execution path can combine multiple policy groups when supported

## Current Logical Settings Matrix

| Setting | Meaning | Auto behavior when unset | Typical reason to override |
|---|---|---|---|
| `ROW_COUNT` | Total rows processed | N/A | Run bigger or smaller tests |
| `GENERATE_PARTITIONS` | Source generation partition count | Auto-derived in benchmark2 scripts | Force source-side fan-out |
| `TARGET_PARTITIONS` | Target/write partition count | Auto-derived in benchmark2 scripts | Force output-side fan-out |
| `WORK_UNIT_COUNT_TARGET` | Target number of grouped work units | Derived from `TARGET_PARTITIONS * WORK_UNIT_COUNT_MULTIPLIER` | Force a known grouped-work count |
| `WORK_UNIT_COUNT_MULTIPLIER` | Auto-mode work-unit multiplier | Defaults to `2.0` in the newer scripts | Increase or decrease grouped-work fan-out |
| `WORK_UNIT_ROW_COUNT` | Rows per grouped work unit | Derived from `ROW_COUNT / WORK_UNIT_COUNT_TARGET` | Force a known grouped-work size |
| `CRDP_REQUEST_ITEM_TARGET` | Target values per CRDP request chunk | Auto-aligned to work-unit size, usually capped in script logic | Force a known CRDP chunk size |
| `CRDP_MULTI_POLICY_ENABLED` | Whether mixed policy groups can combine when supported | Usually left unset in benchmark scripts | Force or test path behavior |

## Recommended Default Position

For the newer benchmark scripts, the recommended default starting point is:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

That is the recommended auto path.

## How Auto Mode Works

### Core derivation order

For the benchmark2 logic, the flow is:

1. Start with `TARGET_PARTITIONS`
2. Derive:

```python
work_unit_count_target = ceil(TARGET_PARTITIONS * WORK_UNIT_COUNT_MULTIPLIER)
```

3. Then derive:

```python
work_unit_row_count = ceil(ROW_COUNT / work_unit_count_target)
```

4. Then derive the CRDP request target:

- if `CRDP_REQUEST_ITEM_TARGET` is explicitly set, use that value
- otherwise align it to the work-unit size
- for larger runs, apply any script-side safety ceiling

### Worked example

If:

- `ROW_COUNT = 350000`
- `TARGET_PARTITIONS = 32`
- `WORK_UNIT_COUNT_MULTIPLIER = 2.0`

then the script derives:

```python
work_unit_count_target = ceil(32 * 2.0) = 64
work_unit_row_count = ceil(350000 / 64) = 5469
```

That is why the notebook prints values such as:

- `work_unit_count_target: 64`
- `work_unit_row_count: 5469`
- `work_unit_row_strategy: derived_from_target_partitions_multiplier`

## When The Multiplier Is Active

`WORK_UNIT_COUNT_MULTIPLIER` only matters in auto mode.

It is used when both of these are unset:

- `WORK_UNIT_COUNT_TARGET = None`
- `WORK_UNIT_ROW_COUNT = None`

It is bypassed when:

- `WORK_UNIT_COUNT_TARGET` is explicitly set
- `WORK_UNIT_ROW_COUNT` is explicitly set

Simple interpretation:

- `1.0` means about one work unit per target partition
- `2.0` means about two work units per target partition
- higher values mean more, smaller work units
- lower values mean fewer, larger work units

## How Partition Auto Calculation Works

The newer scripts also auto-calculate partition recommendations.

### Generate partitions

Generation partitioning starts from total row count plus cluster scheduling capacity.

The current row bands used by the benchmark2 scripts are:

- `small`: up to `1,000,000` rows
- `medium`: more than `1,000,000` and up to `10,000,000` rows
- `large`: more than `10,000,000` rows

The scripts derive generation partitioning from:

- row-count tier
- target rows per partition by tier
- partition floor from `spark.sparkContext.defaultParallelism`

### Target partitions

Target/output partitioning starts from estimated output size.

The scripts derive target partitioning from:

- sampled average row width
- estimated total output size
- target output partition size
- partition floor from `spark.sparkContext.defaultParallelism`

This is why a smaller dataset may still end up with more partitions than raw data size alone suggests: the partition floor keeps enough tasks available to occupy the cluster.

## Current Load Bands

### Small loads

Row band:

- up to `1,000,000` rows

Typical intent:

- validation
- smoke tests
- short benchmark runs

Recommended logical settings:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

### Medium loads

Row band:

- more than `1,000,000` and up to `10,000,000` rows

Typical intent:

- sustained comparison runs
- fair tuning baselines
- moderate throughput tuning

Recommended logical settings:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

### Large loads

Row band:

- more than `10,000,000` rows

Typical intent:

- throughput-focused jobs
- long-running production-style tests
- scaling studies

Recommended logical settings:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

## Java And Python Alignment

For the newer benchmark scripts, the Java grouped-array benchmark path and the Python helper benchmark path now align conceptually like this:

| Logical concept | Java benchmark2 path | Python helper benchmark2 path |
|---|---|---|
| Spark fan-out | `GENERATE_PARTITIONS`, `TARGET_PARTITIONS` | `GENERATE_PARTITIONS`, `TARGET_PARTITIONS` |
| Work-unit count | derived from `WORK_UNIT_COUNT_TARGET` or multiplier | derived from `WORK_UNIT_COUNT_TARGET` or multiplier |
| Work-unit row size | derived from `WORK_UNIT_ROW_COUNT` or work-unit count | derived from `WORK_UNIT_ROW_COUNT` or work-unit count |
| CRDP chunk size | derived from `CRDP_REQUEST_ITEM_TARGET`, passed to Java via `spark.conf` | derived from `CRDP_REQUEST_ITEM_TARGET`, used directly by helper |

The mechanics are still different:

- Python helper uses the resolved values directly in the helper runtime
- Java benchmark2 resolves the same logical values in the notebook and passes the effective request target into Java through `spark.conf`

But the user-facing tuning story is now similar enough that teams should think in terms of the same logical settings first.

## Use Case Matrix

| Use case | Focus most on | Why |
|---|---|---|
| Quick validation run | `ROW_COUNT`, auto partitions | Keep the run simple and fast |
| Fair baseline comparison | `TARGET_PARTITIONS`, multiplier auto path | Let the script derive grouped work consistently |
| Throughput experiment | `TARGET_PARTITIONS`, `WORK_UNIT_COUNT_MULTIPLIER`, `CRDP_REQUEST_ITEM_TARGET` | These most directly change parallelism, grouped work, and request size |
| Fixed-shape experiment | `WORK_UNIT_COUNT_TARGET` or `WORK_UNIT_ROW_COUNT` | Force a known grouped-work pattern |
| CRDP chunk test | `CRDP_REQUEST_ITEM_TARGET` | Force a known request size without changing total row count |

## What Teams Should Usually Do

A simple public-safe recommendation is:

1. Start with the auto path:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

2. Run the workload and inspect:

- `effective_target_partitions`
- `work_unit_count_target`
- `work_unit_row_count`
- `effective_crdp_request_item_target`

3. Only override values when you have a specific reason:

- set `WORK_UNIT_COUNT_TARGET` when you want a known grouped-work count
- set `WORK_UNIT_ROW_COUNT` when you want a known grouped-work size
- set `CRDP_REQUEST_ITEM_TARGET` when you want a known CRDP chunk size

In most cases, the auto path is the right starting point and the right public recommendation.
