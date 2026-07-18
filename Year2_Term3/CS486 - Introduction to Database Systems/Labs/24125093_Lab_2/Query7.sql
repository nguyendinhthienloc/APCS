SELECT C.course_id, C.course_name
FROM Course C
WHERE C.course_id NOT IN (
    SELECT DISTINCT SEC.course_id
    FROM Teaching T
    JOIN Section SEC ON T.section_id = SEC.section_id
    WHERE T.instructor_id = 'I002'
);
