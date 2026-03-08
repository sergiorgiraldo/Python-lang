# Find All Anagrams in a String (LeetCode #438)

🔗 [LeetCode 438: Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given two strings `s` and `p`, return the start indices of `p`'s anagrams in `s`. An anagram is a rearrangement using all characters exactly once.

**Example:**
```
Input: s = "cbaebabacd", p = "abc"
Output: [0, 6]
Explanation: "cba" (index 0) and "bac" (index 6) are anagrams of "abc"
```

**Constraints:**
- 1 <= s.length, p.length <= 3 * 10^4
- s and p consist of lowercase English letters

---

## Thought Process

This is [567. Permutation in String](567_permutation_in_string.md) with one change: instead of returning True when the first match is found, collect all matching positions.

The mechanism is identical. If you can solve 567, you can solve this.

---

## Worked Example

This is the same pattern as Permutation in String (567), but instead of returning True/False, return all starting indices where an anagram of p appears in s. Slide a window of length len(p) across s and collect all positions where character counts match.

```
Input: s = "cbaebabacd", p = "abc"

  Target counts: Counter("abc") = {'a':1, 'b':1, 'c':1}
  Window size = 3

  i=0: window "cba" → counts={'c':1,'b':1,'a':1} → MATCH. Record index 0.
  i=1: window "bae" → add 'e', remove 'c': {'b':1,'a':1,'e':1} → no match.
  i=2: window "aeb" → add 'b', remove 'b': {'a':1,'e':1,'b':1} → no.
       Wait: add s[4]='b', remove s[1]='b'. Hmm, let me redo this.

  Let me track more carefully:
  Initial window s[0..2] = "cba": {c:1, b:1, a:1} → matches {a:1, b:1, c:1}. Result: [0]

  Slide to s[1..3] = "bae": remove s[0]='c', add s[3]='e'.
    {b:1, a:1, e:1} → no match.

  Slide to s[2..4] = "aeb": remove s[1]='b', add s[4]='b'.
    {a:1, e:1, b:1} → no match (has 'e' instead of 'c').

  Slide to s[3..5] = "eba": remove s[2]='a', add s[5]='a'.
    {e:1, b:1, a:1} → no (still has 'e').

  Slide to s[4..6] = "bab": remove s[3]='e', add s[6]='a'.
    {b:2, a:1} → no (b count too high).

  Slide to s[5..7] = "aba": remove s[4]='b', add s[7]='c'.
    {a:2, c:1} → no (a count too high, missing b).

  Slide to s[6..8] = "bac": remove s[5]='a', add s[8]='c'.
    Let me re-read: s = "cbaebabacd"
    s[6]='b', s[7]='a', s[8]='c'. Window "bac": {b:1, a:1, c:1} → MATCH. Record index 6.

  Slide to s[7..9] = "acd": remove 'b', add 'd'. {a:1, c:1, d:1} → no.

  Result: [0, 6]
```

---

## Approaches

### Approach 1: Counter Comparison (Simple)

<details>
<summary>📝 Explanation</summary>

Same as Permutation in String but collect all matching indices instead of returning at the first match.

Slide a window of size len(p) across s. At each position, compare window counts to p counts. If they match, append the starting index to the result list.

**Time:** O(n × 26) ≈ O(n) where n = len(s).
**Space:** O(1) for the counters (26 entries each), O(m) for the result list where m is the number of anagram occurrences.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def find_anagrams_counter(s: str, p: str) -> list[int]:
    if len(p) > len(s):
        return []
    target = Counter(p)
    window = Counter(s[:len(p)])
    result = []
    if window == target:
        result.append(0)
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        old = s[i - len(p)]
        window[old] -= 1
        if window[old] == 0:
            del window[old]
        if window == target:
            result.append(i - len(p) + 1)
    return result
```

</details>

### Approach 2: Match Counting (Optimal)

<details>
<summary>📝 Explanation</summary>

Same match-counting optimization as problem 567. Track how many of the 26 characters have matching counts. When matches == 26, record the current starting index.

The only difference from 567: instead of returning True at the first match, continue sliding and collect all positions where matches == 26.

**Time:** O(n) with O(1) per slide.
**Space:** O(1) for tracking + O(m) for results.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def find_anagrams(s: str, p: str) -> list[int]:
    if len(p) > len(s):
        return []
    need = Counter(p)
    window_size = len(p)
    matches_needed = len(need)
    result = []
    for i in range(len(s)):
        char_in = s[i]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                matches_needed -= 1
        if i >= window_size:
            char_out = s[i - window_size]
            if char_out in need:
                if need[char_out] == 0:
                    matches_needed += 1
                need[char_out] += 1
        if matches_needed == 0:
            result.append(i - window_size + 1)
    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Multiple matches | `"cbaebabacd", "abc"` | `[0, 6]` | Standard case |
| Overlapping | `"abab", "ab"` | `[0, 1, 2]` | Consecutive anagrams overlap |
| Pattern longer | `"a", "ab"` | `[]` | Can't fit |
| No match | `"xyz", "abc"` | `[]` | Different characters |
| Single char | `"aaaa", "a"` | `[0,1,2,3]` | Every position matches |
| All same chars | `"aaa", "aa"` | `[0, 1]` | Repeating pattern |

---

## Common Pitfalls

Same as [567](567_permutation_in_string.md). The additional pitfall specific to this problem:

1. **Forgetting overlapping matches** - Anagrams can overlap. `"abab"` with pattern `"ab"` has matches at 0, 1 and 2. The sliding window handles this naturally since it moves one character at a time.

---

## Interview Tips

**If you've already solved 567:**
> "This is the same mechanism as Permutation in String. The only difference is I collect all start indices instead of returning after the first match."

**If this comes up first:** Solve it fully, then mention "I could modify this to return a boolean for checking if any permutation exists."

Recognizing that 567 and 438 share the same mechanism demonstrates pattern recognition, which is exactly what interviewers want to see.

**What the interviewer evaluates:** Nearly identical to 567. If asked both in sequence, the interviewer tests whether you can adapt your solution (return list instead of boolean) without starting over. Reusing your sliding window template with a minor output change is the right move.

---

## DE Application

Finding all positions of a pattern (not just the first) is useful when:
- Scanning logs for all occurrences of a specific error signature
- Finding all time windows where a metric pattern appeared
- Identifying recurring event sequences in clickstream data
- Any scenario where "find the first" isn't enough and you need "find every"

## At Scale

Same as Permutation in String (567) but returns all matching positions instead of a boolean. Memory and time complexity are identical: O(1) space, O(n) time. At scale, the concern is output size: if matches are frequent, the result list grows. For 1B characters with matches every 100 positions, that's 10M matches (~80MB of indices). Streaming this as an iterator (yield positions as found) avoids materializing the full result. In SQL, this type of pattern matching uses window functions: `COUNT(*) OVER (ROWS BETWEEN k PRECEDING AND CURRENT ROW)` with a HAVING-like filter.

---

## Related Problems

- [567. Permutation in String](567_permutation_in_string.md) - Same mechanism, boolean return
- [76. Minimum Window Substring](076_min_window_substring.md) - Variable window version (doesn't need exact size match)
- [3. Longest Substring Without Repeating](003_longest_substring.md) - Variable window (different constraint)
