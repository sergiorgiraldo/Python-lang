"""Tests for LeetCode 580: Count Student Number in Departments."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestCountStudentsPerDept:

    def test_example(self, db) -> None:
        db.execute("""
            CREATE TABLE Department (id INTEGER PRIMARY KEY, name VARCHAR(100));
            CREATE TABLE Student (
                student_id INTEGER PRIMARY KEY,
                student_name VARCHAR(100),
                gender VARCHAR(1),
                department_id INTEGER
            );
            INSERT INTO Department VALUES (1, 'Engineering'), (2, 'Science'), (3, 'Law');
            INSERT INTO Student VALUES
                (1, 'Jack', 'M', 1), (2, 'Jane', 'F', 1), (3, 'Mark', 'M', 2);
        """)
        result = run_sql_file_df(
            db, PROBLEM_DIR / "580_count_students_per_dept.sql"
        )
        assert len(result) == 3
        # Ordered by count desc, then name asc
        assert result[0]["dept_name"] == "Engineering"
        assert result[0]["student_number"] == 2
        assert result[1]["dept_name"] == "Science"
        assert result[1]["student_number"] == 1
        assert result[2]["dept_name"] == "Law"
        assert result[2]["student_number"] == 0

    def test_empty_departments(self, db) -> None:
        """Departments with no students must appear with count 0."""
        db.execute("""
            CREATE TABLE Department (id INTEGER PRIMARY KEY, name VARCHAR(100));
            CREATE TABLE Student (
                student_id INTEGER PRIMARY KEY,
                student_name VARCHAR(100),
                gender VARCHAR(1),
                department_id INTEGER
            );
            INSERT INTO Department VALUES (1, 'Engineering'), (2, 'Science');
        """)
        result = run_sql_file_df(
            db, PROBLEM_DIR / "580_count_students_per_dept.sql"
        )
        assert len(result) == 2
        for r in result:
            assert r["student_number"] == 0

    def test_tie_ordering(self, db) -> None:
        """Tied counts ordered by department name ascending."""
        db.execute("""
            CREATE TABLE Department (id INTEGER PRIMARY KEY, name VARCHAR(100));
            CREATE TABLE Student (
                student_id INTEGER PRIMARY KEY,
                student_name VARCHAR(100),
                gender VARCHAR(1),
                department_id INTEGER
            );
            INSERT INTO Department VALUES (1, 'Zoology'), (2, 'Art'), (3, 'Biology');
            INSERT INTO Student VALUES
                (1, 'A', 'M', 1), (2, 'B', 'F', 2), (3, 'C', 'M', 3);
        """)
        result = run_sql_file_df(
            db, PROBLEM_DIR / "580_count_students_per_dept.sql"
        )
        # All have count 1, so ordered by name: Art, Biology, Zoology
        names = [r["dept_name"] for r in result]
        assert names == ["Art", "Biology", "Zoology"]
