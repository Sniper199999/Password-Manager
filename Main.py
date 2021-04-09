import concurrent.futures
import gc
import pathlib
import sqlite3
import sys
import time
import traceback
import tracemalloc
import csv
from tqdm import tqdm
import PyQt5
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QRunnable, pyqtSlot, QThreadPool, QObject, QFileInfo
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMenu, QMessageBox, QFileDialog
from ColorProfile import select_color
from GUI import Ui_MainWindow
from enc_dec import encrypt, decrypt
import sysinfo
import string
from random import *
from PopupUI import Ui_msgbox_cnguser
import qrcode
import pyotp


#QR Code generation....
class Image(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        print(border, width, box_size)
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(
            size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QtGui.QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)

    def save(self, stream, kind=None):
        pass


class DialogBox(QtWidgets.QDialog, Ui_msgbox_cnguser):
    def __init__(self,parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    leng = pyqtSignal(int)

#Multithreading implementation
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

#This Runs first...
class MyWork(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWork, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)      #Calls GUI.py, loads the GUI
        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.say_hello("kakabura")
        self.table_dict = None
        self.update_list = 0
        self.num = None
        self.event = None
        self.result = None
        self.counter = 0
        self.val = 1
        self.user_id = None
        self.logged_in = False
        self.show_pass_val = False

        self.dlb = DialogBox()
        self.ui.setupUi(self)
        #self.handle()
       # self.ui.tbox_user_signup.textChanged.connect(self.handle)

        self.ui.acnCsv_New_Acc.triggered.connect(self.btn_import_clk)
        self.ui.acnLogout.triggered.connect(self.btn_logout_clk)
        self.ui.acnExit.triggered.connect(self.close)
        self.ui.acnRefresh_db.triggered.connect(self.btn_refresh_clk)
        self.ui.acnDel_mainacc.triggered.connect(self.del_main_acc)
        self.ui.acnDark.triggered.connect(self.dark)
        self.ui.acnDefault.triggered.connect(self.default)
        #self.ui.acnAdd_2FA.triggered.connect()
        self.ui.acnDel_2FA.triggered.connect(self.del2fa)
        self.ui.acnAdd_2FA.triggered.connect(self.add2fa)
        self.ui.acnExport_CSV.triggered.connect(self.btn_export_clk)



        # CheckBox actions
        self.ui.chkbox_2fa_signup.stateChanged.connect(self.chkbox_toggled)
        self.ui.tbox_search.textChanged.connect(self.handleTextEntered)
        #self.ui.tbox_user_login.textChanged.connect(self.asd)
        self.dlb.tbox_cng_user.textChanged.connect(self.import_cng_username)

        self.ui.tab_login.currentChanged.connect(self.onChange)
        #Show Pass Lbl
        self.dlb.lbl_show_pass.mouseReleaseEvent = lambda event: self.show_pass(6)
        self.ui.lbl_showpass1_signup.mouseReleaseEvent = lambda event: self.show_pass(0)
        self.ui.lbl_showpass2_signup.mouseReleaseEvent = lambda event: self.show_pass(1)
        self.ui.lbl_showpass_add.mouseReleaseEvent = lambda event: self.show_pass(3)
        self.ui.lbl_showpass_edit.mouseReleaseEvent = lambda event: self.show_pass(4)
        self.ui.lbl_showpass_login.mouseReleaseEvent = lambda event: self.show_pass(2)
        self.ui.lbl_showpass_pgen.mouseReleaseEvent = lambda event: self.show_pass(5)

        # Button actons
        args = 1
        self.ui.btn_login.clicked.connect(self.log_btn_clk)
        self.ui.btn_signup.clicked.connect(self.reg_btn_clk)
        self.ui.btn_logout.clicked.connect(self.btn_logout_clk)
        self.ui.btn_save_add.clicked.connect(self.save_btn_clk)
        self.ui.btn_delete_action.clicked.connect(self.del_btn_clk)
        self.ui.btn_edit_action.clicked.connect(self.edit_btn_clk)
        self.ui.btn_apply_edit.clicked.connect(self.apply_btn_clk)
        self.ui.btn_refresh.clicked.connect(self.btn_refresh_clk)
        self.ui.btn_genpass.clicked.connect(self.btn_genpass_clk)
        self.ui.btn_cpy_pass.clicked.connect(self.btn_cpy_clk)
        self.ui.btn_export.clicked.connect(self.btn_export_clk)
        self.ui.btn_signup_done.clicked.connect(self.signup_done_clk)
        #self.ui.btn_submit_login.clicked.connect(self.submit_login_clk)
        self.ui.btn_submit_login.mouseReleaseEvent = lambda event: self.submit_login_clk(self.totp)

        # CellClicked
        self.ui.table_view.cellDoubleClicked.connect(self.cell_was_clicked)
        self.ui.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.table_view.customContextMenuRequested.connect(self.showMenu)

        self.disablebtn(True)


    # Register
    def signup_done_clk(self):
        self.ui.stk_signup.setCurrentIndex(0)
        self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 195))

    def reg_btn_clk(self):
        username_reg = str(self.ui.tbox_user_signup.text())
        pass_reg = str(self.ui.tbox_pass_signup.text())
        pass_confirm = str(self.ui.tbox_repass_signup.text())
        totp = ""
        no = 1
        if len(username_reg) == 0 or len(pass_reg) == 0 or len(pass_confirm) == 0:
            print("Input Fields Cannot Be Empty!")
            select_color(str("red"), no, self)
            self.ui.lbl_warn_signup.setText("Input Fields Cannot Be Empty!")
        else:
            conn = sqlite3.connect('User.db')
            c = conn.cursor()
            c.execute("SELECT 'User' FROM security WHERE `User` = ? ", (username_reg,))
            result = c.fetchall()
            if result:
                select_color(str("red"), no, self)
                self.ui.lbl_warn_signup.setText("Username Already Exists...")
                print("Username Already Exists Please Select a Different Username")
                self.ui.tbox_user_signup.setText("")
            elif pass_reg == pass_confirm:
                if len(pass_reg) < 8:
                    select_color(str("red"), no, self)
                    self.ui.lbl_warn_signup.setText("Password Must Have Atleast 8 Characters!")
                    print("Password Should Be Atleast 8 Characters Long!")
                else:
                    if self.ui.chkbox_2fa_signup.isChecked() == True:
                        self.ui.stk_signup.setCurrentIndex(1)
                        self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 331))
                        self.ui.stk_signup.setGeometry(QtCore.QRect(3, 3, 261, 301))
                        totp = self.handle(username_reg, pass_reg, self.ui.lbl_qr_signup)
                    print(username_reg, pass_reg)
                    c = conn.cursor()
                    c.execute('INSERT INTO security(User, Hash, Topt) VALUES(?,?,?)',
                              (username_reg, encrypt(pass_reg, username_reg), totp))
                    conn.commit()
                    # print(c.lastrowid)
                    select_color(str("green"), no, self)
                    self.ui.lbl_warn_signup.setText("New Account Registerd!")
                    self.ui.listWidget.addItem("New Account Registered!")
                    self.ui.listWidget.scrollToBottom()
                    print("New Account Registerd!")
                    self.ui.tbox_pass_signup.setText("")
                    self.ui.tbox_user_signup.setText("")
                    self.ui.tbox_repass_signup.setText("")
            else:
                print("Passwords Doesnt match Please Retype!")
                select_color(str("red"), no, self)
                self.ui.lbl_warn_signup.setText("Passwords Doesnt match Please Retype!")
                self.ui.tbox_repass_signup.setText("")
            conn.close()
        print("out of loop")


    #Login
    def submit_login_clk(self, can):
        totp = can
        print(totp.now())
        if self.ui.tbox_otp_login.text() == totp.now():
            print("Current OTP:", totp.now())
            print("valid")
            self.ui.stk_user.setCurrentIndex(1)
            print("Logged In..")
            self.ui.acnAdd_2FA.setDisabled(True)
            self.disablebtn(False)
            self.ui.tbox_pass_login.setText("")
            self.ui.tbox_user_login.setText("")
            #item = "Welcome " + username
            self.ui.listWidget.addItem("Logged In...")
            #self.ui.listWidget.addItem(item)
            self.load()
            #return 1
        else:
            print("wrong")
            #return 0

    def log_btn_clk(self):
        tracemalloc.start()
        username = str(self.ui.tbox_user_login.text())
        pass1 = str(self.ui.tbox_pass_login.text())
        no = 0
        print("USER:-", username, "/ PASS:-", pass1)
        conn = sqlite3.connect('User.db')
        if len(username) == 0 or len(pass1) == 0:
            print("Input Fields Cannot Be Empty!")
            select_color(str("red"), no, self)
            self.ui.lbl_warn_login.setText("Input Fields Cannot Be Empty!")
        else:
            c = conn.cursor()
            c.execute("SELECT * FROM security WHERE `User` = ? ", (username,))
            row = c.fetchone()
            conn.close()
            if row:
                print("ID:-", row[0], "/ USER:- ", row[1], "/ HASH:-", row[2], "/ Hash1:-", row[3])
                try:
                    if decrypt(pass1, row[2]) == username:
                        print("dawdawww")
                        self.logged_in = True
                        self.user_id = row[0]
                        self.main_pass = pass1
                        self.username = username
                        if row[3] != "":
                            can = decrypt(pass1, row[3])
                            print(can)
                            self.ui.stk_login.setCurrentIndex(1)
                            self.totp = pyotp.TOTP(can)
                        else:
                            #self.ui.stk_user.setCurrentIndex(1)
                            select_color(str("green"), no, self)
                            print("Logged In..")
                            item = "Welcome " + username
                            self.ui.listWidget.addItem("Logged In...")
                            self.ui.listWidget.addItem(item)
                            self.ui.listWidget.scrollToBottom()
                            self.ui.tbox_user_login.setText("")
                            self.ui.tbox_pass_login.setText("")
                            self.ui.acnDel_2FA.setDisabled(True)
                            self.disablebtn(False)
                            self.load()
                except Exception as ex:
                    select_color(str("red"), no, self)
                    print("You Entered The Wrong Password!", ex)
                    self.ui.lbl_warn_login.setText("You Entered The Wrong Password!")
            else:
                select_color(str("red"), no, self)
                print("No Such User!")
                self.ui.lbl_warn_login.setText("No such user!")
        gc.collect()
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        for stat in top_stats[:10]:
            print(stat)
        print("out for the loop")

    def load(self):
        zu = see()
        worker = Worker(zu.maina, self.user_id, self.main_pass)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.loads)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.setProgressVal)
        self.threadpool.start(worker)

    def loads(self, result):
        print("adaddwdwd", result)
        self.ui.table_view.setRowCount(0)
        t1 = time.perf_counter()
        for row_no, row_data in enumerate(result):
            #row_number = result.index(row_data)
            print("ROW:-", row_no, "/ DATA:-", row_data)
            self.ui.table_view.setSortingEnabled(False)
            self.ui.table_view.insertRow(row_no)
            for column_no, data in enumerate(row_data):
                #column_number = row_data.index(data)
                self.ui.table_view.setItem(row_no, column_no, QtWidgets.QTableWidgetItem(str(data)))
            self.ui.table_view.setSortingEnabled(True)
        t2 = time.perf_counter()
        print("Time Taken:-", t2 - t1)
        self.ui.stk_user.setCurrentIndex(1)
        return

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def setProgressVal(self, val):
        self.counter += 1
        vals = self.counter * 100 / val
        print(val, self.counter, int(vals),"%")
        self.ui.progressBar.setValue(int(vals))
        if vals == 100:
            ku = see()
            setzero = Worker(ku.time)  # Any other args, kwargs are passed to the run function
            setzero.signals.result.connect(self.setProgressZero)
            self.threadpool.start(setzero)

    def setProgressZero(self):
        self.ui.progressBar.setValue(0)
        self.counter = 0


    # Logout
    def btn_logout_clk(self):
        self.logged_in = False
        self.ui.table_view.setRowCount(0)
        self.ui.stk_user.setCurrentIndex(0)
        self.ui.stk_login.setCurrentIndex(0)
        self.ui.progressBar.setValue(0)
        self.counter = 0
        self.val = 1
        self.ui.listWidget.addItem("Logged Out...")
        self.ui.listWidget.scrollToBottom()
        self.disablebtn(True)


    # Delete Main Account From DataBase...
    def del_main_acc(self):
        conn = sqlite3.connect('User.db')
        c = conn.cursor()
        c.execute("SELECT `Hash` FROM security WHERE `User` = ?", (self.username,))
        result = c.fetchone()
        print(result[0])
        self.dlb.zaf(1)
        while self.dlb.exec_():
            if self.dlb.tbox_pass.text() != 0:
                try:
                    if decrypt(str(self.dlb.tbox_pass.text()), result[0]) == self.username:
                        user_id = self.user_id
                        self.btn_logout_clk()
                        conn2 = sqlite3.connect('Accounts.db')
                        c2 = conn2.cursor()
                        c2.execute("DELETE FROM accounts WHERE `security_ID` = ?", (user_id,))
                        conn2.commit()
                        conn2.close()
                        conn1 = sqlite3.connect('User.db')
                        c1 = conn1.cursor()
                        c1.execute("DELETE FROM security WHERE `ID` = ?", (user_id,))
                        conn1.commit()
                        conn1.close()
                        print("Deleted ID", user_id)
                        self.ui.listWidget.addItem("Account Deleted Permanently!")
                        self.ui.listWidget.scrollToBottom()
                        self.disablebtn(True)
                        break
                except:
                    print("Error")
                    continue
            else:
                continue
        print("cancel")
        self.dlb.tbox_pass.setText("")


    # add 2 Factor Authentication
    def add2fa(self):
        totp_hash = self.handle(self.username, self.main_pass, self.dlb.lbl_show_qr)
        self.dlb.add2fa_gui()
        # totp = self.handle(self.username, self.main_pass, self.dlb.lbl_show_qr)
        while self.dlb.exec_():
            print("awddwdd")
            if self.dlb.tbox_confirm_2fa.text() != "":
                can = decrypt(self.main_pass, totp_hash)
                print(can)
                totp = pyotp.TOTP(can)
                print(totp.now())
                if self.dlb.tbox_confirm_2fa.text() == totp.now():
                    print("Current OTP:", totp.now())
                    conn = sqlite3.connect('User.db')
                    c = conn.cursor()
                    c.execute("UPDATE security SET `Topt` = ? WHERE `User` = ?", (totp_hash, self.username))
                    conn.commit()
                    self.ui.acnDel_2FA.setDisabled(False)
                    self.ui.acnAdd_2FA.setDisabled(True)
                    self.ui.listWidget.addItem("2FA Added!")
                    self.ui.listWidget.scrollToBottom()
                    break
                else:
                    continue
            else:
                continue
        self.dlb.tbox_confirm_2fa.setText("")

    # delete 2 Factor Authentication...
    def del2fa(self):
        conn = sqlite3.connect('User.db')
        c = conn.cursor()
        c.execute("SELECT `Hash` FROM security WHERE `User` = ?", (self.username,))
        result = c.fetchone()
        print(result[0])
        self.dlb.zaf(0)
        while self.dlb.exec_():
            if self.dlb.tbox_pass.text() != 0:
                try:
                    if decrypt(str(self.dlb.tbox_pass.text()), result[0]) == self.username:
                        print("dawdawww")
                        c.execute("UPDATE security SET 'Topt' = ? WHERE `User` = ?", ("", self.username))
                        conn.commit()
                        conn.close()
                        print("Deleted")
                        self.ui.acnDel_2FA.setDisabled(True)
                        self.ui.acnAdd_2FA.setDisabled(False)
                        self.ui.listWidget.addItem("2FA Removed!")
                        self.ui.listWidget.scrollToBottom()
                        break
                except Exception as ex:
                    print("Error")
                    continue
            else:
                continue
        self.dlb.tbox_pass.setText("")

    def handle(self, user, password, label):
        salt = pyotp.random_base32()
        url = pyotp.totp.TOTP(salt).provisioning_uri(user, issuer_name="1PassGo!")
        label.setPixmap(
            qrcode.make(url, image_factory=Image).pixmap())
        # totp = pyotp.TOTP(salt)
        # totp = pyotp.TOTP("VADCBKIX63IN7O4E")
        aa = encrypt(password, salt)
        print(aa)
        # print("Current OTP:", totp.now())
        return aa


    #GUI
    def onChange(self, id):
        if id == 0:
            if self.ui.stk_login.currentIndex() == 1:
                self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 141))
            else:
                self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 141))
        else:
            if self.ui.stk_signup.currentIndex() == 1:
                self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 331))
            else:
                self.ui.tab_login.setGeometry(QtCore.QRect(0, 0, 265, 185))
            #self.chkbox_toggled()

    def dark(self):
        sshFile = "black.qss"
        with open(sshFile, "r") as fh:
            self.ui.centralwidget.setStyleSheet(fh.read())
        print("done")
        fh.close()
        sshFile = "black_menubar.qss"
        with open(sshFile, "r") as fh:
            self.ui.menubar.setStyleSheet(fh.read())
        print("done")
        fh.close()
        sshFile = "black_tab.qss"
        with open(sshFile, "r") as fh:
            self.ui.tab_login.setStyleSheet(fh.read())
        print("done")
        fh.close()

    def default(self):
        self.ui.centralwidget.setStyleSheet("")
        self.ui.menubar.setStyleSheet("")
        self.ui.tab_login.setStyleSheet("")

    def show_pass(self, event):
        chk = [self.ui.tbox_pass_signup, self.ui.tbox_repass_signup, self.ui.tbox_pass_login, self.ui.tbox_pass_add,
               self.ui.tbox_pass_edit, self.ui.tbox_genpass_pgen, self.dlb.tbox_pass]
        if self.show_pass_val is False:
            print(event)
            chk[event].setEchoMode(QtWidgets.QLineEdit.Normal)
            self.show_pass_val = True
        else:
            chk[event].setEchoMode(QtWidgets.QLineEdit.Password)
            self.show_pass_val = False

    def tick_box_login(self, state):
        self.tk_box(state, 0)

    def tick_box_reg(self, state):
        self.tk_box(state, 1)

    def tick_box_edit(self, state):
        self.tk_box(state, 3)

    def tick_box_add(self, state):
        self.tk_box(state, 2)

    def tick_box_pgen(self, state):
        self.tk_box(state, 4)

    def tk_box(self, state, val):
        chk = [self.ui.tbox_pass_login, self.ui.tbox_pass_signup, self.ui.tbox_pass_add, self.ui.tbox_pass_edit,
               self.ui.tbox_genpass_pgen]
        if state == QtCore.Qt.Checked:
            print("Show Password")
            chk[val].setEchoMode(QtWidgets.QLineEdit.Normal)
            if val == 1:
                self.ui.tbox_repass_signup.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            print("Hide Password")
            chk[val].setEchoMode(QtWidgets.QLineEdit.Password)
            if val == 1:
                self.ui.tbox_repass_signup.setEchoMode(QtWidgets.QLineEdit.Password)

    # disable/enable buttons....
    def disablebtn(self, bool):
        if bool is True:
            self.ui.menuImport_Db.setDisabled(True)
            self.ui.acnExport_db.setDisabled(True)
            self.ui.acnLight.setDisabled(True)
            self.ui.acnCng_masterpass.setDisabled(True)
            self.ui.acnCng_username.setDisabled(True)
            self.ui.acnCsv_Update_Acc.setDisabled(True)
        self.ui.btn_refresh.setDisabled(bool)
        # self.ui.table_view.setDisabled(True)
        self.ui.btn_logout.setDisabled(bool)
        self.ui.btn_export.setDisabled(bool)
        self.ui.menuImport_CSV.setDisabled(bool)
        self.ui.acnExport_CSV.setDisabled(bool)
        self.ui.acnLogout.setDisabled(bool)
        self.ui.acnExit.setDisabled(bool)
        self.ui.acnRefresh_db.setDisabled(bool)
        self.ui.menuAccount.setDisabled(bool)


    #CSV
    def btn_export_clk(self):
        if self.logged_in is True:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Database", "untitled.csv", "CSV Files (*.csv)",
                                                      options=options)
            if fileName:
                print(fileName)
                if fileName.find(".csv") == -1:
                    fileName = fileName + '.csv'
                print(fileName)
                conn1 = sqlite3.connect('User.db')
                c1 = conn1.cursor()
                c1.execute("SELECT User, User, Hash, Topt FROM security WHERE `ID` = ?", (self.user_id,))
                conn2 = sqlite3.connect('Accounts.db')
                c2 = conn2.cursor()
                c2.execute("SELECT Account, User, Hash, Date FROM accounts WHERE `security_ID` = ?", (self.user_id,))
                with open(fileName, "w", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerows(c1)
                    csv_writer.writerow([i[0] for i in c2.description])
                    csv_writer.writerows(c2)
                conn1.close()
                conn2.close()
                item = "CSV exported to:- " + fileName
                self.ui.listWidget.addItem(item)
                self.ui.listWidget.scrollToBottom()

                #self.btn_import_clk()

    def db_connect(self, database, username):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT 'User' FROM security WHERE `User` = ? ", (username,))
        result = c.fetchone()
        conn.close()
        return result

    def import_cng_username(self):
        new_user = self.dlb.tbox_cng_user.text()
        return new_user

    def btn_import_clk(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Load CSV File", "", "CSV Files (*.csv)", options=options)
        if fileName:
            print(fileName)
            if fileName.find(".csv") == -1:
                fileName = fileName + '.csv'
            print(fileName)
            with open(fileName, "r", newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
                conn1 = sqlite3.connect('User.db')
                conn2 = sqlite3.connect('Accounts.db')
                db_list = []
                user_changed = False
                for row_no, data in enumerate(csv_reader):
                    user = data[0]
                    if row_no == 0:
                        pass_hash = data[2]
                        topt = data[3]
                        result = self.db_connect("User.db", data[0])
                        if result:
                            print("Username already exists in existing database! Please Change Your Username")
                            while self.dlb.exec_():
                                new_user = self.import_cng_username()
                                if new_user != "":
                                    check = self.db_connect("User.db", new_user)
                                    if check:
                                        print("Usename already Exists")
                                        continue
                                else:
                                    continue
                                password = self.dlb.tbox_pass.text()
                                try:
                                    print(data[2])
                                    if decrypt(password, data[2]) == user:
                                        user = new_user
                                        pass_hash = encrypt(password, user)
                                        user_changed = True
                                        print("Username Changed!")
                                        break
                                except Exception as ex:
                                    print("You Entered The Wrong Password!", ex)
                                    continue
                            self.dlb.tbox_pass.setText("")
                            self.dlb.tbox_cng_user.setText("")
                            if user_changed is False:
                                break
                        if not result or user_changed is True:
                            c = conn1.cursor()
                            c.execute('INSERT INTO security(User, Hash, Topt) VALUES(?,?,?)', (user, pass_hash, topt))
                            conn1.commit()
                            user_id = c.lastrowid
                            conn1.close()
                            print("Acount Added!")
                            self.ui.listWidget.addItem("New Account Added!")
                            self.ui.listWidget.scrollToBottom()

                    if row_no > 1:
                        row = [data[0], data[1], data[2], data[3], user_id]
                        db_list.append(row)
                print(db_list)
                c = conn2.cursor()
                c.executemany('INSERT INTO accounts(Account, User, Hash, Date, security_ID) VALUES(?,?,?,?,?)', db_list)
                conn2.commit()
                conn2.close()
            print("Done")


    #Refresh Database
    def btn_refresh_clk(self):
        if self.logged_in is True:
            self.ui.table_view.setRowCount(0)
            self.load()
            self.ui.listWidget.addItem("Database Refreshed!")
            self.ui.listWidget.scrollToBottom()
        else:
            print("You have not logged in!")


    #Generate Random Password
    def btn_cpy_clk(self):
        no = 4
        password = self.ui.tbox_genpass_pgen.text()
        if password != "":
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(password)
            print("copied", password)
            select_color(str("green"), no, self)
            self.ui.lbl_warn_pgen.setText("Password Copied To Clipboard!")
        else:
            print("empty")

    def btn_genpass_clk(self):
        no = 4
        length = self.ui.tbox_slen_pgen.text()
        if length.isdigit():
            characters = string.ascii_letters + string.digits + string.punctuation
            password = "".join(choice(characters) for _ in range(int(length)))
            self.ui.tbox_genpass_pgen.setText(password)
            select_color(str("green"), no, self)
            self.ui.lbl_warn_pgen.setText("New Password Generated!")
        else:
            select_color(str("red"), no, self)
            self.ui.lbl_warn_pgen.setText("Only Numbers are expected!")


    #Table
    def cell_was_clicked(self, row, column):
        print("Row %d and Column %d was clicked" % (row, column))
        if column == 1 or column == 2:
            self.copySlot(None, column, row)
        elif column == 2:
            self.copySlot(None, column, row)
        return

    def copySlot(self, event, mode, rowdata):
        print(event)
        if rowdata is None:
            row = self.ui.table_view.rowAt(event.y())
        else:
            row = rowdata
        print(row)
        cell = self.ui.table_view.item(row, 1)
        data = cell.data(Qt.DisplayRole)
        print(data)
        if mode == 2:
            cell = self.ui.table_view.item(row, 0)
            acc_name = cell.data(Qt.DisplayRole)
            conn = sqlite3.connect('Accounts.db')
            conn.commit()
            c = conn.cursor()
            c.execute("SELECT Hash FROM accounts WHERE `Account` = ? AND `User` = ?", (acc_name, data))
            result = c.fetchone()
            conn.close()
            for hash in result:
                print("match found:-", hash)
                data = self.decrypt_pass(hash)
            self.ui.listWidget.addItem("Password Copied To Clipboard!")
        else:
            self.ui.listWidget.addItem("Username Copied To Clipboard!")
        self.ui.listWidget.scrollToBottom()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(data)
        print("copied", data)
        self.ui.listWidget.scrollToBottom()
        return

    def autofill(self, event):
        print(event)
        row = self.ui.table_view.rowAt(event.y())
        # col = self.ui.table_view.columnAt(event.x())
        print(row)
        col = 0
        cell = self.ui.table_view.item(row, col)
        data = cell.data(Qt.DisplayRole)
        print(data)
        while col <= 1:
            item = self.ui.table_view.item(row, col)
            data = item.data(Qt.DisplayRole)
            print(data)
            if col == 0:
                self.ui.tbox_acc_action.setText(data)
            else:
                self.ui.tbox_user_action.setText(data)
            col = col + 1
        return

    def showMenu(self, event):
        print(event.x())
        menu = QMenu()
        copy_user_action = menu.addAction("Copy Username")
        copy_pass_action = menu.addAction("Copy Password")
        delete_action = menu.addAction("Delete")
        autofill_action = menu.addAction("Auto Fill")
        action = menu.exec_(QtGui.QCursor.pos())
        if action == copy_user_action:
            self.copySlot(event, 1, None)
        elif action == copy_pass_action:
            self.copySlot(event, 2, None)
        elif action == delete_action:
            self.event = event
            self.num = 3
            self.del_btn_clk()
        elif action == autofill_action:
            self.autofill(event)

    def decrypt_pass(self, data):
        main_pass = str(self.main_pass)
        new = decrypt(main_pass, data)
        print("pass = ", new)
        return new


    #Search Table
    def handleTextEntered(self):
        print("adsawdawdwd")
        if self.table_dict is None and self.update_list == 0:
            print("list is none")
            self.backup()
        check = self.ui.tbox_search.text()
        print(check)
        table_dict = self.table_dict
        self.ui.table_view.setRowCount(0)
        row_no = 0
        for idx in table_dict:
            # print("ACCOUNT:-", idx[0], "        USERNAME:-", idx[1])
            if idx[0].find(check) != -1 or idx[1].find(check) != -1 or (table_dict[idx])[1].find(check) != -1:
                print("Match Found : " + str(idx))
                self.ui.table_view.setSortingEnabled(False)
                self.ui.table_view.insertRow(row_no)
                column_no = 2
                self.ui.table_view.setItem(row_no, 0, QtWidgets.QTableWidgetItem(idx[0]))
                self.ui.table_view.setItem(row_no, 1, QtWidgets.QTableWidgetItem(idx[1]))
                for cell in table_dict[idx]:
                    self.ui.table_view.setItem(row_no, column_no, QtWidgets.QTableWidgetItem(cell))
                    column_no += 1
                row_no += 1
                self.ui.table_view.setSortingEnabled(True)
            else:
                # self.ui.table_view.setRowCount(0)
                # print('Found Nothing')
                pass
            # print(results)


    #Add Accounts
    def save_btn_clk(self):
        acc_name = str(self.ui.tbox_acc_add.text())
        username = str(self.ui.tbox_user_add.text())
        password = str(self.ui.tbox_pass_add.text())
        user_id = self.user_id
        no = 2
        if len(username) == 0 or len(password) == 0 or len(acc_name) == 0:
            print("Input Fields Cannot Be Empty!")
            select_color(str("red"), no, self)
            self.ui.lbl_warn_add.setText("Input Fields Cannot Be Empty!")
        else:
            conn = sqlite3.connect('Accounts.db')
            c = conn.cursor()
            c.execute("SELECT Account, User FROM accounts WHERE `Account` = ? AND `User` = ? AND `security_ID` = ?",
                      (acc_name, username, user_id))
            result = c.fetchall()
            if result:
                for _ in result:
                    select_color(str("red"), no, self)
                    self.ui.lbl_warn_add.setText("Username Already Exists...")
                    print("Username Already Exists, Select a Different Username")
                    self.ui.tbox_user_add.setText("")
                    break
            elif len(password) < 8:
                select_color(str("red"), no, self)
                self.ui.lbl_warn_add.setText("Password Must Have Atleast 8 Characters!")
                print("Password Should Be Atleast 8 Characters Long!")
            else:
                now = QDate.currentDate()
                date = now.toString(Qt.DefaultLocaleShortDate)
                print(acc_name, username, password, str(self.main_pass), date)
                c = conn.cursor()
                c.execute('INSERT INTO accounts(Account, User, Hash, Date, security_ID) VALUES(?,?,?,?,?)'
                          , (acc_name, username, encrypt(str(self.main_pass), password), date, user_id))
                conn.commit()
                select_color(str("green"), no, self)
                self.ui.lbl_warn_add.setText("New Account Registerd!")
                self.ui.listWidget.addItem("New Account Added In DB!")
                self.ui.listWidget.scrollToBottom()
                check = self.ui.tbox_search.text()
                hid_pass = str("")
                for _ in password:
                    hid_pass += str("●")
                if check == "" or acc_name.find(check) != -1 or username.find(check) != -1 or date.find(
                        check) != -1:
                    new_row = self.ui.table_view.rowCount()
                    print("row count add", new_row)
                    self.ui.table_view.setSortingEnabled(False)
                    self.ui.table_view.insertRow(new_row)
                    temp_list = [acc_name, username, hid_pass, date]
                    for column in range(self.ui.table_view.columnCount()):
                        print("column no:-", column)
                        new_column = temp_list[column]
                        print(new_column)
                        print("column no:-", column)
                        self.ui.table_view.setItem(
                            new_row, column, QtWidgets.QTableWidgetItem(new_column))
                    self.ui.table_view.setSortingEnabled(True)
                if self.table_dict is None and self.update_list == 0:
                    print("list is none")
                    self.backup()
                key = (acc_name, username)
                list1 = [hid_pass, date]
                table_dict = self.table_dict
                table_dict[key] = list1
                print(table_dict)
                self.table_dict = table_dict
            conn.close()
        print("out of loop")


    #Accounts Action
    def action_sec(self):
        no = 3
        acc_name = str(self.ui.tbox_acc_action.text())
        username = str(self.ui.tbox_user_action.text())
        conn = sqlite3.connect('Accounts.db')
        conn.commit()
        c = conn.cursor()
        c.execute("SELECT Account, User FROM accounts WHERE `Account` = ? AND `User` = ?", (acc_name, username))
        result = c.fetchall()
        conn.close()
        if result:
            for row in result:
                print("match found:-", row)
                return "%s-%s-%s" % (1, acc_name, username)
        else:
            print("account name, username mismatch!")
            return "%s-%s-%s" % (0, None, None)

    def del_btn_clk(self):
        event = self.event
        no = 3
        # mode value comes from def showMenu...
        username, acc_name = None, None
        if self.num == 3:
            row = self.ui.table_view.rowAt(event.y())
            col = 0
            while col <= 1:
                cell = self.ui.table_view.item(row, col)
                if col == 0:
                    acc_name = cell.data(Qt.DisplayRole)
                else:
                    username = cell.data(Qt.DisplayRole)
                col += 1
            print("acc:-", acc_name, "   user:-", username)
            val = str("1")
        else:
            val, acc_name, username = self.action_sec().split("-")
            print("acc:-", acc_name, "   user:-", username)
        self.num = None
        if val == str("1"):
            a = str("This will Delete the corresponding data of..")
            b = str(str("Account:-" + acc_name) + str("\nUsername :-" + username))
            value = self.show_popup("Are You Sure?", a, b)
            if value == 1024:
                self.update_table(acc_name, username, None, None, None, str("delete"))
                # trial(self, acc_name, username, None, None, None, str("delete"))
                item = "Acc:-" + acc_name + " & User:-" + username + " has been deleted!"
                self.ui.listWidget.addItem(item)
                self.ui.listWidget.scrollToBottom()
                select_color(str("red"), no, self)
                self.ui.lbl_warn_action.setText("Account Deleted Successfully!")
                conn = sqlite3.connect('Accounts.db')
                conn.commit()
                c = conn.cursor()
                c.execute("DELETE FROM accounts WHERE `Account` = ? AND `User` = ?", (acc_name, username))
                conn.commit()
                conn.close()
            else:
                print("Cancel Pressed!")
        else:
            print("No Such Account/User")
            select_color(str("red"), no, self)
            self.ui.lbl_warn_action.setText("No Such Account/User!")

    def show_popup(self, title, message, info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setInformativeText(info)
        msg.setWindowTitle(title)
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.resize(200, 300)
        retval = msg.exec_()
        print("value of pressed message box button:", retval)
        return retval

    def edit_btn_clk(self):
        no = 3
        val, acc_name, username = self.action_sec().split("-")
        if val == str("1"):
            self.ui.stk_action.setCurrentIndex(1)
            return "%s-%s" % (acc_name, username)
        else:
            print("No Such Account/User")
            select_color(str("red"), no, self)
            self.ui.lbl_warn_action.setText("No Such Account/User!")

    def apply_btn_clk(self):
        no = 5
        cng_user = str(self.ui.tbox_user_edit.text())
        cng_pass = str(self.ui.tbox_pass_edit.text())
        acc_name, username = self.edit_btn_clk().split("-")
        if len(cng_user) != 0 or len(cng_pass) >= 8:
            item2 = None
            mode = str("update")
            conn = sqlite3.connect('Accounts.db')
            c = conn.cursor()
            new_pass = str("")
            for _ in cng_pass:
                new_pass = new_pass + str("●")
            if len(cng_user) != 0 and len(cng_pass) >= 8:
                main_pass = str(self.main_pass)
                enc_pass = encrypt(main_pass, cng_pass)
                c.execute(
                    "UPDATE accounts SET `User` = ?, `Hash` = ? WHERE `Account` = ? AND `User` = ?",
                    (cng_user, enc_pass, acc_name, username))
                self.update_table(acc_name, username, new_pass, cng_user, 2, mode)
                item = "Username changed:- " + username + " -> " + cng_user
                item2 = cng_user + "'s Password has been changed!"
            elif len(cng_user) != 0 and len(cng_pass) == 0:
                c.execute(
                    "UPDATE accounts SET `User` = ? WHERE `Account` = ? AND `User` = ?",
                    (cng_user, acc_name, username))
                self.update_table(acc_name, username, None, cng_user, 0, mode)
                item = "Username changed:- " + username + " -> " + cng_user
            elif len(cng_user) == 0 and len(cng_pass) >= 8:
                main_pass = str(self.main_pass)
                enc_pass = encrypt(main_pass, cng_pass)
                c.execute(
                    "UPDATE accounts SET `Hash` = ? WHERE `Account` = ? AND `User` = ?",
                    (enc_pass, acc_name, username))
                self.update_table(acc_name, username, new_pass, None, 1, mode)
                item = username + "'s Password has been changed!"
            conn.commit()
            conn.close()
            self.ui.stk_action.setCurrentIndex(0)
            self.ui.tbox_user_edit.setText("")
            self.ui.tbox_pass_edit.setText("")
            self.ui.listWidget.addItem(item)
            if item2 is not None:
                self.ui.listWidget.addItem(item2)
            self.ui.listWidget.scrollToBottom()
            select_color(str("green"), 3, self)
            self.ui.lbl_warn_action.setText("Changes made successfully!")
            print("Changes Made Successfully!")
        else:
            if len(cng_pass) >= 1:
                print("Password should be atleast 8 char long!")
                select_color(str("red"), no, self)
                self.ui.lbl_warn_edit.setText("Password should be atleast 8 char long!")
            else:
                print("Either 1 Field Should Be filled!")
                select_color(str("red"), no, self)
                self.ui.lbl_warn_edit.setText("Either 1 Field Should be filled")

    def update_table(self, acc_name, username, new_pass, cng_user, value, mode):
        if self.table_dict is None and self.update_list == 0:
            print("list is none")
            self.backup()
        check = self.ui.tbox_search.text()
        conn = sqlite3.connect('Accounts.db')
        print(acc_name, username)
        conn.commit()
        c = conn.cursor()
        c.execute("SELECT Date FROM accounts WHERE `Account` = ? AND `User` = ?", (acc_name, username))
        date = c.fetchone()
        conn.close()
        if check == "" or acc_name.find(check) != -1 or username.find(check) != -1 or str(date[0]).find(
                check) != -1:
            for row in range(self.ui.table_view.rowCount()):
                find = False
                for column in range(1):
                    item = self.ui.table_view.item(row, column)
                    print("row no:-", row, "  column no:-", column, "  data:-", item.data(Qt.DisplayRole))
                    if item and item.data(Qt.DisplayRole) == acc_name:
                        print("Acc found:-", item.data(Qt.DisplayRole))
                        column += 1
                        item = self.ui.table_view.item(row, column)
                        if item and item.data(Qt.DisplayRole) == username:
                            print("User found:-", item.data(Qt.DisplayRole))
                            if mode == str("update"):
                                temp_list = [[cng_user, None, 1], [new_pass, None, 2], [cng_user, new_pass, 1]]
                                update_column = temp_list[value][0]
                                update_column2 = temp_list[value][1]
                                column_no = temp_list[value][2]
                                self.ui.table_view.setItem(row, column_no, QtWidgets.QTableWidgetItem(update_column))
                                if value == 2:
                                    self.ui.table_view.setItem(row, 2, QtWidgets.QTableWidgetItem(update_column2))
                                find = True
                            else:
                                self.ui.table_view.removeRow(row)
                                find = True
                if find:
                    break
        table_dict = self.table_dict
        for idx in table_dict:
            print("ACCOUNT:-", idx[0], "        USERNAME:-", idx[1])
            if idx[0] == acc_name and idx[1] == username:
                print("Dict Match Found:-" + str(idx))
                if mode == str("update"):
                    temp_list = [[cng_user, table_dict[idx][0]], [idx[1], new_pass], [cng_user, new_pass]]
                    u_name = temp_list[value][0]
                    password = temp_list[value][1]
                    list1 = [password, table_dict[idx][1]]
                    print("Sub-List:-", [password, table_dict[idx][1]])
                    key = (idx[0], u_name)
                    del table_dict[idx]
                    table_dict[key] = list1
                    print(table_dict)
                    self.table_dict = table_dict
                    return
                else:
                    del table_dict[idx]
                    print(table_dict)
                    self.table_dict = table_dict
                    return


    #Backup
    def backup(self):
        table_dict = {}
        for row in range(self.ui.table_view.rowCount()):
            list1 = []
            for column in range(2, 4):
                item = self.ui.table_view.item(row, column)
                list1.insert(column, item.data(Qt.DisplayRole))
            item = self.ui.table_view.item(row, 0)
            item2 = self.ui.table_view.item(row, 1)
            key = (item.data(Qt.DisplayRole), item2.data(Qt.DisplayRole))
            table_dict[key] = list1
        print("Len:", len(table_dict), table_dict)
        self.table_dict = table_dict


    #Dont Know
    def say_hello(self, user_text):
        text = "Hello there, {0}!".format(user_text)
        self.ui.lbl_warn_login.setText(text)

    def update_label(self):
        self.ui.lbl_warn_signup.setText("")

    def chkbox_toggled(self):
            if self.ui.chkbox_2fa_signup.isChecked() == True:
                print("dawdw")
            else:
                print("awdwdwd")


#Login/Multithreading
class see(Ui_MainWindow):
    def leds(self, data):
        hash_len = self.hash_len
        new = decrypt(str(self.m_pass), str(data))
        j = str("")
        for _ in new:
            j += str("●")
        progress = self.progress
        progress.emit(hash_len)
        return j

    def maina(self, user_id, password, progress_callback):
        self.m_pass = password
        conn = sqlite3.connect('Accounts.db')
        print("Main Pass:-", str(self.m_pass))
        c = conn.cursor()
        c.execute("SELECT Account, User, Hash, Date FROM accounts WHERE `security_ID` = ?", (str(user_id),))
        result = c.fetchall()
        conn.close()
        hash_list = []
        start = time.perf_counter()
        for row_data in result:
            hash_list.append(row_data[2])
        self.hash_len = len(hash_list)
        self.progress = progress_callback
        print("adwaddaddawdawdwd", progress_callback)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # results = [executor.map(self.leds, lis) for _ in range(len(lis))]
            results = executor.map(self.leds, hash_list)
        passes = []
        for f in results:
            passes.append(f)
            print(f)
        table = []
        for row_no, row_data in enumerate(result):
            row = []
            for column_no, data in enumerate(row_data):
                if column_no != 2:
                    row.append(data)
                else:
                    row.append(passes[row_no])
            table.append(row)
        finish = time.perf_counter()
        print(f'Finished in {round(finish - start, 2)} second(s)')
        return table

    def time(self, progress_callback):
        print("here")
        time.sleep(1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    dialog = MyWork()
    app.exec_()

if __name__ == "__main__":
    main()
