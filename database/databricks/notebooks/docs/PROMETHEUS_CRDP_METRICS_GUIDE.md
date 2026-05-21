# Prometheus CRDP Metrics Guide

This guide explains how to interpret the CRDP Prometheus metrics currently exposed by the service, which PromQL queries are most useful for benchmarking, and what to use for autoscaling and bottleneck analysis.

## Available CRDP business metrics

The most useful CRDP workload metrics currently exposed are:

- `protect_bulk_success_count`
- `protect_bulk_success_transaction_count`
- `protect_bulk_failure_count`
- `protect_bulk_failure_transaction_count`
- `protect_success_count`
- `protect_failure_count`
- `reveal_bulk_success_count`
- `reveal_bulk_success_transaction_count`
- `reveal_bulk_failure_count`
- `reveal_bulk_failure_transaction_count`
- `reveal_success_count`
- `reveal_failure_count`

These are more useful for workload analysis than the Prometheus scrape metrics:

- `promhttp_metric_handler_requests_in_flight`
- `promhttp_metric_handler_requests_total`

Those `promhttp_*` metrics describe scraping of the metrics endpoint itself, not CRDP protect or reveal business traffic.

## What the bulk protect metrics mean

For bulk protect benchmarking:

### `protect_bulk_success_count`

This counts successful bulk protect API requests.

Use it to understand:

- how many successful CRDP bulk requests were served
- request fan-out
- whether Databricks grouping created many small requests or fewer larger requests

### `protect_bulk_success_transaction_count`

This counts the successful values processed inside those bulk requests.

Use it to understand:

- how much real protect work CRDP completed
- workload throughput
- effective values processed per second

### `protect_bulk_failure_count`

This counts failed bulk protect API requests.

Use it to understand:

- request-level failures
- reliability issues
- whether overload or instability is starting to appear

### `protect_bulk_failure_transaction_count`

This counts failed values inside bulk protect requests.

Use it to understand:

- how much actual business work failed
- whether failures are small isolated request failures or larger workload-impacting failures

## Most useful PromQL queries

## Throughput

### Successful values per second

This is usually the best current throughput metric for bulk protect:

```promql
rate(protect_bulk_success_transaction_count[5m])
```

Use it for:

- steady-state throughput
- deployment comparison
- observing whether CRDP scaling actually increases completed work

### Successful bulk requests per second

```promql
rate(protect_bulk_success_count[5m])
```

Use it for:

- request-rate analysis
- request fan-out
- checking whether grouping changes caused a large increase in request volume

### Count over a fixed window

For clean benchmarking windows, these are also useful:

```promql
increase(protect_bulk_success_transaction_count[5m])
increase(protect_bulk_success_count[5m])
```

Use `increase(...)` when you want:

- total completed values during the run
- total successful requests during the run

Use `rate(...)` when you want:

- per-second behavior
- autoscaling observation
- steady-state comparisons

## Efficiency

### Average values per successful bulk request

This is one of the most useful derived calculations:

```promql
rate(protect_bulk_success_transaction_count[5m])
/
rate(protect_bulk_success_count[5m])
```

This shows the average number of values processed per successful bulk request.

Interpretation:

- higher value usually means larger, more efficient bulk requests
- lower value usually means smaller requests and more request overhead

This is a very good way to validate the impact of:

- `GROUP_SIZE_OVERRIDE`
- `GROUP_COUNT_OVERRIDE`
- `BATCH_SIZE`

## Reliability

### Failed requests per second

```promql
rate(protect_bulk_failure_count[5m])
```

### Failed values per second

```promql
rate(protect_bulk_failure_transaction_count[5m])
```

### Request failure ratio

```promql
rate(protect_bulk_failure_count[5m])
/
(
  rate(protect_bulk_success_count[5m])
  +
  rate(protect_bulk_failure_count[5m])
)
```

### Transaction failure ratio

```promql
rate(protect_bulk_failure_transaction_count[5m])
/
(
  rate(protect_bulk_success_transaction_count[5m])
  +
  rate(protect_bulk_failure_transaction_count[5m])
)
```

The transaction failure ratio is often more meaningful than the request failure ratio because it reflects failed values, not just failed requests.

## Distribution across replicas

If Prometheus includes `pod` or `instance` labels, use:

```promql
rate(protect_bulk_success_transaction_count[5m]) by (pod)
```

