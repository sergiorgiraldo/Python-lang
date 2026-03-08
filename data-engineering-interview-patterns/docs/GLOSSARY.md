# Glossary

Comprehensive glossary covering algorithmic, SQL and system design terms used throughout this repository. Entries are alphabetical for easy searching.

---

**3NF (Third Normal Form)**: Full normalization where each non-key attribute depends only on the primary key. Minimizes data duplication, best for OLTP workloads. Requires many joins for analytical queries.

**ACID transactions (data lake)**: Atomicity, Consistency, Isolation and Durability guarantees applied to data lake table operations by Delta Lake and Iceberg. Prevents partial writes from being visible to readers.

**activity selection**: Classic greedy algorithm for selecting the maximum number of non-overlapping activities. Sort by end time, greedily select.

**Adaptive Query Execution (AQE)**: A Spark 3+ feature that automatically detects skew at runtime and splits large partitions into smaller ones, handling many skew scenarios without manual intervention.

**adjacency list (tree storage)**: Database representation where each row has a parent_id column. Simple to update but requires recursive queries for subtree operations.

**anchor query (recursive CTE)**: The base case of a recursive CTE that runs exactly once and provides the initial row set for recursion.

**anti-join**: A join pattern that returns rows from the left table with no match in the right table. Implemented as LEFT JOIN + IS NULL, NOT EXISTS or NOT IN (with NULL caveats).

**Apache Iceberg**: An open-source table format for huge analytic datasets built on Parquet/ORC. Adds ACID transactions, time travel, schema/partition evolution and efficient upserts. Broadest engine compatibility across Spark, Trino, Athena and Snowflake.

**approximate aggregation**: Uses probabilistic data structures to estimate aggregates (distinct counts, quantiles, top-K) with bounded error in O(1) memory, dramatically faster than exact computation on large datasets.

**APPROX_COUNT_DISTINCT**: A SQL aggregate function that uses HyperLogLog to estimate distinct counts with approximately 2% error and O(1) memory, regardless of input cardinality.

**ASOF JOIN**: Joins on the closest (rather than exact) matching timestamp. Supported natively in DuckDB and Snowflake. Useful for point-in-time lookups.

**at-least-once delivery**: A guarantee that every message is delivered one or more times. Retries on failure may cause duplicates; downstream deduplication is required.

**at-most-once delivery**: A guarantee that a message is delivered zero or one time. No retries; may lose data on failure. Simpler but risks data loss.

**Avro**: A row-oriented binary serialization format with a schema. Widely used for streaming data with a schema registry because of its support for schema evolution and smaller payloads than JSON.

**back-of-envelope calculation**: Quick estimation using rough numbers to determine feasibility. Essential skill for system design interviews where you need to validate whether an approach can handle the required scale.

**back-pressure**: A mechanism where a slow downstream component signals upstream producers to slow their output rate, preventing buffer overflow. Kafka consumer groups implement back-pressure naturally through offset management.

**backfill**: Re-running a pipeline for a historical date range. Requires parameterized pipelines, idempotent writes and partition-aware storage to overwrite rather than append.

**binary search the answer**: Technique where binary search is applied to the solution space rather than the data. Requires a monotonic feasibility function. O(n log M) where n is the check cost and M is the solution space.

**binlog (MySQL binary log)**: MySQL's transaction log recording all DDL and DML operations in binary format. The source read by Debezium for MySQL log-based CDC.

**Bloom filter**: A probabilistic data structure that tests set membership. Returns false positives but never false negatives. Used for cheap "definitely not in the set" checks like skipping files in a lake that cannot contain a key.

**BOM explosion (Bill of Materials)**: Recursively expanding a product into all its leaf-level components, multiplying quantities at each level. The classic recursive CTE use case in manufacturing and supply chain.

**broadcast join**: Distributed join strategy where the smaller table is copied to every worker, avoiding a shuffle. Works when one side fits in worker memory. Spark automatically broadcasts tables under 10 MB by default.

**BSP (Bulk Synchronous Parallel)**: Computation model for distributed graph processing. Alternates between local computation, message passing and global synchronization. Used by Pregel and Giraph.

**B-tree**: Self-balancing tree with high fan-out, used for database indexes. Each node holds many keys, minimizing disk reads. Lookup, insert and delete are all O(log n).

