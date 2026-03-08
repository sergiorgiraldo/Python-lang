# Data Modeling Patterns

Data modeling determines how efficiently data can be queried and how easily
it can evolve. The right model depends on who queries the data, how they
query it and how frequently the underlying schema changes. There is no
universally correct model. There are tradeoffs.

## Pattern 1: Star Schema

The most widely used analytical modeling pattern. Fact tables hold events or
transactions (orders, clicks, payments). Dimension tables hold descriptive
attributes (customers, products, dates).

### Structure

Facts are skinny: foreign keys to dimensions plus numeric measures (amount,
quantity, duration). Dimensions are wide: all the descriptive attributes a
query might filter or group by.

```
           dim_customer
               |
dim_product ---+--- fact_orders --- dim_date
               |
           dim_store
```

A well-designed star schema query joins 2-5 tables. The fact table provides
the measures and the dimensions provide the filters and groupings. BI tools
(Looker, Tableau, Power BI) are built to work with this pattern.

### When to Use

Analytical queries, dashboards, BI tools and ad-hoc analysis. The star schema
is the default choice for dimensional modeling in warehouses. If you are
building a serving layer for analysts, start here.

### Tradeoffs

Denormalized for read performance (fewer joins than 3NF) but harder to
maintain dimensional consistency. When a customer's address changes, the
dimension table needs updating and the approach to that update matters (see
SCD patterns below).

A star schema with 5 dimensions and 1 fact table at 1B rows occupies roughly
100-200 GB in compressed Parquet. The dimension tables are typically 1-10 GB
combined. Query performance is excellent because the star join pattern lets
the query engine apply predicate pushdown on dimensions before scanning the
fact table.

## Pattern 2: One Big Table (OBT)

Pre-join everything into a single wide table. No joins at query time. Every
row contains all the dimensional attributes alongside the measures.

### When to Use

Simple analytics with a single primary use case. Teams unfamiliar with
dimensional modeling who need quick results. Prototyping before investing
in a proper star schema.

An OBT with 100 columns at 1B rows occupies roughly 50-100 GB in Parquet.
Column pruning means queries that select 5 of those 100 columns only read
about 5% of the data, so the wide table does not hurt query performance as
much as you might expect.

### When NOT to Use

Multiple fact tables at different grains (you cannot flatten orders and
page views into one table without duplication). Frequently changing
dimensions (a customer name change requires updating every row that
references that customer). Large dimensions with many attributes
(repeating 50 customer columns across billions of rows wastes storage).

### Tradeoff

Zero join complexity at the cost of storage bloat and update difficulty.
For a single-purpose analytics table refreshed daily, this is often the
pragmatic choice. For a warehouse serving multiple teams with different
needs, star schema scales better. See `foundations/tradeoff_framework.md`
on the normalized vs denormalized tradeoff.

## Pattern 3: Normalized (3NF)

Full normalization stores each fact exactly once. Every non-key attribute
depends on the key, the whole key and nothing but the key.

### When to Use

OLTP systems and source-of-truth databases where write performance and
data integrity matter. The staging layer of a warehouse often uses
normalized models before transforming to star schema.

### When NOT to Use

Analytical queries. A normalized schema for a moderately complex business
domain might require 10-15 table joins for a single business question.
At warehouse scale (billions of rows), those joins are expensive and slow.

Postgres handles roughly 10K transactions/sec on a normalized schema.
That is excellent for OLTP. But an analyst running a 15-table join across
1B rows will wait minutes instead of seconds compared to the same query
on a denormalized star schema.

### Connection to Interview

If asked about modeling choices, the key insight is: normalize for writes,
denormalize for reads. Warehouses are read-heavy (hundreds of queries per
data refresh), so denormalize. Source databases are write-heavy, so normalize.

## Pattern 4: Data Vault

Data Vault separates structural concerns into three entity types:

- **Hubs:** Business keys (customer_id, order_id). One row per unique entity.
- **Links:** Relationships between hubs (customer placed order). Many-to-many
  relationships live here.
- **Satellites:** Descriptive attributes with full history. Each change creates
  a new satellite row with a load timestamp.

### When to Use

Enterprise data warehouses integrating many sources where requirements change
frequently. Regulated industries (finance, healthcare) where full audit trails
are mandatory. Environments where source systems change schema without warning.

Data Vault handles source changes gracefully: a new source adds new satellites
to existing hubs rather than requiring restructuring of fact tables.

### Tradeoffs

