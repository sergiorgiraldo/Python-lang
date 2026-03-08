# Recursion and Tree Patterns

## What Is It?

### The basics

A binary tree is a hierarchical data structure where each node has at most two children (left and right). Trees are recursive by nature: every subtree is itself a tree. This makes recursion the natural tool for tree problems.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

That's the entire data structure. Three fields. The complexity comes from how you traverse and process it.

### Why recursion works for trees

Every tree problem follows the same recursive structure:
1. **Base case:** What do you return for an empty node (None)?
2. **Recursive case:** Process the current node, recurse on left and right children, combine the results.

```python
def solve(node):
    if not node:
        return base_value          # base case

    left = solve(node.left)        # recurse left
    right = solve(node.right)      # recurse right

    return combine(node, left, right)  # combine
```

The "combine" step is what changes between problems. For max depth, it's `1 + max(left, right)`. For tree sum, it's `node.val + left + right`. For "is this a valid BST?", it's a range check. But the structure is always the same.

### Three traversal orders

How you order the "process current node" step relative to the recursive calls determines the traversal:

```
        1
       / \
      2   3
     / \
    4   5

Pre-order  (process, left, right): 1, 2, 4, 5, 3
In-order   (left, process, right): 4, 2, 5, 1, 3
Post-order (left, right, process): 4, 5, 2, 3, 1
Level-order (BFS):                 1, 2, 3, 4, 5
```

**Pre-order** visits the root first. Useful for copying trees or prefix expressions.
**In-order** visits nodes in sorted order for BSTs. Useful for validation and sorted output.
**Post-order** visits children before parent. Useful when you need child results before processing the parent (e.g., computing heights).
**Level-order (BFS)** visits by depth. Useful for shortest path and level-based processing.

### Recursion vs iteration

