SELECT DISTINCT t1.instructor_id
FROM Teaching t1
JOIN Teaching t2
  ON t1.instructor_id = t2.instructor_id
WHERE t1.teaching_role = 'Lecturer'
  AND t2.teaching_role = 'TA';