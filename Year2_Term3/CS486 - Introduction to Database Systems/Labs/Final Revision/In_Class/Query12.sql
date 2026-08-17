/*
QUESTION 12 - TRANSACTIONS AND CONCURRENCY
==========================================
Assume all concurrent calls use the same (student_id, section_id).
SQL Server uses READ COMMITTED by default.

Problems in the original procedures:
1. ReadGradeTwice had no explicit transaction. Its two SELECT statements were
   separate autocommit transactions, so an UPDATE or DELETE could commit during
   the ten-second delay and make the second result different from the first.
2. The writer procedures had no TRY/CATCH or SET XACT_ABORT ON.
3. Each existence check and its later modification must be one atomic unit.
*/

/*
Procedure 9
-----------
REPEATABLE READ retains a shared lock on an existing grade row until COMMIT.
A concurrent UPDATE or DELETE of that row must therefore wait until both reads
have finished. Use SERIALIZABLE instead if an initially absent row must also
remain absent; SERIALIZABLE protects the relevant key range.

Setting the isolation level without BEGIN TRANSACTION would not solve the
problem because each SELECT would still be a separate transaction.
*/
GO
CREATE OR ALTER PROCEDURE ReadGradeTwice
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- The shared lock acquired here is retained until COMMIT.
        SELECT grade_100, grade_ABC
        FROM GRADEREPORT
        WHERE student_id = @student_id
          AND section_id = @section_id;

        WAITFOR DELAY '00:00:10';

        -- An existing row has the same values as in the first SELECT.
        SELECT grade_100, grade_ABC
        FROM GRADEREPORT
        WHERE student_id = @student_id
          AND section_id = @section_id;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

/*
Procedure 10
------------
The STUDENT and SECTION checks and the DELETE form one transaction. If either
parent row is absent, the transaction is rolled back as required.

The question only requires the parent rows to be validated. If both parents
exist but their GRADEREPORT row does not, DELETE affects zero rows and commits.
*/
CREATE OR ALTER PROCEDURE DeleteStudentGrade
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    BEGIN TRY
        BEGIN TRANSACTION;

        IF NOT EXISTS
        (
            SELECT 1
            FROM STUDENT
            WHERE student_id = @student_id
        )
        OR NOT EXISTS
        (
            SELECT 1
            FROM SECTION
            WHERE section_id = @section_id
        )
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END;

        DELETE FROM GRADEREPORT
        WHERE student_id = @student_id
          AND section_id = @section_id;

        DECLARE @deleted_rows INT = @@ROWCOUNT;

        COMMIT TRANSACTION;

        -- 1 means deleted; 0 means that no matching grade existed.
        SELECT @deleted_rows AS deleted_rows;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

/*
Procedure 11
------------
The UPDATE expression is atomic. SQL Server takes an exclusive lock on the
row. If two calls multiply the same grade, one waits; the second call then
multiplies the first call's committed result. For example:

    80 * 1.1 * 1.1

There is no lost update because the calculation is performed directly by one
UPDATE statement. A SELECT followed by UPDATE grade_100 = @calculated_value
would be more vulnerable to a lost update.

Question 11 says to commit even when an ID does not exist. Therefore, this
procedure performs no UPDATE in that case but still commits the transaction.
*/
CREATE OR ALTER PROCEDURE MultiplyStudentGrade
    @student_id VARCHAR(20),
    @section_id INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @updated_rows INT = 0;

        IF EXISTS
        (
            SELECT 1
            FROM STUDENT
            WHERE student_id = @student_id
        )
        AND EXISTS
        (
            SELECT 1
            FROM SECTION
            WHERE section_id = @section_id
        )
        BEGIN
            UPDATE GRADEREPORT
            SET grade_100 = grade_100 * 1.1
            WHERE student_id = @student_id
              AND section_id = @section_id;

            SET @updated_rows = @@ROWCOUNT;
        END;

        COMMIT TRANSACTION;

        -- 1 means updated; 0 means that no matching grade was updated.
        SELECT @updated_rows AS updated_rows;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

