--4. Find the department(s) with the highest average salary for their instructors.
USE University_DB
GO
SELECT TOP 1 WITH TIES d.department_id, d.department_name, AVG(i.salary) as average_salary

FROM Department d JOIN Instructor i  
ON d.department_id = i.department_id
GROUP BY d.department_id, d.department_name
ORDER BY AVG(i.salary) DESC