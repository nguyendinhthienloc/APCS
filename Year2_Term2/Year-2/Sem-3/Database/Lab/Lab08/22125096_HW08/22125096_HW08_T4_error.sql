
-- Create transaction T4
	go
	create or alter procedure DeleteProductFromInvoice
	@order_number int,
	@product_code varchar(15)
	as
	begin
		begin transaction;
		declare @status varchar(50);
		if exists (
				select 1
				from orders O join orderdetails OD on O.orderNumber = OD.orderNumber
				where O.orderNumber = @order_number
					and OD.productCode = @product_code
			)
				begin
					select @status = O.status
					from orders O	
					where O.orderNumber = @order_number
				end
				if @status = 'Shipped'
					begin
						print 'Deletion is not allowed as the invoice status is "Shipped".';
						return;
					end
				if @status = 'In Process'
					begin
						delete from orderdetails
						where orderNumber = @order_number
							and productCode = @product_code
							waitfor delay '00:00:05'
						update orders
						set status = 'Resolved',
							comments = isnull(comments, '') + ' The customer requested to cancel one product in this order, and it has been resolved.'
						where orderNumber = @order_number
					end
		else
			print 'No invoices found.';
		commit transaction;
	end;
	go

	-- Test transaction T4
exec DeleteProductFromInvoice @order_number = 10425, @product_code = S50_1392