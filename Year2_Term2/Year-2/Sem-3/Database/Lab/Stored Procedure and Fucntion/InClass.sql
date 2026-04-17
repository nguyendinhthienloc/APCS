-- xuất ds các giảng viên -> không có tham số
create proc XemDSHocKy
as
	select * from Instructor
go
-- gọi thực thi
exec XemDSHocKy
-- xuất ds các gv khoa CNTT -> có tham số input: mã khoa
go
alter proc XemDSHocKy
	@department_id varchar(5)
as
	select * from Instructor
	where department_id = @department_id
go
-- gọi thực thi
exec XemDSHocKy 'CS'

-- cho input là 2 số
-- tính tổng
go
create proc TinhTong
	@first_num int,
	@second_num int
as
	return @first_num + @second_num
go
declare @tong int
exec @tong = TinhTong 1,2
print @tong

-- tính tổng version mới
go
create proc TinhTong2
	@first_num int,
	@second_num int,
	@result int out
as
	set @result = @first_num + @second_num
go
declare @tong int
exec TinhTong2 1,2,@tong out
print @tong

-- tìm kiếm thông tin của gv theo mã gv
-- xuất ra họ tên, lương
-- cho biết thủ tục thực hiện thành công hay không

go
create proc SearchInstruction
	@instructor_id varchar(5),
	@name nvarchar(50) out,
	@salary int out
as
	begin
		select @name = instructor_name, @salary = salary
		from Instructor
		where instructor_id = @instructor_id
		if @@ERROR <> 0 return 1
		return 0
	end
go
declare @name nvarchar(50), @salary int, @error int
exec @error = SearchInstruction 'I002',@name out ,@salary out
if @error = 0
	begin
		print N'Họ và tên ' + @name
		print N'Lương ' + cast(@salary as nvarchar(50))
	end
else
	print N'Không thành công'

-- tính tuổi sv
go
create function TinhTuoiSV (@student_id varchar(20))
returns int
as
	begin
		return (select year(GETDATE()) - year(birthdate)
		from Student
		where student_id = @student_id)
	end
go
-- gọi thực thi
-- cho ds sv, tuổi sv của các sv > 20 tuổi
select student_id,student_name, dbo.TinhTuoiSV(student_id)
from Student
where  dbo.TinhTuoiSV(student_id) > 20
