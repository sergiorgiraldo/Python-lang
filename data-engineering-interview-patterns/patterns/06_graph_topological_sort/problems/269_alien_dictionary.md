# Alien Dictionary (LeetCode #269)

🔗 [LeetCode 269: Alien Dictionary](https://leetcode.com/problems/alien-dictionary/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

*This is a LeetCode Premium problem. The problem description below is written in our own words. If you have LeetCode Premium, the original is at https://leetcode.com/problems/alien-dictionary/.*

## Problem Statement

You're given a list of words sorted in an alien language's dictionary order. Derive the ordering of characters in that language. If no valid ordering exists (contradictions), return an empty string. If multiple valid orderings exist, return any one.

**Example:**
```
Input: words = ["wrt", "wrf", "er", "ett", "rftt"]
Output: "wertf"

Derivation:
  "wrt" vs "wrf": w=w, r=r, t vs f → t before f
  "wrf" vs "er":  w vs e → w before e
  "er" vs "ett":  e=e, r vs t → r before t
  "ett" vs "rftt": e vs r → e before r
```

**Constraints:**
- 1 <= words.length <= 100
- 1 <= words[i].length <= 100
- words[i] consists of lowercase English letters

---

## Thought Process

1. **Two steps** - Extract ordering constraints by comparing adjacent words. Topological sort those constraints.
2. **Extracting constraints** - Compare words[i] and words[i+1] character by character. The first differing position gives one edge. Characters after that tell us nothing.
3. **Edge case** - If words[i] is longer than words[i+1] but starts with words[i+1], the input is invalid.

---

## Worked Example

Given a sorted list of words in an alien language, infer the character ordering. Compare adjacent words to find ordering rules (which character comes before which), then topological sort those rules.

```
Input: words = ["wrt", "wrf", "er", "ett", "rftt"]

Step 1 - Extract ordering rules by comparing adjacent words:
  "wrt" vs "wrf": first difference at index 2 → t < f (t comes before f)
  "wrf" vs "er":  first difference at index 0 → w < e
  "er" vs "ett":  first difference at index 1 → r < t
  "ett" vs "rftt": first difference at index 0 → e < r

  Rules: t→f, w→e, r→t, e→r

Step 2 - Topological sort:
  Graph: w→e→r→t→f
  In-degrees: w:0, e:1, r:1, t:1, f:1
  Queue: [w]

  Process w→e drops to 0. Process e→r drops to 0.
  Process r→t drops to 0. Process t→f drops to 0.

  Order: w, e, r, t, f

Edge case: if "abc" comes before "ab" in the word list, that's
invalid (a longer prefix can't come before a shorter one). Return "".
```

---

## Approaches

### Approach 1: Kahn's Algorithm

<details>
<summary>💡 Hint</summary>

Extract one edge per adjacent word pair (first differing character), then topological sort.

</details>

<details>
<summary>📝 Explanation</summary>

Two-phase approach:

**Phase 1 - Extract ordering rules:** Compare each pair of adjacent words in the list. Find the first character position where they differ. That gives one ordering rule: `word1[pos] < word2[pos]` in the alien alphabet. If word1 is a prefix of word2, no rule is extracted. If word2 is a prefix of word1, the input is invalid (a shorter word can't come after its own prefix in a sorted list).

**Phase 2 - Topological sort:** Build a directed graph from the extracted rules. Run Kahn's algorithm. The result is the alien character order.

Edge cases: if topological sort detects a cycle, the ordering rules are contradictory. Return "". If some characters appear in words but have no ordering constraints relative to each other, they can appear in any position (multiple valid orderings exist).

**Time:** O(C) where C is the total length of all words (for extracting rules) plus O(V + E) for topological sort where V = unique characters and E = rules.
**Space:** O(V + E).

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict, deque

def alien_order(words):
    graph = defaultdict(set)
    in_degree = {c: 0 for word in words for c in word}
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break
    queue = deque(c for c in in_degree if in_degree[c] == 0)
    result = []
    while queue:
        char = queue.popleft()
        result.append(char)
        for neighbor in graph[char]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return "".join(result) if len(result) == len(in_degree) else ""
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Two words | `["z", "x"]` | `"zx"` | Simplest constraint |
| Cycle | `["z", "x", "z"]` | `""` | Contradictory ordering |
| Prefix violation | `["abc", "ab"]` | `""` | Longer before shorter prefix |
| Single word | `["abc"]` | Any permutation of a,b,c | No constraints |
| All same | `["a", "a"]` | `"a"` | No constraints to extract |

---

## Common Pitfalls

1. **Only using first differing character** - Characters after the first difference tell us nothing. Don't add extra edges.
2. **Missing prefix check** - "abc" before "ab" is invalid in any language. Many forget this.
3. **Duplicate edges** - Use a set for graph neighbors to avoid inflating in-degrees.
4. **Forgetting unconstrained characters** - Characters with no constraints must still appear in output.

---

## Interview Tips

**What to say:**
> "Two-step problem. First extract ordering constraints by comparing adjacent words - the first differing character gives one directed edge. Then topological sort. If the sort doesn't include all characters, there's a contradiction."

**What the interviewer evaluates:** This problem combines graph construction (extracting ordering from word comparisons) with topological sort. The construction phase is where most bugs occur. Handling edge cases (like a word that's a prefix of another but appears after it, which means invalid input) tests thoroughness. This is one of the harder graph problems and is typically used for senior+ interviews.

---

## DE Application

Constraint extraction + topological sort is the pattern behind:
- Schema evolution ordering from version comparison
- Configuration priority derived from implicit rules
- Custom sort orders based on business logic constraints

The key insight: sometimes the graph isn't given directly. You derive it from data (like these sorted words), then sort.

## At Scale

Building the character ordering graph from the word list is O(total characters). The topological sort is O(V + E) where V is the alphabet size (at most 26) and E is the ordering constraints (at most 26^2). This is a tiny graph regardless of how many words the dictionary has. At scale, the interesting application is schema inference: given sample data, infer column ordering, data types and constraints. This is a constraint satisfaction problem similar to inferring the alien alphabet from word ordering. For large datasets, sampling is sufficient - you don't need to examine every record to infer the schema.

---

## Related Problems

- [210. Course Schedule II](210_course_schedule_ii.md) - Topo sort with explicit edges (easier)
- [207. Course Schedule](207_course_schedule.md) - Cycle detection
