# Combined Patterns

## What Is It?

### Beyond single-pattern problems

Patterns 01-11 each teach one technique in isolation. Real interview problems rarely announce which pattern to use. More importantly, many problems require two or more patterns working together: count frequencies with a hash map, then greedily schedule with a heap. Build a graph, then constrain traversal with Bellman-Ford rounds. Track frequencies in a hash map, then layer stacks on top for O(1) access.

This section practices the skill of pattern recognition and composition. Each problem requires identifying which patterns apply and combining them into a solution where neither pattern alone is sufficient.

### How patterns combine

The combinations in this section's problems:

**Hash Map + Heap + Greedy (Patterns 01 + 05)**
Count frequencies with a hash map. Use a max-heap to greedily select the best candidate each step. A cooldown or constraint queue manages eligibility. Example: Task Scheduler schedules the most frequent available task each interval.

**Graph + Constrained BFS (Patterns 06 + Modified Dijkstra/Bellman-Ford)**
Standard shortest-path algorithms assume you only care about cost. Adding constraints (hop limits, capacity) requires modifying the traversal. Bellman-Ford's round-based relaxation naturally limits hops. Modified Dijkstra tracks constraint state alongside cost. Example: Cheapest Flights within K stops.

**Hash Map + Stack (Patterns 01 + 08)**
A hash map tracks element properties (frequency, count, state). A stack provides LIFO ordering within each property level. Together they enable data structures that combine priority with recency. Example: Maximum Frequency Stack uses frequency-indexed stacks.

**Hash Map + Heap with Custom Ordering (Patterns 01 + 05)**
When top-k selection needs multi-level sorting (frequency first, then alphabetical for ties), the heap needs a custom comparator. The hash map counts, the heap selects, and the comparator class bridges the two patterns. Example: Top K Frequent Words with lexicographic tie-breaking.

### Pattern recognition in interviews

The hardest part of a coding interview isn't implementing the solution. It's figuring out which approach to use. Here are recognition signals:

| If you see... | Think... |
|---|---|
| "Schedule with cooldown / spacing constraints" | Hash map + heap (greedy) |
| "Shortest path with hop/stop limit" | Graph + Bellman-Ford or modified Dijkstra |
| "Pop most frequent / most priority" | Hash map + stack or heap |
| "Top K with tie-breaking rules" | Hash map + heap (custom comparator) |
| "Find all pairs/triplets that sum to X" | Sort + two pointers |
| "Smallest window/substring containing..." | Sliding window + hash map |
| "Shortest path / minimum cost" | Graph + heap (Dijkstra) |
| "Is this element in a large set?" | Hash set or Bloom filter |

When you don't immediately recognize the pattern, ask yourself:
1. What data structure would make the key operation fast?
2. Do I need to process things in a specific order?
3. Is there a preprocessing step that simplifies the main logic?

### Connection to data engineering

In DE work, you rarely solve problems with a single tool:
- **ETL pipelines** combine hashing (dedup) + sorting (merge joins) + graph traversal (dependency resolution)
- **Query optimization** combines hash joins + sort-merge joins + index lookups based on data characteristics
- **Data quality** combines frequency counting (hash maps) + anomaly detection (statistical thresholds) + lineage tracking (graphs)
- **Task scheduling** combines frequency analysis + priority queues + constraint satisfaction

The ability to recognize which technique applies where and compose them effectively is what separates senior from principal engineers.

### What the problems in this section cover

| Problem | Patterns Combined | What it teaches |
|---|---|---|
| Task Scheduler | Hash Map + Heap + Greedy | Frequency-driven scheduling with constraints |
| Cheapest Flights | Graph + Constrained BFS | Shortest path with hop limits |
| Max Frequency Stack | Hash Map + Stack | O(1) frequency-aware data structure design |
| Top K Frequent Words | Hash Map + Heap (custom comparator) | Multi-level sort in top-k selection |

## When to Use It

This isn't a pattern you "use." It's a skill you develop. Every problem in patterns 01-11 is practice for the real interview, where problems combine multiple techniques and don't come with labels.

## Visual Aid

