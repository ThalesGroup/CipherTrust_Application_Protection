# Delta Partitioning Guidance

This note explains how to think about **Delta table partition columns** for
performance in Databricks, and how that differs from Spark execution
partitioning.

## Important distinction

There are two different concepts:

### 1. Spark execution partitions

This is about how Spark splits a job across tasks and executors.

Examples:

- `df.repartition(200)`
- `df.repartition(200, "custid")`

This affects runtime parallelism for UDF jobs.

### 2. Delta table partition columns

This is about the physical layout of a Delta table on disk.

Example:

```sql
CREATE TABLE my_catalog.my_schema.orders_protected (
  ...
)
USING DELTA
PARTITIONED BY (order_date);
```

This affects file layout, pruning, and data skipping behavior.

These are related ideas, but they are not the same thing.

## Current Databricks recommendation

For new Delta tables, Databricks generally recommends:

- **do not use legacy partition columns by default**
- prefer **liquid clustering** when available
- use classic `PARTITIONED BY` only when there is a clear reason

That means for many customer tables, the safest starting point is simply:

```sql
CREATE TABLE my_catalog.my_schema.plaintext_protected_internal (
  ...
)
USING DELTA;
```

and then add clustering or other optimizations only when query patterns justify
them.

## What makes a good Delta partition column

A good Delta partition column is usually:

- low cardinality
- heavily used in filters
- stable over time
- able to create reasonably sized partitions

Typical examples:

- `event_date`
- `ingest_date`
- `business_date`
- `region` in some workloads

## What makes a poor Delta partition column

Poor candidates usually include:

- high-cardinality keys like `custid`, `account_id`, `email`
- timestamps with many distinct values
- protected token columns
- external header columns such as `email_header`
- columns that are rarely filtered

These tend to create:

- too many partitions
- too many small files
- higher write overhead
- more maintenance complexity

## Important rule for protected tables

For tables in this project such as:

- `plaintext_plaintext`
- `plaintext_protected_internal`
- `plaintext_protected_external`

you should generally **not** partition the Delta table by:

- protected columns
- token columns
- header columns

Why:

- they are usually high-cardinality
- they are not good physical partition keys
- they can create inefficient file layout

## What to use instead

### Best modern option

If your Databricks environment supports it, prefer **liquid clustering** for
large important tables.

That lets you optimize layout for query patterns without forcing a rigid legacy
partitioning scheme.

Example:

```sql
CREATE TABLE my_catalog.my_schema.plaintext_protected_internal (
  ...
)
USING DELTA
CLUSTER BY (custid);
```

In practice, choose clustering keys based on:

- actual query filters
- join patterns
- data skipping needs

not just schema intuition.

### Conservative default

If there is no strong need for physical partitioning, keep the table
unpartitioned:

```sql
CREATE TABLE my_catalog.my_schema.plaintext_protected_internal (
  ...
)
USING DELTA;
```

This is often the best first step.

### Legacy partition column example

Use classic `PARTITIONED BY` only when the table is large and the filter column
is a strong low-cardinality candidate.

Example:

```sql
CREATE TABLE my_catalog.my_schema.orders_protected (
  ...
)
USING DELTA
PARTITIONED BY (order_date);
```

## Good rule of thumb

Use a Delta partition column only when all of these are true:

1. The table is large enough to justify it.
2. Queries frequently filter on that column.
3. The column has low or moderate cardinality.
4. The partition count will not explode.

Otherwise:

- leave the table unpartitioned
- prefer liquid clustering if available
- rely on Databricks optimization features

## How this differs from Spark repartitioning

A good Spark repartition key is often a **bad Delta partition column**.

Example:

- `custid` may be a good Spark execution key
- `custid` is usually a bad Delta partition column

Why:

- Spark repartitioning is about spreading runtime work evenly
- Delta partition columns are about physical file layout

So do not assume the same column should be used for both.

## Guidance for multi-column protection workloads

If a table has many columns and several of them require protection, the Delta
partition-column choice should still be based on:

- query filter patterns
- low cardinality
- physical layout needs

not on which columns are being protected.

Even if 5 out of 15 columns are protected, those columns are usually **not**
the right physical partition keys.

## Recommended customer message

For protected Delta tables, do not add partition columns by default. Most of
the time, the better starting point is an unpartitioned Delta table and Spark
execution repartitioning for the protection job itself. If the table becomes
large and query patterns justify physical layout tuning, prefer liquid
clustering when available, and use classic `PARTITIONED BY` only for clear
low-cardinality filter columns such as business dates.

## Lift-and-shift OLTP guidance

Many customers first load raw transactional data from external OLTP systems
before they build facts, dimensions, or data marts. That is still a normal
Databricks pattern.

In those lift-and-shift tables:

- `accountid` or similar keys may repeat across many transactions
- the data may not yet be modeled into normal warehouse structures
- sensitive fields may still be embedded directly in transactional rows

That does **not** change the core Delta partitioning advice very much.

Even if `accountid` repeats, it is still often a poor **legacy Delta partition
column** when it has very high overall cardinality.

So for raw OLTP-style protected tables:

- do not assume a repeating transactional key should become `PARTITIONED BY (accountid)`
- prefer an unpartitioned Delta table first
- if physical layout tuning is needed later, prefer liquid clustering when available
- reserve classic `PARTITIONED BY` for truly low-cardinality filter columns such as:
  - `business_date`
  - `ingest_date`
  - `region`

This leads to an important distinction:

- `accountid` may be a good Spark repartition key for the **protection job**
- `accountid` may still be a poor classic Delta partition column for the **table layout**
