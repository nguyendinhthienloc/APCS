CREATE PROCEDURE MultiplyStudentGrade
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    BEGIN TRANSACTION;

    IF EXISTS (
        SELECT *
        FROM STUDENT
        WHERE student_id = @student_id
    )
    AND EXISTS (
        SELECT *
        FROM SECTION
        WHERE section_id = @section_id
    )
    BEGIN
        UPDATE GRADEREPORT
        SET grade_100 = grade_100 * 1.1
        WHERE student_id = @student_id
          AND section_id = @section_id;
    END;

    COMMIT TRANSACTION;
END;
GO