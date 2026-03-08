"""Tests for LeetCode 550: Game Play Analysis IV."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestGamePlayIV:

    def test_example(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played)
            VALUES
                (1, 2, '2016-03-01', 5),
                (1, 2, '2016-03-02', 6),
                (2, 3, '2017-06-25', 1),
                (3, 1, '2016-03-02', 0),
                (3, 4, '2018-07-03', 5);
        """)
        result = run_sql_file_df(
            db_activity, PROBLEM_DIR / "550_game_play_analysis_iv.sql"
        )
        assert result[0]["fraction"] == 0.33

    def test_all_retained(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played)
            VALUES
                (1, 1, '2020-01-01', 1),
                (1, 1, '2020-01-02', 1),
                (2, 1, '2020-01-01', 1),
                (2, 1, '2020-01-02', 1);
        """)
        result = run_sql_file_df(
            db_activity, PROBLEM_DIR / "550_game_play_analysis_iv.sql"
        )
        assert result[0]["fraction"] == 1.0

    def test_none_retained(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played)
            VALUES
                (1, 1, '2020-01-01', 1),
                (1, 1, '2020-01-05', 1),
                (2, 1, '2020-01-01', 1);
        """)
        result = run_sql_file_df(
            db_activity, PROBLEM_DIR / "550_game_play_analysis_iv.sql"
        )
        assert result[0]["fraction"] == 0.0
