--22125096
--Đoàn Công Thành
--22TT2 - Monday class
create database Restaurant
go
use Restaurant
go

create table Menu(
	menuID varchar(5),	
	restaurantID varchar(5),
	mainDishID varchar(5) NULL

	constraint PK_menu primary key(menuID,restaurantID),
	constraint PK_menu_restaurant
)

create table Dish(
	dishID varchar(5),
	restaurantID varchar(5),
	menuID varchar(5),
	price decimal default(199)
	constraint PK_dish primary key (dishID,restaurantID)
)

create table Restaurant(
	restaurantID varchar(5),
	restauntrantName varchar(30),
	rating int,
	[location] varchar(30)

	constraint CK_rating check (rating >= 1 and rating <= 5),
	constraint PK_restaurant primary key (restaurantID),
	UNIQUE (restauntrantName, [location])

)

alter table Menu
add constraint FK_menu_restaurant
foreign key (restaurantID)
references Restaurant

alter table Dish
add constraint FK_dish_restaunt
foreign key (restaurantID)
references Restaurant

alter table Dish
add constraint FK_dish_menu
foreign key (menuID)
references Menu

insert into	Menu values
('1','001','ab'),
('2','002','cd'),
('3','003','ef')

insert into Dish values
('01','001','1'),
('02','002','2'),
('03','003','3')

insert into Restaurant values
('001','North',1,'N'),
('002','East',2,'E'),
('003','West',3,'W')