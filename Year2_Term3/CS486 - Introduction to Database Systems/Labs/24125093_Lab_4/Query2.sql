USE University;
GO

IF OBJECT_ID('dbo.fn_CountStudents', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_CountStudents;
GO

CREATE FUNCTION dbo.fn_CountStudents
(
    @section_id INT
)
RETURNS INT
AS
BEGIN
    DECLARE @student_count INT;

    SELECT @student_count = COUNT(student_id)
    FROM GradeReport
    WHERE section_id = @section_id;

    RETURN ISNULL(@student_count, 0);
END;
GO

SELECT dbo.fn_CountStudents(1) AS StudentCount;
GO
