-- Activity table for game play analysis
-- Used by: 511, 550

CREATE TABLE IF NOT EXISTS Activity (
    player_id INTEGER,
    device_id INTEGER,
    event_date DATE,
    games_played INTEGER
);
