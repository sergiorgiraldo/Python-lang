"""Tests for LeetCode 177: Nth Highest Salary."""

from pathlib import Path

import duckdb

PROBLEM_DIR = Path(__file__).parent


def run_nth_salary(conn: duckdb.DuckDBPyConnection, n: int) -> int | None:
    """Run the Nth highest salary query with the given N."""
    sql_template = (PROBLEM_DIR / "177_nth_highest_salary.sql").read_text()
    sql = sql_template.replace("{n}", str(n))
    result = conn.execute(sql).fetchall()
    return result[0][0] if result else None


class TestNthHighestSalary:

    def test_second_highest(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'A', 100, 1), (2, 'B', 200, 1), (3, 'C', 300, 1)
        """)
        assert run_nth_salary(db_employee, 2) == 200

    def test_first_highest(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'A', 100, 1), (2, 'B', 200, 1)
        """)
        assert run_nth_salary(db_employee, 1) == 200

    def test_n_exceeds_distinct(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'A', 100, 1), (2, 'B', 200, 1)
        """)
        assert run_nth_salary(db_employee, 3) is None

    def test_with_ties(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'A', 300, 1), (2, 'B', 300, 1), (3, 'C', 200, 1)
        """)
        assert run_nth_salary(db_employee, 2) == 200

    def test_single_employee(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'A', 100, 1)
        """)
        assert run_nth_salary(db_employee, 1) == 100
        assert run_nth_salary(db_employee, 2) is None
