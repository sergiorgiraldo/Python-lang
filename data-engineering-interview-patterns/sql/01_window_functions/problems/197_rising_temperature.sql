/*
LeetCode 197: Rising Temperature

Find dates where the temperature is higher than the previous day's.

Pattern: LAG window function with date comparison
*/

SELECT id
FROM (
    SELECT id,
           temperature,
           recordDate,
           LAG(temperature) OVER (ORDER BY recordDate) AS prev_temp,
           LAG(recordDate) OVER (ORDER BY recordDate) AS prev_date
    FROM Weather
) t
WHERE temperature > prev_temp
  AND recordDate = prev_date + INTERVAL '1 day';
