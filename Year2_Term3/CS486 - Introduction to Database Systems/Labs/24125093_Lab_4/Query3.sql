USE University;
GO

IF OBJECT_ID('dbo.sp_GetSectionDetails', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetSectionDetails;
GO

CREATE PROCEDURE dbo.sp_GetSectionDetails
    @section_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        s.section_id,
        c.course_name,
        s.semester,
        s.school_year,
        dbo.fn_CountStudents(s.section_id) AS [number of registered students],
        dbo.fn_CountInstructors(s.section_id) AS [number of lecturers assigned to the section]
    FROM Section s
    JOIN Course c ON s.course_id = c.course_id
    WHERE s.section_id = @section_id;
END;
GO

EXEC dbo.sp_GetSectionDetails @section_id = 1;
GO
