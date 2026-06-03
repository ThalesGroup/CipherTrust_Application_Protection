# Bulk UDF Tuning Cheat Sheet

This cheat sheet summarizes the main tuning variables used in
[internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py)
and how to think about them during performance testing.

## When to use scalar vs bulk

Use scalar UDFs when the workload is naturally row-oriented and simplicity is
more important than bulk tuning.

Best fit for scalar:

- transaction-style processing
- JDBC or application flows doing inserts, updates, or deletes one row at a time
- smaller row-by-row transformations
- simple `CREATE TABLE AS SELECT` or `INSERT ... SELECT` examples where the goal
  is operational clarity rather than maximum throughput
- cases where the simplest SQL pattern is preferred

Use bulk UDFs when the workload is naturally batch-oriented and values can be
grouped into arrays before protection or reveal.

Best fit for bulk:

- batch loads
- migration jobs
- larger backfills
- analytics-style processing over medium or large result sets
- performance benchmarking and throughput tuning

Simple mental model:

- scalar is best for transaction-oriented row processing
- bulk is best for batch and analytics-style processing

Important clarification:

- scalar notebooks in this repo are still distributed across Spark partitions
  and executors
- they are scalar at the UDF level, meaning one protected value is handled at a
  time inside each row expression
- they do not use grouped bulk-array processing and are not the main notebooks
  for `BATCH_SIZE` tuning
- several scalar demo notebooks read the small sample tables created by
  `plaintext_setup.sql`, which is why they often show about 20 rows instead of
  benchmark-scale volumes

## Benchmark notebooks

There are three bulk benchmark notebooks that all follow the same general
pattern:

- generate a synthetic benchmark source table
- bulk-protect 5 sensitive columns
- write a protected benchmark target table
- show sample encrypted rows
- create a temporary reveal view
- show sample revealed rows
- record benchmark metrics in
  `my_catalog.my_schema.thales_perf_test_metrics`

### Internal bulk benchmark

Notebook:

- [internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py)

What it does:

- benchmarks object-aware bulk protect for the internal use case
- uses `thales_protect_bulk_by_object_and_column(...)`
- uses the protected object mapping for the internal arrays/table path

Main output tables:

- source:
  `my_catalog.my_schema.plaintext_plaintext_bulk_parallelism_diag`
- protected target:
  `my_catalog.my_schema.plaintext_protected_internal_bulk_parallelism_diag`

How to use it:

- use it for bulk internal protect throughput testing
- compare `generate_source_delta` and `protect_internal_table_bulk`
- inspect encrypted rows in the target table
- inspect revealed rows from the temp reveal view created at the end of the
  notebook

### External bulk benchmark

Notebook:

- [external_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external\external_bulk_array_benchmark.py)

What it does:

- benchmarks object-aware bulk protect for the external use case
- uses
  `thales_protect_bulk_by_object_and_column_with_external_header(...)`
- writes both protected values and sibling `*_header` columns

Main output tables:

- source:
  `my_catalog.my_schema.plaintext_plaintext_external_bulk_parallelism_diag`
- protected target:
  `my_catalog.my_schema.plaintext_protected_external_bulk_parallelism_diag`

How to use it:

- use it for bulk external protect throughput testing
- compare `generate_source_delta` and `protect_external_table_bulk`
- inspect encrypted rows plus header columns in the target table
- inspect revealed rows from the temp reveal view created at the end of the
  notebook

### None bulk benchmark

Notebook:

- [none_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\none\none_bulk_array_benchmark.py)

What it does:

- benchmarks object-aware bulk protect for the none use case
- uses `thales_protect_bulk_by_object_and_column(...)`
- writes the normal protected target table used for the benchmark
- also writes a grouped array table after the timed protect step for follow-on
  reveal testing

Main output tables:

- source:
  `my_catalog.my_schema.plaintext_plaintext_bulk_parallelism_diag`
- protected target:
  `my_catalog.my_schema.plaintext_protected_none_bulk_parallelism_diag`
- grouped array table:
  `my_catalog.my_schema.plaintext_protected_none_bulk_parallelism_diag_arrays`

How to use it:

