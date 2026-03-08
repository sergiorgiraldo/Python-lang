# Minimum Window Substring (LeetCode #76)

🔗 [LeetCode 76: Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string.

**Example:**
```
Input: s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
Explanation: "BANC" is the shortest substring containing A, B, and C.
```

**Constraints:**
- 1 <= s.length, t.length <= 10^5
- s and t consist of uppercase and lowercase English letters

---

## Thought Process

1. **This is a variable-size window** but we're finding the shortest valid window, not the longest. That flips the expand/contract logic.
2. **Expand until valid:** Move right until the window contains all characters of t.
3. **Contract to minimize:** Once valid, shrink from the left as far as possible while staying valid. Record the shortest valid window found.
4. **Frequency tracking:** Same mechanism as 567/438 - track how many characters still need matching. But here the window size varies.

The key difference from "longest" problems: in longest-window problems, you contract when the window is invalid. Here, you contract when the window is valid (to find the minimum).

---

## Approaches

### Approach: Variable Window with Frequency Matching

<details>
<summary>💡 Hint 1</summary>

Expand right until you have all characters of t. Then shrink left to find the minimum window. Track the shortest window you've found across all shrink phases.

</details>

<details>
<summary>💡 Hint 2</summary>

Use a `chars_needed` counter that tracks how many distinct characters still need to reach their target count. When it hits 0, the window is valid.

</details>

<details>
<summary>📝 Explanation</summary>

Initialize a frequency map `need` from t. Track `chars_needed` (distinct characters not yet fully matched).

For each right pointer:
1. **Expand:** If `s[right]` is in `need`, decrement its count. If count hits 0, decrement `chars_needed`.
2. **Contract:** While `chars_needed == 0` (window is valid):
   - Record this window if it's the shortest so far.
   - Remove `s[left]` from the window. If it was fully matched (count was 0), increment `chars_needed` (no longer fully matched).
   - Move left forward.

The contract loop runs inside the expand loop, but `left` only moves forward. Total movement of both pointers: O(n).

**Time:** O(n + m) where n = len(s) and m = len(t)
**Space:** O(m) for the frequency map

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    chars_needed = len(need)
    left = 0
    min_start = 0
    min_len = float("inf")
    for right in range(len(s)):
        char_in = s[right]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                chars_needed -= 1
        while chars_needed == 0:
            window_size = right - left + 1
            if window_size < min_len:
                min_len = window_size
                min_start = left
            char_out = s[left]
            if char_out in need:
                if need[char_out] == 0:
                    chars_needed += 1
                need[char_out] += 1
            left += 1
    if min_len == float("inf"):
        return ""
    return s[min_start:min_start + min_len]
```

</details>

---

## Worked Example

Variable-size window with frequency matching. Expand the right side until all characters of t are covered. Then shrink from the left to find the shortest valid window. A frequency map tracks how many more of each character we need. A `chars_needed` counter tracks how many distinct characters are still unsatisfied, so we don't have to scan the whole map each step.

```
s = "ADOBECODEBANC", t = "ABC"
need: {A:1, B:1, C:1}, chars_needed = 3, best = ""

Expand right until valid:
  i=0  'A': need[A]=1→0. Satisfied. chars_needed=2.  Window: [A]DOBECODEBANC
  i=1  'D': not in t. Skip.                           Window: [AD]OBECODEBANC
  i=2  'O': not in t.                                 Window: [ADO]BECODEBANC
  i=3  'B': need[B]=1→0. Satisfied. chars_needed=1.   Window: [ADOB]ECODEBANC
  i=4  'E': not in t.                                 Window: [ADOBE]CODEBANC
  i=5  'C': need[C]=1→0. Satisfied. chars_needed=0.   Window: [ADOBEC]ODEBANC
  VALID. Length=6. best="ADOBEC".

Shrink from left:
  left=0 'A': need[A]=0→1. Unsatisfied. chars_needed=1. Invalid. Stop shrinking.

Expand right again:
  i=6  'O': not in t.
  i=7  'D': not in t.
  i=8  'E': not in t.
  i=9  'B': need[B]=0→-1. Already satisfied (negative = surplus). chars_needed still 1.
  i=10 'A': need[A]=1→0. Satisfied. chars_needed=0. Window: s[1..10]="DOBECODEBANC"
  VALID. Length=10. Worse than best. Don't update.

Shrink from left:
  left=1 'D': not in t. Still valid. Length=9.
  left=2 'O': not in t. Still valid. Length=8.
  left=3 'B': need[B]=-1→0. Still satisfied (0 means exact). chars_needed still 0.
            Window: s[4..10]="ECODEBANC". Length=7.
  left=4 'E': not in t. Length=6. Tied with best.
  left=5 'C': need[C]=0→1. Unsatisfied. chars_needed=1. Invalid. Stop.

Expand right:
  i=11 'N': not in t.
  i=12 'C': need[C]=1→0. chars_needed=0. Window: s[6..12]="ODEBANC".
  VALID. Length=7. Worse than best.

Shrink from left:
  left=6  'O': not in t. Length=6.
  left=7  'D': not in t. Length=5. NEW BEST. best="EBANC".
  left=8  'E': not in t. Length=4. NEW BEST. best="BANC".
  left=9  'B': need[B]=0→1. Unsatisfied. chars_needed=1. Invalid. Stop.

Right exhausted. Answer: "BANC" (length 4).

Each character entered the window once (right pointer) and left once
(left pointer). O(n + m) total where n=len(s), m=len(t).
```

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `"ADOBECODEBANC", "ABC"` | `"BANC"` | Basic case |
| Single char | `"a", "a"` | `"a"` | Exact match |
| Insufficient | `"a", "aa"` | `""` | Not enough characters |
| Exact match | `"aa", "aa"` | `"aa"` | Window = entire string |
| t longer | `"a", "abc"` | `""` | Can't contain all chars |
| Repeated in t | `"adobecodebanc", "aab"` | varies | Must have 2 a's |
| Window at start | `"abcdef", "abc"` | `"abc"` | Minimum at beginning |
| Window at end | `"defabc", "abc"` | `"abc"` | Minimum at end |

---

## Common Pitfalls

1. **Contract logic direction** - In "longest" problems you contract when invalid. Here you contract when *valid*. Getting this backward gives wrong results.
2. **Need count going negative** - `need[char]` can go below 0 (more of that character in the window than needed). This is fine and handled correctly. `chars_needed` only changes when `need[char]` crosses 0.
3. **Tracking the result** - Store `min_start` and `min_len` instead of slicing the string at each step. Slicing is O(k) and would add up.
4. **Case sensitivity** - The problem says s and t can contain both uppercase and lowercase. Counter handles this correctly since 'a' != 'A'.

---

## Interview Tips

**What to say:**
> "This is a variable window where I'm looking for the shortest valid window instead of the longest. I'll expand right until I have all characters of t, then shrink from the left to minimize. I'll track the frequency of needed characters and a counter for how many are fully matched."

**If stuck on the contract direction:**
> "In 'longest' problems, I shrink when invalid. Here I want the shortest valid window, so I shrink while the window IS valid, recording each valid window I find."

**This is often the hardest sliding window problem in interview sets.** If you can implement this correctly, you've demonstrated mastery of the pattern. The key is keeping track of `chars_needed` cleanly.

**What the interviewer evaluates:** This is a hard problem combining variable windows with character frequency tracking. The "have" counter optimization (tracking how many unique characters are satisfied) avoids O(26) comparisons per step. This tests both pattern knowledge and implementation precision. At principal level, discussing the streaming application and comparing to SQL approaches shows breadth.

---

## DE Application

Finding the minimum window that covers required elements appears when:
- **Log analysis** - "Find the shortest time span that contains all error types we're investigating"
- **Event correlation** - "What's the shortest period containing events from all systems involved in the incident?"
- **Coverage analysis** - "Find the minimum number of consecutive batches that together cover all customer segments"
- **Data completeness** - "What's the smallest partition range that contains at least one record of every category?"

The variable window with frequency matching is also the basis for "covering" queries in stream processing.

## At Scale

The hash map tracking character frequencies uses O(|t|) space where t is the target string. For typical inputs, this is tiny. The string s is processed in a single pass: O(n) time. At 1B characters in s, this takes ~10 seconds. The variable-size window pattern (expand right to satisfy, shrink left to minimize) is the most complex sliding window variant. In production, this answers questions like "what's the shortest time period containing all required event types?" In SQL, this requires a self-join or correlated subquery approach that's much less efficient than the algorithmic solution. For real-time monitoring ("alert when all critical events have occurred within a short window"), the streaming implementation maintains the character/event frequency map as state.

---

## Related Problems

- [567. Permutation in String](567_permutation_in_string.md) - Fixed window version (exact size match)
- [438. Find All Anagrams](438_find_all_anagrams.md) - Fixed window, find all positions
- [3. Longest Substring Without Repeating](003_longest_substring.md) - Variable window finding longest (opposite direction)
- [424. Longest Repeating Character Replacement](424_longest_repeating_char.md) - Variable window with constraint
