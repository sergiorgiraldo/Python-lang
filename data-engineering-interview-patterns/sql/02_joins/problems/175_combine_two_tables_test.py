"""Tests for LeetCode 175: Combine Two Tables."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestCombineTwoTables:

    def test_example(self, db_person_address) -> None:
        db_person_address.execute("""
            INSERT INTO Person (personId, lastName, firstName) VALUES
                (1, 'Wang', 'Allen'), (2, 'Alice', 'Bob');
            INSERT INTO Address (addressId, personId, city, state) VALUES
                (1, 2, 'New York City', 'New York');
        """)
        result = run_sql_file_df(
            db_person_address, PROBLEM_DIR / "175_combine_two_tables.sql"
        )
        result_by_name = {r["firstName"]: r for r in result}
        assert result_by_name["Allen"]["city"] is None
        assert result_by_name["Bob"]["city"] == "New York City"

    def test_no_addresses(self, db_person_address) -> None:
        db_person_address.execute("""
            INSERT INTO Person (personId, lastName, firstName) VALUES
                (1, 'Wang', 'Allen');
        """)
        result = run_sql_file_df(
            db_person_address, PROBLEM_DIR / "175_combine_two_tables.sql"
        )
        assert len(result) == 1
        assert result[0]["city"] is None

    def test_multiple_addresses(self, db_person_address) -> None:
        """Person with multiple addresses appears multiple times."""
        db_person_address.execute("""
            INSERT INTO Person (personId, lastName, firstName) VALUES
                (1, 'Wang', 'Allen');
            INSERT INTO Address (addressId, personId, city, state) VALUES
                (1, 1, 'Boston', 'MA'), (2, 1, 'NYC', 'NY');
        """)
        result = run_sql_file_df(
            db_person_address, PROBLEM_DIR / "175_combine_two_tables.sql"
        )
        assert len(result) == 2
