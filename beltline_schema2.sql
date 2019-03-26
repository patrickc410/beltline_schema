DROP DATABASE IF EXISTS beltline;
CREATE DATABASE beltline;
USE beltline;




DROP TABLE IF EXISTS user;
CREATE TABLE user (
    username varchar(20) PRIMARY KEY,
    user_type ENUM('Visitor','Employee','Both'),
    fname varchar(20),
    lname varchar(20),
    status ENUM('Approved', 'Declined', 'Pending') DEFAULT 'Pending',
    password varchar(20)
);


INSERT INTO user VALUES
    ('user1', 'Visitor', 'Patrick', 'Crawford', 'Declined', 'password1'),
    ('user2', 'Employee', 'Madison', 'Smith', 'Approved', 'password2'),
    ('user3', 'Both', 'Lauren', 'Johnson', 'Approved', 'password3'),
    ('user4', 'Visitor', 'Katie', 'Neil', 'Pending', 'password4'),
    ('user5', 'Both', 'Abbey', 'Nannis', 'Approved', 'password5');




DROP TABLE IF EXISTS email;
CREATE TABLE email (
    username varchar(20),
    email varchar(100),
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
    employeeID decimal(10,0) PRIMARY KEY,
    username varchar(20) UNIQUE KEY,
    phone decimal(10,0),
    address varchar(40),
    city varchar(20),
    state varchar(15),
    zipcode int(9),
    employee_type ENUM('Administrator','Staff','Manager'),
    CONSTRAINT employee_fk1 FOREIGN KEY (username) REFERENCES user(username) ON UPDATE CASCADE ON DELETE CASCADE
);


INSERT INTO employee VALUES
    (1, 'user2', 6789998212, '123 Address Lane', 'Atlanta', 'GA', 30030, 'Staff'),
    (2, 'user3', 4040001111, '456 Address Street', 'Dallas', 'TX', 300309212, 'Manager'),
    (3, 'user4', 7701112222, '789 Address Way', 'New York City', 'NY', 300309212, 'Administrator');



DROP TABLE IF EXISTS site;
CREATE TABLE site (
    name varchar(40) PRIMARY KEY,
    address varchar(40),
    zipcode decimal(9,0),
    openeveryday ENUM('Yes','No'),
    managerID decimal(10,0),
    CONSTRAINT site_fk1 FOREIGN KEY (managerID) REFERENCES employee (employeeID)
);

INSERT INTO site VALUES
    ('site1', '111 Site1 Way', 300309999, 'Yes', 0000000002),
    ('site2', '222 Site2 Way', 300309999, 'No', 0000000002),
    ('site3', '333 Site3 Way', 300309999, 'Yes', 0000000002);




DROP TABLE IF EXISTS transit;
CREATE TABLE transit (
    type varchar(20),
    route varchar(20),
    price decimal(3,2),
    PRIMARY KEY (type, route)
);





DROP TABLE IF EXISTS event;
CREATE TABLE event (
    name varchar(40),
    start_date date,
    site_name varchar(40),
    description varchar(100),
    min_staff_req decimal(4,0),
    capacity decimal(5,0),
    price decimal(3,2),
    end_date date,
    PRIMARY KEY (name, start_date, site_name),
    CONSTRAINT event_fk1 FOREIGN KEY (site_name) REFERENCES site (name) ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS take_transit;
CREATE TABLE take_transit (
    username varchar(20),
    transit_type varchar(20),
    route varchar(20),
    take_date date,
    PRIMARY KEY (username, transit_type, route, take_date),
    CONSTRAINT take_transit_fk1 FOREIGN KEY (username) REFERENCES user (username) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT take_transit_fk2 FOREIGN KEY (transit_type, route) REFERENCES transit (type, route) ON UPDATE CASCADE ON DELETE CASCADE
);


DROP TABLE IF EXISTS visit_site;
CREATE TABLE visit_site (
    username varchar(20),
    site_name varchar(40),
    visit_date date,
    PRIMARY KEY (username, site_name, visit_date),
    CONSTRAINT visit_site_fk1 FOREIGN KEY (username) REFERENCES user (username) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT visit_site_fk2 FOREIGN KEY (site_name) REFERENCES site (name) ON UPDATE CASCADE ON DELETE CASCADE
);





DROP TABLE IF EXISTS visit_event;
CREATE TABLE visit_event (
    username varchar(20),
    event_name varchar(40),
    start_date date,
    site_name varchar(40),
    visit_date char(10),
    PRIMARY KEY (username, event_name, start_date, site_name, visit_date),
    CONSTRAINT visit_event_fk1 FOREIGN KEY (username) REFERENCES user (username),
    CONSTRAINT visit_event_fk2 FOREIGN KEY (event_name, start_date, site_name) REFERENCES event (name, start_date, site_name)
);





DROP TABLE IF EXISTS transit_connections;
CREATE TABLE transit_connections (
    site_name varchar(40),
    transit_type varchar(20),
    route varchar(20),
    PRIMARY KEY (site_name, transit_type, route),
    CONSTRAINT transit_connections_fk1 FOREIGN KEY (site_name) REFERENCES site (name),
    CONSTRAINT transit_connections_fk2 FOREIGN KEY (transit_type, route) REFERENCES transit (type, route)
);





DROP TABLE IF EXISTS event_staff_assignments;
CREATE TABLE event_staff_assignments (
    employeeID decimal(10,0),
    event_name varchar(40),
    start_date date,
    site_name varchar(40),
    PRIMARY KEY (employeeID, event_name, start_date, site_name),
    CONSTRAINT event_staff_assignments_fk1 FOREIGN KEY (employeeID) REFERENCES employee (employeeID),
    CONSTRAINT event_staff_assignments_fk2 FOREIGN KEY (event_name, start_date, site_name) REFERENCES event (name, start_date, site_name)
);
