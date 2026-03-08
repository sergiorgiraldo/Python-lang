# Cost Models Reference

Cloud costs are the operating expense of data engineering. These numbers are
approximate, based on 2024 list pricing in us-east-1 (AWS) and us-central1
(GCP). Actual costs depend on reserved capacity, committed use discounts and
negotiated enterprise agreements. Treat these as ballpark figures for
interview estimation.

## Compute Costs

| Service | Unit | Cost | Example |
|---|---|---|---|
| BigQuery (on-demand) | Per TB scanned | $5.00/TB | 10 queries at 100 GB each = $5/day |
| BigQuery (flat-rate) | Per slot-hour | ~$0.04/slot-hour | 100 slots = ~$96/day |
| Snowflake XS | Per credit-hour | $2-4/credit | 1 credit/hr, 8 hrs = $16-32/day |
| Snowflake M | Per credit-hour | $2-4/credit | 4 credits/hr, 8 hrs = $64-128/day |
| Snowflake L | Per credit-hour | $2-4/credit | 8 credits/hr, 8 hrs = $128-256/day |
| Spark (EMR) | Per instance-hour | ~$0.10-0.50/core-hour | 100 cores, 2 hrs = $20-100 |
| Spark (EMR, spot) | Per instance-hour | ~$0.03-0.15/core-hour | 60-90% savings vs on-demand |
| Databricks | Per DBU-hour | ~$0.15-0.40/DBU | 50 DBUs, 2 hrs = $15-40 |
| Lambda | Invocations + duration | $0.20/1M + $0.0000167/GB-sec | 1M at 256 MB, 1 sec = ~$4.37 |
| Fargate | vCPU + memory hours | $0.04/vCPU-hr + $0.004/GB-hr | 4 vCPU, 8 GB, 24 hrs = $4.60/day |

**Interview tip:** Snowflake XS at $2-4/credit with auto-suspend after 5
minutes of inactivity is the common baseline for cost estimation. BigQuery
on-demand at $5/TB scanned is the other. Know both.

## Storage Costs

| Service | Tier | Cost/GB/month | Notes |
|---|---|---|---|
| S3 Standard | Hot | $0.023 | Default for active data |
| S3 Infrequent Access | Warm | $0.0125 | Min 30-day charge, retrieval fee |
| S3 Glacier Instant | Cold | $0.004 | Millisecond retrieval, archival |
| S3 Glacier Deep Archive | Archive | $0.00099 | 12-48 hour retrieval |
| BigQuery (active) | Hot | $0.020 | Queried in last 90 days |
| BigQuery (long-term) | Warm | $0.010 | Not queried in 90+ days, automatic |
| Snowflake | Hot | $0.023-0.040 | Varies by cloud provider and region |
| Delta Lake (on S3) | Hot | S3 pricing | Plus ~5-10% overhead for txn log |
| Iceberg (on S3) | Hot | S3 pricing | Plus metadata overhead (~1-3%) |
| Redis (ElastiCache) | In-memory | ~$3.50/GB/month | r6g.large: 13 GB for ~$45/month |
| DynamoDB | On-demand | $0.25/GB/month | Plus read/write unit costs |

**Storage math shortcut:** 1 TB on S3 Standard = $23/month. 10 TB = $230.
100 TB = $2,300. This scales linearly and is the cheapest durable storage
available. Moving to Glacier after 90 days cuts costs by ~80%.

## Streaming Costs

| Service | Ingress | Per-Unit Cost | Storage |
|---|---|---|---|
| Kafka (MSK) | $0.10/GB in | Broker instance hours | $0.10/GB/month on broker |
| Kafka (MSK Serverless) | $0.10/GB in | $0.01/partition-hour | Included |
| Kinesis Data Streams | $0.015/shard-hour | $0.014/1M PUT payload units | 24h included, 7d: $0.02/shard-hr |
| GCP Pub/Sub | $40/TB ingested | Per-message delivery fee | $0.27/GB/month for 7d+ retention |
| Confluent Cloud | $0.13/GB in | ~$0.11/CKU-hour | Included with broker |

**Interview tip:** Kafka (MSK) at $0.10/GB ingress is easy to estimate. At
10 GB/day ingress, streaming cost is ~$30/month. At 100 GB/day, ~$300/month.
The broker instance cost dominates at low volume. Ingress cost dominates at
high volume.

## Data Transfer Costs

| Path | Cost |
|---|---|
| Into any cloud (internet ingress) | Free |
| Out of AWS to internet | $0.09/GB (first 10 TB/month) |
| Out of AWS to internet | $0.085/GB (next 40 TB/month) |
| Between AWS regions | $0.02/GB |
| S3 to EC2 (same region) | Free |
| S3 to EC2 (cross-region) | $0.02/GB |
| Between clouds (AWS to GCP) | $0.09-0.12/GB |
| CloudFront to internet | $0.085/GB (lower than direct) |

**Hidden cost warning:** Cross-cloud and cross-region transfer adds up fast.
A 10 TB daily sync between AWS and GCP costs 10,000 GB * $0.09 = $900/day
= $27,000/month. This is why multi-cloud architectures need careful cost
analysis. Keep compute and storage in the same region.

## Cost Estimation Worksheet

Use this template during interview estimation or practice:

```
Step 1: Volume
  Daily events:         _____ events/day
  Event size:           _____ bytes average
  Daily raw volume:     _____ GB/day
  Compressed (Parquet): _____ GB/day (raw / 4)
```

```
Step 2: Monthly/Annual Storage
  Monthly new data:     _____ GB * 30 = _____ GB
  Annual new data:      _____ GB * 365 = _____ TB
  Retained data (year 1): _____ TB
```

```
Step 3: Costs
  Storage:   _____ TB * $23/TB/month  = $_____/month
  Compute:   _____ hours * $___/hour  = $_____/month
  Streaming: _____ GB/day * $0.10/GB  = $_____/month
  Queries:   _____ queries * ___ TB * $5 = $_____/month
  Transfer:  _____ GB * $___/GB       = $_____/month

  Total monthly: $_____
  Total annual:  $_____
```

## Common Cost Scenarios

These pre-computed scenarios give you quick reference points for interviews.

| Scenario | Volume | Estimated Monthly Cost |
|---|---|---|
| Small SaaS analytics | 10 GB/day, 5 analysts | $50-150 (BigQuery on-demand) |
| Mid-size event pipeline | 100 GB/day, hourly batch | $500-1,500 (Kafka + Spark + S3) |
| Large streaming pipeline | 1 TB/day, real-time | $3,000-8,000 (Kafka + Flink + warehouse) |
| Enterprise data lake | 10 TB stored, 50 analysts | $500-2,000 (S3 + Snowflake) |
| ML feature store | 500 features, low-latency | $3,000-5,000 (Redis + Spark + Flink) |

These ranges assume standard pricing without reserved instances or committed
use discounts. Enterprise discounts typically reduce costs by 20-40%.
