# Top K Frequent Words (LeetCode #692)

🔗 [LeetCode 692: Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a list of words, return the k most frequent words sorted by frequency (highest first). If two words have the same frequency, sort them lexicographically (alphabetical order).

## Thought Process

1. **Almost like Top K Frequent Elements (#347):** Count with a hash map, select with a heap. But the tie-breaking rule (lexicographic order) adds complexity.
2. **Custom heap comparison:** Python's heapq is a min-heap with no custom comparator. We need a wrapper class that defines `__lt__` to handle our two-level sorting: frequency (descending) then lexicographic order (ascending).
3. **The trick for min-heap:** In a min-heap of size k, we pop the "least desirable" element. So "least desirable" means: lowest frequency, and for ties, lexicographically largest (the opposite of what we want to keep).

## Worked Example

The custom comparator is where the two patterns connect. A basic hash map + heap solves the frequency ranking, but the tie-breaking rule means the heap needs to understand word ordering. Without the custom comparison, tied words come out in arbitrary order.

```
words = ["i", "love", "leetcode", "i", "love", "coding"], k=2

Phase 1: Hash Map
  Counter: {"i": 2, "love": 2, "leetcode": 1, "coding": 1}

Phase 2: Min-Heap of size k=2 with custom comparison

  Push WordFreq("i", 2):     heap size 1 <= k
  Push WordFreq("love", 2):  heap size 2 <= k
  Push WordFreq("leetcode", 1): heap size 3 > k
    Pop smallest: WordFreq("leetcode", 1) removed (freq 1 < freq 2)
    heap = [WordFreq("love", 2), WordFreq("i", 2)]

  Push WordFreq("coding", 1): heap size 3 > k
    Pop smallest: WordFreq("coding", 1) removed
    heap = [WordFreq("love", 2), WordFreq("i", 2)]

  Extract in reverse: pop "love", pop "i" -> reversed: ["i", "love"]

  Why "i" before "love"? Both have freq 2.
  Tie-break: lexicographic order -> "i" < "love".

  Custom __lt__ for min-heap:
    WordFreq("love", 2) < WordFreq("i", 2)?
    Same freq -> compare words in REVERSE: "love" > "i" -> True
    So "love" is "smaller" in heap terms -> would be popped first.
    This means "i" survives, which is what we want (it sorts first).
```

## Approaches

### Approach 1: Hash Map + Min-Heap with Custom Comparator

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map (Counter) for frequency counting + min-heap for top-k selection. The custom comparator (via a wrapper class with `__lt__`) handles the two-level sort.

Count frequencies. For each word, push a WordFreq object onto a min-heap. If heap exceeds k, pop. The min-heap pops the "least desirable" word: lowest frequency, and among ties the lexicographically largest (since we want to keep the smallest).

After processing all words, extract from the heap in reverse order (heap gives smallest first, we want largest first).

The wrapper class is necessary because Python's heapq doesn't support custom key functions. The `__lt__` method defines: lower frequency is "less than" (popped first), and for equal frequency, lexicographically later is "less than" (popped first, keeping earlier words).

**Time:** O(n log k). Counter is O(n). Each of at most n heap operations is O(log k).
**Space:** O(n) for the counter, O(k) for the heap.

</details>

### Approach 2: Hash Map + Sort

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map for counting + built-in sort with a key function.

Count frequencies. Sort all unique words by (-frequency, word). Take the first k.

The sort key `(-frequency, word)` handles both levels: negating frequency gives descending order, and Python's default string comparison gives ascending lexicographic order for ties.

Simpler to implement but O(n log n) instead of O(n log k). For small k relative to n, the heap approach is significantly faster.

**Time:** O(n log n) for the sort.
**Space:** O(n).

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| All words same frequency | Lexicographic order | Tie-breaking rule applies to everything |
| k = number of unique words | All words, sorted | Return everything |
| Single word repeated | That word | Only one unique word |

## Interview Tips

> "I'll count frequencies with a Counter, then use a min-heap of size k. The twist is the tie-breaking rule: I need a custom comparator. In Python, I'll wrap word-frequency pairs in a class with `__lt__` that handles both frequency (descending) and lex order (ascending)."

**Demonstrate understanding of Python's heap limitations.** Mentioning that heapq doesn't support custom key functions and explaining the wrapper pattern shows language mastery.

**What the interviewer evaluates:** The custom comparator is the key detail. In Python, the `__lt__` wrapper class is necessary because heapq doesn't support custom key functions. Explaining WHY the min-heap comparison is inverted for tie-breaking (lexicographically larger is "smaller" in heap terms, so it gets popped first and the lexicographically smaller word survives) demonstrates deep understanding of heap mechanics. Mentioning both heap (O(n log k)) and sort (O(n log n)) approaches with their tradeoffs shows completeness.

## DE Application

Finding the top error messages or most common query patterns in log data. The tie-breaking rule matters when you need deterministic, reproducible rankings for dashboards and reports. Alphabetical ordering for ties ensures consistent display.

## At Scale

The counting phase dominates: O(n) for all words, O(d) memory for d unique words. For 1B words with 10M unique words, the Counter uses ~2GB. The heap phase processes d unique words with a heap of size k: O(d log k). For k=100, the heap is negligible. At scale, this is a classic MapReduce problem: each mapper counts local word frequencies, reducers merge counts and extract top-k. The custom comparator (frequency descending, then lexicographic ascending for ties) is the twist that makes this harder than basic top-k. In SQL: `GROUP BY word ORDER BY count DESC, word ASC LIMIT k`. The SQL optimizer handles the multi-key sort internally. Spark's approach: `groupBy("word").count().orderBy(desc("count"), asc("word")).limit(k)`.

## Related Problems

- [347. Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) - Same structure without tie-breaking
- [451. Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) - Similar, character level