**CDC (Change Data Capture)**: A technique for capturing individual row-level changes (INSERT, UPDATE, DELETE) from a source database, typically by reading the transaction log. Streams changes downstream with low latency and minimal source overhead.

**checkpointing (Flink)**: Flink periodically snapshots job state and Kafka offsets atomically to durable storage. On failure, Flink restores from the last checkpoint and replays events since that point, enabling exactly-once recovery.

**circuit breaker (data quality)**: A reliability pattern that stops retrying a failing operation after repeated failures, opens the "circuit" to prevent resource waste and alerts the on-call engineer. Closes the circuit when the source recovers.

**closure table**: A data model that pre-materializes all ancestor-descendant pairs in a separate table, enabling fast subtree queries without recursive CTEs. Trades storage for query performance.

**CLUSTER BY**: In BigQuery, organizes data within partitions by up to 4 columns, enabling block-level pruning. In Snowflake, sets a clustering key for automatic micro-partition ordering.

**column pruning**: Reading only the columns referenced in the query from columnar storage. Reduces I/O by 80-96% for wide tables compared to SELECT *.

**compaction**: Merging many small files into fewer, right-sized files (100 MB to 1 GB) to improve read performance and reduce metadata overhead. Delta Lake uses OPTIMIZE; Iceberg uses rewrite_data_files.

**composite partitioning**: Combining partitioning by one column (e.g., date) with clustering/sorting within partitions by another column (e.g., user_id). BigQuery supports PARTITION BY + CLUSTER BY; Delta Lake uses Z-ORDER BY.

**conditional aggregation**: Embedding CASE expressions inside aggregate functions to compute multiple filtered metrics in a single scan. Equivalent to the FILTER clause in DuckDB and Postgres.

**constrained shortest path**: Shortest path with an additional constraint (max hops, required waypoints, time windows). Standard algorithms must be modified to track the constraint alongside distance.

**consumer group (Kafka)**: A set of Kafka consumers that together consume a topic, splitting partitions among themselves. Each partition is assigned to one consumer in the group at a time.

**contract testing**: Asserting that upstream data meets expected schema and quality requirements at pipeline boundaries, catching breaking changes before bad data propagates downstream.

**correlated subquery**: A subquery that references a column from the outer query, executing once per outer row. Can be O(n * m); modern optimizers often rewrite as a join.

**Count-Min Sketch**: A probabilistic data structure for estimating frequencies of elements (heavy hitters). Uses multiple hash functions and a 2D array of counters. Always overestimates, never underestimates.

**critical path**: The longest path through a DAG, determining the minimum end-to-end execution time assuming unlimited parallelism. Computed with topological sort + dynamic programming.

**CROSS JOIN**: A join that produces the Cartesian product of two tables (every combination of rows). Used for generating expected-value sets or sparse dimension coverage checks.

**CTE (Common Table Expression)**: A named, temporary result set defined with the WITH clause. Used to decompose complex queries, avoid repeated subqueries and improve readability. Not always materialized by the engine.

**CUBE**: Produces all 2^n combinations of n grouping columns. CUBE(a, b) produces (a, b), (a), (b), (). Use cautiously with many columns as the number of groupings grows exponentially.

**cursor-based pagination**: API pagination that uses a stable pointer (cursor) rather than page numbers. Handles concurrent inserts/deletes during iteration safely, unlike offset-based pagination.

**cycle detection (recursive CTE)**: Preventing infinite recursion in graphs with circular references. Strategies include path-array membership check, depth limit or UNION deduplication.

**DAG (Directed Acyclic Graph)**: A graph with directed edges and no cycles. Used to represent pipeline task dependencies in orchestrators like Airflow, which resolve execution order via topological sort.

**data leakage (ML)**: Using information in training that would not be available at prediction time. Produces models that perform well in training but poorly in production. Prevented by point-in-time correct feature retrieval.

**data lineage**: Tracking the origin and transformation path of data from source to destination. Used for impact analysis and debugging data quality issues.

**data observability**: Continuous monitoring of data freshness, volume, schema changes and distribution drift to detect problems before they surface as failures.

**data quarantine**: Pattern for isolating malformed or unparseable records in a separate storage location for later investigation, rather than failing the entire pipeline.

