-- Retrieve the codes and names of students who have passed more than two courses

select s.student_id, s.student_name, count(distinct c.course_id) as no_passed_courses
from student s 
join GradeReport gr on s.student_id = gr.student_id
join Section sec on sec.section_id = gr.section_id
join Course c on sec.course_id = c.course_id
where gr.grade_100 > 50
group by s.student_id, s.student_name
having count(distinct c.course_id) > 2