# Public Execution Guidelines And Tuning

This document explains the current public-safe tuning model for the compute-cluster benchmark scripts in this repo.



## Executive Summary

Use the `Python helper v2` path as the default recommendation for notebook-first and DataFrame-first compute-cluster workloads.

Use the `Java UDF` path when teams strongly prefer:

- SQL-shaped ETL
- CTAS / `INSERT OVERWRITE`
- row-oriented Spark SQL expressions
- a familiar Java UDF operating model

Use `Unity Catalog Python UDFs` for governed SQL-facing use cases such as SQL Warehouse, BI tools, and persistent catalog functions/views.

For customers using the compute-cluster helper API, the parameter-level explanation of the input DataFrame, `object_name`, `config`, and `options` is documented in:

- [PYTHON_DIRECT_API_GUIDE.md](E:\codex\work\thales.databricks.integration\docs\PYTHON_DIRECT_API_GUIDE.md:1)
- [JAVA_UDF_API_GUIDE.md](E:\codex\work\thales.databricks.integration\docs\JAVA_UDF_API_GUIDE.md:1)

## Current Recommendation By Use Case

| Use case | Recommended path | Why |
|---|---|---|
| Notebook-first / DataFrame-first pipelines | Python helper v2 | Simplest API and clearest high-level control model |
| SQL-shaped compute-cluster ETL / CTAS | Java UDF | Best fit for Spark SQL expressions and CTAS-style jobs |
| Governed shared SQL abstraction | UC Python UDF | Persistent catalog function/view model |
| Benchmarking logical work-unit tuning | Python helper v2 or Java benchmark2 | Both now expose the same logical tuning model |

## The Three Control Layers

The current tuning model is easiest to understand as three layers:

1. `Spark / Databricks parallelism`

- how many partitions/tasks are created
- how much work Spark can schedule in parallel

2. `Work-unit shaping`

- how many business rows are grouped into one logical unit of work
- how many grouped work units the job creates

3. `CRDP request shaping`

- how many protected values go into one outbound `protectbulk` or `revealbulk` request
- whether multiple policy groups can be combined when the execution path supports it

## The New Logical Tuning Knobs

The simplified logical model is:

- `WORK_UNIT_COUNT_TARGET`
- `WORK_UNIT_COUNT_MULTIPLIER`
- `WORK_UNIT_ROW_COUNT`
- `CRDP_REQUEST_ITEM_TARGET`
- `CRDP_MULTI_POLICY_ENABLED`

Interpretation:

- `WORK_UNIT_COUNT_TARGET`
  target number of grouped work units
- `WORK_UNIT_COUNT_MULTIPLIER`
  auto-mode multiplier that derives work-unit count from target partitions
- `WORK_UNIT_ROW_COUNT`
  target number of business rows per grouped work unit
- `CRDP_REQUEST_ITEM_TARGET`
  target number of protected values in one outbound CRDP request chunk
- `CRDP_MULTI_POLICY_ENABLED`
  whether the engine should combine multiple policy groups when the path supports it

## Recommended Default Positioning

If a team asks, "What should we use by default?", the answer should be:

- `Python helper v2` for performance-first compute-cluster batch workloads
- `Java UDF` for SQL-first compute-cluster workflows
- `UC Python UDF` for governed shared SQL

For the newer benchmark scripts, the recommended default logical settings are:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

That is the recommended auto path.

## How Auto Calculation Works

For the `benchmark2`-style scripts, the flow is:

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
- otherwise align it to the derived work-unit size, usually with a script-side ceiling for large runs

### Example

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

## When The Multiplier Is Used

`WORK_UNIT_COUNT_MULTIPLIER` only matters in auto mode.

It is used when both of these stay unset:

- `WORK_UNIT_COUNT_TARGET = None`
- `WORK_UNIT_ROW_COUNT = None`

When it is not used:

- if you explicitly set `WORK_UNIT_COUNT_TARGET`
- if you explicitly set `WORK_UNIT_ROW_COUNT`

In those cases, the multiplier is bypassed.

Simple interpretation:

