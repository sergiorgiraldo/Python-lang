# Throughput and Latency Reference

These numbers are approximate and configuration-dependent. They are meant for
back-of-envelope estimation during interviews, not production capacity
planning. When in doubt, round to the nearest power of 10.

All figures assume typical configurations as of 2024. Your mileage will vary
with hardware, tuning and workload characteristics.

## Message Brokers

| System | Throughput | Latency | Max Message | Notes |
|---|---|---|---|---|
| Kafka (per partition) | 1M msgs/sec (small msgs) | 2-10ms | 1 MB default | Scales linearly with partitions |
| Kafka (per broker) | 100 MB/sec sustained | 2-10ms | Configurable | Compressed, single broker |
| Kinesis (per shard) | 1 MB/sec or 1K records/sec | 200ms-1s | 1 MB | Scales with shard count |
| GCP Pub/Sub | 200 MB/sec per topic | 10-100ms | 10 MB | Auto-scales, no partitioning to manage |
| RabbitMQ | 30K msgs/sec per node | <1ms | No hard limit | Single node, small-to-moderate scale |
| AWS SQS | Unlimited (with batching) | 1-10ms | 256 KB | Serverless, no provisioning |
| Redpanda | 1M+ msgs/sec/node | <10ms | Configurable | Kafka-compatible, no JVM/ZooKeeper |

**Interview shorthand:** Kafka handles 1M small messages/sec per partition.
Kinesis handles 1K records/sec per shard. These two numbers cover most
estimation scenarios.

## Processing Engines

| System | Throughput | Latency | Memory | Notes |
|---|---|---|---|---|
| Spark (batch) | ~1 TB/hour typical | Minutes to hours | 1-8 GB/executor | Varies with shuffle and I/O |
| Spark Structured Streaming | ~100K events/sec | 100ms-seconds | Similar to batch | Micro-batch model |
| Flink | ~1M events/sec/TaskManager | <100ms per event | 1-8 GB/TM | True streaming, event-at-a-time |
| dbt (on BigQuery) | Depends on warehouse | Minutes | N/A | SQL-based, warehouse does compute |
| Pandas | ~1M rows/sec in-memory ops | N/A | Must fit in RAM | Single machine, row-oriented |
| Polars | ~10M rows/sec in-memory ops | N/A | Must fit in RAM | Single machine, columnar |
| DuckDB | ~100M rows/sec analytical | Milliseconds | Must fit in RAM | Single machine, columnar, OLAP |

**Key insight:** Spark batch at 1 TB/hour means a 6-hour batch window handles
6 TB. Most companies process far less than this nightly. If your total data
is under 1 TB, Spark may be overkill.

## Databases and Warehouses

| System | Write Throughput | Read Throughput | Latency | Notes |
|---|---|---|---|---|
| PostgreSQL | ~10K TPS | ~10K QPS | 1-10ms | OLTP, single node |
| MySQL | ~10K TPS | ~10K QPS | 1-10ms | OLTP, single node |
| BigQuery | Load jobs (batch) | ~100 GB/slot/hour scan | 1-30s | Serverless columnar |
| Snowflake | COPY INTO (batch) | Varies by warehouse size | 1-30s | Auto-scale compute |
| Redis | ~100K ops/sec | ~100K ops/sec | <1ms | In-memory key-value |
| DynamoDB | 25K WCU default | 25K RCU default | <10ms | Serverless, on-demand scaling |
| Cassandra | ~50K writes/sec/node | ~10K reads/sec/node | 1-10ms | Wide-column, write-optimized |
| ClickHouse | ~100K rows/sec insert | ~100M rows/sec scan | 10-100ms | Columnar analytics |

**Interview shorthand:** OLTP databases handle ~10K TPS. Redis handles ~100K
ops/sec. Warehouses process queries in seconds, not milliseconds. These
baselines help you judge whether a design needs caching, sharding or a
different storage tier.

## Object Storage

| System | Read Throughput | Write Throughput | Latency | Cost/GB/month |
|---|---|---|---|---|
| S3 | 5 GB/sec per prefix | 3.5K PUTs/sec per prefix | 10-100ms first byte | $0.023 |
| GCS | Similar to S3 | Similar to S3 | Similar | $0.020 |
| Azure Blob | Similar to S3 | Similar to S3 | Similar | $0.018 |

S3 throughput scales with prefix count. For high-throughput workloads, use
randomized prefixes or date-partitioned paths to distribute requests across
multiple prefixes. A single prefix hitting 3.5K PUTs/sec is the bottleneck,
not S3 overall.

## Network

| Path | Latency | Bandwidth |
|---|---|---|
| Same datacenter | ~0.5ms | 10+ Gbps |
| Same region, different AZ | 1-2ms | 5 Gbps |
| Cross-region (US East to US West) | 40-70ms | 1-5 Gbps |
| Cross-continent (US to Europe) | 80-150ms | 100 Mbps - 1 Gbps |
| S3 to EC2 (same region) | 1-5ms | 10+ Gbps |

**Key takeaway for interviews:** Same-region network latency is ~1ms with
high bandwidth. Cross-region adds 40-70ms. Cross-continent adds 80-150ms.
These numbers drive decisions about data locality and replication strategy.

## Compression Ratios

| Format | Compression vs Raw CSV | Notes |
|---|---|---|
| Parquet + Snappy | ~3:1 | Default for most analytics workloads |
| Parquet + ZSTD | ~5:1 | Better ratio, slower read/write |
| Parquet + Gzip | ~4:1 | Good compatibility, moderate speed |
| JSON (gzipped) | ~5-8:1 vs raw JSON | Common for log ingestion |
| Avro + Snappy | ~2-3:1 vs raw JSON | Row-oriented, good for streaming |

**Interview shorthand:** Parquet is roughly 4x smaller than raw CSV/JSON.
Use this ratio for storage estimation: 100 GB/day raw becomes ~25 GB/day
compressed Parquet.

## Quick Estimation Cheat Sheet

| Question | Shortcut |
|---|---|
| Events/sec from events/day | Divide by 86,400 (~100K) |
| Peak from average | Multiply by 3-5x |
| Raw to compressed Parquet | Divide by 4 |
| JSON to Parquet | Divide by 5-8 |
| GB/day to TB/year | Multiply by 0.365 |
| Monthly S3 cost from TB | Multiply by $23 |
| Seconds in a day | 86,400 (~10^5) |
| Seconds in a year | ~31.5M (~3 * 10^7) |
