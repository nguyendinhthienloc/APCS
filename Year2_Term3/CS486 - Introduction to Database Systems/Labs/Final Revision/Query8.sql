CREATE TRIGGER trg_DeleteDepartment
ON Department
INSTEAD OF DELETE
AS
BEGIN
    UPDATE Department
    SET department_head = NULL
    WHERE department_id IN (
        SELECT department_id
        FROM deleted
    );

    DELETE FROM Teaching
    WHERE instructor_id IN (
        SELECT instructor_id
        FROM Instructor
        WHERE department_id IN (
            SELECT department_id FROM deleted
        )
    )
    OR section_id IN (
        SELECT s.section_id
        FROM Section s
        JOIN Course c ON s.course_id = c.course_id
        WHERE c.department_id IN (
            SELECT department_id FROM deleted
        )
    );

    DELETE FROM GradeReport
    WHERE student_id IN (
        SELECT student_id
        FROM Student
        WHERE department_id IN (
            SELECT department_id FROM deleted
        )
    )
    OR section_id IN (
        SELECT s.section_id
        FROM Section s
        JOIN Course c ON s.course_id = c.course_id
        WHERE c.department_id IN (
            SELECT department_id FROM deleted
        )
    );

    DELETE FROM Prerequisite
    WHERE course_id IN (
        SELECT course_id
        FROM Course
        WHERE department_id IN (
            SELECT department_id FROM deleted
        )
    )
    OR prerequisite_id IN (
        SELECT course_id
        FROM Course
        WHERE department_id IN (
            SELECT department_id FROM deleted
        )
    );

    DELETE FROM Section
    WHERE course_id IN (
        SELECT course_id
        FROM Course
        WHERE department_id IN (
            SELECT department_id FROM deleted
        )
    );

    DELETE FROM Student
    WHERE department_id IN (
        SELECT department_id FROM deleted
    );

    DELETE FROM Course
    WHERE department_id IN (
        SELECT department_id FROM deleted
    );

    DELETE FROM Instructor
    WHERE department_id IN (
        SELECT department_id FROM deleted
    );

    DELETE FROM Department
    WHERE department_id IN (
        SELECT department_id FROM deleted
    );
END;