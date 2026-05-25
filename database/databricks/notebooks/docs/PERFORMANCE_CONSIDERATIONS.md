# Performance Considerations

This note explains the fastest practical ways to transform plaintext data with
the current Databricks UDF project, and how to think about scalar UDFs, bulk
functions, arrays, Spark partitions, and executors.

## Most important practical warning

If the cluster is effectively single-node, throughput results will be much
lower than a real distributed load.

In recent benchmark runs, the metrics showed:

- `worker_count = 0`
- `executor_count_estimate = 0`

That usually means there are no separate worker executors beyond the driver.
Even if the node itself has 4 cores, that is still not the same as a real
multi-worker Spark cluster.

Why this matters:

- the Java UDF work is not spreading across multiple worker nodes
- outbound CRDP concurrency is limited
- a single-node run is useful for correctness, but not for estimating scaled
  production throughput

So the best mental model is:

- single-node benchmark = functional validation and rough baseline
- multi-worker benchmark = realistic throughput measurement

## Short answer

For customers loading plaintext and wanting to protect it quickly, the best
current default path is:

- use a Databricks compute cluster
- use the Java UDFs
- run `CREATE TABLE AS SELECT` or `INSERT ... SELECT`
- let Spark parallelize the work across partitions and executors

In other words:

- executors and partitions give you parallelism
- bulk and array functions reduce UDF and CRDP call overhead
- Java `UDF1` / `UDF3` names describe function signatures, not speed tiers

## Simple mental model

### Scalar Java UDFs

Examples:

- `thales_protect_by_column(...)`
- `thales_protect_by_column_with_external_header(...)`

These run per row, but Spark still distributes those rows across partitions and
executors.

So a statement like this is already parallelized by Spark:

```sql
CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal AS
SELECT
  custid,
  thales_protect_by_column(CAST(email AS STRING), 'char', 'email') AS email
FROM my_catalog.my_schema.plaintext_plaintext;
```

It is row-wise at the function level, but cluster-parallel at the Spark task
level.

### Bulk and array UDFs

Examples:

- `thales_protect_bulk_by_column(...)`
- `thales_reveal_bulk_by_column_with_user(...)`

These handle arrays of values in one call.

That can help when:

- UDF invocation overhead matters
- CRDP bulk APIs help
- the workflow can tolerate batching into arrays and flattening later

### Executors and partitions

This is usually the first scaling lever that matters.

Even scalar Java UDFs can perform well if:

- the source table has enough data
- Spark partitions are healthy
- executors are busy

So the biggest practical speed improvement often comes from Spark parallelism
itself, not from whether the Java class implements `UDF1`, `UDF3`, or `UDF5`.

## The first tuning lever: cluster shape

Before fine-tuning partitions, confirm that the benchmark is running on a real
multi-worker cluster.

Recommended progression:

1. single-node or very small cluster for correctness only
2. 1 driver + 2 workers for the first real throughput benchmark
3. 1 driver + 4 workers if you want a better scaling comparison

For example:

- current baseline: one `Standard_D4ds_v5`
- better first throughput test: 1 driver + 2 workers of `Standard_D4ds_v5`

This usually matters more than partition tuning alone.

## Partition guidance for UDF-heavy loads

Once there are real worker executors, start with roughly 2 to 4 partitions per
core across the cluster.

Examples:

- 4 cores total: start around `16`
- 12 cores total: try `24`, then `48`
- 20 cores total: try `40`, then `80`

Do not overfit this rule. The right answer still depends on:

- CRDP latency
- task size
- shuffle behavior
- file layout

But it is a much better starting point than using a tiny partition count on a
multi-worker cluster.

## Best current default with this project

### Internal protect

If a customer has a plaintext table and wants to create a protected table
quickly, the recommended first approach is a compute-cluster `CTAS` or
`INSERT ... SELECT` using the scalar Java protect UDFs.

Example:

```sql
CREATE OR REPLACE TABLE my_catalog.my_schema.plaintext_protected_internal AS
SELECT
  custid,
  name,
  thales_protect_by_column(CAST(address AS STRING), 'char', 'address') AS address,
  thales_protect_by_column(CAST(email AS STRING), 'char', 'email') AS email,
  thales_protect_by_column(CAST(creditcard AS STRING), 'nbr', 'creditcard') AS creditcard
FROM my_catalog.my_schema.plaintext_plaintext;
```

