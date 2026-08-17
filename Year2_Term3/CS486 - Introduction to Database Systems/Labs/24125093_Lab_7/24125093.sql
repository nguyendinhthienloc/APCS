-- Student ID: 24125093
-- Full name: Nguyen Dinh Thien Loc
-- CS486 - Lab 7: Transactions and Isolation Levels

USE University;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetDepartmentPayrollSummary
    @DepartmentID varchar(5)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT
            d.department_name,
            COUNT(i.instructor_id) AS NumberOfInstructors,
            COALESCE(SUM(CONVERT(bigint, i.salary)), 0) AS TotalSalary
        FROM dbo.Department AS d
        LEFT JOIN dbo.Instructor AS i
            ON i.department_id = d.department_id
        WHERE d.department_id = @DepartmentID
        GROUP BY d.department_name;

        IF @@ROWCOUNT = 0
            THROW 50001, 'Department does not exist. Transaction rolled back.', 1;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_AdjustInstructorSalary
    @InstructorID varchar(9),
    @NewSalary int
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        IF @NewSalary IS NULL OR @NewSalary <= 0
            THROW 50002, 'NewSalary must be greater than zero. Transaction rolled back.', 1;

        UPDATE dbo.Instructor
        SET salary = @NewSalary
        WHERE instructor_id = @InstructorID;

        IF @@ROWCOUNT = 0
            THROW 50003, 'Instructor does not exist. Transaction rolled back.', 1;

        COMMIT TRANSACTION;

        SELECT
            N'COMMIT' AS TransactionResult,
            @InstructorID AS instructor_id,
            @NewSalary AS salary;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_AddNewInstructor
    @InstructorID varchar(9),
    @InstructorName nvarchar(50),
    @Phone nvarchar(9),
    @DepartmentID varchar(5),
    @Salary int
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        IF @Salary IS NULL OR @Salary <= 0
            THROW 50004, 'Salary must be greater than zero. Transaction rolled back.', 1;

        -- A direct INSERT is atomic. The primary key is the concurrency-safe
        -- existence check, so no SELECT lock hint is needed.
        INSERT INTO dbo.Instructor
            (instructor_id, instructor_name, phone, department_id, salary)
        VALUES
            (@InstructorID, @InstructorName, @Phone, @DepartmentID, @Salary);

        COMMIT TRANSACTION;

        SELECT
            N'COMMIT' AS TransactionResult,
            @InstructorID AS instructor_id;
    END TRY
    BEGIN CATCH
        DECLARE @ErrorNumber int = ERROR_NUMBER();

        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        IF @ErrorNumber IN (2601, 2627)
            THROW 50005, 'Instructor already exists. Transaction rolled back.', 1;

        THROW;
    END CATCH;
END;
GO

-- Example calls (kept commented so running the complete file only installs
-- the procedures and never changes the supplied University data):
-- EXEC dbo.usp_GetDepartmentPayrollSummary @DepartmentID = 'CS';
-- EXEC dbo.usp_AdjustInstructorSalary @InstructorID = 'I001', @NewSalary = 1200;
-- EXEC dbo.usp_AddNewInstructor
--     @InstructorID = 'I013', @InstructorName = N'New Instructor',
--     @Phone = N'090000000', @DepartmentID = 'CS', @Salary = 1800;
