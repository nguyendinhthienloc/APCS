USE University;
GO

IF OBJECT_ID('dbo.sp_GetStudentsEnrolledInAllDepartmentCourses', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetStudentsEnrolledInAllDepartmentCourses;
GO

CREATE PROCEDURE dbo.sp_GetStudentsEnrolledInAllDepartmentCourses
    @department_name NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        st.student_id,
        st.student_name
    FROM Student st
    WHERE NOT EXISTS (
        SELECT c.course_id
        FROM Course c
        JOIN Department d ON c.department_id = d.department_id
        WHERE d.department_name = @department_name
          AND NOT EXISTS (
              SELECT 1
              FROM GradeReport gr
              JOIN Section sec ON gr.section_id = sec.section_id
              WHERE gr.student_id = st.student_id
                AND sec.course_id = c.course_id
          )
    )
    AND EXISTS (
        SELECT 1
        FROM Course c
        JOIN Department d ON c.department_id = d.department_id
        WHERE d.department_name = @department_name
    );
END;
GO

EXEC dbo.sp_GetStudentsEnrolledInAllDepartmentCourses @department_name = 'Information System';
GO
