-- 2. Identify all instructors who are teaching a course in the same semester and year as the department head of their own department.
SELECT DISTINCT i.instructor_name
FROM Instructor AS i
JOIN Department AS d
    ON i.department_id = d.department_id
JOIN Teaching AS t1
    ON i.instructor_id = t1.instructor_id
JOIN Section AS s1
    ON t1.section_id = s1.section_id
JOIN Teaching AS t2
    ON t2.instructor_id = d.department_head
JOIN Section AS s2
    ON s2.section_id = t2.section_id
WHERE s1.semester = s2.semester
  AND s1.school_year = s2.school_year;