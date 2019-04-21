import csv
import pymysql
import sys
global connection
try:
    connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password=sys.argv[1],
                                     db='beltline',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
except Exception as e:
    print(e)

with open('username_data.csv') as un_data:
    reader = csv.reader(un_data)
    username_data = [line for line in reader]
    curs = connection.cursor()
    for i in username_data[1:]:
        i[1] = hash(i[1])
    for item in username_data[1:]:
        query = ("INSERT into user(username,password,status,fname,lname,user_type) VALUES (%s,%s,%s,%s,%s,%s);")
        curs.execute(query,item)


with open('email_data.csv') as un_data:
    reader = csv.reader(un_data)
    email_data = [line for line in reader]
    curs = connection.cursor()
    for item in email_data[1:]:
        query = ("INSERT into email VALUES (%s,%s);")
        curs.execute(query,item)

with open('visitorlist_data.csv') as un_data:
    reader = csv.reader(un_data)
    visitorlist_data = [line for line in reader]
    curs = connection.cursor()
    for item in visitorlist_data[1:]:
        query = ("INSERT into visitor_list VALUES (%s);")
        curs.execute(query,item[0])

with open('employee_data.csv') as un_data:
    reader = csv.reader(un_data)
    emp_data = [line for line in reader]
    curs = connection.cursor()
    for item in emp_data[1:]:
        query = ("INSERT into employee VALUES (%s,%s,%s,%s,%s,%s,%s,%s);")
        curs.execute(query,item)

with open('site_data.csv') as un_data:
    reader = csv.reader(un_data)
    emp_data = [line for line in reader]
    curs = connection.cursor()
    for item in emp_data[1:]:
        query = ("INSERT into site VALUES (%s,%s,%s,%s,%s);")
        curs.execute(query,item)

with open('event_data.csv') as un_data:
    reader = csv.reader(un_data)
    event_data = [line for line in reader]
    curs = connection.cursor()
    for item in event_data[1:]:
        query = ("INSERT into event VALUES (%s,%s,%s,%s,%s,%s,%s,%s);")
        curs.execute(query,item)

with open('transit_data.csv') as un_data:
    reader = csv.reader(un_data)
    transit_data = [line for line in reader]
    curs = connection.cursor()
    for item in transit_data[1:]:
        query = ("INSERT into transit VALUES (%s,%s,%s);")
        curs.execute(query,item)


with open('connect_data.csv') as un_data:
    reader = csv.reader(un_data)
    connect_data = [line for line in reader]
    curs = connection.cursor()
    for item in connect_data[1:]:
        query = ("INSERT into transit_connections VALUES (%s,%s,%s);")
        curs.execute(query,item)

with open('taketransit_data.csv') as un_data:
    reader = csv.reader(un_data)
    taketransit_data = [line for line in reader]
    curs = connection.cursor()
    for item in taketransit_data[1:]:
        query = ("INSERT into take_transit VALUES (%s,%s,%s,%s);")
        curs.execute(query,item)

with open('assignto_data.csv') as un_data:
    reader = csv.reader(un_data)
    assignto_data = [line for line in reader]
    curs = connection.cursor()
    for item in assignto_data[1:]:
        query = ("INSERT into event_staff_assignments VALUES (%s,%s,%s,%s);")
        curs.execute(query,item)

with open('visitevent_data.csv') as un_data:
    reader = csv.reader(un_data)
    visitevent_data = [line for line in reader]
    curs = connection.cursor()
    for item in visitevent_data[1:]:
        query = ("INSERT into visit_event VALUES (%s,%s,%s,%s,%s);")
        curs.execute(query,item)

with open('visitsite_data.csv') as un_data:
    reader = csv.reader(un_data)
    visitsite_data = [line for line in reader]
    curs = connection.cursor()
    for item in visitsite_data[1:]:
        query = ("INSERT into visit_site VALUES (%s,%s,%s);")
        curs.execute(query,item)

connection.commit()

curs.close()
