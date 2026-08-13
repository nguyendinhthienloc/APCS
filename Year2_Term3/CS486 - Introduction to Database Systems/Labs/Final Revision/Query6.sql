--6. (CTE allowed) For each department, find the lecturer with the highest number of unique courses taught.
USE University_DB;
GO

WITH LecturerCourseCounts AS (
    SELECT
        d.department_id,
        d.department_name,
        i.instructor_id,
        i.instructor_name,
        COUNT(DISTINCT sec.course_id) AS course_count
    FROM Department AS d
    JOIN Instructor AS i
        ON i.department_id = d.department_id
    JOIN Teaching AS t
        ON t.instructor_id = i.instructor_id
    JOIN Section AS sec
        ON sec.section_id = t.section_id
    WHERE t.teaching_role = 'Lecturer'
    GROUP BY
        d.department_id,
        d.department_name,
        i.instructor_id,
        i.instructor_name
)
,MaximumCounts AS (
    SELECT
        department_id,
        MAX(course_count) AS max_course_count
    FROM LecturerCourseCounts
    GROUP BY department_id
)
SELECT
    l.department_id,
    l.department_name,
    l.instructor_id,
    l.instructor_name,
    l.course_count
FROM LecturerCourseCounts AS l
JOIN MaximumCounts AS m
    ON m.department_id = l.department_id
   AND m.max_course_count = l.course_count;