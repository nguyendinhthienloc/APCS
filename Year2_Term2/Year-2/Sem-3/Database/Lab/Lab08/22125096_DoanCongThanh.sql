-- Q1: 
-- create the stored procedure
create or alter procedure RetrieveFailedStudents 
    @course_name nvarchar(50),
    @semester varchar(9),
    @year int
as
begin
    -- check if there are any students who failed the specified course in the given semester and year
    if exists (
        select 1
        from gradereport gr
        join section s on gr.section_id = s.section_id
        join course c on s.course_id = c.course_id
        where c.course_name = @course_name
        and s.semester = @semester
        and s.school_year = @year
        and gr.grade_100 < 50
    )
    begin
		waitfor delay '00:00:05'
        -- display student details who failed the course
        select st.student_id, st.student_name, c.course_name, gr.grade_100
        from gradereport gr
        join section s on gr.section_id = s.section_id
        join course c on s.course_id = c.course_id
        join student st on gr.student_id = st.student_id
        where c.course_name = @course_name
        and s.semester = @semester
        and s.school_year = @year
        and gr.grade_100 < 50;
    end
    else
    begin
        -- notify that no students failed the course
        print 'No students failed the specified course in the given semester and year.';
    end
end;
go

-- test the stored procedure
exec RetrieveFailedStudents @course_name = 'Databases', @semester = 'Fall', @year = 2022
go

-- Q2:
-- create the stored procedure
create or alter procedure UpdateGrades 
    @course_name nvarchar(50),
    @semester varchar(9),
    @year int
as
begin
    declare @section_id int;

    -- find the section_id for the specified course in the given semester and year
    select @section_id = s.section_id
    from section s
    join course c on s.course_id = c.course_id
    where c.course_name = @course_name
    and s.semester = @semester
    and s.school_year = @year;

    -- check if there are students with a grade of 40 in this course
    if exists (
        select 1
        from gradereport gr
        where gr.section_id = @section_id
        and gr.grade_100 between 0 and 50
    )
    begin
        -- update the grade from 40 to 50 for all students in this section
        update gradereport
        set grade_100 = 50
        where section_id = @section_id
        and grade_100 between 40 and 50
        print 'Grades updated successfully.';
    end
    else
    begin
        print 'No matching records found with grade between 40 and 50 for the specified course, semester, and year.';
    end
end;
go

-- test the stored procedure
exec UpdateGrades @course_name = 'Databases', @semester = 'Fall', @year = 2022
go

select *
from GradeReport
where section_id like '1' and grade_100 < 50

-- Q3:
go
begin transaction
set transaction isolation level repeatable read
exec RetrieveFailedStudents @course_name = 'Databases', @semester = 'Fall', @year = 2022
commit


