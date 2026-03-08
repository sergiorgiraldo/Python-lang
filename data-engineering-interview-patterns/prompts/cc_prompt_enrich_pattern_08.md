# CC Prompt: Enrich Pattern 08 (Stack) to Principal Level

## Context

Pattern 08 has 6 problems and 4 DE scenarios (with the DE scenario count varying - check actual files). Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/08_stack/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

Stack operations (push/pop/peek) are O(1). The stack itself uses O(n) memory in the worst case (e.g., all opening brackets, no closers). For most problems, the stack size is bounded by something smaller than n.

| Problem type | Typical stack size | Memory at n=10M |
|---|---|---|
| Bracket matching | O(nesting depth), usually << n | Negligible |
| Expression evaluation | O(operands), usually << n | Negligible |
| Monotonic stack | O(n) worst case | ~80MB for indices |
| Next greater element | O(n) worst case | ~80MB for indices |

Stack algorithms are inherently sequential: each push/pop depends on the current state. They don't parallelize. This is usually fine because stack operations are fast and the data is processed in a single pass.

**Streaming context:** Stack-based algorithms work naturally on streams because they process elements left to right in a single pass. A bracket validator for streaming JSON doesn't need the full document in memory - just the stack of open brackets. In practice, streaming JSON parsers (like Python's ijson) use exactly this pattern. The memory is bounded by nesting depth, not document size.

**When stacks break at scale:** Recursive stack algorithms (DFS on deep graphs) can hit Python's recursion limit (~1000 by default). For very deep structures, convert to iterative with an explicit stack. This isn't about scale in the data-size sense but in the nesting-depth sense. A JSON document with 10K levels of nesting will crash recursive parsers.

### SQL equivalent

Stack operations don't have a direct SQL equivalent because SQL is set-based, not sequential. However, the problems stacks solve appear in SQL: bracket matching is structural validation (usually done outside SQL), expression evaluation is handled by the SQL parser itself, and the monotonic stack's "next greater element" can be computed with a self-join or window function: `SELECT a.val, MIN(b.val) FROM t a JOIN t b ON b.idx > a.idx AND b.val > a.val GROUP BY a.idx, a.val`. The window function approach is less efficient than the stack algorithm. Recursive CTEs can simulate stack-based traversal for hierarchical data.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 020_valid_parentheses.md
```markdown
## At Scale

The stack holds at most O(n) characters in the worst case (all openers). For a 1GB JSON file, worst case stack depth is the maximum nesting depth, typically a few hundred levels - not 1B characters. Memory is bounded by nesting depth, not input size. This makes bracket validation streaming-friendly: read characters one at a time, push/pop the stack and never hold the full input. Production JSON validators (Python's json module, streaming parsers like ijson) use exactly this approach. For validating files before ingestion in a pipeline, a streaming validator catches malformed data without loading the entire file.
```

### 155_min_stack.md
```markdown
## At Scale

Each entry uses O(1) extra memory (the min snapshot). For n=10M elements, the tuple approach uses ~240MB (three values per entry: value, min, pointer). The two-stack approach uses less if the minimum changes infrequently. In production, the interesting application is maintaining running statistics over a data stream with O(1) query time. The trade-off: O(n) memory to maintain the history. If you only need the current min (not the ability to pop and restore), a single variable suffices with O(1) memory. The stack-based approach is specifically for "undo-able" minimum tracking.
```

### 150_eval_rpn.md
```markdown
## At Scale

The stack holds at most O(n/2) operands - roughly half the tokens. For 1M-token expressions, that's ~4MB. Expression evaluation is sequential and doesn't parallelize. At scale, the practical concern is precision: floating-point accumulation errors compound over long expressions. Financial calculations use decimal types, not floats. In data pipelines, expression evaluation appears in computed columns: config-driven transformations like `revenue - cost * tax_rate`. Template engines (Jinja in dbt, expression languages in Spark) parse and evaluate these using stack-based approaches internally.
```