- use it for bulk none protect throughput testing
- compare `generate_source_delta` and
  `protect_none_table_bulk_object_aware`
- inspect encrypted rows in the target table
- inspect revealed rows from the temp reveal view created at the end of the
  notebook

## Recommended starting point

For most benchmark runs:

- set `BATCH_SIZE = 20000` in `udfConfig.properties`
- leave it there unless benchmarking shows a clear reason to change it
- tune the grouping controls in the notebook before tuning `BATCH_SIZE`

Why this is the best starting point:

- it keeps CRDP request chunking large enough for strong baseline throughput
- it avoids forcing customers to hand-tune low-level request sizing too early
- the benchmark notebooks already auto-shape the effective request size using
  the grouping settings

The practical idea is:

- `BATCH_SIZE` is the maximum chunk size CRDP will accept per bulk request
- the notebook decides how many values are grouped together before the Java
  bulk path sees them
- the effective request size is therefore auto-calculated from the notebook
  settings and capped by `BATCH_SIZE`

### Worked example from notebook output

If the notebook prints:

```text
Row count: 100000
Configured BATCH_SIZE: 20000
Group size override: None
Group count override: 64
Group size multiplier: 1.0
Resolved grouping strategy: group_count_override
Resolved group size: 1563
Estimated grouped UDF rows: 64
```

then the practical interpretation is:

- Spark will shape the workload into about `64` grouped UDF rows
- each grouped UDF row will carry about `1563` values for a given protected
  column
- the Java bulk path will compare that grouped size to `BATCH_SIZE = 20000`
- because `1563 < 20000`, CRDP does not need to split the grouped call further
- the effective CRDP request size is therefore about `1563`

Simple formula:

- effective request size ~= `min(resolved_group_size, BATCH_SIZE)`

So for this example:

- `min(1563, 20000) = 1563`

That means:

- `GROUP_COUNT_OVERRIDE` is the setting that really shaped the request size
- `BATCH_SIZE` only acted as the upper ceiling
- if the resolved group size had been `50000`, CRDP would have split it into
  multiple requests because of the `20000` ceiling

## The three control layers

### 1. Spark work shape

These settings control how much Spark work exists and how it is distributed:

- `ROW_COUNT`
- `GENERATE_PARTITIONS`
- `TARGET_PARTITIONS`

Use these to shape:

- total workload size
- Spark task count
- output write parallelism

### How executors, cores, and partitions relate

In Databricks, the compute cluster provides the driver and worker resources.
Spark then uses those worker-side executors to process partitions.

Simple mental model:

- executors are the worker-side JVM processes doing the work
- executor cores determine how many Spark tasks can run at the same time
- partitions are the chunks of data Spark turns into those tasks

That means:

- more executor cores usually allow more tasks to run concurrently
- more partitions give Spark more chunks of work to schedule
- too few partitions can leave executors underutilized
- too many partitions can increase task and shuffle overhead

In these benchmark notebooks:

- `GENERATE_PARTITIONS` shapes source-data generation parallelism
- `TARGET_PARTITIONS` shapes protect/write parallelism
- grouped UDF settings shape how much CRDP work each Spark task carries once it
  starts running

Practical rule of thumb:

- cluster size sets the parallel capacity
- partitions determine how much of that capacity Spark can actually use

### 2. Databricks grouping shape

These settings control how Databricks groups values before calling the bulk UDF:

- `GROUP_SIZE_OVERRIDE`
- `GROUP_COUNT_OVERRIDE`
- `GROUP_SIZE_MULTIPLIER`

Use these to shape:

- values per grouped bulk-UDF call
- number of grouped UDF rows
- amount of independent CRDP work in flight

### 3. CRDP request chunking

This setting controls how the Java bulk path splits each grouped call into one
or more CRDP requests:

- `BATCH_SIZE`

Use this to shape:

- maximum values per outbound CRDP bulk request

## What each main variable really means

### `ROW_COUNT`

How many source rows the notebook generates and processes.

Impact:

- increases total work linearly
- does **not** directly change per-request size
- larger runs are better for stable benchmarking because startup overhead matters less

Rule of thumb:

- use small values for sanity checks
- use large values for real throughput testing

