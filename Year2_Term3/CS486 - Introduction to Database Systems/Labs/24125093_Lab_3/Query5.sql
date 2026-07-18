USE University;
GO


UPDATE GradeReport
SET grade_ABC = CASE
    WHEN grade_100 BETWEEN 90 AND 100 THEN 'A'
    WHEN grade_100 BETWEEN 80 AND 89 THEN 'B'
    WHEN grade_100 BETWEEN 70 AND 79 THEN 'C'
    WHEN grade_100 BETWEEN 65 AND 69 THEN 'D'
    WHEN grade_100 BETWEEN 50 AND 64 THEN 'E'
    WHEN grade_100 < 50 THEN 'F'
    ELSE NULL -- Handles any grades outside 0-100, if any
END;
GO

-- Select the updated GradeReport to verify the changes
SELECT * FROM GradeReport;
