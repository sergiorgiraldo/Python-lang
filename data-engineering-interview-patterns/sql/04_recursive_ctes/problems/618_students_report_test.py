"""Tests for LeetCode 618: Students Report By Geography."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _setup_table(db):
    """Create Student_Geo table with inline data."""
    db.execute("""
        CREATE TABLE Student_Geo (
            name VARCHAR(50),
            continent VARCHAR(20)
        )
    """)
    return db


class TestStudentsReportByGeography:
    """Test pivot with ROW_NUMBER alignment."""

    def test_leetcode_example(self, db) -> None:
        """America=[Jack, Jane], Asia=[Xi], Europe=[Pascal]."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Student_Geo VALUES
                ('Jane', 'America'),
                ('Pascal', 'Europe'),
                ('Xi', 'Asia'),
                ('Jack', 'America')
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "618_students_report.sql")
        # Row 1: America=Jack (alphabetical), Asia=Xi, Europe=Pascal
        # Row 2: America=Jane, Asia=NULL, Europe=NULL
        assert result[0]["America"] == "Jack"
        assert result[0]["Asia"] == "Xi"
        assert result[0]["Europe"] == "Pascal"
        assert result[1]["America"] == "Jane"
        assert result[1]["Asia"] is None
        assert result[1]["Europe"] is None

    def test_uneven_continent_sizes(self, db) -> None:
        """One continent has more students, shorter columns get NULLs."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Student_Geo VALUES
                ('Alice', 'America'),
                ('Bob', 'America'),
                ('Carol', 'America'),
                ('Xi', 'Asia')
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "618_students_report.sql")
        assert len(result) == 3
        # Row 1: Alice, Xi, NULL
        assert result[0]["America"] == "Alice"
        assert result[0]["Asia"] == "Xi"
        assert result[0]["Europe"] is None
        # Row 2: Bob, NULL, NULL
        assert result[1]["America"] == "Bob"
        assert result[1]["Asia"] is None
        # Row 3: Carol, NULL, NULL
        assert result[2]["America"] == "Carol"
        assert result[2]["Asia"] is None

    def test_single_continent(self, db) -> None:
        """Only one continent populated, others all NULL."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Student_Geo VALUES
                ('Xi', 'Asia'),
                ('Yuki', 'Asia')
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "618_students_report.sql")
        assert len(result) == 2
        for row in result:
            assert row["America"] is None
            assert row["Europe"] is None
        assert result[0]["Asia"] == "Xi"
        assert result[1]["Asia"] == "Yuki"

    def test_empty_continent(self, db) -> None:
        """Continent with no students shows as NULL in all rows."""
        _setup_table(db)
        db.execute("""
            INSERT INTO Student_Geo VALUES
                ('Jack', 'America'),
                ('Pascal', 'Europe')
        """)
        result = run_sql_file_df(db, PROBLEM_DIR / "618_students_report.sql")
        assert len(result) == 1
        assert result[0]["America"] == "Jack"
        assert result[0]["Asia"] is None
        assert result[0]["Europe"] == "Pascal"
