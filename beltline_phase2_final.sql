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



DROP TABLE IF EXISTS email;
CREATE TABLE email (
    username varchar(20),
    email varchar(100) NOT NULL,
    PRIMARY KEY (email),
    CONSTRAINT email_fk1 FOREIGN KEY (username) 
        REFERENCES user(username) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



-- we created the visitor_list table to hold all of the visitor ands and employee-visitors,
-- so when a visitor is deleted or employee-visitor returns to a plain employee status,
-- they will be deleted from this table, and consquently, all of their associated
-- visit_site and visit_event history will be deleted, too
CREATE TABLE visitor_list (
    username varchar(20) PRIMARY KEY,
    CONSTRAINT visitor_list_fk1 FOREIGN KEY (username) 
        REFERENCES user(username) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS employee;
CREATE TABLE employee (
    employeeID int AUTO_INCREMENT,
    username varchar(20) UNIQUE KEY NOT NULL,
    phone char(10) UNIQUE KEY NOT NULL,
    address varchar(40) NOT NULL,
    city varchar(20) NOT NULL,
    state ENUM('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
               'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
               'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
               'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
               'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'Other') NOT NULL,
    zipcode char(5) NOT NULL,
    employee_type ENUM('Administrator','Staff','Manager') NOT NULL,
    PRIMARY KEY(employeeID),
    CONSTRAINT employee_fk1 FOREIGN KEY (username) 
        REFERENCES user(username) 
        ON UPDATE CASCADE ON DELETE CASCADE
);

ALTER TABLE employee AUTO_INCREMENT = 100000000;



DROP TABLE IF EXISTS site;
CREATE TABLE site (
    name varchar(40) PRIMARY KEY,
    address varchar(40),
    zipcode char(5) NOT NULL,
    openeveryday ENUM('Yes','No') NOT NULL,
    managerID int NOT NULL,
    CONSTRAINT site_fk1 FOREIGN KEY (managerID) 
        REFERENCES employee (employeeID) 
        ON UPDATE CASCADE ON DELETE RESTRICT
);



DROP TABLE IF EXISTS transit;
CREATE TABLE transit (
    type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    price decimal(4,2) NOT NULL,
    PRIMARY KEY (type, route)
);



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
    CONSTRAINT event_fk1 FOREIGN KEY (site_name) 
        REFERENCES site (name) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS take_transit;
CREATE TABLE take_transit (
    username varchar(20) NOT NULL,
    transit_type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    take_date date NOT NULL,
    PRIMARY KEY (username, transit_type, route, take_date),
    CONSTRAINT take_transit_fk1 FOREIGN KEY (username) REFERENCES user (username) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT take_transit_fk2 FOREIGN KEY (transit_type, route) 
        REFERENCES transit (type, route) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS visit_site;
CREATE TABLE visit_site (
    username varchar(20) NOT NULL,
    site_name varchar(40) NOT NULL,
    visit_date date NOT NULL,
    PRIMARY KEY (username, site_name, visit_date),
    CONSTRAINT visit_site_fk1 FOREIGN KEY (username) 
        REFERENCES visitor_list (username) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT visit_site_fk2 FOREIGN KEY (site_name) 
        REFERENCES site (name) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS visit_event;
CREATE TABLE visit_event (
    username varchar(20) NOT NULL,
    event_name varchar(40) NOT NULL,
    start_date date NOT NULL,
    site_name varchar(40) NOT NULL,
    visit_date date NOT NULL,
    PRIMARY KEY (username, event_name, start_date, site_name, visit_date),
    CONSTRAINT visit_event_fk1 FOREIGN KEY (username) 
        REFERENCES visitor_list (username) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT visit_event_fk2 FOREIGN KEY (event_name, start_date, site_name) 
        REFERENCES event (name, start_date, site_name) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS transit_connections;
CREATE TABLE transit_connections (
    site_name varchar(40) NOT NULL,
    transit_type ENUM('MARTA','Bus','Bike') NOT NULL,
    route varchar(20) NOT NULL,
    PRIMARY KEY (site_name, transit_type, route),
    CONSTRAINT transit_connections_fk1 FOREIGN KEY (site_name) 
        REFERENCES site (name) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT transit_connections_fk2 FOREIGN KEY (transit_type, route) 
        REFERENCES transit (type, route) 
        ON UPDATE CASCADE ON DELETE CASCADE
);



DROP TABLE IF EXISTS event_staff_assignments;
CREATE TABLE event_staff_assignments (
    employeeID int NOT NULL,
    event_name varchar(40) NOT NULL,
    start_date date NOT NULL,
    site_name varchar(40) NOT NULL,
    PRIMARY KEY (employeeID, event_name, start_date, site_name),
    CONSTRAINT event_staff_assignments_fk1 FOREIGN KEY (employeeID) 
        REFERENCES employee (employeeID) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT event_staff_assignments_fk2 FOREIGN KEY (event_name, start_date, site_name) 
        REFERENCES event (name, start_date, site_name) 
        ON UPDATE CASCADE ON DELETE CASCADE
);
