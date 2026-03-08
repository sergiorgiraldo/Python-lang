"""Tests for LeetCode 511: Game Play Analysis I."""

import datetime
from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestGamePlayAnalysisI:

    def test_basic_multiple_players(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played) VALUES
                (1, 2, '2016-03-01', 5),
                (1, 2, '2016-05-02', 6),
                (2, 3, '2017-06-25', 1),
                (2, 3, '2017-06-23', 3),
                (3, 1, '2016-03-02', 0),
                (3, 4, '2018-07-03', 5);
        """)
        result = run_sql_file_df(db_activity, PROBLEM_DIR / "511_game_play_analysis_i.sql")
        lookup = {r["player_id"]: r["first_login"] for r in result}
        assert lookup[1] == datetime.date(2016, 3, 1)
        assert lookup[2] == datetime.date(2017, 6, 23)
        assert lookup[3] == datetime.date(2016, 3, 2)

    def test_single_login(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played) VALUES
                (1, 2, '2020-01-15', 3);
        """)
        result = run_sql_file_df(db_activity, PROBLEM_DIR / "511_game_play_analysis_i.sql")
        assert len(result) == 1
        assert result[0]["first_login"] == datetime.date(2020, 1, 15)

    def test_same_first_login_date(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played) VALUES
                (1, 2, '2020-01-01', 5),
                (1, 2, '2020-06-01', 2),
                (2, 3, '2020-01-01', 3),
                (2, 3, '2020-07-01', 4);
        """)
        result = run_sql_file_df(db_activity, PROBLEM_DIR / "511_game_play_analysis_i.sql")
        lookup = {r["player_id"]: r["first_login"] for r in result}
        assert lookup[1] == datetime.date(2020, 1, 1)
        assert lookup[2] == datetime.date(2020, 1, 1)

    def test_ordering_does_not_affect_result(self, db_activity) -> None:
        db_activity.execute("""
            INSERT INTO Activity (player_id, device_id, event_date, games_played) VALUES
                (1, 2, '2020-12-31', 1),
                (1, 2, '2020-01-01', 2),
                (1, 2, '2020-06-15', 3);
        """)
        result = run_sql_file_df(db_activity, PROBLEM_DIR / "511_game_play_analysis_i.sql")
        assert result[0]["first_login"] == datetime.date(2020, 1, 1)
