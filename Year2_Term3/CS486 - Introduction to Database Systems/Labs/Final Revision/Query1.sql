USE University_DB
GO
-- 1. Find the names of all courses that have at least one prerequisite, but none of their prerequisite courses have any prerequisites themselves.
SELECT c.course_name
FROM Course c  
WHERE EXISTS (
    SELECT p1.prerequisite_id
    FROM Prerequisite p1
    WHERE p1.course_id = c.course_id
)
AND NOT EXISTS (
    SELECT p1.course_id
    FROM Prerequisite p1
    JOIN Prerequisite p2
        ON p1.prerequisite_id = p2.course_id
    WHERE c.course_id = p1.course_id
);  