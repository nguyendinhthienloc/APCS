USE University_DB;
GO

DISABLE TRIGGER head_department ON Department;
GO

BEGIN TRY
    UPDATE Department
    SET department_head = 'I001'
    WHERE department_id IN ('CS', 'SE');
END TRY
BEGIN CATCH
    PRINT ERROR_MESSAGE();
END CATCH;
GO

ENABLE TRIGGER head_department ON Department;
GO