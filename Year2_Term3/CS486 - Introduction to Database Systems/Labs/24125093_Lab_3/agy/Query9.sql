USE University;
GO

-- 9. List students whose average grade is higher than the average of all 
--    students in their department.

WITH StudentAverage AS (
    SELECT 
        s.student_id,
        s.student_name,
        s.department_id,
        AVG(CAST(gr.grade_100 AS DECIMAL(5,2))) AS avg_grade
    FROM Student s
    JOIN GradeReport gr ON s.student_id = gr.student_id
    GROUP BY s.student_id, s.student_name, s.department_id
),
DepartmentAverage AS (
    SELECT 
        department_id,
        AVG(avg_grade) AS dept_avg_grade
    FROM StudentAverage
    GROUP BY department_id
)
SELECT 
    sa.student_id,
    sa.student_name,
    sa.department_id,
    sa.avg_grade,
    da.dept_avg_grade
FROM StudentAverage sa
JOIN DepartmentAverage da ON sa.department_id = da.department_id
WHERE sa.avg_grade > da.dept_avg_grade
ORDER BY sa.department_id, sa.avg_grade DESC;
GO