Why this is the best default:

- simple
- easy to explain
- naturally distributed on executors
- good enough for many customer loads
- avoids array batching complexity

### External protect

For external protect, the best current path is the new struct-returning scalar
function:

- `thales_protect_by_column_with_external_header(...)`

That function returns both:

- `protected_value`
- `external_header`

Example:

```sql
INSERT OVERWRITE my_catalog.my_schema.plaintext_protected_external
SELECT
  custid,
  protected_email.protected_value AS email,
  protected_email.external_header AS email_header
FROM (
  SELECT
    custid,
    thales_protect_by_column_with_external_header(CAST(email AS STRING), 'char', 'email') AS protected_email
  FROM my_catalog.my_schema.plaintext_plaintext
) s;
```

This is still distributed across Spark executors even though the UDF itself is
scalar.

## Where the current setup scripts fit

The current setup scripts are designed to be customer-readable and to show the
recommended table shapes and reveal patterns:

- internal protected tables
- external protected tables with sibling `*_header` columns
- cast-back views
- internal and external reveal examples
- array-based reveal examples

They are intentionally more teaching-oriented than maximum-throughput-optimized.

## What to do first for speed

### Recommended default load method

Use:

- a compute cluster
- Java UDFs
- `CREATE TABLE AS SELECT` or `INSERT ... SELECT`
- ordinary Spark partitioning and executor parallelism

This is the best balance of:

- speed
- simplicity
- supportability

### Recommended benchmark method

For pure protect-step tuning, use:

- [internal_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_scalar_object_aware_benchmark.py)

That notebook:

- generates the source table directly in Delta
- avoids ADLS raw-file overhead
- calls the internal high-throughput protect notebook
- records step-level metrics in a persistent Delta table

For full pipeline realism, use:

- [internal_pipeline_end_to_end_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_pipeline_end_to_end_load_test.py)

That notebook includes:

- raw CSV write to ADLS Gen2
- load back into Delta
- protect step

### Very important benchmark nuance

The current scalar benchmark path uses:

- `thales_protect_by_object_and_column(...)`

That looks scalar at the Spark SQL layer, and it is scalar from the notebook
## Diagnostic Notebook Variable Reference

The diagnostic bulk notebook
[internal_bulk_array_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_bulk_array_benchmark.py)
includes several tuning variables. They do not all affect throughput in the
same way, so it helps to separate them into:

- Spark work-shape settings
- grouped bulk-UDF settings
- CRDP request-chunk settings

### Spark work-shape settings

#### `ROW_COUNT`

How many source rows are generated and processed.

Impact:

- increases total work almost linearly
- does not directly set CRDP request size
- larger values are better for stable benchmarks because startup overhead matters less

Use:

- small values for sanity checks
- large values for real throughput tests

#### `GENERATE_PARTITIONS`

How many Spark partitions are used to generate the source Delta table.

Impact:

- affects source-data generation speed
- has little direct effect on CRDP throughput after the source table is written
- too low can underutilize Spark during generation
- too high can add Spark overhead

This mainly affects:

- `generate_source_delta`

#### `TARGET_PARTITIONS`

How many partitions are used before writing the protected target table.

Impact:

- affects Spark task count and output write parallelism
- can slightly affect end-to-end protect timing because flattening and writing are part of the step
- usually is not the main CRDP lever

### Grouped bulk-UDF settings

These settings determine how Databricks shapes the grouped bulk-UDF calls
before the CRDP Java service sees them.

#### `GROUP_SIZE_OVERRIDE`

If set, this directly forces the group size.

Impact:

- controls how many values go into each grouped bulk-UDF call
- this is the clearest knob for controlling request size sent into the CRDP bulk path
- if `GROUP_SIZE_OVERRIDE` is set, it wins over the other grouping settings

Use when:

- you want precise request-size control
- you want predictable Prometheus counts
- you want to test larger or smaller grouped calls directly

#### `GROUP_COUNT_OVERRIDE`

If set, this forces an approximate number of grouped UDF rows by deriving:

- `GROUP_SIZE = ceil(ROW_COUNT / GROUP_COUNT_OVERRIDE)`

Impact:

- controls how many grouped bulk-UDF rows Spark creates
- effectively controls how much independent CRDP work can be in flight
- acts as a parallelism-shaping knob more than a request-size knob

