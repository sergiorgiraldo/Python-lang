-- Person and Address tables
-- Used by: 175

CREATE TABLE IF NOT EXISTS Person (
    personId INTEGER PRIMARY KEY,
    lastName VARCHAR(100),
    firstName VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Address (
    addressId INTEGER PRIMARY KEY,
    personId INTEGER,
    city VARCHAR(100),
    state VARCHAR(100)
);
