Use my_database
SELECT * from instructor 
--Find instructors who are teaching CS07 course in Fall 2022
SELECT instructor_name, course_id, salary FROM Instructor i
JOIN teaching on i.instructor_id = teaching.instructor_id
JOIN section s on teaching.section_id = s.section_id
WHERE s.course_id = 'CS07'
--Increase salary by 10% for all instructors teaching CS07 
update instructor set salary = salary * 1.1
where instructor_id in (
    SELECT i.instructor_id FROM Instructor i
    JOIN teaching t on i.instructor_id = t.instructor_id
    JOIN section s on t.section_id = s.section_id
    WHERE s.course_id = 'CS07'
)
