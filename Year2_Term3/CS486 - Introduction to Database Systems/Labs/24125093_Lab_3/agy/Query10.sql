USE University;
GO

-- 10. Create the StudentStatistics table with primary and foreign keys,
--     and populate it using data extracted from the existing database.

-- Drop the table if it already exists to allow re-running the script
IF OBJECT_ID('StudentStatistics', 'U') IS NOT NULL
    DROP TABLE StudentStatistics;
GO

-- Step 1: Create the table with necessary PK and FK constraints
CREATE TABLE StudentStatistics (
    student_id VARCHAR(9) NOT NULL,
    student_name NVARCHAR(50) NOT NULL,
    school_year INT NOT NULL,
    semester VARCHAR(9) NOT NULL,
    nb_credits INT NOT NULL,
    
    PRIMARY KEY (student_id, school_year, semester),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
);
GO

-- Step 2: Populate the table using data extracted from existing tables
-- We join Student, GradeReport (enrollment records), Section, and Course 
-- to sum up the course credits for each student in each semester/school year.
INSERT INTO StudentStatistics (student_id, student_name, school_year, semester, nb_credits)
SELECT 
    s.student_id,
    s.student_name,
    sec.school_year,
    sec.semester,
    SUM(c.credit) AS nb_credits
FROM Student s
JOIN GradeReport gr ON s.student_id = gr.student_id
JOIN Section sec ON gr.section_id = sec.section_id
JOIN Course c ON sec.course_id = c.course_id
GROUP BY s.student_id, s.student_name, sec.school_year, sec.semester;
GO

-- Verify the populated statistics
SELECT * FROM StudentStatistics;
GO
