/*
Self-Joins for Hierarchies

Multi-level self-join for org chart traversal.
Employee -> Manager -> Director (two levels up).

Limitations: fixed depth. For arbitrary depth, use recursive CTEs.
*/

-- Setup: org chart
CREATE TABLE org_chart (
    emp_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    title VARCHAR(100),
    manager_id INTEGER
);

INSERT INTO org_chart VALUES
    (1, 'Alice', 'CEO', NULL),
    (2, 'Bob', 'VP Engineering', 1),
    (3, 'Carol', 'VP Sales', 1),
    (4, 'Dave', 'Engineering Manager', 2),
    (5, 'Eve', 'Sales Manager', 3),
    (6, 'Frank', 'Senior Engineer', 4),
    (7, 'Grace', 'Engineer', 4),
    (8, 'Hank', 'Sales Rep', 5),
    (9, 'Ivy', 'Junior Engineer', 6);


-- Two-level rollup: employee -> manager -> director
SELECT e.name AS employee,
       e.title AS employee_title,
       m.name AS manager,
       m.title AS manager_title,
       d.name AS director,
       d.title AS director_title
FROM org_chart e
LEFT JOIN org_chart m ON e.manager_id = m.emp_id
LEFT JOIN org_chart d ON m.manager_id = d.emp_id
ORDER BY e.emp_id;
