"""Tests for LeetCode 615: Average Salary: Departments vs Company."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _setup_tables(db) -> None:
    """Create Salary table (Employee + Department already loaded by db_employee)."""
    db.execute("""
        CREATE TABLE Salary (
            id INTEGER,
            employee_id INTEGER,
            amount INTEGER,
            pay_date DATE
        );
    """)


class TestAverageSalary:

    def test_higher_than_company(self, db_employee) -> None:
        _setup_tables(db_employee)
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'Engineering'), (2, 'Sales');
        """)
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 0, 1), (2, 'B', 0, 1), (3, 'C', 0, 2);
        """)
        db_employee.execute("""
            INSERT INTO Salary (id, employee_id, amount, pay_date) VALUES
                (1, 1, 9000, '2017-03-31'),
                (2, 2, 6000, '2017-03-31'),
                (3, 3, 3000, '2017-03-31');
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "615_average_salary.sql"
        )
        lookup = {r["department_id"]: r["comparison"] for r in result}
        # Company avg = (9000+6000+3000)/3 = 6000
        # Dept 1 avg = (9000+6000)/2 = 7500 -> higher
        # Dept 2 avg = 3000 -> lower
        assert lookup[1] == "higher"
        assert lookup[2] == "lower"

    def test_lower_than_company(self, db_employee) -> None:
        _setup_tables(db_employee)
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'Engineering'), (2, 'Sales');
        """)
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 0, 1), (2, 'B', 0, 2);
        """)
        db_employee.execute("""
            INSERT INTO Salary (id, employee_id, amount, pay_date) VALUES
                (1, 1, 2000, '2017-03-31'),
                (2, 2, 8000, '2017-03-31');
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "615_average_salary.sql"
        )
        lookup = {r["department_id"]: r["comparison"] for r in result}
        # Company avg = (2000+8000)/2 = 5000
        # Dept 1 = 2000 -> lower
        # Dept 2 = 8000 -> higher
        assert lookup[1] == "lower"
        assert lookup[2] == "higher"

    def test_equal_to_company(self, db_employee) -> None:
        _setup_tables(db_employee)
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'Engineering'), (2, 'Sales');
        """)
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 0, 1), (2, 'B', 0, 2);
        """)
        db_employee.execute("""
            INSERT INTO Salary (id, employee_id, amount, pay_date) VALUES
                (1, 1, 5000, '2017-03-31'),
                (2, 2, 5000, '2017-03-31');
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "615_average_salary.sql"
        )
        for r in result:
            assert r["comparison"] == "same"

    def test_multiple_months(self, db_employee) -> None:
        _setup_tables(db_employee)
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'Engineering'), (2, 'Sales');
        """)
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 0, 1), (2, 'B', 0, 2);
        """)
        db_employee.execute("""
            INSERT INTO Salary (id, employee_id, amount, pay_date) VALUES
                (1, 1, 9000, '2017-01-31'),
                (2, 2, 3000, '2017-01-31'),
                (3, 1, 4000, '2017-02-28'),
                (4, 2, 8000, '2017-02-28');
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "615_average_salary.sql"
        )
        # January: company avg = 6000, dept1=9000 (higher), dept2=3000 (lower)
        # February: company avg = 6000, dept1=4000 (lower), dept2=8000 (higher)
        lookup = {(str(r["pay_month"])[:7], r["department_id"]): r["comparison"] for r in result}
        assert lookup[("2017-01", 1)] == "higher"
        assert lookup[("2017-01", 2)] == "lower"
        assert lookup[("2017-02", 1)] == "lower"
        assert lookup[("2017-02", 2)] == "higher"

    def test_single_department(self, db_employee) -> None:
        _setup_tables(db_employee)
        db_employee.execute("""
            INSERT INTO Department (id, name) VALUES (1, 'Engineering');
        """)
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId) VALUES
                (1, 'A', 0, 1), (2, 'B', 0, 1);
        """)
        db_employee.execute("""
            INSERT INTO Salary (id, employee_id, amount, pay_date) VALUES
                (1, 1, 5000, '2017-03-31'),
                (2, 2, 7000, '2017-03-31');
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "615_average_salary.sql"
        )
        # Single dept: dept avg = company avg = 6000
        assert len(result) == 1
        assert result[0]["comparison"] == "same"
