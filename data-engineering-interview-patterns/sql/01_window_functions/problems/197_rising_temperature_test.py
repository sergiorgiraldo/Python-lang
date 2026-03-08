"""Tests for LeetCode 197: Rising Temperature."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestRisingTemperature:

    def test_example(self, db_weather) -> None:
        db_weather.execute("""
            INSERT INTO Weather (id, recordDate, temperature) VALUES
                (1, '2015-01-01', 10),
                (2, '2015-01-02', 25),
                (3, '2015-01-03', 20),
                (4, '2015-01-04', 30);
        """)
        result = run_sql_file_df(
            db_weather, PROBLEM_DIR / "197_rising_temperature.sql"
        )
        ids = {r["id"] for r in result}
        assert ids == {2, 4}

    def test_no_rise(self, db_weather) -> None:
        db_weather.execute("""
            INSERT INTO Weather (id, recordDate, temperature) VALUES
                (1, '2015-01-01', 30),
                (2, '2015-01-02', 20),
                (3, '2015-01-03', 10);
        """)
        result = run_sql_file_df(
            db_weather, PROBLEM_DIR / "197_rising_temperature.sql"
        )
        assert len(result) == 0

    def test_gap_in_dates(self, db_weather) -> None:
        """Non-consecutive dates: should not compare across gaps."""
        db_weather.execute("""
            INSERT INTO Weather (id, recordDate, temperature) VALUES
                (1, '2015-01-01', 10),
                (2, '2015-01-03', 25);
        """)
        result = run_sql_file_df(
            db_weather, PROBLEM_DIR / "197_rising_temperature.sql"
        )
        assert len(result) == 0  # dates aren't consecutive

    def test_single_record(self, db_weather) -> None:
        db_weather.execute("""
            INSERT INTO Weather (id, recordDate, temperature) VALUES
                (1, '2015-01-01', 10);
        """)
        result = run_sql_file_df(
            db_weather, PROBLEM_DIR / "197_rising_temperature.sql"
        )
        assert len(result) == 0


class TestRisingTemperatureAlt:

    def test_example(self, db_weather) -> None:
        db_weather.execute("""
            INSERT INTO Weather (id, recordDate, temperature) VALUES
                (1, '2015-01-01', 10),
                (2, '2015-01-02', 25),
                (3, '2015-01-03', 20),
                (4, '2015-01-04', 30);
        """)
        result = run_sql_file_df(
            db_weather, PROBLEM_DIR / "197_rising_temperature_alt.sql"
        )
        ids = {r["id"] for r in result}
        assert ids == {2, 4}