Use when:

- doing executor-scaling experiments
- doing parallelism experiments
- trying to keep grouped work roughly stable across runs
- deliberately changing request fan-out

Not ideal as the general default for:

- tiny sanity-check runs
- simple baseline docs
- cases where `GROUP_SIZE ~= BATCH_SIZE` is all you want

#### `GROUP_SIZE_MULTIPLIER`

Used only when neither override is set. In that case:

- `GROUP_SIZE = BATCH_SIZE * GROUP_SIZE_MULTIPLIER`

Impact:

- lets you scale grouping up or down relative to `BATCH_SIZE`
- easier for simple baseline tuning than a fixed `GROUP_COUNT_OVERRIDE`

Examples:

- `1.0` means `GROUP_SIZE ~= BATCH_SIZE`
- `0.5` means smaller grouped calls and more request fan-out
- `2.0` means larger grouped calls, which may cause CRDP to split them into multiple requests

#### `GROUP_SIZE`

This is the resolved runtime value and is one of the most important things to
watch in the notebook output.

It determines:

- values per grouped bulk-UDF call
- grouped UDF row count
- request fan-out shape

Derived formulas:

- grouped rows ~= `ceil(ROW_COUNT / GROUP_SIZE)`
- expected request count ~= `grouped_rows * protected_columns`
- expected transaction count = `ROW_COUNT * protected_columns`

For the current internal bulk benchmark with 5 protected columns:

- expected requests ~= `grouped_rows * 5`
- expected transactions = `ROW_COUNT * 5`

#### `ESTIMATED_GROUP_COUNT`

Computed as:

- `ceil(ROW_COUNT / GROUP_SIZE)`

Impact:

- estimates how many grouped bulk-UDF rows Spark will process
- is a good proxy for how much independent work can be fed to executors

More grouped rows usually means:

- more Spark and CRDP concurrency potential

Fewer grouped rows usually means:

- larger individual calls
- lower request overhead
- less independent work in flight

### CRDP request-chunk settings

#### `BATCH_SIZE`

This is read from `udfConfig.properties`.

Impact:

- controls the maximum number of values sent in one CRDP `/v1/protectbulk` or `/v1/revealbulk` request
- acts as the CRDP-side chunk ceiling
- only matters when Databricks hands CRDP a list larger than this value

Important:

- actual CRDP request size is roughly `min(GROUP_SIZE, BATCH_SIZE)`

Example:

- if `GROUP_SIZE = 5469` and `BATCH_SIZE = 20000`, the actual request size is about `5469`
- if `GROUP_SIZE = 50000` and `BATCH_SIZE = 20000`, CRDP will split one grouped call into about 3 requests

### Other benchmark labels

#### `CLUSTER_VM_HINT`

This is only a label stored with the metrics so you know which CRDP
environment was used.

Impact:

- no direct runtime effect in the notebook
- very useful for comparing results across CRDP topologies

#### `LOAD_PATTERN`

This is a metrics label that describes the benchmark shape.

Impact:

- no direct runtime effect
- useful for filtering and comparing benchmark runs

### Best way to think about the controls

#### Spark-side work shape

- `ROW_COUNT`
- `GENERATE_PARTITIONS`
- `TARGET_PARTITIONS`

These control:

- how much Spark work exists
- how it is partitioned
- how output is written

#### Databricks grouping shape

- `GROUP_SIZE_OVERRIDE`
- `GROUP_COUNT_OVERRIDE`
- `GROUP_SIZE_MULTIPLIER`

These control:

- how many grouped UDF rows Spark creates
- how many values go into each grouped call
- how much independent CRDP work can be in flight

#### CRDP request chunking

- `BATCH_SIZE`

This controls:

- the maximum values per outbound CRDP request

### Practical performance summary

If you want to increase CRDP request size:

- increase `GROUP_SIZE`
- usually by using `GROUP_SIZE_OVERRIDE`
- as long as it stays below `BATCH_SIZE`

If you want to increase independent work in flight:

- increase grouped row count
- usually by using `GROUP_COUNT_OVERRIDE`

If you want a simple general baseline:

```python
GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0
```

If you want a parallelism experiment:

```python
GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0
```

If you want a fixed request-size experiment:

