create table data(
	name varchar(80) primary key,
	json varchar(9999999)
);

create table log(
	date timestamp,
	text varchar (9999999),
	is_new boolean
);
