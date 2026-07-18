USE University;
GO

-- 4. Insert data into the TeachingCapacity table using a query.
-- The query joins Teaching and Section to map instructor_id to course_id, 
-- and counts the distinct school_years taught by the instructor for that course.

-- Clear any existing data first to prevent duplicate key violations
TRUNCATE TABLE TeachingCapacity;
GO

INSERT INTO TeachingCapacity (instructor_id, course_id, nb_year)
SELECT 
    t.instructor_id,
    s.course_id,
    COUNT(DISTINCT s.school_year) AS nb_year
FROM Teaching t
JOIN Section s ON t.section_id = s.section_id
GROUP BY t.instructor_id, s.course_id;
GO

-- Verify the inserted data
SELECT * FROM TeachingCapacity;
GO
