-- 5. Identify the students who are currently enrolled in a course but have not yet passed any of its prerequisite courses.
USE University_DB;
GO

SELECT DISTINCT
    s.student_id,
    s.student_name,
    c.course_id,
    c.course_name

FROM Student AS s
JOIN GradeReport AS g
    ON g.student_id = s.student_id
JOIN Section AS sec
    ON sec.section_id = g.section_id
JOIN Course AS c
    ON c.course_id = sec.course_id

WHERE g.grade_100 IS NULL
  AND EXISTS (
      SELECT 1
      FROM Prerequisite AS p
      WHERE p.course_id = c.course_id
  )
  AND NOT EXISTS (
      SELECT 1
      FROM Prerequisite AS p
      JOIN Section AS preq_sec
            ON preq_sec.course_id = p.prerequisite_id
      JOIN GradeReport AS preq_grade
            ON preq_grade.section_id = preq_sec.section_id
            AND preq_grade.student_id = s.student_id
      WHERE p.course_id = c.course_id
        AND preq_grade.grade_100 >= 50
  );