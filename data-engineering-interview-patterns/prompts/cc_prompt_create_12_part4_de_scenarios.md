# CC Prompt: Create Pattern 12 Combined Patterns (Part 4 of 4)

## What This Prompt Does

Creates 2 DE scenarios: Multi-Pattern Pipeline Analysis and Pattern Recognition Practice.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable with demo) and .md (documented)

---

## DE Scenario 1: Multi-Pattern Pipeline Analysis

### `de_scenarios/pipeline_analysis.py`

```python
"""
DE Scenario: Multi-pattern pipeline analysis.

Real-world application: analyzing a data pipeline to find bottlenecks,
compute critical path and identify the most error-prone tasks. Combines
hash maps (frequency counting), graphs (dependency traversal) and heaps
(priority-based processing).

Run: uv run python -m patterns.12_combined_patterns.de_scenarios.pipeline_analysis
"""

import heapq
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class TaskExecution:
    """A single task execution record."""

    task_name: str
    duration_seconds: float
    status: str  # success, failure, retry
    timestamp: str


def analyze_pipeline(
    tasks: list[dict],
    dependencies: list[tuple[str, str]],
    executions: list[TaskExecution],
) -> dict:
    """
    Comprehensive pipeline analysis combining three patterns.

    1. Hash Map: count error frequencies per task.
    2. Graph: build dependency graph, compute layers.
    3. Heap: find top-k slowest and most error-prone tasks.
    """
    # Phase 1: Hash Map - error frequency counting
    error_counts: dict[str, int] = defaultdict(int)
    total_counts: dict[str, int] = defaultdict(int)
    avg_durations: dict[str, list[float]] = defaultdict(list)

    for ex in executions:
        total_counts[ex.task_name] += 1
        avg_durations[ex.task_name].append(ex.duration_seconds)
        if ex.status == "failure":
            error_counts[ex.task_name] += 1

    error_rates = {
        task: error_counts[task] / total_counts[task]
        for task in total_counts
        if total_counts[task] > 0
    }

    avg_duration_map = {
        task: sum(durations) / len(durations)
        for task, durations in avg_durations.items()
    }

    # Phase 2: Graph - dependency analysis
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)
    task_names = {t["name"] for t in tasks}

    for task in task_names:
        in_degree.setdefault(task, 0)

    for parent, child in dependencies:
        graph[parent].append(child)
        in_degree[child] = in_degree.get(child, 0) + 1

    # Compute execution layers (topological order)
    layers: dict[str, int] = {}

    def get_layer(task: str, visited: set[str] | None = None) -> int:
        if task in layers:
            return layers[task]
        if visited is None:
            visited = set()
        if task in visited:
            return 0  # cycle protection
        visited.add(task)

        parents = [p for p, children in graph.items() if task in children]
        if not parents:
            layers[task] = 0
        else:
            layers[task] = 1 + max(get_layer(p, visited) for p in parents)
        return layers[task]

    for task in task_names:
        get_layer(task)

    # Phase 3: Heap - top-k analysis
    # Top 3 slowest tasks
    slowest = heapq.nlargest(
        3,
        avg_duration_map.items(),
        key=lambda x: x[1],
    )

    # Top 3 most error-prone tasks
    most_errors = heapq.nlargest(
        3,
        error_rates.items(),
        key=lambda x: x[1],
    )

    # Critical path (longest path through the DAG by duration)
    critical_path_duration = 0.0
    for task in task_names:
        layer = layers.get(task, 0)
        path_duration = sum(
            avg_duration_map.get(t, 0)
            for t, l in layers.items()
            if l <= layer
        )
        critical_path_duration = max(critical_path_duration, path_duration)

    return {
        "error_rates": dict(error_rates),
        "avg_durations": dict(avg_duration_map),
        "layers": dict(layers),
        "top_3_slowest": slowest,
        "top_3_error_prone": most_errors,
        "critical_path_duration": critical_path_duration,
        "total_tasks": len(task_names),
        "total_executions": len(executions),
    }


if __name__ == "__main__":
    import random

    print("=== Multi-Pattern Pipeline Analysis ===\n")

    tasks = [
        {"name": "extract_orders"},
        {"name": "extract_customers"},
        {"name": "extract_products"},
        {"name": "clean_orders"},
        {"name": "clean_customers"},
        {"name": "join_order_customer"},
        {"name": "aggregate_revenue"},
        {"name": "build_dashboard"},
    ]

    dependencies = [
        ("extract_orders", "clean_orders"),
        ("extract_customers", "clean_customers"),
        ("clean_orders", "join_order_customer"),
        ("clean_customers", "join_order_customer"),
        ("extract_products", "join_order_customer"),
        ("join_order_customer", "aggregate_revenue"),
        ("aggregate_revenue", "build_dashboard"),
    ]

    # Generate execution history
    executions = []
    base_durations = {
        "extract_orders": 30, "extract_customers": 15,
        "extract_products": 10, "clean_orders": 45,
        "clean_customers": 20, "join_order_customer": 120,
        "aggregate_revenue": 60, "build_dashboard": 25,
    }
    error_probs = {
        "extract_orders": 0.15, "clean_orders": 0.10,
        "join_order_customer": 0.20,
    }

    for run in range(100):
        for task in tasks:
            name = task["name"]
            duration = base_durations.get(name, 30) * random.uniform(0.8, 1.3)
            fail = random.random() < error_probs.get(name, 0.02)
            executions.append(TaskExecution(
                task_name=name,
                duration_seconds=duration,
                status="failure" if fail else "success",
                timestamp=f"2024-01-{15 + run // 10:02d}",
            ))

    result = analyze_pipeline(tasks, dependencies, executions)

    print("  Execution layers:")
    for layer_num in sorted(set(result["layers"].values())):
        layer_tasks = [t for t, l in result["layers"].items() if l == layer_num]
        print(f"    Layer {layer_num}: {layer_tasks}")

    print(f"\n  Top 3 slowest tasks:")
    for task, dur in result["top_3_slowest"]:
        print(f"    {task}: {dur:.1f}s avg")

    print(f"\n  Top 3 most error-prone:")
    for task, rate in result["top_3_error_prone"]:
        print(f"    {task}: {rate:.1%} failure rate")

    print(f"\n  Pipeline stats:")
    print(f"    Tasks: {result['total_tasks']}")
    print(f"    Total executions: {result['total_executions']}")
```

