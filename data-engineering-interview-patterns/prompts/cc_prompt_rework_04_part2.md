# CC Prompt: Full Rework - Pattern 04 Sliding Window (Part 2 of 2)

## What This Prompt Does

Continues from Part 1. Rewrites `## Worked Example` and `📝 Explanation` blocks for problems 4-6, plus all 4 DE scenario worked examples.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

Same as Part 1. Only `.md` files. REPLACE specified sections only. NO Oxford commas, NO em dashes, NO exclamation points.

---

## Problem 4: 424_longest_repeating_char.md

**Worked Example:**

```markdown
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
```

**Approach: Variable Window with Frequency Tracking - replace explanation:**

```
Maintain a window [left, right] and a frequency count of characters in the window. The window is valid when `window_length - max_frequency <= k` (the number of characters that differ from the most frequent one is at most k, meaning we can replace them all).

1. Expand right, incrementing the count for the new character.
2. Update `max_freq` if the new character's count exceeds it.
3. If `(right - left + 1) - max_freq > k`: the window is too big. Contract from the left (decrement the count for the removed character, increment left).
4. Update the maximum valid window length.

A subtle optimization: we never decrease `max_freq` when contracting. Why? We're looking for the *longest* valid window. A window can only beat our current best if it has a higher max_freq or the same max_freq with a wider window. Decreasing max_freq would only make the valid window condition easier to satisfy, but we've already found a window of the current best length, so we don't need to find smaller ones.

**Time:** O(n) - both pointers traverse the string once.
**Space:** O(1) - at most 26 entries in the frequency map (for uppercase English letters).
```

---

## Problem 5: 567_permutation_in_string.md

**Worked Example:**

```markdown
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
```

**Approach 1: Counter Comparison - replace explanation:**

```
Count character frequencies in s1. Slide a fixed-size window (length = len(s1)) across s2. At each position, compare the window's character counts to s1's counts. If they match, return True.

On each slide: add the new character's count, subtract the outgoing character's count, compare the full counter.

**Time:** O(n × 26) where n = len(s2). We slide through s2 (O(n) positions), and each comparison checks up to 26 characters. Since 26 is constant, this simplifies to O(n).
**Space:** O(1) - two counter arrays/dicts, each with at most 26 entries.

Simple and correct. The comparison is technically O(26) per slide, which is fine. The optimization below makes it O(1) per slide.
```

**Approach 2: Match Counting - replace explanation:**

```
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
```

---

## Problem 6: 438_find_all_anagrams.md

**Worked Example:**

```markdown
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

  Slide to s[6..8] = "bac": remove s[5]='a', add s[8]='d'. Wait, s[8]='c'.
    Let me re-read: s = "cbaebabacd"
    s[6]='b', s[7]='a', s[8]='c'. Window "bac": {b:1, a:1, c:1} → MATCH. Record index 6.

  Slide to s[7..9] = "acd": remove 'b', add 'd'. {a:1, c:1, d:1} → no.

  Result: [0, 6]
```
```

**Approach 1: Counter Comparison - replace explanation:**

```
Same as Permutation in String but collect all matching indices instead of returning at the first match.

Slide a window of size len(p) across s. At each position, compare window counts to p counts. If they match, append the starting index to the result list.

**Time:** O(n × 26) ≈ O(n) where n = len(s).
**Space:** O(1) for the counters (26 entries each), O(m) for the result list where m is the number of anagram occurrences.
```

**Approach 2: Match Counting - replace explanation:**

```
Same match-counting optimization as problem 567. Track how many of the 26 characters have matching counts. When matches == 26, record the current starting index.

The only difference from 567: instead of returning True at the first match, continue sliding and collect all positions where matches == 26.

**Time:** O(n) with O(1) per slide.
**Space:** O(1) for tracking + O(m) for results.
```

---

## DE Scenario Worked Examples

### de_scenarios/moving_averages.md

```markdown
## Worked Example

Moving averages smooth noisy data by averaging the last k observations. This is the fixed-size sliding window applied to time-series monitoring. Instead of re-summing k values at each step, the window adds the new value and subtracts the one that fell off.

```
Metric: API response times (ms), arriving every second:
  [120, 85, 340, 95, 210, 150, 88, 445, 110, 75]

Moving average with window k=4:

  Window [120, 85, 340, 95]:   sum=640,  avg=160.0 ms
  Window [85, 340, 95, 210]:   sum=730,  avg=182.5 ms  (added 210, removed 120)
  Window [340, 95, 210, 150]:  sum=795,  avg=198.75 ms
  Window [95, 210, 150, 88]:   sum=543,  avg=135.75 ms
  Window [210, 150, 88, 445]:  sum=893,  avg=223.25 ms ← spike
  Window [150, 88, 445, 110]:  sum=793,  avg=198.25 ms
  Window [88, 445, 110, 75]:   sum=718,  avg=179.5 ms

The raw data has a spike at 445ms. The moving average shows it as a
gradual rise and fall (223 → 198 → 179) rather than a sharp spike,
which is better for alerting (fewer false positives).

SQL equivalent:
  AVG(response_ms) OVER (ORDER BY ts ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
```
```

### de_scenarios/sessionization.md

```markdown
## Worked Example

Sessionization groups events into sessions based on inactivity gaps. If two consecutive events are more than `gap` minutes apart, they belong to different sessions. This is a variable-size window where the window "breaks" when the gap condition is violated.

