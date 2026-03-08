# Serialize and Deserialize Binary Tree (LeetCode #297)

🔗 [LeetCode 297: Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Design an algorithm to serialize a binary tree to a string and deserialize it back. There is no restriction on the format, but serialize and deserialize must be inverses of each other.

## Thought Process

1. **The challenge:** A tree is a 2D structure (nodes with pointers). A string is 1D. We need a serialization format that captures both values AND structure unambiguously.
2. **Pre-order with null markers:** If we serialize in pre-order (root, left, right) and write "null" for every missing child, the format is unambiguous. The decoder can reconstruct the exact tree by consuming tokens in the same order.
3. **Why pre-order?** The root comes first, which makes it natural to build the tree top-down during deserialization. Each recursive call consumes exactly the tokens for its subtree.

## Worked Example

Pre-order traversal with null markers creates an unambiguous encoding. The decoder reads tokens left to right, building nodes recursively. Each "null" token tells the decoder "this child doesn't exist, stop recursing on this side."

```
Tree:
      1
     / \
    2   3
       / \
      4   5

Serialize (pre-order with nulls):
  visit 1 -> "1"
  visit 2 -> "2"
    left of 2: null -> "null"
    right of 2: null -> "null"
  visit 3 -> "3"
  visit 4 -> "4"
    left of 4: null -> "null"
    right of 4: null -> "null"
  visit 5 -> "5"
    left of 5: null -> "null"
    right of 5: null -> "null"

  Serialized: "1,2,null,null,3,4,null,null,5,null,null"

Deserialize:
  tokens: [1, 2, null, null, 3, 4, null, null, 5, null, null]

  consume "1" -> create node(1)
    left: consume "2" -> create node(2)
      left: consume "null" -> return None
      right: consume "null" -> return None
    right: consume "3" -> create node(3)
      left: consume "4" -> create node(4)
        left: consume "null" -> return None
        right: consume "null" -> return None
      right: consume "5" -> create node(5)
        left: consume "null" -> return None
        right: consume "null" -> return None

  Each recursive call consumes exactly its own subtree's tokens.
  The deque (popleft) ensures tokens are consumed in order.
```

## Approaches

### Approach 1: Pre-order DFS

<details>
<summary>📝 Explanation</summary>

Serialize: walk the tree in pre-order. Append the node's value or "null" for missing nodes. Join with commas.

Deserialize: split the string on commas into a deque. Recursively consume tokens: if the token is "null", return None. Otherwise create a node and recursively build its left and right children.

The deque is critical: `popleft()` ensures each token is consumed exactly once and in the correct order. The recursion structure of deserialization mirrors the recursion structure of serialization, which guarantees they're inverses.

**Time:** O(n) for both serialize and deserialize. Each node produces/consumes exactly one token (plus two null markers for leaves).
**Space:** O(n) for the string. O(h) for the recursion stack.

</details>

### Approach 2: Level-order BFS

<details>
<summary>📝 Explanation</summary>

Serialize with BFS (level-order). This produces the same format LeetCode uses to display trees: `[1, 2, 3, null, null, 4, 5]`. Strip trailing nulls to save space.

Deserialize by processing tokens with a queue: create the root, then for each node in the queue, consume the next two tokens as its left and right children.

BFS serialization is more human-readable (it shows the tree level by level) and compact (trailing nulls stripped). DFS serialization is simpler to implement and reason about.

**Time:** O(n) for both.
**Space:** O(n) for the queue (up to n/2 nodes at the widest level).

</details>

## Edge Cases

| Input | Why It Matters |
|---|---|
| Empty tree | Serialize to empty string, deserialize back to None |
| Single node | Simplest non-empty tree |
| Left-skewed | Every node has only a left child |
| Negative values | "-1" must not be confused with a delimiter |
| Large values | Multi-digit numbers serialize correctly |

## Common Pitfalls

- **Not handling null markers:** Without explicit nulls, "1,2,3" is ambiguous (multiple tree structures produce the same in-order traversal).
- **Using a list index instead of a deque:** With a list you need to pass the index by reference (or use a mutable wrapper). A deque with popleft is cleaner.
- **Forgetting to handle the empty string in deserialize:** If serialize returns "" for None, deserialize must handle "" as input.

## Interview Tips

> "I'll use pre-order traversal with null markers. This captures both values and structure. Deserialization consumes tokens in the same order using a deque, recursively building the tree. Both operations are O(n)."

**This is a Hard problem.** Take time to explain the format before coding. Draw the serialized string and show how the decoder would consume it.

**What the interviewer evaluates:** Designing a serialization format that can reconstruct the tree unambiguously tests protocol design. Preorder with null markers is the standard approach. The interviewer may ask about alternatives (level-order, parenthesized) and their tradeoffs. Mentioning production storage formats (adjacency list vs nested sets vs materialized paths) shows database design knowledge - a strong principal-level signal.

## DE Application

This bridges Pattern 09 (string parsing) and Pattern 10 (recursion). Serialization is everywhere in DE: JSON (tree -> string), Avro/Parquet (nested structures -> bytes), protocol buffers. Understanding how tree structures are serialized and restored helps debug data format issues and design efficient transport formats.

## At Scale

Serialized tree size is O(n) - each node contributes a value and null markers for missing children. For 1M nodes with integer values, the serialized form is ~10MB (values + delimiters). Serialization format choice matters at scale: the comma-separated preorder format here is simple but not self-describing. Production formats (JSON, Protobuf, Avro) add type information and schema. For trees stored in databases, the adjacency list (parent_id column), nested sets or materialized path approaches trade storage for query efficiency. The adjacency list is simplest to update. Nested sets enable fast subtree queries. Materialized paths enable fast ancestor queries. Choosing the right representation is a principal-level design decision.

## Related Problems

- [449. Serialize and Deserialize BST](https://leetcode.com/problems/serialize-and-deserialize-bst/) - More efficient for BSTs
- [271. Encode and Decode Strings](https://leetcode.com/problems/encode-and-decode-strings/) - Pattern 09, same concept for flat lists
