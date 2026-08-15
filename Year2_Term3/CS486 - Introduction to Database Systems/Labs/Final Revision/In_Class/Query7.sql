-- 7. Identify the table of influence and write at least one trigger to ensure the BR1: There are no two courses within the same department having the same name.
CREATE TRIGGER duplicate
ON Course 
AFTER INSERT, UPDATE
AS 
BEGIN 
    IF EXISTS (
        SELECT c.course_id
        FROM inserted as i
        JOIN Course as c
            ON c.department_id = i.department_id
            AND c.course_name = i.course_name
        WHERE c.course_id <> i.course_id
    )
    BEGIN
        ROLLBACK TRANSACTION;
        RAISERROR ( '2 Courses cannot have the same name', 16, 1); 
    END
END;