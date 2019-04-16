DROP PROCEDURE if exists user_login;
DELIMITER //
CREATE PROCEDURE user_login (IN inemail VARCHAR(50), IN inpassword VARCHAR(20))
 BEGIN
 SELECT email,password
 FROM email join user
 USING (username)
 WHERE email = inemail and password = inpassword;
 END //
DELIMITER ;

DROP PROCEDURE if exists check_approval;
DELIMITER //
CREATE PROCEDURE check_approval (IN inemail VARCHAR(50))
 BEGIN
 select status
 from email
 join user using (username)
 where email = inemail;
 END //
DELIMITER ;

DROP PROCEDURE if exists check_user_unique;
DELIMITER //
CREATE PROCEDURE check_user_unique (IN inusername VARCHAR(20))
 BEGIN
 select username
 from user
 where (username = inusername);
 END //
DELIMITER ;

DROP PROCEDURE if exists create_user;
DELIMITER //
CREATE PROCEDURE create_user (
    IN inusername VARCHAR(20),
    IN inpassword VARCHAR(20),
    IN infname varchar(20),
    IN inlname varchar(20),
    IN inemail varchar(50))
 BEGIN
 insert into user
    values (inusername, inpassword, "Pending", infname, inlname, "User");
 insert into email
    values (inusername, inemail);
 END //
DELIMITER ;

DROP PROCEDURE if exists create_visitor;
DELIMITER //
CREATE PROCEDURE create_visitor (
    IN inusername VARCHAR(20),
    IN inpassword VARCHAR(20),
    IN infname varchar(20),
    IN inlname varchar(20),
    IN inemail varchar(50))
 BEGIN
 insert into user
    values (inusername, inpassword, "Pending", infname, inlname, "User");
 insert into email
    values (inusername, inemail);
 insert into visitor_list
    values (inusername);
 END //
DELIMITER ;

DROP PROCEDURE if exists check_userphone_unique;
DELIMITER //
CREATE PROCEDURE check_userphone_unique (
    IN inusername VARCHAR(20),
    IN inphone char(10))
 BEGIN
 select username
 from user
 where (username = inusername);
 select phone
 from employee
 where (phone = inphone);
 END //
DELIMITER ;

DROP PROCEDURE if exists create_employee;
DELIMITER //
CREATE PROCEDURE create_employee (
    IN inusername VARCHAR(20),
    IN inpassword VARCHAR(20),
    IN infname varchar(20),
    IN inlname varchar(20),
    IN inemail varchar(50),
    IN inphone char(10),
    IN inaddress varchar(40),
    IN incity varchar(20),
    IN instate ENUM('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
               'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
               'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
               'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
               'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'Other'),
    IN zipcode char(5),
    IN inemployee_type ENUM('Admin','Staff','Manager'))
 BEGIN
 insert into user
    values (inusername, inpassword, "Pending", infname, inlname, "User");
 insert into email
    values (inusername, inemail);
 insert into employee(username, phone, address, city, state, zipcode, employee_type)
    values (inusername, inphone, inaddress, incity, instate, inzipcode, inemployee_type);
 END //
DELIMITER ;

