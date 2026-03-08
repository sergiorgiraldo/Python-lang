/*
Hierarchy Traversal with Recursive CTE

Org chart traversal: find all reports (direct and indirect) for a manager.
This is the most common recursive CTE pattern in production.
*/

-- Org chart: CEO -> VPs -> Directors -> Managers -> ICs
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

-- Recursive CTE: find all descendants of VP Engineering (id=2)
WITH RECURSIVE reports AS (
    -- Base case: direct reports of VP Engineering
    SELECT emp_id, name, manager_id, 1 AS depth
    FROM org_chart
    WHERE manager_id = 2

    UNION ALL

    -- Recursive case: reports of reports
    SELECT o.emp_id, o.name, o.manager_id, r.depth + 1
    FROM org_chart o
    JOIN reports r ON o.manager_id = r.emp_id
)
SELECT * FROM reports ORDER BY depth, name;
