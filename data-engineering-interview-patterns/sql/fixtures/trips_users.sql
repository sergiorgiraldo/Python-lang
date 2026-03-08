-- Trips and Users tables
-- Used by: 262

CREATE TABLE IF NOT EXISTS Users (
    users_id INTEGER PRIMARY KEY,
    banned VARCHAR(10),
    role VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Trips (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    driver_id INTEGER,
    city_id INTEGER,
    status VARCHAR(50),
    request_at DATE
);
