Use University;

-- [Test Query 2 with CS11 that indirectly has CS07 as prerequisite through CS10. The query will return all courses that have CS07 as a prerequisite, either directly or indirectly.]

-- INSERT INTO Prerequisite (course_id, prerequisite_id)
-- VALUES ('CS11', 'CS10');



WITH PrerequisiteChain AS (
    -- Anchor member: Direct dependents (courses where CS07 is a prerequisite)
    SELECT 
        Prerequisite.course_id, 
        Prerequisite.prerequisite_id, -- This is the 'parent' in the chain
        c1.course_name AS course_name,
        c2.course_name AS prerequisite_name
    FROM Prerequisite
    JOIN Course c1 ON Prerequisite.course_id = c1.course_id
    JOIN Course c2 ON Prerequisite.prerequisite_id = c2.course_id
    WHERE Prerequisite.prerequisite_id = 'CS07' 

    UNION ALL

    -- Recursive member: Link next dependents back to the previous course_id
    SELECT 
        p.course_id, 
        p.prerequisite_id,
        c1.course_name,
        c2.course_name
    FROM Prerequisite p 
    JOIN PrerequisiteChain pc ON p.prerequisite_id = pc.course_id 
    JOIN Course c1 ON p.course_id = c1.course_id
    JOIN Course c2 ON p.prerequisite_id = c2.course_id
) 

SELECT DISTINCT 
    course_id, 
    course_name, 
    prerequisite_id, 
    prerequisite_name
FROM PrerequisiteChain;