USE University;
GO

DROP TRIGGER IF EXISTS check_prerequisites;
GO

CREATE TRIGGER check_prerequisites
ON GradeReport
AFTER INSERT, UPDATE
AS
BEGIN
    --Create variable @violation
    DECLARE @violation BIT = 0;

    --Start of Recursive CTE
    ;WITH AllPrerequisites AS (
        -- Direct prerequisites
        SELECT
            i.student_id,
            sec.course_id,
            preq.prerequisite_id
        FROM inserted AS i
        JOIN Section AS sec
            ON i.section_id = sec.section_id
        JOIN Prerequisite AS preq
            ON sec.course_id = preq.course_id

        UNION ALL

        -- Indirect prerequisites
        SELECT
            ap.student_id,
            ap.course_id,
            preq.prerequisite_id
        FROM AllPrerequisites AS ap
        JOIN Prerequisite AS preq
            ON ap.prerequisite_id = preq.course_id
    ) 
    --End of Recursive CTE 

    --Seek violation
    SELECT TOP 1
        @violation = 1
    FROM AllPrerequisites AS ap
    WHERE NOT EXISTS (
        SELECT 1
        FROM GradeReport AS gr
        JOIN Section AS previous_sec
            ON gr.section_id = previous_sec.section_id
        WHERE gr.student_id = ap.student_id
          AND previous_sec.course_id = ap.prerequisite_id
          AND gr.grade_ABC <> 'F'
    );
    --End of seek violation
    
    IF @violation = 1
    BEGIN
        RAISERROR (
            'The student has not passed all prerequisites.',
            16,
            1
        );

        ROLLBACK;
    END
END;
GO  