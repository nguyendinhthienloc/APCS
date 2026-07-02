USE my_database;
SELECT 
    c1.course_id, 
    c1.course_name, 
    c2.course_name AS prerequisite_name
FROM course c1
INNER JOIN prerequisite p 
    ON c1.course_id = p.course_id
INNER JOIN course c2 
    ON p.prerequisite_id = c2.course_id
WHERE 
    c1.department_id = 'IS';