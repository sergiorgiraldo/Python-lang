# DE Scenario: Pipeline DAG Analysis

## Real-World Context

Every data platform is a directed acyclic graph (DAG): sources feed transforms, transforms feed models, models feed reports. Answering "what's affected if this source breaks?" (downstream/impact analysis) and "what does this dashboard depend on?" (upstream/dependency analysis) requires graph traversal.

Tools like dbt, Airflow and Dagster build these DAGs. Understanding the traversal mechanics helps you debug lineage issues and design efficient execution strategies.

## Worked Example

A pipeline DAG extends tree traversal to handle multiple parents (a model can depend on several transforms). BFS with a visited set handles the fan-in correctly, avoiding duplicate processing when two paths converge on the same node.

```
Pipeline:
  raw_orders --> stg_orders --> fct_orders --> revenue_report
  raw_customers -> stg_customers -> dim_customers -+-> customer_dashboard
  raw_products -----------------> fct_orders ------+

Impact analysis: raw_orders changes
  BFS from raw_orders:
    -> stg_orders
    -> fct_orders (via stg_orders)
    -> revenue_report (via fct_orders)
    -> customer_dashboard (via fct_orders)
  Result: [stg_orders, fct_orders, revenue_report, customer_dashboard]

Dependency analysis: customer_dashboard
  BFS upstream from customer_dashboard:
    -> dim_customers, fct_orders
    -> stg_customers (via dim_customers)
    -> stg_orders, raw_products, dim_customers (via fct_orders)
       (dim_customers already visited, skip)
    -> raw_customers (via stg_customers)
    -> raw_orders (via stg_orders)
  Result: all upstream nodes

Execution layers (what can run in parallel):
  Layer 0: raw_orders, raw_customers, raw_products (sources, no deps)
  Layer 1: stg_orders, stg_customers (depend only on layer 0)
  Layer 2: dim_customers (depends on layer 1)
  Layer 3: fct_orders (depends on layers 0, 1, 2)
  Layer 4: revenue_report, customer_dashboard (depend on layer 3)
```

## Key Design Decisions

1. **BFS with visited set.** Unlike trees, DAGs have multiple paths to the same node. Without a visited set, you'd process nodes multiple times.
2. **Separate upstream and downstream links.** Store both directions so you can traverse in either direction without rebuilding the graph.
3. **Layer computation for parallelism.** A node's layer is 1 + max of its upstream layers. Nodes in the same layer can execute in parallel.