### 739_daily_temperatures.md
```markdown
## At Scale

The monotonic stack stores indices, not values: O(n) memory in the worst case (all decreasing temperatures). For 10M days, that's ~80MB of indices. The O(n) time guarantee (each element pushed and popped at most once) makes this efficient for very large time series. At scale, "next event exceeding a threshold" is a common monitoring query. The monotonic stack answers this in a single pass, but it requires the full sequence. For streaming time series, you can maintain a monotonic stack over a sliding window - new elements enter from the right, stale elements expire from the left. This gives you real-time "time until next spike" metrics.
```

### 853_car_fleet.md
```markdown
## At Scale

Sort + stack: O(n log n) time, O(n) memory. For 10M cars, sorting takes ~3 seconds, the stack pass takes ~50ms. The sorting step dominates. At scale, car fleet is an abstraction for task scheduling with dependencies: "which tasks catch up to (are blocked by) slower tasks ahead?" In pipeline scheduling, a fast task following a slow dependency is effectively in a "fleet" with the slow task - it can't finish faster than its predecessor. Understanding this bottleneck analysis helps with pipeline optimization: the fleet count tells you how many independent execution streams exist, which is your maximum parallelism.
```

### 084_largest_rectangle.md
```markdown
## At Scale

The monotonic increasing stack approach is O(n) time and O(n) memory. For 10M histogram bars, that's ~80MB and completes in ~100ms. The brute force O(n^2) approach would take hours. At scale, the largest rectangle problem appears in resource allocation: "given varying capacity over time, what's the maximum sustained load I can handle?" The rectangle area (height * width) represents sustained throughput over a time period. In capacity planning, finding these rectangles across different time windows helps identify optimal maintenance windows and scaling triggers. The stack-based O(n) solution is essential because capacity data can span millions of time points.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 020 (Valid Parentheses):
```markdown
**What the interviewer evaluates:** This is the canonical "do you know stacks?" problem. Clean, fast execution is expected. The dict mapping closers to openers is the standard approach. Mentioning streaming validation for large files shows production awareness. This is usually a warm-up.
```

### 155 (Min Stack):
```markdown
**What the interviewer evaluates:** Combining two data structures (stack + min tracking) tests design thinking. The tuple approach is simpler; the two-stack approach optimizes space. Explaining WHY popping restores the correct minimum (the snapshot argument) shows understanding, not memorization.
```

### 150 (Eval RPN):
```markdown
**What the interviewer evaluates:** Operand order for subtraction and division (second-popped is the left operand) is where bugs hide. Division truncation toward zero (not floor division) is a Python-specific gotcha. Clean implementation with an operator dict shows good coding style. The interviewer likely has follow-up problems about infix evaluation or additional operators.
```

### 739 (Daily Temperatures):
```markdown
**What the interviewer evaluates:** The monotonic stack is a non-obvious choice. Explaining the O(n) amortized analysis (each element pushed once, popped once, total 2n operations despite nested loops) is the key differentiator. Candidates who can explain WHY this is O(n) demonstrate deeper algorithmic understanding than those who just implement it.
```

### 853 (Car Fleet):
```markdown
**What the interviewer evaluates:** The sort-by-position + arrival-time-stack combination tests multi-step reasoning. Understanding that a slower car ahead blocks faster cars behind it (forming a fleet) tests physical intuition. Connecting this to pipeline dependency bottlenecks shows engineering judgment.
```

### 084 (Largest Rectangle):
```markdown
**What the interviewer evaluates:** This is a hard problem. The monotonic increasing stack with sentinel values is a common technique. Most candidates struggle with what happens when you pop (computing the width using the new top of stack as the left boundary). Walking through a complete example with the interviewer demonstrates composure under complexity. This problem is often the final, hardest problem in an interview set.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **monotonic stack**: Stack maintaining elements in sorted order (increasing or decreasing). New elements that violate the invariant cause pops, resolving the popped elements. O(n) amortized because each element is pushed and popped at most once.
- **streaming parser**: Parser that processes input incrementally without loading the entire document. Uses bounded memory regardless of input size. Examples: SAX (XML), ijson (JSON).
- **nesting depth**: Maximum depth of nested structures (brackets, tags, function calls). Determines stack memory usage for recursive/stack-based parsers.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/08_stack/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/08_stack/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/08_stack/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/08_stack/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/08_stack/ --tb=short -q 2>&1 | tail -3
```
