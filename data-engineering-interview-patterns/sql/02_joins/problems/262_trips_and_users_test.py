"""Tests for LeetCode 262: Trips and Users."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestTripsAndUsers:

    def test_leetcode_example(self, db_trips) -> None:
        db_trips.execute("""
            INSERT INTO Users (users_id, banned, role) VALUES
                (1, 'No', 'client'), (2, 'Yes', 'client'),
                (3, 'No', 'client'), (4, 'No', 'client'),
                (10, 'No', 'driver'), (11, 'No', 'driver'),
                (12, 'No', 'driver'), (13, 'No', 'driver');
            INSERT INTO Trips (id, client_id, driver_id, city_id, status, request_at) VALUES
                (1, 1, 10, 1, 'completed', '2013-10-01'),
                (2, 2, 11, 1, 'cancelled_by_driver', '2013-10-01'),
                (3, 3, 12, 6, 'completed', '2013-10-01'),
                (4, 4, 13, 6, 'cancelled_by_client', '2013-10-01'),
                (5, 1, 10, 1, 'completed', '2013-10-02'),
                (6, 2, 11, 6, 'completed', '2013-10-02'),
                (7, 3, 12, 6, 'completed', '2013-10-02'),
                (8, 2, 12, 12, 'completed', '2013-10-03'),
                (9, 3, 10, 12, 'completed', '2013-10-03'),
                (10, 4, 13, 12, 'cancelled_by_driver', '2013-10-03');
        """)
        result = run_sql_file_df(
            db_trips, PROBLEM_DIR / "262_trips_and_users.sql"
        )
        by_day = {str(r["Day"]): r["Cancellation Rate"] for r in result}
        # Day 1: trip 2 excluded (banned client), trips 1,3,4 remain, 1 cancelled / 3 = 0.33
        assert by_day["2013-10-01"] == 0.33
        # Day 2: trip 6 excluded (banned client), trips 5,7 remain, 0 cancelled / 2 = 0.00
        assert by_day["2013-10-02"] == 0.0
        # Day 3: trip 8 excluded (banned client), trips 9,10 remain, 1 cancelled / 2 = 0.50
        assert by_day["2013-10-03"] == 0.5

    def test_no_cancellations(self, db_trips) -> None:
        db_trips.execute("""
            INSERT INTO Users (users_id, banned, role) VALUES
                (1, 'No', 'client'), (10, 'No', 'driver');
            INSERT INTO Trips (id, client_id, driver_id, city_id, status, request_at) VALUES
                (1, 1, 10, 1, 'completed', '2013-10-01'),
                (2, 1, 10, 1, 'completed', '2013-10-01');
        """)
        result = run_sql_file_df(
            db_trips, PROBLEM_DIR / "262_trips_and_users.sql"
        )
        assert len(result) == 1
        assert result[0]["Cancellation Rate"] == 0.0

    def test_all_cancelled(self, db_trips) -> None:
        db_trips.execute("""
            INSERT INTO Users (users_id, banned, role) VALUES
                (1, 'No', 'client'), (10, 'No', 'driver');
            INSERT INTO Trips (id, client_id, driver_id, city_id, status, request_at) VALUES
                (1, 1, 10, 1, 'cancelled_by_client', '2013-10-01'),
                (2, 1, 10, 1, 'cancelled_by_driver', '2013-10-01');
        """)
        result = run_sql_file_df(
            db_trips, PROBLEM_DIR / "262_trips_and_users.sql"
        )
        assert len(result) == 1
        assert result[0]["Cancellation Rate"] == 1.0

    def test_banned_users_excluded(self, db_trips) -> None:
        """Trips involving banned clients or drivers are excluded."""
        db_trips.execute("""
            INSERT INTO Users (users_id, banned, role) VALUES
                (1, 'No', 'client'), (2, 'Yes', 'client'),
                (10, 'No', 'driver'), (11, 'Yes', 'driver');
            INSERT INTO Trips (id, client_id, driver_id, city_id, status, request_at) VALUES
                (1, 1, 10, 1, 'completed', '2013-10-01'),
                (2, 2, 10, 1, 'cancelled_by_client', '2013-10-01'),
                (3, 1, 11, 1, 'cancelled_by_driver', '2013-10-01');
        """)
        result = run_sql_file_df(
            db_trips, PROBLEM_DIR / "262_trips_and_users.sql"
        )
        # Only trip 1 remains (unbanned client AND driver)
        assert len(result) == 1
        assert result[0]["Cancellation Rate"] == 0.0
