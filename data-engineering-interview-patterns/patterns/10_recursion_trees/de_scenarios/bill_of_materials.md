# DE Scenario: Bill of Materials Explosion

## Real-World Context

Manufacturing, retail and software systems maintain bills of materials (BOMs): a product is made of components, which are made of sub-components, recursively. "Exploding" a BOM means flattening this tree into a list of all parts with their total quantities and costs.

The same pattern applies to recipe systems (ingredients of sub-recipes), software dependency trees (package A depends on B which depends on C) and cost allocation hierarchies.

## Worked Example

BOM explosion multiplies quantities down through the tree. A bicycle needs 2 wheels. Each wheel needs 32 spokes. Total spokes per bicycle: 2 x 32 = 64. The recursion carries the parent's quantity into each child, multiplying at each level.

```
Bicycle (qty: 1)
+-- Frame (qty: 1)              -> 1 x 1 = 1 frame
+-- Wheel Assembly (qty: 2)     -> 1 x 2 = 2 assemblies
|   +-- Tire (qty: 1)           -> 2 x 1 = 2 tires
|   +-- Spoke (qty: 32)         -> 2 x 32 = 64 spokes
|   +-- Hub (qty: 1)            -> 2 x 1 = 2 hubs
+-- Chain (qty: 1)              -> 1 x 1 = 1 chain
+-- Pedal (qty: 2)              -> 1 x 2 = 2 pedals

Cost rollup (post-order traversal):
  Spoke:  64 x $0.25 = $16.00
  Hub:    2 x $8.00  = $16.00
  Tire:   2 x $12.50 = $25.00
  Wheel:  2 x $5.00  = $10.00 (assembly cost)
  Wheel total:         $67.00 (assembly + sub-components)
  Frame:  1 x $85.00 = $85.00
  Chain:  1 x $15.00 = $15.00
  Pedal:  2 x $7.50  = $15.00
  Bicycle total:       $182.00

SQL equivalent:
  WITH RECURSIVE bom AS (
      SELECT child_id, quantity, quantity AS total_qty
      FROM relationships WHERE parent_id = 'BIKE'
      UNION ALL
      SELECT r.child_id, r.quantity, bom.total_qty * r.quantity
      FROM relationships r JOIN bom ON r.parent_id = bom.child_id
  )
  SELECT c.name, bom.total_qty, bom.total_qty * c.unit_cost AS total_cost
  FROM bom JOIN components c ON bom.child_id = c.id;
```

## Key Design Decisions

1. **Quantity multiplication is the core operation.** Each level multiplies the parent's effective quantity by the child's per-unit quantity. This is where mistakes happen.
2. **Assembly cost vs component cost.** A wheel assembly has its own cost ($5 for labor) plus the cost of its sub-components. The rollup must add both.
3. **Shared components.** A spoke might appear in both front and rear wheel assemblies. The explosion lists it twice (once per parent). Aggregation (GROUP BY component) gives the total across the entire product.
