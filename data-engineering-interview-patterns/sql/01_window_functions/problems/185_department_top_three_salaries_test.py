"""Tests for LeetCode 185: Department Top Three Salaries."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestDeptTopThree:

    def test_example(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT'), (2, 'Sales');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'Joe', 85000, 1), (2, 'Henry', 80000, 2),
                (3, 'Sam', 60000, 2), (4, 'Max', 90000, 1),
                (5, 'Janet', 69000, 1), (6, 'Randy', 85000, 1),
                (7, 'Will', 70000, 1);
        """)
        result = run_sql_file_df(
            db_employee,
            PROBLEM_DIR / "185_department_top_three_salaries.sql",
        )
        it_salaries = sorted(
            [r["Salary"] for r in result if r["Department"] == "IT"],
            reverse=True,
        )
        # Top 3 distinct: 90000, 85000, 70000
        # Joe=85000 (rank 2), Max=90000 (rank 1), Randy=85000 (rank 2), Will=70000 (rank 3)
        # Janet=69000 (rank 4) excluded
        assert 69000 not in it_salaries
        assert 90000 in it_salaries

    def test_fewer_than_three(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'Joe', 85000, 1), (2, 'Max', 90000, 1);
        """)
        result = run_sql_file_df(
            db_employee,
            PROBLEM_DIR / "185_department_top_three_salaries.sql",
        )
        assert len(result) == 2  # both are in top 3

    def test_ties_in_top_three(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 100, 1), (2, 'B', 100, 1),
                (3, 'C', 90, 1), (4, 'D', 80, 1), (5, 'E', 70, 1);
        """)
        result = run_sql_file_df(
            db_employee,
            PROBLEM_DIR / "185_department_top_three_salaries.sql",
        )
        salaries = {r["Salary"] for r in result}
        assert salaries == {100, 90, 80}  # top 3 distinct
        assert len(result) == 4  # A and B both at rank 1
