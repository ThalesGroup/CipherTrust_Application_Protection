# Databricks and Thales CRDP FAQ

## What is the recommended deployment model?

Use two patterns depending on workload:

- SQL Warehouse with Unity Catalog Python functions and secured views for BI,
  dashboards, and SQL-centric access
- compute clusters with Java Spark UDFs for high-throughput ETL and batch jobs

## Why do we expose views instead of direct function access?

Views give a cleaner governance boundary. They let Databricks inject
`session_user()` or `current_user()` and prevent end users from passing an
arbitrary reveal username directly.

## Why do some functions use `by_column`?

`by_column` means the caller provides a logical column name such as `email` or
`ssn`, and the policy is resolved from config. This allows one function to
apply different policies to different fields.

## How does a Java Spark UDF such as `ThalesCrdpProtectByColumnUdf` scale across the cluster?

It runs inside Spark tasks on executors, not just on the driver.

Typical flow:

1. register the Java UDF once on the cluster
2. Spark builds a query plan over partitioned data
3. each partition is processed by tasks on executors
4. the UDF is evaluated inside those executor tasks for the rows in that partition

That means tokenization/protection is parallelized across partitions and
executors.

Important nuance:

- `ThalesCrdpProtectByColumnUdf` is scalar and row-oriented, so Spark may call
  it once per row
- for the highest throughput, bulk UDF variants are generally better because
  they process arrays/batches rather than one value at a time

## Why do the legacy functions not use `by_column`?

The legacy functions follow older default-profile behavior and do not take a
column name parameter. They are mainly for backward compatibility.

## Is `COLUMN_PROFILES` table-aware?

No. It is column-name based, not table-name based. If different tables need
different policies for similarly named fields, use more specific logical names
such as `customer_email` and `employee_email`.

## Do end users need direct access to the functions?

Usually no. The recommended pattern is:

- deployers create functions
- deployers create secured views
- consumers get `SELECT` on the views

## How is secure reveal-user handling done?

For SQL Warehouse, the recommended pattern is to inject `session_user()` in a
secured view. For compute clusters, inject `current_user()` or `session_user()`
when calling the Java `*_with_user` UDFs.

## Does the Java code resolve the Databricks user automatically?

Not internally in the same way as Python. The Java path expects the reveal user
to be passed at runtime for secure reveal, or it falls back to config defaults.

## Does the Python code resolve the Databricks user automatically?

It can try to. The Python helper attempts to resolve the user from the active
Spark session or notebook context before falling back to configured defaults.

## What if `spark_session` is not passed to the secure Python API?

The secure Python API still tries to find the active Spark session
automatically. If it cannot, it falls back to notebook-context lookup and then
configured defaults.

## Can a user pass some other username into the secure Python API?

Not through the production-safe entry point. The secure function does not
accept a `reveal_user` parameter, and its non-business parameters are
keyword-only to make positional override attempts fail early.

## Do users see the full Python source code after deployment?

Usually they see the function name and metadata first. For Unity Catalog
functions, metadata commands can show the stored function body, but for the
wheel-backed bulk functions that body is only a short wrapper. The packaged
wheel implementation is separate and generally requires access to the wheel
artifact to inspect directly.

## When should bulk functions be used?

Use bulk functions when the source data is naturally processed in arrays or
batches and the values in that batch use the same resolved protection policy.

## Why can’t all rows be sent in one bulk request?

CRDP v1 bulk calls must use one protection policy per request. That means mixed
profiles cannot be combined into one request.

## What does the array-based view example mean?

It represents a normal table where one column is an `ARRAY<STRING>`. The view
still returns one row per source row, but the revealed output column is also an
array.

## What is the difference between `TEMP VIEW` and `VIEW`?

`TEMP VIEW` exists only for the current Spark session and is best for testing.
`VIEW` is persisted in the metastore and is appropriate for shared governed
access.

## Should grants be applied to functions or views?

For end users, prefer grants on views. Direct function `EXECUTE` should usually
be limited to deployers, admins, or controlled service principals.

## Is calling `current_user()` directly in a notebook secure enough for regular users?

Not as the main governance model. It is acceptable in controlled admin or ETL
contexts, but for regular production users the safer pattern is to expose only
secured views and keep direct `*_with_user` calls out of the supported user path.

## Where should CRDP be deployed?

Close to Databricks in Azure whenever possible. Runtime latency between
Databricks and CRDP matters more than where CipherTrust Manager runs.

## Is detokenization caching supported?

Yes, optionally in the Java bulk service as a bounded executor-local reveal
cache. It can improve repeated reveal workloads, but it stores plaintext in
memory, so it should be enabled intentionally.

## How much memory can the reveal cache use?

The reveal cache is a bounded executor-local in-memory LRU-style cache
implemented with Java `LinkedHashMap`, not an external caching product.

A practical planning estimate is roughly `200 to 500 bytes` per cached entry,
depending on:

- ciphertext length
- plaintext length
- cache-key length
- JVM object overhead

Typical planning range:

- `10,000` entries: about `3 MB to 5 MB` per executor
- `20,000` entries: about `6 MB to 10 MB` per executor
- `50,000` entries: about `15 MB to 25 MB` per executor

Because the cache stores revealed plaintext in memory, memory sizing and
security review should both be part of enablement decisions.

## Is this compatible with DLT or Lakeflow?

Yes, especially through SQL Warehouse or Unity Catalog SQL/Python functions for
SQL-driven pipelines. Compute-cluster Java UDFs fit Spark-driven ETL better.
