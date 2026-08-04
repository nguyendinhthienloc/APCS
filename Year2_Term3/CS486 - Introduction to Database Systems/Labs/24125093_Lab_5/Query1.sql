USE University;
GO

CREATE TRIGGER max_4
ON Teaching
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT teaching.section_id
        FROM course
        JOIN section
            ON course.course_id = section.course_id
        JOIN teaching
            ON teaching.section_id = section.section_id
        GROUP BY teaching.section_id
        HAVING COUNT(*) > 4
    )
    BEGIN
        RAISERROR (
            'A section cannot have more than 4 instructors.',
            16,
            1
        );

        ROLLBACK;
    END
END;
GO