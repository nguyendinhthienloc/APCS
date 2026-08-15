--3. Find all students who have taken and passed at least one course from every department in the university.
USE University_DB
GO
SELECT s.student_id, s.student_name

FROM Student AS s
JOIN GradeReport AS g
    ON s.student_id = g.student_id
JOIN Section AS sec
    ON sec.section_id = g.section_id
JOIN Course AS c
    ON c.course_id = sec.course_id
    
WHERE g.grade_100 >= 50
GROUP BY s.student_id, s.student_name
HAVING COUNT(DISTINCT c.department_id) =
       (SELECT COUNT(*) FROM Department)