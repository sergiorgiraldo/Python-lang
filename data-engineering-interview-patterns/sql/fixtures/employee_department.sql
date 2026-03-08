-- Employee and Department tables
-- Used by: 176, 177, 178, 181, 184, 185, 570, 615

CREATE TABLE IF NOT EXISTS Department (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Employee (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    salary INTEGER,
    departmentId INTEGER,
    managerId INTEGER
);
