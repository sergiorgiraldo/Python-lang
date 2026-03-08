# CC Prompt: Enrich Pattern 04 (Sliding Window) to Principal Level

## Context

Pattern 04 has 8 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files
- Only ADD content to .md files
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/04_sliding_window/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

Sliding window algorithms process each element exactly once (or twice: once entering, once leaving). This makes them inherently streaming-friendly: you don't need the full dataset in memory, just the current window state.

| Window type | Memory usage | Input size dependency |
|---|---|---|
| Fixed-size window (k) | O(k) | Independent of n |
| Variable window with hash map | O(unique elements in window) | Usually << n |
| Variable window with deque (max/min) | O(k) worst case | Bounded by window size |

**Streaming context:** Sliding windows map directly to stream processing frameworks. Kafka Streams, Flink and Spark Structured Streaming all have first-class window operations: tumbling (non-overlapping), sliding (overlapping) and session (gap-based) windows. The window state is maintained incrementally - exactly like the algorithmic pattern.

**Memory concern at scale:** The window state is usually small (O(k) or O(alphabet)). The risk is when the window itself is large. A 30-day sliding window over events at 1M events/day means the window holds 30M events. If you need all events in the window (not just aggregates), that's ~2.4GB. Incremental aggregation (maintain running sum, subtract exiting elements) avoids storing individual events.

### SQL equivalent

Window functions in SQL (`OVER (ORDER BY ... ROWS BETWEEN ...)`) implement the sliding window pattern. `SUM(amount) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)` is a 30-day rolling sum. The SQL engine maintains the window state internally. For large windows, the engine may need to materialize the window frame, so performance depends on window size. The SQL section's window functions subsection covers these patterns in depth.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 643_max_average_subarray.md (or actual filename)
```markdown
## At Scale

Fixed-size sliding window uses O(1) memory regardless of input size. For 1B elements with window size 1000, you store only the running sum and the window boundaries. The computation is dominated by I/O (reading the data) not memory or CPU. In streaming systems, this is a tumbling or sliding window aggregate: `SELECT AVG(value) OVER (ORDER BY timestamp ROWS BETWEEN 999 PRECEDING AND CURRENT ROW)`. At scale, the concern shifts from algorithm efficiency to data freshness: how quickly does the window update as new data arrives? Micro-batch (Spark) updates every few seconds; true streaming (Flink) updates per event.
```

### 219_contains_duplicate_ii.md
```markdown
## At Scale

The sliding window of size k uses O(k) memory (a hash set of the current window). For k=1000, that's negligible. For very large k (millions), the set grows proportionally. The brute force O(n*k) approach is unacceptable at scale: 1B elements with k=1M means 10^15 operations. The sliding window reduces this to O(n) regardless of k. In production, "find duplicates within a time window" is an event dedup problem. Streaming dedup with a window is standard in event pipelines: maintain a set of recently seen IDs, expire entries older than the window.
```

### 003_longest_substring.md
```markdown
## At Scale

The hash set tracks characters in the current window. For ASCII input, that's at most 128 entries - O(1) space regardless of string length. For Unicode, the set could grow to thousands of entries but is still bounded by the character set, not the string length. At 1B characters, the single-pass O(n) algorithm takes ~10 seconds. The practical equivalent in data pipelines: finding the longest period of unique events in a time series. In SQL: a self-join or window function approach, though the sliding window algorithm is more efficient than what most SQL engines generate for this type of query.
```

### 424_longest_repeating_replacement.md
```markdown
## At Scale

The character frequency array uses O(26) = O(1) space. The sliding window makes a single pass through the string. At 1B characters, this takes ~10 seconds and uses essentially zero extra memory. The "maximum frequency in the window" optimization avoids recalculating the mode each step. In data quality contexts, this pattern answers "what's the longest run of near-consistent values?" For sensor data or time series, finding the longest period where a metric stays within tolerance (allowing k exceptions) is the same structure. The window grows while the "error budget" (replacements allowed) isn't exhausted.
```

### 567_permutation_in_string.md
```markdown
## At Scale

Fixed window of size len(s1) with a character frequency comparison. Memory is O(26) = O(1). The "matches" counter avoids comparing full frequency arrays each step, making each window slide O(1). At 1B characters in s2, this takes ~10 seconds with constant memory. The pattern generalizes to "does any window of size k contain the exact same distribution as a reference?" In data pipelines, this appears as pattern matching in event streams: "did these 5 specific event types all occur within any 10-minute window?"
```

### 438_find_anagrams.md
```markdown
## At Scale

Same as Permutation in String (567) but returns all matching positions instead of a boolean. Memory and time complexity are identical: O(1) space, O(n) time. At scale, the concern is output size: if matches are frequent, the result list grows. For 1B characters with matches every 100 positions, that's 10M matches (~80MB of indices). Streaming this as an iterator (yield positions as found) avoids materializing the full result. In SQL, this type of pattern matching uses window functions: `COUNT(*) OVER (ROWS BETWEEN k PRECEDING AND CURRENT ROW)` with a HAVING-like filter.
```

