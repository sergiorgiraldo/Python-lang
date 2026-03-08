/*
LeetCode 601: Human Traffic of Stadium

Find rows where 3+ consecutive rows have people >= 100.
Return all rows that are part of such a streak.

Pattern: Window function for streak detection (island problem)
*/

WITH high_traffic AS (
    SELECT *,
           id - ROW_NUMBER() OVER (ORDER BY id) AS grp
    FROM Stadium
    WHERE people >= 100
),
streaks AS (
    SELECT grp
    FROM high_traffic
    GROUP BY grp
    HAVING COUNT(*) >= 3
)
SELECT h.id, h.visit_date, h.people
FROM high_traffic h
JOIN streaks s ON h.grp = s.grp
ORDER BY h.id;