```
How combined patterns solve Task Scheduler:

Tasks: [A, A, A, B, B, B], cooldown n=2

Phase 1: Hash Map counts frequencies
  {A: 3, B: 3}

Phase 2: Build frame from most frequent task
  max_freq = 3, count_at_max = 2

  Frame structure (n+1 slots per chunk):
  +-------+-------+-------+
  | A B _ | A B _ | A B   |   <- final chunk: only max-freq tasks
  +-------+-------+-------+
   chunk 1  chunk 2  final

  (max_freq - 1) full chunks of (n+1) + count_at_max
  = (3-1) * (2+1) + 2
  = 6 + 2 = 8 intervals

  If more task types existed (C, D, E...), they fill the _ slots.
  When all slots are filled: answer = len(tasks) (no idle needed).
```

## Trade-offs

**Preprocessing cost vs main loop efficiency:**
Sorting costs O(n log n) but enables O(n) two-pointer scans. Building a hash map costs O(n) but enables O(1) lookups. The preprocessing is always worth it when it reduces the main loop's complexity by a factor of n or more.

**Space vs time:**
Hash maps trade O(n) space for O(1) lookups. Heaps use O(k) space for top-k problems. Sometimes you can avoid extra space by sorting in-place, but this modifies the input.

**Simulation vs formula:**
Heap simulation is general and easy to extend (Task Scheduler). Math formulas are faster but problem-specific and harder to derive. In interviews, start with the simulation (shows pattern thinking), then mention the formula (shows depth).

### Scale characteristics

Combined-pattern problems have composite complexity. The bottleneck is usually one phase:

| Problem | Phase 1 | Phase 2 | Bottleneck |
|---|---|---|---|
| Task Scheduler | O(n) counting | O(n) heap simulation | Counting (data volume) |
| Cheapest Flights | O(V+E) graph build | O(K*E) Bellman-Ford | Relaxation rounds |
| Max Freq Stack | O(1) per push | O(1) per pop | Neither (all O(1)) |
| Top K Words | O(n) counting | O(n log k) heap | Counting (data volume) |

The general principle: when combining patterns, the total complexity is dominated by the most expensive phase. Optimize the bottleneck, not the fast parts.

**Distributed combined patterns:** In production, multi-pattern solutions decompose into pipeline stages. Task scheduling becomes: count frequencies (map phase, embarrassingly parallel), then schedule (single-node, small state). Top-k-with-custom-ordering becomes: count per partition, merge counts, heap-extract globally. The pattern composition maps naturally to ETL stages. Understanding which phase can parallelize and which must be centralized is the principal-level insight.

### The meta-skill

The problems in this section aren't harder algorithms. They're harder RECOGNITION. The ability to look at a problem and say "this is counting + selection, so hash map + heap" or "this is shortest path with a constraint, so modified BFS" is what separates prepared candidates from strong engineers. This skill transfers directly to production: looking at a data pipeline requirement and decomposing it into known patterns is the core of technical design.

### Cross-section connections

These problems bridge the entire patterns section:
- Task Scheduler uses Pattern 01 (Hash Map) + Pattern 05 (Heap)
- Cheapest Flights uses Pattern 06 (Graph) + modified Pattern 05 (Heap)
- Max Freq Stack uses Pattern 01 (Hash Map) + Pattern 08 (Stack)
- Top K Words uses Pattern 01 (Hash Map) + Pattern 05 (Heap)

The SQL section's optimization subsection covers the SQL equivalents of these combinations: GROUP BY + ORDER BY LIMIT (counting + selection), recursive CTEs with cost tracking (graph + constraint) and window functions with custom ordering.

## Problems in This Section

| # | Problem | Difficulty | Patterns Combined |
|---|---|---|---|
| [621](https://leetcode.com/problems/task-scheduler/) | [Task Scheduler](problems/621_task_scheduler.md) | Medium | Hash Map + Heap + Greedy |
| [787](https://leetcode.com/problems/cheapest-flights-within-k-stops/) | [Cheapest Flights](problems/787_cheapest_flights.md) | Medium | Graph + Modified BFS |
| [895](https://leetcode.com/problems/maximum-frequency-stack/) | [Max Frequency Stack](problems/895_max_freq_stack.md) | Hard | Hash Map + Stack |
| [692](https://leetcode.com/problems/top-k-frequent-words/) | [Top K Frequent Words](problems/692_top_k_words.md) | Medium | Hash Map + Heap (custom comparator) |

## DE Scenarios

| Scenario | Patterns | Real-World Use |
|---|---|---|
| [Multi-Pattern Pipeline](de_scenarios/pipeline_analysis.md) | Hash + Graph + Heap | End-to-end pipeline optimization |
| [Pattern Recognition Practice](de_scenarios/pattern_recognition.md) | All | Interview simulation with unlabeled problems |
