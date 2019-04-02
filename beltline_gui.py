from pprint import pprint

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

        self.parent = parent
        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.confirmpassword = QLineEdit(self)

        form_group_box = QGroupBox()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("First Name: "), self.firstname)
        form_layout.addRow(QLabel("Last Name: "), self.lastname)
        form_layout.addRow(QLabel("Username: "), self.username)
        form_layout.addRow(QLabel("Password: "), self.password)
        form_layout.addRow(QLabel("Confirm Password: "), self.confirmpassword)
        form_group_box.setLayout(form_layout)

        form_group_box2 = QGroupBox()
        form_layout2 = QFormLayout()
        self.email = QLineEdit(self)
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.handle_add_email)
        form_layout2.addRow(QLabel("Email: "), self.email)
        form_layout2.addRow(self.add_button)
        form_group_box2.setLayout(form_layout2)


        self.buttonBack = QPushButton('Back', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonBack.clicked.connect(self.handleBack)
        self.buttonRegister.clicked.connect(self.handleRegister)
        self.buttonRegister.setDefault(True)

        form_group_box3 = QGroupBox()
        form_layout3 = QFormLayout()
        form_layout3.addRow(self.buttonRegister, self.buttonBack)
        form_group_box3.setLayout(form_layout3)

        # hbox = QHBoxLayout()
        # hbox.addWidget(self.buttonRegister)
        # hbox.addWidget(self.buttonBack)

        vbox = QVBoxLayout()
        vbox.addWidget(form_group_box)
        vbox.addWidget(form_group_box2)
        # vbox.addWidget(self.buttonRegister)
        # vbox.addWidget(self.buttonBack)

        vbox.addWidget(form_group_box3)

        # vbox.addWidget(self.buttonRegister)
        # vbox.addWidget(self.buttonBack)

        self.setLayout(vbox)

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
            cursor.close()
            print("succesful registration")

            QMessageBox.information(self, 'PyQt5 message', "Your registration was a success!", QMessageBox.Ok)

            load_login_data()

            self.close()
            self.parent.back()



    def handle_add_email(self):
        pass




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




class UserLogin(QDialog):
    def __init__(self, parent=None):
        super(UserLogin, self).__init__(parent)
        self.setWindowTitle("Atlanta Beltline Login")
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonRegister = QPushButton('Register', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonRegister.clicked.connect(self.handleRegister)

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


    def handleLogin(self):

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
            print("successful login")
            self.accept()


    def handleRegister(self):
        self.hide()
        self.register_nav = RegisterNavigation(self)
        self.register_nav.show()





class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)






def establish_connection():
    global connection
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='Brav3s10!',
                                     db='beltline',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print(f"Couldn't log {login.user.text()} in to MySQL server on {login.host.text()}")
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


def login_sequence():
    login_dict = load_login_data()
    global login
    login = UserLogin()

    if login.exec_() == QDialog.Accepted:
        print("successful login")

def main():
    app = QApplication(sys.argv)

    # global connection
    # global login_dict
    # global login

    establish_connection()

    login_sequence()


    sys.exit(app.exec_())



if __name__ == '__main__':

    main()









# SCRAPPED:


# def register_sequence():
#     global register_nav
#     register_nav = RegisterNavigation()
#     register_nav.show()
#     # while register_nav.click == 0:
#     #     pass



 # login_dict = load_login_data()

    # login = UserLogin(login_dict)

    # if login.exec_() == QDialog.Accepted:
    #     if (login.mode == 1):
    #         pass
    #     elif (login.mode == 2):
    #         pass


    # window = Window()
    # window.show()
