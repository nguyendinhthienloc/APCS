USE University;
GO

-- 6. Find the ID and name of each student, along with the average grade (grade_100) 
--    of the sections they have passed (grade_100 >= 50).
SELECT 
    s.student_id,
    s.student_name,
    AVG(CAST(gr.grade_100 AS DECIMAL(5,2))) AS average_passed_grade
FROM Student s
JOIN GradeReport gr ON s.student_id = gr.student_id
WHERE gr.grade_100 >= 50
GROUP BY s.student_id, s.student_name;
GO
