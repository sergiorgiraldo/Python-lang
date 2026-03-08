# Impact Analysis (Downstream Effects)

**Run it:** `uv run python -m patterns.06_graph_topological_sort.de_scenarios.impact_analysis`

## Real-World Context

"If I change the schema of the users table, what breaks?" Every data engineer has asked this question. Impact analysis traverses the lineage graph forward from a changed table to find everything downstream. This tells you what dashboards, reports and downstream tables need attention.

## The Problem

Given a data lineage graph (which tables feed into which), find all tables affected by a change to a source table. Include the distance (number of hops) so the team can prioritize - directly dependent tables are more likely to break than tables three hops away.

## Worked Example

"If I change table X, what downstream tables/reports break?" BFS from the changed node, following dependency edges forward. Every reachable node is impacted.

```
Table lineage graph:
  raw_events → clean_events → daily_aggregates → executive_dashboard
                            → hourly_metrics → alerts_pipeline
               user_dim → daily_aggregates

Question: what breaks if raw_events schema changes?

BFS from raw_events:
  Level 1 (direct dependents): [clean_events]
  Level 2: [daily_aggregates, hourly_metrics]
  Level 3: [executive_dashboard, alerts_pipeline]

Impact: 5 downstream objects affected.
user_dim is NOT impacted (no path from raw_events to user_dim).

The level information is useful: level 1 impacts are immediate,
level 3 impacts might not surface until later pipeline stages.
```

## Why Graphs

This is BFS on a directed graph. BFS gives you the distance (hops) naturally through its level-by-level processing. DFS would find all affected tables but wouldn't give you the distances as cleanly.

## Production Considerations

- **Column-level lineage:** Table-level is coarse. If you change one column, only tables that use that specific column are affected. dbt and tools like Alation track column-level lineage for more precise impact analysis.
- **Bi-directional traversal:** Forward traversal finds downstream impact. Backward traversal finds upstream dependencies ("where does this data come from?"). Both are useful.
- **Cross-system lineage:** Real lineage graphs span databases, Kafka topics, S3 buckets and dashboards. Tools like OpenLineage and DataHub track cross-system lineage.
- **Automated testing:** Once you know the affected tables, run their tests automatically before deploying the schema change.

## Connection to LeetCode

Direct application of BFS traversal from problems 200 (Islands) and 547 (Provinces), applied to a directed graph. The distance tracking is the same as BFS level counting.

## Benchmark

BFS traversal of a lineage graph is O(V + E). Even for large organizations with thousands of tables and tens of thousands of edges, this completes in milliseconds.
