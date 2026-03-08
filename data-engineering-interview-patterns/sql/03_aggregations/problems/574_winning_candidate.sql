/*
LeetCode 574: Winning Candidate

Find the name of the candidate who got the most votes.

Pattern: JOIN + GROUP BY + ORDER BY + LIMIT
*/

SELECT c.name
FROM Vote v
JOIN Candidate c ON v.candidateId = c.id
GROUP BY c.id, c.name
ORDER BY COUNT(*) DESC
LIMIT 1;
