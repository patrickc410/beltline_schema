from pprint import pprint
import re
from decimal import Decimal

import pymysql
import sys
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QDialog,
    QGroupBox,
    QVBoxLayout,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QLabel,
    qApp,
    QAction,
    QSplitter,
    QListView,
    QTableWidget,
    QTableWidgetItem,
    QTableView,
    QAbstractItemView,
    QMainWindow,
    QMessageBox,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QPlainTextEdit
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QPixmap)


#TODO - column sorting?
#TODO - better email pattern checking
#TODO - price out of range




def hash_password(astring):
    out = 17
    count = 0
    for i in astring:
        if count % 2 == 0:
            out = out + (61 * ord(i))
        if count % 3 == 0:
            out = out + (51 * ord(i))
        if count % 5 == 0:
            out = out + (41 * ord(i))
        out = out + (31 * ord(i))
    return out



def check_selected(table_view, table_model, parent, index_list=None):
    selected = len(table_view.selectedIndexes())
    row_index = table_view.currentIndex().row()
    if (not selected):
        QMessageBox.warning(
            parent, 'Error', 'Please select a row of the table')
        return None
    else:
        if index_list == None:
            return row_index
        else:
            out_list = []
            for i in index_list:
                out_list.append(table_model.data[row_index][i])
            return out_list


def valid_email_check(astring, parent):
    email_format = r'\S+@\S+\.\S+'
    email_check = re.fullmatch(email_format, astring)
    if (email_check == None):
        QMessageBox.warning(
            parent, 'Error', 'Please enter a valid email address')
        return False
    else:
        return True


def valid_date_check(astring, parent):
    date_pattern = r'[\d]{4}-[0,1][\d]{1}-[0,1,2,3][\d]{1}'
    date_check1 = re.fullmatch(date_pattern, astring)
    if (date_check1 == None):
        QMessageBox.warning(
            parent, 'Error', 'Please enter valid dates in the form YYYY-MM-DD')
        return False
    else:
        return True

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def createTable(headers, rows, singleSelection=True):
    table_model = SimpleTableModel(headers, rows)
    table_view = QTableView()

    # proxy_model = QSortFilterProxyModel()
    # proxy_model.setSourceModel(table_model)

    table_view.setModel(table_model)
    # table_view.setModel(proxy_model)
    table_view.setSortingEnabled(True)
    if (singleSelection):
        table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
    else:
        table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.MultiSelection)
    return table_model, table_view



def createHBox(parent, list_of_tuples):
    hbox = QHBoxLayout()
    hbox_list = []
    for tup in list_of_tuples:
        if (tup[0] == 'QLabel'):
            label = QLabel(tup[1][0])
            hbox.addWidget(label)
            hbox_list.append(label)
        elif (tup[0] == 'QComboBox'):
            combo_box = QComboBox()
            combo_box.addItems(tup[1][0])
            hbox.addWidget(combo_box)
            hbox_list.append(combo_box)
        elif (tup[0] == 'QPushButton'):
            btn = QPushButton(tup[1][0])
            exec(f"btn.clicked.connect(parent.{tup[1][1]})")
            hbox.addWidget(btn)
            hbox_list.append(btn)
        elif (tup[0] == 'QLineEdit'):
            if (len(tup[1]) == 0):
                line_edit = QLineEdit()
            else:
                line_edit = QLineEdit(tup[1][0])
            hbox.addWidget(line_edit)
            hbox_list.append(line_edit)
        elif (tup[0] == 'QPlainTextEdit'):
            if (len(tup[1]) == 0):
                text_edit = QPlainTextEdit()
            elif (len(tup[1]) == 1):
                text_edit = QPlainTextEdit(tup[1][0])
            elif (len(tup[1]) == 2):
                text_edit = QPlainTextEdit(tup[1][0])
                text_edit.setReadOnly(tup[1][1])
            hbox.addWidget(text_edit)
            hbox_list.append(text_edit)
    return (hbox, hbox_list)


def sqlQueryOutput(query, alist=None):
    cursor = connection.cursor()
    cursor.execute(query)
    data = [line for line in cursor]
    cursor.close()
    if (alist == None):
        return data
    else:
        output_list = []
        for i in data:
            append_list = []
            for x in alist:
                if (isinstance(i[x], Decimal)):
                    append_list.append(float(i[x]))
                elif ('date' in x):
                    append_list.append(str(i[x]))
                else:
                    append_list.append(i[x])
            output_list.append(append_list)
        return output_list


def sqlInsertDeleteQuery(query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()






#SCREEN NUMBER 38
class VisitorVisitHistory(QWidget):
    def __init__(self,parent,username):
        super(VisitorVisitHistory, self).__init__()
        self.setWindowTitle("Visit History")
        self.username = username
        self.parent = parent

        self.vbox = QVBoxLayout()

        site_name_list = create_site_name_list()
        site_name_list.insert(0, '--ALL--')

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Event: ']), ('QLineEdit', [])],
            [('QLabel', ['Site: ']), ('QComboBox', [site_name_list])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter'])]
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.drop_query = "drop temporary table if exists s38"

        self.temp_table_query = "create temporary table s38 "\
            + "(select VE.visit_date, VE.site_name, VE.event_name, E.price from visit_event as VE "\
            + "join event as E on E.name = VE.event_name "\
            + f"and E.site_name = VE.site_name and E.start_date = VE.start_date and username = '{self.username}') "\
            + "union all "\
            + f"(select visit_date, site_name, null, 0 from visit_site where username = '{self.username}') "

        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        self.root_query = "select * from s38 "
        self.curr_query = self.root_query

        self.table_rows = sqlQueryOutput(self.root_query, ['visit_date', 'event_name', 'site_name', 'price'])
        self.headers = ['Date', 'Event', 'Site', 'Price']

        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        self.vbox.addWidget(self.table_view)

        self.hbox_list1 = []
        hbox_contents1 = [
            [('QPushButton', ['Back', 'handleBack'])]]

        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.setLayout(self.vbox)


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleFilter(self):
        event = self.hbox_list[0][1][1].text()
        site = self.hbox_list[1][1][1].currentText()
        start_date = self.hbox_list[2][1][1].text()
        end_date = self.hbox_list[3][1][1].text()

        event_filter = (not (event == ''))
        start_date_filter = (not (start_date == ''))
        end_date_filter = (not (end_date == ''))
        site_name_filter = (not (site == '--ALL--'))

        if start_date_filter:
            if not valid_date_check(start_date, self):
                return
        if end_date_filter:
            if not valid_date_check(end_date, self):
                return

        query = self.root_query
        sub_query = 'where '

        filter_count = 0
        if start_date_filter:
            sub_query += f"visit_date >= '{start_date}' "
            filter_count += 1
        if end_date_filter:
            if filter_count:
                sub_query += "and "
            sub_query += f"visit_date <= '{end_date}' "
            filter_count += 1
        if site_name_filter:
            if filter_count:
                sub_query += "and "
            sub_query += f"site_name = '{site}' "
            filter_count += 1
        if event_filter:
            if filter_count:
                sub_query += "and "
            sub_query += f"event_name = '{event}' "
            filter_count += 1

        if filter_count:
            query += sub_query

        self.handleUpdateTable(query)



    def handleUpdateTable(self, query=None):

        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        if query == None:
            query = self.root_query

        self.curr_query = query
        self.table_rows = sqlQueryOutput(query, ['visit_date', 'event_name', 'site_name', 'price'])

        self.table_model = SimpleTableModel(self.headers, self.table_rows)
        self.table_view.setModel(self.table_model)




#SCREEN NUMBER 37
class VisitorSiteDetail(QWidget):
    def __init__(self,parent,username,site_name):
        super(VisitorSiteDetail, self).__init__()
        self.setWindowTitle("Visitor Site Detail")
        self.username = username
        self.parent = parent
        self.site_name = site_name

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()

        self.site_label = QLabel("Site:")
        self.hbox1.addWidget(self.site_label)

        self.openeveryday_label = QLabel("Open Everyday:")
        self.hbox1.addWidget(self.openeveryday_label)

        self.address_label = QLabel("Address:")
        self.hbox2.addWidget(self.address_label)

        self.vbox = QVBoxLayout()

        query =  "select openeveryday, address from site "\
            + f"where name = '{self.site_name}';"

        data = sqlQueryOutput(query, ['openeveryday', 'address'])
        data = data[0]


        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Site: ']), ('QLabel', [self.site_name])],
            [('QLabel', ['Open Everyday: ']), ('QLabel', [f'{data[0]}'])],
            [('QLabel', ['Address: ']), ('QLabel', [f'{data[1]}'])],
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.hbox_list1 = []
        hbox_contents1 = [
        [('QLabel', ["Visit Date"]), ('QLineEdit', []), ('QPushButton', ['Log Visit', 'handleLogVisit'])],
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleLogVisit(self):
        log_date = self.hbox_list1[0][1][1].text()

        date_check = valid_date_check(log_date, self)

        if date_check:

            query = "select exists (select * from visit_site  "\
                + f"where site_name = '{self.site_name}' "\
                + f"and username = '{self.username}' "\
                + f"and visit_date = '{log_date}') "
            x = sqlQueryOutput(query)
            already_visited = list(x[0].values())[0]

            if (already_visited):
                QMessageBox.warning(
                    self, 'Error', 'You already visited on this day silly goose!')
            else:

                query = "insert into visit_site (username, site_name, visit_date) "\
                    + f"values ('{self.username}', '{self.site_name}', '{log_date}') "

                sqlInsertDeleteQuery(query)

                QMessageBox.information(
                    self, 'Success', "You successfully logged your visit!", QMessageBox.Ok)

                self.parent.handleUpdateTable()
                self.handleBack()

#SCREEN NUMBER 36
class VisitorTransitDetail(QWidget):
    def __init__(self, parent, username, site_name):
        super(VisitorTransitDetail, self).__init__()
        self.setWindowTitle("Visitor Transit Detail")

        self.username = username
        self.parent = parent
        self.site_name = site_name

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()

        self.site_label = QLabel("Site: ")
        self.selected_site_label = QLabel(self.site_name)
        self.hbox1.addWidget(self.site_label)
        self.hbox1.addWidget(self.selected_site_label)

        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type_dropdown = QComboBox(self)
        self.transport_type_dropdown.addItems(["--ALL--", "MARTA", "Bus", "Bike"])
        self.hbox2.addWidget(self.transport_type_label)
        self.hbox2.addWidget(self.transport_type_dropdown)


        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)


        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addWidget(self.filter_btn)


        self.root_query = "select T.route, type, price, count(site_name) as '# Connected Sites' "\
            + "from transit as T join transit_connections as TC "\
            + "on TC.route = T.route "\
            + "and TC.transit_type = T.type "\
            + "where (T.route, T.type) in "\
            + "(select route, transit_type from transit_connections "\
            + f"where site_name = '{self.site_name}') "

        self.group_by = "group by T.route, T.type "

        query = self.root_query + self.group_by

        table_rows = sqlQueryOutput(query, ['route', 'type', 'price', '# Connected Sites'])

        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)


        self.hbox4 = QHBoxLayout()
        self.transit_date_label = QLabel("Transit Date: ")
        self.transit_date = QLineEdit(self)
        self.log_transit_btn = QPushButton('Log Transit', self)
        self.log_transit_btn.clicked.connect(self.handleLogTransit)
        self.hbox4.addWidget(self.transit_date_label)
        self.hbox4.addWidget(self.transit_date)
        self.hbox4.addWidget(self.log_transit_btn)
        self.vbox.addLayout(self.hbox4)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)


    def handleFilter(self):

        transit_type = self.transport_type_dropdown.currentText()

        table_data = []
        cursor = connection.cursor()

        transit_type_filter = True
        filterquery = ''

        if (transit_type == '--ALL--'):
            filterquery = self.root_query + self.group_by

        else:
            filterquery = self.root_query + f"and T.type = '{transit_type}' " + self.group_by

        cursor.execute(filterquery)
        transit_data = [line for line in cursor]
        for i in transit_data:
            table_data.append([i["route"], i["type"], str(i["price"]), i["# Connected Sites"]])

        self.hide()
        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], table_data)
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        self.show()

    def handleLogTransit(self):
        row_index = self.table_view.currentIndex().row()

        if (row_index == -1):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:

            transit_date = self.transit_date.text()
            date_pattern = r'[\d]{4}-[0,1][\d]{1}-[0,1,2,3][\d]{1}'
            date_check = re.fullmatch(date_pattern, transit_date)
            route = self.table_model.data[row_index][0]
            transit_type = self.table_model.data[row_index][1]
            query_check = "select exists (select username " \
                + "from take_transit " \
                + f"where username = '{self.username}' " \
                + f"and transit_type = '{transit_type}' " \
                + f"and route = '{route}' " \
                + f"and take_date = '{transit_date}')"
            cursor = connection.cursor()
            cursor.execute(query_check)
            same_day_check = [line for line in cursor]
            same_day = list(same_day_check[0].values())[0]

            cursor.close()

            if (date_check == None):
                QMessageBox.warning(
                    self, 'Error', 'Please enter a valid date in the form YYYY-MM-DD')
            elif (same_day):
                QMessageBox.warning(
                    self, 'Error', 'You cannot take the same transit twice in one day')
            else:

                query = "insert into take_transit " \
                    + "(username, transit_type, route, take_date) " \
                    + f"values ('{self.username}', '{transit_type}', '{route}', '{transit_date}');"
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                cursor.close()
                QMessageBox.information(self, 'Congrats!', "You successfully logged your journey!", QMessageBox.Ok)
    def handleBack(self):
        self.close()
        self.parent.show()


