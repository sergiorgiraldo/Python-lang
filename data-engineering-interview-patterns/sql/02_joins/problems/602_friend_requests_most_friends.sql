/*
LeetCode 602: Friend Requests II - Who Has the Most Friends

Each row in RequestAccepted is a friendship (bidirectional).
Find the person with the most friends and their friend count.

Pattern: UNION ALL to normalize bidirectional relationships + GROUP BY
*/

WITH all_friends AS (
    SELECT requester_id AS id FROM RequestAccepted
    UNION ALL
    SELECT accepter_id AS id FROM RequestAccepted
)
SELECT id, COUNT(*) AS num
FROM all_friends
GROUP BY id
ORDER BY num DESC
LIMIT 1;
