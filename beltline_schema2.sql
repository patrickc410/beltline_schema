DROP DATABASE IF EXISTS beltline;
CREATE DATABASE beltline;
USE beltline;




DROP TABLE IF EXISTS user;
CREATE TABLE user (
    username varchar(20) PRIMARY KEY,
    user_type ENUM('User','Visitor','Employee') NOT NULL,
    fname varchar(20) NOT NULL,
    lname varchar(20) NOT NULL,
    status ENUM('Approved', 'Declined', 'Pending') DEFAULT 'Pending',
    password varchar(20) NOT NULL
);


INSERT INTO user VALUES
    ('user1', 'Visitor', 'Patrick', 'Crawford', 'Declined', 'password1'),
    ('user2', 'Employee', 'Madison', 'Smith', 'Approved', 'password2'),
    ('user3', 'User', 'Lauren', 'Johnson', 'Approved', 'password3'),
    ('user4', 'Visitor', 'Katie', 'Neil', 'Pending', 'password4'),
    ('user5', 'User', 'Abbey', 'Nannis', 'Approved', 'password5');




DROP TABLE IF EXISTS email;
CREATE TABLE email (
    username varchar(20),
    email varchar(100) NOT NULL,
    PRIMARY KEY (username, email),
    CONSTRAINT email_fk1 FOREIGN KEY (username) REFERENCES user(username) ON UPDATE CASCADE ON DELETE CASCADE
);


INSERT INTO email VALUES
    ('user1', 'user1_email1_@gmail.com'),
    ('user2', 'user2_email1_@aol.com'),
    ('user2', 'user2_email2_@aol.com'),
    ('user3', 'user3_email1_@bellsouth.net'),
    ('user3', 'user3_email2_@bellsouth.net'),
    ('user3', 'user3_email3_@bellsouth.net'),
    ('user4', 'user4_email1_@yahoo.com'),
    ('user4', 'user4_email2_@yahoo.com'),
    ('user4', 'user4_email3_@yahoo.com'),
    ('user4', 'user4_email4_@yahoo.com'),
    ('user5', 'user5_email1_@icloud.com'),
    ('user5', 'user5_email2_@icloud.com'),
    ('user5', 'user5_email3_@icloud.com'),
    ('user5', 'user5_email4_@icloud.com'),
    ('user5', 'user5_email5_@icloud.com');



DROP TABLE IF EXISTS employee;
CREATE TABLE employee (
    employeeID int AUTO_INCREMENT,
    username varchar(20) UNIQUE KEY NOT NULL,
    phone decimal(10,0) UNIQUE KEY NOT NULL,
    address varchar(40) NOT NULL,
    city varchar(20) NOT NULL,
    state varchar(15) NOT NULL,
    zipcode int(9) NOT NULL,
    employee_type ENUM('Administrator','Staff','Manager') NOT NULL,
    PRIMARY KEY(employeeID),
    CONSTRAINT employee_fk1 FOREIGN KEY (username) REFERENCES user(username) ON UPDATE CASCADE ON DELETE CASCADE
);

ALTER TABLE employee AUTO_INCREMENT = 100000000;

CREATE TABLE visitor_list (
    username varchar(20) PRIMARY KEY,
    CONSTRAINT visitor_list_fk1 FOREIGN KEY (username) REFERENCES user(username)
);
-- we created the visitor_list table to hold all of the visitor ands and employee-visitors,
-- so when a visitor is deleted or employee-visitor returns to a plain employee status,
-- they will be deleted from this table, and consquently, all of their associated history will be deleted, too
INSERT INTO employee(username,phone,address,city,state,zipcode,employee_type) VALUES
    ('user2', 6789998212, '123 Address Lane', 'Atlanta', 'GA', 30030, 'Staff'),
    ('user3', 4040001111, '456 Address Street', 'Dallas', 'TX', 300309212, 'Manager'),
    ('user4', 7701112222,'', 'New York City', 'NY', 300309212, 'Administrator');



DROP TABLE IF EXISTS site;
CREATE TABLE site (
    name varchar(40) PRIMARY KEY,
    address varchar(40),
    zipcode int(5) NOT NULL,
    openeveryday ENUM('Yes','No') NOT NULL,
    managerID int NOT NULL,
    CONSTRAINT site_fk1 FOREIGN KEY (managerID) REFERENCES employee (employeeID) ON UPDATE CASCADE ON DELETE RESTRICT
);

