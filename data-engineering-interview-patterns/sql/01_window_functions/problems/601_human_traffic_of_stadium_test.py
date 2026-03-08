"""Tests for LeetCode 601: Human Traffic of Stadium."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestHumanTraffic:

    def test_example(self, db_stadium) -> None:
        db_stadium.execute("""
            INSERT INTO Stadium (id, visit_date, people) VALUES
                (1, '2017-01-01', 10),
                (2, '2017-01-02', 109),
                (3, '2017-01-03', 150),
                (4, '2017-01-04', 99),
                (5, '2017-01-05', 145),
                (6, '2017-01-06', 1455),
                (7, '2017-01-07', 199),
                (8, '2017-01-08', 188);
        """)
        result = run_sql_file_df(
            db_stadium, PROBLEM_DIR / "601_human_traffic_of_stadium.sql"
        )
        ids = [r["id"] for r in result]
        assert ids == [5, 6, 7, 8]

    def test_no_streak(self, db_stadium) -> None:
        db_stadium.execute("""
            INSERT INTO Stadium (id, visit_date, people) VALUES
                (1, '2017-01-01', 100),
                (2, '2017-01-02', 100),
                (3, '2017-01-03', 50),
                (4, '2017-01-04', 100);
        """)
        result = run_sql_file_df(
            db_stadium, PROBLEM_DIR / "601_human_traffic_of_stadium.sql"
        )
        assert len(result) == 0

    def test_exact_three(self, db_stadium) -> None:
        db_stadium.execute("""
            INSERT INTO Stadium (id, visit_date, people) VALUES
                (1, '2017-01-01', 200),
                (2, '2017-01-02', 200),
                (3, '2017-01-03', 200),
                (4, '2017-01-04', 50);
        """)
        result = run_sql_file_df(
            db_stadium, PROBLEM_DIR / "601_human_traffic_of_stadium.sql"
        )
        ids = [r["id"] for r in result]
        assert ids == [1, 2, 3]

    def test_multiple_streaks(self, db_stadium) -> None:
        db_stadium.execute("""
            INSERT INTO Stadium (id, visit_date, people) VALUES
                (1, '2017-01-01', 200), (2, '2017-01-02', 200),
                (3, '2017-01-03', 200), (4, '2017-01-04', 50),
                (5, '2017-01-05', 300), (6, '2017-01-06', 300),
                (7, '2017-01-07', 300);
        """)
        result = run_sql_file_df(
            db_stadium, PROBLEM_DIR / "601_human_traffic_of_stadium.sql"
        )
        ids = [r["id"] for r in result]
        assert ids == [1, 2, 3, 5, 6, 7]
