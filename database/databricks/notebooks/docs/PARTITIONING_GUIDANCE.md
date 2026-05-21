# Partitioning Guidance

This note explains how to think about Spark partitioning for Databricks
compute-cluster UDF workloads in this project.

## Two meanings of partitioning

There are two different concepts that are easy to mix together:

### 1. Spark execution partitions

These are the partitions Spark uses to split work across tasks and executors
for a job.

Examples:

- `df.repartition(8)`
- `df.repartition(200, "custid")`

This is the main partitioning concept that matters for Java UDF execution
parallelism.

### 2. Delta table partition columns

These are physical storage layout choices such as:

```sql
PARTITIONED BY (state)
```

That is a different topic. It affects how Delta stores files, but it is not the
same thing as how Spark splits a particular UDF job into execution tasks.

This note focuses on Spark execution partitions.

## What `repartition(...)` means

### `repartition(n)`

Example:

```python
df.repartition(200)
```

This tells Spark to shuffle the data and create `200` execution partitions.

No specific key is used. Spark just redistributes rows across the requested
number of partitions.

This is often a good default when:

- no single column is clearly a good distribution key
- candidate columns are skewed
- you mainly want even task parallelism

### `repartition(n, "column")`

Example:

```python
df.repartition(200, "custid")
```

This tells Spark to hash on `custid` and distribute rows into `200`
partitions based on that key.

This is useful when the chosen column has good distribution characteristics.

## Should the partitioning column be one of the protected columns

Not necessarily.

Usually the best partitioning column is:

- high-cardinality
- evenly distributed
- stable
- mostly non-null

That is often a business key such as:

- `custid`
- `account_id`
- `order_id`
- a surrogate row key

It does not need to be one of the columns being protected.

In many cases, a row key is a better partitioning key than a protected column.

## What makes a good partitioning column

Good characteristics:

- many distinct values
- no large hot spots
- fairly even distribution
- present on most or all rows
- stable across reruns

Poor characteristics:

- low cardinality like `state`, `status`, `country`
- many nulls
- one or two dominant values
- strong skew

## What if the dataset has many repeating values

If many rows share the same value for a candidate key, Spark can end up with
skewed partitions.

Examples of risky choices:

- `state`
- `customer_status`
- `active_flag`

In those cases, a safer starting point is often:

```python
df.repartition(200)
```

instead of partitioning by a weak column.

If a good high-cardinality key exists, prefer:

```python
df.repartition(200, "custid")
```

## What if multiple columns are being protected

If a table has many columns and several of them need protection, the
partitioning choice should still be based on row distribution, not on which
individual columns are protected.

For example, if a table has 15 columns and 5 require protection, the goal is
still:

- spread rows evenly across tasks
- avoid skew
- keep executors busy

So the partitioning key is usually chosen from:

- primary key
- surrogate key
- account or customer identifier
- another well-distributed row-level key

not from whichever protected column happens to be most visible.

## Practical starting guidance

### Best default if you have a good key

Use:

```python
df.repartition(200, "custid")
```

### Best default if you do not trust any column distribution

Use:

```python
df.repartition(200)
```

### If one column is too skewed

Consider:

- a different key
- multiple columns
- or plain `repartition(n)` without a key

## About the partition verification notebook

The notebook:

- [spark_partition_verification.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\spark_partition_verification.py)

uses:

```python
.repartition(TARGET_PARTITIONS)
```

That is a simple demo choice.

It is not saying:

- the protected column should be the partition key
- or that the workload must always repartition without a key

It is only forcing multiple execution partitions so the Spark UI is easy to
read during a demo.

## Recommended customer message

For Databricks UDF workloads, partitioning is usually about spreading rows
evenly across Spark tasks, not about choosing one of the protected columns.
A good partitioning key is typically a high-cardinality business key such as
`custid` or `account_id`. If no single column distributes well, using
`repartition(n)` without a column is often a better starting point than using
a low-cardinality skewed column.

## Lift-and-shift OLTP guidance

Many customers first land raw transactional data from legacy OLTP systems
before building facts, dimensions, or data marts. That is still a normal
Databricks use case.

In that kind of table:

- sensitive values may still sit in transactional rows
- business keys like `accountid` may repeat often
- the model may not yet be a dimensional warehouse design

For **Spark execution repartitioning**, repeating transactional keys can still
be reasonable partitioning candidates if:

- there are many distinct keys overall
- the data is not dominated by a tiny number of accounts
- the resulting task distribution is reasonably even

So for raw OLTP-style protection jobs:

- `repartition(n, "accountid")` can be a good choice when `accountid`
  distributes work well
- `repartition(n)` is safer if `accountid` is heavily skewed or uncertain

The key point is:

- repeating values do not automatically make a column a bad Spark repartition key
- what matters is whether the rows spread evenly enough across tasks

