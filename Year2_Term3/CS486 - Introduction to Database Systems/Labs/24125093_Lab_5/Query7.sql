USE University_DB;
GO

DROP TRIGGER IF EXISTS no_cycle;
GO

CREATE TRIGGER no_cycle
ON Prerequisite
AFTER INSERT, UPDATE
AS
BEGIN
    DECLARE @violation BIT = 0;

    ;WITH PrerequisiteChain AS (
        -- Start from each newly inserted prerequisite relationship
        SELECT
            i.course_id AS original_course_id,
            i.prerequisite_id AS current_prerequisite_id
        FROM inserted AS i

        UNION ALL

        -- Keep following prerequisite relationships
        SELECT
            pc.original_course_id,
            p.prerequisite_id
        FROM PrerequisiteChain AS pc
        JOIN Prerequisite AS p
            ON pc.current_prerequisite_id = p.course_id
    )
    SELECT TOP 1
        @violation = 1
    FROM PrerequisiteChain
    WHERE original_course_id = current_prerequisite_id;

    IF @violation = 1
    BEGIN
        RAISERROR (
            'The prerequisite relationship cannot contain a cycle.',
            16,
            1
        );

        ROLLBACK;
    END
END;
GO 