**Data Vault**: An enterprise data modeling methodology for integration layers. Separates concerns into Hubs (business keys), Links (relationships) and Satellites (descriptive attributes with history). Suited for regulated industries.

**data skew**: Uneven data distribution across partitions or workers in a distributed job, causing some workers to take significantly longer than others. The job finishes when the slowest worker finishes.

**dbt (data build tool)**: A SQL-based transformation framework that allows engineers to define models, tests and documentation. Handles DAG-based model dependencies, incremental materializations and built-in data quality tests.

**dead letter queue (DLQ)**: A sink for messages that fail processing (malformed records, schema violations). Isolates failures to prevent blocking the main pipeline and enables separate investigation.

**Debezium**: An open-source CDC platform that reads database transaction logs (MySQL binlog, Postgres WAL, SQL Server, MongoDB) and publishes changes to Kafka topics.

**Delta Lake**: An open-source storage layer from Databricks built on Parquet. Adds ACID transactions, time travel, schema enforcement, schema evolution and efficient upserts. Strong Spark integration.

**DENSE_RANK()**: Window function that assigns the same rank to tied rows without gaps (e.g., 1, 1, 2). Used for Nth highest or top-N distinct value queries.

**dimension table**: A table containing descriptive attributes (customer name, product category, date components) used for filtering and grouping fact table queries in a star schema.

**entity resolution**: Process of identifying records across datasets that refer to the same real-world entity. Often modeled as a connected components problem on a similarity graph.

**Euler tour**: Technique for flattening a tree into a sequence by recording entry and exit visits. Combined with a sparse table, enables O(1) LCA queries after O(n log n) preprocessing.

**event sourcing**: An architectural pattern where the event stream is the source of truth. Current state is derived by replaying all events from the beginning, providing a complete audit trail.

**exactly-once semantics**: A guarantee that each message is processed exactly once with no duplicates or losses. Requires coordinated producer idempotence, transactional consumers and atomic state commits.

**EXPLAIN / EXPLAIN ANALYZE**: SQL statements that show the query execution plan or actual execution statistics. Used to identify full-table scans, expensive sorts, skewed joins and optimization opportunities.

**exponential backoff**: A retry strategy that doubles the wait time between consecutive failures (1s, 2s, 4s, 8s), preventing a failing service from being overwhelmed by rapid retries.

**external hashing**: Hash-based processing for datasets that don't fit in memory. Partition data to disk by hash, then process each partition in memory.

**external merge sort**: Sorting data too large for memory by sorting in-memory chunks, writing to disk, then merging sorted runs. O(n log n) time with O(M) memory where M is the available RAM.

**fact table**: A table containing quantitative measures (amounts, counts, durations) and foreign keys to dimension tables. Each row represents an event or transaction at a specific grain.

**fan-out (join)**: Row multiplication caused by a one-to-many join. When an order joins to its line items, each order row becomes N rows, inflating aggregates if not handled carefully.

**fan-out (top-k)**: Distributed top-k strategy where each partition computes local top-k, then a coordinator merges and selects the global top-k from at most P*k candidates.

**fan-out-on-read**: Computing derived data at read time. Lower write cost, higher read cost.

**fan-out-on-write**: Precomputing derived data (like feeds) at write time. Higher write cost, lower read cost.

**feature store**: A centralized system for managing, computing, storing and serving ML features. Provides an offline store for training (point-in-time correct historical values) and an online store for low-latency serving.

**FILTER clause**: Syntactic sugar for conditional aggregation: SUM(amount) FILTER (WHERE status = 'completed'). Supported only in DuckDB and Postgres.

**Flink (Apache Flink)**: A distributed stream processing engine providing true event-at-a-time streaming with exactly-once semantics, stateful computation, event-time processing and watermarks. Achieves sub-100ms per-event latency.

**frame clause**: Limits which rows within a partition are included in a window function computation. Uses ROWS, RANGE or GROUPS as the frame type.

**FULL OUTER JOIN**: Returns all rows from both sides, filling NULLs where no match exists. Used for bidirectional reconciliation between two datasets.

**gap detection**: Finding missing values in an expected sequence by generating the expected set, left-joining to the actual set and filtering for NULLs. Anti-join pattern applied to generated sequences.

**generate_series**: A table-generating function that produces a sequence of integers, dates or timestamps. Available in DuckDB and Postgres; BigQuery uses GENERATE_DATE_ARRAY, Snowflake uses GENERATOR.