### `GENERATE_PARTITIONS`

How many Spark partitions are used when generating the source Delta table.

Impact:

- affects source-data generation speed
- has little direct effect on CRDP throughput once the source table is already written
- too low can underutilize Spark during generation
- too high can add unnecessary Spark overhead

This mostly matters for:

- the `generate_source_delta` step

not as much for:

- the `protect_internal_table_bulk` step

### `TARGET_PARTITIONS`

How many partitions are used before writing the protected output table.

Impact:

- affects Spark task count and output write parallelism
- can slightly affect end-to-end protect step time because flattening/writing is part of the step
- usually not the main CRDP lever

Too low:

- not enough Spark write parallelism

Too high:

- more shuffle/task overhead

### `CONFIG_BATCH_SIZE`

This is read from `udfConfig.properties` as `BATCH_SIZE`.

Impact:

- controls the **maximum number of values CRDP sends in a single `/v1/protectbulk` or `/v1/revealbulk` request**
- it is the **CRDP-side chunk ceiling**
- it only matters if Databricks hands CRDP a list larger than this

Recommended default:

- set `BATCH_SIZE = 20000`

For most customers, do not treat `BATCH_SIZE` as the first tuning knob.
Instead:

- leave `BATCH_SIZE` at `20000`
- let the notebook auto-calculate the working request shape through:
  - `GROUP_SIZE_OVERRIDE`
  - `GROUP_COUNT_OVERRIDE`
  - `GROUP_SIZE_MULTIPLIER`

Important:

- actual request size is roughly `min(resolved_group_size, BATCH_SIZE)`

So if:

- `GROUP_SIZE = 5469`
- `BATCH_SIZE = 20000`

then CRDP request size is about `5469`, not `20000`.

That is why `BATCH_SIZE = 20000` can stay fixed while the effective request
size still changes from run to run. The benchmark notebook auto-calculates the
grouping shape first, and then the CRDP layer uses `BATCH_SIZE` only as the
final ceiling.

Simple mental model:

- start at `BATCH_SIZE = 20000`
- change grouping settings in the notebook
- let the resolved `GROUP_SIZE` determine the real request size
- only change `BATCH_SIZE` if the resolved grouped calls are consistently
  larger than `20000` and benchmarking shows a real benefit

### `GROUP_SIZE_OVERRIDE`

If set, this directly forces the group size.

Impact:

- controls **how many values go into each grouped bulk-UDF call**
- this is the clearest knob for controlling CRDP request size, as long as it stays below `BATCH_SIZE`

If you want about 10,000 values per grouped call:

```python
GROUP_SIZE_OVERRIDE = 10000
```

Use when:

- you want precise control
- you want predictable Prometheus counts
- you want to test larger or smaller grouped requests directly

### `GROUP_COUNT_OVERRIDE`

If set, this forces an approximate number of grouped UDF rows by deriving:

- `GROUP_SIZE = ceil(ROW_COUNT / GROUP_COUNT_OVERRIDE)`

Impact:

- controls **how many grouped bulk-UDF rows Spark creates**
- this effectively controls how much independent CRDP work can be in flight
- this is more of a **parallelism-shaping knob** than a request-size knob

Example:

- `ROW_COUNT = 350000`
- `GROUP_COUNT_OVERRIDE = 64`

gives:

- `GROUP_SIZE = 5469`
- about `64` grouped UDF rows

Use when:

- doing executor-scaling experiments
- doing parallelism experiments
- trying to keep grouped work roughly stable across runs

Not ideal as the universal default for:

- tiny runs
- simple baseline docs
- cases where you just want `GROUP_SIZE ~= BATCH_SIZE`

### `GROUP_SIZE_MULTIPLIER`

Used only when neither override is set.

Then:

- `GROUP_SIZE = BATCH_SIZE * GROUP_SIZE_MULTIPLIER`

Impact:

- lets you scale grouping up or down relative to `BATCH_SIZE`
- easier for general baseline tuning than fixed `GROUP_COUNT_OVERRIDE`

Examples:

- `1.0` means `GROUP_SIZE ~= BATCH_SIZE`
- `0.5` means smaller grouped calls and more request fan-out
- `2.0` means larger grouped calls, which may cause CRDP to split them into multiple requests