```python
GROUP_SIZE_OVERRIDE = 10000
GROUP_COUNT_OVERRIDE = None
GROUP_SIZE_MULTIPLIER = 1.0
```
author's perspective. Under the hood, the Java implementation delegates into
the shared bulk service and ultimately calls the CRDP `protectbulk` endpoint.

However, for the scalar path, each row is effectively wrapped into a
single-item list before it reaches the bulk service. That means:

- the benchmark does call `protectbulk`
- but it does not bulk many Spark rows together into large CRDP requests

So `BATCH_SIZE` is technically read and active in the code path, but it is not
the main throughput lever for the scalar benchmark notebook.

This matters when interpreting benchmark results:

- the scalar benchmark is a good baseline for the simple object-aware protect
  design
- it is not the best benchmark for evaluating the impact of large CRDP bulk
  request sizes

If you want to measure where `BATCH_SIZE` and true CRDP bulk behavior matter,
use a dedicated bulk benchmark with:

- grouped arrays of values
- `thales_protect_bulk_by_column(...)`
- explicit flattening back to row form after the bulk call

### What the bulk benchmark throughput actually includes

The bulk benchmark notebook reports end-to-end protect-step throughput, not
pure CRDP service throughput by itself.

For
[internal_bulk_array_benchmark_basic.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_bulk_array_benchmark_basic.py),
the reported `rows_per_second` for `protect_internal_table_bulk` includes the
Spark-side work around the CRDP calls, including:

- grouping rows into arrays
- `collect_list(...)`
- bulk UDF invocation
- flattening arrays back into row form with `posexplode`
- repartitioning and writing the protected Delta target table
- final target row count validation

So if a run reports about `5000 rows/sec`, that should be interpreted as the
overall notebook protect-step throughput for that workload shape.

If each row protects 5 sensitive columns, it is still useful to derive an
approximate protected-value rate:

- `5000 rows/sec * 5 columns = about 25000 protected values/sec`

That derived protected-value rate is often more meaningful than rows/sec alone,
but it still does not imply `25000` individual HTTP requests per second
because CRDP `protectbulk` can process many values in one request.

### Example capacity-planning estimates

Using a current observed single-node-style bulk benchmark result of roughly
`5000 rows/sec`, a `15,000,000` row load would take about:

- `15,000,000 / 5,000 = 3,000 seconds`
- about `50 minutes`

If each row protects 5 sensitive columns, that same baseline is also roughly:

- `25,000 protected values/sec`

The following estimates are useful for planning and conversation, but they are
not guaranteed SLA numbers. Real results will depend on:

- whether the Databricks cluster is truly multi-worker
- CRDP service-side concurrency and CPU headroom
- network latency
- Spark grouping, flattening, and Delta write overhead

| Cluster shape | Approx rows/sec | Approx protected values/sec (5 cols) | Approx time for 15M rows |
|---|---:|---:|---:|
| `1 driver, 0 workers` or effectively single-node | `5,000` | `25,000` | `50 min` |
| `1 driver + 2 workers` | `9,000 - 12,500` | `45,000 - 62,500` | `20 - 28 min` |
| `1 driver + 4 workers` | `15,000 - 22,000` | `75,000 - 110,000` | `11 - 17 min` |
| `1 driver + 8 workers` | `25,000 - 35,000` | `125,000 - 175,000` | `7 - 10 min` |

These ranges assume that:

- the current single-node `5000 rows/sec` result is a fair baseline
- the CRDP service does not become the dominant bottleneck immediately as
  Databricks concurrency increases
- `GROUP_SIZE ~= BATCH_SIZE` remains a reasonable setting

Recommended first validation path:

1. rerun the bulk benchmark on `1 driver + 2 workers`
2. keep the same `BATCH_SIZE` and `GROUP_SIZE` used in the baseline
3. compare rows/sec and protected values/sec
4. only then decide whether larger worker counts or larger `BATCH_SIZE` values
   are worth the extra cost

### Faster but more complex option

For very large internal jobs, a second optimization path is:

- repartition rows
- batch sensitive columns into arrays
- use bulk protect functions
- explode the results back into row form

That can improve throughput because it reduces:

- UDF invocation count
- CRDP call count
- per-row overhead

But it is more complex and is not the best default starting point.

### When `BATCH_SIZE` really matters

`BATCH_SIZE` matters most when the UDF is given many values in one invocation,
for example:

