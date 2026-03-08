"""Tests for LeetCode 571: Find Median Given Frequency of Numbers."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _setup_table(db):
    """Create Numbers table with inline data."""
    db.execute("CREATE TABLE Numbers (num INTEGER, frequency INTEGER)")
    return db


class TestMedianGivenFrequency:
    """Test cumulative frequency median approach."""

    def test_leetcode_example(self, db) -> None:
        """LeetCode example: (0,7),(1,1),(2,3),(3,1) -> median = 0.0."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Numbers VALUES
                (0, 7),
                (1, 1),
                (2, 3),
                (3, 1)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "571_median_given_frequency.sql")
        assert result[0]["median"] == 0.0

    def test_single_number(self, db) -> None:
        """Single number with frequency 1."""
        _setup_table(db)
        db.execute("INSERT INTO Numbers VALUES (5, 1)")
        result = run_sql_file_df(db, PROBLEM_DIR / "571_median_given_frequency.sql")
        assert result[0]["median"] == 5.0

    def test_two_numbers_even_total(self, db) -> None:
        """Two numbers with equal frequency: average of middle values."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Numbers VALUES
                (1, 1),
                (3, 1)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "571_median_given_frequency.sql")
        # Total frequency = 2, median = avg(1, 3) = 2.0
        assert result[0]["median"] == 2.0

    def test_all_same_number(self, db) -> None:
        """All same number regardless of frequency."""
        _setup_table(db)
        db.execute("INSERT INTO Numbers VALUES (42, 100)")
        result = run_sql_file_df(db, PROBLEM_DIR / "571_median_given_frequency.sql")
        assert result[0]["median"] == 42.0

    def test_odd_total_frequency(self, db) -> None:
        """Odd total frequency: exact middle value."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Numbers VALUES
                (1, 2),
                (2, 1),
                (3, 2)
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "571_median_given_frequency.sql")
        # Expanded: [1,1,2,3,3], total=5, median position=3 -> value=2
        assert result[0]["median"] == 2.0
