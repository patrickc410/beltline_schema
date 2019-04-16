-- screen 25 display
select E.name as 'Name', count(distinct staff_user) as 'Staff Count', datediff(E.end_date, E.start_date) as 'Duration (days)',
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


