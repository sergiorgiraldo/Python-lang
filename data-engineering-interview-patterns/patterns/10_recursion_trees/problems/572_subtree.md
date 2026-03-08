# Subtree of Another Tree (LeetCode #572)

🔗 [LeetCode 572: Subtree of Another Tree](https://leetcode.com/problems/subtree-of-another-tree/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given the roots of two binary trees `root` and `subRoot`, return True if there is a subtree of `root` with the same structure and node values as `subRoot`.

## Thought Process

1. **Two separate recursive checks:** First, traverse `root` looking for nodes where the subtree might start. Second, at each candidate node, check if the subtrees are identical.
2. **"Same tree" helper:** Comparing two trees for equality is itself recursive: same value at the root, same left subtree, same right subtree.
3. **Combine:** For each node in `root`, check "is the tree rooted here identical to `subRoot`?" If yes at any node, return True.

## Worked Example

Two levels of recursion: the outer one traverses the main tree looking for a match, the inner one compares entire subtrees node by node. The outer traversal visits every node in `root`. At each node, the inner comparison runs against `subRoot`.

```
root:            subRoot:
    3               4
   / \             / \
  4   5           1   2
 / \
1   2

Outer traversal of root:
  Node 3: is tree(3) same as tree(4)?
    3 vs 4 -> values differ. No.
  Recurse left -> Node 4: is tree(4) same as tree(4)?
    4 vs 4 -> match. Check children:
      1 vs 1 -> match. Children: None vs None -> match (both leaves).
      2 vs 2 -> match. Children: None vs None -> match.
    All nodes match. -> TRUE.

  Return True (found at node 4).

Worst case: every node in root triggers a full comparison
with subRoot. O(m * n) where m = |root|, n = |subRoot|.
```

## Approaches

### Approach 1: DFS + Same Tree Check

<details>
<summary>📝 Explanation</summary>

Two functions: `is_subtree` traverses the main tree, calling `is_same_tree` at each node. `is_same_tree` does a node-by-node comparison of two trees.

`is_subtree(root, sub)`:
- If sub is None, return True (empty tree is a subtree of anything).
- If root is None, return False (non-empty sub can't match empty root).
- If `is_same_tree(root, sub)`, return True.
- Otherwise, recurse: `is_subtree(root.left, sub) or is_subtree(root.right, sub)`.

`is_same_tree(p, q)`:
- If both None, return True.
- If one is None or values differ, return False.
- Recurse on both children.

**Time:** O(m * n) worst case. For each of m nodes in root, we might compare n nodes in subRoot. In practice, most comparisons fail early at the root value check.
**Space:** O(h) for the recursion stack where h is the height of root.

There are O(m + n) approaches using tree serialization or hashing, but the recursive approach is cleaner for interviews and sufficient for all but extreme cases.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `subRoot` is None | True | Empty tree is always a subtree |
| `root` is None, `subRoot` is not | False | Can't find a non-empty subtree in nothing |
| Identical trees | True | The whole tree is a subtree of itself |
| Same values but different structure | False | Structure must match exactly |

## Common Pitfalls

- **Confusing "subtree" with "substructure":** A subtree must match from a node all the way down to the leaves. A node in root with the same value but extra children below doesn't count.
- **Forgetting the None-None base case in is_same_tree:** Both None is True (matching empty subtrees), not False.

## Interview Tips

> "I'll use two recursive functions: one to traverse the main tree finding candidate roots, and one to compare entire subtrees. The comparison function checks value equality and recurses on both children."

**What the interviewer evaluates:** The decomposition into "check every node as potential root" + "are these two trees identical?" tests recursive composition. The serialization optimization (O(n+m) with string matching) tests whether you can find non-obvious approaches. Mentioning KMP or hashing for the string match shows algorithmic breadth.

## DE Application

Schema comparison: checking if a subset schema exists within a larger document structure. Also used in AST (abstract syntax tree) matching for code analysis tools and query plan comparison in query optimization.

## At Scale

Naive subtree matching is O(n * m) where n is the main tree and m is the candidate subtree. For large trees, this is expensive. The serialization approach (serialize both trees, check if one string contains the other) reduces to O(n + m) using KMP or similar string matching. At scale, subtree matching appears in schema comparison: "is this table's column structure a subset of another table's?" and in data lineage: "does this DAG subgraph appear as part of a larger pipeline?" These are typically small-graph operations even in large systems.

## Related Problems

- [100. Same Tree](https://leetcode.com/problems/same-tree/) - The helper function on its own
- [652. Find Duplicate Subtrees](https://leetcode.com/problems/find-duplicate-subtrees/) - Find all matching subtrees
