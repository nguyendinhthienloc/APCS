-- Find top 2 students based on average grade (including all ties)
Use University;

WITH StudentAverage AS (
    SELECT
        student_id,
        AVG(grade_100) AS avg_grade
    FROM GradeReport
    GROUP BY student_id
),
RankedStudents AS (
    SELECT
        s.student_id,
        s.student_name,
        sa.avg_grade,
        DENSE_RANK() OVER (ORDER BY sa.avg_grade DESC) AS rank
    FROM Student s
    JOIN StudentAverage sa ON s.student_id = sa.student_id
)
SELECT
    student_id,
    student_name,
    avg_grade,
    rank AS rank
FROM RankedStudents
WHERE rank <= 2
ORDER BY rank, student_id;