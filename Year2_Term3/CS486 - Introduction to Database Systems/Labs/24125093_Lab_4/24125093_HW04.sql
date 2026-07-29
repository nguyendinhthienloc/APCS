USE University;
GO

IF OBJECT_ID('dbo.fn_CountInstructors', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_CountInstructors;
GO

CREATE FUNCTION dbo.fn_CountInstructors
(
    @section_id INT
)
RETURNS INT
AS
BEGIN
    DECLARE @instructor_count INT;

    SELECT @instructor_count = COUNT(instructor_id)
    FROM Teaching
    WHERE section_id = @section_id;

    RETURN ISNULL(@instructor_count, 0);
END;
GO

IF OBJECT_ID('dbo.fn_CountStudents', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_CountStudents;
GO

CREATE FUNCTION dbo.fn_CountStudents
(
    @section_id INT
)
RETURNS INT
AS
BEGIN
    DECLARE @student_count INT;

    SELECT @student_count = COUNT(student_id)
    FROM GradeReport
    WHERE section_id = @section_id;

    RETURN ISNULL(@student_count, 0);
END;
GO

IF OBJECT_ID('dbo.sp_GetSectionDetails', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetSectionDetails;
GO

CREATE PROCEDURE dbo.sp_GetSectionDetails
    @section_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        s.section_id,
        c.course_name,
        s.semester,
        s.school_year,
        dbo.fn_CountStudents(s.section_id) AS [number of registered students],
        dbo.fn_CountInstructors(s.section_id) AS [number of lecturers assigned to the section]
    FROM Section s
    JOIN Course c ON s.course_id = c.course_id
    WHERE s.section_id = @section_id;
END;
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

IF OBJECT_ID('dbo.sp_GetInstructorClassesBySemester', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetInstructorClassesBySemester;
GO

CREATE PROCEDURE dbo.sp_GetInstructorClassesBySemester
    @year INT,
    @semester VARCHAR(9)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        i.instructor_id,
        @year AS [year],
        @semester AS [semester],
        COUNT(DISTINCT t.section_id) AS [number of classes taught by each lecturer]
    FROM Instructor i
    JOIN Teaching t ON i.instructor_id = t.instructor_id
    JOIN Section s ON t.section_id = s.section_id
    WHERE s.school_year = @year
      AND s.semester = @semester
    GROUP BY i.instructor_id;
END;
GO

IF OBJECT_ID('dbo.fn_GetTotalRegisteredCredits', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_GetTotalRegisteredCredits;
GO

CREATE FUNCTION dbo.fn_GetTotalRegisteredCredits
(
    @student_id VARCHAR(9),
    @year INT,
    @semester VARCHAR(9)
)
RETURNS INT
AS
BEGIN
    DECLARE @total_credits INT;

    SELECT @total_credits = SUM(c.credit)
    FROM GradeReport gr
    JOIN Section sec ON gr.section_id = sec.section_id
    JOIN Course c ON sec.course_id = c.course_id
    WHERE gr.student_id = @student_id
      AND sec.school_year = @year
      AND sec.semester = @semester;

    RETURN ISNULL(@total_credits, 0);
END;
GO
