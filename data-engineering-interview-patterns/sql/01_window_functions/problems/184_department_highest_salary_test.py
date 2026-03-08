"""Tests for LeetCode 184: Department Highest Salary."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestDeptHighestSalary:

    def test_example(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT'), (2, 'Sales');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'Joe', 85000, 1), (2, 'Henry', 80000, 2),
                (3, 'Sam', 60000, 2), (4, 'Max', 90000, 1);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "184_department_highest_salary.sql"
        )
        result_set = {
            (r["Department"], r["Employee"], r["Salary"]) for r in result
        }
        assert result_set == {("IT", "Max", 90000), ("Sales", "Henry", 80000)}

    def test_tie(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'Joe', 90000, 1), (2, 'Max', 90000, 1);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "184_department_highest_salary.sql"
        )
        names = {r["Employee"] for r in result}
        assert names == {"Joe", "Max"}

    def test_single_dept_single_emp(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'IT');
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'Joe', 50000, 1);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "184_department_highest_salary.sql"
        )
        assert len(result) == 1
        assert result[0]["Employee"] == "Joe"
