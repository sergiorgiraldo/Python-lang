/*
LeetCode 580: Count Student Number in Departments

Return department name and student count, ordered by count desc then name asc.
Include departments with zero students.

Pattern: LEFT JOIN + COUNT with GROUP BY
*/

SELECT d.name AS dept_name,
       COUNT(s.student_id) AS student_number
FROM Department d
LEFT JOIN Student s ON d.id = s.department_id
GROUP BY d.id, d.name
ORDER BY student_number DESC, dept_name ASC;
