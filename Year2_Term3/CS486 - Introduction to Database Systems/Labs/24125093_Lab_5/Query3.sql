DROP TRIGGER IF EXISTS max_4_subjects;
GO
CREATE Trigger max_4_subjects
ON GradeReport
AFTER INSERT, UPDATE
AS 
BEGIN
    IF EXISTS (
    SELECT 
        gr.student_id,
        sec.semester,
        sec.school_year
    FROM GradeReport gr
    JOIN Section sec
        ON gr.section_id = sec.section_id
    GROUP BY 
        gr.student_id,
        sec.semester,
        sec.school_year
    HAVING COUNT(DISTINCT sec.course_id) > 4
    )
    BEGIN 
        RAISERROR(
        'Students should study a maximum of 4 subjects per semester',
        16,
        1
        );
        ROLLBACK;
    END
END;