/*
WHAT HAPPENS WHEN THE PROCEDURES RUN CONCURRENTLY?
==================================================

A. ReadGradeTwice + MultiplyStudentGrade
----------------------------------------
With the original READ COMMITTED implementation, this schedule was possible:

    1. ReadGradeTwice reads 80.
    2. MultiplyStudentGrade changes 80 to 88 and commits.
    3. ReadGradeTwice reads 88.

This is a non-repeatable read. In the implementation above, REPEATABLE READ
retains the reader's shared lock. MultiplyStudentGrade waits for the reader to
perform its second SELECT and commit.

B. ReadGradeTwice + DeleteStudentGrade
--------------------------------------
With the original READ COMMITTED implementation, the first SELECT could return
a grade and the second could return no row after a concurrent DELETE. This is
also a non-repeatable read. It is not normally called a phantom here because
one identified row, rather than a changing range of rows, is being reread.

With the implementation above, DeleteStudentGrade waits for ReadGradeTwice to
perform its second SELECT and commit.

C. MultiplyStudentGrade + DeleteStudentGrade
--------------------------------------------
Both need an exclusive lock on the same GRADEREPORT row, so SQL Server
serializes them:

    - Multiply first: the grade is changed and committed; DELETE then removes
      the updated row.
    - Delete first: the row is removed and committed; Multiply then updates
      zero rows and commits because STUDENT and SECTION still exist.

In either successful ordering, the final GRADEREPORT row is absent. The only
difference is whether the multiplication occurs temporarily before deletion.

D. All three procedures
-----------------------
With the original code, one possible schedule was:

    1. ReadGradeTwice reads 80.
    2. MultiplyStudentGrade changes 80 to 88 and commits.
    3. DeleteStudentGrade deletes the row and commits.
    4. ReadGradeTwice performs its second SELECT and returns no row.

Depending on timing, the original second SELECT could return 80, 88, or no
row. With the procedures above, the reader holds its shared lock for both
reads. Both writers wait. After the reader commits, DELETE and UPDATE obtain
exclusive access one at a time, following one of the serial orderings in C.

The procedures access STUDENT, SECTION, and GRADEREPORT in the same order,
which reduces deadlock risk. Blocking is expected and is not itself an error.
*/

/*
CONCURRENCY PHENOMENA AT EACH ISOLATION LEVEL
=============================================

1. READ UNCOMMITTED
   - Allows dirty reads, non-repeatable reads, and phantom reads.
   - The reader might observe an uncommitted multiplication or deletion that
     is later rolled back.
   - Writers still use exclusive locks, so SQL Server prevents dirty writes.

2. READ COMMITTED (default)
   - Prevents dirty reads.
   - Allows non-repeatable reads because a SELECT normally releases its shared
     lock when the statement finishes.
   - Allows phantom reads for range queries.
   - A reader waits while a writer has an incompatible lock.

3. REPEATABLE READ
   - Prevents dirty and non-repeatable reads.
   - Retains shared locks on rows read until COMMIT.
   - Still allows phantom rows for range queries.
   - Here, UPDATE and DELETE of an existing grade wait for ReadGradeTwice.

4. SERIALIZABLE
   - Prevents dirty, non-repeatable, and phantom reads.
   - Key-range locks also protect the result when the requested row is absent.
   - Provides the strongest locking consistency, but causes more blocking and
     may increase the chance of deadlocks.

5. SNAPSHOT
   - Reads a transaction-level, consistent committed version of the database.
   - Prevents dirty, non-repeatable, and phantom reads without blocking writers.
   - Two writers changing the same row can cause an update-conflict error; the
     failed transaction should be retried.
   - ALLOW_SNAPSHOT_ISOLATION must first be enabled for the database.

6. READ_COMMITTED_SNAPSHOT (RCSI)
   - Is not the same as transaction-level SNAPSHOT.
   - Each statement normally receives its own committed snapshot, so two
     SELECT statements may still differ if another transaction commits between them.
*/

/*
OPTIONAL NON-BLOCKING SOLUTION FOR PROCEDURE 9
==============================================
An administrator can enable SNAPSHOT isolation once:

    ALTER DATABASE University_DB SET ALLOW_SNAPSHOT_ISOLATION ON;

ReadGradeTwice can then use this transaction structure:

    SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
    BEGIN TRANSACTION;
    -- First SELECT
    -- WAITFOR DELAY '00:00:10'
    -- Second SELECT
    COMMIT TRANSACTION;

Both SELECT statements see the same committed snapshot, while DELETE and
UPDATE can proceed without waiting for the ten-second delay. This is preferable
when a stable historical view is acceptable and writer blocking is undesirable.
*/

/*
HANDLING SUMMARY
================
1. Put logically related statements inside one explicit transaction.
2. Use TRY/CATCH and SET XACT_ABORT ON; roll back when an error occurs.
3. Use REPEATABLE READ or SERIALIZABLE when both reads must match and writer
   blocking is acceptable.
4. Use transaction-level SNAPSHOT for consistent non-blocking reads when it is
   enabled for the database.
5. Keep transactions short. WAITFOR deliberately makes Procedure 9 long, so
   blocking under locking isolation is expected.
6. Use one atomic UPDATE expression to avoid lost updates.
7. Check @@ROWCOUNT so the caller knows whether a row was modified.
8. Access tables in a consistent order and retry a transaction if SQL Server
   chooses it as a deadlock victim or reports a snapshot update conflict.
*/

