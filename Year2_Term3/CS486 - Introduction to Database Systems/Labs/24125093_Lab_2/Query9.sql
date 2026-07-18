SELECT s.student_id, s.student_name
FROM Student s
JOIN GradeReport gr_pass ON s.student_id = gr_pass.student_id
JOIN Section sec_pass    ON gr_pass.section_id = sec_pass.section_id
JOIN Course c_pass       ON sec_pass.course_id = c_pass.course_id
JOIN GradeReport gr_fail ON s.student_id = gr_fail.student_id
JOIN Section sec_fail    ON gr_fail.section_id = sec_fail.section_id
JOIN Course c_fail       ON sec_fail.course_id = c_fail.course_id
WHERE c_pass.course_id = 'CS03' AND gr_pass.grade_100 >= 50
  AND sec_pass.semester = 'Fall' AND sec_pass.school_year = 2022
  AND c_fail.course_id = 'CS04' AND gr_fail.grade_100 < 50
  AND sec_fail.semester = 'Fall' AND sec_fail.school_year = 2022;