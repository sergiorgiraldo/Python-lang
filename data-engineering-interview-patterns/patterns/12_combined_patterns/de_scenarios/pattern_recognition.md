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
