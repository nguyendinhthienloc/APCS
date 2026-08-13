-- 8. Write a trigger to perform a cascading delete for a department.
CREATE TRIGGER trg_Department_CascadeDelete
ON Department
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Clear Department.department_head for instructors
    --    who are about to be deleted.
    UPDATE Department
    SET department_head = NULL
    WHERE department_head IN (
        -- Find instructors belonging to departments in deleted
    );

    -- 2. Delete Teaching rows:
    --    a) sections belonging to the deleted departments' courses
    --    b) instructors belonging to the deleted departments

    -- 3. Delete GradeReport rows:
    --    a) students belonging to the deleted departments
    --    b) sections belonging to the deleted departments' courses

    -- 4. Delete Prerequisite rows where either course column
    --    refers to a course from the deleted departments

    -- 5. Delete Section rows belonging to those courses

    -- 6. Delete the direct children
    DELETE s
    FROM Student s
    JOIN deleted d
        ON d.department_id = s.department_id;

    -- Delete Course here
    -- Delete Instructor here

    -- 7. Delete the departments themselves
    DELETE dep
    FROM Department dep
    JOIN deleted d
        ON d.department_id = dep.department_id;
END;