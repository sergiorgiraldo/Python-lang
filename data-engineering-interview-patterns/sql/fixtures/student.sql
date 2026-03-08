-- Student table
-- Used by: 580, 618

CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY,
    student_name VARCHAR(100),
    gender VARCHAR(1),
    department_id INTEGER
);
