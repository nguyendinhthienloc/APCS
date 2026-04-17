-- T3 fix
go
create or alter procedure DisplaySaleReport 
    @month int,
    @year int
as
begin
    set transaction isolation level repeatable read;
    begin transaction;

    declare @number_of_invoices int;
    declare @number_of_products int;
    declare @total_revenue decimal;
    declare @total_retail_revenue decimal;
    declare @total_profit decimal;
    declare @best_selling nvarchar(255);
    declare @slowest_selling nvarchar(255);
    
    if exists (
        select 1
        from orders O with (UPDLOCK) join orderdetails OD with (UPDLOCK) on O.orderNumber = OD.orderNumber
        where YEAR(orderDate) = @year and MONTH(orderDate) = @month
    )
    begin
        select @number_of_invoices = count(*)
        from orders O with (UPDLOCK) join orderdetails OD with (UPDLOCK) on O.orderNumber = OD.orderNumber
        where YEAR(orderDate) = @year and MONTH(orderDate) = @month
		waitfor delay '00:00:05'
        select @number_of_products = SUM(quantityOrdered), 
               @total_revenue = SUM(P.buyPrice * OD.quantityOrdered), 
               @total_retail_revenue = SUM(OD.priceEach * OD.quantityOrdered), 
               @total_profit = @total_retail_revenue - @total_revenue
        from orders O with (UPDLOCK)
            join orderdetails OD with (UPDLOCK) on O.orderNumber = OD.orderNumber
            join products P with (UPDLOCK) on P.productCode = OD.productCode
        where YEAR(orderDate) = @year and MONTH(orderDate) = @month 
          and O.status in ('Shipped', 'On Hold', 'In Process')

        select top 1 @best_selling = P.productName
        from orders O with (UPDLOCK)
            join orderdetails OD with (UPDLOCK) on O.orderNumber = OD.orderNumber
            join products P with (UPDLOCK) on P.productCode = OD.productCode
        where YEAR(orderDate) = @year
          and MONTH(orderDate) = @month
          and O.status in ('Shipped', 'On Hold', 'In Process')
        group by P.productCode, P.productName
        order by SUM(quantityOrdered) desc

        select top 1 @slowest_selling = P.productName
        from orders O with (UPDLOCK)
            join orderdetails OD with (UPDLOCK) on O.orderNumber = OD.orderNumber
            join products P with (UPDLOCK) on P.productCode = OD.productCode
        where YEAR(orderDate) = @year
          and MONTH(orderDate) = @month
          and O.status in ('Shipped', 'On Hold', 'In Process')
        group by P.productCode, P.productName
        order by SUM(quantityOrdered) asc

        print 'SALE REPORT IN MONTH ' + cast(@month as varchar(2)) + '/' + cast(@year as varchar(10));
        print 'Number of invoices: ' + cast(@number_of_invoices as varchar(10));
        print 'Number of products: ' + cast(@number_of_products as varchar(10));
        print 'Total revenue (factory price): ' + cast(@total_revenue as varchar(20));
        print 'Total retail revenue: ' + cast(@total_retail_revenue as varchar(20));
        print 'Total profit: ' + cast(@total_profit as varchar(20));

        if @total_profit <= 0
            print 'Status: {Loss}'
        else
            print 'Status: {Profit}'

        print 'Top 1 Best-selling product of the month: ' + @best_selling;
        print 'Top 1 Slowest-selling product of the month:' + @slowest_selling;
    end
    else
        print 'No invoices found.';
    
    commit transaction;
end;
go
