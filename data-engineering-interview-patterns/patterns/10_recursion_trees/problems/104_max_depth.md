# Maximum Depth of Binary Tree (LeetCode #104)

🔗 [LeetCode 104: Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given the root of a binary tree, return its maximum depth. Maximum depth is the number of nodes along the longest path from root to the farthest leaf.

## Thought Process

1. **Base case:** An empty tree (None) has depth 0.
2. **Recursive case:** The depth of a tree is 1 (the current node) plus the maximum of its left subtree's depth and right subtree's depth.
3. **That's it.** This is the simplest tree recursion and the foundation for every other tree problem.

## Worked Example

Every tree problem starts with the same question: what's the base case, and how do I combine child results? For max depth, the base case is "empty tree -> 0" and the combination is "1 + max(left depth, right depth)." The recursion handles all the traversal automatically.

```
        3
       / \
      9   20
         / \
        15   7

  maxDepth(3):
    maxDepth(9):
      maxDepth(None) = 0     <- base case
      maxDepth(None) = 0     <- base case
      return 1 + max(0, 0) = 1
    maxDepth(20):
      maxDepth(15):
        return 1 + max(0, 0) = 1
      maxDepth(7):
        return 1 + max(0, 0) = 1
      return 1 + max(1, 1) = 2
    return 1 + max(1, 2) = 3

  Answer: 3 (path: 3 -> 20 -> 15 or 3 -> 20 -> 7)

  The recursion visits every node exactly once: O(n).
  The call stack depth equals the tree height: O(h).
  For a balanced tree, h = log(n). For a skewed tree, h = n.
```

## Approaches

### Approach 1: Recursive DFS

<details>
<summary>📝 Explanation</summary>

The classic recursive solution. If the node is None, return 0. Otherwise return 1 plus the max of the recursive calls on left and right children.

This is post-order traversal: we need the child results (depths) before we can compute the parent's depth. The recursion handles this naturally because the recursive calls complete before the current call returns.

**Time:** O(n) - every node is visited exactly once.
**Space:** O(h) where h is the tree height. The recursion stack holds one frame per level. For a balanced tree, h = O(log n). For a completely skewed tree (linked list), h = O(n).

This is the textbook starting point for tree problems. Master this pattern and every other tree problem is a variation.

</details>

### Approach 2: Iterative BFS

<details>
<summary>📝 Explanation</summary>

Use a queue to process the tree level by level. Each level adds 1 to the depth counter. The number of levels IS the max depth.

Process all nodes at the current level (using the queue's current size), enqueue their children, increment the depth counter. When the queue is empty, all levels have been processed.

**Time:** O(n) - same as recursive.
**Space:** O(w) where w is the maximum width of the tree. For a balanced tree, the bottom level has ~n/2 nodes, so space is O(n). For a skewed tree, each level has 1 node, so space is O(1).

BFS is a natural fit when you're counting levels. DFS is more natural when you're computing path-based properties.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `None` | 0 | Empty tree |
| `[1]` | 1 | Single node is both root and leaf |
| `[1, 2, None, 3, None, 4]` | 4 | Left-skewed (worst case for recursion depth) |
| `[1, 2, 3, 4, 5, 6, 7]` | 3 | Balanced tree |

## Common Pitfalls

- **Confusing depth with height:** Some definitions count edges (height) vs nodes (depth). LeetCode counts nodes. Clarify in the interview.
- **Forgetting the +1:** `max(left, right)` gives the subtree depth. You need `1 + max(left, right)` to include the current node.

## Interview Tips

> "The depth of a tree is 1 plus the max depth of its subtrees. Base case: an empty tree has depth 0. This visits every node once, so it's O(n) time and O(h) space for the recursion stack."

This is often a warm-up problem. Solve it quickly and cleanly to build momentum.

**What the interviewer evaluates:** This tests basic tree recursion. Clean `1 + max(left, right)` is expected immediately. The base case (None -> 0) tests edge case handling. This is a warm-up - finishing fast shows fluency. The follow-up "what about iterative?" tests whether you can convert recursion to a stack or queue.

## DE Application

Measuring hierarchy depth in data. "How many levels deep is our org chart?" is the same computation. In SQL: `WITH RECURSIVE` to walk the hierarchy, counting levels. The recursive CTE's anchor clause is the base case, and the recursive clause is the "1 + recurse on children" step.

## At Scale

Recursive DFS uses O(h) stack space. For a balanced tree with 1M nodes, that's ~20 stack frames - trivial. For a skewed tree with 1M nodes, it crashes Python (recursion limit). The iterative BFS approach uses O(w) memory where w is the maximum width - O(n/2) for a balanced tree's last level, which is actually more memory than DFS for balanced trees. At scale, tree depth computations are usually done in SQL with recursive CTEs: `WITH RECURSIVE depths AS (...)`. The recursion depth limit in BigQuery is 500, in Snowflake it's configurable. For very deep trees, iterative SQL approaches (repeated self-joins) avoid the recursion limit.

## Related Problems

- [111. Minimum Depth](https://leetcode.com/problems/minimum-depth-of-binary-tree/) - Similar but finds the shallowest leaf
- [543. Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) - Max depth variant tracking the longest path through any node
