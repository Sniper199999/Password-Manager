from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_msgbox_cnguser(object):
    def setupUi(self, msgbox_cnguser):
        self.msgz = msgbox_cnguser
        self.msgz.setObjectName("self.msgz")
        self.msgz.resize(305, 165)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.msgz.sizePolicy().hasHeightForWidth())
        self.msgz.setSizePolicy(sizePolicy)
        self.msgz.setMinimumSize(QtCore.QSize(305, 165))
        self.msgz.setMaximumSize(QtCore.QSize(305, 165))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.msgz.setPalette(palette)
        self.frame = QtWidgets.QFrame(self.msgz)
        self.frame.setGeometry(QtCore.QRect(0, 125, 311, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.frame.setPalette(palette)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.btn_box = QtWidgets.QDialogButtonBox(self.frame)
        self.btn_box.setGeometry(QtCore.QRect(133, 6, 161, 32))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.btn_box.setPalette(palette)
        self.btn_box.setOrientation(QtCore.Qt.Horizontal)
        self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.Save|QtWidgets.QDialogButtonBox.Cancel)
        self.btn_box.setCenterButtons(False)
        self.btn_box.setObjectName("btn_box")
        self.lbl_1 = QtWidgets.QLabel(self.msgz)
        self.lbl_1.setGeometry(QtCore.QRect(62, 11, 241, 16))
        self.lbl_1.setObjectName("lbl_1")
        self.lbl_2 = QtWidgets.QLabel(self.msgz)
        self.lbl_2.setGeometry(QtCore.QRect(62, 33, 211, 16))
        self.lbl_2.setObjectName("lbl_2")
        self.lbl_exclamation = QtWidgets.QLabel(self.msgz)
        self.lbl_exclamation.setGeometry(QtCore.QRect(10, 10, 45, 45))
        self.lbl_exclamation.setStyleSheet("background-color: transparent;")
        self.lbl_exclamation.setText("")
        self.lbl_exclamation.setPixmap(QtGui.QPixmap("C:\\Users\\Leader\\Desktop\\../Downloads/pngguru.com.png"))
        self.lbl_exclamation.setScaledContents(True)
        self.lbl_exclamation.setObjectName("lbl_exclamation")
        self.tbox_cng_user = QtWidgets.QLineEdit(self.msgz)
        self.tbox_cng_user.setGeometry(QtCore.QRect(90, 58, 201, 20))
        self.tbox_cng_user.setInputMask("")
        self.tbox_cng_user.setText("")
        self.tbox_cng_user.setObjectName("tbox_cng_user")
        self.tbox_pass = QtWidgets.QLineEdit(self.msgz)
        self.tbox_pass.setGeometry(QtCore.QRect(90, 90, 201, 20))
        self.tbox_pass.setObjectName("tbox_pass")
        self.lbl_pass = QtWidgets.QLabel(self.msgz)
        self.lbl_pass.setGeometry(QtCore.QRect(36, 91, 51, 16))
        self.lbl_pass.setObjectName("lbl_pass")
        self.lbl_new_user = QtWidgets.QLabel(self.msgz)
        self.lbl_new_user.setGeometry(QtCore.QRect(10, 57, 71, 20))
        self.lbl_new_user.setObjectName("lbl_new_user")
        self.lbl_show_pass = QtWidgets.QLabel(self.msgz)
        self.lbl_show_pass.setGeometry(QtCore.QRect(267, 90, 21, 20))
        self.lbl_show_pass.setText("")
        self.lbl_show_pass.setPixmap(QtGui.QPixmap("showpass.png"))
        self.lbl_show_pass.setScaledContents(True)
        self.lbl_show_pass.setObjectName("lbl_show_pass")

        self.lbl_confirm_2fa = QtWidgets.QLabel(self.msgz)
        self.lbl_confirm_2fa.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.lbl_confirm_2fa.setObjectName("lbl_confirm_2fa")

        self.lbl_show_qr = QtWidgets.QLabel(self.msgz)
        self.lbl_show_qr.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.lbl_show_qr.setScaledContents(True)
        self.lbl_show_qr.setObjectName("lbl_show_qr")

        self.tbox_confirm_2fa = QtWidgets.QLineEdit(self.msgz)
        self.tbox_confirm_2fa.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.tbox_confirm_2fa.setObjectName("tbox_confrim_2fa")

        self.tbox_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.retranslateUi(self.msgz)
        self.btn_box.accepted.connect(self.msgz.accept)
        self.btn_box.rejected.connect(self.msgz.reject)
        QtCore.QMetaObject.connectSlotsByName(self.msgz)

    def retranslateUi(self, msgbox_cnguser):
        _translate = QtCore.QCoreApplication.translate
        msgbox_cnguser.setWindowTitle(_translate("msgbox_cnguser", "Warning!"))
        msgbox_cnguser.setWindowIcon(QtGui.QIcon('lock-icon.png'))
        self.lbl_1.setText(_translate("msgbox_cnguser", "Matching Username Found In Existing Database!"))
        self.lbl_2.setText(_translate("msgbox_cnguser", "Please Change Your Account\'s Username!"))
        self.tbox_cng_user.setPlaceholderText(_translate("msgbox_cnguser", "Change Username!"))
        self.tbox_pass.setPlaceholderText(_translate("msgbox_cnguser", "Your Old Password"))
        self.tbox_confirm_2fa.setPlaceholderText(_translate("msgbox_cnguser", "Otp Code From Google Authenticator"))
        self.lbl_pass.setText(_translate("msgbox_cnguser", "Password"))
        self.lbl_new_user.setText(_translate("msgbox_cnguser", "New Username"))
        self.lbl_confirm_2fa.setText(_translate("msgbox_cnguser", "Confirm 2FA"))

    def zaf(self, mode):
        self.msgz.setWindowTitle("Delete 2FA")
        self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.tbox_pass.setGeometry(QtCore.QRect(70, 58, 221, 20))
        self.tbox_cng_user.setGeometry(QtCore.QRect(0, 0, 0, 0))   # hide
        self.lbl_pass.setGeometry(QtCore.QRect(13, 57, 51, 16))
        self.lbl_new_user.setGeometry(QtCore.QRect(0, 0, 0, 0))     # hide
        self.lbl_show_pass.setGeometry(QtCore.QRect(267, 58, 21, 20))
        self.frame.setGeometry(QtCore.QRect(0, 90, 311, 41))
       # self.btn_box.setGeometry(QtCore.QRect(133, 6, 161, 32))

        self.msgz.setMaximumSize(QtCore.QSize(305, 131))
        self.msgz.setMinimumSize(QtCore.QSize(305, 131))
        self.lbl_confirm_2fa.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.tbox_confirm_2fa.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.lbl_show_qr.setGeometry(QtCore.QRect(0, 0, 0, 0))
        if mode == 0:
            self.lbl_1.setText("You Really Want To Delete 2FA?")
            self.lbl_2.setText("Enter Account Password To confirm Action")
        else:
            self.lbl_1.setText("You Really Want To Delete Your Main Account?")
            self.lbl_2.setText("Enter Account Password To confirm Action")
        self.tbox_pass.setPlaceholderText("????????????????????????")


    def add2fa_gui(self):
        self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        self.lbl_1.setText("Scan QR CODE in Google Authenticator")
        self.lbl_2.setText("Then Enter the generated code to confirm!")
        self.msgz.setMaximumSize(QtCore.QSize(305, 300))
        self.msgz.setMinimumSize(QtCore.QSize(305, 300))
        self.frame.setGeometry(QtCore.QRect(0, 260, 311, 41))
        self.lbl_confirm_2fa.setGeometry(QtCore.QRect(13, 230, 61, 20))
        self.tbox_confirm_2fa.setGeometry(QtCore.QRect(84, 230, 211, 20))
        self.lbl_show_qr.setGeometry(QtCore.QRect(72, 59, 161, 161))
        self.tbox_pass.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.tbox_cng_user.setGeometry(QtCore.QRect(0, 0, 0, 0))  # hide
        self.lbl_pass.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.lbl_new_user.setGeometry(QtCore.QRect(0, 0, 0, 0))  # hide
        self.lbl_show_pass.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.msgz.setWindowTitle("Add 2FA")

