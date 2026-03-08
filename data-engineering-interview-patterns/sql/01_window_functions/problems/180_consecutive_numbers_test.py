"""Tests for LeetCode 180: Consecutive Numbers."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestConsecutiveNumbers:

    def test_example(self, db_logs) -> None:
        db_logs.execute("""
            INSERT INTO Logs (id, num) VALUES
                (1, 1), (2, 1), (3, 1), (4, 2),
                (5, 1), (6, 2), (7, 2);
        """)
        result = run_sql_file_df(db_logs, PROBLEM_DIR / "180_consecutive_numbers.sql")
        nums = {r["ConsecutiveNums"] for r in result}
        assert nums == {1}

    def test_no_consecutive(self, db_logs) -> None:
        db_logs.execute("""
            INSERT INTO Logs (id, num) VALUES
                (1, 1), (2, 2), (3, 1), (4, 2);
        """)
        result = run_sql_file_df(db_logs, PROBLEM_DIR / "180_consecutive_numbers.sql")
        assert len(result) == 0

    def test_multiple_consecutive(self, db_logs) -> None:
        db_logs.execute("""
            INSERT INTO Logs (id, num) VALUES
                (1, 1), (2, 1), (3, 1),
                (4, 2), (5, 2), (6, 2);
        """)
        result = run_sql_file_df(db_logs, PROBLEM_DIR / "180_consecutive_numbers.sql")
        nums = {r["ConsecutiveNums"] for r in result}
        assert nums == {1, 2}

    def test_longer_streak(self, db_logs) -> None:
        db_logs.execute("""
            INSERT INTO Logs (id, num) VALUES
                (1, 5), (2, 5), (3, 5), (4, 5), (5, 5);
        """)
        result = run_sql_file_df(db_logs, PROBLEM_DIR / "180_consecutive_numbers.sql")
        nums = {r["ConsecutiveNums"] for r in result}
        assert nums == {5}


class TestConsecutiveNumbersAlt:

    def test_example(self, db_logs) -> None:
        db_logs.execute("""
            INSERT INTO Logs (id, num) VALUES
                (1, 1), (2, 1), (3, 1), (4, 2),
                (5, 1), (6, 2), (7, 2);
        """)
        result = run_sql_file_df(
            db_logs, PROBLEM_DIR / "180_consecutive_numbers_alt.sql"
        )
        nums = {r["ConsecutiveNums"] for r in result}
        assert nums == {1}
