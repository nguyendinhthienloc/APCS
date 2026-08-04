USE University
DROP TRIGGER IF EXISTS teach_max_3
GO
CREATE TRIGGER teach_max_3 
ON Teaching 
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 
        t.instructor_id,
        sec.semester,
        sec.school_year
        FROM Teaching t 
        JOIN Section sec
        ON t.section_id = sec.section_id
        GROUP BY 
        t.instructor_id,
        sec.semester,
        sec.school_year
        HAVING COUNT(*) > 3
    )
    BEGIN
    RAISERROR(
        'An instructor cannot teach more than 3 sections per semester', 16, 1
    )
    ROLLBACK;

    END

END;