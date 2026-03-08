# Valid Anagram (LeetCode #242)

🔗 [LeetCode 242: Valid Anagram](https://leetcode.com/problems/valid-anagram/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` and `false` otherwise.

An anagram uses all the original letters exactly once, rearranged.

**Example:**
```
Input: s = "anagram", t = "nagaram"
Output: true

Input: s = "rat", t = "car"
Output: false
```

**Constraints:**
- 1 <= s.length, t.length <= 5 * 10^4
- s and t consist of lowercase English letters

---

## Thought Process

1. **Quick check** - If lengths differ, it's impossible. Return false immediately.
2. **Brute force** - Sort both strings and compare. O(n log n).
3. **Optimize** - Count character frequencies. If both strings have the same frequency distribution, they're anagrams. O(n).

---

## Worked Example

Two strings are anagrams if they contain the same characters in the same quantities, just rearranged. "racecar" and "carrace" both have two r's, two a's, two c's and one e.

The dict key here is each character and the value is how many times it appears (the count). We count characters in both strings and compare the counts. Python's `Counter` from the collections module does exactly this - it takes a string and returns a dict of character counts.

```
Input: s = "racecar", t = "carrace"

Counter approach:
  Counter("racecar") = {'r': 2, 'a': 2, 'c': 2, 'e': 1}
  Counter("carrace") = {'c': 2, 'a': 2, 'r': 2, 'e': 1}
  Same counts → True (valid anagram)

  Under the hood, Counter is just a dict. Comparing two Counters
  checks that every key has the same value in both.

Manual single-dict approach (shows the mechanics):
  Increment for each character in s, decrement for each in t.
  If the strings are anagrams, every count ends at zero.

  Process s = "racecar" (increment):
    r → {r:1}
    a → {r:1, a:1}
    c → {r:1, a:1, c:1}
    e → {r:1, a:1, c:1, e:1}
    c → {r:1, a:1, c:2, e:1}
    a → {r:1, a:2, c:2, e:1}
    r → {r:2, a:2, c:2, e:1}

  Process t = "carrace" (decrement):
    c → {r:2, a:2, c:1, e:1}
    a → {r:2, a:1, c:1, e:1}
    r → {r:1, a:1, c:1, e:1}
    r → {r:0, a:1, c:1, e:1}
    a → {r:0, a:0, c:1, e:1}
    c → {r:0, a:0, c:0, e:1}
    e → {r:0, a:0, c:0, e:0}

  All counts are 0 → True (every character in s was "cancelled out" by t)

Non-anagram case: s = "hello", t = "world"
  Counter("hello") = {h:1, e:1, l:2, o:1}
  Counter("world") = {w:1, o:1, r:1, l:1, d:1}
  h:1 vs h:0, l:2 vs l:1 → counts differ → False
```

---

## Approaches

### Approach 1: Sorting

<details>
<summary>📝 Explanation</summary>

If two strings are anagrams, they contain the exact same letters in the exact same quantities - just in different positions. Sorting rearranges the letters into a consistent order, so any two anagrams produce the same sorted string.

"racecar" sorted → "aaccer"
"carrace" sorted → "aaccer"
Same result → anagram.

"hello" sorted → "ehllo"
"world" sorted → "dlorw"
Different result → not an anagram.

The implementation is one line: `return sorted(s) == sorted(t)`.

**Time:** O(n log n) - sorting both strings. The comparison afterwards is O(n).
**Space:** O(n) - `sorted()` creates new lists.

This is the simplest approach and worth stating first in an interview. Then follow up with "but we can do O(n) with frequency counting" to show optimization awareness. A quick early check you can add: if the strings are different lengths, they can't be anagrams. Return `False` immediately in O(1).

</details>

<details>
<summary>💻 Code</summary>

```python
def is_anagram_sort(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)
```

</details>

---

### Approach 2: Frequency Counting (Optimal)

<details>
<summary>💡 Hint</summary>

Two strings are anagrams if and only if they have identical character frequency distributions.

</details>

<details>
<summary>📝 Explanation</summary>

Two strings are anagrams if every character appears the same number of times in both. Instead of sorting (which rearranges the characters), we count how many times each character appears and compare the counts.

Python's `Counter` from the `collections` module does this directly:

```python
return Counter(s) == Counter(t)
```

`Counter("racecar")` returns `{'r': 2, 'a': 2, 'c': 2, 'e': 1}` - a dict mapping each character to its count. Comparing two Counters checks that every key has the same value in both.

The manual version uses a single dict: increment for each character in `s`, decrement for each character in `t`. If the strings are anagrams, every count ends at exactly zero. If any count is non-zero, the characters don't match up.

**Time:** O(n) - one pass through each string. Each dict operation is O(1).
**Space:** O(1) for lowercase English letters (at most 26 keys in the dict) or O(k) where k is the size of the character set. Technically the space is bounded by the alphabet size, not the string length.

The Counter approach is cleaner for production code. The single-dict approach shows you understand the mechanics and is more likely what an interviewer wants to see you implement.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)
```

Manual version (shows the pattern):

```python
def is_anagram_manual(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts: dict[str, int] = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in t:
        counts[char] = counts.get(char, 0) - 1
    return all(v == 0 for v in counts.values())
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Valid anagram | `"anagram", "nagaram"` | `true` | Happy path |
| Not anagram | `"rat", "car"` | `false` | Different characters |
| Empty strings | `"", ""` | `true` | Empty is technically an anagram of empty |
| Different lengths | `"a", "ab"` | `false` | Quick rejection |
| Same chars, different freq | `"aab", "abb"` | `false` | Frequency matters, not just character set |

---

## Common Pitfalls

1. **Forgetting the length check** - Always check lengths first. It's O(1) and eliminates many cases.
2. **Checking character set instead of frequency** - `"aab"` and `"abb"` have the same character set but aren't anagrams.
3. **Not handling unicode** - The `Counter` approach works for any characters. A fixed-size array only works for known alphabets.

---

## Interview Tips

**What to say:**
> "Anagrams have the same character frequencies. I can sort both strings and compare in O(n log n), or count frequencies with a hash map in O(n)."

**Follow-up: "What if the input could contain Unicode characters?"**
→ `Counter` handles this naturally. A fixed-size array (e.g., `[0] * 26`) only works for lowercase English letters.

**Follow-up: "How would you check anagrams across millions of strings?"**
→ This leads to Group Anagrams (LeetCode 49) - compute a canonical key for each string and group by that key.

**What the interviewer evaluates at each stage:** The sorting approach tests basic problem-solving. The frequency counting approach tests whether you recognize that counting is O(n) vs sorting at O(n log n). Follow-up questions about Unicode or large-scale anagram checking test generalization ability. This is a warm-up problem - the interviewer expects a clean solution quickly and will move to harder follow-ups like Group Anagrams.

---

## DE Application

Frequency counting is the foundation of many data engineering patterns:
- Validating that two datasets have the same value distribution after a migration
- Detecting data quality issues (unexpected character frequencies in a column)
- Building histograms for monitoring and profiling

---

## At Scale

Character frequency counting uses O(1) space (26 letters for lowercase English, 128 for ASCII, ~150K for full Unicode). This is one of the rare problems where the hash map doesn't grow with input size. At 1B-character strings, the bottleneck is I/O (reading the string) not memory. The sorted approach creates a copy of each string - for very long strings, that's double the memory. In a distributed setting, frequency counting is embarrassingly parallel: each worker counts locally, then merge the frequency maps (which are tiny).

---

## Related Problems

- [49. Group Anagrams](049_group_anagrams.md) - Groups strings by their anagram key
- [438. Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) - Sliding window + frequency counting
