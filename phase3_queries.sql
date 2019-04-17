
-- screen 16 filtering base query
select TT.take_date, TT.route, TT.transit_type, T.price
from take_transit as TT
join transit as T
on T.route = TT.route
and T.type = TT.transit_type
where TT.username = 'manager2'

-- screen 16 all filters applied
select TT.take_date, TT.route, TT.transit_type, T.price
from take_transit as TT
join transit as T
on T.route = TT.route
and T.type = TT.transit_type
join transit_connections as TC
on TT.transit_type = TC.transit_type
and TT.route = TC.route
where TT.username = 'manager2'
and TC.site_name = 'Inman Park'
and take_date >= '2019-03-01'
and take_date <= '2019-03-23'
and TT.route = 'Blue'
and TT.transit_type = 'MARTA'
order by TT.take_date



-- screen 17 check if employee is a visitor
select exists (select * from visitor_list
where username = 'manager2')


-- screen 17 check to see that an email to add is unique
select exists (select * from email
where email = 'dsmith@outlook.com')

-- screen 17 check to see that phone is unique
select exists (select * from employee
where phone = '1234567890')

-- screen 17 delete emails
delete from email where email = '{i}'

-- screen 17 add emails
insert into email (username, email)
values ('{self.username_d}', '{i}')

-- screen 17 delete from visitor_list
delete from visitor_list where username = ''

-- screen 17 insert into visitor_list
insert into visitor_list (username) values ('')






-- screen 18, temporary table
drop temporary table if exists s18_table;
create temporary table s18_table
select U.username, count(E.email) as 'email count',
(case U.user_type when 'User' then 'User'
when 'Visitor' then 'Visitor'
when 'Employee' then (select employee_type from employee where username = U.username)
else null end) as 'user_type', U.status
from user as U
join email as E
using (username)
left outer join employee as EMP
using (username)
group by U.username;

-- screen 18, initialize table view
select * from s18_table
where user_type <> 'Admin'


-- screen 18, with filters
select * from s18_table
where user_type <> 'Admin'
and user_type = 'Manager'
and status = 'Pending'
and username = 'manager1'


-- screen 18 approve user
 update user set status = 'Approved' where username = ''




-- screen 19 inital table view
select name, concat(fname, ' ', lname)  as full_name, 
openeveryday, manager_user from site join user where manager_user = username

-- screen 19 table all filters applied
select name, concat(fname, ' ', lname)  as full_name, 
openeveryday, manager_user from site join user where manager_user = username
and openeveryday = '{openeveryday}'
and name = '{site}'
and manager_user = '{manager}'



-- screen 20 inital display
select name, zipcode, address, concat(fname, ' ', lname)  as full_name,
openeveryday from site join user where manager_user = username
and name = 'Inman Park'

-- screen 20 inital display, manager dropdown list
(select manager_user, concat(fname, ' ', lname)  as full_name
from site join user where manager_user = username
and name = 'Inman Park')
union
(select username, concat(fname, ' ', lname) as full_name 
from employee join user using (username) 
where employee_type = 'Manager' 
and username not in (select manager_user from site)
order by user.lname)


-- screen 20 update site
update site set name = '{}', zipcode = '{}', address = '{}',
manager_user = '{}', openeveryday = '{}' where name = '{}'







-- screen 25 display
select E.name as 'Name', count(distinct staff_user) as 'Staff Count', datediff(E.end_date, E.start_date) + 1 as 'Duration (days)',
count(VE.username) as 'Total Visits', E.price * count(VE.username) as 'Total Revenue ($)'
from event as E
join event_staff_assignments as ESA
on E.name = ESA.event_name
and E.site_name = ESA.site_name
and E.start_date = ESA.start_date
left outer join visit_event as VE
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
group by E.name, E.start_date, E.site_name
order by E.name

-- screen 25 event keys
select E.name, E.site_name, E.start_date
from event as E
order by name



-- screen 25 check that manager can delete/edit the given site
select exists (select manager_user from site
where name = '{}'
and manager_user = '{}')


-- screen 25 delete event
delete from event
where name = '{}'
and start_date = '{}'
and site_name = '{}'



-- screen 26 display, part 1
select name, price, E.start_date, E.end_date, E.min_staff_req, capacity, description
from event as E
join event_staff_assignments as ESA
on E.name = ESA.event_name
and E.site_name = ESA.site_name
and E.start_date = ESA.start_date
left outer join visit_event as VE
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
where E.name = '{}'
and E.site_name = '{}'
and E.start_date = '{}'
group by E.name, E.start_date, E.site_name

-- screen 26 display, part 2
select visit_date, count(*) as 'Daily Visits', E.price * count(*) as 'Daily Revenue ($)'
from visit_event as VE
join event as E
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
where VE.event_name = '{}'
and VE.site_name = '{}'
and VE.start_date = '{}'
group by visit_date

