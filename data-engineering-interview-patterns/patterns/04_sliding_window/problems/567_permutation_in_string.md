# Permutation in String (LeetCode #567)

🔗 [LeetCode 567: Permutation in String](https://leetcode.com/problems/permutation-in-string/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given two strings `s1` and `s2`, return true if `s2` contains a permutation of `s1`. In other words, return true if one of `s1`'s permutations is a substring of `s2`.

**Example:**
```
Input: s1 = "ab", s2 = "eidbaooo"
Output: true ("ba" is a permutation of "ab" and appears in s2)

Input: s1 = "ab", s2 = "eidboaoo"
Output: false
```

**Constraints:**
- 1 <= s1.length, s2.length <= 10^4
- s1 and s2 consist of lowercase English letters

---

## Thought Process

1. **A permutation has the same character frequencies.** So we need to find a window in s2 of size len(s1) that has identical character counts to s1.
2. **Fixed-size window.** The window size is len(s1). Slide it across s2.
3. **Two approaches to checking the match:**
   - **Counter comparison:** Compare Counter objects at each step. O(26) per comparison, O(26n) total.
   - **Match counting:** Track how many distinct characters still need matching. When all are matched, return True. O(1) per step, O(n) total.

---

## Worked Example

Check if any permutation (anagram) of s1 exists as a substring in s2. A permutation has the exact same character counts as the original. So we slide a window of length len(s1) across s2 and check if the character counts in the window match s1's counts.

This combines the fixed-size window (size = len(s1)) with frequency counting from the anagram pattern.

```
Input: s1 = "ab", s2 = "eidcbaooo"

  Target counts: Counter("ab") = {'a':1, 'b':1}
  Window size = 2

  Window "ei": counts={'e':1,'i':1} → doesn't match {'a':1,'b':1}
  Window "id": counts={'i':1,'d':1} → no
  Window "dc": {'d':1,'c':1} → no
  Window "cb": {'c':1,'b':1} → no (has b but not a)
  Window "ba": {'b':1,'a':1} → MATCH. Return True.

  Found at index 4-5. "ba" is a permutation of "ab".

The match check each slide: naive comparison of two Counter dicts is
O(26) for lowercase letters, effectively O(1). With the "match count"
optimization below, it's literally O(1) per slide.
```

---

## Approaches

### Approach 1: Counter Comparison (Simple)

<details>
<summary>📝 Explanation</summary>

Count character frequencies in s1. Slide a fixed-size window (length = len(s1)) across s2. At each position, compare the window's character counts to s1's counts. If they match, return True.

On each slide: add the new character's count, subtract the outgoing character's count, compare the full counter.

**Time:** O(n × 26) where n = len(s2). We slide through s2 (O(n) positions), and each comparison checks up to 26 characters. Since 26 is constant, this simplifies to O(n).
**Space:** O(1) - two counter arrays/dicts, each with at most 26 entries.

Simple and correct. The comparison is technically O(26) per slide, which is fine. The optimization below makes it O(1) per slide.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def check_inclusion_counter(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    target = Counter(s1)
    window = Counter(s2[:len(s1)])
    if window == target:
        return True
    for i in range(len(s1), len(s2)):
        window[s2[i]] += 1
        old = s2[i - len(s1)]
        window[old] -= 1
        if window[old] == 0:
            del window[old]
        if window == target:
            return True
    return False
```

</details>

### Approach 2: Match Counting (Optimal)

<details>
<summary>💡 Hint</summary>

Instead of comparing entire Counters, track how many characters have reached their target count. When all characters match, you have a permutation.

</details>

<details>
<summary>📝 Explanation</summary>

Instead of comparing the full counters every slide, track how many of the 26 possible characters currently have matching counts. Increment/decrement this "matches" counter as the window slides. When matches == 26, all character counts are equal and we've found a permutation.

Setup:
1. Build frequency arrays for s1 and the initial window (first len(s1) characters of s2).
2. Count initial matches: for each of the 26 letters, if s1_count[c] == window_count[c], increment matches.

On each slide:
- Add the new character: increment window_count. If window_count now equals s1_count for that character, increment matches. If it was equal before the increment (and now isn't), decrement matches.
- Remove the outgoing character: same logic in reverse.
- If matches == 26: return True.

**Time:** O(n) with O(1) per slide (constant-time update to matches, no full comparison needed).
**Space:** O(1) - two arrays of size 26.

The match counting optimization is useful to know but not always expected in interviews. Mention it as a follow-up if the interviewer asks about optimization.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def check_inclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window_size = len(s1)
    matches_needed = len(need)
    for i in range(len(s2)):
        char_in = s2[i]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                matches_needed -= 1
        if i >= window_size:
            char_out = s2[i - window_size]
            if char_out in need:
                if need[char_out] == 0:
                    matches_needed += 1
                need[char_out] += 1
        if matches_needed == 0:
            return True
    return False
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Match in middle | `"ab", "eidbaooo"` | `True` | Standard case |
| No match | `"ab", "eidboaoo"` | `False` | Characters present but not adjacent |
| Exact match | `"abc", "abc"` | `True` | Window = entire string |
| Reversed | `"abc", "cba"` | `True` | Permutation, not exact match |
| s1 longer | `"abcdef", "abc"` | `False` | Can't fit |
| Repeated chars | `"aab", "cbdaaboa"` | `True` | Frequency matters, not just presence |
| All same | `"aaa", "aaaa"` | `True` | Any window of 3 matches |

---

## Common Pitfalls

1. **Checking presence instead of frequency** - "ab" in a string containing 'a' and 'b' isn't enough. They need to be adjacent and in the right counts.
2. **Forgetting to clean up zero counts** - In the Counter approach, delete keys with count 0 so equality comparison works correctly.
3. **Off-by-one on window boundary** - The character leaving the window is at index `i - len(s1)`, not `i - len(s1) + 1`.

---

## Interview Tips

**What to say:**
> "A permutation has the same character frequencies. So I need a fixed window of size len(s1) and I'll check if the character counts match at each position."

**Counter vs match counting:**
> "Comparing Counters at each step is O(26) per step. I can optimize to O(1) per step by tracking how many characters still need matching. But for an interview, the Counter approach is cleaner and the constant factor doesn't matter."

In practice, use whichever you can implement quickly and correctly. The Counter approach has fewer places to make mistakes.

**What the interviewer evaluates:** The "matches" counter optimization (comparing one character at a time instead of full arrays) tests whether you think about unnecessary work. A candidate who compares 26-element arrays every step gets O(26n) = O(n), but the constant factor matters for very large inputs. The optimization to O(1) per step shows attention to practical performance.

---

## DE Application

Fixed-window frequency matching appears when:
- Detecting specific event patterns in logs (e.g., "these 5 event types all occurred within a 10-second window")
- Sequence matching in data pipelines: "does this batch contain the expected mix of record types?"
- Data validation: checking that each micro-batch has the expected distribution of categories

## At Scale

Fixed window of size len(s1) with a character frequency comparison. Memory is O(26) = O(1). The "matches" counter avoids comparing full frequency arrays each step, making each window slide O(1). At 1B characters in s2, this takes ~10 seconds with constant memory. The pattern generalizes to "does any window of size k contain the exact same distribution as a reference?" In data pipelines, this appears as pattern matching in event streams: "did these 5 specific event types all occur within any 10-minute window?"

---

## Related Problems

- [438. Find All Anagrams](438_find_all_anagrams.md) - Same mechanism, but return all positions instead of boolean
- [76. Minimum Window Substring](076_min_window_substring.md) - Variable window version (window can be larger than pattern)
- [242. Valid Anagram](../../01_hash_map/problems/242_valid_anagram.md) - Same frequency comparison without the sliding
