# Maximum Frequency Stack (LeetCode #895)

🔗 [LeetCode 895: Maximum Frequency Stack](https://leetcode.com/problems/maximum-frequency-stack/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Design a stack-like data structure that pops the most frequent element. If there's a tie, pop the most recently pushed among the tied elements.

## Thought Process

1. **Just a heap?** A max-heap keyed by (frequency, recency) would work for pop, but updating frequencies on push requires removing and reinserting elements - O(n) per push.
2. **The breakthrough:** An element pushed 3 times has been at frequency 1, then 2, then 3. It exists at ALL three frequency levels simultaneously. Maintain a stack for each frequency level. Pop always takes from the highest frequency stack, which gives LIFO order within that frequency.
3. **Two hash maps:** `freq` maps element to its current frequency. `group` maps frequency to a stack of elements at that level. Push appends to the current frequency's stack. Pop takes from the max frequency stack.

## Worked Example

Each frequency level has its own stack. An element appearing at frequency 3 also exists in the stacks for frequencies 1 and 2. Popping from the highest frequency stack "demotes" the element back to the previous frequency level, where it already has an entry waiting.

```
Push sequence: [5, 7, 5, 7, 4, 5]

push(5): freq={5:1}. group={1:[5]}.            max_freq=1
push(7): freq={5:1,7:1}. group={1:[5,7]}.      max_freq=1
push(5): freq={5:2,7:1}. group={1:[5,7],2:[5]}. max_freq=2
push(7): freq={5:2,7:2}. group={1:[5,7],2:[5,7]}. max_freq=2
push(4): freq={5:2,7:2,4:1}. group={1:[5,7,4],2:[5,7]}. max_freq=2
push(5): freq={5:3,7:2,4:1}. group={1:[5,7,4],2:[5,7],3:[5]}. max_freq=3

pop(): max_freq=3. Pop from group[3] -> 5.
       freq[5]=2. group[3] empty -> max_freq=2.
       group = {1:[5,7,4], 2:[5,7]}

pop(): max_freq=2. Pop from group[2] -> 7.
       freq[7]=1. group[2]=[5].
       group = {1:[5,7,4], 2:[5]}

pop(): max_freq=2. Pop from group[2] -> 5.
       freq[5]=1. group[2] empty -> max_freq=1.
       group = {1:[5,7,4]}

pop(): max_freq=1. Pop from group[1] -> 4.
       freq[4]=0.
       group = {1:[5,7]}

Notice: 5 was pushed 3 times and appears in groups 1, 2 and 3.
Each pop "peels off" one frequency layer. The element remains
in lower-frequency groups until those are popped too.
```

## Approaches

### Approach 1: Frequency Map + Group Stacks

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map for O(1) frequency lookup + stack-per-frequency for O(1) LIFO access at each level.

Two data structures:
- `freq`: dict mapping element to its current frequency
- `group`: dict mapping frequency number to a list (used as stack) of elements

**Push(x):** Increment freq[x]. Append x to group[freq[x]]. Update max_freq if needed.

**Pop():** Pop from group[max_freq]. Decrement freq for the popped element. If group[max_freq] is now empty, decrement max_freq.

The elegance: we never need to remove elements from lower-frequency groups. When an element at frequency 3 is popped, its entries in group[1] and group[2] remain valid. If it's pushed again later, it gets a new entry at the appropriate level.

**Time:** O(1) for both push and pop.
**Space:** O(n) total across all groups.

Neither a hash map alone (no LIFO ordering) nor a stack alone (no frequency tracking) solves this. The combination is essential.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| All same element | Pop returns that element each time | Single frequency group, LIFO |
| All different elements | Pop returns most recent (like normal stack) | All at frequency 1, LIFO applies |
| Push-pop-push-pop | Frequencies reset correctly | freq map tracks current state |

## Interview Tips

> "I need O(1) push and pop. A heap would give O(log n) pop. Instead, I'll use two hash maps: one for frequencies, one mapping each frequency to a stack. Push appends to the current frequency's stack. Pop takes from the highest frequency stack. An element at frequency 3 exists in all three frequency stacks simultaneously."

**The key insight to communicate:** why the element exists at multiple frequency levels, and why we don't need to clean up lower levels on pop.

**What the interviewer evaluates:** This is a hard design problem. The "element exists at multiple frequency levels" insight is non-obvious. Most candidates try a heap (O(log n) per operation) before discovering the O(1) approach. Walking through the data structure state step by step with the interviewer is essential - the design is hard to verify without a trace. The follow-up "what about thread safety?" or "what about persistence?" pivots toward system design.

## DE Application

Priority event processing where both frequency and recency matter. In a monitoring system, if the same alert fires 10 times it should be handled before one-off alerts, but among equally frequent alerts the most recent should be addressed first. This is exactly the FreqStack ordering.

## At Scale

All operations are O(1). Memory is O(n) for n pushed elements (each element exists in multiple frequency groups, but the total references are bounded by the total pushes). For 10M pushes, that's ~200MB. The data structure doesn't benefit from distribution because the frequency ordering is global state. At scale, the pattern appears in priority event processing: "handle the most frequent alert type first, breaking ties by recency." In a monitoring system processing 1M alerts/minute, the O(1) push/pop is essential. A log(n) alternative (heap) would also work but the constant factor matters at high throughput. Redis sorted sets provide a similar frequency + recency ordering in production.

## Related Problems

- [155. Min Stack](https://leetcode.com/problems/min-stack/) - Augmented stack (simpler)
- [460. LFU Cache](https://leetcode.com/problems/lfu-cache/) - Similar frequency tracking with eviction
