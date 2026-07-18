-- 11. Retrieve the school years and semesters, along with the number of courses held in each semester of every year.
select sec.school_year, sec.semester, count(distinct c.course_id) as no_courses
from section sec 
join Course c on sec.course_id = c.course_id
group by sec.school_year, sec.semester

-- 12. Retrieve the codes and names of courses with the highest number of instructors who have taught those courses.
SELECT TOP 1 c.course_id, c.course_name, COUNT(DISTINCT t.instructor_id) AS num_instructors
FROM Course c
JOIN Section sec ON sec.course_id = c.course_id
JOIN Teaching t ON sec.section_id = t.section_id
GROUP BY c.course_id, c.course_name
ORDER BY num_instructors DESC

-- 13. Retrieve the codes and names of instructors who have only taught courses managed by their own department.
SELECT i.instructor_id, i.instructor_name
FROM Instructor i
JOIN Teaching t ON i.instructor_id = t.instructor_id
JOIN Section sec ON sec.section_id = t.section_id
JOIN Course c ON sec.course_id = c.course_id
GROUP BY i.instructor_id, i.instructor_name, i.department_id
HAVING COUNT(DISTINCT c.department_id) = 1
   AND MIN(c.department_id) = i.department_id;


-- 14. Retrieve the code and name of ALL students, along with the count of courses managed by each department that they have participated in.
SELECT
    s.student_id,
    s.student_name,
    COUNT(DISTINCT c.course_id) AS courses_participated
FROM STUDENT s
LEFT JOIN GRADE_REPORT gr
    ON gr.student_id = s.student_id
LEFT JOIN SECTION sec
    ON sec.section_id = gr.section_id
LEFT JOIN COURSE c
    ON c.course_id = sec.course_id
   AND c.department_id = s.department_id   -- only courses managed by the student's own dept
GROUP BY s.student_id, s.student_name
ORDER BY s.student_id;
-- 15. Find the top scoring student in each section. Print all top students with their IDs if their scores are tied.
SELECT section_id, student_id, grade_100
FROM (
    SELECT
        section_id, student_id, grade_100,
        RANK() OVER (PARTITION BY section_id ORDER BY grade_100 DESC) AS rnk
    FROM GRADE_REPORT
) ranked
WHERE rnk = 1
ORDER BY section_id, student_id;