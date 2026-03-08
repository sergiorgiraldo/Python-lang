# Longest Repeating Character Replacement (LeetCode #424)

🔗 [LeetCode 424: Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a string `s` of uppercase English letters and an integer `k`, you can choose any character and change it to any other uppercase character at most `k` times. Find the length of the longest substring containing all the same character after performing at most `k` operations.

**Example:**
```
Input: s = "AABABBA", k = 1
Output: 4 ("AABA" → replace B → "AAAA")

Input: s = "ABAB", k = 2
Output: 4 (replace both Bs → "AAAA")
```

**Constraints:**
- 1 <= s.length <= 10^5
- s consists of uppercase English letters
- 0 <= k <= s.length

---

## Thought Process

1. **What defines a valid window?** A substring of length L is valid if we can make all characters the same with at most k replacements. That means: `L - count_of_most_frequent_char <= k`.
2. **Variable window:** Expand right. If the window becomes invalid, shrink from the left.
3. **Tracking max frequency:** Keep a frequency map of characters in the window. The most frequent character stays, everything else gets "replaced."
4. **Subtle optimization:** `max_freq` doesn't need to decrease when we shrink. The window only grows when we find a new `max_freq`. This means `max_freq` is a historical maximum, not the current maximum - but that's fine because we're looking for the longest window, and a shorter window with a lower max_freq can't beat our current best.

---

## Worked Example

Find the longest substring where you can replace at most k characters to make all characters the same. The variable-size window expands right. The key insight: a window is valid if `window_length - count_of_most_frequent_char <= k`. The difference is how many characters need to be replaced to make the entire window the same character.

We don't need to track which specific character is most frequent at all times. We just track `max_freq` (the highest frequency of any single character seen in any window). Even if max_freq becomes "stale" (referring to a character that's no longer the most frequent in the current window), it doesn't matter because we only care about expanding the window - a stale max_freq just means we contract less aggressively than strictly necessary, which doesn't affect correctness.

```
Input: s = "AABCABBB", k = 2

  left=0, max_freq=0

  right=0: char='A', counts={'A':1}, max_freq=1
    Window "A", length 1. Replacements needed: 1-1=0 <= 2. Valid. max_len=1.

  right=1: 'A', counts={'A':2}, max_freq=2
    "AA", length 2. Replacements: 2-2=0. Valid. max_len=2.

  right=2: 'B', counts={'A':2,'B':1}, max_freq=2
    "AAB", length 3. Replacements: 3-2=1 <= 2. Valid. max_len=3.

  right=3: 'C', counts={'A':2,'B':1,'C':1}, max_freq=2
    "AABC", length 4. Replacements: 4-2=2 <= 2. Valid. max_len=4.

  right=4: 'A', counts={'A':3,'B':1,'C':1}, max_freq=3
    "AABCA", length 5. Replacements: 5-3=2 <= 2. Valid. max_len=5.

  right=5: 'B', counts={'A':3,'B':2,'C':1}, max_freq=3
    "AABCAB", length 6. Replacements: 6-3=3 > 2. Invalid. Contract:
    Remove s[0]='A'. counts={'A':2,'B':2,'C':1}. left=1.
    Length 5. Replacements: 5-2=3 > 2. Still invalid. Contract:
    Remove s[1]='A'. counts={'A':1,'B':2,'C':1}. left=2.
    Length 4. Replacements: 4-2=2 <= 2. Valid. max_len still 5.

  right=6: 'B', counts={'A':1,'B':3,'C':1}, max_freq=3
    "BCABB", length 5. Replacements: 5-3=2. Valid. max_len=5.

  right=7: 'B', counts={'A':1,'B':4,'C':1}, max_freq=4
    "BCABBB", length 6. Replacements: 6-4=2. Valid. max_len=6.

  Answer: 6 (substring "BCABBB" → replace B,C with B to get "BBBBBB").
```

---

## Approaches

### Approach: Variable Window with Frequency Tracking

<details>
<summary>💡 Hint 1</summary>

For any substring, the minimum replacements needed = length - count of the most frequent character.

</details>

<details>
<summary>💡 Hint 2</summary>

