/*
LeetCode 175: Combine Two Tables

Report firstName, lastName, city, state for each person.
If a person doesn't have an address, report NULL.

Pattern: LEFT JOIN (preserve all rows from the left table)
*/

SELECT p.firstName, p.lastName, a.city, a.state
FROM Person p
LEFT JOIN Address a ON p.personId = a.personId;
