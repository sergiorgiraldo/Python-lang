# Bill of Materials Explosion

## Overview

A Bill of Materials (BOM) defines the components needed to build a product. Components can themselves have sub-components, forming a tree. BOM explosion is the process of recursively expanding a product into all its leaf-level parts, multiplying quantities at each level to get the total count of each part needed.

This is the classic recursive CTE use case in manufacturing and supply chain systems.

## The Pattern

```sql
WITH RECURSIVE explosion AS (
    -- Base case: direct components
    SELECT component_id, quantity AS total_quantity, unit_cost
    FROM bom
    WHERE parent_id = :product

    UNION ALL

    -- Recursive case: sub-components with multiplied quantity
    SELECT b.component_id,
           e.total_quantity * b.quantity,
           b.unit_cost
    FROM bom b
    JOIN explosion e ON b.parent_id = e.component_id
)
SELECT component_id,
       total_quantity,
       total_quantity * unit_cost AS total_cost
FROM explosion
WHERE unit_cost IS NOT NULL;  -- leaf components
```

## Quantity Multiplication

The critical operation in BOM explosion is carrying `total_quantity = parent_quantity * component_quantity` through each recursion level.

Example: a Bicycle needs 2 Wheels. Each Wheel needs 32 Spokes. Total Spokes = 2 * 32 = 64.

```
Level 0: Bicycle
Level 1: Frame(1), Wheel(2), Chain(1)
Level 2: Steel Tube(1*3=3), Weld(1*6=6),
         Rim(2*1=2), Spoke(2*32=64), Tire(2*1=2)
```

## Cost Rollup

After explosion, total cost is the sum of (total_quantity * unit_cost) across all leaf components:

```sql
SELECT SUM(total_quantity * unit_cost) AS product_cost
FROM explosion
WHERE unit_cost IS NOT NULL;
```

For the Bicycle example:
- Chain: 1 * $15.00 = $15.00
- Steel Tube: 3 * $8.00 = $24.00
- Weld: 6 * $0.50 = $3.00
- Rim: 2 * $25.00 = $50.00
- Spoke: 64 * $0.75 = $48.00
- Tire: 2 * $20.00 = $40.00
- **Total: $180.00**

## Multi-Level Cost Aggregation

In more complex BOMs, intermediate assemblies also have assembly costs (labor, tooling). The total cost includes both component costs and assembly costs at each level:

```sql
-- Add assembly_cost column to bom
-- Total cost = SUM(leaf component costs) + SUM(assembly costs at each level)
```

This is common in manufacturing ERP systems where cost estimation drives pricing decisions.

## At Scale

BOM trees are typically shallow (5-10 levels) but can be wide (hundreds of components per assembly). The explosion output can be large: a product with 10 components, each with 10 sub-components, across 5 levels produces 10^5 = 100K rows.

Performance considerations:
- Recursion depth is bounded by tree depth (usually < 10 for manufactured goods)
- Output size grows exponentially with width and depth
- Quantity multiplication is arithmetic, so per-row cost is minimal
- The JOIN at each level is the main cost: index `bom(parent_id)` for fast lookups

For products with very complex BOMs (aircraft, vehicles with 100K+ unique parts), pre-materializing the explosion into a flat table is common. The flat table is rebuilt periodically (daily or on BOM changes) and queried without recursion.

## Shared Components

Real BOMs have shared components (the same bolt appears in multiple assemblies). The recursive CTE handles this naturally: the bolt appears in the explosion once per path, with the correct total_quantity for each path. Summing by component_id across all paths gives the true total:

```sql
SELECT component_id,
       SUM(total_quantity) AS grand_total_quantity
FROM explosion
WHERE unit_cost IS NOT NULL
GROUP BY component_id;
```

## Production Examples

- **Manufacturing:** "How many of each part do we need to build 1000 bicycles?" Multiply explosion quantities by the production order quantity.
- **Supply chain planning:** "Which suppliers do we depend on for this product?" Traverse the BOM to find all leaf components, then join to the supplier table.
- **Cost estimation:** "What happens to our product cost if steel prices increase 10%?" Re-run the cost rollup with adjusted unit_costs.
- **Software dependency trees:** "What transitive dependencies does this package have?" Package dependency graphs are BOMs where the product is the top-level package and components are dependencies.
- **Recipe costing in food service:** "What is the ingredient cost of this menu item?" Recipes are BOMs where components are ingredients.
