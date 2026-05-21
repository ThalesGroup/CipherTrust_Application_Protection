# Architecture Recommendation

This guide summarizes the current architecture recommendation for Databricks plus CRDP based on the benchmark patterns observed in this repository.

It is intentionally focused on deployment direction, scaling behavior, and production guidance rather than on individual benchmark numbers.

## Main conclusion

For the workloads tested here, **CRDP capacity and topology matter more than further Databricks tuning once Spark executors are already being used effectively**.

The practical takeaway is:

- do not keep over-optimizing Databricks knobs once the job shape is stable
- treat CRDP deployment shape as the main architecture decision
- design production scaling around CRDP concurrency, latency, and availability

## What the benchmark results suggest

The observed benchmark pattern supports a few consistent conclusions:

- a larger single CRDP deployment and a multi-instance CRDP deployment can land in a similar performance class
- horizontal scaling helps, but it is not linear
- a single larger CRDP deployment can be more compute-efficient than many smaller replicas
- multiple replicas are still the better production direction when availability and scaling flexibility matter

The important lesson is not a single rows-per-second number. The important lesson is that **combined CPU and memory available to CRDP, plus how that capacity is packaged, are major throughput drivers**.

## What seems to matter most for CRDP performance

The likely leading factors are:

- how much concurrent request work CRDP can sustain
- total CPU available to CRDP
- total memory available to CRDP
- per-request latency
- how many independent grouped calls Databricks can keep in flight
- request and connection overhead across replicas

This also explains why platform metrics can look healthy even when throughput flattens. The limiting behavior may come from service-level concurrency and queueing rather than obvious resource exhaustion.

Examples of likely service-level ceilings include:

- request queueing
- thread-pool saturation
- connection-pool saturation
- application-level serialization
- internal batching limits
- uneven request distribution across replicas

## Recommended starting point

### For performance benchmarking

Start with a **single larger CRDP deployment** when the goal is to establish a clean single-environment throughput baseline.

Why:

- simplest topology
- easiest to reason about
- good way to measure the practical ceiling of one CRDP instance

### For production

Start with a **small number of medium or large CRDP replicas**, not one tiny instance and not many very small replicas.

A practical starting pattern is:

- `2` or `3` medium/large CRDP replicas
- one shared private endpoint
- internal load balancing
- warm minimum replica count
- autoscaling based on application metrics

Why:

- good balance of throughput and availability
- better scaling path than one large box
- less overhead and less operational fragility than many small replicas

## Deployment guidance by use case

| Use case | Recommended CRDP topology | Why | Tradeoff | When to move to multi-job ingestion |
|---|---|---|---|---|
| Functional POC | Single CRDP instance or small shared CRDP environment | Fastest to stand up and easiest to validate end-to-end behavior | Not the best basis for final performance or HA conclusions | Only if runtime becomes too slow for the POC objective |
| Performance benchmarking | One larger CRDP instance or equivalent larger container allocation | Cleanest way to measure single-environment throughput | Less resilient than a production multi-replica design | When one tuned job still misses the target runtime |
| Production steady load | `2` to `3` medium/large CRDP replicas behind one private endpoint | Good balance of throughput, efficiency, and availability | More platform complexity than a single VM | When one tuned job is stable but SLA still needs more throughput |
| Production bursty load | AKS with warm minimum replicas and autoscaling | Better fit when multiple jobs may overlap and demand varies | Requires Prometheus, KEDA, and AKS operational tuning | When static sizing is either too expensive or too slow |
| High availability in one region | Multiple CRDP replicas spread across nodes or zones | Better fault tolerance than one large instance | Slightly more overhead than a single larger deployment | When uptime matters as much as raw throughput |
| Multi-region / DR | Separate AKS environments per region | Better fit for region-level continuity planning | Highest complexity and cost | When business continuity requires regional resilience |
| Very large bulk loads with strict SLA | Shared AKS-hosted CRDP environment plus multiple concurrent Databricks jobs | Parallel jobs become a stronger lever than more micro-tuning of one job | Requires concurrency validation so jobs do not interfere badly | When single-job tuning has flattened and runtime is still too long |

## AKS production direction

For production, the preferred direction is **AKS**, not a long-term single-VM pattern.

Recommended model:

- use a small number of medium/large CRDP replicas
- keep a warm minimum replica count
- scale pods from CRDP application metrics
- let AKS scale nodes when pods need more capacity

Within one region:

- multiple CRDP replicas
- private ingress or internal load balancing
- spread across nodes or zones where possible

Across regions:

- separate AKS environments per region
- independent regional capacity planning
- treat multi-region as a DR or active-active decision, not just "more pods"

## Shared CRDP environment for split-file or multi-job ingestion

For very large loads, multiple Databricks jobs can target the **same logical CRDP service endpoint** while AKS scales the CRDP pods behind that endpoint.

The pattern is:

- split a large file into multiple partitions or files
- run multiple Databricks jobs
- point all jobs to the same CRDP service hostname
- let the service or load balancer distribute requests across pods
- let AKS scale the backend as load rises

This is usually the most natural production model, but it works well only if a few conditions are true.

### Conditions for a shared autoscaled CRDP environment

1. CRDP must scale safely as multiple replicas

- stateless enough for replicated operation
- no hidden single-node bottleneck
- no shared dependency that collapses under concurrency

2. Autoscaling must be tuned well

- do not rely on scale-from-zero for this workload
- keep warm replicas
- scale on good application signals

3. Concurrent-job behavior must be validated

- do not assume "one job works" means "four jobs will also work well"
- test the concurrency curve explicitly

Recommended validation pattern:

- `1` concurrent job
- `2` concurrent jobs
- `4` concurrent jobs

