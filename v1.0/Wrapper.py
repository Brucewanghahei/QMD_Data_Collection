# This is very important because it imports the GUI created earlier using Qt Designer
# To import the GUI from another python file, it is very somple. Just following the following steps:
# 1. Creat an empty file called __init__.py in the same directory as the GUI file
# 2. If the GUI file and __init__.py file are in the same directory as this file, just type "from .GUIfilename import classname"
# 3. If the GUI file and __init__.py file are in the sub file of this file, then type "from subfilename.GUIfilename.GUIfilename import classname"
# classname is the name of the class in the GUI file, usually it should be 'Ui_MainWindow'

from Sub_Scripts.GUI import Ui_MainWindow

# Import numpy library
import numpy

import os

import sys

import datetime

import visa

import math

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# This class controls all the operations of the GUI. This is the main class that contains all the functions that control the GUI.
class MyForm(QMainWindow):
    
    # The __init__ function is what everything the user wants to be initialized when the class is called.
    # Here we shall define the tring functions to corresponding variables.
    # The 'self' variable means that the function is part of the class and can be called inside and outside the class.
    def __init__(self, parent = None):
        
        # Standard GUI code
        QWidget.__init__(self, parent)
        
        # All the GUI data and widgets in the Ui_MainWindow() class is defined to "self.ui"
        # Thus to do anything on the GUI, the commands must go through this variable
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.Refresh_visa()
        
        # Initialize the table in the beginning
        # self.InitalizeTable()

        # For the canvas.
        self.canvas_general = FigureCanvas(self.ui.mplwidget_general.figure)
        self.canvas_general.setParent(self.ui.widget_general)
        # We need the toolbar widget for the canvas
        self.mpl_toolbar_general = NavigationToolbar(self.canvas_general, self.ui.widget_general)
        
        self.canvas_import = FigureCanvas(self.ui.mplwidget_import.figure)
        self.canvas_import.setParent(self.ui.widget_import)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_import = NavigationToolbar(self.canvas_import, self.ui.widget_import)
        
        self.canvas_scan = FigureCanvas(self.ui.mplwidget_scan.figure)
        self.canvas_scan.setParent(self.ui.widget_scan)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_scan = NavigationToolbar(self.canvas_scan, self.ui.widget_scan)
        
        # Create the QVBoxLayout object and add the widget into the layout
        vbox_general = QVBoxLayout()
        # The matplotlib canvas
        vbox_general.addWidget(self.canvas_general)
        # The matplotlib toolbar
        vbox_general.addWidget(self.mpl_toolbar_general)
        self.ui.widget_general.setLayout(vbox_general)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_import = QVBoxLayout()
        # The matplotlib canvas
        vbox_import.addWidget(self.canvas_import)
        # The matplotlib toolbar
        vbox_import.addWidget(self.mpl_toolbar_import)
        self.ui.widget_import.setLayout(vbox_import)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_scan = QVBoxLayout()
        # The matplotlib canvas
        vbox_scan.addWidget(self.canvas_scan)
        # The matplotlib toolbar
        vbox_scan.addWidget(self.mpl_toolbar_scan)
        self.ui.widget_scan.setLayout(vbox_scan)
        
        # Connect the mplwidget with canvas
        self.ui.mplwidget_general = self.canvas_general
        self.ui.mplwidget_import = self.canvas_import
        self.ui.mplwidget_scan = self.canvas_scan
        
        # Connect buttons in the General Array tab
        self.connect(self.ui.pushButton_plot, SIGNAL('clicked()'), self.Plot_general)
        # self.connect(self.ui.pushButton_delete_last, SIGNAL('clicked()'), self.Delete_last)
        self.connect(self.ui.pushButton_clear, SIGNAL('clicked()'), self.Clear)
        self.connect(self.ui.pushButton_save, SIGNAL('clicked()'), self.Save)
        self.connect(self.ui.pushButton_browse_save, SIGNAL('clicked()'), self.Browse_save)
        # self.connect(self.ui.pushButton_browse_import, SIGNAL('clicked()'), self.Browse_import)
        # self.connect(self.ui.pushButton_import, SIGNAL('clicked()'), self.Import_general)
        # Connect buttons in the Keithely tab
        self.connect(self.ui.pushButton_browse_keithley, SIGNAL('clicked()'), self.Browse_keithley)
        self.connect(self.ui.pushButton_import_keithley, SIGNAL('clicked()'), self.Import_keithley)
        self.connect(self.ui.pushButton_close_keithley, SIGNAL('clicked()'), self.Close_keithley)
        self.connect(self.ui.pushButton_select_keithley, SIGNAL('clicked()'), self.Select_keithley)
        self.connect(self.ui.pushButton_scan_keithley, SIGNAL('clicked()'), self.Scan_keithley)
        self.connect(self.ui.pushButton_stop_keithley, SIGNAL('clicked()'), self.Stop_keithley)
        self.connect(self.ui.pushButton_clear_keithley, SIGNAL('clicked()'), self.Clear_keithley)
        
        self.Values = []
        self.Step = []
        self.Peak = []
        self.round = 0
        self.new_start = 0
        
        self.ui.lineEdit_directory_save.setText(os.getcwd())
        
    def Plot_general(self):
        first_available = True
        
        if self.ui.lineEdit_start.text() == '':
            self.ui.textEdit_condition.setText('Please enter Starting Value.')
        elif self.ui.textEdit_peaks_steps.toPlainText() == '':
            self.ui.textEdit_condition.setText('Please enter Peaks and Steps Value.')
        else:
            self.parameters = []
            self.Values = []
            
            para = str(self.ui.textEdit_peaks_steps.toPlainText())
            para = map(str, para.split('\n'))
            for i in range(0, len(para)):
                if para[i] != '':
                    try:
                        para[i] = map(float, para[i].split(','))
                        if len(para[i]) != 3:
                            self.ui.textEdit_condition.setText('Invalid values entered. Please check line #' + str(i + 1) + '.')
                            first_available = False
                            break
                        elif para[i][1] != math.floor(para[i][1]) or para[i][1] < 1:
                            self.ui.textEdit_condition.setText('Please enter an integer repeat value in line #' + str(i + 1) + '.')
                            first_available = False
                            break
                        else:
                            self.parameters.append(para[i])
                            self.ui.textEdit_condition.setText('')
                    except Exception, e:
                        first_available = False
                        self.ui.textEdit_condition.setText('Invalid values entered. Please check line #' + str(i + 1) + '.')
                        break
            
            if first_available:   
                repeat_sub_values = []
                
                start = float(self.ui.lineEdit_start.text())
                step = self.parameters[0][0]
                repeat = int(math.floor(self.parameters[0][1]))
                peak = self.parameters[0][2]
                if peak != start and step == 0:
                    self.ui.textEdit_condition.setText('Invalid values entered. Please check line #' + str(1) + '.')
                else:
                    if peak < start and step > 0:
                        step = -1 * step
                    sub_values = numpy.arange(start, peak + step, step, dtype = 'float')
                    if abs(sub_values[len(sub_values) - 1]) > abs(peak):
                        sub_values[len(sub_values) - 1] = peak
                    if len(self.parameters) == 1:
                        end = len(sub_values)
                    else:
                        end = len(sub_values) - 1
                    for i in range(0, end):
                        for j in range(0, repeat):
                            repeat_sub_values.append(sub_values[i])
                    self.Values.append(repeat_sub_values)
                    for i in range(1, len(self.parameters)):
                        repeat_sub_values = []
                        start = peak
                        step = self.parameters[i][0]
                        repeat = int(math.floor(self.parameters[i][1]))
                        peak = self.parameters[i][2]
                        if peak != start and step == 0:
                            self.ui.textEdit_condition.setText('Invalid values entered. Please check line #' + str(i + 1) + '.')
                            break
                        elif para[i][1] != math.floor(para[i][1]):
                            self.ui.textEdit_condition.setText('Please enter an integer repeat value in line #' + str(i + 1) + '.')
                            first_available = False
                            break
                        else:
                            if peak < start and step > 0:
                                step = -1 * step
                            sub_values = numpy.arange(start, peak + step, step, dtype = 'float')
                            if abs(sub_values[len(sub_values) - 1]) > abs(peak):
                                sub_values[len(sub_values) - 1] = peak
                            if i == len(self.parameters) - 1:
                                end = len(sub_values)
                            else:
                                end = len(sub_values) - 1
                            for i in range(0, end):
                                for j in range(0, repeat):
                                    repeat_sub_values.append(sub_values[i])
                            self.Values.append(repeat_sub_values)
                            
                            print self.Values
                    self.Plot()
                    self.ui.textEdit_condition.setText('Array has been plotted')
                    self.ui.pushButton_clear.setEnabled(True)
                    self.ui.pushButton_save.setEnabled(True)
            # if self.round == 0:
            #     start = float(self.ui.lineEdit_start.text())
            # elif self.round > 0:
            #     start = self.new_start
            # step = float(self.ui.lineEdit_step.text())
            # peak = float(self.ui.lineEdit_peak.text())
            # if peak < start and step > 0:
            #     step = -1 * step;
            # sub_values = numpy.arange(start, peak + step, step, dtype = 'float')
            # if abs(sub_values[len(sub_values) - 1]) > abs(peak):
            #     sub_values[len(sub_values) - 1] = peak
            # self.Peak.append(peak)
            # self.Values.append(sub_values)
            # if step < 0:
            #     self.Step.append(step * -1)
            # else:
            #     self.Step.append(step)
            # self.Plot()
            # 
            # self.AddTable(str(sub_values))
            # self.round += 1
            # self.new_start = peak
            # self.ui.pushButton_delete_last.setEnabled(True)
            # self.ui.pushButton_clear.setEnabled(True)
            # self.ui.pushButton_save.setEnabled(True)
            # self.ui.lineEdit_start.setEnabled(False)
            # self.ui.label_starting_value.setEnabled(False)
    
    def Plot(self):
        x_value = []
        y_value = []
        item = 0
        for i in range(0, len(self.Values)):
            for j in range(0, len(self.Values[i])):
                x_value.append(item)
                x_value.append(item + 1 - 0.0001)
                y_value.append(self.Values[i][j])
                y_value.append(self.Values[i][j])
                item += 1
        
        self.Reset_plot_general()
        self.axes_general.plot(x_value, y_value, marker = '.', linestyle = '-')
        self.axes_general.grid()
        self.axes_general.set_title("Data File Plot")
        self.axes_general.set_xlabel("Steps")
        self.axes_general.set_ylabel("Values")
        self.ui.mplwidget_general.draw()
    
    # This method works to initalize the data table.
    # The data table can show all the values each time you added to the steps
    # def InitalizeTable(self):
    #     variables = ["Values"]
    #     for i in range(len(variables)):
    #         self.ui.tableWidget_trace.insertColumn(0)
    #     self.ui.tableWidget_trace.setHorizontalHeaderLabels(variables)
    # 
    # def AddTable(self, values):
    #     self.ui.tableWidget_trace.insertRow(0)
    #     self.ui.tableWidget_trace.setItem(0, 0, QTableWidgetItem(values))
    
    def Reset_plot_general(self):
        self.ui.mplwidget_general.figure.clear()
        self.axes_general = self.ui.mplwidget_general.figure.add_subplot(111)
        
    def Reset_plot_import(self):
        self.ui.mplwidget_import.figure.clear()
        self.axes_import = self.ui.mplwidget_import.figure.add_subplot(111)
    
    def Reset_plot_scan(self):
        self.ui.mplwidget_scan.figure.clear()
        self.axes_scan = self.ui.mplwidget_scan.figure.add_subplot(111)
        
    # def Delete_last(self):
    #     if len(self.Values) > 0:
    #         self.round -= 1
    #         self.Values = self.Values[:len(self.Values) - 1]
    #         self.Peak = self.Peak[:len(self.Peak) - 1]
    #         x_value = []
    #         y_value = []
    #         item = 0
    #         for i in range(0, len(self.Values)):
    #             for j in range(0, len(self.Values[i])):
    #                 x_value.append(item * self.Step[i])
    #                 x_value.append((item + 1) * self.Step[i] - 0.0001)
    #                 y_value.append(self.Values[i][j])
    #                 y_value.append(self.Values[i][j])
    #                 item += 1
    #         
    #         self.ui.tableWidget_trace.removeRow(0)
    #         
    #         self.Reset_plot_general()
    #         self.axes_general.plot(x_value, y_value, marker = '.', linestyle = '-')
    #         self.axes_general.grid()
    #         self.ui.mplwidget_general.draw()
    #         self.new_start = self.Peak[len(self.Peak) - 1]
    #         if len(self.Values) == 0:
    #             self.Values = []
    #             self.Step = []
    #             self.round = 0
    #             self.new_start = 0
    #     else:
    #         self.Values = []
    #         self.Step = []
    #         self.round = 0
    #         self.new_start = 0
    #         self.ui.textEdit_condition.setText("No more peaks to be deleted.")
    #         self.ui.pushButton_save.setText(False)
                        
    def Clear(self):
        self.Reset_plot_general()
        self.axes_general.grid()
        self.ui.mplwidget_general.draw()
        self.Values = []
        self.ui.textEdit_peaks_steps.clear()
        self.ui.textEdit_condition.setText('')
        self.ui.lineEdit_start.setText('')
        self.ui.lineEdit_array_name.setText('')
        self.ui.lineEdit_user_name.setText('')
        self.ui.pushButton_clear.setEnabled(False)
        self.ui.pushButton_save.setEnabled(False)
    
    def Save(self):
        file_name = self.ui.lineEdit_array_name.text()
        if file_name == '':
            self.ui.textEdit_condition.setText("Please enter the valid array name.")
        else:
            if self.ui.lineEdit_directory_save.text() != "None":
                name = self.ui.lineEdit_directory_save.text() + '\\' + self.ui.lineEdit_array_name.text() + ".array"
                
                f = open(name, 'w')
                f.write("File Name" + "," + file_name + '\n')
                f.write("User Name"  + "," + str(self.ui.lineEdit_user_name.text()) + '\n')
                f.write("Time"  + "," + str(datetime.datetime.now()) + '\n')
                f.write("Parameters"  + "," + str(self.parameters) + '\n')
                f.write("Array Data" + '\n')
                f.write("X_Value" + "," + "Y_Value" + '\n')
                item = 1
                for i in range(0, len(self.Values)):
                    for j in range(0, len(self.Values[i])):
                        f.write(str(item) + ',' + str(self.Values[i][j]) + '\n')
                        item += 1
                f.close()
                
                self.ui.textEdit_condition.setText("File has been saved.")
            else:
                self.ui.textEdit_condition.setText("Please enter the valid saving directory.")
            
    # Tab: General Array
    # Group: Save
    # Search and find the directory of the folder you want to save
    def Browse_save(self):
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getExistingDirectory(self, 'Select Folder to Save', prev_dir)
        if fileDir != '':
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            self.ui.lineEdit_directory_save.setText(fileDir)
        else:
            self.ui.lineEdit_directory_save.setText("None")
            self.ui.textEdit_condition.setText("Please choose valid saving directory.")
    
    # Tab: General Array
    # Group: Import
    # Search and find the directory of the file you want to import
    # def Browse_import(self):
    #     prev_dir = os.getcwd()
    #     fileDir = QFileDialog.getOpenFileName(self, 'Select File to Import', prev_dir)
    #     if fileDir != '':
    #         file_list = str(fileDir).split('/')
    #         for i in range(0, len(file_list) - 1):
    #             if i < len(file_list) - 1:
    #                 open_dir += file_list[i] + '\\'
    #             elif i == len(file_list) - 1:
    #                 open_dir += file_list[i]
    #         fileDir.replace('/', '\\')
    #         self.ui.lineEdit_directory_save.setText(fileDir)
    #         self.ui.pushButton_browse_import.setEnabled(True)
    #     else:
    #         self.ui.textEdit_condition.setText("Please choose valid file import directory.")
    
    # Tab: General Array
    # Group: Import
    # Import the file
    # def Import_general(self):
    #     pass
    
    # Tab: Keithley
    # Group: Import
    # Search and find the directory of the file you want to import
    def Browse_keithley(self):
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getOpenFileName(self, 'Select File to Import', prev_dir, filter="Array Files (*.array)")
        if fileDir != '':
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                global open_dir
                open_dir = ''
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            self.ui.lineEdit_directory_keithley.setText(fileDir)
            self.ui.pushButton_import_keithley.setEnabled(True)
            self.ui.lineEdit_condition_keithley.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
            self.ui.groupBox_visa_keithley.setEnabled(True)
        else:
            self.ui.lineEdit_condition_keithley.setText("Please choose valid file to import.")
    
    # Tab: Keithley
    # Group: Import
    # Import the file ends in ".array"
    def Import_keithley(self):
        divider_found = True
        count = 0
        temp = 0
        x_value = []
        y_value = []
        
        fileDir = self.ui.lineEdit_directory_keithley.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.lineEdit_condition_keithley.setText("Data not found in file. Please check it.")
                divider_found = False
                break
            line = fp.readline()
            line_list = line.split(',')
            if line_list[0].upper() == "Array Data".upper() + '\n':
                break
            count += 1
            
        if divider_found == True:
            line = fp.readline()
            while True:
                line = fp.readline().replace('\n', '')
                if line == '':
                    break
                value = line.split(',')
                x_value.append(temp)
                x_value.append(temp + 1 - 0.0001)
                y_value.append(value[1])
                y_value.append(value[1])
                temp += 1
                
            
            self.Plot_import(x_value, y_value)
            self.ui.lineEdit_condition_keithley.setText("File is imported correctly.")
                
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Data File Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import.draw()
        
    def Reset_plot_import(self):
        self.ui.mplwidget_import.figure.clear()
        self.axes_import = self.ui.mplwidget_import.figure.add_subplot(111)
    
    def Refresh_visa(self):
        self.rm = visa.ResourceManager()
        try:
            all_visas = self.rm.list_resources()
            print all_visas
        except:
            all_visas = "No Visa Available."
        self.ui.comboBox_visa_keithley.clear()
        for item in all_visas:
            self.ui.comboBox_visa_keithley.addItem(item)
    
    # Tab: Keithley
    # Group: Visa
    # Select the visa address of the Keithley
    def Select_keithley(self):
        self.visa_address = str(self.ui.comboBox_visa_keithley.currentText())
        self.rm = visa.ResourceManager()
        self.rm.list_resources()
        inst = self.rm.open_resource(self.visa_address)
        self.visa_check = self.Check_visa(inst)
        if self.visa_check == True:
            self.ui.lineEdit_condition_keithley.setText("Visa is selected succefully!")
            self.visa_name = inst.query("*IDN?")
            self.ui.lineEdit_visa_keithley.setText(self.visa_name)
            self.visa_chosen = inst
            self.ui.groupBox_scan_keithley.setEnabled(True)
        elif self.visa_check == False:
            self.ui.lineEdit_condition_keithley.setText("Invalid visa address.")
            self.ui.lineEdit_visa_keithley.setText("None.")
            self.visa_chosen = False

    def Check_visa(self, inst):
        try:
            inst.ask("*IDN?")
            valid = True
        except:
            valid = False
        return valid
    
    # Tab: Keithley
    # Group: Visa
    # Close the visa address you choose
    def Close_keithley(self):
        self.visa_chosen.close()
        self.ui.lineEdit_condition_keithley.setText('Visa address is closed')
        self.ui.lineEdit_visa_keithley.setText('')
        self.ui.groupBox_scan_keithley.setEnabled(False)
    
    # Tab: Keithley
    # Group: Scan
    # Start to scan by the keithley
    def Scan_keithley(self):
        pass
 
    # Tab: Keithley
    # Group: Scan   
    # Stop the scan
    def Stop_keithley(self):
        pass
    
    # Tab: Keithley
    # Group: Scan
    # Clear the scan result and ready to start again
    def Clear_keithley(self):
        pass

    # Make sure the user is going to quit the program
    def closeEvent(self, event):
        quit_msg = "DO you want to quit the program?"
        reply = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            question.accept()
        else:
            question.ignore()
    
if __name__ == "__main__":
    # To open the GUI
    app = QApplication(sys.argv)
    myapp = MyForm()
    
    # It shows the GUI
    myapp.show()
    
    # Exit the GUI when "x" button is clicked
    sys.exit(app.exec_()) 
        