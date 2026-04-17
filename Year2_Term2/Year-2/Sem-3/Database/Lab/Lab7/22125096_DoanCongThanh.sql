-- BR1: For each order, the OrderDate must always be before the shippedDate.

-- Table of influence
----		insert delete update
-- orders	  +       -		+(OrderDate,ShippedDate)

create or alter trigger UpdateOrderDate
on orders
for update,insert
as
begin
		if exists(
		select 1
		from inserted
		where OrderDate >= ShippedDate)
		begin
			raiserror ('OrderDate must be before ShippedDate.', 16, 1);
			rollback transaction;
		end
end
go

insert into Orders (orderNumber, OrderDate, requiredDate, ShippedDate, status, customerNumber) 
values (2, '2023-01-02', '2023-01-01', '2023-01-01', 'Shipped','103');

-- BR2: The value of totalAmount for each order must always be equal to the sum of the order details
-- of the corresponding orderID.

-- Table of influence
----			insert	delete	update
-- orders		  +		  -		+(totalAmount)
-- orderdetails	  +		  +		+(quantityOrdered,priceEach)
alter table orders
add totalAmount decimal(10, 2);

go
create or alter trigger UpdateOrderdetails
on orderdetails
after insert, update, delete
as
begin

    declare @affected_orders table (orderid int);

    insert into @affected_orders (orderid)
    select distinct orderNumber
    from inserted;

    insert into @affected_orders (orderid)
    select distinct orderNumber
    from deleted;

    update orders
    set totalAmount = (
        select sum(quantityordered * priceeach)
        from orderdetails
        where orderdetails.orderLineNumber = orders.orderNumber
    )
    where orders.orderNumber in (select orderid from @affected_orders);
end;
go

create trigger UpdateTotalAmount
on orders
after insert, update
as
begin
    declare @affected_orders table (orderNumber int);

    insert into @affected_orders (orderNumber)
    select distinct orderNumber
    from inserted;

    if exists (
        select 1
        from orders o
        join @affected_orders ao on o.orderNumber = ao.orderNumber
        join (
            select orderNumber, sum(quantityordered * priceeach) as calculated_total
            from orderdetails
            group by orderNumber
        ) od on o.orderNumber = od.orderNumber
        where o.totalAmount <> od.calculated_total
    )
    begin
        -- Raise an error if the totalAmount does not match
        raiserror ('TotalAmount must be equal to the sum of the order details.', 16, 1);
        rollback transaction;
    end
end;

-- BR3: An employee can only report to another employee who is located in the same office

-- Table of influence
----			insert	delete	update
-- employess	  +       -     +(reportsTo,officeCode)
go
create trigger UpdateEmployee
on employees
after insert, update
as
begin
    -- Check if the reporting employee is in the same office as the employee being inserted or updated
    if exists (
        select 1
        from employees e
        join inserted i on e.employeeNumber = i.reportsTo
        where i.officeCode <> e.officeCode
    )
    begin
        -- Raise an error if the reporting employee is not in the same office
        raiserror ('An employee can only report to another employee who is located in the same office.', 16, 1);
        rollback transaction;
    end
end;
