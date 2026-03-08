"""Tests for LeetCode 569: Median Employee Salary."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _setup_table(db):
    """Create Employee_Company table with inline data."""
    db.execute("""
        CREATE TABLE Employee_Company (
            id INTEGER PRIMARY KEY,
            company VARCHAR(10),
            salary INTEGER
        )
    """)
    return db


class TestMedianEmployeeSalary:
    """Test ROW_NUMBER + COUNT median approach."""

    def test_odd_count_single_median(self, db) -> None:
        """Odd number of employees per company returns one median."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Company VALUES
                (1, 'A', 2341),
                (2, 'A', 341),
                (3, 'A', 15)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "569_median_employee_salary.sql")
        assert len(result) == 1
        assert result[0]["salary"] == 341

    def test_even_count_two_medians(self, db) -> None:
        """Even number of employees returns both middle values."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Company VALUES
                (1, 'A', 100),
                (2, 'A', 200),
                (3, 'A', 300),
                (4, 'A', 400)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "569_median_employee_salary.sql")
        salaries = [r["salary"] for r in result]
        assert salaries == [200, 300]

    def test_single_employee_per_company(self, db) -> None:
        """Single employee is the median."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Company VALUES
                (1, 'A', 500),
                (2, 'B', 700)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "569_median_employee_salary.sql")
        result_by_company = {r["company"]: r["salary"] for r in result}
        assert result_by_company == {"A": 500, "B": 700}

    def test_multiple_companies_different_counts(self, db) -> None:
        """Multiple companies with odd and even counts."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Company VALUES
                (1, 'A', 2341),
                (2, 'A', 341),
                (3, 'A', 15),
                (4, 'A', 15314),
                (5, 'A', 451),
                (6, 'A', 513),
                (7, 'B', 15),
                (8, 'B', 13),
                (9, 'B', 1154),
                (10, 'B', 1345),
                (11, 'B', 1221),
                (12, 'B', 234)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "569_median_employee_salary.sql")
        a_salaries = sorted(r["salary"] for r in result if r["company"] == "A")
        b_salaries = sorted(r["salary"] for r in result if r["company"] == "B")
        # A has 6 employees: sorted = [15, 341, 451, 513, 2341, 15314]
        # Median positions: 3 and 4 -> 451, 513
        assert a_salaries == [451, 513]
        # B has 6 employees: sorted = [13, 15, 234, 1154, 1221, 1345]
        # Median positions: 3 and 4 -> 234, 1154
        assert b_salaries == [234, 1154]

    def test_tied_salary_values(self, db) -> None:
        """Ties in salary are handled by id tiebreaker."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Company VALUES
                (1, 'A', 100),
                (2, 'A', 100),
                (3, 'A', 100),
                (4, 'A', 200),
                (5, 'A', 200)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "569_median_employee_salary.sql")
        # 5 employees, median position = 3
        # Sorted by (salary, id): (100,1),(100,2),(100,3),(200,4),(200,5)
        # Position 3 -> salary 100
        assert len(result) == 1
        assert result[0]["salary"] == 100
