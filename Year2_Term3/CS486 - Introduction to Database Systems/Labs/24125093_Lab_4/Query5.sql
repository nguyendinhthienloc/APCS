USE University;
GO

IF OBJECT_ID('dbo.sp_GetInstructorClassesBySemester', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetInstructorClassesBySemester;
GO

CREATE PROCEDURE dbo.sp_GetInstructorClassesBySemester
    @year INT,
    @semester VARCHAR(9)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        i.instructor_id,
        @year AS [year],
        @semester AS [semester],
        COUNT(DISTINCT t.section_id) AS [number of classes taught by each lecturer]
    FROM Instructor i
    JOIN Teaching t ON i.instructor_id = t.instructor_id
    JOIN Section s ON t.section_id = s.section_id
    WHERE s.school_year = @year
      AND s.semester = @semester
    GROUP BY i.instructor_id;
END;
GO

EXEC dbo.sp_GetInstructorClassesBySemester @year = 2022, @semester = 'Fall';
GO
