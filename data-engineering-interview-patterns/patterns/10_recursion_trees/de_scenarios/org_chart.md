# DE Scenario: Org Chart Traversal

## Real-World Context

Every company has an org chart stored as a flat table: `(employee_id, name, title, manager_id)`. Turning this flat table into a tree and answering questions like "who reports to Bob, directly or indirectly?" or "what's the management chain from CEO to this engineer?" requires recursive traversal.

In SQL, this is a recursive CTE. In Python, it's the same tree traversal patterns from problems 104-297. Understanding both helps you choose the right tool and debug when queries behave unexpectedly.

## Worked Example

Build the tree from a flat list using a hash map (two passes: create nodes, then link them). Then traverse it recursively for different queries. Each query type maps to a different traversal pattern.

```
Flat data:
  (1, Alice, CEO, NULL)
  (2, Bob, VP Eng, 1)
  (3, Charlie, VP Sales, 1)
  (4, Diana, Sr Eng, 2)
  (5, Eve, Engineer, 2)
  (6, Frank, Sales Lead, 3)
  (7, Grace, Jr Eng, 4)

Tree:
  Alice (CEO)
  +-- Bob (VP Eng)
  |   +-- Diana (Sr Eng)
  |   |   +-- Grace (Jr Eng)
  |   +-- Eve (Engineer)
  +-- Charlie (VP Sales)
      +-- Frank (Sales Lead)

Queries:
  Management chain to Grace:
    Alice -> Bob -> Diana -> Grace
    (DFS path finding, same as LCA path approach)

  All reports under Bob:
    [Diana, Grace, Eve]
    (DFS collecting all descendants)

  Headcount rollup:
    Alice: 6, Bob: 3, Charlie: 1, Diana: 1, Eve: 0, Frank: 0, Grace: 0
    (Post-order: compute children counts before parent)

SQL equivalent for "all reports under Bob":
  WITH RECURSIVE reports AS (
      SELECT id, name, manager_id FROM employees WHERE id = 2
      UNION ALL
      SELECT e.id, e.name, e.manager_id
      FROM employees e JOIN reports r ON e.manager_id = r.id
  )
  SELECT name FROM reports WHERE id != 2;
```
