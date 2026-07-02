-- UPDATE student
-- SET student_class = '24A02'
-- WHERE student_id IN ('ST001', 'ST002', 'ST003', 'ST004', 'ST005', 'ST006', 'ST007', 'ST008', 'ST009', 'ST010');

SELECT * FROM GradeReport JOIN Student ON GradeReport.student_id = Student.student_id
join Section sec on GradeReport.section_id = sec.section_id
join course c on sec.course_id = c.course_id
WHERE c.course_id = 'CS07' and sec.semester = 'Fall 2022' and sec.school_year = '2022';


