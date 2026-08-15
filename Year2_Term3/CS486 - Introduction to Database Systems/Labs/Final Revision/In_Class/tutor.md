# CS486 Final Review Tutor Memory

## Student preference

- Act as a tutor.
- Explain the logic and syntax for memorization.
- Give hints or partial queries first.
- Give a complete answer only when the student explicitly asks for it.
- When checking a query, identify what is correct and what needs changing.

## Workspace

- Database: `University_DB`
- Main schema file: `University_DB.sql`
- Review questions: `Topic10_FinalReview_Questions.txt`
- ERD: `database_erd.md`

## Important schema

- `Department(department_id, department_name, office, department_head)`
- `Student(student_id, student_name, ..., department_id)`
- `Course(course_id, course_name, credit, department_id)`
- `Instructor(instructor_id, instructor_name, ..., department_id, salary)`
- `Section(section_id, course_id, semester, school_year, capacity)`
- `Teaching(section_id, instructor_id, teaching_role)`
- `GradeReport(section_id, student_id, grade_100, grade_ABC)`
- `Prerequisite(course_id, prerequisite_id)`

## Completed questions

### Question 1

Find courses with at least one prerequisite, where none of those prerequisites has another prerequisite.

The student’s final logic was correct:

```sql
SELECT c.course_name
FROM Course c
WHERE EXISTS (
    SELECT p1.prerequisite_id
    FROM Prerequisite p1
    WHERE p1.course_id = c.course_id
)
AND NOT EXISTS (
    SELECT p1.course_id
    FROM Prerequisite p1
    JOIN Prerequisite p2
        ON p1.prerequisite_id = p2.course_id
    WHERE c.course_id = p1.course_id
);
```

Memory pattern:

```text
EXISTS      = must have at least one
NOT EXISTS  = must not have any matching rows
```

`Prerequisite` is a self-referencing associative table. `course_id` is the course being taken; `prerequisite_id` is the required course. Both refer to `Course.course_id`, but they have different roles.

### Question 2

Find instructors teaching in the same semester and school year as the head of their own department.

The student’s query was correct. It compares two paths:

```text
instructor → own department → department head
instructor → section taught
department head → section taught
```

`DISTINCT` prevents duplicate instructors when several matching sections exist.

### Question 3

Find students who passed at least one course from every department.

The student’s query was correct, assuming `grade_100 >= 50` means passed.

Memory pattern:

```sql
GROUP BY student
HAVING COUNT(DISTINCT department_id) =
       (SELECT COUNT(*) FROM Department)
```

## Current question: Question 4

Question: Find the department(s) with the highest average salary for their instructors.

Current query:

```sql
SELECT TOP 1 d.department_id, d.department_name, AVG(i.salary) as average_salary
FROM Department d JOIN Instructor i
ON d.department_id = i.department_id
GROUP BY d.department_id, d.department_name
```

Diagnosis: the join and grouping are correct, but `TOP 1` without `ORDER BY` does not guarantee the department with the highest average. Also, `TOP 1` returns only one department even if departments tie.

Useful correction pattern:

```sql
TOP 1 WITH TIES
...
ORDER BY AVG(i.salary) DESC
```

Optional precision improvement in SQL Server: cast `salary` to a decimal before applying `AVG`, because `salary` is an integer.

## General SQL reminders

- `ON` defines how rows from two tables match.
- Column names do not need to match if the values represent the same entity.
- A self-join uses aliases to represent different rows of the same table.
- `GROUP BY` creates one result row per group.
- `HAVING` filters groups after aggregation.
- `WHERE` filters rows before grouping.
- `TOP` should normally be combined with `ORDER BY` when selecting highest or lowest values.
- Use `WITH TIES` when the question says department(s), student(s), or any wording that allows ties.
