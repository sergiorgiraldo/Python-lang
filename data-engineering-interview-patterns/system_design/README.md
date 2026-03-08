# System Design for Data Engineering Interviews

## What This Section Is

Frameworks and patterns for data engineering system design interviews. This is
light-touch reference material for 45-minute interview rounds, structured to
help you think and communicate clearly under pressure.

This is **not** a comprehensive system design textbook. You will not find
exhaustive deep-dives into every technology or architecture. Instead, you will
find repeatable frameworks, concrete numbers and practical patterns that let you
walk into a system design round with a clear approach.

The goal: when the interviewer says "Design a real-time analytics pipeline,"
you have a structured way to reason through the problem, make defensible
tradeoff decisions and communicate your thinking clearly.

## How DE System Design Differs from Backend System Design

Backend system design and data engineering system design share common ground but
emphasize different concerns.

**Backend system design focuses on:**
- API design and request routing
- Load balancing and horizontal scaling
- Caching strategies (Redis, CDN, application-level)
- Database sharding and replication
- Availability and latency SLAs (99.9% uptime, p99 < 200ms)

**Data engineering system design focuses on:**
- Data pipeline architecture (ingestion, transformation, serving)
- Storage format selection (Parquet, Avro, Delta Lake, Iceberg)
- Ingestion patterns (batch, streaming, CDC, API polling)
- Data modeling for analytical workloads (star schema, OBT, Data Vault)
- Cost optimization (compute spend, storage tiering, query efficiency)
- Data quality and correctness guarantees

**Overlapping areas:**
- Scalability and throughput reasoning
- Fault tolerance and recovery strategies
- Monitoring, alerting and observability

**The biggest difference:** backend interviews optimize for availability and
latency. DE interviews optimize for data correctness and cost. A backend system
that drops 0.01% of requests might be acceptable. A pipeline that drops 0.01%
of financial transactions is a serious incident.

## How to Use This Section

**Step 1: Build your thinking framework**
Read the foundations first. These documents teach you how to reason about
tradeoffs, estimate capacity and structure your communication during a
45-minute interview.

**Step 2: Learn the patterns**
Study the pattern docs covering ingestion, modeling, pipeline architecture,
scaling strategies and data quality. These are the building blocks you will
combine during interviews.

**Step 3: Practice full simulations**
Work through the walkthroughs. Each one simulates a complete 45-minute
interview with requirements gathering, design, deep-dive and scaling
discussion.

**Step 4: Reference the numbers**
Use the reference docs (throughput numbers, cost models, technology comparison
matrices) during practice to build intuition for realistic numbers.

## Structure Overview

| Directory | Contents | Purpose |
|---|---|---|
| `foundations/` | Tradeoff framework, capacity estimation, communication | How to THINK and TALK |
| `patterns/` | Ingestion, modeling, pipeline, scale, quality | What patterns exist |
| `walkthroughs/` | 5 full interview simulations | How to PUT IT TOGETHER |
| `reference/` | Throughput numbers, cost models, tech decisions | Quick-reference lookup |

## Connection to Other Sections

This system design section builds on the work in the patterns and SQL sections
of this repo.

**From [`patterns/`](../patterns/):** The "At Scale" discussions throughout the pattern section
(see [`patterns/11_probabilistic_structures/`](../patterns/11_probabilistic_structures/README.md) for Bloom filters, HyperLogLog
and Count-Min Sketch) directly inform system design reasoning. When you need
approximate distinct counts on 1B rows, the probabilistic structures pattern
explains the algorithms. The system design section explains when and why you
would choose them.

**From [`sql/`](../sql/):** The optimization subsection ([`sql/05_optimization_and_production/`](../sql/05_optimization_and_production/README.md))
covers query-level performance: indexing strategies, partition pruning and
query planning. System design operates one level up, covering the architecture
decisions that determine which queries are even possible and how efficiently
they can run.

**The relationship:** Patterns give you algorithmic tools. SQL gives you
query-level tools. System design gives you architecture-level tools. A complete
interview prep covers all three.

## A Note on Scope

This section provides enough framework to handle a 45-minute interview round
confidently. It covers the most common DE system design topics at a depth that
supports clear, structured discussion with concrete numbers.

A separate deep-dive system design series may follow with more detailed
walkthroughs, real production case studies and technology-specific guidance.
For now, focus on internalizing the frameworks here. They will serve you well
in the vast majority of DE system design interviews.
