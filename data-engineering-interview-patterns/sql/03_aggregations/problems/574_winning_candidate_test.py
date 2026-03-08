"""Tests for LeetCode 574: Winning Candidate."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestWinningCandidate:

    def test_clear_winner(self, db_candidate) -> None:
        db_candidate.execute("""
            INSERT INTO Candidate (id, name) VALUES
                (1, 'A'), (2, 'B'), (3, 'C');
        """)
        db_candidate.execute("""
            INSERT INTO Vote (id, candidateId) VALUES
                (1, 2), (2, 4), (3, 3), (4, 2), (5, 2);
        """)
        result = run_sql_file_df(
            db_candidate, PROBLEM_DIR / "574_winning_candidate.sql"
        )
        assert len(result) == 1
        assert result[0]["name"] == "B"

    def test_tie_returns_one(self, db_candidate) -> None:
        db_candidate.execute("""
            INSERT INTO Candidate (id, name) VALUES
                (1, 'A'), (2, 'B');
        """)
        db_candidate.execute("""
            INSERT INTO Vote (id, candidateId) VALUES
                (1, 1), (2, 2);
        """)
        result = run_sql_file_df(
            db_candidate, PROBLEM_DIR / "574_winning_candidate.sql"
        )
        # With a tie, LIMIT 1 returns one of them (non-deterministic)
        assert len(result) == 1
        assert result[0]["name"] in {"A", "B"}

    def test_single_vote(self, db_candidate) -> None:
        db_candidate.execute("""
            INSERT INTO Candidate (id, name) VALUES
                (1, 'A'), (2, 'B');
        """)
        db_candidate.execute("""
            INSERT INTO Vote (id, candidateId) VALUES
                (1, 1);
        """)
        result = run_sql_file_df(
            db_candidate, PROBLEM_DIR / "574_winning_candidate.sql"
        )
        assert len(result) == 1
        assert result[0]["name"] == "A"

    def test_all_votes_one_candidate(self, db_candidate) -> None:
        db_candidate.execute("""
            INSERT INTO Candidate (id, name) VALUES
                (1, 'A'), (2, 'B'), (3, 'C');
        """)
        db_candidate.execute("""
            INSERT INTO Vote (id, candidateId) VALUES
                (1, 2), (2, 2), (3, 2), (4, 2);
        """)
        result = run_sql_file_df(
            db_candidate, PROBLEM_DIR / "574_winning_candidate.sql"
        )
        assert len(result) == 1
        assert result[0]["name"] == "B"