INSERT INTO site VALUES
    ('site1', '111 Site1 Way', 300309999, 'Yes', 100000002),
    ('site2', '222 Site2 Way', 300309999, 'No', 100000002),
    ('site3', '333 Site3 Way', 300309999, 'Yes', 100000002);




DROP TABLE IF EXISTS transit;
CREATE TABLE transit (
    type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    price decimal(3,2) NOT NULL,
    connected_sites int(2) NOT NULL,
    PRIMARY KEY (type, route)
);
INSERT INTO transit VALUES
    ('MARTA',816, 4.30,4);



DROP TABLE IF EXISTS event;
CREATE TABLE event (
    name varchar(40) NOT NULL,
    start_date date NOT NULL,
    site_name varchar(40) NOT NULL,
    description varchar(500),
    min_staff_req int NOT NULL,
    capacity int NOT NULL,
    price decimal(4,2) NOT NULL,
    end_date date NOT NULL,
    PRIMARY KEY (name, start_date, site_name),
    CONSTRAINT event_fk1 FOREIGN KEY (site_name) REFERENCES site (name) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO event VALUES
    ('ice cream','2014-02-04','site1','fjdk',304,4,23.4,'2018-03-23');


DROP TABLE IF EXISTS take_transit;
CREATE TABLE take_transit (
    username varchar(20) NOT NULL,
    transit_type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    take_date date NOT NULL,
    PRIMARY KEY (username, transit_type, route, take_date),
    CONSTRAINT take_transit_fk1 FOREIGN KEY (username) REFERENCES user (username) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT take_transit_fk2 FOREIGN KEY (transit_type, route) REFERENCES transit (type, route) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO take_transit VALUES
    ('user1','MARTA',816,'1999-04-14');


DROP TABLE IF EXISTS visit_site;
CREATE TABLE visit_site (
    username varchar(20) NOT NULL,
    site_name varchar(40) NOT NULL,
    visit_date date NOT NULL,
    PRIMARY KEY (username, site_name, visit_date),
    CONSTRAINT visit_site_fk1 FOREIGN KEY (username) REFERENCES user (username) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT visit_site_fk2 FOREIGN KEY (site_name) REFERENCES site (name) ON UPDATE CASCADE ON DELETE CASCADE
);





DROP TABLE IF EXISTS visit_event;
CREATE TABLE visit_event (
    username varchar(20) NOT NULL,
    event_name varchar(40) NOT NULL,
    start_date date NOT NULL,
    site_name varchar(40) NOT NULL,
    visit_date date NOT NULL,
    PRIMARY KEY (username, event_name, start_date, site_name, visit_date),
    CONSTRAINT visit_event_fk1 FOREIGN KEY (username) REFERENCES user (username) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT visit_event_fk2 FOREIGN KEY (event_name, start_date, site_name) REFERENCES event (name, start_date, site_name) ON UPDATE CASCADE ON DELETE CASCADE
);





DROP TABLE IF EXISTS transit_connections;
CREATE TABLE transit_connections (
    site_name varchar(40) NOT NULL,
    transit_type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    PRIMARY KEY (site_name, transit_type, route),
    CONSTRAINT transit_connections_fk1 FOREIGN KEY (site_name) REFERENCES site (name) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT transit_connections_fk2 FOREIGN KEY (transit_type, route) REFERENCES transit (type, route) ON UPDATE CASCADE ON DELETE CASCADE
);





DROP TABLE IF EXISTS event_staff_assignments;
CREATE TABLE event_staff_assignments (
    employeeID int NOT NULL,
    event_name varchar(40) NOT NULL,
    start_date date NOT NULL,
    site_name varchar(40) NOT NULL,
    PRIMARY KEY (employeeID, event_name, start_date, site_name),
    CONSTRAINT event_staff_assignments_fk1 FOREIGN KEY (employeeID) REFERENCES employee (employeeID) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT event_staff_assignments_fk2 FOREIGN KEY (event_name, start_date, site_name) REFERENCES event (name, start_date, site_name) ON UPDATE CASCADE ON DELETE CASCADE
);
