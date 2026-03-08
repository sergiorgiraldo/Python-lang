/*
Bill of Materials Explosion with Recursive CTE

Expand a product into all its components (and sub-components).
Multiply quantities across levels to get total parts needed.
Roll up costs to compute total product cost.
*/

CREATE TABLE bom (
    parent_id VARCHAR(20),
    component_id VARCHAR(20),
    quantity INTEGER,
    unit_cost DECIMAL(10,2)
);

-- Bicycle -> Frame, Wheels(2), Chain
-- Frame -> Steel Tube(3), Welds(6)
-- Wheels -> Rim, Spokes(32), Tire
INSERT INTO bom VALUES
    ('Bicycle',  'Frame',      1,  NULL),
    ('Bicycle',  'Wheel',      2,  NULL),
    ('Bicycle',  'Chain',      1,  15.00),
    ('Frame',    'Steel Tube', 3,   8.00),
    ('Frame',    'Weld',       6,   0.50),
    ('Wheel',    'Rim',        1,  25.00),
    ('Wheel',    'Spoke',     32,   0.75),
    ('Wheel',    'Tire',       1,  20.00);

-- BOM explosion: expand Bicycle into all leaf components with total quantities
WITH RECURSIVE explosion AS (
    -- Base case: direct components of Bicycle
    SELECT parent_id,
           component_id,
           quantity AS total_quantity,
           unit_cost,
           1 AS depth
    FROM bom
    WHERE parent_id = 'Bicycle'

    UNION ALL

    -- Recursive case: sub-components, multiplying quantities
    SELECT b.parent_id,
           b.component_id,
           e.total_quantity * b.quantity AS total_quantity,
           b.unit_cost,
           e.depth + 1
    FROM bom b
    JOIN explosion e ON b.parent_id = e.component_id
)
SELECT component_id,
       total_quantity,
       unit_cost,
       total_quantity * unit_cost AS total_cost,
       depth
FROM explosion
WHERE unit_cost IS NOT NULL  -- leaf components only
ORDER BY depth, component_id;

-- Total cost of a Bicycle
-- SELECT SUM(total_quantity * unit_cost) AS bicycle_total_cost
-- FROM explosion
-- WHERE unit_cost IS NOT NULL;