**giant component**: In graph theory, a connected component containing a significant fraction of all nodes. Creates partition skew in distributed graph processing.

**GROUPING SETS**: An extension to GROUP BY that computes multiple grouping combinations in a single pass over the data. More efficient than multiple GROUP BY queries connected by UNION ALL.

**GROUPING() function**: Returns 1 if a column is aggregated away in the current grouping level (a subtotal row), and 0 if it holds a real value. Disambiguates NULLs caused by GROUPING SETS from NULLs in source data.

**hash aggregation**: An aggregation strategy that builds a hash table keyed on group-by columns, accumulating aggregates per group. O(n) time, O(distinct groups) memory. Default for GROUP BY.

**hash join**: A join algorithm that hashes the smaller table into a hash table (build phase), then probes it with each row from the larger table. O(n + m) expected complexity. Default for equi-joins on large tables.

**hash partitioning**: Distributing data evenly across N partitions using a hash of a column value. Prevents hot partitions but provides no benefit for range queries.

**hash-partitioned join**: Distributed join where both tables are shuffled by join key so matching keys land on the same worker.

**heavy hitter**: An element whose frequency exceeds a threshold (e.g., >1% of total count). Detecting heavy hitters in a stream without storing all frequencies uses probabilistic structures like Count-Min Sketch.

