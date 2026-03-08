/*
LeetCode 550: Game Play Analysis IV

Find the fraction of players who logged in on the day after
their first login date (day 1 retention).

Pattern: Window function (MIN for first login) + date comparison
*/

WITH first_login AS (
    SELECT player_id,
           MIN(event_date) AS first_date
    FROM Activity
    GROUP BY player_id
)
SELECT ROUND(
    CAST(COUNT(DISTINCT a.player_id) AS DECIMAL) /
    (SELECT COUNT(DISTINCT player_id) FROM Activity),
    2
) AS fraction
FROM first_login f
JOIN Activity a
    ON a.player_id = f.player_id
    AND a.event_date = f.first_date + INTERVAL '1 day';
