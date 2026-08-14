-- 9. Create a stored procedure to do the following steps with the given <student_id> and <section_id>:
--    a) Read the current grade of the student <student_id> in the section <section_id>.
--    b) Delay for 10 seconds
--    c) Reread the grade of that student
GO
CREATE PROCEDURE ReadGradeTwice
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    -- a) Read the current grade
    SELECT grade_100, grade_ABC
    FROM GRADEREPORT
    WHERE student_id = @student_id
      AND section_id = @section_id;

    -- b) Wait for 10 seconds
    WAITFOR DELAY '00:00:10';

    -- c) Read the grade again
    SELECT grade_100, grade_ABC
    FROM GRADEREPORT
    WHERE student_id = @student_id
      AND section_id = @section_id;
END;
GO