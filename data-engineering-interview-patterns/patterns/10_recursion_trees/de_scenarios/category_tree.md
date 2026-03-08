# DE Scenario: Category Tree Explosion

## Real-World Context

E-commerce category hierarchies are stored as flat tables (`id, name, parent_id`) but consumed as paths ("Electronics > Phones > Smartphones") for search indexing, breadcrumb navigation and dimension tables. "Exploding" the tree means generating every path from root to leaf.

## Worked Example

Build the tree from a flat list, then walk it recursively, accumulating the path string as you descend. Each node produces one record with its full path. Leaf nodes are flagged for filtering.

```
Flat data:
  (1, Electronics, NULL)
  (2, Phones, 1)
  (3, Laptops, 1)
  (4, Smartphones, 2)
  (5, Feature Phones, 2)
  (6, Gaming Laptops, 3)

Tree:
  Electronics
  +-- Phones
  |   +-- Smartphones
  |   +-- Feature Phones
  +-- Laptops
      +-- Gaming Laptops

Explosion (all paths):
  Electronics
  Electronics > Phones
  Electronics > Phones > Smartphones
  Electronics > Phones > Feature Phones
  Electronics > Laptops
  Electronics > Laptops > Gaming Laptops

Dimension table output:
  id=1  depth=1  Electronics                            (not leaf)
  id=2  depth=2  Electronics > Phones                   (not leaf)
  id=4  depth=3  Electronics > Phones > Smartphones     (leaf)
  id=5  depth=3  Electronics > Phones > Feature Phones  (leaf)
  id=3  depth=2  Electronics > Laptops                  (not leaf)
  id=6  depth=3  Electronics > Laptops > Gaming Laptops (leaf)

SQL equivalent:
  WITH RECURSIVE cat_path AS (
      SELECT id, name, name AS full_path, 1 AS depth
      FROM categories WHERE parent_id IS NULL
      UNION ALL
      SELECT c.id, c.name, cp.full_path || ' > ' || c.name, cp.depth + 1
      FROM categories c JOIN cat_path cp ON c.parent_id = cp.id
  )
  SELECT * FROM cat_path;
```
