# Optimized UC Python UDF Memory Guidance

This note explains the optimization used in the optimized SQL Warehouse reveal path for `plaintext_protected_internal`.

Related script:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql](/E:/eclipse-workspace/thales.databricks.udf/sql_warehouse/create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config_optimized.sql)

## What Changed

The original array reveal view used:

- 5 Databricks UC Python UDF calls
- 5 Thales CRDP `revealbulk` calls

The optimized array reveal view uses:

- 1 Databricks UC Python UDF call
- 5 Thales CRDP `revealbulk` calls

So the optimization reduces Databricks SafeSpark/Python invocation overhead, while keeping the same CRDP behavior of one reveal call per protected column.

## Why It Helps

In query profiles, the expensive part was often the Databricks Python UDF execution layer, not just the Delta scan. Bundling the 5 sensitive columns into one UC Python function reduces:

- Python UDF invocation overhead
- SafeSpark request overhead
- repeated serialization/deserialization between SQL and Python

## Tradeoff

The bundled function holds more data in memory in a single Python invocation because it temporarily keeps:

- all bundled input arrays
- all decrypted output arrays
- one JSON payload used to return all arrays back to SQL

That means performance often improves, but memory pressure per UDF invocation is higher.

## Rough Sizing Formula

Use this as a planning estimate:

```text
peak_bytes ~= batch_size * sum(avg_input_bytes_per_col + avg_output_bytes_per_col) * 3
```

Where:

- `batch_size` = number of records stored inside one array batch row
- `avg_input_bytes_per_col` = average token length in bytes for one column
- `avg_output_bytes_per_col` = average revealed plaintext length in bytes for one column
- `* 3` = rough multiplier to loosely account for Python object overhead, JSON overhead, and runtime buffering

This is only an estimate, not an exact memory model.

## Worked Example For `plaintext_protected_internal`

Protected columns in the optimized reveal bundle:

- `address`
- `email`
- `creditcard`
- `creditcardcode`
- `ssn`

Example rough averages:

```text
address       input 20   output 20
email         input 30   output 25
creditcard    input 23   output 16
creditcardcode input 10  output 4
ssn           input 18   output 11
```

Per-row total:

```text
(20+20) + (30+25) + (23+16) + (10+4) + (18+11) = 177 bytes
```

### Example Batch Sizes

Batch size `100`:

```text
100 * 177 * 3 = 53,100 bytes
```

About `52 KB`

Batch size `1,000`:

```text
1,000 * 177 * 3 = 531,000 bytes
```

About `0.5 MB`

Batch size `10,000`:

```text
10,000 * 177 * 3 = 5,310,000 bytes
```

About `5.1 MB`

Batch size `100,000`:

```text
100,000 * 177 * 3 = 53,100,000 bytes
```

About `50.6 MB`

## How To Use This In Practice

1. Estimate typical token length and revealed length for each protected column.
2. Plug those values into the formula.
3. Evaluate a few candidate batch sizes such as `100`, `1000`, and `5000`.
4. Run a representative query and compare the estimate to the Databricks query profile.

## What To Watch In Databricks

When validating the estimate, check the query profile for:

- Python UDF execution time
- number of UDF invocations
- SafeSpark request count
- sandbox peak memory

## Practical Guidance

- Keep batch sizes moderate.
- Use the optimized array view when Python UDF overhead is the main bottleneck.
- If sandbox memory grows too much, reduce batch size before changing the reveal logic.
- If response payloads become very large, consider splitting the workload rather than bundling more columns into the same function.

## Customer-Friendly Summary

The optimized SQL Warehouse reveal path reduces Databricks overhead by combining five UC Python UDF invocations into one bundled invocation. Inside that bundled function, the code still makes one Thales `revealbulk` call per protected column, so the CRDP behavior stays the same. The tradeoff is that more data is held in memory inside one Python call, so batch size should remain reasonable.
