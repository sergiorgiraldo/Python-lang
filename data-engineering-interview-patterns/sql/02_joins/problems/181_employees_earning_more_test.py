"""Tests for LeetCode 181: Employees Earning More Than Their Managers."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestEmployeesEarningMore:

    def test_basic(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Joe', 70000, 1, 3),
                (2, 'Henry', 80000, 1, 4),
                (3, 'Sam', 60000, 1, NULL),
                (4, 'Max', 90000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "181_employees_earning_more.sql"
        )
        names = {r["Employee"] for r in result}
        assert names == {"Joe"}

    def test_no_one_earns_more(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Joe', 50000, 1, 2),
                (2, 'Sam', 90000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "181_employees_earning_more.sql"
        )
        assert len(result) == 0

    def test_multiple_earn_more(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Joe', 80000, 1, 3),
                (2, 'Henry', 90000, 1, 3),
                (3, 'Sam', 60000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "181_employees_earning_more.sql"
        )
        names = {r["Employee"] for r in result}
        assert names == {"Joe", "Henry"}

    def test_null_manager_excluded(self, db_employee) -> None:
        """Employees with no manager should not appear."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Joe', 100000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "181_employees_earning_more.sql"
        )
        assert len(result) == 0

    def test_equal_salary_excluded(self, db_employee) -> None:
        """Equal salary should not appear (strictly greater)."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Joe', 70000, 1, 2),
                (2, 'Sam', 70000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "181_employees_earning_more.sql"
        )
        assert len(result) == 0