-- screen 26 display, staff assignments
select exists (
select staff_user from event_staff_assignments as ESA
where event_name = '{}'
and start_date = '{}'
and site_name = '{}'
and staff_user = '{}')


-- screen 26 display, daily visits and revenue
select VE.visit_date, count(username) as 'Daily Visits', E.price * count(username) as 'Daily Revenue'
from visit_event as VE
join event as E
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
where E.name = '{}'
and E.start_date = '{}'
and E.site_name = '{}'
group by VE.visit_date



-- screen 27 initial staff table data
select user.username, concat(user.fname, ' ', user.lname) as 'full_name'
from employee join user using (username)
where employee_type = 'Staff'
order by user.username



-- screen 27 filter staff
select EMP.username, concat(U.fname, ' ', U.lname) as 'full_name' from employee as EMP
join user as U using (username)
where EMP.employee_type = 'Staff'
and EMP.username not in (
select distinct staff_user from event_staff_assignments as ESA
join event as E
on E.name = ESA.event_name
and E.site_name = ESA.site_name
and E.start_date = ESA.start_date
where ((E.start_date >= '{}' and E.start_date <= '{}')
or (E.end_date >= '{}' and E.end_date <= '{}')))
order by EMP.username


-- screen 27 check that event_name and start_date are unique to the site
select exists (select name, start_date from event
where site_name in (
select name from site
where manager_user = '{}')
and name = '{}'
and start_date = '{}')


-- screen 27 check that no events of same name overlap at that site
select exists (select * from event
where site_name in (
select name from site
where manager_user = '{}')
and name = '{}'
and ((start_date >= '{}' and start_date <= '{}')
or (end_date >= '{}' and end_date <= '{}')))


-- screen 27 check that no selected employee is working during the given dates
select exists (select EMP.username from employee as EMP
where EMP.employee_type = 'Staff'
and EMP.username = '{username}'
and EMP.username not in (
select distinct staff_user from event_staff_assignments as ESA
join event as E
on E.name = ESA.event_name
and E.site_name = ESA.site_name
and E.start_date = ESA.start_date
where ((E.start_date >= '{start_date}' and E.start_date <= '{end_date}')
or (E.end_date >= '{start_date}' and E.end_date <= '{end_date}')))
order by EMP.username)


-- screen 27 select site name based on manager username
select name from site
where manager_user = '{username}'


-- screen 27 insert into event table
insert into event (name, start_date, site_name, end_date, price, capacity, min_staff_req, description)
values ('{event_name}', '{start_date}', '{site_name}',
    '{end_date}', {price}, {capacity}, {min_staff_req}, '{description}')

-- screen 27 insert into event_staff_assignments table
insert into event_staff_assignments (staff_user, event_name, start_date, site_name)
values ('{username}', '{event_name}', '{start_date}', '{site_name}')



-- screen 28 filter
select U.username, concat(U.fname, ' ', U.lname) as 'full_name', count(event_name) as '# Event Shifts'
from user as U
join event_staff_assignments as ESA
on U.username = ESA.staff_user
join event as E
on E.name = ESA.event_name
and E.site_name = ESA.site_name
and E.start_date = ESA.start_date
where ((E.start_date >= '{start_date}' and E.start_date <= '{end_date}')
or (E.end_date >= '{start_date}' and E.end_date <= '{end_date}'))
group by U.username
order by U.lname





-- screen 32 display
select end_date, datediff(end_date, start_date) + 1 as 'Duration (days)',
capacity, price, description from event
where name = 'Bus Tour'
and start_date = '2019-02-01'
and site_name = 'Inman Park'


-- screen 32 display: staff assigned
select concat(U.fname, ' ', U.lname) as 'full_name'
from user as U join event_staff_assignments as ESA
on U.username = ESA.staff_user
where ESA.event_name = 'Bus Tour'
and ESA.start_date = '2019-02-01'
and ESA.site_name = 'Inman Park'



-- screen 33 display, before filters
select E.name, E.site_name, E.price, E.capacity - count(VE.username) as 'Ticket Remaining',
count(VE.username) as 'Total Visits',
count(case VE.username when 'mary.smith' then 1 else null end) as 'My Visits'
from event as E
join visit_event as VE
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
group by E.name, E.start_date, E.site_name
order by E.name


-- screen 34 display
select E.end_date, E.price, E.capacity - count(VE.username) as 'Ticket Remaining', description
from event as E
join visit_event as VE
on E.name = VE.event_name
and E.start_date = VE.start_date
and E.site_name = VE.site_name
where E.name = 'Bus Tour'
and E.start_date = '2019-02-01'
and E.site_name = 'Inman Park'


-- screen 34 insert query
insert into visit_event (username, event_name, start_date, site_name, visit_date)
values ('{self.username}', '{self.event_name}', '{self.start_date}', '{self.site_name}', '{log_date}')
