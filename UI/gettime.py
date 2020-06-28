from PyQt5.QtCore import QDate, QTime,Qt

def getTime():
    now = QDate.currentDate()  # 获取当前日期
    print(now.toString(Qt.ISODate))  # ISO日期格式打印
    year_month_day = now.toString(Qt.DefaultLocaleLongDate)  # 本地化长格式日期打印
    # datetime = QDateTime.currentDateTime()  # 获取当前日期与时间
    # print(datetime.toString())  # 当前日期与时间打印
    time = QTime.currentTime()  # 获取当前时间
    hour_min_sec = time.toString(Qt.DefaultLocaleLongDate)  # 本地化长格式时间打印
    return year_month_day,hour_min_sec

getTime()

__metaclass__ = type
# !coding= utf-8
# http://blog.csdn.net/gatieme/article/details/17659259
# gatieme


# import sys
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
#
#
# # --------------------------------------------------------------------------------
# class SystemTrayIcon(QSystemTrayIcon):
#     """
#     The systemTrayIcon which uesd to connect the clock
#     """
#
#     # ----------------------------------------------------------------------------
#     def __init__(self, mainWindow, parent=None):
#         """
#         mainWindow : the main window that the system tray icon serves to
#         """
#         super(SystemTrayIcon, self).__init__(parent)
#         self.window = mainWindow
#         self.setIcon(QIcon("heart.svg"))  # set the icon of the systemTrayIcon
#
#         self.createActions()
#         self.createTrayMenu()
#
#         self.connect(self, SIGNAL("doubleClicked"), self.window, SLOT("showNormal"))
#         # self.connect(self, SIGNAL("activated( )"), self, SLOT("slot_iconActivated"))
#
#     def createActions(self):
#         """
#         create some action to Max Min Normal show the window
#         """
#         self.minimizeAction = QAction("Mi&nimize", self.window, triggered=self.window.hide)
#         self.maximizeAction = QAction("Ma&ximize", self.window, triggered=self.window.showMaximized)
#         self.restoreAction = QAction("&Restore", self.window, triggered=self.window.showNormal)
#         self.quitAction = QAction("&Quit", self.window, triggered=qApp.quit)
#
#     def createTrayMenu(self):
#         self.trayIconMenu = QMenu(self.window)
#         self.trayIconMenu.addAction(self.minimizeAction)
#         self.trayIconMenu.addAction(self.maximizeAction)
#         self.trayIconMenu.addAction(self.restoreAction)
#         self.trayIconMenu.addSeparator()
#         self.trayIconMenu.addAction(self.quitAction)
#
#         self.setContextMenu(self.trayIconMenu)
#
#     def setVisible(self, visible):
#         self.minimizeAction.setEnabled(not visible)
#         self.maximizeAction.setEnabled(not self.window.isMaximized())
#         self.restoreAction.setEnabled(self.window.isMaximized() or not visible)
#         super(Window, self).setVisible(visible)
#
#     def closeEvent(self, event):
#         # if event.button( ) == Qt.RightButton:
#         self.showMessage("Message",
#                          "The program will keep running in the system tray. To "
#                          "terminate the program, choose <b>Quit</b> in the "
#                          "context menu of the system tray entry.",
#                          QSystemTrayIcon.Information, 5000)
#         self.window.hide()
#         event.ignore()
#
#     def slot_iconActivated(self, reason):
#         if reason == QSystemTrayIcon.DoubleClick:
#             self.wiondow.showNormal()
#
#
# # --------------------------------------------------------------------------------
# class DigitClock(QLCDNumber):
#     """
#     the DigitClock show a digit clock int the printer
#     """
#
#     # ----------------------------------------------------------------------------
#     def __init__(self, parent=None):
#         """
#         the constructor function of the DigitClock
#         """
#         super(DigitClock, self).__init__(parent)
#         pale = self.palette()
#
#         pale.setColor(QPalette.Window, QColor(100, 180, 100))
#         self.setPalette(pale)
#
#         self.setNumDigits(19)
#         self.systemTrayIcon = SystemTrayIcon(mainWindow=self)
#
#         self.dragPosition = None;
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup | Qt.Tool)
#         self.setWindowOpacity(1)
#
#         self.showTime()  # print the time when the clock show
#         self.systemTrayIcon.show()  # show the SystemTaryIcon when the clock show
#
#         self.timer = QTimer()
#         self.connect(self.timer, SIGNAL("timeout( )"), self.showTime)
#         self.timer.start(1000)
#
#         self.resize(500, 60)
#
#     # ----------------------------------------------------------------------------
#     def showTime(self):
#         """
#         show the current time
#         """
#         self.date = QDate.currentDate()
#         self.time = QTime.currentTime()
#         text = self.date.toString("yyyy-MM-dd") + " " + self.time.toString("hh:mm:ss")
#         self.display(text)
#
#     # ----------------------------------------------------------------------------
#     def mousePressEvent(self, event):
#         """
#         clicked the left mouse to move the clock
#         clicked the right mouse to hide the clock
#         """
#         if event.button() == Qt.LeftButton:
#             self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
#             event.accept()
#         elif event.button() == Qt.RightButton:
#             self.systemTrayIcon.closeEvent(event)
#
#             # self.systemTrayIcon.hide( )
#             # self.close( )
#
#     def mouseMoveEvent(self, event):
#         """
#         """
#         if event.buttons() & Qt.LeftButton:
#             self.move(event.globalPos() - self.dragPosition)
#             event.accept()
#
#     def keyPressEvent(self, event):
#         """
#         you can enter "ESC" to normal show the window, when the clock is Maxmize
#         """
#         if event.key() == Qt.Key_Escape and self.isMaximized():
#             self.showNormal()
#
#     def mouseDoubleClickEvent(self, event):
#         """
#         """
#         if event.buttons() == Qt.LeftButton:
#             if self.isMaximized():
#                 self.showNormal()
#             else:
#                 self.showMaximized()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
# 
#     digitClock = DigitClock()
#     digitClock.show()
#
#     sys.exit(app.exec_())
