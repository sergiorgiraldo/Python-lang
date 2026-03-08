/*
Path Enumeration with Recursive CTE

Build the full path from root to each node in a hierarchy.
Example: "CEO / VP Engineering / Director Backend"

Uses the same org_chart table as hierarchy_traversal.sql.
*/

CREATE TABLE org_chart (
    emp_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    manager_id INTEGER
);

INSERT INTO org_chart VALUES
    (1, 'CEO', NULL),
    (2, 'VP Engineering', 1),
    (3, 'VP Sales', 1),
    (4, 'Director Backend', 2),
    (5, 'Director Frontend', 2),
    (6, 'Manager API', 4),
    (7, 'Senior IC', 6),
    (8, 'Junior IC', 6),
    (9, 'Sales Lead', 3);

-- Build full path from root to each node
WITH RECURSIVE paths AS (
    -- Base case: root nodes (no manager)
    SELECT emp_id, name, manager_id,
           name AS full_path,
           1 AS depth
    FROM org_chart
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: append child name to parent path
    SELECT o.emp_id, o.name, o.manager_id,
           p.full_path || ' / ' || o.name AS full_path,
           p.depth + 1
    FROM org_chart o
    JOIN paths p ON o.manager_id = p.emp_id
)
SELECT emp_id, name, full_path, depth
FROM paths
ORDER BY full_path;

-- Subtree query: find everyone under VP Engineering using path prefix
-- WITH RECURSIVE paths AS ( ... same as above ... )
-- SELECT * FROM paths WHERE full_path LIKE 'CEO / VP Engineering%';
