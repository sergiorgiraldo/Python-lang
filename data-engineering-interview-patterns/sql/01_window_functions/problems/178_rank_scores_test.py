"""Tests for LeetCode 178: Rank Scores."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestRankScores:

    def test_example(self, db) -> None:
        db.execute("""
            CREATE TABLE Scores (id INTEGER PRIMARY KEY, score DECIMAL(5,2));
            INSERT INTO Scores VALUES
                (1, 3.50), (2, 3.65), (3, 4.00),
                (4, 3.85), (5, 4.00), (6, 3.65);
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "178_rank_scores.sql")
        scores = [(float(r["score"]), r["rank"]) for r in result]
        assert scores == [
            (4.00, 1), (4.00, 1), (3.85, 2),
            (3.65, 3), (3.65, 3), (3.50, 4),
        ]

    def test_single_score(self, db) -> None:
        db.execute("""
            CREATE TABLE Scores (id INTEGER PRIMARY KEY, score DECIMAL(5,2));
            INSERT INTO Scores VALUES (1, 5.00);
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "178_rank_scores.sql")
        assert result[0]["rank"] == 1

    def test_all_same(self, db) -> None:
        db.execute("""
            CREATE TABLE Scores (id INTEGER PRIMARY KEY, score DECIMAL(5,2));
            INSERT INTO Scores VALUES (1, 3.00), (2, 3.00), (3, 3.00);
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "178_rank_scores.sql")
        assert all(r["rank"] == 1 for r in result)
