select *
from instructor i  
join department d on i.department_id = d.department_id
where d.department_name = 'Artificial Intelligence' 
and i.salary < 3000 and i.salary > 2000