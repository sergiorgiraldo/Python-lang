# CC Prompt: Enrich Pattern 10 (Recursion/Trees) to Principal Level

## Context

Pattern 10 has 5 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/10_recursion_trees/README.md`, find `## Trade-offs` and ADD:

```markdown
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
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 104_max_depth.md (or actual filename)
```markdown
## At Scale

Recursive DFS uses O(h) stack space. For a balanced tree with 1M nodes, that's ~20 stack frames - trivial. For a skewed tree with 1M nodes, it crashes Python (recursion limit). The iterative BFS approach uses O(w) memory where w is the maximum width - O(n/2) for a balanced tree's last level, which is actually more memory than DFS for balanced trees. At scale, tree depth computations are usually done in SQL with recursive CTEs: `WITH RECURSIVE depths AS (...)`. The recursion depth limit in BigQuery is 500, in Snowflake it's configurable. For very deep trees, iterative SQL approaches (repeated self-joins) avoid the recursion limit.
```

### 226_invert_binary_tree.md
```markdown
## At Scale

Inverting a tree is O(n) time and O(h) space. Every node is visited once, and children are swapped. At scale, the relevant application is schema transformation: mirroring a hierarchical schema, reversing parent-child relationships for a different query pattern. In a data warehouse, denormalized hierarchies are sometimes stored in both directions (top-down for breadcrumb navigation, bottom-up for rollup aggregation). Building the inverted version is a one-time ETL operation, not a runtime operation. The recursive vs iterative choice matters only for very deep hierarchies.
```

### 572_subtree_of_another_tree.md
```markdown
## At Scale

Naive subtree matching is O(n * m) where n is the main tree and m is the candidate subtree. For large trees, this is expensive. The serialization approach (serialize both trees, check if one string contains the other) reduces to O(n + m) using KMP or similar string matching. At scale, subtree matching appears in schema comparison: "is this table's column structure a subset of another table's?" and in data lineage: "does this DAG subgraph appear as part of a larger pipeline?" These are typically small-graph operations even in large systems.
```

### 236_lowest_common_ancestor.md
```markdown
## At Scale

Single LCA query is O(n) time with O(h) space for the recursion stack. For multiple LCA queries on the same tree, preprocessing with Euler tour + sparse table gives O(n log n) preprocessing and O(1) per query. At scale, LCA computations appear in org chart analysis ("who is the lowest common manager of employees A and B?"), taxonomy navigation ("what is the most specific shared category?") and version control (finding the merge base of two branches). In SQL, LCA requires computing ancestors for both nodes (recursive CTE), then finding the deepest shared ancestor. This is O(depth) per query - efficient for shallow hierarchies but slow for deep ones.
```

### 297_serialize_deserialize.md
```markdown
## At Scale

Serialized tree size is O(n) - each node contributes a value and null markers for missing children. For 1M nodes with integer values, the serialized form is ~10MB (values + delimiters). Serialization format choice matters at scale: the comma-separated preorder format here is simple but not self-describing. Production formats (JSON, Protobuf, Avro) add type information and schema. For trees stored in databases, the adjacency list (parent_id column), nested sets or materialized path approaches trade storage for query efficiency. The adjacency list is simplest to update. Nested sets enable fast subtree queries. Materialized paths enable fast ancestor queries. Choosing the right representation is a principal-level design decision.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 104 (Max Depth):
```markdown
**What the interviewer evaluates:** This tests basic tree recursion. Clean `1 + max(left, right)` is expected immediately. The base case (None → 0) tests edge case handling. This is a warm-up - finishing fast shows fluency. The follow-up "what about iterative?" tests whether you can convert recursion to a stack or queue.
```

### 226 (Invert Binary Tree):
```markdown
**What the interviewer evaluates:** Simple recursive swap tests your comfort with tree mutation. The key question is traversal order: pre-order (swap then recurse) and post-order (recurse then swap) both work. In-order doesn't (you'd swap, recurse left which is now the old right, then swap back). Explaining which orders work and why shows understanding.
```

### 572 (Subtree of Another Tree):
```markdown
**What the interviewer evaluates:** The decomposition into "check every node as potential root" + "are these two trees identical?" tests recursive composition. The serialization optimization (O(n+m) with string matching) tests whether you can find non-obvious approaches. Mentioning KMP or hashing for the string match shows algorithmic breadth.
```

### 236 (LCA):
```markdown
**What the interviewer evaluates:** The recursive post-order approach (return the node if it matches, propagate upward) is elegant but non-obvious. Walking through an example is essential - the interviewer wants to see you trace the recursion. The follow-up "what about multiple queries on the same tree?" tests preprocessing knowledge (Euler tour, binary lifting). Connecting to org chart queries shows DE application.
```

### 297 (Serialize/Deserialize):
```markdown
**What the interviewer evaluates:** Designing a serialization format that can reconstruct the tree unambiguously tests protocol design. Preorder with null markers is the standard approach. The interviewer may ask about alternatives (level-order, parenthesized) and their tradeoffs. Mentioning production storage formats (adjacency list vs nested sets vs materialized paths) shows database design knowledge - a strong principal-level signal.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **adjacency list (tree storage)**: Database representation where each row has a parent_id column. Simple to update but requires recursive queries for subtree operations.
- **nested sets**: Database representation where each node stores left/right visit numbers from a DFS. Enables fast subtree queries (WHERE left BETWEEN parent_left AND parent_right) but expensive to update.
- **materialized path**: Database representation where each node stores its full ancestor path (e.g., "/root/child1/grandchild2"). Enables fast ancestor queries with LIKE but path length is unbounded.
- **Euler tour**: Technique for flattening a tree into a sequence by recording entry and exit visits. Combined with a sparse table, enables O(1) LCA queries after O(n log n) preprocessing.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/10_recursion_trees/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/10_recursion_trees/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/10_recursion_trees/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/10_recursion_trees/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/10_recursion_trees/ --tb=short -q 2>&1 | tail -3
```
