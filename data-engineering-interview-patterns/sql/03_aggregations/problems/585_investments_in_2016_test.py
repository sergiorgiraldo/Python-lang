"""Tests for LeetCode 585: Investments in 2016."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestInvestmentsIn2016:

    def test_leetcode_example(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 20, 20, 20, 20),
                (3, 10, 30, 20, 20),
                (4, 10, 40, 40, 40);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016.sql"
        )
        # pid 1 and 4: tiv_2015=10 (shared), unique locations
        # pid 3: tiv_2015=10 (shared), but location (20,20) is shared with pid 2
        # Sum = 5 + 40 = 45.0
        assert result[0]["tiv_2016"] == 45.0

    def test_no_one_meets_both_criteria(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 20, 20, 20, 20),
                (3, 30, 30, 30, 30);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016.sql"
        )
        # No shared tiv_2015 values, so first condition fails for all
        assert result[0]["tiv_2016"] is None

    def test_all_unique_locations_shared_tiv(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 10, 15, 20, 20),
                (3, 10, 25, 30, 30);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016.sql"
        )
        # All share tiv_2015=10, all have unique locations
        assert result[0]["tiv_2016"] == 45.0

    def test_single_policyholder(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016.sql"
        )
        # Single row: tiv_2015 not shared (HAVING COUNT > 1 fails)
        assert result[0]["tiv_2016"] is None


class TestInvestmentsIn2016Alt:

    def test_leetcode_example(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 20, 20, 20, 20),
                (3, 10, 30, 20, 20),
                (4, 10, 40, 40, 40);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016_alt.sql"
        )
        assert result[0]["tiv_2016"] == 45.0

    def test_no_one_meets_both_criteria(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 20, 20, 20, 20),
                (3, 30, 30, 30, 30);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016_alt.sql"
        )
        assert result[0]["tiv_2016"] is None

    def test_all_unique_locations_shared_tiv(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10),
                (2, 10, 15, 20, 20),
                (3, 10, 25, 30, 30);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016_alt.sql"
        )
        assert result[0]["tiv_2016"] == 45.0

    def test_single_policyholder(self, db_insurance) -> None:
        db_insurance.execute("""
            INSERT INTO Insurance (pid, tiv_2015, tiv_2016, lat, lon) VALUES
                (1, 10, 5, 10, 10);
        """)
        result = run_sql_file_df(
            db_insurance, PROBLEM_DIR / "585_investments_in_2016_alt.sql"
        )
        assert result[0]["tiv_2016"] is None
