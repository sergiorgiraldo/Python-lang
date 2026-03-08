/*
GROUPING SETS, ROLLUP, and CUBE

Multi-level aggregation in a single query. Instead of running
separate GROUP BY queries for different levels and UNION ALL'ing,
GROUPING SETS computes all levels in one pass.
*/

CREATE TABLE sales (
    region VARCHAR(20),
    product VARCHAR(20),
    quarter VARCHAR(10),
    revenue INTEGER
);

INSERT INTO sales VALUES
    ('East', 'Widget', 'Q1', 100), ('East', 'Widget', 'Q2', 150),
    ('East', 'Gadget', 'Q1', 200), ('East', 'Gadget', 'Q2', 250),
    ('West', 'Widget', 'Q1', 120), ('West', 'Widget', 'Q2', 180),
    ('West', 'Gadget', 'Q1', 220), ('West', 'Gadget', 'Q2', 280);

-- GROUPING SETS: explicitly define which groupings you want
SELECT
    region,
    product,
    SUM(revenue) AS total,
    GROUPING(region) AS is_region_total,
    GROUPING(product) AS is_product_total
FROM sales
GROUP BY GROUPING SETS (
    (region, product),   -- revenue per region + product
    (region),            -- revenue per region (subtotal)
    ()                   -- grand total
)
ORDER BY region NULLS LAST, product NULLS LAST;
