"""Tests for LeetCode 176: Second Highest Salary."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestSecondHighestSalary:
    """Test the DENSE_RANK approach."""

    def test_basic(self, db_employee) -> None:
        """Standard case: two distinct salaries."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1),
                   (2, 'Bob', 200, 1),
                   (3, 'Carol', 300, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary.sql")
        assert result[0]["SecondHighestSalary"] == 200

    def test_single_employee(self, db_employee) -> None:
        """Only one employee: no second highest, return NULL."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary.sql")
        assert result[0]["SecondHighestSalary"] is None

    def test_duplicate_highest(self, db_employee) -> None:
        """Two employees with the same highest salary."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 300, 1),
                   (2, 'Bob', 300, 1),
                   (3, 'Carol', 200, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary.sql")
        assert result[0]["SecondHighestSalary"] == 200

    def test_all_same_salary(self, db_employee) -> None:
        """All employees have the same salary: no second highest."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1),
                   (2, 'Bob', 100, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary.sql")
        assert result[0]["SecondHighestSalary"] is None

    def test_negative_salaries(self, db_employee) -> None:
        """Negative values work correctly."""
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', -100, 1),
                   (2, 'Bob', -200, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary.sql")
        assert result[0]["SecondHighestSalary"] == -200


class TestSecondHighestSalaryAlt:
    """Test the OFFSET approach."""

    def test_basic(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1),
                   (2, 'Bob', 200, 1),
                   (3, 'Carol', 300, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary_alt.sql")
        assert result[0]["SecondHighestSalary"] == 200

    def test_single_employee(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary_alt.sql")
        assert result[0]["SecondHighestSalary"] is None

    def test_all_same(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId)
            VALUES (1, 'Alice', 100, 1),
                   (2, 'Bob', 100, 1)
        """)
        result = run_sql_file_df(db_employee, PROBLEM_DIR / "176_second_highest_salary_alt.sql")
        assert result[0]["SecondHighestSalary"] is None
