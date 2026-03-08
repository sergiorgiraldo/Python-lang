/*
LeetCode 511: Game Play Analysis I

Find the first login date for each player.

Pattern: GROUP BY + MIN aggregate
*/

SELECT player_id,
       MIN(event_date) AS first_login
FROM Activity
GROUP BY player_id;