- `thales_protect_bulk(...)`
- `thales_protect_bulk_by_column(...)`
- bulk reveal equivalents

In those flows, the service will chunk the input list into batches of up to
`BATCH_SIZE` values per CRDP `protectbulk` or `revealbulk` request.

In the current property file, use one setting only:

- `BATCH_SIZE=<your chosen test value>`

Reasonable first benchmark values are often:

- `1000`
- `5000`
- `10000`
- `20000`

`BATCH_SIZE` is still a tuning parameter rather than a universally optimal
value. It should be tested against:

- CRDP latency
- request payload size
- executor memory pressure
- network behavior
- error and retry patterns

### External protect caveat

For external protect, the current project supports:

- scalar protect returning a struct with token and header

It does not currently provide:

- a bulk array-of-struct external protect function

So for external protect, the current best path is:

- distributed scalar Spark load
- not array bulk protect

## What should be done differently from the setup scripts

### Internal path

If a customer wants maximum throughput and the dataset is large:

- start with distributed scalar `CTAS`
- only move to array or bulk protect if scalar throughput is not good enough

### External path

For external protect:

- keep the distributed `INSERT ... SELECT` or `CTAS`
- use `thales_protect_by_column_with_external_header(...)`
- persist both token and header columns

This is the cleanest current method.

## Recommendation by use case

### Internal

1. Use a compute cluster, not SQL Warehouse, for the main protection load.
2. Repartition the plaintext source if needed.
3. Use `CREATE TABLE AS SELECT` or `INSERT ... SELECT` with
   `thales_protect_by_column(...)`.
4. Only move to array and bulk protect if throughput is not good enough.

### External

1. Use a compute cluster.
2. Repartition the plaintext source if needed.
3. Use `CREATE TABLE AS SELECT` or `INSERT ... SELECT` with
   `thales_protect_by_column_with_external_header(...)`.
4. Persist both token and header columns.

## Why not jump straight to array and bulk

Array and bulk workflows add:

- batching logic
- flattening logic
- more moving parts
- more troubleshooting complexity

They are useful when needed, but they should usually be treated as an
optimization step rather than the default customer story.

## Customer-ready summary

The fastest practical method today is usually a distributed compute-cluster load
using the Java protect UDFs in a `CTAS` or `INSERT ... SELECT`. Spark handles
parallelism across executors automatically. Bulk and array functions can
improve throughput further, but they add batching complexity and are best
treated as an optimization step, especially since external protect currently
uses the scalar struct-returning function.

## Concrete scripts in this repository

The current repository includes two compute-cluster notebooks that implement
the default high-throughput load patterns described above:

- internal load:
  [internal_scalar_object_aware_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_scalar_object_aware_load.py)
- external load:
  [external_scalar_with_headers_load.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\external_scalar_with_headers_load.py)

It also includes benchmark-oriented notebooks:

- scalar/object-aware protect benchmark:
  [internal_scalar_object_aware_benchmark.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_scalar_object_aware_benchmark.py)
- raw-file realism benchmark:
  [internal_pipeline_end_to_end_load_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_pipeline_end_to_end_load_test.py)
- true bulk-protect benchmark:
  [internal_bulk_array_benchmark_basic.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\internal_bulk_array_benchmark_basic.py)

## Bulk benchmark sizing guidance

For the true bulk-protect benchmark, the best first default is:

- `GROUP_SIZE ~= BATCH_SIZE`

That keeps the Spark-side grouped array size aligned with the CRDP-side chunk
size.

Recommended first comparison:

- `GROUP_SIZE = 0.5 * BATCH_SIZE`
- `GROUP_SIZE = 1.0 * BATCH_SIZE`
- `GROUP_SIZE = 2.0 * BATCH_SIZE`

Why:

- below `BATCH_SIZE`, the service never fills a full CRDP batch
- at `BATCH_SIZE`, each grouped array is a natural one-batch request
- above `BATCH_SIZE`, the service has to split one grouped array into multiple
  CRDP requests, which may or may not help overall throughput

So there is a useful first ratio:

- `GROUP_SIZE : BATCH_SIZE = 1 : 1`

But real tuning still needs measurement. There is no guaranteed universal
winner across different clusters, CRDP deployments, and data shapes.

Both notebooks:

- self-register the required Java UDFs if they are missing in the current
  session
