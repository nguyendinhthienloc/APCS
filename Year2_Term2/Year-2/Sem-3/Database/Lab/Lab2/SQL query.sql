--Lab02
--tạo csdl
create database CarModeldb
go
use CarModeldb
go
--tạo các bảng: thuộc tính, khoá chính, rb:unique
create table employee(
employeeNumber varchar(5),
lastName nvarchar(30),
firstName nvarchar(30),
extension varchar(10),
email varchar(3),
officeCode varchar(5),
reportsTo varchar(5),
jobTitle nvarchar(50)
constraint PK_employee primary key(employeeNumber)
)

--chỉnh sửa bảng
--alter table customers
--xoá constraint
--drop constraint PK_customers
--add constraint PK_customers primary key(employeeNumber)

create table customers(
customerNumber int,
customerName varchar(50) NOT NULL,
contactLastName varchar(50),
contactFirstName  varchar(50),
phone varchar(50),
addressLine1 varchar(50),
addressLine2 varchar(50),
city varchar(50),
[state] varchar(50),
postalCode varchar(5),
country varchar(50),
salesRepEmployeeNumber int,
creditLimit decimal
constraint PK_customers primary key(customerNumber)
)

create table payments(
customerNumber int,
checkNumber varchar(50),
paymentDate date,
amount decimal default(0)
constraint PK_payments primary key(customerNumber,checkNumber)
)

create table orders(
orderNumber int,
orderDate date,
requiredDate date,
shippedDate date,
[status] varchar(15),
comments nvarchar(100),
customerNumber int
constraint PK_orders primary key(orderNumber),
constraint CK_Date CHECK (orderDate < shippedDate),
constraint CK_Status CHECK ([status] in ('Cancelled','Disputed','Process','Hold',
'Resolved','Shipped'))
)

--tạo khoá ngoại
--FK_oders_customers(customerNumber) -> Customers
alter table orders
add constraint FK_orders_customers
foreign key (customerNumber)
references customers
--nhập dữ liệu
insert into customers (customerNumber,customerName,creditLimit)
values(1,'Xuan Thanh',2)
--cập nhật dữ liệu
update customers set phone = '1234'
where customerNumber = 1