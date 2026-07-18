USE University;
GO

-- 8. For each department, find the student(s) with the highest average grade 
--    across all enrolled sections. Return department_id, department name, 
--    student_id, student name, and average grade (including ties).

WITH StudentAverage AS (
    SELECT 
        student_id,
        AVG(CAST(grade_100 AS DECIMAL(5,2))) AS avg_grade
    FROM GradeReport
    GROUP BY student_id
),
DepartmentRanked AS (
    SELECT 
        d.department_id,
        d.department_name,
        s.student_id,
        s.student_name,
        sa.avg_grade,
        DENSE_RANK() OVER (PARTITION BY d.department_id ORDER BY sa.avg_grade DESC) AS rnk
    FROM Student s
    JOIN Department d ON s.department_id = d.department_id
    JOIN StudentAverage sa ON s.student_id = sa.student_id
)
SELECT 
    department_id,
    department_name,
    student_id,
    student_name,
    avg_grade
FROM DepartmentRanked
WHERE rnk = 1
ORDER BY department_id;
GO
