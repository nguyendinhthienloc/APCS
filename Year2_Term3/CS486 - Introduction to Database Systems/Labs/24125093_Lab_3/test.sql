USE University;
SELECT *
FROM Course, 
     Prerequisite 
WHERE Course.course_id = Prerequisite.course_id