## Why warm replicas matter

Autoscaling helps, but it is not instantaneous.

If multiple jobs start at once and the CRDP backend is initially undersized, the early part of the burst may still queue or flatten before autoscaling catches up.

That is why the recommended production model includes:

- a non-zero `minReplicaCount`
- enough warm baseline capacity for expected bursts
- not relying only on reactive scaling

## Recommended autoscaling model

The best scaling model for this workload is usually:

- **KEDA** for pod autoscaling
- **Prometheus-backed CRDP metrics** for primary scaling signals
- **AKS cluster autoscaler** for node scaling

Think of it as two scaling loops.

### Pod scaling

With the metrics currently exposed by CRDP, KEDA would typically watch Prometheus-derived workload counters such as:

- completed bulk transactions per second
- completed bulk requests per second
- failure ratios

KEDA then adjusts the CRDP Deployment replica count.

### Node scaling

If the cluster does not have enough room for the additional pods:

- AKS cluster autoscaler adds nodes to the node pool

## What to scale on

With the metrics currently available from CRDP, the best current autoscaling-oriented signal is usually:

- completed bulk transactions per second

Derived from:

- `rate(protect_bulk_success_transaction_count[2m])`

Useful supporting signals are:

- completed bulk requests per second
- request failure ratio
- transaction failure ratio
- CPU

Why this is the best current option:

- it measures actual work completed
- it is less sensitive to request fan-out than request count alone
- it maps better to true bulk-load throughput than scrape or platform metrics

Important limitation:

- this is still a completion metric, not a waiting-work metric
- if CRDP is saturated, completion rate may flatten rather than clearly showing rising demand

Best future signals to add in CRDP if possible:

- active or in-flight business requests
- request queue depth
- latency

Why not CPU-only:

- throughput ceilings can appear without obvious VM distress
- CPU can lag the real application bottleneck
- queueing and concurrency are often better indicators for CRDP than raw CPU alone

## Practical autoscaling starting pattern

A practical starting model is:

- `minReplicaCount > 0`
- often `2` warm replicas to start
- moderate `maxReplicaCount`
- scale from Prometheus metrics first
- use CPU as supporting evidence, not the only trigger

The key idea is:

- AKS captures platform metrics like CPU and memory
- Prometheus captures CRDP application metrics
- KEDA uses those richer CRDP metrics to drive pod scaling

## Metrics that matter most

To compare one larger CRDP deployment versus multiple smaller replicas, the most useful metrics are not just raw throughput.

### Metrics available from CRDP today

Per CRDP instance or pod, the most useful currently exposed metrics are:

- successful bulk requests per second
- successful bulk transactions per second
- failed bulk requests per second
- failed bulk transactions per second
- average values per successful bulk request

These come from counters such as:

- `protect_bulk_success_count`
- `protect_bulk_success_transaction_count`
- `protect_bulk_failure_count`
- `protect_bulk_failure_transaction_count`

Useful derived calculations include:

- values per second
- requests per second
- average values per successful request
- request failure ratio
- transaction failure ratio

Across replicas:

- requests by replica
- transactions by replica
- CPU by replica
- whether traffic is distributed evenly

### Platform metrics to pair with CRDP counters

Because CRDP does not currently expose rich latency or queue-depth metrics, pair the CRDP counters with platform metrics such as:

- pod CPU
- pod memory
- pod restarts
- node pressure

### Metrics not currently exposed by CRDP but still worth adding later

If CRDP metrics can be enhanced, the most useful additions would be:

- active or in-flight business requests
- p50, p95, and p99 request latency
- queue depth
- heap usage and GC behavior
- connection-pool usage

Important decision metrics:

- throughput relative to total CPU and memory
- throughput relative to cost
- steady-state behavior under sustained load
- behavior when one replica disappears

These tell more than a single peak rows-per-second result.

## Databricks guidance

Once the workload shape is stable and executors are clearly being used, keep the Databricks side reasonably steady.

That usually means:

- stable worker count
- stable partitioning and grouping pattern
- avoid repeated micro-tuning unless there is evidence Spark is still the bottleneck

The main benchmark notebook settings can remain the basis for repeatable comparison runs, but the architecture decision should move toward CRDP deployment shape rather than endless Spark tuning.

## Guidance for very large bulk loads

For bulk ingestion, keep using one tuned job when:

- one job already meets the SLA
- CRDP throughput is stable
- operational simplicity matters more than squeezing out the last margin of performance

Move toward multiple concurrent jobs when:

- single-job throughput has stabilized across repeated tests
- CRDP-side tuning yields only small gains
- the runtime still misses the SLA
- the data can be partitioned cleanly
- the CRDP environment has enough horizontal capacity for overlap

At some point, **parallel files and multiple jobs become a stronger lever than trying to perfect one single-job configuration**.

## Simple recommendation statement

For production, a small number of medium/large CRDP replicas in AKS is the best general starting point. It gives better availability and scaling behavior than a single box while avoiding the inefficiency of too many small replicas.

For very large loads, the preferred long-term model is usually:

- one shared AKS-hosted CRDP service
- warm baseline replicas
- autoscaling from CRDP application metrics
- multiple Databricks jobs only after concurrency behavior has been validated

## Bottom line

The current recommendation is:

- do not keep over-optimizing Databricks knobs once the job shape is stable
- treat CRDP deployment shape as the main architecture decision
- start with enough combined CPU and memory to place CRDP in the right performance class
- prefer a small number of medium/large CRDP replicas over many tiny ones
- use AKS for production-scale availability and scaling
- use Prometheus plus KEDA for CRDP-aware autoscaling
- move to concurrent multi-job ingestion when the single-job tuning curve has flattened
