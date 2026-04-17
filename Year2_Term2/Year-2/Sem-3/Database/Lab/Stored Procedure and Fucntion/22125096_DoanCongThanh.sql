-- 1. Write a function that counts the number of instructors assigned to a given section_id.
create function CountInstructor(@section_id int)
returns int
as
	begin
		return
		(
		select distinct count(*)
		from Teaching
		where section_id = @section_id
		)
	end
-- Execute
go
declare @number_of_instructor int = dbo.CountInstructor(1)
print 'Number of instructors assigned to section_id 1 is: ' + cast(@number_of_instructor as varchar(20))

-- 2. Write a function that counts the number of students registered for a given section_id.
go
create function CountStudent(@section_id int)
returns int
as
	begin
		return
		(
		select distinct count(*)
		from GradeReport
		where section_id = @section_id
		)
	end
go
-- Execute
declare @number_of_student int = dbo.CountStudent(1)
print 'Number of students register course for section_id 1 is: ' + cast(@number_of_student as varchar(20))

--3. Write a stored procedure to retrieve the section ID, course name, semester, school year, number
--of instructors assigned to the section, and number of students registered for the section.
--● Input: section_id
--● Output: section_id, course_name, semester, school_year, number of registered students,
--number of lecturers assigned to the section.
--● Note: Reuse the functions defined in the questions 1 and 2.
go
alter proc RetrieveInformationFromSectionID
	@section_id int,
	@section_id_out int,
	@course_name nvarchar(50), 
	@semester varchar(9), 
	@school_year int,
	@number_of_registered_students int,
	@number_of_lecturers int
as
	begin
		select @section_id_out=S.section_id, @section_id_out = S.section_id,@course_name = C.course_name, @semester = S.semester, @school_year = S.school_year, @number_of_registered_students = dbo.CountStudent(@section_id),@number_of_lecturers = dbo.CountInstructor(@section_id)
		from Section S join Course C on S.course_id = C.course_id
		where S.section_id = @section_id
		if @@ERROR <> 0 return 1
		return 0
	end
go
--Execute
declare @section_id int,
	@course_name nvarchar(50), 
	@semester varchar(9), 
	@school_year int,
	@number_of_registered_students int,
	@number_of_lecturers int,
	@error int
select 