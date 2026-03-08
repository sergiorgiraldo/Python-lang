"""Tests for LeetCode 579: Find Cumulative Salary of an Employee."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _setup_table(db):
    """Create Employee_Monthly table with inline data."""
    db.execute("""
        CREATE TABLE Employee_Monthly (
            id INTEGER,
            month INTEGER,
            salary INTEGER
        )
    """)
    return db


class TestCumulativeSalary:
    """Test rolling 3-month sum with most-recent exclusion."""

    def test_leetcode_example(self, db) -> None:
        """Multiple employees across months."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Monthly VALUES
                (1, 1, 20),
                (1, 2, 30),
                (1, 3, 40),
                (1, 4, 60),
                (1, 7, 90),
                (2, 1, 20),
                (2, 2, 30),
                (3, 2, 40),
                (3, 3, 60),
                (3, 4, 70)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "579_cumulative_salary.sql")
        # Build a lookup: (id, month) -> Salary
        lookup = {(r["id"], r["month"]): r["Salary"] for r in result}

        # Employee 1: most recent is month 7, excluded
        # month 4: sum(40+30+20)=90... wait, ROWS BETWEEN 2 PRECEDING
        # Rows for emp 1 sorted by month: 1(20), 2(30), 3(40), 4(60), 7(90)
        # month 1: only self = 20
        # month 2: 20+30 = 50
        # month 3: 20+30+40 = 90
        # month 4: 30+40+60 = 130
        # month 7: 40+60+90 = 190 (excluded as most recent)
        assert lookup[(1, 4)] == 130
        assert lookup[(1, 3)] == 90
        assert lookup[(1, 2)] == 50
        assert lookup[(1, 1)] == 20
        assert (1, 7) not in lookup

        # Employee 2: most recent is month 2, excluded
        # month 1: 20
        assert lookup[(2, 1)] == 20
        assert (2, 2) not in lookup

        # Employee 3: most recent is month 4, excluded
        # month 2: 40
        # month 3: 40+60 = 100
        assert lookup[(3, 3)] == 100
        assert lookup[(3, 2)] == 40
        assert (3, 4) not in lookup

    def test_single_month_excluded(self, db) -> None:
        """Employee with only 1 month is fully excluded."""
        _setup_table(db)
        db.execute("INSERT INTO Employee_Monthly VALUES (1, 5, 100)")
        result = run_sql_file_df(db, PROBLEM_DIR / "579_cumulative_salary.sql")
        assert len(result) == 0

    def test_two_months(self, db) -> None:
        """Employee with 2 months: most recent excluded, first has only its own salary."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Monthly VALUES
                (1, 3, 50),
                (1, 4, 70)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "579_cumulative_salary.sql")
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["month"] == 3
        assert result[0]["Salary"] == 50

    def test_exactly_three_months(self, db) -> None:
        """Three months: third excluded, first two show partial windows."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Monthly VALUES
                (1, 1, 10),
                (1, 2, 20),
                (1, 3, 30)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "579_cumulative_salary.sql")
        lookup = {r["month"]: r["Salary"] for r in result}
        # month 3 excluded (most recent)
        # month 1: 10
        # month 2: 10+20 = 30
        assert lookup[1] == 10
        assert lookup[2] == 30
        assert 3 not in lookup

    def test_gaps_in_months(self, db) -> None:
        """ROWS frame counts physical rows, not month values."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Employee_Monthly VALUES
                (1, 1, 10),
                (1, 5, 50),
                (1, 9, 90),
                (1, 12, 120)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "579_cumulative_salary.sql")
        lookup = {r["month"]: r["Salary"] for r in result}
        # month 12 excluded (most recent)
        # Physical rows sorted by month: 1(10), 5(50), 9(90), 12(120)
        # month 1: 10
        # month 5: 10+50 = 60
        # month 9: 10+50+90 = 150
        assert lookup[1] == 10
        assert lookup[5] == 60
        assert lookup[9] == 150
        assert 12 not in lookup