### `de_scenarios/pipeline_analysis.md`

````markdown
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
````

---

## DE Scenario 2: Pattern Recognition Practice

### `de_scenarios/pattern_recognition.py`

```python
"""
DE Scenario: Pattern recognition practice.

This module presents interview-style problems WITHOUT pattern labels.
The challenge: identify which pattern(s) apply before solving.

Run: uv run python -m patterns.12_combined_patterns.de_scenarios.pattern_recognition
"""


def practice_problems() -> list[dict]:
    """
    Return a list of practice problems for pattern recognition.
    Each has a description, hints, and the patterns involved.
    """
    return [
        {
            "title": "Event Session Windows",
            "description": (
                "Given a stream of user events (user_id, timestamp), group events "
                "into sessions. A session ends when there's a gap of more than "
                "30 minutes between events. Return the session count per user."
            ),
            "hints": [
                "Sort events by user and timestamp",
                "Track the gap between consecutive events",
                "What pattern handles consecutive-element comparisons?",
            ],
            "patterns": ["Sort", "Two Pointers / Sliding Window", "Hash Map"],
            "approach": (
                "Sort by (user_id, timestamp). For each user, iterate through "
                "events tracking the current session. When the gap exceeds 30 "
                "minutes, start a new session. Hash map stores session count "
                "per user."
            ),
        },
        {
            "title": "Data Quality Anomaly Detection",
            "description": (
                "Given daily record counts for 100 data tables over the past "
                "year, find tables where today's count deviates by more than "
                "3 standard deviations from the rolling 30-day average."
            ),
            "hints": [
                "What pattern computes rolling statistics?",
                "How do you efficiently track a 30-day window?",
            ],
            "patterns": ["Sliding Window", "Hash Map"],
            "approach": (
                "For each table, maintain a sliding window of the last 30 "
                "days of counts. Compute the mean and standard deviation "
                "within the window. Compare today's count against the "
                "threshold. Hash map stores per-table window state."
            ),
        },
        {
            "title": "Find Circular Dependencies",
            "description": (
                "Given a list of table dependencies (table_a depends on "
                "table_b), detect if any circular dependencies exist. "
                "Return the cycle if found."
            ),
            "hints": [
                "What data structure represents dependencies?",
                "What algorithm detects cycles in a directed graph?",
            ],
            "patterns": ["Graph", "DFS / Topological Sort"],
            "approach": (
                "Build a directed graph from the dependency list. Run DFS "
                "with three states (unvisited, in-progress, completed). "
                "If you visit an in-progress node, you've found a cycle. "
                "Alternatively, attempt topological sort - if it fails "
                "(not all nodes processed), a cycle exists."
            ),
        },
        {
            "title": "Optimal Batch Size",
            "description": (
                "Given a sorted list of file sizes and a maximum batch size, "
                "find the maximum number of files that can fit in one batch. "
                "Files must be consecutive in the sorted order."
            ),
            "hints": [
                "The data is sorted. What pattern works on sorted data?",
                "You need a contiguous range that satisfies a constraint.",
            ],
            "patterns": ["Sliding Window", "Binary Search"],
            "approach": (
                "Sliding window: maintain a running sum. Expand right until "
                "the sum exceeds the batch size, then shrink left. Track "
                "the maximum window size. Alternatively, binary search on "
                "the answer: for a given window size k, check if any k "
                "consecutive files fit."
            ),
        },
        {
            "title": "Top Error Producers",
            "description": (
                "Given a stream of 10 million log entries, find the top 10 "
                "error messages by frequency. Memory is limited to 100 MB."
            ),
            "hints": [
                "What pattern counts frequencies?",
                "What pattern extracts top-k efficiently?",
                "Could you use an approximate approach?",
            ],
            "patterns": ["Hash Map + Heap", "Count-Min Sketch (approximate)"],
            "approach": (
                "Exact: Hash map for frequency counting + min-heap of size "
                "10 for top-k extraction. If error messages are long and "
                "diverse, the hash map might exceed 100 MB. Approximate: "
                "Count-Min Sketch for frequency estimation + heap for "
                "candidates. Fixed memory regardless of cardinality."
            ),
        },
    ]


if __name__ == "__main__":
    print("=== Pattern Recognition Practice ===\n")
    print("  Try to identify the pattern(s) before reading the hints.\n")

    for i, problem in enumerate(practice_problems(), 1):
        print(f"  Problem {i}: {problem['title']}")
        print(f"  {problem['description']}")
        print()
        print(f"  Hints:")
        for hint in problem["hints"]:
            print(f"    - {hint}")
        print(f"  Patterns: {', '.join(problem['patterns'])}")
        print(f"  Approach: {problem['approach']}")
        print()
        print("  " + "-" * 60)
        print()
```

