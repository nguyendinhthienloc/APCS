--Creating 2 CTEs Student and GradeReport and inserting values into them
WITH 
StudentAverage AS (
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
        RANK() OVER (ORDER BY sa.avg_grade DESC) AS rank
    FROM Student s
    JOIN StudentAverage sa ON s.student_id = sa.student_id
) 
--These 2 CTEs are not saved in the database, they are just virtual tables created for the purpose of this query. The first virtual table StudentAverage calculates the average grade for each student by grouping the GradeReport table by student_id. The second virtual table RankedStudents joins the Student table with the StudentAverage table to get the student names and their average grades, and assigns a rank to each student based on their average grade in descending order. Finally, the main query selects the student_id, student_name, avg_grade, and rank from the RankedStudents virtual table where the rank is less than or equal to 2, and orders the results by rank and student_id in descending order.

SELECT student_id, student_name, avg_grade, rank as rank 
FROM RankedStudents
WHERE rank <= 2 
ORDER BY rank, student_id DESC;