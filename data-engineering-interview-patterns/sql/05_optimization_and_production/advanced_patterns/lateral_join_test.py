"""Tests for LATERAL JOIN pattern."""

import duckdb
import pytest


@pytest.fixture
def db_lateral(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with departments and employees tables for LATERAL join tests."""
    db.execute("""
        CREATE TABLE departments_lat (
            id INTEGER, name VARCHAR(50)
        )
    """)
    db.execute("""
        CREATE TABLE employees_lat (
            id INTEGER, name VARCHAR(50),
            department_id INTEGER, salary INTEGER
        )
    """)
    db.execute("""
        INSERT INTO departments_lat VALUES
            (1, 'Engineering'), (2, 'Sales'), (3, 'Marketing')
    """)
    db.execute("""
        INSERT INTO employees_lat VALUES
            (1, 'Alice', 1, 120000), (2, 'Bob', 1, 110000),
            (3, 'Carol', 1, 105000), (4, 'Dave', 1, 100000),
            (5, 'Eve', 2, 95000), (6, 'Frank', 2, 90000),
            (7, 'Grace', 3, 85000)
    """)
    return db


class TestLateralJoin:
    """Test LATERAL JOIN for top-N per group."""

    def test_top_2_per_department(
        self, db_lateral: duckdb.DuckDBPyConnection
    ) -> None:
        """Each department returns at most 2 employees, highest paid."""
        result = db_lateral.execute("""
            SELECT d.name AS department, e.name AS employee, e.salary
            FROM departments_lat d,
            LATERAL (
                SELECT name, salary
                FROM employees_lat
                WHERE department_id = d.id
                ORDER BY salary DESC
                LIMIT 2
            ) e
            ORDER BY d.name, e.salary DESC
        """).fetchall()
        # Engineering: Alice(120k), Bob(110k)
        # Marketing: Grace(85k)
        # Sales: Eve(95k), Frank(90k)
        assert len(result) == 5
        eng = [r for r in result if r[0] == "Engineering"]
        assert len(eng) == 2
        assert eng[0] == ("Engineering", "Alice", 120000)
        assert eng[1] == ("Engineering", "Bob", 110000)

        sales = [r for r in result if r[0] == "Sales"]
        assert len(sales) == 2
        assert sales[0] == ("Sales", "Eve", 95000)

        marketing = [r for r in result if r[0] == "Marketing"]
        assert len(marketing) == 1
        assert marketing[0] == ("Marketing", "Grace", 85000)

    def test_lateral_excludes_empty_groups(
        self, db_lateral: duckdb.DuckDBPyConnection
    ) -> None:
        """Departments with no employees are excluded (CROSS JOIN semantics)."""
        db_lateral.execute("""
            INSERT INTO departments_lat VALUES (4, 'Legal')
        """)
        result = db_lateral.execute("""
            SELECT d.name AS department, e.name AS employee
            FROM departments_lat d,
            LATERAL (
                SELECT name
                FROM employees_lat
                WHERE department_id = d.id
                LIMIT 2
            ) e
        """).fetchall()
        departments = {r[0] for r in result}
        assert "Legal" not in departments

    def test_left_join_lateral_preserves_empty(
        self, db_lateral: duckdb.DuckDBPyConnection
    ) -> None:
        """LEFT JOIN LATERAL preserves rows with no matches."""
        db_lateral.execute("""
            INSERT INTO departments_lat VALUES (4, 'Legal')
        """)
        result = db_lateral.execute("""
            SELECT d.name AS department, e.name AS employee
            FROM departments_lat d
            LEFT JOIN LATERAL (
                SELECT name
                FROM employees_lat
                WHERE department_id = d.id
                LIMIT 2
            ) e ON true
            ORDER BY d.name
        """).fetchall()
        departments = {r[0] for r in result}
        assert "Legal" in departments
        legal_row = [r for r in result if r[0] == "Legal"]
        assert legal_row[0][1] is None  # no employee

    def test_lateral_matches_window_function(
        self, db_lateral: duckdb.DuckDBPyConnection
    ) -> None:
        """LATERAL top-2 matches window function approach."""
        lateral_result = db_lateral.execute("""
            SELECT d.name AS department, e.name AS employee, e.salary
            FROM departments_lat d,
            LATERAL (
                SELECT name, salary
                FROM employees_lat
                WHERE department_id = d.id
                ORDER BY salary DESC
                LIMIT 2
            ) e
            ORDER BY department, salary DESC
        """).fetchall()
        window_result = db_lateral.execute("""
            SELECT department, employee, salary FROM (
                SELECT d.name AS department, el.name AS employee, el.salary,
                       ROW_NUMBER() OVER (
                           PARTITION BY d.id ORDER BY el.salary DESC
                       ) AS rn
                FROM departments_lat d
                JOIN employees_lat el ON d.id = el.department_id
            ) t WHERE rn <= 2
            ORDER BY department, salary DESC
        """).fetchall()
        assert lateral_result == window_result
