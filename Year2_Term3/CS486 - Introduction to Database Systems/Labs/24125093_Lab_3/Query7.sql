USE University;
GO

-- 7. Retrieve the code and name of ALL students, along with the count of 
--    courses they have passed (grade_100 >= 50).
-- Note: A student passes a course by passing any section of that course. 
-- We use a CTE to get all unique student-course combinations that are passed, 
-- then LEFT JOIN with the Student table to include students with 0 passed courses.

WITH PassedCourses AS (
    SELECT DISTINCT 
        gr.student_id,
        s.course_id
    FROM GradeReport gr
    JOIN Section s ON gr.section_id = s.section_id
    WHERE gr.grade_100 >= 50
)
SELECT 
    s.student_id,
    s.student_name,
    COUNT(pc.course_id) AS passed_courses_count
FROM Student s
LEFT JOIN PassedCourses pc ON s.student_id = pc.student_id
GROUP BY s.student_id, s.student_name
ORDER BY passed_courses_count DESC, s.student_id;
GO
