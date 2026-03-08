/*
LATERAL JOIN: reference the left table in the right subquery.
Useful for "top N per group" and flattening nested data.

Supported in: DuckDB, Postgres, Snowflake (as LATERAL)
BigQuery alternative: UNNEST with CROSS JOIN
Spark alternative: explode()
*/

CREATE TABLE departments_lat (
    id INTEGER,
    name VARCHAR(50)
);

CREATE TABLE employees_lat (
    id INTEGER,
    name VARCHAR(50),
    department_id INTEGER,
    salary INTEGER
);

INSERT INTO departments_lat VALUES (1, 'Engineering'), (2, 'Sales'), (3, 'Marketing');
INSERT INTO employees_lat VALUES
    (1, 'Alice', 1, 120000), (2, 'Bob', 1, 110000), (3, 'Carol', 1, 105000),
    (4, 'Dave', 1, 100000), (5, 'Eve', 2, 95000), (6, 'Frank', 2, 90000),
    (7, 'Grace', 3, 85000);

-- Top 2 earners per department using LATERAL
SELECT d.name AS department, e.name AS employee, e.salary
FROM departments_lat d,
LATERAL (
    SELECT name, salary
    FROM employees_lat
    WHERE department_id = d.id
    ORDER BY salary DESC
    LIMIT 2
) e
ORDER BY d.name, e.salary DESC;
