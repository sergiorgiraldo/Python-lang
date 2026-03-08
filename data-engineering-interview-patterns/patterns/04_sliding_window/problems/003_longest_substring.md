# Longest Substring Without Repeating Characters (LeetCode #3)

🔗 [LeetCode 3: Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given a string `s`, find the length of the longest substring without repeating characters.

**Example:**
```
Input: s = "abcabcbb"
Output: 3 ("abc")

Input: s = "bbbbb"
Output: 1 ("b")

Input: s = "pwwkew"
Output: 3 ("wke")
```

**Constraints:**
- 0 <= s.length <= 5 * 10^4
- s consists of English letters, digits, symbols and spaces

---

## Thought Process

1. **Brute force:** Check every possible substring for uniqueness. O(n^3) - two loops for substring boundaries, one to check uniqueness.
2. **Better:** Use a set to check uniqueness in O(1), reducing to O(n^2).
3. **Best:** Sliding window. When a duplicate appears, don't start over from scratch. Shrink from the left until the duplicate is gone.
4. **Even better:** Instead of shrinking one step at a time, track each character's last index and jump `left` directly past the duplicate.

---

## Worked Example

Find the longest substring with no repeating characters. This is a variable-size window problem. The right pointer expands the window one character at a time. When a duplicate character enters, the left pointer contracts the window until the duplicate is gone.

We use a set to track characters currently in the window. When the new character is already in the set, we shrink from the left, removing characters from the set, until the duplicate is gone.

```
Input: s = "abcdbefa"

  left=0

  right=0: char='a', seen={}, 'a' not in seen → add. seen={a}. Length=1.
  right=1: char='b', not in seen → add. seen={a,b}. Length=2.
  right=2: char='c', not in seen → add. seen={a,b,c}. Length=3.
  right=3: char='d', not in seen → add. seen={a,b,c,d}. Length=4. max=4.

  right=4: char='b', 'b' IS in seen → duplicate. Contract from left:
    Remove s[0]='a'. left=1. seen={b,c,d}. 'b' still in seen.
    Remove s[1]='b'. left=2. seen={c,d}. 'b' gone. Stop contracting.
    Add 'b'. seen={c,d,b}. Length=3.

  right=5: char='e', not in seen → add. seen={c,d,b,e}. Length=4. max=4.
  right=6: char='f', not in seen → add. seen={c,d,b,e,f}. Length=5. max=5.
  right=7: char='a', not in seen → add. seen={c,d,b,e,f,a}. Length=6. max=6.

  Answer: 6 (the substring "cdbefa").

Both pointers moved a total of 8+2 = 10 positions combined for an
8-character string. The brute force approach (check all 36 substrings)
would do much more work, especially on longer strings.
```

---

## Approaches

### Approach 1: Set-Based Variable Window

<details>
<summary>💡 Hint 1</summary>

When you find a duplicate, you don't need to reset. You only need to remove characters from the left until the duplicate is gone.

</details>

<details>
<summary>📝 Explanation</summary>

Use a set to track characters in the current window. The right pointer expands the window by adding characters. When the new character is already in the set (duplicate), shrink the window from the left by removing characters until the duplicate is gone.

1. Initialize `left = 0`, `seen = set()`, `max_len = 0`.
2. For each `right` from 0 to n-1:
   - While `s[right]` is in `seen`: remove `s[left]` from seen, increment left.
   - Add `s[right]` to seen.
   - Update `max_len = max(max_len, right - left + 1)`.

The inner while loop removes characters one by one from the left until the duplicate is gone. In the worst case (like "abcabc"), each character is added once and removed once, so the total work is O(n).

**Time:** O(n) - each character enters and leaves the set at most once.
**Space:** O(min(n, alphabet_size)) - the set holds at most one of each character. For lowercase English letters, that's at most 26.

</details>

<details>
<summary>💻 Code</summary>

```python
def length_of_longest_substring_set(s: str) -> int:
    char_set = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
```

</details>

### Approach 2: Hash Map with Jump (Optimal)

<details>
<summary>💡 Hint 2</summary>

If you know the index of the duplicate character's last occurrence, you can jump `left` directly past it instead of sliding one step at a time.

</details>

<details>
<summary>📝 Explanation</summary>

An optimization: instead of removing characters one by one from the left, use a dict that maps each character to its most recent index. When a duplicate is found, jump `left` directly past the previous occurrence.

1. Initialize `left = 0`, `char_index = {}`, `max_len = 0`.
2. For each `right`:
   - If `s[right]` is in `char_index` AND `char_index[s[right]] >= left`:
     Jump `left` to `char_index[s[right]] + 1` (one past the previous occurrence).
   - Update `char_index[s[right]] = right`.
   - Update `max_len`.

The `>= left` check is important: the character might be in the dict from before the current window (left has moved past it). Only jump if the previous occurrence is still inside the current window.

**Time:** O(n) - single pass. No inner loop because `left` jumps instead of walking.
**Space:** O(min(n, alphabet_size)) - the dict stores one entry per unique character.

The time complexity is the same O(n) as the set approach (both visit each element at most twice), but the jump avoids the inner while loop, making the code slightly simpler and potentially faster in practice.

</details>

<details>
<summary>💻 Code</summary>

```python
def length_of_longest_substring(s: str) -> int:
    char_index = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `"abcabcbb"` | `3` | Basic case |
| All same | `"bbbbb"` | `1` | Maximum contraction |
| Partial repeat | `"pwwkew"` | `3` | Repeat in middle |
| Empty | `""` | `0` | No characters |
| Single | `"a"` | `1` | Trivial case |
| All unique | `"abcdef"` | `6` | Window = entire string |
| `"dvdf"` | `"dvdf"` | `3` | Left must jump, not just slide |

The `"dvdf"` case is the classic trap. When we hit the second `d`, left must jump past index 0 (the first `d`). But the first `v` at index 1 is already past where left needs to be. The `char_index[char] >= left` check handles this: we only jump if the duplicate is still inside our current window.

---

## Common Pitfalls

1. **Not checking `char_index[char] >= left`** - The character might have a stored index from before the current window. Jumping to it would move left backward, which is wrong.
2. **Using a set without the jump optimization** - Both are O(n) but the hash map with jump does fewer operations on strings with many repeated characters.
3. **Returning max_len vs the substring** - The problem asks for the length. If asked for the actual substring, track `max_start` and `max_end` alongside `max_len`.

---

## Interview Tips

**What to say:**
> "This is a variable-size sliding window. I'll expand right and track characters in a hash map. When I hit a duplicate that's inside my window, I'll jump left past it. Each character is processed at most twice, so it's O(n)."

**The "dvdf" case is worth mentioning.** If the interviewer gives you this test case, explain the `>= left` check. It shows you understand the subtlety.

**This is probably the most common medium-difficulty interview question.** It comes up frequently because it tests sliding windows, hash maps and edge case handling in one clean problem.

**What the interviewer evaluates:** Variable-size windows are harder than fixed-size. The expand/shrink logic tests your ability to manage two pointers with a state invariant. Getting the shrink condition right (when to move left) is where most candidates struggle. A clean implementation with clear variable names is a strong signal.

---

## DE Application

Variable-size windows with uniqueness constraints appear when:
- Finding the longest period without repeated error codes in a log
- Detecting unique user sessions (no repeated page views within a session)
- Analyzing network packets for unique signature sequences
- Any streaming scenario where you need the longest "clean" run

The set-based approach maps directly to streaming deduplication windows, where you maintain a set of recently seen IDs and check incoming records against it.

## At Scale

The hash set tracks characters in the current window. For ASCII input, that's at most 128 entries - O(1) space regardless of string length. For Unicode, the set could grow to thousands of entries but is still bounded by the character set, not the string length. At 1B characters, the single-pass O(n) algorithm takes ~10 seconds. The practical equivalent in data pipelines: finding the longest period of unique events in a time series. In SQL: a self-join or window function approach, though the sliding window algorithm is more efficient than what most SQL engines generate for this type of query.

---

## Related Problems

- [219. Contains Duplicate II](219_contains_duplicate_ii.md) - Fixed window with uniqueness (simpler version)
- [424. Longest Repeating Character Replacement](424_longest_repeating_char.md) - Variable window with a different constraint
- [76. Minimum Window Substring](076_min_window_substring.md) - Variable window finding the shortest (not longest) match
- [1. Two Sum](../../01_hash_map/problems/001_two_sum.md) - Same hash map lookup technique for a different pattern