## Derived variables

### `GROUP_SIZE`

This is the most important resolved runtime value.

It determines:

- values per grouped bulk-UDF call
- grouped UDF row count
- request fan-out shape

Formulas:

- grouped rows ~= `ceil(ROW_COUNT / GROUP_SIZE)`
- expected request count ~= `grouped_rows * protected_columns`
- expected transaction count = `ROW_COUNT * protected_columns`

For the current 5 protected columns:

- requests ~= `grouped_rows * 5`
- transactions = `ROW_COUNT * 5`

### `ESTIMATED_GROUP_COUNT`

Computed as:

- `ceil(ROW_COUNT / GROUP_SIZE)`

Impact:

- estimates how many grouped bulk-UDF rows Spark will process
- a good proxy for how much independent work can be fed to executors

More grouped rows usually means:

- more Spark and CRDP concurrency potential

Fewer grouped rows usually means:

- larger individual calls
- lower request overhead
- less independent work in flight

## The most important mental model

### `GROUP_SIZE`

Controls:

- how large each grouped call is

### `GROUP_COUNT_OVERRIDE`

Controls:

- how many grouped calls Spark creates

That makes:

- `GROUP_SIZE_OVERRIDE` a request-size knob
- `GROUP_COUNT_OVERRIDE` a parallelism-shaping knob
- `BATCH_SIZE` the CRDP request-chunk ceiling

## Core formulas

Assuming 5 protected columns in the current bulk benchmark:

- grouped rows ~= `ceil(ROW_COUNT / GROUP_SIZE)`
- expected request count ~= `grouped_rows * 5`
- expected transaction count = `ROW_COUNT * 5`

These formulas are useful for validating Prometheus counters.

## Prometheus sanity check

For the current bulk benchmark notebooks:

- each input row protects `5` columns
- `protect_bulk_success_transaction_count` should track total protected values
- `protect_bulk_success_count` should track successful bulk protect requests

That means:

- expected `protect_bulk_success_transaction_count = ROW_COUNT * 5`
- expected `protect_bulk_success_count ~= ceil(ROW_COUNT / GROUP_SIZE) * 5`

Examples for `ROW_COUNT = 10`:

- `GROUP_SIZE = 1`
  expected request count = `50`
  expected transaction count = `50`
- `GROUP_SIZE = 5`
  expected request count = `10`
  expected transaction count = `50`
- `GROUP_SIZE = 10`
  expected request count = `5`
  expected transaction count = `50`

This is especially helpful for small runs where a large `GROUP_COUNT_OVERRIDE` can resolve to `GROUP_SIZE = 1` and make the request count look surprisingly high even though the notebook is behaving correctly.

## Recommended starting patterns

### Simple medium/large baseline

```python
GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0
```

Use when:

- you want the simplest benchmark baseline
- you want `GROUP_SIZE ~= BATCH_SIZE`

### Parallelism experiment

```python
GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0
```

Use when:

- you want to test whether executors have enough grouped rows to stay busy
- you want to shape CRDP fan-out without forcing an exact request size

### Fixed request-size experiment

```python
GROUP_SIZE_OVERRIDE = 10000
GROUP_COUNT_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0
```

Use when:

- you want grouped calls of about 10,000 values each
- you want a clearer relationship between grouping and CRDP request size

## When not to overuse `GROUP_COUNT_OVERRIDE`

Avoid making `GROUP_COUNT_OVERRIDE` the default for every run when:

- doing tiny sanity-check runs
- writing simple baseline docs
- you only want `GROUP_SIZE ~= BATCH_SIZE`

It is best treated as an advanced tuning control, not the universal default.

## Practical takeaway

If you want:

- larger CRDP requests, increase `GROUP_SIZE`
- more independent work in flight, increase grouped row count
- simpler behavior, stay close to the baseline pattern

If you are unsure where to start:

1. begin with the simple medium/large baseline
2. use `GROUP_COUNT_OVERRIDE` for executor and parallelism experiments
3. use `GROUP_SIZE_OVERRIDE` when you want precise control over grouped call size
