DROP DATABASE IF EXISTS beltline;
CREATE DATABASE beltline;
USE beltline;

-- SET NAMES utf8; -- what is this?



DROP TABLE IF EXISTS user;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE user (
    username varchar(20) PRIMARY KEY,
    fname varchar(20),
    lname varchar(20),
    status ENUM('Administrator','Staff','Manager'),
    password varchar(20)
);



DROP TABLE IF EXISTS email;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE email (
    username varchar(20),
    email varchar(100),
    PRIMARY KEY (username, email),
    CONSTRAINT email_fk1 FOREIGN KEY (username) REFERENCES user(username)
);


DROP TABLE IF EXISTS employee;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE employee (
    employeeID decimal(10,0) PRIMARY KEY,
    username varchar(20) UNIQUE KEY,
    phone decimal(10,0),
    address varchar(40),
    city varchar(20),
    state varchar(15),
    zipcode int(9),
    CONSTRAINT employee_fk1 FOREIGN KEY (username) REFERENCES user(username)
);



DROP TABLE IF EXISTS site;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE site (
    name varchar(40) PRIMARY KEY,
    address varchar(40),
    zipcode decimal(9,0),
    openeveryday ENUM('Yes','No'),
    managerID decimal(10,0),
    CONSTRAINT site_fk1 FOREIGN KEY (managerID) REFERENCES employee (employeeID)
);





DROP TABLE IF EXISTS transit;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE transit (
    type varchar(20),
    route varchar(20),
    price decimal(3,2),
    PRIMARY KEY (type, route)
);



DROP TABLE IF EXISTS event;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE event (
    name varchar(40),
    start_date char(10),
    site_name varchar(40),
    description varchar(100),
    min_staff_req decimal(4,0),
    capacity decimal(5,0),
    price decimal(3,2),
    end_date char(10),
    PRIMARY KEY (name, start_date, site_name),
    CONSTRAINT event_fk1 FOREIGN KEY (site_name) REFERENCES site (name)
);



DROP TABLE IF EXISTS take_transit;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE take_transit (
    username varchar(20),
    transit_type varchar(20),
    route varchar(20),
    take_date char(10),
    PRIMARY KEY (username, transit_type, route, take_date),
    CONSTRAINT take_transit_fk1 FOREIGN KEY (username) REFERENCES user (username),
    CONSTRAINT take_transit_fk2 FOREIGN KEY (transit_type, route) REFERENCES transit (type, route)
);


DROP TABLE IF EXISTS visit_site;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE visit_site (
    username varchar(20),
    site_name varchar(40),
    visit_date char(10),
    PRIMARY KEY (username, site_name, visit_date),
    CONSTRAINT visit_site_fk1 FOREIGN KEY (username) REFERENCES user (username),
    CONSTRAINT visit_site_fk2 FOREIGN KEY (site_name) REFERENCES site (name)
);





DROP TABLE IF EXISTS visit_event;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE visit_event (
    username varchar(20),
    event_name varchar(40),
    start_date char(10),
    site_name varchar(40),
    visit_date char(10),
    PRIMARY KEY (username, event_name, start_date, site_name, visit_date),
    CONSTRAINT visit_event_fk1 FOREIGN KEY (username) REFERENCES user (username),
    CONSTRAINT visit_event_fk2 FOREIGN KEY (event_name, start_date) REFERENCES event (name, start_date),
    CONSTRAINT visit_event_fk3 FOREIGN KEY (site_name) REFERENCES event (site_name)
);





DROP TABLE IF EXISTS transit_connections;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE transit_connections (
    site_name varchar(40),
    transit_type varchar(20),
    connect_route varchar(20),
    PRIMARY KEY (site_name, transit_type, route),
    CONSTRAINT transit_connections_fk1 FOREIGN KEY (site_name) REFERENCES site (name),
    CONSTRAINT transit_connections_fk2 FOREIGN KEY (transit_type) REFERENCES transit (type),
    CONSTRAINT transit_connections_fk3 FOREIGN KEY (connect_route) REFERENCES transit (route)
);





DROP TABLE IF EXISTS event_staff_assignments;
-- SET character_set_client = utf8mb4 ; -- what is this?
CREATE TABLE event_staff_assignments (
    employeeID decimal(10,0),
    event_name varchar(40),
    start_date char(10),
    site_name varchar(40),
    PRIMARY KEY (employeeID, event_name, start_date, site_name),
    CONSTRAINT visit_event_fk1 FOREIGN KEY (employeeID) REFERENCES employee (employeeID),
    CONSTRAINT visit_event_fk2 FOREIGN KEY (event_name) REFERENCES event (name),
    CONSTRAINT visit_event_fk3 FOREIGN KEY (start_date) REFERENCES event (start_date),
    CONSTRAINT visit_event_fk4 FOREIGN KEY (site_name) REFERENCES event (site_name)
);