```
User click events (sorted by timestamp):
  [10:01, 10:03, 10:07, 10:08, 10:45, 10:47, 10:48, 11:30]

Session gap threshold: 15 minutes

  Event 10:01 → start session 1. Window: [10:01]
  Event 10:03 → gap = 2 min < 15 → same session. Window: [10:01, 10:03]
  Event 10:07 → gap = 4 min → same session. Window grows.
  Event 10:08 → gap = 1 min → same session. Window: [10:01..10:08]

  Event 10:45 → gap = 37 min > 15 → NEW SESSION.
    Close session 1: [10:01, 10:03, 10:07, 10:08] (4 events, 7 min duration)
    Start session 2: [10:45]

  Event 10:47 → gap = 2 min → same session.
  Event 10:48 → gap = 1 min → same session. Window: [10:45..10:48]

  Event 11:30 → gap = 42 min > 15 → NEW SESSION.
    Close session 2: [10:45, 10:47, 10:48] (3 events, 3 min duration)
    Start session 3: [11:30] (1 event)

Result: 3 sessions. Single pass through the sorted events, O(n) time.
This is how Google Analytics and most clickstream tools define sessions.
```
```

### de_scenarios/anomaly_detection.md

```markdown
## Worked Example

Detect values that deviate significantly from a sliding window of recent observations. The window maintains a running sum and count (or mean and standard deviation) and flags values that fall outside a threshold.

```
Server CPU usage (%), sampled every minute:
  [45, 48, 42, 50, 47, 44, 93, 46, 43, 88, 91, 47]

Window size k=5, alert threshold: value > window_mean + 2 × window_std

  Window [45, 48, 42, 50, 47]: mean=46.4, std=2.87
    New value: 44. 44 <= 46.4 + 5.74 = 52.14. Normal.

  Window [48, 42, 50, 47, 44]: mean=46.2, std=2.93
    New value: 93. 93 > 46.2 + 5.86 = 52.06. ANOMALY.

  Window [42, 50, 47, 44, 93]: mean=55.2, std=19.0
    New value: 46. Normal (93 inflated the window stats).

  Window [50, 47, 44, 93, 46]: mean=56.0, std=18.5
    New value: 43. Normal.

  Window [47, 44, 93, 46, 43]: mean=54.6, std=18.9
    New value: 88. 88 > 54.6 + 37.8 = 92.4. Normal (barely).

  Window [44, 93, 46, 43, 88]: mean=62.8, std=22.1
    New value: 91. 91 > 62.8 + 44.2 = 107.0. Normal.

The anomaly detector caught the 93 spike but not the later 88 and 91
because the window had already shifted to include the earlier spike,
raising the baseline. This is a known limitation of simple moving-window
approaches - they adapt to sustained anomalies.
```
```

### de_scenarios/rate_limiting.md

```markdown
## Worked Example

Rate limiting counts events within a sliding time window and rejects new events if the count exceeds a threshold. This is a variable-size window where the "validity" condition is the count staying under the limit.

```
API requests from user_42 (timestamps in seconds):
  [1.0, 1.2, 1.5, 2.0, 2.3, 2.5, 2.8, 3.1, 3.2, 3.5]

Rate limit: max 5 requests per 2-second window

  Request at 1.0: window [1.0]. Count=1 <= 5. ALLOW.
  Request at 1.2: window [1.0, 1.2]. Count=2. ALLOW.
  Request at 1.5: window [1.0, 1.2, 1.5]. Count=3. ALLOW.
  Request at 2.0: window [1.0, 1.2, 1.5, 2.0]. Count=4. ALLOW.
  Request at 2.3: window [1.0, 1.2, 1.5, 2.0, 2.3]. Count=5. ALLOW.

  Request at 2.5: window would be [1.0, 1.2, 1.5, 2.0, 2.3, 2.5].
    But 1.0 is outside the 2-second window (2.5 - 1.0 = 1.5... wait, that's within 2 sec).
    All 6 in window. Count=6 > 5. REJECT.

  Actually: 2-second window ending at 2.5 = [0.5, 2.5].
    All requests from 1.0 to 2.5 are within this range. Count=6 > 5. REJECT.

  Request at 2.8: window [0.8, 2.8].
    Requests in range: [1.0, 1.2, 1.5, 2.0, 2.3, 2.5, 2.8]. Count=7 > 5. REJECT.

  Request at 3.1: window [1.1, 3.1].
    Requests in range: [1.2, 1.5, 2.0, 2.3, 2.5, 2.8, 3.1].
    1.0 is now outside (1.0 < 1.1). Count=7. Still > 5. REJECT.

  Request at 3.2: window [1.2, 3.2].
    Count = 8 (1.2 through 3.2). REJECT.

  Request at 3.5: window [1.5, 3.5].
    Requests: [1.5, 2.0, 2.3, 2.5, 2.8, 3.1, 3.2, 3.5]. Count=8. REJECT.

The burst starting at 2.5 triggered the rate limiter. Earlier requests
gradually age out of the window, allowing new requests eventually.

Implementation: maintain a deque of timestamps. On each request, remove
timestamps older than (current - window_size) from the front. If the
remaining count < limit, allow and append. Otherwise reject.
```
```

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'
uv run pytest patterns/04_sliding_window/ -v --tb=short 2>&1 | tail -5

# Spot-check: Longest Repeating should have the max_freq explanation
grep "max_freq" patterns/04_sliding_window/problems/424_longest_repeating_char.md | head -3

# Spot-check: Sessionization should show 3 sessions
grep "session" patterns/04_sliding_window/de_scenarios/sessionization.md | head -5
```
