USE University;
GO

IF OBJECT_ID('dbo.fn_GetTotalRegisteredCredits', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_GetTotalRegisteredCredits;
GO

CREATE FUNCTION dbo.fn_GetTotalRegisteredCredits
(
    @student_id VARCHAR(9),
    @year INT,
    @semester VARCHAR(9)
)
RETURNS INT
AS
BEGIN
    DECLARE @total_credits INT;

    SELECT @total_credits = SUM(c.credit)
    FROM GradeReport gr
    JOIN Section sec ON gr.section_id = sec.section_id
    JOIN Course c ON sec.course_id = c.course_id
    WHERE gr.student_id = @student_id
      AND sec.school_year = @year
      AND sec.semester = @semester;

    RETURN ISNULL(@total_credits, 0);
END;
GO

SELECT dbo.fn_GetTotalRegisteredCredits('ST001', 2022, 'Fall') AS [number of register credits];
GO
