from pprint import pprint
import re

import pymysql
import sys
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
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
    QComboBox
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QPixmap)


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


        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], [["", "", "", ""]])
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

        table_data = []
        cursor = connection.cursor()

        transit_type_filter = True
        lower_price_bound_filter = True
        upper_price_bound_filter = True
        query = ''

        if (transit_type == '--ALL--'):
            transit_type_filter = False

        if (lower_price_bound == ''):
            lower_price_bound_filter = False

        if (upper_price_bound == ''):
            upper_price_bound_filter = False

        if (not lower_price_bound_filter and not upper_price_bound_filter):
            if (not transit_type_filter):
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + "group by transit.route, transit.type;"
            else:
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and type = '{transit_type}' " \
                    + "group by transit.route, transit.type;"
        elif (lower_price_bound_filter):
            if (not transit_type_filter):
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and price > {float(lower_price_bound)} " \
                    + "group by transit.route, transit.type;"
            else:
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and type = '{transit_type}' " \
                    + f"and price > {float(lower_price_bound)} " \
                    + "group by transit.route, transit.type;"
        elif (upper_price_bound_filter):
            if (not transit_type_filter):
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and price < {float(upper_price_bound)} " \
                    + "group by transit.route, transit.type;"
            else:
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and type = '{transit_type}' " \
                    + f"and price < {float(upper_price_bound)} " \
                    + "group by transit.route, transit.type;"
        else:
            if (not transit_type_filter):
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and price between {float(lower_price_bound)} and {float(upper_price_bound)} " \
                    + "group by transit.route, transit.type;"
            else:
                query = "select transit.route, type, price, count(site_name) as '# Connected Sites' from transit join transit_connections " \
                    + "where transit_connections.route = transit.route " \
                    + "and transit_connections.transit_type = transit.type " \
                    + f"and (transit.route, type) in (select route, transit_type from transit_connections where site_name = '{contain_site}') " \
                    + f"and type = '{transit_type}' " \
                    + f"and price between {float(lower_price_bound)} and {float(upper_price_bound)} " \
                    + "group by transit.route, transit.type;"


        # print(query)
        cursor.execute(query)
        transit_data = [line for line in cursor]
        for i in transit_data:
            table_data.append([i["route"], i["type"], str(i["price"]), i["# Connected Sites"]])

        self.hide()
        self.table_model = SimpleTableModel(["Route", "Transport Type", "Price", "# Connected Sites"], table_data)
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        self.show()

    def handleBack(self):
        self.close()
        self.parent.show()

    def handleLogTransit(self):
        row_index = self.table_view.currentIndex().row()
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
        print(same_day)
        # print(same_day_check)

        cursor.close()
        if (row_index == -1):
            QMessageBox.warning(
                self, 'Error', 'Please select a row of the table')
        elif (date_check == None):
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
            QMessageBox.information(self, 'PyQt5 message', "You successfully logged your journey!", QMessageBox.Ok)




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
        pass

    def handleExploreSite(self):
        pass

    def handleExploreEvent(self):
        pass

    def handleViewVisitHistory(self):
        pass

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
        pass

    def handleViewSchedule(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        pass

    def handleExploreSite(self):
        pass

    def handleExploreEvent(self):
        pass

    def handleViewVisitHistory(self):
        pass

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
        pass

    def handleViewSchedule(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        pass

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
        pass

    def handleManageEvent(self):
        pass

    def handleViewStaff(self):
        pass

    def handleViewSiteReport(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleExploreSite(self):
        pass

    def handleExploreEvent(self):
        pass

    def handleViewTransitHistory(self):
        pass

    def handleViewVisitHistory(self):
        pass

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
        pass

    def handleManageEvent(self):
        pass

    def handleViewStaff(self):
        pass

    def handleViewSiteReport(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleExploreSite(self):
        pass

    def handleExploreEvent(self):
        pass

    def handleViewTransitHistory(self):
        pass

    def handleViewVisitHistory(self):
        pass

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
        pass

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
        pass

    def handleManageUser(self):
        pass

    def handleManageTransit(self):
        pass

    def handleManageSite(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleExploreSite(self):
        pass

    def handleExploreEvent(self):
        pass

    def handleViewTransitHistory(self):
        pass

    def handleViewVisitHistory(self):
        pass

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
        pass

    def handleManageUser(self):
        pass

    def handleManageTransit(self):
        pass

    def handleManageSite(self):
        pass

    def handleTakeTransit(self):
        self.hide()
        self.user_take_transit = UserTakeTransit(self, self.username)
        self.user_take_transit.show()
        self.user_take_transit.raise_()

    def handleViewTransitHistory(self):
        pass

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




        self.email_box = EmailBox(self)

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
        self.vbox.addWidget(self.email_box)

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
            or (len(self.email_box.email_list)) == 0 and self.email_box.email_input.text() == '') \
            or user_type == 'Select User Type' \
            or phone == '' \
            or address == '' \
            or city == '' \
            or state == 'Select State' \
            or zipcode == '':
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(phone) != 10):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 10 digit phone number')
        elif (len(zipcode) != 5):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 5 digit zip code')
        else:
            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{password}');"
            cursor.execute(query)

            for x in self.email_box.email_list:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            if (self.email_box.email_input.text() != '' \
                and self.email_box.email_input.text() != ' ' \
                and self.email_box.email_input.text() not in self.email_box.email_list):

                query3 = f"insert into email (username, email) values ('{username}', " \
                    + f"'{self.email_box.email_input.text()}');"

                cursor.execute(query3)

            query4 = f"insert into employee (username, phone, address, city, state, zipcode, employee_type)" \
                    + f"values ('{username}', '{phone}', '{address}', '{city}', " \
                    + f"'{state}', '{zipcode}', '{user_type}');"

            print(query4)

            cursor.execute(query4)

            query5 = f"insert into visitor_list values ('{username}')"
            cursor.execute(query5)


            connection.commit()
            cursor.close()
            print("succesful registration")

            QMessageBox.information(self, 'PyQt5 message', "Your registration was a success!", QMessageBox.Ok)

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




        self.email_box = EmailBox(self)

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
        self.vbox.addWidget(self.email_box)

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
            or (len(self.email_box.email_list)) == 0 and self.email_box.email_input.text() == '') \
            or user_type == 'Select User Type' \
            or phone == '' \
            or address == '' \
            or city == '' \
            or state == 'Select State' \
            or zipcode == '':
            QMessageBox.warning(
                self, 'Error', 'Please fill in all fields')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        elif (len(phone) != 10):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 10 digit phone number')
        elif (len(zipcode) != 5):
            QMessageBox.warning(
                self, 'Error', 'Please provide a valid 5 digit zip code')
        else:
            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{password}');"
            cursor.execute(query)

            for x in self.email_box.email_list:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            if (self.email_box.email_input.text() != '' \
                and self.email_box.email_input.text() != ' ' \
                and self.email_box.email_input.text() not in self.email_box.email_list):

                query3 = f"insert into email (username, email) values ('{username}', " \
                    + f"'{self.email_box.email_input.text()}');"

                cursor.execute(query3)

            query4 = f"insert into employee (username, phone, address, city, state, zipcode, employee_type)" \
                    + f"values ('{username}', '{phone}', '{address}', '{city}', " \
                    + f"'{state}', '{zipcode}', '{user_type}');"

            print(query4)

            cursor.execute(query4)


            connection.commit()
            cursor.close()
            print("succesful registration")

            QMessageBox.information(self, 'PyQt5 message', "Your registration was a success!", QMessageBox.Ok)

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

        self.email_box = EmailBox(self)

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
        self.vbox.addWidget(self.email_box)

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
        email_list = load_db_emails()


        if (username == '' or password == '' or firstname == '' \
            or lastname == '' or confirmpassword == '' \
            or (len(self.email_box.email_list)) == 0 \
            and self.email_box.email_input.text() == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all the text fields')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        else:
            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, lname, status, password) values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{password}');"
            print(query)
            cursor.execute(query)

            for x in self.email_box.email_list:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            if (self.email_box.email_input.text() != '' \
                and self.email_box.email_input.text() != ' ' \
                and self.email_box.email_input.text() not in self.email_box.email_list):

                query3 = f"insert into email (username, email) values ('{username}', " \
                    + f"'{self.email_box.email_input.text()}');"
                cursor.execute(query3)

            query4 = f"insert into visitor_list values ('{username}')"
            cursor.execute(query4)

            connection.commit()
            cursor.close()
            print("succesful registration")

            QMessageBox.information(self, 'PyQt5 message', "Your registration was a success!", QMessageBox.Ok)

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

        self.email_box = EmailBox(self)

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
        self.vbox.addWidget(self.email_box)

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
        email_list = load_db_emails()


        if (username == '' or password == '' or firstname == '' \
            or lastname == '' or confirmpassword == '' \
            or (len(self.email_box.email_list)) == 0 \
            and self.email_box.email_input.text() == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in all the text fields')
        elif (username in username_list):
            QMessageBox.warning(
                self, 'Error', 'The username provided is already an existing user')
        elif (password != confirmpassword):
            QMessageBox.warning(
                self, 'Error', 'The password and confirm password fields must match exactly')
        else:
            cursor = connection.cursor()
            query = f"insert into user (username, user_type, fname, " \
                + "lname, status, password) " \
                + f"values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{password}');"
            cursor.execute(query)

            for x in self.email_box.email_list:

                query2 = f"insert into email (username, email) values ('{username}', '{x}');"
                cursor.execute(query2)

            if (self.email_box.email_input.text() != '' \
                and self.email_box.email_input.text() != ' ' \
                and self.email_box.email_input.text() not in self.email_box.email_list):

                query3 = f"insert into email values ('{username}', " \
                    + f"'{self.email_box.email_input.text()}');"
                cursor.execute(query3)

            connection.commit()
            cursor.close()
            print("succesful registration")

            QMessageBox.information(self, 'PyQt5 message', "Your registration was a success!", QMessageBox.Ok)

            self.close()
            self.parent.back()


class EmailBox(QGroupBox):
    def __init__(self, parent, email_count=0):
        super(EmailBox, self).__init__(parent)
        self.parent = parent
        self.email_count = email_count

        self.vbox = QVBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()

        self.setLayout(self.vbox)

        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)

        self.email_list = []

        self.added_email_label = QLabel("Added Email(s): ")
        self.added_emails = QLabel(" ")
        self.remove_button = QPushButton("Remove Last")
        self.remove_button.clicked.connect(self.handle_remove_email)

        self.hbox1.addWidget(self.added_email_label)
        self.hbox1.addWidget(self.added_emails)
        self.hbox1.addWidget(self.remove_button)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.handle_add_email)
        self.email_input = QLineEdit()
        self.email_label = QLabel("Email: ")

        self.hbox2.addWidget(self.email_label)
        self.hbox2.addWidget(self.email_input)
        self.hbox2.addWidget(self.add_button)

    def handle_add_email(self):

        cursor = connection.cursor()
        query = "select email from email;"
        cursor.execute(query)


        email1 = self.email_input.text()
        email_format = r'\S+@\S+\.\S+'
        email_check = re.fullmatch(email_format, email1)
        if (email1 == ''):
            QMessageBox.warning(
                self.parent, 'Error', 'Please fill in the email field')
        elif email_check == None:
            QMessageBox.warning(
                self.parent, 'Error', 'Please enter a valid email address')
        elif (email1 in self.email_list):
            QMessageBox.warning(
                self.parent, 'Error', 'Each email must be unique')
        else:
            self.email_list.append(email1)
            self.email_count += 1
            count = self.email_count
            self.parent.hide()
            if (self.email_count == 1):
                self.added_emails.setText(f"{email1}")
            else:
                self.added_emails.setText(f"{self.added_emails.text()},\n {email1}")
            self.parent.show()


    def handle_remove_email(self):


        if (self.email_count == 0):
            QMessageBox.warning(
                self.parent, 'Error', 'There are no emails to remove')
        else:
            x = self.added_emails.text()
            y = self.email_list[self.email_count - 1]
            y_len = len(y)
            x = x[:len(x) - y_len - 2]
            self.parent.hide()
            self.added_emails.setText(f'{x}')
            self.parent.show()
            self.email_list.pop()
            self.email_count -= 1




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
        elif (email not in login_dict.keys()):
            QMessageBox.warning(
                self, 'Error', 'The email provided is not linked to an existing user')
        elif (login_dict[email] != password):
            QMessageBox.warning(
                self, 'Error', 'The password provided is incorrect')
        else:

            cursor = connection.cursor()
            query = 'select status from email join user ' \
                + f"using (username) where email = '{email}';"
            print(query)
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
                print("login success")
                # self.close()
                self.functionality(email)


    def handleRegister(self):
        self.hide()
        self.register_nav = RegisterNavigation(self)
        self.register_nav.show()

    def functionality(self, email):

        cursor = connection.cursor()
        query = 'select username, user_type from email join user ' \
            + f"using (username) where email = '{email}';"
        # print(query)
        cursor.execute(query)

        user_data = [line for line in cursor]
        cursor.close()
        user_type = user_data[0]['user_type']
        username = user_data[0]['username']
        if user_type == 'User':
            # print('user functionality')
            self.hide()
            self.user_func = UserFunctionality(self, username)
            self.user_func.show()
        elif user_type == 'Visitor':
            # print ('visitor functionality')
            self.hide()
            self.visitor_func = VisitorFunctionality(self, username)
            self.visitor_func.show()
        elif user_type == 'Employee':
            cursor = connection.cursor()
            query2 = 'select employee_type from employee join email' \
                + f" using (username) where email = '{email}';"
            cursor.execute(query2)
            user_data = [line for line in cursor]
            cursor.close()
            emp_type = user_data[0]["employee_type"]

            cursor = connection.cursor()
            query3 = 'select username from visitor_list join email ' \
                + f" using (username) where email = '{email}';"
            # print(query3)
            cursor.execute(query3)
            user_data = [line for line in cursor]
            cursor.close()
            visitor = len(user_data)
            # print(visitor)


            if (emp_type == 'Admin' and not visitor):
                print("admin functionality")
                self.hide()
                self.admin_func = AdminFunctionality(self, username)
                self.admin_func.show()
            elif (emp_type == 'Admin' and visitor):
                print("admin-visitor functionality")
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





# class Window(QMainWindow):
#     def __init__(self, parent=None):
#         super(Window, self).__init__(parent)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)






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
        login_dict[user_dict['email']] = user_dict['password']
    return login_dict



if __name__ == '__main__':

    app = QApplication(sys.argv)
    establish_connection(sys.argv[1])
    global login
    login = UserLogin()
    sys.exit(app.exec_())


    # TO RUN THE GUI:
    # python beltline_login.py {insert your mysql password here}





