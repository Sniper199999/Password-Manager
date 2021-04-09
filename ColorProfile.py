from PyQt5 import QtCore, QtGui

def select_color(color: str, no: int, self):
    if color == str("red"):
        set_color = QtGui.QBrush(QtGui.QColor(255, 0, 0))
    else:
        set_color = QtGui.QBrush(QtGui.QColor(0, 121, 0))
    palette = QtGui.QPalette()
    brush = set_color
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
    brush = set_color
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
    brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
    lbl = [self.ui.lbl_warn_login, self.ui.lbl_warn_signup, self.ui.lbl_warn_add, 0,
           self.ui.lbl_warn_pgen, 0]
    lbl[no].setPalette(palette)