- `1.0` means about one work unit per target partition
- `2.0` means about two work units per target partition
- higher values mean more, smaller work units
- lower values mean fewer, larger work units

## How Partition Auto Calculation Works

The newer scripts also auto-calculate partition recommendations.

### Generate partitions

Generation partitioning starts from total row count plus cluster scheduling capacity.

The scripts use row bands such as:

- `small`: up to `1,000,000` rows
- `medium`: more than `1,000,000` and up to `10,000,000` rows
- `large`: more than `10,000,000` rows

For generation, the auto path derives:

- a target rows-per-partition value by load tier
- a partition floor from `spark.sparkContext.defaultParallelism`
- a recommended partition count as the larger of:
  - data-based partitions
  - partition floor

### Target partitions

Target/output partitioning starts from estimated output size.

The auto path derives:

- average row width from a sample
- estimated total output size
- a size-based partition count using a target partition size
- a partition floor from `spark.sparkContext.defaultParallelism`
- a recommended target partition count as the larger of:
  - size-based partitions
  - partition floor

This is why a smaller dataset may still end up with more partitions than its raw size alone would suggest: the floor keeps enough Spark work available to occupy the cluster.

## Current Load Bands For The Auto Path

### 1. Small Loads

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

Interpretation:

- let the script auto-calculate partitions
- let the script derive work-unit count from target partitions
- let request sizing align automatically to the work-unit size

### 2. Medium Loads

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

Interpretation:

- use the auto-derived target partitions
- use the auto-derived work-unit count
- keep CRDP request sizing in auto mode unless you are intentionally experimenting

### 3. Large Loads

Row band:

- more than `10,000,000` rows

Typical intent:

- throughput-focused protect jobs
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

Interpretation:

- let the script scale partition counts by load tier
- let the script derive grouped work from final target partitions
- use the auto request ceiling first, then override only if testing shows a clear reason

## Java And Python Alignment

For the newer benchmark scripts, the Java grouped-array path and the Python helper path now use the same logical tuning model:

- `WORK_UNIT_COUNT_TARGET`
- `WORK_UNIT_COUNT_MULTIPLIER`
- `WORK_UNIT_ROW_COUNT`
- `CRDP_REQUEST_ITEM_TARGET`

The mechanics are still different:

- Python helper path uses the resolved values directly in the helper runtime
- Java grouped-array benchmark resolves the same logical values in the notebook, then passes the effective request target into Java through `spark.conf`

But the public tuning model is now aligned enough that teams can reason about both paths with the same mental model.

## CRDP Multi-Policy Guidance

`CRDP_MULTI_POLICY_ENABLED` is meaningful when the execution path supports combining policy groups in one request.

Current public guidance:

- leave it unset in the benchmark scripts unless you want to force a specific behavior
- treat it as a path-dependent capability, not a universal knob that behaves identically everywhere

## Safety And Validation Notes

- `CRDP_REQUEST_ITEM_TARGET` must be positive when explicitly set
- values `<= 0` should fail fast
- values below `1000` are valid for testing, but should be treated as intentionally conservative
- use auto mode first before introducing explicit overrides

## Practical Guidance

A simple public-safe recommendation is:

1. Start with the auto path:

```python
WORK_UNIT_COUNT_TARGET = None
WORK_UNIT_COUNT_MULTIPLIER = 2.0
WORK_UNIT_ROW_COUNT = None
CRDP_REQUEST_ITEM_TARGET = None
CRDP_MULTI_POLICY_ENABLED = None
```

2. Run the benchmark or workload and inspect:

- `effective_target_partitions`
- `work_unit_count_target`
- `work_unit_row_count`
- `effective_crdp_request_item_target`

3. Only override values when you have a specific reason:

- force `WORK_UNIT_COUNT_TARGET` if you want a known grouped-work count
- force `WORK_UNIT_ROW_COUNT` if you want a known grouped-work size
- force `CRDP_REQUEST_ITEM_TARGET` if you want a known CRDP chunk size

In most cases, the auto path is the right public recommendation and the right first test position.