You don't need to track which character is most frequent. You just need the count. And that count only needs to be accurate when it increases.

</details>

<details>
<summary>📝 Explanation</summary>

Maintain a window [left, right] and a frequency count of characters in the window. The window is valid when `window_length - max_frequency <= k` (the number of characters that differ from the most frequent one is at most k, meaning we can replace them all).

1. Expand right, incrementing the count for the new character.
2. Update `max_freq` if the new character's count exceeds it.
3. If `(right - left + 1) - max_freq > k`: the window is too big. Contract from the left (decrement the count for the removed character, increment left).
4. Update the maximum valid window length.

A subtle optimization: we never decrease `max_freq` when contracting. Why? We're looking for the *longest* valid window. A window can only beat our current best if it has a higher max_freq or the same max_freq with a wider window. Decreasing max_freq would only make the valid window condition easier to satisfy, but we've already found a window of the current best length, so we don't need to find smaller ones.

**Time:** O(n) - both pointers traverse the string once.
**Space:** O(1) - at most 26 entries in the frequency map (for uppercase English letters).

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def character_replacement(s: str, k: int) -> int:
    counts = defaultdict(int)
    left = 0
    max_freq = 0
    max_len = 0
    for right in range(len(s)):
        counts[s[right]] += 1
        max_freq = max(max_freq, counts[s[right]])
        window_size = right - left + 1
        if window_size - max_freq > k:
            counts[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `"AABABBA", 1` | `4` | Basic case |
| Full replacement | `"ABAB", 2` | `4` | Entire string becomes valid |
| No replacements | `"ABCDE", 0` | `1` | Each char is its own window |
| All same | `"AAAA", 2` | `4` | Already valid, k is unused |
| Empty string | `"", 1` | `0` | Boundary |
| Interrupted run | `"AAABAAAA", 1` | `8` | Fix one char, whole string is valid |

---

## Common Pitfalls

1. **Trying to decrease max_freq** - It's tempting to recompute max_freq when shrinking. Don't. The stale value is correct for finding the longest window.
2. **Using `while` instead of `if`** - Since max_freq doesn't decrease, the window only shrinks by one at a time. Use `if`, not `while`. This is different from most variable window problems.
3. **Forgetting the `defaultdict`** - A regular dict needs `.get(char, 0)` for characters not yet seen.

---

## Interview Tips

**What to say:**
> "The number of replacements for a window is its size minus the count of the most frequent character. I'll track that frequency and shrink the window when replacements exceed k."

**The max_freq question will come up.** Interviewers often ask "doesn't max_freq become wrong when you shrink?" Be ready:
> "max_freq is a historical maximum. It only matters when it increases because that's what enables a longer window. A stale value means the window stays the same size rather than growing - it never produces a wrong answer."

**What the interviewer evaluates:** The "replacements budget" concept makes the window condition non-trivial. You need to realize that the window is valid when (window size - max frequency) <= k. The insight that max_freq doesn't need to decrease when the window shrinks is the optimization that impresses.

---

## DE Application

The "budget for deviations" concept shows up when:
- Data quality checks: "allow at most k NULL values in a rolling window of N records"
- Stream processing: "alert if more than k errors occur in any 5-minute window"
- ETL validation: "flag batches where more than k records fail schema validation"

The constraint `window_size - max_freq <= k` generalizes to any scenario where you have a tolerance budget within a window.

## At Scale

The character frequency array uses O(26) = O(1) space. The sliding window makes a single pass through the string. At 1B characters, this takes ~10 seconds and uses essentially zero extra memory. The "maximum frequency in the window" optimization avoids recalculating the mode each step. In data quality contexts, this pattern answers "what's the longest run of near-consistent values?" For sensor data or time series, finding the longest period where a metric stays within tolerance (allowing k exceptions) is the same structure. The window grows while the "error budget" (replacements allowed) isn't exhausted.

---

## Related Problems

- [3. Longest Substring Without Repeating](003_longest_substring.md) - Variable window (k=0 for uniqueness)
- [567. Permutation in String](567_permutation_in_string.md) - Fixed window with frequency matching
- [76. Minimum Window Substring](076_min_window_substring.md) - Variable window finding shortest, not longest
