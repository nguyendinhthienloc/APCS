USE University;
GO

IF OBJECT_ID('dbo.fn_CountInstructors', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_CountInstructors;
GO

CREATE FUNCTION dbo.fn_CountInstructors
(
    @section_id INT
)
RETURNS INT
AS
BEGIN
    DECLARE @instructor_count INT;

    SELECT @instructor_count = COUNT(instructor_id)
    FROM Teaching
    WHERE section_id = @section_id;

    RETURN ISNULL(@instructor_count, 0);
END;
GO

SELECT dbo.fn_CountInstructors(1) AS InstructorCount;
GO
