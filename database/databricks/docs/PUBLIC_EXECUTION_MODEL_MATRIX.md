# Public Execution Model Matrix

This matrix is intended for external or customer-safe sharing.

It keeps the execution-model recommendations and use-case guidance, but avoids
publishing environment-specific benchmark numbers.

## Matrix

| Path | Best artifact / pattern | Best for | Interactive query experience | Full-processing throughput position | Main tradeoff |
|---|---|---|---|---|---|
| Compute cluster Python helper | `protect_dataframe(...)` / `reveal_dataframe(...)` | Performance-first batch ETL and DataFrame-first pipelines | Not the primary benchmark style | Highest observed throughput position in the current implementation | Less SQL-shaped than direct Spark SQL UDF usage |
| Compute cluster Java UDF | Java scalar/object-aware UDFs | SQL-shaped ETL, CTAS, `INSERT OVERWRITE`, Spark SQL-first jobs | Not the primary benchmark style | Lower than the Python helper path, but still strong for compute-cluster ETL | Less flexible than the helper path for newer multi-policy batching behavior |
| SQL Warehouse optimized governed path | `v_plaintext_final_reveal_flat_uc_embedded_v2_optimized` | Governed SQL, BI tools, shared reveal views, persistent catalog abstractions | Best current governed SQL Warehouse path | Lower than compute-cluster execution for large batch workloads | Higher fixed SQL Warehouse UC Python UDF overhead |
| SQL Warehouse legacy scalar / per-column bulk views | Older scalar/per-column bulk reveal views | Comparison and troubleshooting only | Materially worse than the optimized governed path | Not recommended for throughput-oriented use | Excess Python UDF fan-out |
| Pandas UDF | Scalar Pandas UDFs and `mapInPandas` examples | Customers who specifically want a Pandas execution surface | Not the primary benchmark style | Supported capability, but not the preferred performance-first path | Extra Arrow / pandas execution overhead |

## Recommendation By Use Case

| Use case | Recommended path |
|---|---|
| Highest compute-cluster throughput | Compute cluster Python helper |
| SQL-shaped compute-cluster ETL / CTAS | Compute cluster Java UDF |
| Governed shared SQL abstraction | SQL Warehouse optimized governed path |
| Customer requirement for Pandas API support | Pandas UDF |

## Important Notes

- Performance always depends on cluster size, SQL Warehouse size, runtime
  version, source data shape, and protected-column mix.
- The SQL Warehouse optimized governed path is the recommended SQL-facing
  design, but it should not be positioned as the throughput-first option for
  large-scale batch processing.
- The Pandas path is supported, but should be positioned as a compatibility/API
  surface rather than the primary performance recommendation.
