-- Candidate and Vote tables
-- Used by: 574

CREATE TABLE IF NOT EXISTS Candidate (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Vote (
    id INTEGER PRIMARY KEY,
    candidateId INTEGER
);