Complex to implement and query. A single business question may require joining
hubs, links and multiple satellites. Requires tooling support and a team
familiar with the methodology. Not a good fit for small teams or simple use
cases.

Data Vault works well as a raw/integration layer that feeds a star schema
presentation layer. The vault stores everything with history. The star schema
provides query-friendly views for analysts.

## Pattern 5: Slowly Changing Dimensions (SCDs)

Dimensions change over time. A customer moves, a product gets reclassified,
a store changes regions. How you handle these changes affects query accuracy
for historical analysis.

### SCD Types

**Type 1 (Overwrite):** Update the dimension row in place. The old value is
lost. Simple but you cannot answer "what region was this customer in last
quarter?"

**Type 2 (New Row):** Insert a new row with version tracking columns
(`effective_date`, `end_date`, `is_current`). Full history preserved. Most
common for analytical warehouses.

**Type 3 (Previous Value Column):** Add a `previous_value` column. Only
tracks one change back. Rarely used in practice because the history depth
is too limited.

**Type 6 (Hybrid):** Combines Types 1, 2 and 3. Current value is overwritten
(Type 1) on all rows, new row is added (Type 2) and previous value is stored
(Type 3). Gives maximum flexibility at maximum complexity.

### Querying SCD Type 2

To get the current version of each dimension record:

```sql
ROW_NUMBER() OVER (
  PARTITION BY business_key
  ORDER BY effective_date DESC
) = 1
```

This window function pattern appears in [`sql/01_window_functions/`](../../sql/01_window_functions/README.md) for the
deduplication scenario. In a system design interview, mentioning SCD Type 2
with this query pattern shows both modeling and SQL depth.

### Choosing an SCD Type

| Need | SCD Type |
|---|---|
| Only current values matter | Type 1 |
| Full history required | Type 2 |
| One previous value sufficient | Type 3 |
| Maximum flexibility, complex team | Type 6 |

Type 2 is the default for analytical warehouses. Use Type 1 only when you
are certain historical values are irrelevant.

## Pattern 6: Schema Evolution

Schemas change. Columns are added, types shift and entire tables are
restructured. How you handle these changes determines whether your pipeline
breaks or adapts.

### Change Categories

**Additive (safe):** Adding a new column with a default value. Old data gets
NULL or the default. New data populates the column. Parquet handles this
natively: new files have the column, old files return NULL.

**Destructive (breaking):** Removing a column or renaming it. Downstream
queries referencing the old name will fail. Must be coordinated across
producers and consumers.

**Type changes (risky):** INT to STRING is safe (every integer is a valid
string). STRING to INT will fail on non-numeric values. FLOAT to INT loses
precision. Always assess the direction of the change.

### Managing Evolution

**Schema registry:** Avro or Protobuf schemas registered centrally. Producers
and consumers negotiate compatible versions. Kafka's schema registry enforces
backward or forward compatibility.

**Contract testing:** Assert that upstream data meets expected schema and
quality before processing. dbt schema tests, Great Expectations and custom
assertions at pipeline boundaries catch breaking changes early.

**Versioned tables:** For major schema changes, create a v2 table alongside v1.
Migrate consumers gradually rather than forcing a big-bang cutover.

## The Medallion Architecture

A layered approach to data organization used widely in lakehouse architectures
(Databricks, Delta Lake, Iceberg).

```
Sources --> Bronze (Raw) --> Silver (Clean) --> Gold (Curated)
            |                |                  |
            As-is from       Typed, deduped,    Aggregated,
            source           validated          business-ready
```

**Bronze:** Raw data preserved exactly as received. Schema-on-read.
No transformations. Enables replay if downstream logic changes.

**Silver:** Cleaned, typed and deduplicated. Schema-on-write enforced.
Bad records quarantined. This is where data quality checks live.

**Gold:** Aggregated, joined and shaped for specific business use cases.
Star schemas, OBTs and summary tables live here. Optimized for query
performance.

Each layer has different modeling standards. Bronze is permissive (store
everything). Silver enforces correctness. Gold optimizes for consumption.

## Connection to Interview

When asked about data modeling, clarify the consumer first. Analysts using
BI tools: star schema. Data scientists needing flexible access: medallion
with a silver layer. Simple single-purpose dashboard: OBT might be enough.
Enterprise integration across many sources: consider Data Vault as the
integration layer feeding star schema for consumption.

The modeling choice is a tradeoff decision. Use the framework from
`foundations/tradeoff_framework.md`: state the options, evaluate against
the consumer's needs and acknowledge what you give up.
