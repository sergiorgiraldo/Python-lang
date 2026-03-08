# Group Anagrams (LeetCode #49)

🔗 [LeetCode 49: Group Anagrams](https://leetcode.com/problems/group-anagrams/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Given an array of strings, group the anagrams together. You can return the answer in any order.

**Example:**
```
Input: strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
```

**Constraints:**
- 1 <= strs.length <= 10^4
- 0 <= strs[i].length <= 100
- strs[i] consists of lowercase English letters

---

## Thought Process

1. **Core insight** - Anagrams share the same characters. We need a way to identify "same characters" as a group key.
2. **What key to use?** - Sorting each string gives a canonical form. "eat", "tea" and "ate" all sort to "aet".
3. **Then group** - Use a hash map where the key is the canonical form and the value is a list of original strings.
4. **Can we do better than sorting?** - Yes. Count character frequencies and use the count as the key. O(k) per string instead of O(k log k).

---

## Worked Example

We need to group words that are anagrams of each other. The insight: if you sort the letters in any anagram, you get the same string. "eat" → "aet", "tea" → "aet", "ate" → "aet". That sorted string becomes the dict key, and we collect all original words that share the same key into a list.

The dict key is the sorted letters (as a string or tuple, since lists can't be keys - see "What can be a key?" in the pattern intro). The value is a list of all original words with those same sorted letters. This is the same concept as SQL's GROUP BY - instead of grouping by a column value, we're grouping by a computed value (the sorted letters).

```
Input: strs = ["eat", "tan", "ate", "nat", "bat", "tea", "tab"]

Build the groups:
  "eat" → sort letters → "aet" → groups = {"aet": ["eat"]}
  "tan" → sort letters → "ant" → groups = {"aet": ["eat"], "ant": ["tan"]}
  "ate" → sort letters → "aet" → found existing group
          groups = {"aet": ["eat", "ate"], "ant": ["tan"]}
  "nat" → sort letters → "ant" → found existing group
          groups = {"aet": ["eat", "ate"], "ant": ["tan", "nat"]}
  "bat" → sort letters → "abt" → new group
          groups = {..., "abt": ["bat"]}
  "tea" → sort letters → "aet" → found existing group
          groups = {"aet": ["eat", "ate", "tea"], "ant": ["tan", "nat"], "abt": ["bat"]}
  "tab" → sort letters → "abt" → found existing group
          groups = {..., "abt": ["bat", "tab"]}

Result: [["eat", "ate", "tea"], ["tan", "nat"], ["bat", "tab"]]

7 words processed in a single pass. Each word needs one sort (O(k log k)
where k is the word length, typically short) and one dict lookup (O(1)).

Without the dict, you'd compare every pair of words to check if they're
anagrams - that's O(n^2) pairs, each requiring an O(k) comparison.

Note: sorted("eat") returns the list ['a', 'e', 't'], which can't be a
dict key (lists are mutable). We join it into a string "aet" or convert
to a tuple ('a', 'e', 't') to make it hashable.
```

---

## Approaches

### Approach 1: Sort-Based Key

<details>
<summary>💡 Hint</summary>

If you sort the characters of two anagrams, you get the same string.

</details>

<details>
<summary>📝 Explanation</summary>

We need a way to identify which words are anagrams of each other. The insight: if we sort the letters of any anagram, we get the same string. "eat" → "aet", "tea" → "aet", "ate" → "aet". That sorted string becomes a dict key, and all words sharing the same key are anagrams of each other.

The process:
1. Create a dict where keys will be sorted letter strings and values will be lists of original words.
2. For each word in the input:
   - Sort its letters to get the canonical form: `key = "".join(sorted(word))`
   - Append the original word to `groups[key]`.
3. Return all the values (the grouped lists).

Using a `defaultdict(list)` avoids having to check if a key exists before appending - it automatically creates an empty list for new keys.

**Time:** O(n × k log k) where n is the number of words and k is the maximum word length. The sort costs O(k log k) per word, and we do it n times. The dict lookup for each word is O(k) because hashing a string takes time proportional to its length.
**Space:** O(n × k) - storing all words in the dict.

Note: `sorted("eat")` returns the list `['a', 'e', 't']`, which can't be a dict key because lists are mutable (unhashable). You need to convert it to a string (`"".join(sorted(word))`) or a tuple (`tuple(sorted(word))`) to use it as a key.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

</details>

---

### Approach 2: Frequency Count Key

<details>
<summary>💡 Hint</summary>

Instead of sorting to get a canonical form, count character frequencies. Two anagrams have identical frequency distributions.

</details>

<details>
<summary>📝 Explanation</summary>

Instead of sorting to get a canonical form, count the frequency of each character and use that count as the dict key. Two anagrams always have identical character frequency distributions.

For lowercase English letters, create a tuple of 26 counts (one per letter). "eat" → (1,0,0,0,1,...,1,...,0) where position 0 is 'a' count, position 4 is 'e' count, position 19 is 't' count. "tea" produces the exact same tuple.

The process:
1. For each word, build a frequency tuple: create a list of 26 zeros, increment the position for each character, convert to a tuple.
2. Use that tuple as the dict key (tuples are hashable, unlike lists).
3. Append the original word to the list at that key.

**Time:** O(n × k) where n is the number of words and k is the maximum word length. Building the frequency count is O(k) per word (no sorting needed). This is theoretically faster than the sort-based approach's O(n × k log k).
**Space:** O(n × k) - same as the sort approach.

In practice, the sort approach is more readable and k is usually small (typical English words are under 20 characters), so the difference between O(k) and O(k log k) is negligible. Interviewers are happy with either. The frequency approach is worth mentioning as an optimization and to show you understand there's more than one way to build a canonical key.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def group_anagrams_count(strs: list[str]) -> list[list[str]]:
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for char in s:
            count[ord(char) - ord("a")] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `["eat","tea","tan","ate","nat","bat"]` | 3 groups | Happy path |
| Single string | `["a"]` | `[["a"]]` | One group with one element |
| Empty string | `[""]` | `[[""]]` | Empty string is its own anagram |
| No anagrams | `["abc","def","ghi"]` | 3 singleton groups | Every string is unique |
| All same | `["a","a","a"]` | `[["a","a","a"]]` | Duplicates go in same group |
| Empty input | `[]` | `[]` | Nothing to group |

---

## Common Pitfalls

1. **Forgetting that tuples are hashable but lists aren't** - Use `tuple(count)` as the key, not `count` directly
2. **Not handling empty strings** - An empty string sorted is still empty, and its frequency tuple is all zeros. Both are valid keys.
3. **Returning groups in a specific order** - The problem says "any order", so don't waste time sorting the output

---

## Interview Tips

**What to say:**
> "I need a way to identify anagrams. Sorting each string gives a canonical form - all anagrams sort to the same thing. Then I just group by that key using a hash map."

**Follow-up: "Can you avoid sorting?"**
> "Yes. Instead of sorting, I can count character frequencies and use the frequency tuple as the key. That's O(k) per string instead of O(k log k)."

**Follow-up: "What if strings could contain any Unicode character?"**
→ The frequency array approach (fixed size 26) only works for lowercase English. For arbitrary characters, use `Counter` and convert to a frozenset of items or a sorted tuple of (char, count) pairs.

**What the interviewer evaluates at each stage:** The sorted-key approach tests whether you can compute a canonical form for grouping. The frequency-count key tests optimization awareness (O(k) vs O(k log k)). Recognizing this as a GROUP BY operation shows you connect algorithms to production systems. At principal level, discussing skew in the grouping (one anagram group much larger than others) is a differentiator.

---

## DE Application

This is fundamentally a GROUP BY operation implemented in code:
- Grouping records by a computed key (not a simple field value)
- Entity resolution - grouping records that represent the same entity but with variations
- Deduplication by content signature rather than exact match

The pattern of "compute a canonical key, then group by it" appears constantly in data pipelines. In SQL it's `GROUP BY`. In Spark it's `groupByKey()`. Here it's a hash map with a computed key.

---

## At Scale

The hash map stores every string, so memory scales with total input size. For 10M strings averaging 10 characters, that's roughly 200MB for the strings plus 400MB for the dict structure. The sorted-key approach creates a sorted copy of each string - for n strings of average length k, that's O(n * k * log k) time. At scale, this is a GROUP BY in Spark/SQL: `GROUP BY sorted_characters`. The shuffle groups strings with the same sorted key onto the same partition. Skew risk: if one anagram group is much larger than others (common in natural language - "aet" covers "eat", "tea", "ate"), that partition gets disproportionate work.

---

## Related Problems

- [242. Valid Anagram](242_valid_anagram.md) - The building block: checking if two strings are anagrams
- [347. Top K Frequent Elements](347_top_k_frequent.md) - Another counting + grouping problem
