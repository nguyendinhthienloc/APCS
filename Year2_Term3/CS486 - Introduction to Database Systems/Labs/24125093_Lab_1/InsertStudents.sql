USE my_database;
GO
INSERT INTO Student (student_id, student_name, gender, birthdate, student_class, department_id)
VALUES
('ST001', 'Nguyen Ai Linh', 'F', '2002-12-01', NULL, 'CS'),
('ST002', 'Tran Thanh Sang', 'M', '2003-09-02', NULL, 'CS'),
('ST003', 'Huynh Thanh Phong', 'M', '2001-05-03', NULL, 'SE'),
('ST004', 'Hoang Nhat Linh', 'F', '2002-05-10', NULL, 'SE'),
('ST005', 'Le Ba Khanh', 'M', '2001-11-12', NULL, 'SE'),
('ST006', 'Ly Quoc Phong', 'M', '2000-08-12', NULL, 'SE'),
('ST007', 'Tran Thanh An', 'F', '2000-11-09', NULL, 'IS'),
('ST008', 'Le Nha Thu', 'F', '2002-08-09', NULL, 'IS'),
('ST009', 'Ho Ngoc Anh', 'F', '2003-11-01', NULL, 'AI'),
('ST010', 'Nguyen Thanh Son', 'M', '2003-12-05', NULL, 'NW');

select * from Student;
Go