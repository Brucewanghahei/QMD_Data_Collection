# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created: Thu Jan 21 21:08:06 2016
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1149, 925)
        self.centralwidget = QtGui.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1127, 883))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.groupBox_parameter = QtGui.QGroupBox(self.tab)
        self.groupBox_parameter.setGeometry(QtCore.QRect(20, 10, 191, 811))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_parameter.setFont(font)
        self.groupBox_parameter.setObjectName(_fromUtf8("groupBox_parameter"))
        self.label_starting_value = QtGui.QLabel(self.groupBox_parameter)
        self.label_starting_value.setGeometry(QtCore.QRect(30, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_starting_value.setFont(font)
        self.label_starting_value.setObjectName(_fromUtf8("label_starting_value"))
        self.lineEdit_start = QtGui.QLineEdit(self.groupBox_parameter)
        self.lineEdit_start.setGeometry(QtCore.QRect(30, 50, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_start.setFont(font)
        self.lineEdit_start.setObjectName(_fromUtf8("lineEdit_start"))
        self.pushButton_plot = QtGui.QPushButton(self.groupBox_parameter)
        self.pushButton_plot.setGeometry(QtCore.QRect(60, 690, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_plot.setFont(font)
        self.pushButton_plot.setObjectName(_fromUtf8("pushButton_plot"))
        self.pushButton_clear = QtGui.QPushButton(self.groupBox_parameter)
        self.pushButton_clear.setEnabled(False)
        self.pushButton_clear.setGeometry(QtCore.QRect(60, 740, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_clear.setFont(font)
        self.pushButton_clear.setObjectName(_fromUtf8("pushButton_clear"))
        self.textEdit_peaks_steps = QtGui.QTextEdit(self.groupBox_parameter)
        self.textEdit_peaks_steps.setGeometry(QtCore.QRect(30, 120, 131, 551))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.textEdit_peaks_steps.setFont(font)
        self.textEdit_peaks_steps.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textEdit_peaks_steps.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit_peaks_steps.setTabStopWidth(80)
        self.textEdit_peaks_steps.setCursorWidth(2)
        self.textEdit_peaks_steps.setObjectName(_fromUtf8("textEdit_peaks_steps"))
        self.label_2 = QtGui.QLabel(self.groupBox_parameter)
        self.label_2.setGeometry(QtCore.QRect(30, 90, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.groupBox_save_general = QtGui.QGroupBox(self.tab)
        self.groupBox_save_general.setGeometry(QtCore.QRect(230, 10, 541, 171))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_save_general.setFont(font)
        self.groupBox_save_general.setObjectName(_fromUtf8("groupBox_save_general"))
        self.lineEdit_array_name = QtGui.QLineEdit(self.groupBox_save_general)
        self.lineEdit_array_name.setGeometry(QtCore.QRect(20, 50, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_array_name.setFont(font)
        self.lineEdit_array_name.setObjectName(_fromUtf8("lineEdit_array_name"))
        self.label_4 = QtGui.QLabel(self.groupBox_save_general)
        self.label_4.setGeometry(QtCore.QRect(20, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.pushButton_save = QtGui.QPushButton(self.groupBox_save_general)
        self.pushButton_save.setEnabled(False)
        self.pushButton_save.setGeometry(QtCore.QRect(440, 70, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.label_6 = QtGui.QLabel(self.groupBox_save_general)
        self.label_6.setGeometry(QtCore.QRect(20, 80, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.lineEdit_directory_save = QtGui.QLineEdit(self.groupBox_save_general)
        self.lineEdit_directory_save.setGeometry(QtCore.QRect(20, 110, 501, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_directory_save.setFont(font)
        self.lineEdit_directory_save.setObjectName(_fromUtf8("lineEdit_directory_save"))
        self.pushButton_browse_save = QtGui.QPushButton(self.groupBox_save_general)
        self.pushButton_browse_save.setGeometry(QtCore.QRect(440, 30, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_browse_save.setFont(font)
        self.pushButton_browse_save.setObjectName(_fromUtf8("pushButton_browse_save"))
        self.label_10 = QtGui.QLabel(self.groupBox_save_general)
        self.label_10.setGeometry(QtCore.QRect(230, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.lineEdit_user_name = QtGui.QLineEdit(self.groupBox_save_general)
        self.lineEdit_user_name.setGeometry(QtCore.QRect(230, 50, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_user_name.setFont(font)
        self.lineEdit_user_name.setObjectName(_fromUtf8("lineEdit_user_name"))
        self.groupBox_plot = QtGui.QGroupBox(self.tab)
        self.groupBox_plot.setGeometry(QtCore.QRect(230, 190, 851, 631))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_plot.setFont(font)
        self.groupBox_plot.setObjectName(_fromUtf8("groupBox_plot"))
        self.mplwidget_general = MatplotlibWidget(self.groupBox_plot)
        self.mplwidget_general.setGeometry(QtCore.QRect(350, 270, 16, 16))
        self.mplwidget_general.setObjectName(_fromUtf8("mplwidget_general"))
        self.widget_general = QtGui.QWidget(self.groupBox_plot)
        self.widget_general.setGeometry(QtCore.QRect(0, 10, 851, 621))
        self.widget_general.setObjectName(_fromUtf8("widget_general"))
        self.groupBox_condition_general = QtGui.QGroupBox(self.tab)
        self.groupBox_condition_general.setGeometry(QtCore.QRect(790, 10, 291, 171))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_condition_general.setFont(font)
        self.groupBox_condition_general.setObjectName(_fromUtf8("groupBox_condition_general"))
        self.textEdit_condition = QtGui.QTextEdit(self.groupBox_condition_general)
        self.textEdit_condition.setGeometry(QtCore.QRect(20, 50, 251, 81))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textEdit_condition.setFont(font)
        self.textEdit_condition.setObjectName(_fromUtf8("textEdit_condition"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.groupBox_import_keithley = QtGui.QGroupBox(self.tab_2)
        self.groupBox_import_keithley.setGeometry(QtCore.QRect(10, 10, 391, 151))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_import_keithley.setFont(font)
        self.groupBox_import_keithley.setObjectName(_fromUtf8("groupBox_import_keithley"))
        self.lineEdit_directory_keithley = QtGui.QLineEdit(self.groupBox_import_keithley)
        self.lineEdit_directory_keithley.setGeometry(QtCore.QRect(20, 50, 351, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_directory_keithley.setFont(font)
        self.lineEdit_directory_keithley.setObjectName(_fromUtf8("lineEdit_directory_keithley"))
        self.label_7 = QtGui.QLabel(self.groupBox_import_keithley)
        self.label_7.setGeometry(QtCore.QRect(20, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.pushButton_browse_keithley = QtGui.QPushButton(self.groupBox_import_keithley)
        self.pushButton_browse_keithley.setGeometry(QtCore.QRect(80, 100, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_browse_keithley.setFont(font)
        self.pushButton_browse_keithley.setObjectName(_fromUtf8("pushButton_browse_keithley"))
        self.pushButton_import_keithley = QtGui.QPushButton(self.groupBox_import_keithley)
        self.pushButton_import_keithley.setEnabled(False)
        self.pushButton_import_keithley.setGeometry(QtCore.QRect(220, 100, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_import_keithley.setFont(font)
        self.pushButton_import_keithley.setObjectName(_fromUtf8("pushButton_import_keithley"))
        self.tabWidget_keithely = QtGui.QTabWidget(self.tab_2)
        self.tabWidget_keithely.setGeometry(QtCore.QRect(10, 250, 1081, 581))
        self.tabWidget_keithely.setObjectName(_fromUtf8("tabWidget_keithely"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.widget_import = QtGui.QWidget(self.tab_3)
        self.widget_import.setGeometry(QtCore.QRect(0, 0, 1081, 551))
        self.widget_import.setObjectName(_fromUtf8("widget_import"))
        self.mplwidget_import = MatplotlibWidget(self.widget_import)
        self.mplwidget_import.setGeometry(QtCore.QRect(520, 230, 16, 16))
        self.mplwidget_import.setObjectName(_fromUtf8("mplwidget_import"))
        self.tabWidget_keithely.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.mplwidget_scan = MatplotlibWidget(self.tab_4)
        self.mplwidget_scan.setGeometry(QtCore.QRect(540, 240, 16, 16))
        self.mplwidget_scan.setObjectName(_fromUtf8("mplwidget_scan"))
        self.widget_scan = QtGui.QWidget(self.tab_4)
        self.widget_scan.setGeometry(QtCore.QRect(0, 0, 1081, 551))
        self.widget_scan.setObjectName(_fromUtf8("widget_scan"))
        self.tabWidget_keithely.addTab(self.tab_4, _fromUtf8(""))
        self.groupBox_condition_keithley = QtGui.QGroupBox(self.tab_2)
        self.groupBox_condition_keithley.setGeometry(QtCore.QRect(10, 160, 391, 81))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_condition_keithley.setFont(font)
        self.groupBox_condition_keithley.setObjectName(_fromUtf8("groupBox_condition_keithley"))
        self.lineEdit_condition_keithley = QtGui.QLineEdit(self.groupBox_condition_keithley)
        self.lineEdit_condition_keithley.setGeometry(QtCore.QRect(20, 30, 351, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit_condition_keithley.setFont(font)
        self.lineEdit_condition_keithley.setObjectName(_fromUtf8("lineEdit_condition_keithley"))
        self.groupBox_visa_keithley = QtGui.QGroupBox(self.tab_2)
        self.groupBox_visa_keithley.setEnabled(False)
        self.groupBox_visa_keithley.setGeometry(QtCore.QRect(410, 10, 381, 231))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_visa_keithley.setFont(font)
        self.groupBox_visa_keithley.setObjectName(_fromUtf8("groupBox_visa_keithley"))
        self.label_chooseVisa = QtGui.QLabel(self.groupBox_visa_keithley)
        self.label_chooseVisa.setGeometry(QtCore.QRect(20, 20, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_chooseVisa.setFont(font)
        self.label_chooseVisa.setObjectName(_fromUtf8("label_chooseVisa"))
        self.comboBox_visa_keithley = QtGui.QComboBox(self.groupBox_visa_keithley)
        self.comboBox_visa_keithley.setGeometry(QtCore.QRect(20, 50, 341, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox_visa_keithley.setFont(font)
        self.comboBox_visa_keithley.setObjectName(_fromUtf8("comboBox_visa_keithley"))
        self.pushButton_select_keithley = QtGui.QPushButton(self.groupBox_visa_keithley)
        self.pushButton_select_keithley.setGeometry(QtCore.QRect(70, 100, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_select_keithley.setFont(font)
        self.pushButton_select_keithley.setObjectName(_fromUtf8("pushButton_select_keithley"))
        self.pushButton_close_keithley = QtGui.QPushButton(self.groupBox_visa_keithley)
        self.pushButton_close_keithley.setGeometry(QtCore.QRect(220, 100, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_close_keithley.setFont(font)
        self.pushButton_close_keithley.setObjectName(_fromUtf8("pushButton_close_keithley"))
        self.label_8 = QtGui.QLabel(self.groupBox_visa_keithley)
        self.label_8.setGeometry(QtCore.QRect(20, 150, 311, 27))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.lineEdit_visa_keithley = QtGui.QLineEdit(self.groupBox_visa_keithley)
        self.lineEdit_visa_keithley.setGeometry(QtCore.QRect(20, 180, 341, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_visa_keithley.setFont(font)
        self.lineEdit_visa_keithley.setObjectName(_fromUtf8("lineEdit_visa_keithley"))
        self.groupBox_scan_keithley = QtGui.QGroupBox(self.tab_2)
        self.groupBox_scan_keithley.setEnabled(False)
        self.groupBox_scan_keithley.setGeometry(QtCore.QRect(800, 10, 291, 231))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_scan_keithley.setFont(font)
        self.groupBox_scan_keithley.setObjectName(_fromUtf8("groupBox_scan_keithley"))
        self.label = QtGui.QLabel(self.groupBox_scan_keithley)
        self.label.setGeometry(QtCore.QRect(80, 30, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_9 = QtGui.QLabel(self.groupBox_scan_keithley)
        self.label_9.setGeometry(QtCore.QRect(160, 30, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.radioButton_voltage = QtGui.QRadioButton(self.groupBox_scan_keithley)
        self.radioButton_voltage.setGeometry(QtCore.QRect(50, 60, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.radioButton_voltage.setFont(font)
        self.radioButton_voltage.setChecked(True)
        self.radioButton_voltage.setObjectName(_fromUtf8("radioButton_voltage"))
        self.radioButton_current = QtGui.QRadioButton(self.groupBox_scan_keithley)
        self.radioButton_current.setGeometry(QtCore.QRect(50, 90, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.radioButton_current.setFont(font)
        self.radioButton_current.setObjectName(_fromUtf8("radioButton_current"))
        self.pushButton_scan_keithley = QtGui.QPushButton(self.groupBox_scan_keithley)
        self.pushButton_scan_keithley.setGeometry(QtCore.QRect(50, 130, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_scan_keithley.setFont(font)
        self.pushButton_scan_keithley.setObjectName(_fromUtf8("pushButton_scan_keithley"))
        self.pushButton_stop_keithley = QtGui.QPushButton(self.groupBox_scan_keithley)
        self.pushButton_stop_keithley.setGeometry(QtCore.QRect(160, 130, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_stop_keithley.setFont(font)
        self.pushButton_stop_keithley.setObjectName(_fromUtf8("pushButton_stop_keithley"))
        self.pushButton_clear_keithley = QtGui.QPushButton(self.groupBox_scan_keithley)
        self.pushButton_clear_keithley.setGeometry(QtCore.QRect(100, 180, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_clear_keithley.setFont(font)
        self.pushButton_clear_keithley.setObjectName(_fromUtf8("pushButton_clear_keithley"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_keithely.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox_parameter.setTitle(_translate("MainWindow", "Parameter", None))
        self.label_starting_value.setText(_translate("MainWindow", "Starting Value:", None))
        self.pushButton_plot.setText(_translate("MainWindow", "Plot", None))
        self.pushButton_clear.setText(_translate("MainWindow", "Clear", None))
        self.label_2.setText(_translate("MainWindow", "Steps, Repeat, Peaks:", None))
        self.groupBox_save_general.setTitle(_translate("MainWindow", "Save", None))
        self.label_4.setText(_translate("MainWindow", "Array Name:", None))
        self.pushButton_save.setText(_translate("MainWindow", "Save", None))
        self.label_6.setText(_translate("MainWindow", "Directory:", None))
        self.pushButton_browse_save.setText(_translate("MainWindow", "Browse", None))
        self.label_10.setText(_translate("MainWindow", "User Name:", None))
        self.groupBox_plot.setTitle(_translate("MainWindow", "Plot", None))
        self.groupBox_condition_general.setTitle(_translate("MainWindow", "Condition", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "General Array", None))
        self.groupBox_import_keithley.setTitle(_translate("MainWindow", "Import", None))
        self.label_7.setText(_translate("MainWindow", "Array Import:", None))
        self.pushButton_browse_keithley.setText(_translate("MainWindow", "Browse", None))
        self.pushButton_import_keithley.setText(_translate("MainWindow", "Import", None))
        self.tabWidget_keithely.setTabText(self.tabWidget_keithely.indexOf(self.tab_3), _translate("MainWindow", "Import Plot", None))
        self.tabWidget_keithely.setTabText(self.tabWidget_keithely.indexOf(self.tab_4), _translate("MainWindow", "Scan Plot", None))
        self.groupBox_condition_keithley.setTitle(_translate("MainWindow", "Condition", None))
        self.groupBox_visa_keithley.setTitle(_translate("MainWindow", "Visa", None))
        self.label_chooseVisa.setText(_translate("MainWindow", "Choose VISA", None))
        self.pushButton_select_keithley.setText(_translate("MainWindow", "Select", None))
        self.pushButton_close_keithley.setText(_translate("MainWindow", "Close", None))
        self.label_8.setText(_translate("MainWindow", "VISA name:", None))
        self.lineEdit_visa_keithley.setText(_translate("MainWindow", "None", None))
        self.groupBox_scan_keithley.setTitle(_translate("MainWindow", "Scan", None))
        self.label.setText(_translate("MainWindow", "X-Value", None))
        self.label_9.setText(_translate("MainWindow", "Y-Value", None))
        self.radioButton_voltage.setText(_translate("MainWindow", "  Voltage      Current", None))
        self.radioButton_current.setText(_translate("MainWindow", "  Current      Voltage", None))
        self.pushButton_scan_keithley.setText(_translate("MainWindow", "Scan", None))
        self.pushButton_stop_keithley.setText(_translate("MainWindow", "Stop", None))
        self.pushButton_clear_keithley.setText(_translate("MainWindow", "Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Keithley", None))

from matplotlibwidget import MatplotlibWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