### `de_scenarios/pattern_recognition.md`

````markdown
# DE Scenario: Pattern Recognition Practice

## Real-World Context

In a real interview, nobody tells you which pattern to use. The problem is presented as a scenario and you must identify the approach. This scenario presents five DE-flavored problems without pattern labels. Try to identify the pattern(s) before reading the solution.

## Worked Example

Pattern recognition starts with identifying the key operation. "Group events into sessions" involves comparing consecutive elements (two pointers) in sorted data (sort). "Find circular dependencies" involves directed relationships (graph) and cycle detection (DFS). The pattern name emerges from the operation, not the domain.

```
Problem: "Find the top 10 error messages from 10M log entries with 100 MB memory limit"

Step 1: What's the core operation?
  Counting frequencies → Hash Map
  Extracting top-k → Heap

Step 2: Any constraints?
  100 MB memory limit. If error messages are diverse (high cardinality),
  a hash map of all messages might not fit.

Step 3: Do I need an approximate approach?
  If cardinality is low (e.g., 1000 unique errors), exact works fine.
  If cardinality is high (e.g., 1M unique errors with long messages),
  Count-Min Sketch + heap for fixed-memory approximation.

Step 4: State your approach
  "I'll use a hash map to count frequencies and a min-heap of size 10
  to track the top errors. If memory is a concern, I can switch to a
  Count-Min Sketch for O(1) memory frequency estimation."

This demonstrates pattern recognition AND engineering judgment
(knowing when exact vs approximate is appropriate).
```

## Practice Tips

1. **Identify the data structure first.** "I need fast lookups" → hash map. "I need sorted access" → heap or sorted array. "I have relationships" → graph.
2. **Look for the preprocessing opportunity.** Can I sort this? Can I build a hash map first? Preprocessing often unlocks a more efficient algorithm.
3. **State your pattern before coding.** "This looks like a sliding window problem because..." shows the interviewer you have a framework, not just memorized solutions.
4. **Combine patterns explicitly.** "Phase 1 uses a hash map for counting. Phase 2 uses a heap for selection." Clear structure impresses more than clever code.
````

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/12_combined_patterns/de_scenarios/*.py patterns/12_combined_patterns/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.12_combined_patterns.de_scenarios.pipeline_analysis 2>&1 | tail -10
echo ""
uv run python -m patterns.12_combined_patterns.de_scenarios.pattern_recognition 2>&1 | tail -10

echo ""
echo "=== Full Pattern 12 test suite ==="
uv run pytest patterns/12_combined_patterns/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Pattern 12 completeness ==="
echo "Problems:"
ls patterns/12_combined_patterns/problems/*.md 2>/dev/null | wc -l
echo "(should be 4)"
echo "DE Scenarios:"
ls patterns/12_combined_patterns/de_scenarios/*.md 2>/dev/null | wc -l
echo "(should be 2)"
echo "Worked Examples:"
grep -rl "## Worked Example" patterns/12_combined_patterns/ | wc -l
echo "(should be 6: 4 problems + 2 DE scenarios)"

echo ""
echo "=== Style check ==="
grep -r "—" patterns/12_combined_patterns/ && echo "❌ Em dashes found" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/12_combined_patterns/ && echo "❌ Wrong section name" || echo "✅ Correct section names"

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```