Every recursive solution can be converted to an iterative one using an explicit stack. The recursive call stack and the explicit stack hold the same information. Recursion is usually cleaner for trees, but iteration avoids stack overflow for very deep trees (Python's default recursion limit is 1000).

```python
# Recursive
def preorder(node):
    if not node:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

# Iterative (same result)
def preorder_iterative(root):
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            result.append(node.val)
            stack.append(node.right)  # right first (LIFO)
            stack.append(node.left)
    return result
```

### Connection to data engineering

Trees and recursion appear throughout DE work:

- **Hierarchical data:** Org charts, category trees, geographic hierarchies (country > state > city). SQL handles these with recursive CTEs.
- **Query execution plans:** Database query plans are trees. Understanding tree traversal helps you read and optimize execution plans.
- **DAG traversal:** Pipeline DAGs are trees (or more precisely, directed acyclic graphs). Topological sort (Pattern 06) is tree traversal generalized to graphs.
- **Nested JSON/XML:** Document structures are trees. Parsing and flattening them is tree traversal.
- **Bill of materials:** Manufacturing and dependency trees that need "explosion" (expanding all nested components) use recursive processing.

The recursive CTE in SQL (`WITH RECURSIVE`) is the direct SQL equivalent of recursive tree traversal in Python. Understanding one makes the other intuitive.

### What the problems in this section cover

| Problem | Concept | What it teaches |
|---|---|---|
| Max Depth | Base case + combine | The simplest tree recursion |
| Invert Binary Tree | Recursive transformation | Modifying tree structure |
| Subtree of Another Tree | Tree comparison | Combining traversal with matching |
| Lowest Common Ancestor | Path-based reasoning | Finding shared structure |
| Serialize/Deserialize | Tree <-> string | Bridges recursion and parsing |

## When to Use It

**Recognition signals in interviews:**
- The input is a TreeNode or hierarchical structure
- "Find the depth/height/diameter..."
- "Check if this tree is valid/balanced/symmetric..."
- "Find the path between two nodes..."
- "Flatten or serialize a tree..."

**Recognition signals in DE work:**
- Hierarchical data that needs traversal or flattening
- Recursive CTEs in SQL
- Pipeline dependency analysis
- Nested document processing

## Visual Aid

```
Tree structure and recursive depth calculation:

        3
       / \
      9   20
         / \
        15   7

  maxDepth(3):
    left  = maxDepth(9)  = 1  (leaf: base + 1)
    right = maxDepth(20) = 2
      left  = maxDepth(15) = 1
      right = maxDepth(7)  = 1
      return 1 + max(1, 1) = 2
    return 1 + max(1, 2) = 3

  Each recursive call handles a smaller subtree.
  The base case (None -> 0) stops the recursion.
  Results bubble up from leaves to root.
```

## Trade-offs

**Recursion vs iteration:**
- Recursion: cleaner code, natural fit for trees. Risk of stack overflow for deep trees (Python limit ~1000).
- Iteration with stack: avoids overflow, can be faster (no function call overhead). More verbose.
- For interviews, use recursion unless the problem specifically requires handling very deep trees.

**DFS vs BFS:**
- DFS (depth-first): uses O(h) space where h is height. Better for deep, narrow trees.
- BFS (breadth-first): uses O(w) space where w is max width. Better for wide, shallow trees.
- DFS finds depth/path answers naturally. BFS finds level-order and shortest-path answers naturally.

### Scale characteristics

Tree traversals are O(n) time and O(h) space where h is the tree height. For balanced trees, h = log n. For skewed trees, h = n.

| Tree shape | Height | Stack/recursion depth at n=1M |
|---|---|---|
| Balanced | ~20 | 20 frames (~trivial) |
| Skewed (linked list) | 1M | 1M frames (stack overflow) |

Python's default recursion limit is 1000. A skewed tree with 10K nodes crashes recursive approaches. Converting to iterative with an explicit stack handles arbitrary depth. In production, always use iterative traversal for untrusted or unbounded tree structures.

**Distributed tree processing:** Trees themselves are small in most DE contexts (org charts, category hierarchies, bill of materials - hundreds to thousands of nodes). The data ATTACHED to trees is large: "aggregate revenue for every node and all its descendants" over 1B transaction records. This is a GROUP BY with recursive rollup. In SQL, recursive CTEs handle the tree traversal, and the engine handles the aggregation at scale. In Spark, broadcast the tree structure (small) and join with the transaction data (large).

**Serialization matters:** Serialized trees (preorder with null markers, or level-order) are compact and cacheable. The (de)serialization in problem 297 is essentially the same as JSON/XML parsing: a structured format that encodes a hierarchical structure. At scale, choosing between JSON (human-readable, larger) and binary formats (Protobuf, Avro - compact, schema-required) is a common engineering decision.

### SQL equivalent

Tree operations in SQL use recursive CTEs. `WITH RECURSIVE cte AS (SELECT root UNION ALL SELECT child FROM cte JOIN edges...)` builds the tree level by level. This is BFS in SQL. The SQL section's recursive CTE subsection covers hierarchy traversal, path enumeration and bill-of-materials explosion. The key difference: SQL processes trees set-at-a-time (all nodes at a level simultaneously), while Python processes node-by-node. SQL's approach is naturally parallel for wide trees but struggles with deep trees (many recursion levels).

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| [104](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | [Maximum Depth](problems/104_max_depth.md) | Easy | Base case + recursive combine |
| [226](https://leetcode.com/problems/invert-binary-tree/) | [Invert Binary Tree](problems/226_invert_tree.md) | Easy | Recursive transformation |
| [572](https://leetcode.com/problems/subtree-of-another-tree/) | [Subtree of Another Tree](problems/572_subtree.md) | Easy | Tree comparison with DFS |
| [236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | [Lowest Common Ancestor](problems/236_lca.md) | Medium | Path finding in trees |
| [297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) | [Serialize/Deserialize](problems/297_serialize_deserialize.md) | Hard | Tree <-> string conversion |

## DE Scenarios

| Scenario | Technique | Real-World Use |
|---|---|---|
| [Org Chart Traversal](de_scenarios/org_chart.md) | Recursive CTE | Reporting hierarchies |
| [Category Tree Explosion](de_scenarios/category_tree.md) | Recursive expansion | E-commerce category paths |
| [Bill of Materials](de_scenarios/bill_of_materials.md) | Recursive explosion | Manufacturing dependencies |
| [Pipeline DAG Analysis](de_scenarios/pipeline_dag.md) | Graph traversal | Upstream/downstream discovery |
