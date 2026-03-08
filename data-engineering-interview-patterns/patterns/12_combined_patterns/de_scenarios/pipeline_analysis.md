# DE Scenario: Multi-Pattern Pipeline Analysis

## Real-World Context

Analyzing a production data pipeline requires combining several patterns: counting error frequencies (hash map), understanding task dependencies (graph), and finding the worst bottlenecks (heap). No single pattern gives you the full picture.

This scenario demonstrates how the patterns from this repository compose in a realistic context.

## Worked Example

Three patterns work together. The hash map counts errors and durations per task. The graph computes dependency layers and critical path. The heap extracts the top-k slowest and most error-prone tasks. Each pattern's output feeds the next, giving a comprehensive pipeline health report.

```
Pipeline tasks and dependencies:
  extract_orders → clean_orders → join_order_customer → aggregate_revenue → dashboard
  extract_customers → clean_customers ↗
  extract_products ↗

Phase 1: Hash Map (error counting from 100 runs)
  error_rates = {
    extract_orders: 15%,
    join_order_customer: 20%,
    clean_orders: 10%,
    ... others ~2%
  }

Phase 2: Graph (dependency layers)
  Layer 0: extract_orders, extract_customers, extract_products
  Layer 1: clean_orders, clean_customers
  Layer 2: join_order_customer
  Layer 3: aggregate_revenue
  Layer 4: build_dashboard

Phase 3: Heap (top-k analysis)
  Top 3 slowest: join_order_customer (120s), aggregate_revenue (60s), clean_orders (45s)
  Top 3 error-prone: join_order_customer (20%), extract_orders (15%), clean_orders (10%)

Combined insight: join_order_customer is both the slowest task AND the most
error-prone. It's also on the critical path (layer 2). This is where
optimization effort should focus first.
```