### 239_sliding_window_maximum.md
```markdown
## At Scale

The monotonic deque approach uses O(k) memory and O(n) time. For k=1000 and n=1B, that's negligible memory and ~10 seconds of processing. The brute force O(n*k) approach would take hours. The deque maintains the invariant that elements are decreasing from front to back. This same structure appears in stream processing as a "sliding window max/min" aggregate. Flink and Kafka Streams implement this internally for time-windowed aggregations. At scale, the deque-based approach is cache-friendly because it processes elements sequentially. The practical concern is window alignment: in time-series data, windows are aligned to clock boundaries (every minute, every hour), not to arbitrary positions.
```

### 076_min_window_substring.md
```markdown
## At Scale

The hash map tracking character frequencies uses O(|t|) space where t is the target string. For typical inputs, this is tiny. The string s is processed in a single pass: O(n) time. At 1B characters in s, this takes ~10 seconds. The variable-size window pattern (expand right to satisfy, shrink left to minimize) is the most complex sliding window variant. In production, this answers questions like "what's the shortest time period containing all required event types?" In SQL, this requires a self-join or correlated subquery approach that's much less efficient than the algorithmic solution. For real-time monitoring ("alert when all critical events have occurred within a short window"), the streaming implementation maintains the character/event frequency map as state.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 643 (Max Average):
```markdown
**What the interviewer evaluates:** This is a warm-up. Clean O(n) with O(1) space is expected quickly. The interviewer is testing whether you know the fixed-size sliding window template. Finishing fast earns time for harder follow-ups.
```

### 219 (Contains Duplicate II):
```markdown
**What the interviewer evaluates:** Combining a sliding window with a hash set tests whether you can compose patterns. The window maintains the distance constraint, the set maintains the uniqueness check. Mentioning streaming dedup shows you've internalized the production application.
```

### 003 (Longest Substring):
```markdown
**What the interviewer evaluates:** Variable-size windows are harder than fixed-size. The expand/shrink logic tests your ability to manage two pointers with a state invariant. Getting the shrink condition right (when to move left) is where most candidates struggle. A clean implementation with clear variable names is a strong signal.
```

### 424 (Longest Repeating Replacement):
```markdown
**What the interviewer evaluates:** The "replacements budget" concept makes the window condition non-trivial. You need to realize that the window is valid when (window size - max frequency) <= k. The insight that max_freq doesn't need to decrease when the window shrinks is the optimization that impresses.
```

### 567 (Permutation in String):
```markdown
**What the interviewer evaluates:** The "matches" counter optimization (comparing one character at a time instead of full arrays) tests whether you think about unnecessary work. A candidate who compares 26-element arrays every step gets O(26n) = O(n), but the constant factor matters for very large inputs. The optimization to O(1) per step shows attention to practical performance.
```

### 438 (Find Anagrams):
```markdown
**What the interviewer evaluates:** Nearly identical to 567. If asked both in sequence, the interviewer tests whether you can adapt your solution (return list instead of boolean) without starting over. Reusing your sliding window template with a minor output change is the right move.
```

### 239 (Sliding Window Maximum):
```markdown
**What the interviewer evaluates:** The monotonic deque is a non-obvious data structure choice. This tests whether you know data structures beyond arrays and hash maps. Explaining WHY the deque maintains a decreasing order (because elements that are both older and smaller can never be the maximum) is the key insight. This problem is frequently used for senior+ interviews.
```

### 076 (Min Window Substring):
```markdown
**What the interviewer evaluates:** This is a hard problem combining variable windows with character frequency tracking. The "have" counter optimization (tracking how many unique characters are satisfied) avoids O(26) comparisons per step. This tests both pattern knowledge and implementation precision. At principal level, discussing the streaming application and comparing to SQL approaches shows breadth.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **tumbling window**: Non-overlapping fixed-size time window in stream processing. Each event belongs to exactly one window.
- **sliding window (streaming)**: Overlapping fixed-size time window. An event may belong to multiple windows. More expensive than tumbling due to overlap.
- **session window**: Variable-size window defined by inactivity gaps. A new window starts when the gap between events exceeds a threshold.
- **incremental aggregation**: Maintaining an aggregate (sum, count, max) by updating it incrementally as elements enter/leave a window, rather than recomputing from scratch.
- **window state**: The data maintained by a stream processing operator for each active window. Must be checkpointed for fault tolerance.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/04_sliding_window/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/04_sliding_window/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/04_sliding_window/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/04_sliding_window/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/04_sliding_window/ --tb=short -q 2>&1 | tail -3
```