or:

```promql
rate(protect_bulk_success_transaction_count[5m]) by (instance)
```

Also useful:

```promql
rate(protect_bulk_success_count[5m]) by (pod)
```

Use these for:

- checking whether traffic is distributed evenly
- spotting hot replicas
- validating load balancer behavior

## What to use for autoscaling

## Best current autoscaling signal from existing CRDP metrics

With the metrics currently exposed, the best autoscaling-oriented workload metric is usually:

```promql
rate(protect_bulk_success_transaction_count[2m])
```

Why:

- it measures completed work, not just request count
- it is less sensitive to request fan-out than `protect_bulk_success_count` alone

But this is still not a perfect autoscaling signal because it measures **completed** work, not waiting work.

If CRDP becomes saturated, completion rate can flatten rather than showing how much demand is building.

## Secondary autoscaling signals

Also observe:

- pod CPU
- pod memory
- failure ratios

If using AKS:

- HPA can scale from CPU and memory
- KEDA can scale from Prometheus metrics

The stronger model for this workload is usually:

- KEDA using Prometheus-backed CRDP metrics
- AKS cluster autoscaler for nodes
- CPU as a secondary confirmation signal

## Best future CRDP metrics to add

If CRDP metrics can be extended later, the most useful additions would be:

- active or in-flight business requests
- request queue depth
- request latency p50/p95/p99

Those are better autoscaling triggers than completion counters alone.

## Bottleneck interpretation

## 1. Throughput flatlines while demand rises

If Databricks is sending more work, but:

```promql
rate(protect_bulk_success_transaction_count[5m])
```

stops rising, that suggests a CRDP-side ceiling.

Possible causes:

- queueing
- thread-pool saturation
- connection-pool saturation
- internal batching or serialization limits
- uneven request distribution across replicas

## 2. Average values per request drops

If this metric falls:

```promql
rate(protect_bulk_success_transaction_count[5m])
/
rate(protect_bulk_success_count[5m])
```

it usually means CRDP is receiving smaller requests.

Possible causes:

- smaller Databricks group size
- more grouped-row fan-out
- less efficient batching

This often increases request overhead even if total business work is unchanged.

## 3. CPU looks fine but throughput still flattens

This usually means the bottleneck is not simple host saturation.

More likely causes include:

- queueing
- request concurrency limits
- connection management overhead
- application-level locking or serialization

This is why CPU-only autoscaling is usually not enough for CRDP-heavy bulk loads.

## 4. One replica is much hotter than others

If:

```promql
rate(protect_bulk_success_transaction_count[5m]) by (pod)
```

shows uneven work distribution, possible causes include:

- load balancer imbalance
- sticky traffic behavior
- uneven pod readiness or performance

## 5. Failure rate rises before throughput improves

If failure counters rise while completed transactions do not increase meaningfully, this suggests overload or instability rather than productive scaling.

## Practical dashboard recommendations

A useful CRDP dashboard should include:

### Load

- `rate(protect_bulk_success_transaction_count[5m])`
- `rate(protect_bulk_success_count[5m])`
- average values per request

### Reliability

- request failure ratio
- transaction failure ratio

### Distribution

- throughput by pod
- request rate by pod

### Platform

- CPU by pod
- memory by pod
- restarts
- node pressure

## Short recommended query set

For bulk protect benchmarking, these are the most useful starting queries:

```promql
rate(protect_bulk_success_transaction_count[5m])
rate(protect_bulk_success_count[5m])
rate(protect_bulk_success_transaction_count[5m]) / rate(protect_bulk_success_count[5m])
rate(protect_bulk_failure_count[5m]) / (rate(protect_bulk_success_count[5m]) + rate(protect_bulk_failure_count[5m]))
rate(protect_bulk_success_transaction_count[5m]) by (pod)
```

## Bottom line

With the current CRDP metrics:

- use `protect_bulk_success_transaction_count` as the main throughput signal
- use `protect_bulk_success_count` to understand request fan-out
- use derived ratios to evaluate efficiency and reliability
- use replica-level grouping to validate load distribution
- do not use `promhttp_*` metrics for business autoscaling

For autoscaling:

- current best available signal is completed transactions per second
- CPU is a useful supporting metric
- the best long-term CRDP autoscaling signals would be active requests, queue depth, and latency
