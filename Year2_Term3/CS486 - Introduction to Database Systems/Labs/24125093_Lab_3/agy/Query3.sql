USE University;
GO

-- 3. Create the TeachingCapacity table with necessary constraints (PK, FK, value-domain constraints)
IF OBJECT_ID('TeachingCapacity', 'U') IS NOT NULL
    DROP TABLE TeachingCapacity;
GO

CREATE TABLE TeachingCapacity (
    instructor_id VARCHAR(9) NOT NULL,
    course_id VARCHAR(9) NOT NULL,
    nb_year INT CHECK (nb_year > 0),
    
    PRIMARY KEY (instructor_id, course_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructor(instructor_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
GO