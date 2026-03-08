# Invert Binary Tree (LeetCode #226)

🔗 [LeetCode 226: Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given the root of a binary tree, invert the tree and return its root. Inverting means swapping every left and right child throughout the tree.

```
Input:       Output:
    4            4
   / \          / \
  2   7   ->   7   2
 / \ / \     / \ / \
1  3 6  9   9  6 3  1
```

## Thought Process

1. **What does "invert" mean?** At every node, swap its left and right children. Do this recursively and the whole tree mirrors.
2. **Base case:** An empty node (None) stays None.
3. **Recursive case:** Swap current node's children, then recursively invert both subtrees.
4. **Order doesn't matter:** You can swap before or after recursing. Pre-order or post-order both work. The swap at each node is independent.

## Worked Example

At each node, swap left and right pointers. The recursion ensures this happens at every level. The key insight: swapping at the root alone only mirrors the top level. Recursing ensures every level gets mirrored.

```
Input tree:
        4
       / \
      2   7
     / \ / \
    1  3 6  9

Step 1: At node 4, swap children.
        4
       / \
      7   2       <- 7 and 2 swapped
     / \ / \
    6  9 1  3     <- but subtrees came along unchanged

Step 2: Recurse on node 7 (was right, now left). Swap its children.
        4
       / \
      7   2
     / \ / \
    9  6 1  3     <- 9 and 6 swapped within the 7 subtree

Step 3: Recurse on node 2 (was left, now right). Swap its children.
        4
       / \
      7   2
     / \ / \
    9  6 3  1     <- 3 and 1 swapped within the 2 subtree

Result: [4, 7, 2, 9, 6, 3, 1]

Each node visited once. O(n) time, O(h) space.
```

## Approaches

### Approach 1: Recursive DFS

<details>
<summary>📝 Explanation</summary>

At each node, swap `node.left` and `node.right` using Python's tuple swap. Then recurse on both children. The base case (None) returns None.

Python's tuple swap `root.left, root.right = root.right, root.left` is atomic - both sides are evaluated before assignment, so no temp variable is needed.

The recursion order (pre-order: swap then recurse, vs post-order: recurse then swap) doesn't affect correctness. Both visit every node and perform the swap.

**Time:** O(n) - visit every node once.
**Space:** O(h) - recursion depth equals tree height.

Three lines of code after the base case. This is recursion at its cleanest.

</details>

### Approach 2: Iterative BFS

<details>
<summary>📝 Explanation</summary>

Use a queue to process nodes level by level. For each node, swap its children and enqueue them. The queue ensures every node gets processed.

Functionally identical to the recursive version but uses an explicit queue instead of the call stack. Useful if the tree could be extremely deep (avoiding stack overflow) or if you prefer iterative solutions.

**Time:** O(n).
**Space:** O(w) where w is the max width (up to n/2 for a balanced tree).

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `None` | `None` | Empty tree stays empty |
| `[1]` | `[1]` | Single node is its own mirror |
| `[1, 2]` | `[1, None, 2]` | Left child becomes right child |
| `[1, 2, 3, 4, 5, 6, 7]` | `[1, 3, 2, 7, 6, 5, 4]` | Full balanced tree |

## Common Pitfalls

- **Modifying the tree in place vs returning a new tree:** This problem modifies in place. If the problem asked for a new tree, you'd create new nodes.
- **Swapping only at the root:** The swap must happen at every node, not just the top.

## Interview Tips

> "Invert means swap left and right at every node, recursively. Base case: None stays None. At each node: swap children, recurse on both. O(n) time since we visit every node once."

This is often a quick warm-up. Demonstrate clean recursion and move on.

**What the interviewer evaluates:** Simple recursive swap tests your comfort with tree mutation. The key question is traversal order: pre-order (swap then recurse) and post-order (recurse then swap) both work. In-order doesn't (you'd swap, recurse left which is now the old right, then swap back). Explaining which orders work and why shows understanding.

## DE Application

Data transformation patterns. Mirroring a tree structure is analogous to pivoting or transposing hierarchical data. More practically, the pattern of "apply a transformation at every node" is the same pattern used when transforming nested JSON documents (changing keys, restructuring levels).

## At Scale

Inverting a tree is O(n) time and O(h) space. Every node is visited once, and children are swapped. At scale, the relevant application is schema transformation: mirroring a hierarchical schema, reversing parent-child relationships for a different query pattern. In a data warehouse, denormalized hierarchies are sometimes stored in both directions (top-down for breadcrumb navigation, bottom-up for rollup aggregation). Building the inverted version is a one-time ETL operation, not a runtime operation. The recursive vs iterative choice matters only for very deep hierarchies.

## Related Problems

- [101. Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) - Check if a tree is its own mirror
- [100. Same Tree](https://leetcode.com/problems/same-tree/) - Compare two trees node by node
