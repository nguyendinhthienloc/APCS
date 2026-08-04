USE University;
GO
CREATE TRIGGER head_department
ON Department 
AFTER INSERT, UPDATE 

AS 
BEGIN 
    IF EXISTS (
    SELECT   
        Department.department_id,
        Department.department_head,
        Instructor.department_id
    FROM Department
    JOIN Instructor
    ON Department.department_head = Instructor.instructor_id
    WHERE Department.department_id <> Instructor.department_id)
    BEGIN 
    RAISERROR(
        'Department head should belong to that department',
        16,
        1
    );
    ROLLBACK;
    END
END;
GO
