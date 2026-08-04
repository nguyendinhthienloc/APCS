USE University
DROP TRIGGER IF EXISTS _1_head_1_deparment
GO
CREATE TRIGGER _1_head_1_deparment
ON Department
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT d.department_head
        FROM Department d 
        GROUP BY 
            d.department_head
        HAVING COUNT(d.department_head) > 1
            
    )
    BEGIN
    RAISERROR(
        'An instructor cannot be the head of more than 1 department(s)', 16, 1
    )
    ROLLBACK;

    END

END;