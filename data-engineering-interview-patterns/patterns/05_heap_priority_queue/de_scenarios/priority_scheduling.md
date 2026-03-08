# Priority-Based Task Scheduling

**Run it:** `uv run python -m patterns.05_heap_priority_queue.de_scenarios.priority_scheduling`

## Real-World Context

Airflow has 200 tasks ready to run but only 16 worker slots. Which tasks go first? A priority queue ensures critical pipeline tasks (revenue reporting, SLA-bound deliverables) run before nice-to-have tasks (experimental dashboards, backfills).

This same pattern shows up in job schedulers, message queue consumers, incident response systems and any system where tasks compete for limited resources.

## The Problem

Given a set of tasks with priorities and submission times, process them in priority order. Among tasks with equal priority, process the earlier submission first (FIFO within priority). Tasks may arrive dynamically while others are running.

## Worked Example

Job scheduling with priorities. A min-heap (priority = urgency) ensures the highest-priority job is always processed next. Jobs can arrive at any time and get inserted in O(log n).

```
Job queue (lower number = higher priority):
  submit(priority=3, "daily_report")    → heap: [(3, daily_report)]
  submit(priority=1, "hotfix_deploy")   → heap: [(1, hotfix), (3, daily)]
  submit(priority=5, "weekly_cleanup")  → heap: [(1, hotfix), (3, daily), (5, weekly)]

  process_next() → pop (1, hotfix_deploy). Run it.
    heap: [(3, daily_report), (5, weekly_cleanup)]

  submit(priority=2, "data_backfill")   → heap: [(2, backfill), (3, daily), (5, weekly)]

  process_next() → pop (2, data_backfill). Run it.
    heap: [(3, daily_report), (5, weekly_cleanup)]

  process_next() → pop (3, daily_report). Run it.

Each submit: O(log n). Each process_next: O(log n).
Compared to a sorted list: insert is O(n) (shift elements).
```

## Why Heaps

For a static set of tasks, a heap gives the same order as sorting - both are O(n log n). The heap wins in the dynamic case: when tasks arrive while others are running, inserting into a sorted list is O(n) but pushing onto a heap is O(log n).

| Operation | Sorted List | Heap |
|-----------|-------------|------|
| Insert task | O(n) | O(log n) |
| Get next task | O(1) | O(log n) |
| Build initial queue | O(n log n) | O(n) |

In production schedulers with continuous task arrival, the O(log n) insert is what matters.

## Production Considerations

- **Priority inversion:** A flood of high-priority tasks can starve low-priority ones indefinitely. Production systems use aging (gradually increasing priority of waiting tasks) to prevent this.
- **Fairness:** Within the same priority, FIFO is the simplest fair policy. Other options: round-robin across task types, weighted fair queuing.
- **Distributed scheduling:** A single heap doesn't scale across machines. Distributed systems use per-worker heaps with a global coordinator or consistent hashing to assign tasks.
- **Dead letter handling:** Tasks that fail repeatedly should be deprioritized or moved to a dead letter queue, not retried indefinitely at high priority.

## Connection to LeetCode

This combines the heap mechanics from problem 1046 (repeatedly extract the max/min) with the priority tuple pattern from problem 23 (breaking ties with secondary keys).

## Benchmark

Running the script schedules 100K tasks. The heap and sort approaches produce identical results. Performance is similar for static scheduling but the heap approach handles dynamic arrival without re-sorting.
