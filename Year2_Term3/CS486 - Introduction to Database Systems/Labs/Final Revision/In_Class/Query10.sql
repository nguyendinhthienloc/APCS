-- 10. Create a stored procedure to delete a student grade given student_ID and section_ID.
--     Input: student_ID, section_ID
--     Output: Rollback if either student_ID or section_ID is non-exists. Otherwise, commit.

CREATE PROCEDURE DeleteStudentGrade
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    BEGIN TRANSACTION;

    IF NOT EXISTS (
        SELECT *
        FROM STUDENT
        WHERE student_id = @student_id
    )
    OR NOT EXISTS (
        SELECT *
        FROM SECTION
        WHERE section_id = @section_id
    )
    BEGIN
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    DELETE FROM GRADEREPORT
    WHERE student_id = @student_id
      AND section_id = @section_id;

    COMMIT TRANSACTION;
END;