**hot partition**: A partition that receives a disproportionate share of writes (typically today's date partition in append-heavy workloads), creating a bottleneck.

**hub (Data Vault)**: A Data Vault entity that stores unique business keys (e.g., customer_id, order_id), one row per unique entity. The stable core of the Data Vault model.

**HyperLogLog (HLL)**: A probabilistic algorithm that estimates cardinality by tracking the maximum number of leading zeros in hashed values across registers. Achieves ~2% error with 16 KB of memory. HLL sketches are mergeable across partitions.

**idempotency**: A property where an operation produces the same result regardless of how many times it is executed. Essential for safe retries in pipelines. Implemented via upserts, INSERT OVERWRITE, deduplication keys or idempotent producers.

**incremental aggregation**: Maintaining an aggregate (sum, count, max) by updating it incrementally as elements enter/leave a window, rather than recomputing from scratch.

**incremental refresh**: Updating a materialized view by processing only new or changed data since the last refresh, rather than reprocessing everything.

**interval tree**: Tree data structure for storing intervals with O(log n + k) query for finding all intervals overlapping a point or range. Used in databases for range index operations.

**island technique**: Uses id - ROW_NUMBER() OVER (ORDER BY id) to assign group labels to consecutive qualifying rows. Consecutive rows in a qualifying sequence share the same constant difference; a gap breaks the sequence.

**key skew**: Uneven distribution of values in a join or group-by key, causing one partition to process disproportionately more data. Mitigated by salting or broadcast joins.

**k-way merge**: Merging k sorted sequences into one sorted output using a heap of size k. O(n log k) total where n is the combined element count. Core of external sort and sort-merge joins.

**label propagation**: Distributed algorithm for finding connected components or communities. Each node adopts the label of its most frequent neighbor iteratively.

**LAG()**: Window function that returns the value of an expression from a previous row in the partition. Used for row-to-row comparisons such as day-over-day change detection.

**lakehouse**: An architecture combining the low-cost, flexible storage of a data lake (S3 in open formats) with the reliability and performance features of a data warehouse (ACID transactions, schema enforcement, efficient queries).

**LATERAL JOIN**: Allows the right-hand subquery in a join to reference columns from the left-hand table. Enables per-row subqueries, top-N-per-group without window functions and array flattening.

**LEAD()**: Window function that returns the value of an expression from a subsequent row in the partition. Used for forward-looking comparisons such as computing validity end dates in SCD Type 2.

**length-prefix encoding**: Serialization technique where each value is preceded by its byte length. Enables unambiguous parsing without delimiter escaping. Used in TCP, Protobuf and Avro.

**link (Data Vault)**: A Data Vault entity that records relationships between hubs (e.g., customer placed order). Captures many-to-many associations with historical tracking.

**LSM tree**: Log-structured merge tree. Write-optimized data structure that batches writes into sorted runs and periodically merges them. Used in Cassandra, RocksDB and LevelDB.

**materialized path**: Database representation where each node stores its full ancestor path (e.g., "/root/child1/grandchild2"). Enables fast ancestor queries with LIKE but path length is unbounded.

**materialized view**: A pre-computed query result stored as a table. Trades storage and freshness for fast reads. Refresh strategies include full refresh, incremental refresh and merge refresh.

**medallion architecture (bronze/silver/gold)**: A layered data organization pattern. Bronze: raw data as-is. Silver: cleaned, typed, deduplicated. Gold: aggregated business-ready tables. Each layer has progressively stricter quality standards.

**MERGE / upsert**: A DML statement that combines INSERT, UPDATE and DELETE into one atomic operation based on a join condition. The standard pattern for incremental warehouse loads and dimension maintenance.

**micro-batch**: Processing data in very small batches (as low as 100ms intervals) to achieve near-real-time latency with batch-like simplicity. Spark Structured Streaming's primary model.

**micro-partition (Snowflake)**: Snowflake's automatic storage unit (50-500 MB compressed). Snowflake prunes micro-partitions based on column min/max statistics; not explicitly user-managed.

**MinHash**: A probabilistic technique for estimating Jaccard similarity (set overlap) between two sets of values.

**monotonic stack**: Stack maintaining elements in sorted order (increasing or decreasing). New elements that violate the invariant cause pops, resolving the popped elements. O(n) amortized because each element is pushed and popped at most once.

**natural key**: The original business identifier from the source system (customer_id, product_id). Used for matching source records to dimension records; not used as the join key in star schemas where surrogate keys are preferred.

**nested loop join**: A join algorithm that iterates over each row in the outer table and, for each, scans or index-looks-up matching rows in the inner table. O(n * m); efficient only when one table is small or the inner table has an index.

**nested sets**: Database representation where each node stores left/right visit numbers from a DFS. Enables fast subtree queries (WHERE left BETWEEN parent_left AND parent_right) but expensive to update.

**nesting depth**: Maximum depth of nested structures (brackets, tags, function calls). Determines stack memory usage for recursive/stack-based parsers.

**NOT IN NULL trap**: A correctness bug: if any value in a NOT IN subquery is NULL, three-valued SQL logic causes the entire NOT IN to return no rows. Fix: use NOT EXISTS or LEFT JOIN + IS NULL.

**OBT (One Big Table)**: A denormalized single wide table with all dimensional attributes pre-joined into fact rows. Zero join complexity at query time; suitable for single-purpose analytics but difficult to maintain.

**offset management (Kafka)**: Tracking which events in a Kafka partition each consumer has processed. Committing offsets after processing gives at-least-once delivery; committing before gives at-most-once.

**OLAP (Online Analytical Processing)**: A workload pattern characterized by complex queries that scan large volumes of data for aggregations and reporting. Warehouses and columnar engines are optimized for OLAP.

**OLTP (Online Transaction Processing)**: A workload pattern characterized by many short, concurrent read/write transactions. Normalized schemas and row-oriented storage are optimized for OLTP.

**order-statistic tree**: Augmented balanced BST that supports O(log n) rank queries (find kth element, find rank of element). Not available in Python's standard library.

**Parquet**: A columnar binary file format with built-in compression. Achieves 3-5x compression vs CSV/JSON. Enables column pruning and predicate pushdown. The default for analytical workloads.

**partial aggregation**: In distributed engines, each node computes local aggregates before shuffling. Only the local summary rows (not all input rows) are transferred over the network.

**PARTITION BY**: Divides rows into independent groups within a window function; each partition is processed separately. Omitting it treats the entire result set as one partition.

**partition pruning**: The query engine skips partitions that cannot satisfy the filter predicate. Requires the partition key to appear as a bare column in the WHERE clause (sargable predicate).

**path enumeration**: Building full path strings from root to each node in a hierarchy (e.g., "CEO / VP Engineering / Director"). Used for breadcrumbs, data lineage and subtree queries via LIKE prefix matching.

**pattern composition**: Combining two or more algorithmic patterns to solve a problem that neither pattern addresses alone. The ability to decompose problems into known patterns is a key interview skill.

**pipeline stage decomposition**: Breaking a multi-pattern algorithm into sequential stages that can be independently parallelized or optimized. Maps to ETL stages in data pipelines.

**PIVOT / UNPIVOT**: PIVOT transforms row-based data into columnar format (values in one column become separate output columns). UNPIVOT reverses the transformation. Supported natively in DuckDB, BigQuery, Snowflake and Spark SQL.

**point-in-time join (as-of join)**: A join that retrieves the value of an attribute as it existed at a specific past timestamp. Critical for preventing data leakage in ML feature stores and accurate historical analysis.

**predicate pushdown**: An optimization where the query engine applies filter predicates as early as possible (at the file-reader level for Parquet), skipping row groups or partitions that cannot match.

**QUALIFY**: A clause (supported in BigQuery, Snowflake, DuckDB, Databricks) that filters rows after window function evaluation, analogous to how HAVING filters after GROUP BY. Eliminates the need for a wrapping subquery.

**range join**: Join between two tables based on overlapping ranges (e.g., WHERE a.start < b.end AND a.end > b.start). Poorly optimized by most SQL engines without explicit indexing or binning.

**range partitioning**: Distributing data across partitions by value range (e.g., dates, ID ranges). Enables partition pruning on range queries.

**RANK()**: Window function that assigns the same rank to tied rows, then skips the next rank (e.g., 1, 1, 3). Used for competition-style ranking.

**recursive CTE (WITH RECURSIVE)**: A CTE that references itself, enabling iterative computation in SQL. Consists of a base case (anchor) and a recursive step joined with UNION ALL. Used for hierarchies, graph traversal and sequence generation.

**reservoir sampling**: Algorithm for uniform random sampling from a stream of unknown size in O(k) memory.

**ROLLUP**: Shorthand for a hierarchical set of GROUPING SETS. ROLLUP(a, b, c) produces (a, b, c), (a, b), (a), (), adding a grand-total row. Column order determines the hierarchy.

**ROW_NUMBER()**: Window function that assigns a unique sequential integer to each row within a partition. Never produces ties. Used for deduplication by keeping the row with ROW_NUMBER() = 1.

**salting**: Technique to handle key skew by appending random values to hot keys, spreading their data across multiple partitions.

**sargable (Search ARGument ABLE)**: A predicate that allows the query engine to use an index or perform partition pruning. Applying a function to the indexed column breaks sargability; rewriting as a range predicate restores it.

**satellite (Data Vault)**: A Data Vault entity that stores descriptive attributes with full history. Each change creates a new row with a load timestamp, enabling complete audit trails.

**SCD (Slowly Changing Dimension)**: A dimension that changes over time. The SCD type determines how changes are handled: Type 1 overwrites, Type 2 versions with a new row, Type 3 tracks one previous value.

**schema evolution**: The process of changing a schema over time (adding columns, changing types, removing fields) in a way that does not break existing producers or consumers.

**schema registry**: A central catalog that stores and enforces Avro or Protobuf schemas for Kafka topics. Ensures backward/forward compatibility between producers and consumers.

**schema-on-read**: Storing raw data without schema enforcement and applying schema at query time. Flexible and fast to set up but risks propagating bad data undetected.

**schema-on-write**: Enforcing a schema at ingestion time; bad data is rejected before entering the system. Protects downstream consumers but makes schema evolution harder.

**self-join**: A table joined to itself under two different aliases. Used for navigating hierarchical or self-referential relationships like org charts, friend networks and BOM structures.

**semi-join**: Returns rows from the left table that have at least one match in the right table, without duplicating left rows. Implemented with EXISTS. Stops scanning after the first match.

**session window**: Variable-size window defined by inactivity gaps. A new window starts when the gap between events exceeds a threshold. Used in sessionization of clickstream data.

**sessionization**: The process of grouping a stream of events into logical sessions by detecting idle-time gaps exceeding a threshold (typically 30 minutes). Implemented with LAG-based gap detection plus a running SUM.

**shuffle (distributed processing)**: In distributed engines, the network transfer of data between workers to co-locate rows with the same key for a join or aggregation. The primary bottleneck for distributed jobs.

**sketch mergeability**: Property of probabilistic data structures where sketches computed on partitions can be combined to produce a sketch equivalent to one computed on the full dataset. HLL, CMS and Bloom filters are all mergeable.

**sliding window (streaming)**: Overlapping fixed-size time window. An event may belong to multiple windows. More expensive than tumbling due to overlap.

**small files problem**: Performance degradation caused by over-partitioning, which creates millions of tiny files. Each file has overhead for metadata, file handles and LIST operations. Fixed by compaction.

**snapshot comparison (CDC)**: Extracting a full table snapshot today, comparing to yesterday's snapshot and detecting changes by diffing the two copies. Most reliable when the source cannot expose change tracking; most expensive.

**sort aggregation**: An aggregation strategy that sorts rows by group key, then walks sorted rows accumulating aggregates per group. O(n log n); chosen when data is already sorted or memory pressure forces disk spill.

**sort-merge join**: A join algorithm that sorts both inputs by the join key, then merges them in a single pass. O(n log n + m log m) for sorting, O(n + m) for the merge. Preferred when both sides are large or already sorted.

**star schema**: The most widely used analytical data model. Fact tables hold events/transactions with foreign keys to skinny dimension tables. Optimized for read performance with 2-5 table joins.

**state machine (parsing)**: Parser that tracks a current state and transitions between states based on input characters. Handles context-dependent parsing like "am I inside a quoted string?"

**streaming distinct**: Deduplication of a sorted stream by comparing each element to the previous. O(1) memory, requires sorted input.

**streaming parser**: Parser that processes input incrementally without loading the entire document. Uses bounded memory regardless of input size. Examples: SAX (XML), ijson (JSON).

**surrogate key**: A system-generated integer key used as the primary key of a dimension table, replacing the natural/business key for joins. Enables SCD Type 2 by allowing multiple rows for the same entity.

**sweep line**: Algorithm technique that processes events (interval starts/ends) in sorted order, maintaining a running state. Converts 2D interval problems into 1D event processing.

**t-digest**: Probabilistic data structure for approximate quantile estimation (median, p95, p99). Provides bounded-error queries with compact memory. Used in Spark, Elasticsearch and BigQuery.

**tiered storage**: Storing data across multiple storage tiers with different cost and access characteristics (S3 Standard to Infrequent Access to Glacier). Lifecycle policies automate movement between tiers.

**time partitioning**: Partitioning data by a date or timestamp column. The most common strategy for event data. Enables partition pruning on date-filtered queries.

**time travel (table format)**: The ability to query data as of a previous snapshot or timestamp. Supported by Delta Lake and Apache Iceberg via their transaction log.

**timestamp-based CDC**: Incremental loading by querying WHERE updated_at > last_run_timestamp. Simplest CDC approach but misses deletes and is vulnerable to clock skew.

**topological sort (orchestration)**: An algorithm that orders DAG nodes such that every directed edge goes from an earlier to a later node. Orchestrators like Airflow use topological sort to determine task execution order.

**training-serving skew**: A discrepancy between feature values used during model training and those used during serving. Prevented by point-in-time correct feature retrieval and consistent feature computation logic.

**trigger-based CDC**: CDC via database triggers that fire on each change and write to a change table. No log access needed but adds 10-30% write overhead.

**tumbling window**: Non-overlapping fixed-size time window in stream processing. Each event belongs to exactly one window. Used for per-period aggregations like hourly totals.

**vectorized UDF**: User-defined function that processes data in batches (pandas DataFrames) rather than row-by-row. 10-100x faster than scalar UDFs in PySpark because it minimizes JVM-Python serialization overhead.

**WAL (Write-Ahead Log)**: Postgres's transaction log, written before data pages are modified. The source read by Debezium for Postgres log-based CDC.

**watermark (incremental SQL)**: The high-water mark (e.g., max updated_at processed), used to filter only records that have changed since the last load.

**watermark (stream processing)**: In Flink and Spark Structured Streaming, a timestamp that tracks how far event time has progressed. Defines when a time window can be considered complete. Late events beyond the watermark are dropped from real-time aggregations.

**window function**: A function that computes values across a set of related rows without collapsing them, returning a result for every input row while allowing access to other rows in the same result set.

**window state**: The data maintained by a stream processing operator for each active window. Must be checkpointed for fault tolerance.

**Z-ordering / Z-ORDER BY**: A multi-column clustering technique that organizes data within files by multiple columns simultaneously, enabling efficient multi-dimensional filtering.

**zone maps / min-max statistics**: Metadata stored per data file or row group recording the minimum and maximum values. Enables query engines to skip files that can't contain matching rows without reading them.
