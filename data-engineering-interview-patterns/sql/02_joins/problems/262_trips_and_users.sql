/*
LeetCode 262: Trips and Users

Calculate the cancellation rate per day for unbanned users.
Only consider trips between '2013-10-01' and '2013-10-03'.
Cancellation rate = cancelled trips / total trips, rounded to 2 decimals.

Pattern: Filtered JOIN + conditional aggregation
*/

SELECT t.request_at AS "Day",
       ROUND(
           SUM(CASE WHEN t.status LIKE 'cancelled%' THEN 1.0 ELSE 0.0 END) /
           COUNT(*),
           2
       ) AS "Cancellation Rate"
FROM Trips t
JOIN Users c ON t.client_id = c.users_id AND c.banned = 'No'
JOIN Users d ON t.driver_id = d.users_id AND d.banned = 'No'
WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
GROUP BY t.request_at
ORDER BY t.request_at;
