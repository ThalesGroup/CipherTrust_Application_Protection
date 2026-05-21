# Bulk UDF Tuning Cheat Sheet

This cheat sheet summarizes the main tuning variables used in
[internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal\internal_bulk_array_benchmark.py)
and how to think about them during performance testing.

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

Important:

- actual request size is roughly `min(resolved_group_size, BATCH_SIZE)`

So if:

- `GROUP_SIZE = 5469`
- `BATCH_SIZE = 20000`

then CRDP request size is about `5469`, not `20000`.

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