- start with `spark.sparkContext.defaultParallelism` as the first repartition
  setting
- write the protected table using distributed executor-side UDF execution

## Current Best-Known Baseline

Based on the recent benchmark series, a practical current baseline is:

```python
ROW_COUNT = 350_000
GENERATE_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 32)
TARGET_PARTITIONS = max(spark.sparkContext.defaultParallelism * 2, 32)

GROUP_SIZE_OVERRIDE = None
GROUP_COUNT_OVERRIDE = 64
GROUP_SIZE_MULTIPLIER = 1.0
```

And:

- Databricks workers: `4`
- `BATCH_SIZE = 20000`

This should be treated as the default comparison point for future CRDP-side
scaling tests.

## Key Finding

The strongest throughput gains in recent testing came from increasing
**CRDP instance capacity**, not from additional Spark executor tuning.

Directionally, the benchmark series moved from roughly:

- `~5k rows/sec` on a smaller CRDP VM
- to `~15k rows/sec` on a larger CRDP VM
- to `~21k rows/sec` on a larger CRDP VM again

That suggests:

- Databricks executors are being used correctly
- Spark worker count is no longer the primary limiting factor
- CRDP-side compute and concurrency are the dominant tuning domain for this
  workload

## Benchmark Tracking

Use the benchmark matrix template in:

- [BENCHMARK_MATRIX_TEMPLATE.csv](/E:/eclipse-workspace/thales.databricks.udf/docs/BENCHMARK_MATRIX_TEMPLATE.csv)

to track:

- Databricks settings
- CRDP deployment shape
- throughput
- latency and concurrency metrics
- notes about observed bottlenecks

## Prometheus Sanity Checks

For the bulk benchmark, Prometheus request and transaction counts are heavily
influenced by grouping settings.

Important rule:

- `protect_bulk_success_transaction_count` should track total protected values
- `protect_bulk_success_count` should track grouped bulk protect requests

For the current benchmark shape:

- protected columns per row = `5`
- total protected values = `ROW_COUNT * 5`
- grouped row count = `ceil(ROW_COUNT / GROUP_SIZE)`
- expected request count = `ceil(ROW_COUNT / GROUP_SIZE) * 5`

This means a very small run with `GROUP_SIZE = 1` can legitimately produce a
much higher request count than expected at first glance, without implying data
duplication across workers.

See:

- [BULK_UDF_TUNING_CHEAT_SHEET.md](/E:/eclipse-workspace/thales.databricks.udf/notebooks/docs/BULK_UDF_TUNING_CHEAT_SHEET.md)

for concrete examples and recommended settings by run type.

## Recommended test matrix

Use this as a simple next-step plan instead of jumping straight to a huge run.

### Phase 1: correctness

- cluster shape: current cluster
- row count: `10_000`
- target partitions: `16`
- goal: confirm the path works and wait for:
  - `THALES_HIGH_THROUGHPUT_LOAD_FINISHED`
  - `THALES_BENCHMARK_FINISHED`

### Phase 2: first useful benchmark

- cluster shape: current cluster or, preferably, 1 driver + 2 workers
- row count: `100_000`
- target partitions: `16`, then `24`
- goal: compare rows/sec and elapsed time

### Phase 3: scalable benchmark

- cluster shape: 1 driver + 2 workers, then 1 driver + 4 workers
- row count: `1_000_000`
- target partitions:
  - start at `24`
  - then try `48`
- goal: determine whether Spark or CRDP becomes the bottleneck

### Phase 4: optional stress test

- cluster shape: real multi-worker cluster
- row count: `5_000_000` or higher
- target partitions: increase gradually
- goal: evaluate stability, runtime, and cost at larger scale

## How to interpret the benchmark notebook output

The most important completion markers are:

- `THALES_HIGH_THROUGHPUT_LOAD_FINISHED`
- `THALES_BENCHMARK_FINISHED`

If those do not appear, do not trust the timing output.

The benchmark notebook records metrics to:

- persistent table:
  [thales_perf_test_metrics](E:\eclipse-workspace\thales.databricks.udf\notebooks\perf_metrics_helpers.py)
- persistent view:
  `my_catalog.my_schema.v_thales_perf_test_summary`

Important note:

- if a protect run is cancelled early, an old target table may still exist from
  a prior run
- the current notebooks now validate completion and expected row count to avoid
  stale-table false positives


