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
    QHBoxLayout
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QPixmap)


class RegisterUser(QWidget):
    def __init__(self, parent):
        super(RegisterUser, self).__init__()
        self.setWindowTitle("Register Navigation")

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
            or lastname == '' or confirmpassword == ''):
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
            query = f"insert into user values ('{username}', 'User'," \
                + f"'{firstname}', '{lastname}', 'Pending', '{password}');"
            cursor.execute(query)
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
        print("register visitor")

    def register_employee(self):
        print("register employee ")

    def register_emp_visitor(self):
        print("register employee visitor")

    def back(self):
        self.close()
        self.parent.show()




class UserLogin(QWidget):
    def __init__(self, parent=None):
        super(UserLogin, self).__init__(parent)
        self.setWindowTitle("Atlanta Beltline Login")
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonLogin.setDefault(True)
        self.buttonRegister.setDefault(False)

        form_group_box = QGroupBox()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Username: "), self.username)
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

        username = self.username.text()
        password = self.password.text()

        if (username == '' or password == ''):
            QMessageBox.warning(
                self, 'Error', 'Please fill in both the username and the password fields')
        elif (username not in login_dict.keys()):
            QMessageBox.warning(
                self, 'Error', 'The username provided is not an existing user')
        elif (login_dict[username] != password):
            QMessageBox.warning(
                self, 'Error', 'The password provided is incorrect')
        else:
            print("login success")
            self.close()


    def handleRegister(self):
        self.hide()
        self.register_nav = RegisterNavigation(self)
        self.register_nav.show()





class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
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
    cursor.execute('select * from user;')
    user_data = [line for line in cursor]
    cursor.close()
    global login_dict
    login_dict = {}
    for user_dict in user_data:
        login_dict[user_dict['username']] = user_dict['password']
    return login_dict



if __name__ == '__main__':

    app = QApplication(sys.argv)
    establish_connection(sys.argv[1])
    global login
    login = UserLogin()
    sys.exit(app.exec_())


    # TO RUN THE GUI:
    # python beltline_login.py {insert your mysql password here}