# SCREEN NUMBER 35
class VisitorExploreSite(QWidget):
    def __init__(self, parent, username):
        super(VisitorExploreSite, self).__init__()
        self.setWindowTitle("Event Detail")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        site_name_list = create_site_name_list()
        site_name_list.insert(0, '--ALL--')
        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Site Name: ']), ('QComboBox', [site_name_list])],
            [('QLabel', ['Open Every Day: ']), ('QComboBox', [['--ALL--', 'Yes', 'No']])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', []), ('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QLabel', ['Total Visits Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Event Count Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))


        self.cb_include_visited = QCheckBox("Include Visited?", self)
        self.cb_include_visited.setChecked(True)
        self.vbox.addWidget(self.cb_include_visited)

        self.hbox_list1 = []
        hbox_contents1 = [
            [('QPushButton', ['Filter', 'handleFilter']), ('QPushButton', ['Site Detail', 'handleSiteDetail']), ('QPushButton', ['Transit Detail', 'handleTransitDetail'])]
            ]

        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.drop_query = 'drop temporary table if exists temp35;'
        self.temp_table_query = 'create temporary table temp35 '\
                + "select S_OUT.name as 'site_name', "\
                + "count(distinct E_OUT.name,E_OUT.start_date) as 'event_counts', "\
                + "(select count(*) as 'total_visits' "\
                + "from site as S "\
                + "join event as E "\
                + "on S.name = E.site_name "\
                + "left outer join visit_site as VS "\
                + "on S.name = VS.site_name "\
                + "group by S.name "\
                + "having S.name = S_OUT.name "\
                + "order by S.name) "\
                + "+ "\
                + "(select count(*) from visit_event "\
                + "group by site_name "\
                + "having site_name = S_OUT.name "\
                + "order by site_name) "\
                + "as 'total_visits', "\
                + "ifnull((select count(*) "\
                + "from site as S "\
                + "join event as E "\
                + "on S.name = E.site_name "\
                + "left outer join visit_site as VS "\
                + "on S.name = VS.site_name "\
                + f"where VS.username = '{self.username}' "\
                + "group by S.name "\
                + "having S.name = S_OUT.name "\
                + "order by S.name), 0) "\
                + "+ "\
                + "ifnull((select count(*) from visit_event "\
                + f"where visit_event.username = '{self.username}' "\
                + "group by site_name "\
                + "having site_name = S_OUT.name "\
                + "order by site_name), 0) "\
                + "as 'my_visits', S_OUT.openeveryday "\
                + "from site as S_OUT "\
                + "join event as E_OUT "\
                + "on E_OUT.site_name = S_OUT.name "\
                + "group by S_OUT.name; "

        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        self.root_query = "select distinct t35.site_name,t35.event_counts,t35.total_visits,t35.my_visits from temp35 as t35 "
        self.curr_query = self.root_query

        self.table_rows = sqlQueryOutput(self.root_query, ['site_name', 'event_counts', 'total_visits', 'my_visits'])
        # self.event_key_list = sqlQueryOutput(query, ['name', 'site_name', 'start_date'])
        self.table_headers = ['Site Name', 'Event Count', 'Total Visits', 'My Visits']
        self.table_model, self.table_view = createTable(self.table_headers, self.table_rows)
        self.vbox.addWidget(self.table_view)


        self.hbox_list2 = []
        hbox_contents1 = [
            [('QPushButton', ['Back', 'handleBack'])]]

        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.setLayout(self.vbox)



    def handleFilter(self):
        site_name = self.hbox_list[0][1][1].currentText()
        openeveryday = self.hbox_list[1][1][1].currentText()
        start_date = self.hbox_list[2][1][1].text()
        end_date = self.hbox_list[2][1][3].text()
        visits_lower = self.hbox_list[3][1][1].text()
        visits_upper = self.hbox_list[3][1][3].text()
        event_count_lower = self.hbox_list[4][1][1].text()
        event_count_upper = self.hbox_list[4][1][3].text()
        include_visited = self.cb_include_visited.checkState()


        site_name_filter = (not (site_name == '--ALL--'))
        openeveryday_filter = (not (openeveryday == '--ALL--'))
        start_date_filter = (not (start_date == ''))
        end_date_filter = (not (end_date == ''))
        visits_lower_filter = (not (visits_lower == ''))
        visits_upper_filter = (not (visits_upper == ''))
        event_lower_filter = (not (event_count_lower == ''))
        event_upper_filter = (not (event_count_upper == ''))


        query = self.root_query
        sub_query = "where "
        filter_count = 0
        date_filter_count = 0

        if (start_date_filter):
            if not valid_date_check(start_date, self):
                return
            else:
                query += "join event on t35.site_name = event.site_name "
                date_filter_count += 1
                sub_query += f"event.start_date >= '{start_date}' "
                filter_count += 1
        if (end_date_filter):
            if not valid_date_check(end_date, self):
                return
            else:
                if not(date_filter_count):
                    query += "join event on t35.site_name = event.site_name "
                if date_filter_count:
                    sub_query += 'and '
                sub_query += f"event.start_date <= '{end_date}' "
                date_filter_count += 1
                filter_count += 1
        if (site_name_filter):
            if filter_count:
                sub_query += "and "
            sub_query += f"t35.site_name = '{site_name}'"
            filter_count += 1
        if (openeveryday_filter):
            if filter_count:
                sub_query += "and "
            sub_query += f"t35.openeveryday = '{openeveryday}'"
            filter_count += 1
        if (event_lower_filter):
            if not is_float(event_count_lower):
                QMessageBox.warning(self, 'Error', 'The event count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"event_counts >= '{event_count_lower}' "
                filter_count += 1
        if (event_upper_filter):
            if not is_float(event_count_upper):
                QMessageBox.warning(self, 'Error', 'The event count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"event_counts <= {event_count_upper} "
                filter_count += 1

        if (visits_lower_filter):
            if not is_float(visits_lower):
                QMessageBox.warning(self, 'Error', 'The visit count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_visits >= {visits_lower} "
                filter_count += 1
        if (visits_upper_filter):
            if not is_float(visits_upper):
                QMessageBox.warning(self, 'Error', 'The visit count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_visits <= '{visits_upper}' "
                filter_count += 1

        if (include_visited):
            if filter_count:
                sub_query += "and "
            sub_query += f"my_visits is null "
            filter_count += 1

        print(sub_query)
        if filter_count:
            query += sub_query

        self.handleUpdateTable(query)

    def handleSiteDetail(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            site_data = self.table_rows[row_index]
            self.hide()
            self.visitor_site_detail = VisitorSiteDetail(self, self.username, site_data[0])
            self.visitor_site_detail.show()
            self.visitor_site_detail.raise_()

    def handleTransitDetail(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            site_data = self.table_rows[row_index]
            self.hide()
            self.visitor_transit_detail = VisitorTransitDetail(self, self.username, site_data[0])
            self.visitor_transit_detail.show()
            self.visitor_transit_detail.raise_()

    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        if (query == None):
            query = self.root_query

        self.table_rows = sqlQueryOutput(query, ['site_name', 'event_counts', 'total_visits', 'my_visits'])
        #self.event_key_list = sqlQueryOutput(query, ['name', 'site_name', 'start_date'])

        self.table_model = SimpleTableModel(self.table_headers, self.table_rows)
        self.table_view.setModel(self.table_model)

        self.curr_query = query

    def handleBack(self):
        self.close()
        self.parent.show()





# SCREEN NUMBER 34
class VisitorEventDetail(QWidget):
    def __init__(self, parent, username, event_name, start_date, site_name):
        super(VisitorEventDetail, self).__init__()
        self.setWindowTitle("Event Detail")
        self.parent = parent
        self.event_name = event_name
        self.start_date = start_date
        self.site_name = site_name
        self.username = username


        self.vbox = QVBoxLayout()

        query =  "select E.end_date, E.price, E.capacity - count(VE.username) as 'Ticket Remaining', description  "\
            + "from event as E "\
            + "join visit_event as VE "\
            + "on E.name = VE.event_name "\
            + "and E.start_date = VE.start_date "\
            + "and E.site_name = VE.site_name "\
            + f"where E.name = '{self.event_name}' "\
            + f"and E.start_date = '{self.start_date}' "\
            + f"and E.site_name = '{self.site_name}' "

        data = sqlQueryOutput(query, ['end_date', 'price', 'Ticket Remaining', 'description'])
        data = data[0]


        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Event: ']), ('QLabel', [self.event_name])],
            [('QLabel', ['Site: ']), ('QLabel', [self.site_name])],
            [('QLabel', ['Start Date: ']), ('QLabel', [self.start_date])],
            [('QLabel', ['End Date: ']), ('QLabel', [f'{data[0]}'])],
            [('QLabel', ['Price ($): ']), ('QLabel', [f'{data[1]}'])],
            [('QLabel', ['Tickets Remaining: ']), ('QLabel', [f'{data[2]}'])],
            [('QLabel', ['Description: '])],
            [('QPlainTextEdit', [f'{data[3]}', True])]
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.hbox_list1 = []
        hbox_contents1 = [
        [('QLabel', ["Visit Date"]), ('QLineEdit', []), ('QPushButton', ['Log Visit', 'handleLogVisit'])],
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleLogVisit(self):
        end_date = self.hbox_list[3][1][1].text()
        tickets_remaining = self.hbox_list[5][1][1].text()
        log_date = self.hbox_list1[0][1][1].text()

        date_check = valid_date_check(log_date, self)

        if date_check:

            query = "select exists (select * from visit_event  "\
                + f"where event_name = '{self.event_name}' "\
                + f"and start_date = '{self.start_date}' "\
                + f"and site_name = '{self.site_name}' "\
                + f"and username = '{self.username}' "\
                + f"and visit_date = '{log_date}') "
            x = sqlQueryOutput(query)
            already_visited = list(x[0].values())[0]


            if (int(tickets_remaining) <= 0):
                QMessageBox.warning(
                    self, 'Error', 'There are no tickets remaining')
            elif (log_date > end_date or log_date < self.start_date):
                QMessageBox.warning(
                    self, 'Error', 'Your visit must be during the dates of the event silly goose!')
            elif (already_visited):
                QMessageBox.warning(
                    self, 'Error', 'You already visited on this day silly goose!')
            else:

                query = "insert into visit_event (username, event_name, start_date, site_name, visit_date) "\
                    + f"values ('{self.username}', '{self.event_name}', '{self.start_date}', '{self.site_name}', '{log_date}') "

                sqlInsertDeleteQuery(query)

                QMessageBox.information(
                    self, 'Success', "You successfully logged your visit!", QMessageBox.Ok)

                self.parent.handleUpdateTable()
                self.handleBack()




# SCREEN NUMBER 33
class VisitorExploreEvent(QWidget):
    def __init__(self, parent, username):
        super(VisitorExploreEvent, self).__init__()
        self.setWindowTitle("Explore Event")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        site_name_list = create_site_name_list()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Description Keyword: ']), ('QLineEdit', [])],
            [('QLabel', ['Site: ']), ('QComboBox', [site_name_list])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QLabel', ['Total Visits Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Ticket Price Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.cb_include_visited = QCheckBox("Include Visited?", self)
        self.cb_include_visited.setChecked(True)
        self.cb_include_soldout = QCheckBox("Include Sold Out Events?", self)
        self.cb_include_soldout.setChecked(True)
        self.vbox.addWidget(self.cb_include_visited)
        self.vbox.addWidget(self.cb_include_soldout)

        self.hbox_list1 = []
        hbox_contents1 = [
            [('QPushButton', ['Filter', 'handleFilter']), ('QPushButton', ['Event Detail', 'handleEventDetail'])],
            ]

        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.drop_query = "drop temporary table if exists s33"
        self.temp_table_query = "create temporary table s33 "\
            + "select E.name, E.site_name, E.start_date, E.price, E.capacity - count(VE.username) as 'ticket_remaining', "\
            + "count(VE.username) as 'total_visits', "\
            + f"count(case VE.username when '{self.username}' then 1 else null end) as 'my_visits', "\
            + "E.description, E.end_date "\
            + "from event as E "\
            + "join visit_event as VE "\
            + "on E.name = VE.event_name "\
            + "and E.start_date = VE.start_date "\
            + "and E.site_name = VE.site_name "\
            + "group by E.name, E.start_date, E.site_name order by E.name; "

        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        self.root_query = "select * from s33 "
        self.curr_query = self.root_query

        self.table_rows = sqlQueryOutput(self.root_query, ['name', 'site_name', 'price', 'ticket_remaining', 'total_visits', 'my_visits'])
        self.event_key_list = sqlQueryOutput(self.root_query, ['name', 'site_name', 'start_date'])
        self.table_headers = ['Event Name', 'Site Name', 'Ticket Price', 'Ticket Remaining', 'Total Visits', 'My Visits']
        self.table_model, self.table_view = createTable(self.table_headers, self.table_rows)
        self.vbox.addWidget(self.table_view)


        self.hbox_list1 = []
        hbox_contents1 = [
            [('QPushButton', ['Back', 'handleBack'])],
            ]

        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)


    def handleFilter(self):
        event_name = self.hbox_list[0][1][1].text()
        desc_keyword = self.hbox_list[1][1][1].text()
        site_name = self.hbox_list[2][1][1].currentText()
        start_date = self.hbox_list[3][1][1].text()
        end_date = self.hbox_list[4][1][1].text()
        tot_visit_lower = self.hbox_list[5][1][1].text()
        tot_visit_upper = self.hbox_list[5][1][3].text()
        price_lower = self.hbox_list[6][1][1].text()
        price_upper = self.hbox_list[6][1][3].text()
        include_visited = self.cb_include_visited.checkState()
        include_soldout = self.cb_include_soldout.checkState()

        query = self.root_query

        if (event_name or desc_keyword or (site_name!= "--ALL--") or start_date or end_date or tot_visit_lower or tot_visit_upper):
            query += "where "
        if event_name != '':
            query += f"name = '{event_name}' and "
        if desc_keyword != '':
            query += f"description like '%{desc_keyword}%' and "
        if site_name != '--ALL--':
            query += f"site_name = '{site_name}' and "
        if start_date != '':
            if not valid_date_check(start_date, self):
                return
            query += f"start_date >= '{start_date}' and "
        if end_date != '':
            if not valid_date_check(end_date, self):
                return
            query += f"end_date <= '{end_date}' and "
        if tot_visit_lower != '':
            if not is_float(tot_visit_lower):
                QMessageBox.warning(
                self, 'Error', 'The total visits bounds must be valid numbers')
                return
            query += f"total_visits >= {tot_visit_lower} and "
        if tot_visit_upper != '':
            if not is_float(tot_visit_upper):
                QMessageBox.warning(
                self, 'Error', 'The total visits bounds must be valid numbers')
                return
            query += f"total_visits <= {tot_visit_upper} and "
        if price_lower != '':
            if not is_float(price_lower):
                QMessageBox.warning(
                self, 'Error', 'The price bounds must be valid numbers')
                return
            query += f"price >= {price_lower} and "
        if price_upper != '':
            if not is_float(price_upper):
                QMessageBox.warning(
                self, 'Error', 'The price bounds must be valid numbers')
                return
            query += f"price <= {price_upper} and "
        if not include_visited:
            query += f"my_visits = 0 and "
        if not include_soldout:
            query += f"ticket_remaining > 0 and "

        query = query.strip('and ')
        self.handleUpdateTable(query)


    def handleEventDetail(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            event_data = self.event_key_list[row_index]
            self.hide()
            self.visitor_event_detail = VisitorEventDetail(self, self.username, event_data[0], event_data[2], event_data[1])
            self.visitor_event_detail.show()
            self.visitor_event_detail.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()


    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        if (query == None):
            query = self.root_query

        self.table_rows = sqlQueryOutput(query, ['name', 'site_name', 'price', 'ticket_remaining', 'total_visits', 'my_visits'])
        self.event_key_list = sqlQueryOutput(query, ['name', 'site_name', 'start_date'])

        self.table_model = SimpleTableModel(self.table_headers, self.table_rows)
        self.table_view.setModel(self.table_model)

        self.curr_query = query




# SCREEN NUMBER 32
class StaffEventDetail(QWidget):
    def __init__(self, parent, event_name, start_date, site_name):
        super(StaffEventDetail, self).__init__()
        self.setWindowTitle("Event Detail")
        self.parent = parent
        self.event_name = event_name
        self.start_date = start_date
        self.site_name = site_name


        self.vbox = QVBoxLayout()

        query =  "select end_date, datediff(end_date, start_date) + 1 as 'Duration (days)',  "\
            + "capacity, price, description from event "\
            + f"where name = '{self.event_name}' "\
            + f"and start_date = '{self.start_date}' "\
            + f"and site_name = '{self.site_name}' "

        data = sqlQueryOutput(query, ['end_date', 'Duration (days)', 'capacity', 'price', 'description'])
        data = data[0]


        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Event: ']), ('QLabel', [self.event_name])],
            [('QLabel', ['Site: ']), ('QLabel', [self.site_name])],
            [('QLabel', ['Start Date: ']), ('QLabel', [self.start_date])],
            [('QLabel', ['End Date: ']), ('QLabel', [f'{data[0]}'])],
            [('QLabel', ['Duration (Days): ']), ('QLabel', [f'{data[1]}'])],
            [('QLabel', ['Capacity: ']), ('QLabel', [f'{data[2]}'])],
            [('QLabel', ['Price ($): ']), ('QLabel', [f'{data[3]}'])],
            [('QLabel', ['Description: '])],
            [('QPlainTextEdit', [f'{data[4]}', True])]
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))


        query2 = "select concat(U.fname, ' ', U.lname) as 'full_name' "\
            + "from user as U join event_staff_assignments as ESA "\
            + "on U.username = ESA.staff_user "\
            + f"where ESA.event_name = '{self.event_name}' "\
            + f"and ESA.start_date = '{self.start_date}' "\
            + f"and ESA.site_name = '{self.site_name}' "

        self.table_rows = sqlQueryOutput(query2, ['full_name'])
        self.headers = ["Staff Assigned"]
        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        self.table_view.setColumnWidth(0, 250)
        self.vbox.addWidget(self.table_view)

        self.hbox_list1 = []
        hbox_contents1 = [
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)


    def handleBack(self):
        self.close()
        self.parent.show()







# SCREEN NUMBER 31
class StaffViewSchedule(QWidget):
    def __init__(self, parent, username):
        super(StaffViewSchedule, self).__init__()
        self.setWindowTitle("View Schedule")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Event Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Description Keyword: ']), ('QLineEdit', [])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter']), ('QPushButton', ['View Event', 'handleViewEvent'])]
            ]
        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))


        self.root_query = "select E.name, E.site_name, E.start_date, E.end_date, count(staff_user) as 'Staff Count', E.description "\
            + "from event as E join event_staff_assignments as ESA "\
            + "on E.name = ESA.event_name "\
            + "and E.site_name = ESA.site_name "\
            + "and E.start_date = ESA.start_date "

        self.group_by = "group by E.name, E.start_date, E.site_name "
        query1 = self.root_query + self.group_by
        self.table_rows = sqlQueryOutput(query1, ['name', 'site_name', 'start_date', 'end_date', 'Staff Count'])


        self.headers = ["Event Name", 'Site Name', "Start Date", 'End Date', 'Staff Count']
        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        # self.table_view.setColumnWidth(0, 100)
        # self.table_view.setColumnWidth(1, 100)
        self.vbox.addWidget(self.table_view)

        self.hbox_list1 = []
        hbox_contents1 = [
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)



    def handleFilter(self):
        event_name = self.hbox_list[0][1][1].text()
        description_keyword = self.hbox_list[1][1][1].text()
        start_date = self.hbox_list[2][1][1].text()
        end_date = self.hbox_list[3][1][1].text()

        event_name_filter = (not (event_name == ''))
        description_keyword_filter = (not (description_keyword == ''))
        start_date_filter = (not (start_date == ''))
        end_date_filter = (not (end_date == ''))

        if start_date_filter:
            if not valid_date_check(start_date, self):
                return
        if end_date_filter:
            if not valid_date_check(end_date, self):
                return

        query = self.root_query
        sub_query = ""

        if event_name_filter:
            sub_query += f"and E.name = '{event_name}' "
        if description_keyword_filter:
            sub_query += f"and E.description like '%{description_keyword}%' "
        if start_date_filter:
            sub_query += f"and E.start_date >= '{start_date}' "
        if end_date_filter:
            sub_query += f"and E.end_date <= '{end_date}' "

        query += sub_query
        query += self.group_by
        self.handleUpdateTable(query)


    def handleViewEvent(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            event_data = self.table_rows[row_index]
            self.hide()
            self.admin_edit_transit = StaffEventDetail(self, event_data[0], event_data[2], event_data[1])
            self.admin_edit_transit.show()
            self.admin_edit_transit.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()


    def handleUpdateTable(self, query=None):
        if query == None:
            query = self.root_query + self.group_by

        self.table_rows = sqlQueryOutput(query, ['name', 'site_name', 'start_date', 'end_date', 'Staff Count'])
        self.table_model = SimpleTableModel(self.headers, self.table_rows)
        self.table_view.setModel(self.table_model)








# SCREEN NUMBER 30
class ManagerDailyDetail(QWidget):
    def __init__(self, parent, username, date):
        super(ManagerDailyDetail, self).__init__()
        self.setWindowTitle("Daily Detail")
        self.parent = parent
        self.username = username
        # self.site_name = site_name
        self.date = date

        sitequery = f"select name from site where manager_user = '{self.username}'"
        x = sqlQueryOutput(sitequery, ['name'])
        self.site_name = x[0][0]

        self.vbox = QVBoxLayout()


        self.drop_query = "drop temporary table if exists screen30;"
        self.temp_table_query = "create temporary table screen30 "\
            +"select distinct VE.event_name, "\
            +"group_concat(distinct ' ',U.fname, ' ', U.lname order by U.fname) as 'staff_names', "\
            +"count(VE.username) as 'visits' "\
            +"from user as U "\
            +"join event_staff_assignments as ESA "\
            +"on U.username = ESA.staff_user "\
            +"join event as E "\
            +"on E.name = ESA.event_name "\
            +"and E.site_name = ESA.site_name "\
            +"and E.start_date = ESA.start_date "\
            +"join visit_event as VE "\
            +"on E.name = VE.event_name "\
            +"and E.start_date = VE.start_date "\
            +f"where E.site_name = '{self.site_name}' "\
            +f"and E.start_date<= '{self.date}' and E.end_date>= '{self.date}' "\
            +"group by VE.event_name;"


        self.root_query = "select distinct event_name, visits, staff_names, E.price*visits "\
            +"as 'revenue' from screen30 join event as E "\
            +"on E.name = screen30.event_name;"

        cursor = connection.cursor()
        cursor.execute(self.drop_query)
        cursor.execute(self.temp_table_query)

        self.table_rows = sqlQueryOutput(self.root_query, ['event_name', 'staff_names', 'visits', 'revenue'])

        self.headers = ["Event Name", "Staff Names", 'Visits', 'Revenue']
        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        self.vbox.addWidget(self.table_view)


        self.hbox_list1 = []
        hbox_contents1 = [
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()





# SCREEN NUMBER 29
class ManagerSiteReport(QWidget):
    def __init__(self, parent, username):
        super(ManagerSiteReport, self).__init__()
        self.setWindowTitle("Site Report")
        self.parent = parent
        self.username = username

        sitequery = f"select name from site where manager_user = '{self.username}'"
        x = sqlQueryOutput(sitequery, ['name'])
        self.site_name = x[0][0]

        self.vbox = QVBoxLayout()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', [f'Site: {self.site_name}'])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QLabel', ['Event Count Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Staff Count Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Total Visits Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Total Revenue Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter']), ('QPushButton', ['Daily Detail', 'handleDailyDetail'])]
            ]
        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.drop_query = "drop temporary table if exists s29_dates; "
        self.temp_table_query = "create temporary table s29_dates "\
            + f"(select visit_date from visit_event where site_name = '{self.site_name}') "\
            + "union "\
            + f"(select visit_date from visit_site where site_name = '{self.site_name}'); "

        self.drop_query2 = "drop temporary table if exists s29;"
        self.temp_table_query2 = "create temporary table s29 "\
            + "select D_OUT.visit_date, "\
            + "(select count(distinct E.name, E.start_date, E.site_name) "\
            + "from event as E where E.start_date <= D_OUT.visit_date "\
            + f"and E.end_date >= D_OUT.visit_date and E.site_name = '{self.site_name}') as 'event_count', "\
            + "(select count(staff_user) from event as E "\
            + "join event_staff_assignments as ESA "\
            + "on E.name = ESA.event_name "\
            + "and E.site_name = ESA.site_name "\
            + "and E.start_date = ESA.start_date "\
            + "where E.start_date <= D_OUT.visit_date "\
            + f"and E.end_date >= D_OUT.visit_date and E.site_name = '{self.site_name}') as 'staff_count', "\
            + "ifnull((select count(username) "\
            + f"from visit_site where visit_site.site_name = '{self.site_name}' "\
            + "group by visit_date "\
            + "having visit_date = D_OUT.visit_date), 0) "\
            + "+ "\
            + f"ifnull((select count(username) from visit_event where visit_event.site_name = '{self.site_name}' "\
            + "group by visit_date "\
            + "having visit_date = D_out.visit_date), 0) "\
            + "as 'total_visits', "\
            + f"(select daily_revenue(D_OUT.visit_date, '{self.site_name}')) as 'total_revenue' "\
            + "from s29_dates as D_OUT "\
            + "order by D_OUT.visit_date; "
        self.root_query = "select * from s29 "

        cursor = connection.cursor()
        cursor.execute(self.drop_query)
        cursor.execute(self.temp_table_query)
        cursor.execute(self.drop_query2)
        cursor.execute(self.temp_table_query2)
        connection.commit()
        cursor.close()

        self.table_rows = sqlQueryOutput(self.root_query, ['visit_date', 'event_count', 'staff_count', 'total_visits', 'total_revenue'])

        self.headers = ["Date", "Event Count", 'Staff Count', 'Total Visits', 'Total Revenue ($)']
        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        self.vbox.addWidget(self.table_view)

        self.hbox_list1 = []
        hbox_contents1 = [
        [('QPushButton', ['Back', 'handleBack'])]
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.setLayout(self.vbox)



    def handleFilter(self):
        start_date = self.hbox_list[1][1][1].text()
        end_date = self.hbox_list[2][1][1].text()
        event_count_lower = self.hbox_list[3][1][1].text()
        event_count_upper = self.hbox_list[3][1][3].text()
        staff_count_lower = self.hbox_list[4][1][1].text()
        staff_count_upper = self.hbox_list[4][1][3].text()
        visits_lower = self.hbox_list[5][1][1].text()
        visits_upper = self.hbox_list[5][1][3].text()
        revenue_lower = self.hbox_list[6][1][1].text()
        revenue_upper = self.hbox_list[6][1][3].text()

        start_date_filter = (not (start_date == ''))
        end_date_filter = (not (end_date == ''))
        event_lower_filter = (not (event_count_lower == ''))
        event_upper_filter = (not (event_count_upper == ''))
        staff_lower_filter = (not (staff_count_lower == ''))
        staff_upper_filter = (not (staff_count_upper == ''))
        visits_lower_filter = (not (visits_lower == ''))
        visits_upper_filter = (not (visits_upper == ''))
        revenue_lower_filter = (not (revenue_lower == ''))
        revenue_upper_filter = (not (revenue_upper == ''))

        query = self.root_query
        sub_query = 'where '
        filter_count = 0

        if (start_date_filter):
            if not valid_date_check(start_date, self):
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"visit_date >= '{start_date}' "
                filter_count += 1
        if (end_date_filter):
            if not valid_date_check(end_date, self):
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"visit_date <= '{end_date}' "
                filter_count += 1
        if (event_lower_filter):
            if not is_float(event_count_lower):
                QMessageBox.warning(self, 'Error', 'The event count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"event_count >= '{event_count_lower}' "
                filter_count += 1
        if (event_upper_filter):
            if not is_float(event_count_upper):
                QMessageBox.warning(self, 'Error', 'The event count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"event_count <= '{event_count_upper}' "
                filter_count += 1

        if (staff_lower_filter):
            if not is_float(staff_count_lower):
                QMessageBox.warning(self, 'Error', 'The staff count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"staff_count >= '{staff_count_lower}' "
                filter_count += 1
        if (staff_upper_filter):
            if not is_float(staff_count_upper):
                QMessageBox.warning(self, 'Error', 'The staff count bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"staff_count <= '{staff_count_upper}' "
                filter_count += 1

        if (visits_lower_filter):
            if not is_float(visits_lower):
                QMessageBox.warning(self, 'Error', 'The total visits bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_visits >= '{visits_lower}' "
                filter_count += 1
        if (visits_upper_filter):
            if not is_float(visits_upper):
                QMessageBox.warning(self, 'Error', 'The total visits bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_visits <= '{visits_upper}' "
                filter_count += 1

        if (revenue_lower_filter):
            if not is_float(revenue_lower):
                QMessageBox.warning(self, 'Error', 'The total revenue bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_revenue >= '{revenue_lower}' "
                filter_count += 1
        if (revenue_upper_filter):
            if not is_float(revenue_upper):
                QMessageBox.warning(self, 'Error', 'The total revenue bounds must be valid numbers')
                return
            else:
                if filter_count:
                    sub_query += "and "
                sub_query += f"total_revenue <= '{revenue_upper}' "
                filter_count += 1

        if filter_count:
            query += sub_query

        self.handleUpdateTable(query)



    def handleDailyDetail(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            selected_site_name = self.table_rows[row_index][1]
            select_date = self.table_rows[row_index][0]

            self.hide()
            self.admin_edit_transit = ManagerDailyDetail(self, self.username, select_date)
            self.admin_edit_transit.show()
            self.admin_edit_transit.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)
        sqlInsertDeleteQuery(self.drop_query2)
        sqlInsertDeleteQuery(self.temp_table_query2)

        if query == None:
            query = self.root_query

        self.table_rows = sqlQueryOutput(query, ['visit_date', 'event_count', 'staff_count', 'total_visits', 'total_revenue'])

        self.table_model = SimpleTableModel(self.headers, self.table_rows)
        self.table_view.setModel(self.table_model)



# SCREEN NUMBER 28
class ManagerManageStaff(QWidget):
    def __init__(self, parent, username):
        super(ManagerManageStaff, self).__init__()
        self.setWindowTitle("Manage Staff")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        site_name_list = create_site_name_list()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Site: ']), ('QComboBox', [site_name_list])],
            [('QLabel', ['First Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Last Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter'])],
            ]
        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        self.table_model, self.table_view = createTable(["Staff Name", '# Event Shifts'], [['', '']])
        self.table_view.setColumnWidth(0, 100)
        self.table_view.setColumnWidth(1, 100)
        self.vbox.addWidget(self.table_view)



        self.hbox_list1 = []
        hbox_contents1 = [
        [('QPushButton', ['Back', 'handleBack'])],
        ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.setLayout(self.vbox)

    def handleFilter(self):
        site_name = self.hbox_list[0][1][1].currentText()
        first_name = self.hbox_list[1][1][1].text()
        last_name = self.hbox_list[2][1][1].text()
        start_date = self.hbox_list[3][1][1].text()
        end_date = self.hbox_list[4][1][1].text()

        date_pattern = r'[\d]{4}-[0,1][\d]{1}-[0,1,2,3][\d]{1}'
        date_check1 = re.fullmatch(date_pattern, start_date)
        date_check2 = re.fullmatch(date_pattern, end_date)

        if (end_date == '' or start_date == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in the date fields before filtering')
        elif (date_check1 == None or date_check2 == None):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid dates in the form YYYY-MM-DD')
        else:
            fname_filter = (not (first_name == ''))
            lname_filter = (not (last_name == ''))


            query = "select U.username, concat(U.fname, ' ', U.lname) as 'full_name', count(event_name) as '# Event Shifts'  "\
                + "from user as U "\
                + "join event_staff_assignments as ESA "\
                + "on U.username = ESA.staff_user "\
                + "join event as E "\
                + "on E.name = ESA.event_name "\
                + "and E.site_name = ESA.site_name "\
                + "and E.start_date = ESA.start_date "\
                + f"where ((E.start_date >= '{start_date}' and E.start_date <= '{end_date}') "\
                + f"or (E.end_date >= '{start_date}' and E.end_date <= '{end_date}')) "\
                + f"and E.site_name = '{site_name}' "


            if (fname_filter):
                query = query + f"and U.fname = '{first_name}' "
            if (lname_filter):
                query = query + f"and U.lname = '{last_name}' "

            query = query + "group by U.username order by U.lname"

            rows = sqlQueryOutput(query, ['full_name', '# Event Shifts'])
            self.table_model = SimpleTableModel(["Staff Name", '# Event Shifts'], rows)
            self.table_view.setModel(self.table_model)


    def handleBack(self):
        self.close()
        self.parent.show()




# SCREEN NUMBER 27
class ManagerCreateEvent(QWidget):
    def __init__(self, parent, username):
        super(ManagerCreateEvent, self).__init__()
        self.setWindowTitle("Create Event")
        self.parent = parent
        self.username = username

        query = f"select name from site where manager_user = '{self.username}'"
        x = sqlQueryOutput(query, ['name'])
        self.site_name = x[0][0]


        self.vbox = QVBoxLayout()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Price ($): ']), ('QLineEdit', [])],
            [('QLabel', ['Capacity: ']), ('QLineEdit', [])],
            [('QLabel', ['Minimum Staff Required: ']), ('QLineEdit', [])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QLabel', ['Description: '])],
            [('QPlainTextEdit', [])],
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        query = "select user.username, concat(user.fname, ' ', user.lname) as 'full_name' "\
            + "from employee join user using (username) "\
            + "where employee_type = 'Staff' " \
            + "order by user.username"
        self.staff_username_list = sqlQueryOutput(query, ["username"])
        self.staff_name_list = sqlQueryOutput(query, ["full_name"])

        self.hbox_list1 = []
        hbox_contents1 = [
            [('QLabel', ['Assign Staff']), ('QPushButton', ['Show Staff Available During Given Dates', 'handleFilterStaff']),]
            ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))


        self.table_model, self.table_view = createTable(["Name"], self.staff_name_list, singleSelection=False)
        self.table_view.setColumnWidth(0, 400)
        self.vbox.addWidget(self.table_view)

        self.hbox_list2 = []
        hbox_contents2 = [
            [('QPushButton', ['Create', 'handleCreate']), ('QPushButton', ['Back', 'handleBack']),]
            ]
        for i in hbox_contents2:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list2.append((x,y))

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.handleUpdateTable()
        self.parent.show()

    def handleCreate(self):
        event_name = self.hbox_list[0][1][1].text()
        price = self.hbox_list[1][1][1].text()
        capacity = self.hbox_list[2][1][1].text()
        min_staff_req = self.hbox_list[3][1][1].text()
        start_date = self.hbox_list[4][1][1].text()
        end_date = self.hbox_list[5][1][1].text()
        description = self.hbox_list[7][1][0].toPlainText()

        selected = len(self.table_view.selectedIndexes())

        query = "select exists (select name, start_date from event "\
            + "where site_name in ( "\
            + "select name from site "\
            + f"where manager_user = '{self.username}') "\
            + f"and name = '{event_name}' "\
            + f"and start_date = '{start_date}') "

        x = sqlQueryOutput(query)
        not_unique_keys = list(x[0].values())[0]

        date_pattern = r'[\d]{4}-[0,1][\d]{1}-[0,1,2,3][\d]{1}'
        date_check1 = re.fullmatch(date_pattern, start_date)
        date_check2 = re.fullmatch(date_pattern, end_date)

        if (event_name == '' or
            price == '' or
            capacity == '' or
            min_staff_req == '' or
            start_date == '' or
            end_date == '' or
            description == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
        elif (not is_int(capacity) or
            not is_float(price) or
            not is_int(min_staff_req)):
            QMessageBox.warning(
                self, 'Error', 'The price field must be valid decimal number, and the capacity and minimum staff required fields must be valid integers')
        elif (float(price) < 0 or float(price) >= 100):
            QMessageBox.warning(
                    self, 'Error', 'Price out of range')
        elif (int(min_staff_req) <= 0):
            QMessageBox.warning(
                self, 'Error', 'The minimum staff required field must be a positive integer')
        elif (date_check1 == None or date_check2 == None):
            QMessageBox.warning(
                    self, 'Error', 'Please enter valid dates in the form YYYY-MM-DD')
        elif (end_date < start_date):
            QMessageBox.warning(
                    self, 'Error', 'The end date must not be before the start date silly!')
        elif (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select one or more employees to work the event')
        elif (not_unique_keys):
            QMessageBox.warning(
                self, 'Error', 'The event name and start date provided are not unique to your site')
        elif (selected < int(min_staff_req)):
            QMessageBox.warning(
                self, 'Error', 'You have not selected enough staff to fulfill the minimum staff requirement')
        else:

            query = "select exists (select * from event "\
                + "where site_name in ( "\
                + "select name from site "\
                + f"where manager_user = '{self.username}') "\
                + f"and name = '{event_name}' "\
                + f"and ((start_date >= '{start_date}' and start_date <= '{end_date}') "\
                + f"or (end_date >= '{start_date}' and end_date <= '{end_date}'))) "

            y = sqlQueryOutput(query)
            overlap = list(x[0].values())[0]

            if (overlap):
                QMessageBox.warning(
                    self, 'Error', 'An event of the same name at this site overlaps with the given start and end dates')
            else:

                overlap_count = 0
                ESA_list = []

                for i in self.table_view.selectedIndexes():
                    # print(self.staff_username_list[i.row()][0])
                    username = self.staff_username_list[i.row()][0]
                    ESA_list.append(username)

                    query = "select exists (select EMP.username from employee as EMP " \
                        + "where EMP.employee_type = 'Staff' " \
                        + f"and EMP.username = '{username}' " \
                        + "and EMP.username not in ( " \
                        + "select distinct staff_user from event_staff_assignments as ESA " \
                        + "join event as E " \
                        + "on E.name = ESA.event_name " \
                        + "and E.site_name = ESA.site_name " \
                        + "and E.start_date = ESA.start_date " \
                        + f"where ((E.start_date >= '{start_date}' and E.start_date <= '{end_date}') " \
                        + f"or (E.end_date >= '{start_date}' and E.end_date <= '{end_date}'))) " \
                        + "order by EMP.username) "

                    x = sqlQueryOutput(query)
                    not_overlap = list(x[0].values())[0]

                    if (not not_overlap):
                        overlap_count += 1

                if (overlap_count):
                    QMessageBox.warning(
                        self, 'Error', 'One or more of the selected employees are already working during the given start and end dates')
                else:
                    price, capacity, min_staff_req = float(price), int(capacity), int(min_staff_req)
                    # pprint([event_name, price, capacity, min_staff_req, start_date, end_date, description])
                    # pprint(ESA_list)

                    query = "insert into event (name, start_date, site_name, end_date, price, capacity, min_staff_req, description) "\
                        + f"values ('{event_name}', '{start_date}', '{self.site_name}',  "\
                        + f"'{end_date}', {price}, {capacity}, {min_staff_req}, '{description}') "

                    sqlInsertDeleteQuery(query)

                    for username in ESA_list:
                        query = "insert into event_staff_assignments (staff_user, event_name, start_date, site_name) "\
                            + f"values ('{username}', '{event_name}', '{start_date}', '{self.site_name}') "
                        sqlInsertDeleteQuery(query)

                    QMessageBox.information(
                        self, 'Success', "You successfully created an event!", QMessageBox.Ok)

                    self.handleBack()



    def handleFilterStaff(self):
        start_date = self.hbox_list[4][1][1].text()
        end_date = self.hbox_list[5][1][1].text()

        if (start_date == '' or end_date == ''):
            QMessageBox.warning(
                self, 'Error', 'You must fill in the start and end date of the event before filtering to see available staff')
        else:
            query = "select EMP.username, concat(U.fname, ' ', U.lname) as 'full_name' from employee as EMP "\
                + "join user as U using (username) "\
                + "where EMP.employee_type = 'Staff' "\
                + "and EMP.username not in ( "\
                + "select distinct staff_user from event_staff_assignments as ESA "\
                + "join event as E "\
                + "on E.name = ESA.event_name "\
                + "and E.site_name = ESA.site_name "\
                + "and E.start_date = ESA.start_date "\
                + f"where ((E.start_date >= '{start_date}' and E.start_date <= '{end_date}') "\
                + f"or (E.end_date >= '{start_date}' and E.end_date <= '{end_date}'))) "\
                + "order by EMP.username "
            self.staff_username_list = sqlQueryOutput(query, ["username"])
            self.staff_name_list = sqlQueryOutput(query, ["full_name"])

            self.table_model = SimpleTableModel(["Name"], self.staff_name_list)
            self.table_view.setModel(self.table_model)








# SCREEN NUMBER 26
class ManagerViewEditEvent(QWidget):
    def __init__(self, parent, event_name, site_name, start_date, readOnly=False):
        super(ManagerViewEditEvent, self).__init__()
        self.setWindowTitle("View/Edit Event")
        self.parent = parent
        self.event_name = event_name
        self.start_date = start_date
        self.site_name = site_name
        self.readOnly = readOnly

        query1 = "select name, price, E.start_date, E.end_date, E.min_staff_req, capacity, description "\
            + "from event as E "\
            + "join event_staff_assignments as ESA "\
            + "on E.name = ESA.event_name "\
            + "and E.site_name = ESA.site_name "\
            + "and E.start_date = ESA.start_date "\
            + "left outer join visit_event as VE "\
            + "on E.name = VE.event_name "\
            + "and E.start_date = VE.start_date "\
            + "and E.site_name = VE.site_name "\
            + f"where E.name = '{self.event_name}' "\
            + f"and E.site_name = '{self.site_name}' "\
            + f"and E.start_date = '{self.start_date}' "\
            + "group by E.name, E.start_date, E.site_name "

        data1 = sqlQueryOutput(query1, ['name', 'price', 'start_date', 'end_date', 'min_staff_req', 'capacity', 'description'])
        data1 = data1[0]

        self.vbox = QVBoxLayout()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Name: ']), ('QLabel', [f'{data1[0]}'])],
            [('QLabel', ['Price ($): ']), ('QLabel', [f'{data1[1]}'])],
            [('QLabel', ['Capacity: ']), ('QLabel', [f'{data1[5]}'])],
            [('QLabel', ['Minimum Staff Required: ']), ('QLabel', [f'{data1[4]}'])],
            [('QLabel', ['Start Date: ']), ('QLabel', [f'{data1[2]}'])],
            [('QLabel', ['End Date: ']), ('QLabel', [f'{data1[3]}'])],
            [('QLabel', ['Description: '])],
            [('QPlainTextEdit', [f'{data1[6]}', self.readOnly])],
            ]

        self.end_date = data1[3]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))

        query = "select staff_user, concat(user.fname, ' ', user.lname) as 'full_name'  "\
            + "from event_staff_assignments as ESA "\
            + "join user on ESA.staff_user = user.username "\
            + f"where event_name = '{self.event_name}' "\
            + f"and start_date = '{self.start_date}' "\
            + f"and site_name = '{self.site_name}' "\
            + "order by staff_user "

        self.staff_username_list = sqlQueryOutput(query, ["staff_user"])
        self.staff_name_list = sqlQueryOutput(query, ["full_name"])
        for i in self.staff_name_list:
            i.append('Yes')

        query2 = "select EMP.username, concat(U.fname, ' ', U.lname) as 'full_name' from employee as EMP "\
            + "join user as U using (username) "\
            + "where EMP.employee_type = 'Staff' "\
            + "and EMP.username not in ( "\
            + "select distinct staff_user from event_staff_assignments as ESA "\
            + "join event as E "\
            + "on E.name = ESA.event_name "\
            + "and E.site_name = ESA.site_name "\
            + "and E.start_date = ESA.start_date "\
            + f"where ((E.start_date >= '{self.start_date}' and E.start_date <= '{self.end_date}') "\
            + f"or (E.end_date >= '{self.start_date}' and E.end_date <= '{self.end_date}'))) "\
            + "order by EMP.username "

        self.staff_username_list += sqlQueryOutput(query2, ['username'])
        self.staff_name_list += sqlQueryOutput(query2, ["full_name"])
        for i in self.staff_name_list:
            if len(i) == 1:
                i.append('No')


        self.table_model, self.table_view = createTable(["Name", "Assigned?"], self.staff_name_list, singleSelection=False)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 150)
        self.vbox.addWidget(self.table_view)


        self.hbox_list1 = []
        hbox_contents1 = [
            [('QLabel', ['Daily Visits Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Daily Revenue Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter'])]
            ]
        for i in hbox_contents1:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list1.append((x,y))

        self.drop_query = "drop temporary table if exists s26_table"
        self.temp_table_query = "create temporary table s26_table "\
            + "select VE.visit_date, count(username) as 'daily_visits', E.price * count(username) as 'daily_revenue' "\
            + "from visit_event as VE "\
            + "join event as E "\
            + "on E.name = VE.event_name "\
            + "and E.start_date = VE.start_date "\
            + "and E.site_name = VE.site_name "\
            + f"where E.name = '{self.event_name}' "\
            + f"and E.start_date = '{self.start_date}' "\
            + f"and E.site_name = '{self.site_name}' "\
            + "group by VE.visit_date "
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)
        self.root_query = "select * from s26_table "
        self.curr_query = self.root_query

        self.headers = ['Date', 'Daily Visits', 'Daily Revenue']
        self.table_rows = sqlQueryOutput(self.root_query, ['visit_date', 'daily_visits', 'daily_revenue'])
        self.table_model2, self.table_view2 = createTable(self.headers, self.table_rows)
        self.vbox.addWidget(self.table_view2)

        self.hbox_list2 = []
        hbox_contents2 = [
            [('QPushButton', ['Update', 'handleUpdate']), ('QPushButton', ['Back', 'handleBack']),]
            ]
        for i in hbox_contents2:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list2.append((x,y))

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.handleUpdateTable()
        self.parent.show()

    def handleUpdate(self):
        if (self.readOnly):
            QMessageBox.warning(
                self, 'Error', 'You can only update events at the site that you manage')
            return
        description = self.hbox_list[7][1][0].toPlainText()
        selected = len(self.table_view.selectedIndexes())
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
            return
        ESA_list = []
        for i in self.table_view.selectedIndexes():
            username = self.staff_username_list[i.row()][0]
            ESA_list.append(username)

        for i in ESA_list:

            query = "select exists (select EMP.username from employee as EMP " \
                + "where EMP.employee_type = 'Staff' " \
                + f"and EMP.username = '{i}' " \
                + "and EMP.username not in ( " \
                + "select distinct staff_user from event_staff_assignments as ESA " \
                + "join event as E " \
                + "on E.name = ESA.event_name " \
                + "and E.site_name = ESA.site_name " \
                + "and E.start_date = ESA.start_date " \
                + f"where ((E.start_date >= '{self.start_date}' and E.start_date <= '{self.end_date}') " \
                + f"or (E.end_date >= '{self.start_date}' and E.end_date <= '{self.end_date}'))) " \
                + "order by EMP.username) "

        query = f"delete from event_staff_assignments where event_name = '{self.event_name}' "\
            + f"and start_date = '{self.start_date}' and site_name = '{self.site_name}' "

        sqlInsertDeleteQuery(query)

        for i in ESA_list:

            query = "insert into event_staff_assignments (staff_user, event_name, start_date, site_name) "\
                + f"values ('{i}', '{self.event_name}', '{self.start_date}', '{self.site_name}') "

            sqlInsertDeleteQuery(query)



        query = f"update event set description = '{description}' where name = '{self.event_name}' "\
            + f"and start_date = '{self.start_date}' and site_name = '{self.site_name}' "
        sqlInsertDeleteQuery(query)

        QMessageBox.information(
            self, 'Success', "You successfully updated the event!", QMessageBox.Ok)

        self.handleBack()



    def handleFilter(self):
        visits_lower_bound = self.hbox_list1[0][1][1].text()
        visits_upper_bound = self.hbox_list1[0][1][3].text()
        revenue_lower_bound = self.hbox_list1[1][1][1].text()
        revenue_upper_bound = self.hbox_list1[1][1][3].text()

        revenue_lower_filter = (not (revenue_lower_bound == ''))
        revenue_upper_filter = (not (revenue_upper_bound == ''))
        visits_lower_filter = (not (visits_lower_bound == ''))
        visits_upper_filter = (not (visits_upper_bound == ''))

        if ((revenue_lower_filter and not is_float(revenue_lower_bound)) or
            (revenue_upper_filter and not is_float(revenue_upper_bound))):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid numbers for revenue range')
            return
        if ((visits_lower_filter and not is_float(visits_lower_bound)) or
            (visits_upper_filter and not is_float(visits_upper_bound))):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid numbers for total visits range')
            return

        query = self.root_query
        sub_query = "where "
        filter_count = 0

        if (revenue_lower_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"daily_revenue >= {revenue_lower_bound} "
            filter_count += 1
        if (revenue_upper_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"daily_revenue <= {revenue_upper_bound} "
            filter_count += 1
        if (visits_lower_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"daily_visits >= {visits_lower_bound} "
            filter_count += 1
        if (visits_upper_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"daily_visits <= {visits_upper_bound} "
            filter_count += 1

        if (filter_count):
            query += sub_query

        self.handleUpdateTable(query)

    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        if (query == None):
            query = self.root_query

        self.curr_query = query
        self.table_rows = sqlQueryOutput(self.curr_query, ['visit_date', 'daily_visits', 'daily_revenue'])
        self.table_model2 = SimpleTableModel(self.headers, self.table_rows)
        self.table_view2.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.table_view2.setModel(self.table_model2)









# SCREEN NUMBER 25
class ManagerManageEvent(QWidget):
    def __init__(self, parent, username):
        super(ManagerManageEvent, self).__init__()
        self.setWindowTitle("Manage Event")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        self.hbox_list = []
        hbox_contents = [
            [('QLabel', ['Name: ']), ('QLineEdit', [])],
            [('QLabel', ['Description Keyword: ']), ('QLineEdit', [])],
            [('QLabel', ['Start Date: ']), ('QLineEdit', [])],
            [('QLabel', ['End Date: ']), ('QLineEdit', [])],
            [('QLabel', ['Duration Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Total Visits Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QLabel', ['Total Revenue Range: ']), ('QLineEdit', []), ('QLabel', [' -- ']), ('QLineEdit', [])],
            [('QPushButton', ['Filter', 'handleFilter']),]
            ]

        for i in hbox_contents:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list.append((x,y))


        self.drop_query = "drop temporary table if exists s25 "
        sqlInsertDeleteQuery(self.drop_query)

        self.temp_table_query = "create temporary table s25 "\
            + "select E.name as 'Name', count(distinct staff_user) as 'Staff Count', datediff(E.end_date, E.start_date) + 1 as 'duration', "\
            + "count(VE.username) as 'total_visits', E.price * count(VE.username) as 'revenue', E.start_date, E.end_date, E.site_name, E.description "\
            + "from event as E "\
            + "join event_staff_assignments as ESA "\
            + "on E.name = ESA.event_name "\
            + "and E.site_name = ESA.site_name "\
            + "and E.start_date = ESA.start_date "\
            + "left outer join visit_event as VE "\
            + "on E.name = VE.event_name "\
            + "and E.start_date = VE.start_date "\
            + "and E.site_name = VE.site_name "\
            + "group by E.name, E.start_date, E.site_name "\
            + "order by E.name "

        sqlInsertDeleteQuery(self.temp_table_query)

        self.root_query = "select * from s25 "
        self.curr_query = self.root_query

        self.table_rows = sqlQueryOutput(self.root_query, ["Name", "Staff Count", "duration", "total_visits", "revenue"])
        self.headers = ["Name", "Staff Count", "Duration (days)", "Total Visits", "Total Revenue ($)"]

        self.event_key_list = sqlQueryOutput(self.root_query, ["Name", 'site_name', 'start_date'])

        self.table_model, self.table_view = createTable(self.headers, self.table_rows)
        self.vbox.addWidget(self.table_view)


        self.hbox_list2 = []
        hbox_contents2 = [
            [('QPushButton', ['Create', 'handleCreate']), ('QPushButton', ['View/Edit', 'handleViewEdit']), ('QPushButton', ['Delete', 'handleDelete']),],
            [('QPushButton', ['Back', 'handleBack']),]
            ]
        for i in hbox_contents2:
            (x, y) = createHBox(self, i)
            self.vbox.addLayout(x)
            self.hbox_list2.append((x,y))

        self.setLayout(self.vbox)

    def handleFilter(self):
        event_name = self.hbox_list[0][1][1].text()
        description_keyword = self.hbox_list[1][1][1].text()
        start_date = self.hbox_list[2][1][1].text()
        end_date = self.hbox_list[3][1][1].text()
        duration_lower_bound = self.hbox_list[4][1][1].text()
        duration_upper_bound = self.hbox_list[4][1][3].text()
        visits_lower_bound = self.hbox_list[5][1][1].text()
        visits_upper_bound = self.hbox_list[5][1][3].text()
        revenue_lower_bound = self.hbox_list[6][1][1].text()
        revenue_upper_bound = self.hbox_list[6][1][3].text()


        event_name_filter = (not (event_name == ''))
        description_keyword_filter = (not (description_keyword == ''))
        start_date_filter = (not (start_date == ''))
        end_date_filter = (not (end_date == ''))
        duration_lower_filter = (not (duration_lower_bound == ''))
        duration_upper_filter = (not (duration_upper_bound == ''))
        revenue_lower_filter = (not (revenue_lower_bound == ''))
        revenue_upper_filter = (not (revenue_upper_bound == ''))
        visits_lower_filter = (not (visits_lower_bound == ''))
        visits_upper_filter = (not (visits_upper_bound == ''))

        if (start_date_filter):
            if not (valid_date_check(start_date, self)):
                return
        if (end_date_filter):
            if not (valid_date_check(end_date, self)):
                return
        if ((duration_lower_filter and not is_float(duration_lower_bound)) or
            (duration_upper_filter and not is_float(duration_upper_bound))):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid numbers for duration range')
            return
        if ((revenue_lower_filter and not is_float(revenue_lower_bound)) or
            (revenue_upper_filter and not is_float(revenue_upper_bound))):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid numbers for revenue range')
            return
        if ((visits_lower_filter and not is_float(visits_lower_bound)) or
            (visits_upper_filter and not is_float(visits_upper_bound))):
            QMessageBox.warning(
                self, 'Error', 'Please enter valid numbers for total visits range')
            return


        filter_count = 0

        sub_query = "where "

        query = self.root_query
        if (event_name_filter):
            if (not filter_count):
                sub_query += f"name = '{event_name}' "
            else:
                sub_query += f"and name = '{event_name}' "
            filter_count += 1
        if (description_keyword_filter):
            if (not filter_count):
                sub_query += f"description like '%{description_keyword}%' "
            else:
                sub_query += f"and description like '%{description_keyword}%' "
            filter_count += 1
        if (start_date_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"start_date >= '{start_date}' "
            filter_count += 1
        if (end_date_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"end_date <= '{end_date}' "
            filter_count += 1
        if (duration_lower_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"duration >= {duration_lower_bound} "
            filter_count += 1
        if (duration_upper_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"duration <= {duration_upper_bound} "
            filter_count += 1
        if (revenue_lower_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"revenue >= {revenue_lower_bound} "
            filter_count += 1
        if (revenue_upper_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"revenue <= {revenue_upper_bound} "
            filter_count += 1
        if (visits_lower_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"total_visits >= {visits_lower_bound} "
            filter_count += 1
        if (visits_upper_filter):
            if (filter_count):
                sub_query += "and "
            sub_query += f"total_visits <= {visits_upper_bound} "
            filter_count += 1


        if (filter_count):
            query += sub_query
        self.handleUpdateTable(query)

    def handleCreate(self):
        self.hide()
        self.manager_create_event = ManagerCreateEvent(self, self.username)
        self.manager_create_event.show()
        self.manager_create_event.raise_()

    def handleViewEdit(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            event_data = self.event_key_list[row_index]
            query = "select exists (select manager_user from site "\
                f"where name = '{event_data[1]}' "\
                f"and manager_user = '{self.username}') "
            x = sqlQueryOutput(query)
            manager_check = list(x[0].values())[0]
            if (not manager_check):
                readOnly = True
            else:
                readOnly = False
            self.hide()
            self.admin_edit_transit = ManagerViewEditEvent(self, event_data[0], event_data[1], event_data[2], readOnly)
            self.admin_edit_transit.show()
            self.admin_edit_transit.raise_()

    def handleDelete(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            event_data = self.event_key_list[row_index]
            query = "select exists (select manager_user from site "\
                f"where name = '{event_data[1]}' "\
                f"and manager_user = '{self.username}') "
            x = sqlQueryOutput(query)
            manager_check = list(x[0].values())[0]
            if (not manager_check):
                QMessageBox.warning(
                self, 'Error', 'You can only delete events that are at the site that you manage')
            else:
                query = f"delete from event where name = '{event_data[0]}' and "\
                    + f"start_date = '{event_data[2]}' and site_name = '{event_data[1]}'"
                sqlInsertDeleteQuery(query)
                QMessageBox.information(
                    self, 'Success', "You successfully deleted the selected event!", QMessageBox.Ok)
                self.handleUpdateTable()


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_query)
        sqlInsertDeleteQuery(self.temp_table_query)

        if (query == None):
            query = self.root_query

        self.curr_query = query
        self.table_rows = sqlQueryOutput(self.curr_query, ["Name", "Staff Count", "duration", "total_visits", "revenue"])

        self.event_key_list = sqlQueryOutput(self.curr_query, ["Name", 'site_name', 'start_date'])

        self.table_model = SimpleTableModel(self.headers, self.table_rows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.table_view.setModel(self.table_model)




# SCREEN NUMBER 24
class AdminCreateTransit(QWidget):
    def __init__(self, parent):
        super(AdminCreateTransit, self).__init__()
        self.setWindowTitle("Create Transit")
        self.parent = parent

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type_dropdown = QComboBox(self)
        self.transport_type_dropdown.addItems(["MARTA", "Bus", "Bike"])
        self.hbox1.addWidget(self.transport_type_label)
        self.hbox1.addWidget(self.transport_type_dropdown)
        self.vbox.addLayout(self.hbox1)

        self.hbox2 = QHBoxLayout()
        self.route_label = QLabel("Route: ")
        self.route = QLineEdit()
        self.hbox2.addWidget(self.route_label)
        self.hbox2.addWidget(self.route)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.price_label = QLabel("Price ($): ")
        self.price = QLineEdit()
        self.hbox3.addWidget(self.price_label)
        self.hbox3.addWidget(self.price)
        self.vbox.addLayout(self.hbox3)

        site_name_list = create_site_name_list()

        self.connected_sites_checkboxes = []
        for i in site_name_list:
            cb = QCheckBox(i, self)
            cb.setChecked(False)
            self.connected_sites_checkboxes.append(cb)
            self.vbox.addWidget(cb)

        self.hbox4 = QHBoxLayout()
        self.create_btn = QPushButton('Create', self)
        self.create_btn.clicked.connect(self.handleCreate)
        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.hbox4.addWidget(self.create_btn)
        self.hbox4.addWidget(self.back_btn)
        self.vbox.addLayout(self.hbox4)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleCreate(self):
        transit_type = self.transport_type_dropdown.currentText()
        route = self.route.text()
        if (transit_type == '' or route == '' or self.price.text() == ''):
            QMessageBox.warning(
                    self, 'Error', 'Please fill in all fields')
        else:

            price = self.price.text()
            if (not is_float(price)):
                QMessageBox.warning(
                    self, 'Error', 'Please enter a valid decimal number for price')
                return
            if (float(price) < 0 or float(price) >= 100):
                QMessageBox.warning(
                        self, 'Error', 'Price out of range')
                return
            price = float(price)

            query = f"select exists (select route, type from transit where route = '{route}' and type = '{transit_type}')"
            cursor = connection.cursor()
            cursor.execute(query)
            transit_check = [line for line in cursor]
            cursor.close()
            unique_transit = list(transit_check[0].values())[0]
            if (unique_transit):
                QMessageBox.warning(
                        self, 'Error', 'The transit you are trying to create already exists')
                return

            connected_sites_count = 0
            for i in self.connected_sites_checkboxes:
                if (i.isChecked()):
                    connected_sites_count += 1
            if (connected_sites_count < 2):
                QMessageBox.warning(
                    self, 'Error', 'Transits must connect at least two sites')
                return


            query = f"insert into transit (type, route, price) values ('{transit_type}', '{route}', '{price}')"
            cursor = connection.cursor()
            cursor.execute(query)

            connected_sites_list = []

            for i in self.connected_sites_checkboxes:
                if (i.isChecked()):
                    connected_sites_list.append(i.text())

            for i in connected_sites_list:
                query1 = f"insert into transit_connections (site_name, "\
                    + f"transit_type, route) values ('{i}', '{transit_type}', '{route}')"
                cursor.execute(query1)
            connection.commit()
            cursor.close()
            QMessageBox.information(
            self, 'Success', "You successfully created the site!", QMessageBox.Ok)
            self.parent.handleUpdateTable()
            self.close()
            self.parent.show()



# SCREEN NUMBER 23
class AdminEditTransit(QWidget):
    def __init__(self, parent, route, transit_type):
        super(AdminEditTransit, self).__init__()
        self.setWindowTitle("Edit Transit")
        self.parent = parent
        self.route_d = route
        self.type_d = transit_type

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type = QLabel(self.type_d)
        self.hbox1.addWidget(self.transport_type_label)
        self.hbox1.addWidget(self.transport_type)
        self.vbox.addLayout(self.hbox1)

        self.hbox2 = QHBoxLayout()
        self.route_label = QLabel("Route: ")
        self.route = QLineEdit(self.route_d)
        self.hbox2.addWidget(self.route_label)
        self.hbox2.addWidget(self.route)
        self.vbox.addLayout(self.hbox2)

        cursor = connection.cursor()
        query = "select transit.route, type, price, site_name "\
            + "from transit join transit_connections "\
            + "where transit_connections.route = transit.route "\
            + "and transit_connections.transit_type = transit.type "\
            + f"and transit.route = '{self.route_d}' "\
            + f"and type = '{self.type_d}' "
        cursor.execute(query)
        transit_data = [line for line in cursor]
        cursor.close()
        self.price_d = transit_data[0]["price"]
        self.connected_sites_list = []
        for i in transit_data:
            self.connected_sites_list.append(i["site_name"])


        self.hbox3 = QHBoxLayout()
        self.price_label = QLabel("Price ($): ")
        self.price = QLineEdit(str(self.price_d))
        self.hbox3.addWidget(self.price_label)
        self.hbox3.addWidget(self.price)
        self.vbox.addLayout(self.hbox3)

        self.site_name_list = create_site_name_list()

        self.connected_sites_checkboxes = []
        for i in self.site_name_list:
            cb = QCheckBox(i, self)
            if (i in self.connected_sites_list):
                cb.setChecked(True)
            else:
                cb.setChecked(False)
            self.connected_sites_checkboxes.append(cb)
            self.vbox.addWidget(cb)

        self.hbox4 = QHBoxLayout()
        self.update_btn = QPushButton('Update', self)
        self.update_btn.clicked.connect(self.handleUpdate)
        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.hbox4.addWidget(self.update_btn)
        self.hbox4.addWidget(self.back_btn)
        self.vbox.addLayout(self.hbox4)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdate(self):
        route = self.route.text()
        price = self.price.text()
        connections_list = []
        for i in range(len(self.connected_sites_checkboxes)):
            if (self.connected_sites_checkboxes[i].checkState()):
                connections_list.append(self.site_name_list[i])

        if (route == '' or price == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
            return

        if (not is_float(price)):
            QMessageBox.warning(
                self, 'Error', 'Please enter a valid decimal number for price')
            return
        if (float(price) < 0 or float(price) >= 100):
            QMessageBox.warning(
                self, 'Error', 'Price out of range')
            return

        if (route != self.route_d):
            query = f"select exists (select * from transit where type = '{self.type_d}' and route = '{route}')"
            x = sqlQueryOutput(query)
            already_exists = list(x[0].values())[0]
            if (already_exists):
                QMessageBox.warning(
                    self, 'Error', 'This route, type combination already exists as a transit')
                return

        if (len(connections_list) < 2):
            QMessageBox.warning(
                    self, 'Error', 'Transits must connect at least two sites')
            return

        query = f"delete from transit_connections where transit_type = '{self.type_d}' and route = '{self.route_d}'"
        sqlInsertDeleteQuery(query)

        query = f"update transit set route = '{route}', price = {price} "\
            + f"where type = '{self.type_d}' and route = '{self.route_d}' "
        sqlInsertDeleteQuery(query)

        for i in connections_list:
            query = "insert into transit_connections (site_name, transit_type, route) "\
                + f"values ('{i}', '{self.type_d}', '{route}') "
            sqlInsertDeleteQuery(query)

        QMessageBox.information(
                self, 'Success', "You successfully updated the site!", QMessageBox.Ok)
        self.parent.handleUpdateTable()
        self.close()
        self.parent.show()






# SCREEN NUMBER 22
class AdminManageTransit(QWidget):
    def __init__(self, parent, username):
        super(AdminManageTransit, self).__init__()
        self.setWindowTitle("Manage Transit")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.hbox4 = QHBoxLayout()

        site_name_list = create_site_name_list()

        self.contain_site_label = QLabel("Contain Site: ")
        self.contain_site_dropdown = QComboBox(self)
        self.contain_site_dropdown.addItems(site_name_list)
        self.hbox1.addWidget(self.contain_site_label)
        self.hbox1.addWidget(self.contain_site_dropdown)
        self.vbox.addLayout(self.hbox1)

        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type_dropdown = QComboBox(self)
        self.transport_type_dropdown.addItems(["--ALL--", "MARTA", "Bus", "Bike"])
        self.hbox2.addWidget(self.transport_type_label)
        self.hbox2.addWidget(self.transport_type_dropdown)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.route_label = QLabel("Route: ")
        self.route = QLineEdit(self)
        self.hbox3.addWidget(self.route_label)
        self.hbox3.addWidget(self.route)
        self.vbox.addLayout(self.hbox3)

        self.price_range_label = QLabel("Price Range: ")
        self.lower_price_bound = QLineEdit(self)
        self.dash_label = QLabel(" -- ")
        self.upper_price_bound = QLineEdit(self)
        self.hbox4.addWidget(self.price_range_label)
        self.hbox4.addWidget(self.lower_price_bound)
        self.hbox4.addWidget(self.dash_label)
        self.hbox4.addWidget(self.upper_price_bound)
        self.vbox.addLayout(self.hbox4)

        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)
        self.vbox.addWidget(self.filter_btn)

        self.root_query = "select T.route, T.type, T.price, count(distinct site_name) as '# Connected Sites', count(TT.take_date) as '# Transit Logged' "\
            + "from transit as T "\
            + "join transit_connections as TC "\
            + "on T.route = TC.route "\
            + "and T.type = TC.transit_type "\
            + "left outer join take_transit as TT "\
            + "on TT.route = T.route "\
            + "and TT.transit_type = T.type "

        query = self.root_query + "group by T.route, T.type "
        self.curr_query = query

        self.headers = ['route', 'type', 'price', '# Connected Sites', '# Transit Logged']
        self.table_rows = sqlQueryOutput(query, self.headers)


        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites", "# Transit Logged"], self.table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)


        self.hbox5 = QHBoxLayout()
        self.create_btn = QPushButton('Create', self)
        self.create_btn.clicked.connect(self.handleCreate)
        self.edit_btn = QPushButton('Edit', self)
        self.edit_btn.clicked.connect(self.handleEdit)
        self.delete_btn = QPushButton('Delete', self)
        self.delete_btn.clicked.connect(self.handleDelete)
        self.hbox5.addWidget(self.create_btn)
        self.hbox5.addWidget(self.edit_btn)
        self.hbox5.addWidget(self.delete_btn)
        self.vbox.addLayout(self.hbox5)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)

    def handleFilter(self):
        site = self.contain_site_dropdown.currentText()
        transit_type = self.transport_type_dropdown.currentText()
        lower_price_bound = self.lower_price_bound.text()
        upper_price_bound = self.upper_price_bound.text()
        route = self.route.text()

        lower_price_bound_filter = (not (lower_price_bound == ''))
        upper_price_bound_filter = (not (upper_price_bound == ''))
        route_filter = (not (route == ''))
        transit_type_filter = (not (transit_type == '--ALL--'))


        query = self.root_query + f"where (T.route, T.type) in (select route, transit_type from transit_connections where site_name = '{site}') "

        if (lower_price_bound_filter and not is_float(lower_price_bound)):
            QMessageBox.warning(
                self, 'Error', 'The price filters must be valid decimal numbers')
        if (upper_price_bound_filter and not is_float(upper_price_bound)):
            QMessageBox.warning(
                self, 'Error', 'The price filters must be valid decimal numbers')

        if (lower_price_bound_filter):
            query = query + f"and T.price >= {float(lower_price_bound)} "
        if (upper_price_bound_filter):
            query = query + f"and T.price <= {float(upper_price_bound)} "
        if (transit_type_filter):
            query = query + f"and T.type = '{transit_type}' "
        if (route_filter):
            query = query + f"and T.route = '{route}' "

        query = query + "group by T.route, T.type "
        self.curr_query = query
        self.handleUpdateTable(query)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleCreate(self):
        self.hide()
        self.admin_create_transit = AdminCreateTransit(self)
        self.admin_create_transit.show()
        self.admin_create_transit.raise_()

    def handleEdit(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            route = self.table_model.data[row_index][0]
            transport_type = self.table_model.data[row_index][1]
            self.hide()
            self.admin_edit_transit = AdminEditTransit(self, route, transport_type)
            self.admin_edit_transit.show()
            self.admin_edit_transit.raise_()



    def handleDelete(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            route = self.table_model.data[row_index][0]
            transit_type = self.table_model.data[row_index][1]
            query = f"delete from transit where route = '{route}' and type = '{transit_type}'"
            sqlInsertDeleteQuery(query)
            QMessageBox.information(
                self, 'Success', "You successfully deleted the selected site!", QMessageBox.Ok)
            self.handleUpdateTable(self.curr_query)



    def handleUpdateTable(self, query=None):
        if (query == None):
            query = self.root_query + "group by T.route, T.type "

        self.table_rows = sqlQueryOutput(query, self.headers)
        self.table_model = SimpleTableModel(self.headers, self.table_rows)
        self.table_view.setModel(self.table_model)
















# SCREEN NUMBER 21
class AdminCreateSite(QWidget):
    def __init__(self, parent):
        super(AdminCreateSite, self).__init__()
        self.setWindowTitle("Create Site")
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.name_label = QLabel("Name: ")
        self.name = QLineEdit()
        self.hbox1.addWidget(self.name_label)
        self.hbox1.addWidget(self.name)
        self.vbox.addLayout(self.hbox1)

        self.hbox2 = QHBoxLayout()
        self.zipcode_label = QLabel("Zipcode: ")
        self.zipcode = QLineEdit()
        self.hbox2.addWidget(self.zipcode_label)
        self.hbox2.addWidget(self.zipcode)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.address_label = QLabel("Address: ")
        self.address = QLineEdit()
        self.hbox3.addWidget(self.address_label)
        self.hbox3.addWidget(self.address)
        self.vbox.addLayout(self.hbox3)

        cursor = connection.cursor()
        query = "select username, concat(fname, ' ', lname) as full_name " \
            + "from employee join user using (username) " \
            + "where employee_type = 'Manager' " \
            + "and username not in (select manager_user from site) "
        cursor.execute(query)
        manager_data = [line for line in cursor]
        cursor.close()
        manager_dropdown_list = []
        self.manager_username_list = []
        for i in manager_data:
            manager_dropdown_list.append(i["full_name"])
            self.manager_username_list.append(i["username"])

        self.hbox4 = QHBoxLayout()
        self.manager_label = QLabel("Manager: ")
        self.manager_dropdown = QComboBox(self)
        self.manager_dropdown.addItems(manager_dropdown_list)
        self.hbox4.addWidget(self.manager_label)
        self.hbox4.addWidget(self.manager_dropdown)
        self.vbox.addLayout(self.hbox4)

        self.cb = QCheckBox('Open Every Day?', self)
        self.cb.setChecked(False)
        self.vbox.addWidget(self.cb)

        self.hbox5 = QHBoxLayout()
        self.create_btn = QPushButton('Create', self)
        self.create_btn.clicked.connect(self.handleCreate)
        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.hbox5.addWidget(self.create_btn)
        self.hbox5.addWidget(self.back_btn)
        self.vbox.addLayout(self.hbox5)


        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleCreate(self):
        name = self.name.text()
        zipcode = self.zipcode.text()
        address = self.address.text()
        if (len(self.manager_username_list) == 0):
            QMessageBox.warning(
                    self, 'Error', 'There are no available managers')
        else:
            manager = self.manager_username_list[self.manager_dropdown.currentIndex()]

            cursor = connection.cursor()
            query = "select name from site"
            cursor.execute(query)
            site_data = [line for line in cursor]
            cursor.close()
            site_name_list = []
            for i in site_data:
                site_name_list.append(i["name"])

            if (self.cb.isChecked()):
                openeveryday = 'Yes'
            else:
                openeveryday = 'No'


            if (name == '' or zipcode == ''):
                QMessageBox.warning(
                        self, 'Error', 'Please fill in the name and zipcode fields')
            elif (name in site_name_list):
                QMessageBox.warning(
                        self, 'Error', 'This site name already exists')
            elif (len(zipcode) != 5 or not is_int(zipcode)):
                QMessageBox.warning(
                        self, 'Error', 'Please enter a valid 5 digit zipcode')
            else:
                cursor = connection.cursor()
                if (address == ''):
                    query = "insert into site (name, zipcode, openeveryday, manager_user) "\
                    + f"values ('{name}', '{zipcode}', '{openeveryday}', '{manager}')"
                else:
                    query = "insert into site (name, address, zipcode, openeveryday, manager_user) "\
                        + f"values ('{name}', '{address}', '{zipcode}', '{openeveryday}', '{manager}')"
                cursor.execute(query)
                connection.commit()
                cursor.close()
                QMessageBox.information(
                    self, 'Success', "You successfully created a new site!", QMessageBox.Ok)
                self.close()
                self.parent.show()








# SCREEN NUMBER 20
class AdminEditSite(QWidget):
    def __init__(self, parent, site_name):
        super(AdminEditSite, self).__init__()
        self.setWindowTitle("Edit Site")
        self.parent = parent
        self.site_name_d = site_name
        self.vbox = QVBoxLayout()

        cursor = connection.cursor()
        query = "select name, zipcode, address, concat(fname, ' ', lname)  as full_name, " \
            + "openeveryday from site join user where manager_user = username " \
            + f"and name = '{self.site_name_d}'"
        cursor.execute(query)
        site_data = [line for line in cursor]
        cursor.close()
        self.zipcode_d = site_data[0]["zipcode"]
        self.address_d = site_data[0]["address"]
        self.manager_d = site_data[0]["full_name"]
        self.openeveryday_d = site_data[0]["openeveryday"]


        self.hbox1 = QHBoxLayout()
        self.name_label = QLabel("Name: ")
        self.name = QLineEdit(self.site_name_d)
        self.hbox1.addWidget(self.name_label)
        self.hbox1.addWidget(self.name)
        self.vbox.addLayout(self.hbox1)

        self.hbox2 = QHBoxLayout()
        self.zipcode_label = QLabel("Zipcode: ")
        self.zipcode = QLineEdit(self.zipcode_d)
        self.hbox2.addWidget(self.zipcode_label)
        self.hbox2.addWidget(self.zipcode)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.address_label = QLabel("Address: ")
        self.address = QLineEdit(self.address_d)
        self.hbox3.addWidget(self.address_label)
        self.hbox3.addWidget(self.address)
        self.vbox.addLayout(self.hbox3)

        cursor = connection.cursor()
        query = "(select manager_user, concat(fname, ' ', lname)  as full_name "\
            + "from site join user where manager_user = username "\
            + f"and name = '{self.site_name_d}') "\
            + "union "\
            + "(select username, concat(fname, ' ', lname) as full_name  "\
            + "from employee join user using (username)  "\
            + "where employee_type = 'Manager'  "\
            + "and username not in (select manager_user from site) "\
            + "order by user.lname) "

        self.manager_dropdown_list = [i[0] for i in sqlQueryOutput(query, ["full_name"])]
        self.manager_username_list = [i[0] for i in sqlQueryOutput(query, ['manager_user'])]


        self.hbox4 = QHBoxLayout()
        self.manager_label = QLabel("Manager: ")
        self.manager_dropdown = QComboBox(self)
        self.manager_dropdown.addItems(self.manager_dropdown_list)
        self.hbox4.addWidget(self.manager_label)
        self.hbox4.addWidget(self.manager_dropdown)
        self.vbox.addLayout(self.hbox4)

        self.cb = QCheckBox('Open Every Day?', self)
        if (self.openeveryday_d == 'Yes'):
            self.cb.setChecked(True)
        else:
            self.cb.setChecked(False)
        self.vbox.addWidget(self.cb)

        self.hbox5 = QHBoxLayout()
        self.update_btn = QPushButton('Update', self)
        self.update_btn.clicked.connect(self.handleUpdate)
        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.hbox5.addWidget(self.update_btn)
        self.hbox5.addWidget(self.back_btn)
        self.vbox.addLayout(self.hbox5)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdate(self):

        site_name = self.name.text()
        zipcode = self.zipcode.text()
        address = self.address.text()
        manager = self.manager_username_list[self.manager_dropdown.currentIndex()]
        openeveryday = self.cb.checkState()

        if (site_name == '' or zipcode == '' or address == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
            return
        if (len(zipcode) != 5 or not is_int(zipcode)):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 5 digit zip code')
            return
        o = ''
        if (openeveryday):
            o = 'Yes'
        else:
            o = 'No'

        query = f"update site set name = '{site_name}', zipcode = '{zipcode}', address = '{address}', "\
            f"manager_user = '{manager}', openeveryday = '{o}' where name = '{self.site_name_d}' "

        sqlInsertDeleteQuery(query)
        QMessageBox.information(
                self, 'Success', "You successfully updated this site!", QMessageBox.Ok)

        self.parent.handleUpdateTable()
        self.handleBack()




# SCREEN NUMBER 19
class AdminManageSite(QWidget):
    def __init__(self, parent, username):
        super(AdminManageSite, self).__init__()
        self.setWindowTitle("Manage Site")
        self.parent = parent
        self.username = username

        self.vbox = QVBoxLayout()

        site_name_list = create_site_name_list()
        site_name_list.insert(0, "--ALL--")
        self.hbox1 = QHBoxLayout()
        self.site_label = QLabel("Site: ")
        self.site_dropdown = QComboBox(self)
        self.site_dropdown.addItems(site_name_list)
        self.hbox1.addWidget(self.site_label)
        self.hbox1.addWidget(self.site_dropdown)
        self.vbox.addLayout(self.hbox1)


        self.root_query = "select name, concat(fname, ' ', lname)  as full_name, " \
            + "openeveryday, manager_user from site join user where manager_user = username "

        self.table_rows = sqlQueryOutput(self.root_query, ['name', 'full_name', 'openeveryday'])
        self.curr_query = self.root_query

        self.manager_name_list = [i[0] for i in sqlQueryOutput(self.root_query, ['full_name'])]
        self.manager_name_list.insert(0, "--ALL--")
        self.manager_username_list = [i[0] for i in sqlQueryOutput(self.root_query, ['manager_user'])]
        self.manager_username_list.insert(0, "--ALL--")


        self.hbox2 = QHBoxLayout()
        self.manager_label = QLabel("Manager: ")
        self.manager_dropdown = QComboBox(self)
        self.manager_dropdown.addItems(self.manager_name_list)
        self.hbox2.addWidget(self.manager_label)
        self.hbox2.addWidget(self.manager_dropdown)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.openeveryday_label = QLabel("Open Every Day: ")
        self.openeveryday_dropdown = QComboBox(self)
        self.openeveryday_dropdown.addItems(["No", "Yes"])
        self.hbox3.addWidget(self.openeveryday_label)
        self.hbox3.addWidget(self.openeveryday_dropdown)
        self.vbox.addLayout(self.hbox3)

        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)
        self.vbox.addWidget(self.filter_btn)

        self.table_model = SimpleTableModel(["Name", "Manager", "Open Every Day"], self.table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)

        self.hbox4 = QHBoxLayout()
        self.create_btn = QPushButton('Create', self)
        self.create_btn.clicked.connect(self.handleCreate)
        self.edit_btn = QPushButton('Edit', self)
        self.edit_btn.clicked.connect(self.handleEdit)
        self.delete_btn = QPushButton('Delete', self)
        self.delete_btn.clicked.connect(self.handleDelete)
        self.hbox4.addWidget(self.create_btn)
        self.hbox4.addWidget(self.edit_btn)
        self.hbox4.addWidget(self.delete_btn)
        self.vbox.addLayout(self.hbox4)


        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)

    def handleFilter(self):
        site = self.site_dropdown.currentText()
        manager = self.manager_username_list[self.manager_dropdown.currentIndex()]
        openeveryday = self.openeveryday_dropdown.currentText()

        site_filter = (not (site == '--ALL--'))
        manager_filter = (not (manager == '--ALL--'))

        query = self.root_query + f"and openeveryday = '{openeveryday}' "

        if (site_filter):
            query = query + f"and name = '{site}' "
        if manager_filter:
            query = query + f"and manager_user = '{manager}' "

        self.handleUpdateTable(query)
        self.curr_query = query


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleCreate(self):
        self.hide()
        self.admin_create_site = AdminCreateSite(self)
        self.admin_create_site.show()
        self.admin_create_site.raise_()

    def handleEdit(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            site_name = self.table_model.data[row_index][0]
            self.hide()
            self.admin_edit_site = AdminEditSite(self, site_name)
            self.admin_edit_site.show()
            self.admin_edit_site.raise_()


    def handleDelete(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            site_name = self.table_model.data[row_index][0]
            cursor = connection.cursor()
            query = f"delete from site where name = '{site_name}'"
            cursor.execute(query)
            connection.commit()
            cursor.close()
            QMessageBox.information(
                    self, 'Success', "You successfully deleted the selected site!", QMessageBox.Ok)
            self.handleFilter()


    def handleUpdateTable(self, query=None):
        if (query == None):
            query = self.root_query

        self.table_rows = sqlQueryOutput(query, ['name', 'full_name', 'openeveryday'])
        self.table_model = SimpleTableModel(["Name", "Manager", "Open Every Day"], self.table_rows)
        self.table_view.setModel(self.table_model)




# SCREEN NUMBER 18
class AdminManageUser(QWidget):
    def __init__(self, parent, username):
        super(AdminManageUser, self).__init__()
        self.setWindowTitle("Manage Profile")
        self.parent = parent
        self.username_d = username

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.username_label = QLabel("Username: ")
        self.username = QLineEdit(self)
        self.hbox1.addWidget(self.username_label)
        self.hbox1.addWidget(self.username)
        self.vbox.addLayout(self.hbox1)

        self.hbox2 = QHBoxLayout()
        self.type_label = QLabel("Type: ")
        self.type_dropdown = QComboBox(self)
        self.type_dropdown.addItems(["User", "Visitor", "Staff", "Manager"])
        self.hbox2.addWidget(self.type_label)
        self.hbox2.addWidget(self.type_dropdown)
        self.vbox.addLayout(self.hbox2)

        self.hbox3 = QHBoxLayout()
        self.status_label = QLabel("Status: ")
        self.status_dropdown = QComboBox(self)
        self.status_dropdown.addItems(["--ALL--", "Approved", "Pending", "Declined"])
        self.hbox3.addWidget(self.status_label)
        self.hbox3.addWidget(self.status_dropdown)
        self.vbox.addLayout(self.hbox3)

        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)
        self.vbox.addWidget(self.filter_btn)

        self.drop_temp_table = "drop temporary table if exists s18_table;"

        self.temp_table_query = "create temporary table s18_table "\
            + "select U.username, count(E.email) as 'email count', "\
            + "(case U.user_type when 'User' then 'User'  "\
            + "when 'Visitor' then 'Visitor'  "\
            + "when 'Employee' then (select employee_type from employee where username = U.username) "\
            + "else null end) as 'user_type', U.status  "\
            + "from user as U  "\
            + "join email as E "\
            + "using (username) "\
            + "left outer join employee as EMP "\
            + "using (username) "\
            + "group by U.username; "

        sqlInsertDeleteQuery(self.drop_temp_table)
        sqlInsertDeleteQuery(self.temp_table_query)
        self.root_query = "select * from s18_table where user_type <> 'Admin'"
        self.curr_query = self.root_query

        self.table_rows = sqlQueryOutput(self.root_query, ['username', 'email count', 'user_type', 'status'])

        self.table_model = SimpleTableModel(["Username", "Email Count", "User Type", "Status"], self.table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)

        self.hbox4 = QHBoxLayout()
        self.approve_btn = QPushButton('Approve', self)
        self.approve_btn.clicked.connect(self.handleApprove)
        self.decline_btn = QPushButton('Decline', self)
        self.decline_btn.clicked.connect(self.handleDecline)
        self.hbox4.addWidget(self.approve_btn)
        self.hbox4.addWidget(self.decline_btn)
        self.vbox.addLayout(self.hbox4)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)

    def handleFilter(self):

        user_type = self.type_dropdown.currentText()
        status = self.status_dropdown.currentText()
        username = self.username.text()

        status_filter = (not (status == '--ALL--'))
        username_filter = (not (username == ''))

        sqlInsertDeleteQuery(self.drop_temp_table)
        sqlInsertDeleteQuery(self.temp_table_query)

        query = self.root_query + f"and user_type = '{user_type}' "
        if (status_filter):
            query = query + f"and status = '{status}'"
        if (username_filter):
            query = query + f"and username = '{username}'"

        self.handleUpdateTable(query)
        self.curr_query = query


    def handleApprove(self):
        username = check_selected(self.table_view, self.table_model, self, [0, 3])
        if (username != None):
            if username[1] == 'Approved':
                QMessageBox.warning(
                    self, 'Error', 'This account has already been approved')
                return
            query = f"update user set status = 'Approved' where username = '{username[0]}'"
            sqlInsertDeleteQuery(query)
            QMessageBox.information(
                self, 'Congrats!', f"You successfully approved user '{username[0]}'!", QMessageBox.Ok)
            self.handleUpdateTable(self.curr_query)

    def handleDecline(self):
        username = check_selected(self.table_view, self.table_model, self, [0, 3])
        if (username != None):
            if username[1] == 'Approved':
                QMessageBox.warning(
                    self, 'Error', 'You cannot decline an account that has already been approved')
                return
            query = f"update user set status = 'Declined' where username = '{username[0]}'"
            sqlInsertDeleteQuery(query)
            QMessageBox.information(
                self, 'Welp!', f"You just declined user '{username[0]}'!", QMessageBox.Ok)
            self.handleUpdateTable(self.curr_query)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdateTable(self, query=None):
        sqlInsertDeleteQuery(self.drop_temp_table)
        sqlInsertDeleteQuery(self.temp_table_query)
        if (query == None):
            query = self.root_query

        self.table_rows = sqlQueryOutput(query, ['username', 'email count', 'user_type', 'status'])
        self.table_model = SimpleTableModel(["Username", "Email Count", "User Type", "Status"], self.table_rows)
        self.table_view.setModel(self.table_model)




# SCREEN NUMBER 17
class EmployeeManageProfile(QWidget):
    def __init__(self, parent, username):
        super(EmployeeManageProfile, self).__init__()
        self.setWindowTitle("Manage Profile")

        self.username_d = username
        self.parent = parent

        cursor = connection.cursor()
        query = "select fname, lname, username, employeeID, phone, address, city, state, zipcode, employee_type " \
            + f"from user join employee using (username) where username = '{self.username_d}' "
        cursor.execute(query)
        emp_data = [line for line in cursor]
        self.fname_d = emp_data[0]["fname"]
        self.lname_d = emp_data[0]["lname"]
        self.employeeID_d = emp_data[0]["employeeID"]
        self.address_d = emp_data[0]["address"]
        self.city_d = emp_data[0]["city"]
        self.state_d = emp_data[0]["state"]
        self.zipcode_d = emp_data[0]["zipcode"]
        self.employee_type_d = emp_data[0]["employee_type"]
        self.phone_d = emp_data[0]["phone"]
        cursor.close()

        self.site_name_d = " "
        if self.employee_type_d == 'Manager':
            cursor = connection.cursor()
            query_manager_site = "select name " \
                + "from employee join site " \
                + "where manager_user = username " \
                + f"and username = '{self.username_d}' "
            cursor.execute(query_manager_site)
            data = [line for line in cursor]
            self.site_name_d = data[0]["name"]
            cursor.close()

        query_email = "select email from user join email "\
            + f"using (username) where username = '{self.username_d}'"
        cursor = connection.cursor()
        cursor.execute(query_email)
        email_data = [line for line in cursor]
        self.email_list = []
        for i in email_data:
            self.email_list.append([i["email"]])
        self.original_email_list = self.email_list
        cursor.close()

        self.vbox = QVBoxLayout()


        self.firstname = QLineEdit(self.fname_d)
        self.lastname = QLineEdit(self.lname_d)
        self.username = QLabel(self.username_d)
        self.phone = QLineEdit(self.phone_d)
        self.address_string_d = f"{self.address_d}, {self.city_d}, {self.state_d} {self.zipcode_d}"
        self.address = QLabel(self.address_string_d)
        self.employeeID = QLabel("{:09d}".format(self.employeeID_d))
        self.site_name = QLabel(self.site_name_d)
        self.form_group_box = QGroupBox()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("First Name: "), self.firstname)
        self.form_layout.addRow(QLabel("Last Name: "), self.lastname)
        self.form_layout.addRow(QLabel("Username: "), self.username)
        self.form_layout.addRow(QLabel("Site Name: "), self.site_name)
        self.form_layout.addRow(QLabel("Employee ID: "), self.employeeID)
        self.form_layout.addRow(QLabel("Phone: "), self.phone)
        self.form_layout.addRow(QLabel("Address: "), self.address)
        self.form_group_box.setLayout(self.form_layout)
        self.vbox.addWidget(self.form_group_box)

        self.table_model = SimpleTableModel(["Email"], self.email_list)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.table_view.setColumnWidth(0, 400)
        self.vbox.addWidget(self.table_view)

        self.delete_selected_btn = QPushButton('Delete Selected Email', self)
        self.delete_selected_btn.clicked.connect(self.handleDelete)
        self.vbox.addWidget(self.delete_selected_btn)

        self.hbox1 = QHBoxLayout()
        self.email_label = QLabel("Email: ")
        self.email = QLineEdit(self)
        self.add_btn = QPushButton('Add Email', self)
        self.add_btn.clicked.connect(self.handleAdd)
        self.hbox1.addWidget(self.email_label)
        self.hbox1.addWidget(self.email)
        self.hbox1.addWidget(self.add_btn)
        self.vbox.addLayout(self.hbox1)

        query = f"select exists (select * from visitor_list where username = '{self.username_d}')"
        x = sqlQueryOutput(query)
        self.is_visitor = list(x[0].values())[0]
        self.cb = QCheckBox('Visitor?', self)
        self.cb.setChecked(self.is_visitor)
        self.vbox.addWidget(self.cb)

        self.buttonBack = QPushButton('Back', self)
        self.buttonUpdate = QPushButton('Update', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonUpdate.clicked.connect(self.handleUpdate)
        self.buttonUpdate.setDefault(True)
        self.form_group_box3 = QGroupBox()
        self.form_layout3 = QFormLayout()
        self.form_layout3.addRow(self.buttonUpdate, self.buttonBack)
        self.form_group_box3.setLayout(self.form_layout3)
        self.vbox.addWidget(self.form_group_box3)

        self.added_emails = []
        self.deleted_emails = []

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleUpdate(self):
        visitor_checked = self.cb.checkState()

        phone = self.phone.text()
        fname = self.firstname.text()
        lname = self.lastname.text()

        if (fname == '' or lname == '' or phone == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
            return
        if (len(self.email_list) == 0):
            QMessageBox.warning(
                self, 'Error', 'You must have at least one email address linked to your account')
            return

        if (phone != self.phone_d):
            query = f"select exists (select * from employee where phone = '{phone}')"
            x = sqlQueryOutput(query)
            not_unique_phone = list(x[0].values())[0]
            if (not_unique_phone):
                QMessageBox.warning(
                self, 'Error', 'The phone number you have entered is already taken by an existing user')
                return
            if (not is_int(phone)):
                QMessageBox.warning(
                self, 'Error', 'Please provide a valid 10 digit phone number')
                return

            query = f"update employee set phone = '{phone}' where username='{self.username_d}'"
            sqlInsertDeleteQuery(query)

        if (fname != self.fname_d):
            query = f"update user set fname = '{fname}' where username = '{self.username_d}'"
            sqlInsertDeleteQuery(query)

        if (lname != self.lname_d):
            query = f"update user set lname = '{lname}' where username = '{self.username_d}'"
            sqlInsertDeleteQuery(query)


        if (len(self.deleted_emails) > 0):
            for i in self.deleted_emails:
                query = f"delete from email where email = '{i}'"
                sqlInsertDeleteQuery(query)

        if (len(self.added_emails) > 0):
            for i in self.added_emails:
                query = "insert into email (username, email) "\
                    + f"values ('{self.username_d}', '{i}') "
                sqlInsertDeleteQuery(query)

        visitor_change = False
        if (visitor_checked and not self.is_visitor):
            query = f"insert into visitor_list (username) values ('{self.username_d}')"
            sqlInsertDeleteQuery(query)
            visitor_change = True
        elif (not visitor_checked and self.is_visitor):

            query = f"delete from visitor_list where username = '{self.username_d}'"
            sqlInsertDeleteQuery(query)
            visitor_change = True
        QMessageBox.information(self, 'Congrats!', f"You successfully updated your profile!", QMessageBox.Ok)
        self.close()
        if (not visitor_change):
            self.parent.show()
        else:
            self.parent.close()
            self.parent.parent.functionality(usernamex=self.username_d)


    def handleAdd(self):
        curr_email = self.email.text()
        if (curr_email == ''):
            QMessageBox.warning(
                self, 'Error', 'Please enter an email address to add')
            return
        if (valid_email_check(curr_email, self)):
            query = f"select exists (select * from email where email = '{curr_email}')"
            x = sqlQueryOutput(query)
            not_unique = list(x[0].values())[0]

            if (not_unique):
                QMessageBox.warning(
                self, 'Error', 'This email address is already linked to an existing user')
                return
            if (curr_email in self.added_emails):
                QMessageBox.warning(
                self, 'Error', 'You have already added this email address')
                return

            self.added_emails.append(curr_email)
            self.email_list.append([curr_email])

            self.table_model = SimpleTableModel(["Email"], self.email_list)
            self.table_view.setModel(self.table_model)



    def handleDelete(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:
            email_to_delete = self.table_model.data[row_index][0]
            if (email_to_delete in self.added_emails):
                self.added_emails.remove(email_to_delete)
            elif ([email_to_delete] in self.original_email_list):
                self.deleted_emails.append(email_to_delete)
            self.email_list.remove([email_to_delete])
            self.table_model = SimpleTableModel(["Email"], self.email_list)
            self.table_view.setModel(self.table_model)




# SCREEN NUMBER 16
class UserTransitHistory(QWidget):
    def __init__(self, parent, username):
        super(UserTransitHistory, self).__init__()
        self.setWindowTitle("Transit History")

        self.username = username
        self.parent = parent

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type_dropdown = QComboBox(self)
        self.transport_type_dropdown.addItems(["--ALL--", "MARTA", "Bus", "Bike"])
        self.hbox1.addWidget(self.transport_type_label)
        self.hbox1.addWidget(self.transport_type_dropdown)
        self.vbox.addLayout(self.hbox1)

        site_name_list = create_site_name_list()
        self.hbox2 = QHBoxLayout()
        self.contain_site_label = QLabel("Contain Site: ")
        self.contain_site_dropdown = QComboBox(self)
        self.contain_site_dropdown.addItems(site_name_list)
        self.hbox2.addWidget(self.contain_site_label)
        self.hbox2.addWidget(self.contain_site_dropdown)
        self.vbox.addLayout(self.hbox2)


        self.hbox3 = QHBoxLayout()
        self.route_label = QLabel("Route: ")
        self.route = QLineEdit(self)
        self.hbox3.addWidget(self.route_label)
        self.hbox3.addWidget(self.route)
        self.vbox.addLayout(self.hbox3)

        self.hbox4 = QHBoxLayout()
        self.start_date_label = QLabel("Start Date: ")
        self.start_date = QLineEdit(self)
        self.end_date_label = QLabel("End Date: ")
        self.end_date = QLineEdit(self)
        self.hbox4.addWidget(self.start_date_label)
        self.hbox4.addWidget(self.start_date)
        self.hbox4.addWidget(self.end_date_label)
        self.hbox4.addWidget(self.end_date)
        self.vbox.addLayout(self.hbox4)


        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)
        self.vbox.addWidget(self.filter_btn)

        self.root_query = "select TT.take_date, TT.route, TT.transit_type, T.price "\
            + "from take_transit as TT "\
            + "join transit as T "\
            + "on T.route = TT.route "\
            + "and T.type = TT.transit_type "
        query = self.root_query + f"where TT.username = '{self.username}' order by TT.take_date"
        self.curr_query = query
        table_rows = sqlQueryOutput(query, ['take_date', 'route', 'transit_type', 'price'])

        self.table_model = SimpleTableModel(["Date", "Route", "Transport Type", "Price"], table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleFilter(self):
        curr_transport_type = self.transport_type_dropdown.currentText()
        curr_site = self.contain_site_dropdown.currentText()
        curr_route = self.route.text()
        curr_start_date = self.start_date.text()
        curr_end_date = self.end_date.text()

        transit_type_filter = (not (curr_transport_type == '--ALL--'))
        route_filter = (not(curr_route == ''))
        start_date_filter = (not (curr_start_date == ''))
        end_date_filter = (not (curr_end_date == ''))

        if (start_date_filter):
            if (not valid_date_check(curr_start_date, self)):
                return
        if (end_date_filter):
            if (not valid_date_check(curr_end_date, self)):
                return

        query = self.root_query + "join transit_connections as TC "\
            + "on TT.transit_type = TC.transit_type "\
            + "and TT.route = TC.route "\
            + f"where TT.username = '{self.username}' "\
            + f"and TC.site_name = '{curr_site}' "

        if (start_date_filter):
            query = query + f"and take_date >= '{curr_start_date}' "
        if (end_date_filter):
            query = query + f"and take_date <= '{curr_end_date}' "
        if (route_filter):
            query = query + f"and TT.route = '{curr_route}' "
        if (transit_type_filter):
            query = query + f"and TT.transit_type = '{curr_transport_type}' "

        query = query + "order by TT.take_date"

        self.curr_query = query

        table_rows = sqlQueryOutput(query, ['take_date', 'route', 'transit_type', 'price'])

        self.table_model = SimpleTableModel(["Date", "Route", "Transport Type", "Price"], table_rows)
        self.table_view.setModel(self.table_model)




class SimpleTableModel(QAbstractTableModel):

    def __init__(self, headers, rows):
        QAbstractTableModel.__init__(self, None)
        self.data = rows
        self.headers = headers
        self.rows = rows

    def rowCount(self, parent):
        return len(self.rows)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
        else:
            return QVariant(self.rows[index.row()][index.column()])

    def row(self, index):
        return self.data[index]

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        elif orientation == Qt.Vertical:
            return section + 1
        else:
            return self.headers[section]

    def editData(self, data):
        self.rows = data
        self.data = data




# SCREEN NUMBER 15
class UserTakeTransit(QWidget):
    def __init__(self, parent, username):
        super(UserTakeTransit, self).__init__()
        self.setWindowTitle("Take Transit")

        self.username = username
        self.parent = parent

        self.vbox = QVBoxLayout()

        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()

        site_name_list = create_site_name_list()

        self.contain_site_label = QLabel("Contain Site: ")
        self.contain_site_dropdown = QComboBox(self)
        self.contain_site_dropdown.addItems(site_name_list)
        self.hbox1.addWidget(self.contain_site_label)
        self.hbox1.addWidget(self.contain_site_dropdown)

        self.transport_type_label = QLabel("Transport Type: ")
        self.transport_type_dropdown = QComboBox(self)
        self.transport_type_dropdown.addItems(["--ALL--", "MARTA", "Bus", "Bike"])
        self.hbox2.addWidget(self.transport_type_label)
        self.hbox2.addWidget(self.transport_type_dropdown)

        self.price_range_label = QLabel("Price Range: ")
        self.lower_price_bound = QLineEdit(self)
        self.dash_label = QLabel(" -- ")
        self.upper_price_bound = QLineEdit(self)
        self.hbox3.addWidget(self.price_range_label)
        self.hbox3.addWidget(self.lower_price_bound)
        self.hbox3.addWidget(self.dash_label)
        self.hbox3.addWidget(self.upper_price_bound)

        self.filter_btn = QPushButton('Filter', self)
        self.filter_btn.clicked.connect(self.handleFilter)

        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addWidget(self.filter_btn)

        self.root_query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections "\
            + "on transit_connections.route = transit.route "\
            + "and transit_connections.transit_type = transit.type "
        self.group_by = "group by transit.route, transit.type "
        self.curr_query = self.root_query + self.group_by
        self.table_rows = sqlQueryOutput(self.curr_query, ['route', 'type', 'price', '# Connected Sites'])

        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], self.table_rows)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)
        self.vbox.addWidget(self.table_view)


        self.hbox4 = QHBoxLayout()
        self.transit_date_label = QLabel("Transit Date: ")
        self.transit_date = QLineEdit(self)
        self.log_transit_btn = QPushButton('Log Transit', self)
        self.log_transit_btn.clicked.connect(self.handleLogTransit)
        self.hbox4.addWidget(self.transit_date_label)
        self.hbox4.addWidget(self.transit_date)
        self.hbox4.addWidget(self.log_transit_btn)
        self.vbox.addLayout(self.hbox4)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)


    def handleFilter(self):

        transit_type = self.transport_type_dropdown.currentText()
        contain_site = self.contain_site_dropdown.currentText()
        lower_price_bound = self.lower_price_bound.text()
        upper_price_bound = self.upper_price_bound.text()

        transit_type_filter = (not (transit_type == '--ALL--'))
        lower_price_bound_filter = (not (lower_price_bound == ''))
        upper_price_bound_filter = (not (upper_price_bound == ''))

        query = self.root_query \
            + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \

        if (lower_price_bound_filter):
            if not is_float(lower_price_bound):
                return
            else:
                query += f"and price >= {float(lower_price_bound)} "
        if (upper_price_bound_filter):
            if not is_float(upper_price_bound):
                return
            else:
                query += f"and price <= {float(upper_price_bound)} "
        if (transit_type_filter):
            query += f"and type = '{transit_type}' "

        query += self.group_by

        self.handleUpdateTable(query)


    def handleBack(self):
        self.close()
        self.parent.show()

    def handleLogTransit(self):
        row_index = self.table_view.currentIndex().row()

        if (row_index == -1):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        else:

            transit_date = self.transit_date.text()
            date_pattern = r'[\d]{4}-[0,1][\d]{1}-[0,1,2,3][\d]{1}'
            date_check = re.fullmatch(date_pattern, transit_date)
            route = self.table_model.data[row_index][0]
            transit_type = self.table_model.data[row_index][1]
            query_check = "select exists (select username " \
                + "from take_transit " \
                + f"where username = '{self.username}' " \
                + f"and transit_type = '{transit_type}' " \
                + f"and route = '{route}' " \
                + f"and take_date = '{transit_date}')"
            cursor = connection.cursor()
            cursor.execute(query_check)
            same_day_check = [line for line in cursor]
            same_day = list(same_day_check[0].values())[0]

            cursor.close()

            if (date_check == None):
                QMessageBox.warning(
                    self, 'Error', 'Please enter a valid date in the form YYYY-MM-DD')
            elif (same_day):
                QMessageBox.warning(
                    self, 'Error', 'You cannot take the same transit twice in one day')
            else:

                query = "insert into take_transit " \
                    + "(username, transit_type, route, take_date) " \
                    + f"values ('{self.username}', '{transit_type}', '{route}', '{transit_date}');"
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                cursor.close()
                QMessageBox.information(self, 'Congrats!', "You successfully logged your journey!", QMessageBox.Ok)


    def handleUpdateTable(self, query=None):
        if query == None:
            query = self.root_query + self.group_by

        self.table_rows = sqlQueryOutput(query, ['route', 'type', 'price', '# Connected Sites'])
        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], self.table_rows)
        self.table_view.setModel(self.table_model)





def create_site_name_list():

    site_name_list = []
    cursor = connection.cursor()
    cursor.execute("select name from site;")
    site_data = [line for line in cursor]
    for i in site_data:
        site_name_list.append(i["name"])
    return site_name_list



# SCREEN NUMBER 14
class VisitorFunctionality(QWidget):
    def __init__(self, parent, username):
        super(VisitorFunctionality, self).__init__()
        self.setWindowTitle("Visitor Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.explore_site_btn = QPushButton('Explore Site', self)
        self.explore_site_btn.clicked.connect(self.handleExploreSite)

        self.explore_event_btn = QPushButton('Explore Event', self)
        self.explore_event_btn.clicked.connect(self.handleExploreEvent)

        self.view_visit_hist_btn = QPushButton('View Visit History', self)
        self.view_visit_hist_btn.clicked.connect(self.handleViewVisitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.take_transit_btn) #1
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.explore_site_btn) #3
        self.vbox.addWidget(self.explore_event_btn)
        self.vbox.addWidget(self.view_visit_hist_btn) #5
        self.vbox.addWidget(self.back_btn) #6

        self.setLayout(self.vbox)


    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleExploreSite(self):
        self.hide()
        self.visitor_explore_site = VisitorExploreSite(self,self.username)
        self.visitor_explore_site.show()
        self.visitor_explore_site.raise_()

    def handleExploreEvent(self):
        self.hide()
        self.visitor_explore_event = VisitorExploreEvent(self, self.username)
        self.visitor_explore_event.show()
        self.visitor_explore_event.raise_()

    def handleViewVisitHistory(self):
        self.hide()
        self.visitor_visit_history = VisitorVisitHistory(self, self.username)
        self.visitor_visit_history.show()
        self.visitor_visit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()




# SCREEN NUMBER 13
class EmpVisitorFunctionality(QWidget):
    def __init__(self, parent, username):
        super(EmpVisitorFunctionality, self).__init__()
        self.setWindowTitle("Employee-Visitor Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.view_schedule_btn = QPushButton('View Schedule', self)
        self.view_schedule_btn.clicked.connect(self.handleViewSchedule)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.explore_site_btn = QPushButton('Explore Site', self)
        self.explore_site_btn.clicked.connect(self.handleExploreSite)

        self.explore_event_btn = QPushButton('Explore Event', self)
        self.explore_event_btn.clicked.connect(self.handleExploreEvent)

        self.view_visit_hist_btn = QPushButton('View Visit History', self)
        self.view_visit_hist_btn.clicked.connect(self.handleViewVisitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn) #1
        self.vbox.addWidget(self.view_schedule_btn)
        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.explore_site_btn) #5
        self.vbox.addWidget(self.explore_event_btn)
        self.vbox.addWidget(self.view_visit_hist_btn)
        self.vbox.addWidget(self.back_btn) #8

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleViewSchedule(self):
        self.hide()
        self.staff_view_schedule = StaffViewSchedule(self, self.username)
        self.staff_view_schedule.show()
        self.staff_view_schedule.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleExploreSite(self):
        self.hide()
        self.visitor_explore_site = VisitorExploreSite(self,self.username)
        self.visitor_explore_site.show()
        self.visitor_explore_site.raise_()

    def handleExploreEvent(self):
        self.hide()
        self.visitor_explore_event = VisitorExploreEvent(self, self.username)
        self.visitor_explore_event.show()
        self.visitor_explore_event.raise_()

    def handleViewVisitHistory(self):
        self.hide()
        self.visitor_visit_history = VisitorVisitHistory(self, self.username)
        self.visitor_visit_history.show()
        self.visitor_visit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()





# SCREEN NUMBER 12
class EmpFunctionality(QWidget):
    def __init__(self, parent, username):
        super(EmpFunctionality, self).__init__()
        self.setWindowTitle("Employee Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.view_schedule_btn = QPushButton('View Schedule', self)
        self.view_schedule_btn.clicked.connect(self.handleViewSchedule)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn)
        self.vbox.addWidget(self.view_schedule_btn)
        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleViewSchedule(self):
        self.hide()
        self.staff_view_schedule = StaffViewSchedule(self, self.username)
        self.staff_view_schedule.show()
        self.staff_view_schedule.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()



# SCREEN NUMBER 10
class ManagerFunctionality(QWidget):
    def __init__(self, parent, username):
        super(ManagerFunctionality, self).__init__()
        self.setWindowTitle("Manager Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.manage_event_btn = QPushButton('Manage Event', self)
        self.manage_event_btn.clicked.connect(self.handleManageEvent)

        self.view_staff_btn = QPushButton('View Staff', self)
        self.view_staff_btn.clicked.connect(self.handleViewStaff)

        self.view_site_report_btn = QPushButton('View Site Report', self)
        self.view_site_report_btn.clicked.connect(self.handleViewSiteReport)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn) #1
        self.vbox.addWidget(self.manage_event_btn)
        self.vbox.addWidget(self.view_staff_btn)
        self.vbox.addWidget(self.view_site_report_btn)
        self.vbox.addWidget(self.take_transit_btn) #5
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.back_btn) #7

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleManageEvent(self):
        self.hide()
        self.manager_manage_event = ManagerManageEvent(self, self.username)
        self.manager_manage_event.show()
        self.manager_manage_event.raise_()

    def handleViewStaff(self):
        self.hide()
        self.manager_manage_staff = ManagerManageStaff(self, self.username)
        self.manager_manage_staff.show()
        self.manager_manage_staff.raise_()

    def handleViewSiteReport(self):
        self.hide()
        self.manager_site_report = ManagerSiteReport(self, self.username)
        self.manager_site_report.show()
        self.manager_site_report.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()




# SCREEN NUMBER 11
class ManagerVisitorFunctionality(QWidget):
    def __init__(self, parent, username):
        super(ManagerVisitorFunctionality, self).__init__()
        self.setWindowTitle("Manager-Visitor Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.manage_event_btn = QPushButton('Manage Event', self)
        self.manage_event_btn.clicked.connect(self.handleManageEvent)

        self.view_staff_btn = QPushButton('View Staff', self)
        self.view_staff_btn.clicked.connect(self.handleViewStaff)

        self.view_site_report_btn = QPushButton('View Site Report', self)
        self.view_site_report_btn.clicked.connect(self.handleViewSiteReport)

        self.explore_site_btn = QPushButton('Explore Site', self)
        self.explore_site_btn.clicked.connect(self.handleExploreSite)

        self.explore_event_btn = QPushButton('Explore Event', self)
        self.explore_event_btn.clicked.connect(self.handleExploreEvent)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.view_visit_hist_btn = QPushButton('View Visit History', self)
        self.view_visit_hist_btn.clicked.connect(self.handleViewVisitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn) #1
        self.vbox.addWidget(self.manage_event_btn)
        self.vbox.addWidget(self.view_staff_btn)
        self.vbox.addWidget(self.view_site_report_btn)
        self.vbox.addWidget(self.explore_site_btn) #5
        self.vbox.addWidget(self.explore_event_btn)
        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.view_visit_hist_btn)
        self.vbox.addWidget(self.back_btn) #10

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleManageEvent(self):
        self.hide()
        self.manager_manage_event = ManagerManageEvent(self, self.username)
        self.manager_manage_event.show()
        self.manager_manage_event.raise_()

    def handleViewStaff(self):
        self.hide()
        self.manager_manage_staff = ManagerManageStaff(self, self.username)
        self.manager_manage_staff.show()
        self.manager_manage_staff.raise_()

    def handleViewSiteReport(self):
        self.hide()
        self.manager_site_report = ManagerSiteReport(self, self.username)
        self.manager_site_report.show()
        self.manager_site_report.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleExploreSite(self):
        self.hide()
        self.visitor_explore_site = VisitorExploreSite(self,self.username)
        self.visitor_explore_site.show()
        self.visitor_explore_site.raise_()

    def handleExploreEvent(self):
        self.hide()
        self.visitor_explore_event = VisitorExploreEvent(self, self.username)
        self.visitor_explore_event.show()
        self.visitor_explore_event.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleViewVisitHistory(self):
        self.hide()
        self.visitor_visit_history = VisitorVisitHistory(self, self.username)
        self.visitor_visit_history.show()
        self.visitor_visit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()





# SCREEN NUMBER 7
class UserFunctionality(QWidget):
    def __init__(self, parent, username):
        super(UserFunctionality, self).__init__()
        self.setWindowTitle("User Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()


# SCREEN NUMBER 9
class AdminVisitorFunctionality(QWidget):
    def __init__(self, parent, username):
        super(AdminVisitorFunctionality, self).__init__()
        self.setWindowTitle("Administrator-Visitor Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.manage_user_btn = QPushButton('Manage User', self)
        self.manage_user_btn.clicked.connect(self.handleManageUser)

        self.manage_transit_btn = QPushButton('Manage Transit', self)
        self.manage_transit_btn.clicked.connect(self.handleManageTransit)

        self.manage_site_btn = QPushButton('Manage Site', self)
        self.manage_site_btn.clicked.connect(self.handleManageSite)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.explore_site_btn = QPushButton('Explore Site', self)
        self.explore_site_btn.clicked.connect(self.handleExploreSite)

        self.explore_event_btn = QPushButton('Explore Event', self)
        self.explore_event_btn.clicked.connect(self.handleExploreEvent)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.view_visit_hist_btn = QPushButton('View Visit History', self)
        self.view_visit_hist_btn.clicked.connect(self.handleViewVisitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn)
        self.vbox.addWidget(self.manage_user_btn)
        self.vbox.addWidget(self.manage_transit_btn)
        self.vbox.addWidget(self.manage_site_btn)
        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.explore_site_btn)
        self.vbox.addWidget(self.explore_event_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.view_visit_hist_btn)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleManageUser(self):
        self.hide()
        self.admin_manage_user = AdminManageUser(self, self.username)
        self.admin_manage_user.show()
        self.admin_manage_user.raise_()

    def handleManageTransit(self):
        self.hide()
        self.admin_manage_transit = AdminManageTransit(self, self.username)
        self.admin_manage_transit.show()
        self.admin_manage_transit.raise_()

    def handleManageSite(self):
        self.hide()
        self.admin_manage_site = AdminManageSite(self, self.username)
        self.admin_manage_site.show()
        self.admin_manage_site.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleExploreSite(self):
        self.hide()
        self.visitor_explore_site = VisitorExploreSite(self,self.username)
        self.visitor_explore_site.show()
        self.visitor_explore_site.raise_()

    def handleExploreEvent(self):
        self.hide()
        self.visitor_explore_event = VisitorExploreEvent(self, self.username)
        self.visitor_explore_event.show()
        self.visitor_explore_event.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleViewVisitHistory(self):
        self.hide()
        self.visitor_visit_history = VisitorVisitHistory(self, self.username)
        self.visitor_visit_history.show()
        self.visitor_visit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()




# SCREEN NUMBER 8
class AdminFunctionality(QWidget):
    def __init__(self, parent, username):
        super(AdminFunctionality, self).__init__()
        self.setWindowTitle("Administrator Functionality")

        self.username = username
        self.parent = parent
        self.vbox = QVBoxLayout()

        self.manage_profile_btn = QPushButton('Manage Profile', self)
        self.manage_profile_btn.clicked.connect(self.handleManageProfile)

        self.manage_user_btn = QPushButton('Manage User', self)
        self.manage_user_btn.clicked.connect(self.handleManageUser)

        self.manage_transit_btn = QPushButton('Manage Transit', self)
        self.manage_transit_btn.clicked.connect(self.handleManageTransit)

        self.manage_site_btn = QPushButton('Manage Site', self)
        self.manage_site_btn.clicked.connect(self.handleManageSite)

        self.take_transit_btn = QPushButton('Take Transit', self)
        self.take_transit_btn.clicked.connect(self.handleTakeTransit)

        self.view_transit_hist_btn = QPushButton('View Transit History', self)
        self.view_transit_hist_btn.clicked.connect(self.handleViewTransitHistory)

        self.back_btn = QPushButton('Back', self)
        self.back_btn.clicked.connect(self.handleBack)

        self.vbox.addWidget(self.manage_profile_btn)
        self.vbox.addWidget(self.manage_user_btn)
        self.vbox.addWidget(self.manage_transit_btn)
        self.vbox.addWidget(self.manage_site_btn)
        self.vbox.addWidget(self.take_transit_btn)
        self.vbox.addWidget(self.view_transit_hist_btn)
        self.vbox.addWidget(self.back_btn)

        self.setLayout(self.vbox)


    def handleManageProfile(self):
        self.hide()
        self.emp_manage_profile = EmployeeManageProfile(self, self.username)
        self.emp_manage_profile.show()
        self.emp_manage_profile.raise_()

    def handleManageUser(self):
        self.hide()
        self.admin_manage_user = AdminManageUser(self, self.username)
        self.admin_manage_user.show()
        self.admin_manage_user.raise_()

    def handleManageTransit(self):
        self.hide()
        self.admin_manage_transit = AdminManageTransit(self, self.username)
        self.admin_manage_transit.show()
        self.admin_manage_transit.raise_()

    def handleManageSite(self):
        self.hide()
        self.admin_manage_site = AdminManageSite(self, self.username)
        self.admin_manage_site.show()
        self.admin_manage_site.raise_()

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        self.hide()
        self.user_transit_history = UserTransitHistory(self, self.username)
        self.user_transit_history.show()
        self.user_transit_history.raise_()

    def handleBack(self):
        self.close()
        self.parent.show()



class RegisterEmpVisitor(QWidget):
    def __init__(self, parent):
        super(RegisterEmpVisitor, self).__init__()
        self.setWindowTitle("Register Employee-Visitor")

        self.email_count = 0
        self.parent = parent
        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.username = QLineEdit(self)
        self.user_type_dropdown = QComboBox(self)
        self.user_type_dropdown.addItems(['Select User Type', 'Manager', 'Staff'])

        self.password = QLineEdit(self)
        self.confirmpassword = QLineEdit(self)

        self.phone = QLineEdit(self)
        self.address = QLineEdit(self)
        self.city = QLineEdit(self)
        self.state_dropdown = QComboBox(self)
        self.state_dropdown.addItems(
            ['Select State', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
               'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
               'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
               'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
               'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'Other'])
        self.zipcode = QLineEdit(self)



        self.form_group_box = QGroupBox()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("First Name: "), self.firstname)
        self.form_layout.addRow(QLabel("Last Name: "), self.lastname)
        self.form_layout.addRow(QLabel("Username: "), self.username)
        self.form_layout.addRow(QLabel("User Type: "), self.user_type_dropdown)
        self.form_layout.addRow(QLabel("Password: "), self.password)
        self.form_layout.addRow(QLabel("Confirm Password: "), self.confirmpassword)

        self.form_layout.addRow(QLabel("Phone: "), self.phone)
        self.form_layout.addRow(QLabel("Address: "), self.address)
        self.form_layout.addRow(QLabel("City: "), self.city)
        self.form_layout.addRow(QLabel("State: "), self.state_dropdown)
        self.form_layout.addRow(QLabel("Zipcode: "), self.zipcode)

        self.form_group_box.setLayout(self.form_layout)

        self.email_table = EmailTable(self)

        self.buttonBack = QPushButton('Back', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonRegister.setDefault(True)

        self.form_group_box3 = QGroupBox()
        self.form_layout3 = QFormLayout()
        self.form_layout3.addRow(self.buttonRegister, self.buttonBack)
        self.form_group_box3.setLayout(self.form_layout3)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.form_group_box)
        self.vbox.addLayout(self.email_table)
        self.vbox.addWidget(self.form_group_box3)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleRegister(self):
        firstname = self.firstname.text()
        lastname = self.lastname.text()
        username = self.username.text()
        user_type = self.user_type_dropdown.currentText()
        password = self.password.text()
        confirmpassword = self.confirmpassword.text()
        phone = self.phone.text()
        address = self.address.text()
        city = self.city.text()
        state = self.state_dropdown.currentText()
        zipcode = self.zipcode.text()

        username_list = load_db_usernames()
        email_list = load_db_emails()


        if (username == '' \
            or password == ''
            or firstname == '' \
            or lastname == '' \
            or confirmpassword == '' \
            or (len(self.email_table.added_emails) == 0) \
            or user_type == 'Select User Type' \
            or phone == '' \
            or address == '' \
            or city == '' \
            or state == 'Select State' \
            or zipcode == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(password) < 8):
            QMessageBox.warning(
                self, 'Error', 'The password must be at least 8 characters long')
        elif (len(phone) != 10 or not is_int(phone)):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 10 digit phone number')
        elif (len(zipcode) != 5 or not is_int(zipcode)):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 5 digit zip code')
        else:

            query_exists = f"select exists (select * from employee where phone = '{phone}')"
            x = sqlQueryOutput(query_exists)
            not_unique_phone = list(x[0].values())[0]

            if not_unique_phone:
                QMessageBox.warning(
                self, 'Error', 'The phone number you provided is already linked to an existing user')
                return

            for i in self.email_table.added_emails:
                query_exists = f"select exists (select * from email where email = '{i}')"
                x = sqlQueryOutput(query_exists)
                not_unique_email = list(x[0].values())[0]

                if not_unique_email:
                    QMessageBox.warning(
                    self, 'Error', 'One of the emails you provided is already linked to an existing user')
                    return

            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'Employee', " \
                + f"'{firstname}', '{lastname}', 'Pending', '{hash_password(password)}');"
            cursor.execute(query)

            for x in self.email_table.added_emails:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)


            query4 = f"insert into employee (username, phone, address, city, state, zipcode, employee_type)" \
                    + f"values ('{username}', '{phone}', '{address}', '{city}', " \
                    + f"'{state}', '{zipcode}', '{user_type}');"

            cursor.execute(query4)

            query5 = f"insert into visitor_list values ('{username}')"
            cursor.execute(query5)


            connection.commit()
            cursor.close()

            QMessageBox.information(self, 'Congrats!', "Your registration was a success!", QMessageBox.Ok)

            self.close()
            self.parent.back()





class RegisterEmployee(QWidget):
    def __init__(self, parent):
        super(RegisterEmployee, self).__init__()
        self.setWindowTitle("Register Employee")

        self.email_count = 0
        self.parent = parent
        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.username = QLineEdit(self)
        self.user_type_dropdown = QComboBox(self)
        self.user_type_dropdown.addItems(['Select User Type', 'Manager', 'Staff'])

        self.password = QLineEdit(self)
        self.confirmpassword = QLineEdit(self)

        self.phone = QLineEdit(self)
        self.address = QLineEdit(self)
        self.city = QLineEdit(self)
        self.state_dropdown = QComboBox(self)
        self.state_dropdown.addItems(
            ['Select State', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
               'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
               'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
               'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
               'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'Other'])
        self.zipcode = QLineEdit(self)

        self.form_group_box = QGroupBox()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("First Name: "), self.firstname)
        self.form_layout.addRow(QLabel("Last Name: "), self.lastname)
        self.form_layout.addRow(QLabel("Username: "), self.username)
        self.form_layout.addRow(QLabel("User Type: "), self.user_type_dropdown)
        self.form_layout.addRow(QLabel("Password: "), self.password)
        self.form_layout.addRow(QLabel("Confirm Password: "), self.confirmpassword)

        self.form_layout.addRow(QLabel("Phone: "), self.phone)
        self.form_layout.addRow(QLabel("Address: "), self.address)
        self.form_layout.addRow(QLabel("City: "), self.city)
        self.form_layout.addRow(QLabel("State: "), self.state_dropdown)
        self.form_layout.addRow(QLabel("Zipcode: "), self.zipcode)

        self.form_group_box.setLayout(self.form_layout)

        self.email_table = EmailTable(self)

        self.buttonBack = QPushButton('Back', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonRegister.setDefault(True)

        self.form_group_box3 = QGroupBox()
        self.form_layout3 = QFormLayout()
        self.form_layout3.addRow(self.buttonRegister, self.buttonBack)
        self.form_group_box3.setLayout(self.form_layout3)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.form_group_box)
        self.vbox.addLayout(self.email_table)
        self.vbox.addWidget(self.form_group_box3)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleRegister(self):
        firstname = self.firstname.text()
        lastname = self.lastname.text()
        username = self.username.text()
        user_type = self.user_type_dropdown.currentText()
        password = self.password.text()
        confirmpassword = self.confirmpassword.text()
        phone = self.phone.text()
        address = self.address.text()
        city = self.city.text()
        state = self.state_dropdown.currentText()
        zipcode = self.zipcode.text()

        username_list = load_db_usernames()
        email_list = load_db_emails()


        if (username == '' \
            or password == ''
            or firstname == '' \
            or lastname == '' \
            or confirmpassword == '' \
            or (len(self.email_table.added_emails) == 0) \
            or user_type == 'Select User Type' \
            or phone == '' \
            or address == '' \
            or city == '' \
            or state == 'Select State' \
            or zipcode == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all the text fields and provide at least one email address')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(password) < 8):
            QMessageBox.warning(
                self, 'Error', 'The password must be at least 8 characters long')
        elif (len(phone) != 10 or not is_int(phone)):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 10 digit phone number')
        elif (len(zipcode) != 5 or not is_int(zipcode)):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 5 digit zip code')
        else:

            query_exists = f"select exists (select * from employee where phone = '{phone}')"
            x = sqlQueryOutput(query_exists)
            not_unique_phone = list(x[0].values())[0]

            if not_unique_phone:
                QMessageBox.warning(
                self, 'Error', 'The phone number you provided is already linked to an existing user')
                return

            for i in self.email_table.added_emails:
                query_exists = f"select exists (select * from email where email = '{i}')"
                x = sqlQueryOutput(query_exists)
                not_unique_email = list(x[0].values())[0]

                if not_unique_email:
                    QMessageBox.warning(
                    self, 'Error', 'One of the emails you provided is already linked to an existing user')
                    return


            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'Employee'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{hash_password(password)}');"
            cursor.execute(query)


            for x in self.email_table.added_emails:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)


            query4 = f"insert into employee (username, phone, address, city, state, zipcode, employee_type)" \
                    + f"values ('{username}', '{phone}', '{address}', '{city}', " \
                    + f"'{state}', '{zipcode}', '{user_type}');"

            cursor.execute(query4)

            connection.commit()
            cursor.close()

            QMessageBox.information(self, 'Congrats', "Your registration was a success!", QMessageBox.Ok)

            self.close()
            self.parent.back()





class RegisterVisitor(QWidget):
    def __init__(self, parent):
        super(RegisterVisitor, self).__init__()
        self.setWindowTitle("Register Visitor")

        self.email_count = 0
        self.parent = parent
        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.confirmpassword = QLineEdit(self)

        self.form_group_box = QGroupBox()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("First Name: "), self.firstname)
        self.form_layout.addRow(QLabel("Last Name: "), self.lastname)
        self.form_layout.addRow(QLabel("Username: "), self.username)
        self.form_layout.addRow(QLabel("Password: "), self.password)
        self.form_layout.addRow(QLabel("Confirm Password: "), self.confirmpassword)
        self.form_group_box.setLayout(self.form_layout)

        self.email_table = EmailTable(self)

        self.buttonBack = QPushButton('Back', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonRegister.setDefault(True)

        self.form_group_box3 = QGroupBox()
        self.form_layout3 = QFormLayout()
        self.form_layout3.addRow(self.buttonRegister, self.buttonBack)
        self.form_group_box3.setLayout(self.form_layout3)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.form_group_box)
        self.vbox.addLayout(self.email_table)
        self.vbox.addWidget(self.form_group_box3)

        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleRegister(self):
        firstname = self.firstname.text()
        lastname = self.lastname.text()
        username = self.username.text()
        password = self.password.text()
        confirmpassword = self.confirmpassword.text()

        username_list = load_db_usernames()


        if (username == '' or password == '' or firstname == '' \
            or lastname == '' or confirmpassword == '' \
            or (len(self.email_table.added_emails)) == 0):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all the text fields and provide at least one email address')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(password) < 8):
            QMessageBox.warning(
                self, 'Error', 'The password must be at least 8 characters long')
        else:

            for i in self.email_table.added_emails:
                query_exists = f"select exists (select * from email where email = '{i}')"
                x = sqlQueryOutput(query_exists)
                not_unique_email = list(x[0].values())[0]

                if not_unique_email:
                    QMessageBox.warning(
                    self, 'Error', 'One of the emails you provided is already linked to an existing user')
                    return


            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'Visitor'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{hash_password(password)}');"
            cursor.execute(query)

            for x in self.email_table.added_emails:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            query4 = f"insert into visitor_list values ('{username}')"
            cursor.execute(query4)

            connection.commit()
            cursor.close()

            QMessageBox.information(self, 'Congrats!', "Your registration was a success!", QMessageBox.Ok)

            self.close()
            self.parent.back()




class RegisterUser(QWidget):
    def __init__(self, parent):
        super(RegisterUser, self).__init__()
        self.setWindowTitle("Register User")

        self.email_count = 0
        self.parent = parent
        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.confirmpassword = QLineEdit(self)

        self.form_group_box = QGroupBox()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("First Name: "), self.firstname)
        self.form_layout.addRow(QLabel("Last Name: "), self.lastname)
        self.form_layout.addRow(QLabel("Username: "), self.username)
        self.form_layout.addRow(QLabel("Password: "), self.password)
        self.form_layout.addRow(QLabel("Confirm Password: "), self.confirmpassword)
        self.form_group_box.setLayout(self.form_layout)

        self.email_table = EmailTable(self)

        self.buttonBack = QPushButton('Back', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonRegister.setDefault(True)

        self.form_group_box3 = QGroupBox()
        self.form_layout3 = QFormLayout()
        self.form_layout3.addRow(self.buttonRegister, self.buttonBack)
        self.form_group_box3.setLayout(self.form_layout3)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.form_group_box)
        self.vbox.addLayout(self.email_table)
        self.vbox.addWidget(self.form_group_box3)
        self.setLayout(self.vbox)

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleRegister(self):
        firstname = self.firstname.text()
        lastname = self.lastname.text()
        username = self.username.text()
        password = self.password.text()
        confirmpassword = self.confirmpassword.text()

        username_list = load_db_usernames()

        if (username == '' or password == '' or firstname == '' \
            or lastname == '' or confirmpassword == '' \
            or (len(self.email_table.added_emails)) == 0):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all the text fields and provide at least one email address')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(password) < 8):
            QMessageBox.warning(
                self, 'Error', 'The password must be at least 8 characters long')
        else:

            for i in self.email_table.added_emails:
                query_exists = f"select exists (select * from email where email = '{i}')"
                x = sqlQueryOutput(query_exists)
                not_unique_email = list(x[0].values())[0]

                if not_unique_email:
                    QMessageBox.warning(
                    self, 'Error', 'One of the emails you provided is already linked to an existing user')
                    return

            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, " \
                + "lname, status, password) " \
                + f"values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{hash_password(password)}');"
            cursor.execute(query)

            for x in self.email_table.added_emails:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            connection.commit()
            cursor.close()

            QMessageBox.information(self, 'Congrats!', "Your registration was a success!", QMessageBox.Ok)

            self.close()
            self.parent.back()






def load_db_usernames():
    cursor = connection.cursor()
    cursor.execute('select username from user;')
    user_data = [line for line in cursor]
    cursor.close()
    username_list = []
    for user_dict in user_data:
        username_list.append(user_dict['username'])
    return username_list


def load_db_emails():
    cursor = connection.cursor()
    cursor.execute('select email from email;')
    user_data = [line for line in cursor]
    cursor.close()
    email_list = []
    for user_dict in user_data:
        email_list.append(user_dict['email'])
    return email_list







class RegisterNavigation(QWidget):
    def __init__(self, parent):
        super(RegisterNavigation, self).__init__()
        self.parent = parent

        self.setWindowTitle("Register Navigation")

        self.register_user_btn = QPushButton("User Only")
        self.register_user_btn.clicked.connect(self.register_user)

        self.register_visitor_btn = QPushButton("Visitor Only")
        self.register_visitor_btn.clicked.connect(self.register_visitor)

        self.register_employee_btn = QPushButton("Employee Only")
        self.register_employee_btn.clicked.connect(self.register_employee)

        self.register_emp_visitor_btn = QPushButton("Employee-Visitor")
        self.register_emp_visitor_btn.clicked.connect(self.register_emp_visitor)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.back)


        vbox = QVBoxLayout()
        vbox.addWidget(self.register_user_btn)
        vbox.addWidget(self.register_visitor_btn)
        vbox.addWidget(self.register_employee_btn)
        vbox.addWidget(self.register_emp_visitor_btn)
        vbox.addWidget(self.back_btn)
        self.setLayout(vbox)


    def register_user(self):
        self.hide()
        self.register_user = RegisterUser(self)
        self.register_user.show()
        self.register_user.raise_()

    def register_visitor(self):
        self.hide()
        self.register_visitor = RegisterVisitor(self)
        self.register_visitor.show()
        self.register_visitor.raise_()

    def register_employee(self):
        self.hide()
        self.register_employee = RegisterEmployee(self)
        self.register_employee.show()
        self.register_employee.raise_()

    def register_emp_visitor(self):
        self.hide()
        self.register_emp_visitor = RegisterEmpVisitor(self)
        self.register_emp_visitor.show()
        self.register_emp_visitor.raise_()

    def back(self):
        self.close()
        self.parent.show()




class UserLogin(QWidget):
    def __init__(self, parent=None):
        super(UserLogin, self).__init__(parent)
        self.setWindowTitle("Atlanta Beltline Login")
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonLogin.setDefault(True)
        self.buttonRegister.setDefault(False)

        form_group_box = QGroupBox()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Email: "), self.email)
        form_layout.addRow(QLabel("Password: "), self.password)
        form_group_box.setLayout(form_layout)

        vbox_layout = QVBoxLayout(self)
        vbox_layout.addWidget(form_group_box)
        vbox_layout.addWidget(self.buttonLogin)
        vbox_layout.addWidget(self.buttonRegister)
        self.setLayout(vbox_layout)
        self.show()


    def handleLogin(self):

        load_login_data()

        email = self.email.text()
        password = self.password.text()

        if (email == '' or password == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in both the email and the password fields')
            return

        password = hash_password(password)

        if (email not in login_dict.keys()):
            QMessageBox.warning(
                self, 'Error', 'The email provided is not linked to an existing user')
        elif (login_dict[email] != password):
            QMessageBox.warning(
                self, 'Error', 'The password provided is incorrect')
        else:

            cursor = connection.cursor()
            query = 'select status from email join user ' \
                + f"using (username) where email = '{email}';"
            cursor.execute(query)
            user_data = [line for line in cursor]
            status = user_data[0]['status']
            if (status == 'Pending'):
                QMessageBox.warning(
                    self, 'Error', 'Your account registration is currently pending appoval')
            elif (status == 'Declined'):
                QMessageBox.warning(
                    self, 'Error', 'Your account registration has been declined approval')
            else:
                self.functionality(email=email)


    def handleRegister(self):
        self.hide()
        self.register_nav = RegisterNavigation(self)
        self.register_nav.show()

    def functionality(self, email=None, usernamex=None):

        cursor = connection.cursor()
        query = ''
        if email != None:
            query = 'select username, user_type from email join user ' \
                + f"using (username) where email = '{email}';"
        if usernamex != None:
            query = f"select username, user_type from user where username = '{usernamex}' "
        cursor.execute(query)

        user_data = [line for line in cursor]
        cursor.close()
        user_type = user_data[0]['user_type']
        username = user_data[0]['username']
        if user_type == 'User':
            self.hide()
            self.user_func = UserFunctionality(self, username)
            self.user_func.show()
        elif user_type == 'Visitor':
            self.hide()
            self.visitor_func = VisitorFunctionality(self, username)
            self.visitor_func.show()
        elif user_type == 'Employee':
            cursor = connection.cursor()
            query2 = 'select employee_type from employee join user ' \
                + f" using (username) where username = '{username}';"
            cursor.execute(query2)
            user_data = [line for line in cursor]
            cursor.close()
            emp_type = user_data[0]["employee_type"]

            cursor = connection.cursor()
            query3 = 'select username from visitor_list join user ' \
                + f" using (username) where username = '{username}';"
            cursor.execute(query3)
            user_data = [line for line in cursor]
            cursor.close()
            visitor = len(user_data)


            if (emp_type == 'Admin' and not visitor):
                self.hide()
                self.admin_func = AdminFunctionality(self, username)
                self.admin_func.show()
            elif (emp_type == 'Admin' and visitor):
                self.hide()
                self.admin_visitor_func = AdminVisitorFunctionality(self, username)
                self.admin_visitor_func.show()
            elif (emp_type == 'Manager' and not visitor):
                self.hide()
                self.manager_visitor_func = ManagerFunctionality(self, username)
                self.manager_visitor_func.show()
            elif (emp_type == 'Manager' and visitor):
                self.hide()
                self.manager_visitor_func = ManagerVisitorFunctionality(self, username)
                self.manager_visitor_func.show()
            elif (emp_type == 'Staff' and not visitor):
                self.hide()
                self.emp_func = EmpFunctionality(self, username)
                self.emp_func.show()
            elif (emp_type == 'Staff' and visitor):
                self.hide()
                self.emp_visitor_func = EmpVisitorFunctionality(self, username)
                self.emp_visitor_func.show()






class EmailTable(QVBoxLayout):
    def __init__(self, parent):
        super(EmailTable, self).__init__()

        self.parent = parent
        self.email_list = [['']]

        self.headers = ["Email"]

        self.table_model, self.table_view = createTable(self.headers, self.email_list)
        self.table_view.setColumnWidth(0, 300)
        self.addWidget(self.table_view)

        self.delete_selected_btn = QPushButton('Delete Selected Email', self.parent)
        self.delete_selected_btn.clicked.connect(self.handleDelete)
        self.addWidget(self.delete_selected_btn)

        self.hbox1 = QHBoxLayout()
        self.email_label = QLabel("Email: ")
        self.email = QLineEdit(self.parent)
        self.add_btn = QPushButton('Add Email', self.parent)
        self.add_btn.clicked.connect(self.handleAdd)
        self.hbox1.addWidget(self.email_label)
        self.hbox1.addWidget(self.email)
        self.hbox1.addWidget(self.add_btn)
        self.addLayout(self.hbox1)


        self.added_emails = []
        if self.email_list != [[""]]:
            self.added_emails = [i[0] for i in self.email_list]
        self.deleted_emails = []

    def handleAdd(self):
        curr_email = self.email.text()
        if (curr_email == ''):
            QMessageBox.warning(
                self.parent, 'Error', 'Please enter an email address to add')
            return
        if (valid_email_check(curr_email, self.parent)):
            query = f"select exists (select * from email where email = '{curr_email}')"
            x = sqlQueryOutput(query)
            not_unique = list(x[0].values())[0]

            if (not_unique):
                QMessageBox.warning(
                self.parent, 'Error', 'This email address is already linked to an existing user')
                return
            if (curr_email in self.added_emails):
                QMessageBox.warning(
                self.parent, 'Error', 'You have already added this email address')
                return

            if len(self.email_list) > 0:
                if self.email_list[0] == [""]:
                    self.email_list.remove([""])

            self.added_emails.append(curr_email)
            self.email_list.append([curr_email])

            self.table_model = SimpleTableModel(["Email"], self.email_list)
            self.table_view.setModel(self.table_model)



    def handleDelete(self):
        selected = len(self.table_view.selectedIndexes())
        row_index = self.table_view.currentIndex().row()
        if (not selected):
            QMessageBox.warning(
                self.parent, 'Error', 'Please select a row of the table')
        else:
            email_to_delete = self.table_model.data[row_index][0]
            if (email_to_delete in self.added_emails):
                self.added_emails.remove(email_to_delete)
            elif ([email_to_delete] in self.original_email_list):
                self.deleted_emails.append(email_to_delete)
            self.email_list.remove([email_to_delete])
            self.table_model = SimpleTableModel(["Email"], self.email_list)
            self.table_view.setModel(self.table_model)






def establish_connection(mysql_password):
    global connection
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password=mysql_password,
                                     db='beltline',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print(f"Couldn't log in to MySQL server :(")
        print(e)
        qApp.quit()
        sys.exit()



def load_login_data():
    cursor = connection.cursor()
    cursor.execute('select email, password from email join user using (username);')
    user_data = [line for line in cursor]
    cursor.close()
    global login_dict
    login_dict = {}
    for user_dict in user_data:
        login_dict[user_dict['email']] = int(user_dict['password'])
    return login_dict



if __name__ == '__main__':

    app = QApplication(sys.argv)
    establish_connection(sys.argv[1])
    global login
    login = UserLogin()
    sys.exit(app.exec_())


    # TO RUN THE GUI:
    # python beltline_login.py {insert your mysql password here}
