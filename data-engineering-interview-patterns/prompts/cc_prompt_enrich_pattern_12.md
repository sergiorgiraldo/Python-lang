# CC Prompt: Enrich Pattern 12 (Combined Patterns) to Principal Level

## Context

Pattern 12 has 4 problems (621, 787, 895, 692 - freshly replaced) and 2 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/12_combined_patterns/README.md`, find `## Trade-offs` and ADD:

```markdown
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

The SQL section's optimization subsection covers the SQL equivalents of these combinations: GROUP BY + ORDER BY LIMIT (counting + selection), recursive CTEs with cost tracking (graph + constraint), and window functions with custom ordering.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 621_task_scheduler.md
```markdown
## At Scale

The counting phase processes all n tasks: O(n). For 1B tasks with 26 task types, the Counter uses ~2KB. The math formula computes the answer in O(1) after counting. At scale, task scheduling with cooldowns is a real production problem: Airflow's scheduler spaces out tasks that write to the same table to avoid lock contention. The greedy "most frequent first" strategy minimizes idle time. In distributed scheduling, the challenge is that the global view (all task frequencies) must be maintained centrally while execution happens across workers. Spark's task scheduler uses a similar priority queue internally, though the optimization target is data locality rather than cooldown constraints.
```

### 787_cheapest_flights.md
```markdown
## At Scale

Bellman-Ford variant runs O(K * E) where K is the stop limit. For a network with 10K nodes and 100K edges with K=5, that's 500K edge relaxations - milliseconds. For larger graphs (1M nodes, 10M edges), it's still fast because K is usually small. The copy-per-round technique uses O(V) memory per round. At scale, constrained shortest path is a real routing problem: "transfer data through at most 3 intermediate regions to minimize latency and cost." Cloud network routing (selecting the cheapest path between data centers with hop limits) uses similar algorithms. The distributed version partitions the graph and uses iterative message passing (Pregel model), with each superstep corresponding to one Bellman-Ford round.
```

### 895_max_freq_stack.md
```markdown
## At Scale

All operations are O(1). Memory is O(n) for n pushed elements (each element exists in multiple frequency groups, but the total references are bounded by the total pushes). For 10M pushes, that's ~200MB. The data structure doesn't benefit from distribution because the frequency ordering is global state. At scale, the pattern appears in priority event processing: "handle the most frequent alert type first, breaking ties by recency." In a monitoring system processing 1M alerts/minute, the O(1) push/pop is essential. A log(n) alternative (heap) would also work but the constant factor matters at high throughput. Redis sorted sets provide a similar frequency + recency ordering in production.
```

### 692_top_k_words.md
```markdown
## At Scale

The counting phase dominates: O(n) for all words, O(d) memory for d unique words. For 1B words with 10M unique words, the Counter uses ~2GB. The heap phase processes d unique words with a heap of size k: O(d log k). For k=100, the heap is negligible. At scale, this is a classic MapReduce problem: each mapper counts local word frequencies, reducers merge counts and extract top-k. The custom comparator (frequency descending, then lexicographic ascending for ties) is the twist that makes this harder than basic top-k. In SQL: `GROUP BY word ORDER BY count DESC, word ASC LIMIT k`. The SQL optimizer handles the multi-key sort internally. Spark's approach: `groupBy("word").count().orderBy(desc("count"), asc("word")).limit(k)`.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 621 (Task Scheduler):
```markdown
**What the interviewer evaluates:** Recognizing the frequency counting + greedy scheduling decomposition tests pattern composition. Starting with the heap simulation (shows the process) and then mentioning the math formula (shows deeper understanding) is the ideal progression. The interviewer may ask "what if tasks have different durations?" - this breaks the math formula and requires the simulation approach. Handling follow-ups that invalidate your elegant solution gracefully shows maturity.
```

### 787 (Cheapest Flights):
```markdown
**What the interviewer evaluates:** Recognizing that standard Dijkstra fails (and explaining WHY - it doesn't track hop count) is the first hurdle. Choosing Bellman-Ford over modified Dijkstra shows judgment: Bellman-Ford is simpler and more robust for this variant. Explaining the copy-per-round trick (preventing same-round chaining) is the implementation detail that separates correct from incorrect solutions. The follow-up "what about negative edge weights?" (answer: Bellman-Ford already handles them) shows algorithmic breadth.
```

### 895 (Max Freq Stack):
```markdown
**What the interviewer evaluates:** This is a hard design problem. The "element exists at multiple frequency levels" insight is non-obvious. Most candidates try a heap (O(log n) per operation) before discovering the O(1) approach. Walking through the data structure state step by step with the interviewer is essential - the design is hard to verify without a trace. The follow-up "what about thread safety?" or "what about persistence?" pivots toward system design.
```

### 692 (Top K Words):
```markdown
**What the interviewer evaluates:** The custom comparator is the key detail. In Python, the `__lt__` wrapper class is necessary because heapq doesn't support custom key functions. Explaining WHY the min-heap comparison is inverted for tie-breaking (lexicographically larger is "smaller" in heap terms, so it gets popped first and the lexicographically smaller word survives) demonstrates deep understanding of heap mechanics. Mentioning both heap (O(n log k)) and sort (O(n log n)) approaches with their tradeoffs shows completeness.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **pattern composition**: Combining two or more algorithmic patterns to solve a problem that neither pattern addresses alone. The ability to decompose problems into known patterns is a key interview skill.
- **pipeline stage decomposition**: Breaking a multi-pattern algorithm into sequential stages that can be independently parallelized or optimized. Maps to ETL stages in data pipelines.
- **constrained shortest path**: Shortest path with an additional constraint (max hops, required waypoints, time windows). Standard algorithms must be modified to track the constraint alongside distance.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/12_combined_patterns/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics\|meta-skill" patterns/12_combined_patterns/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/12_combined_patterns/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/12_combined_patterns/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/12_combined_patterns/ --tb=short -q 2>&1 | tail -3
```
