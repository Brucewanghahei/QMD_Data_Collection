# Import numpy library
import numpy as np
import os
import sys
import datetime
import visa
import math
import time
import warnings

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Save import Save_Thread
from D_save import Dynamic_Save_Thread

# These are the modules required for the guiqwt widgets.
# Import plot widget base class
from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

import subprocess

class Keithley():
    
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.collect_data_thread = Collect_data()
        self.save_thread = Save_Thread()
        self.dsave_thread = Dynamic_Save_Thread()
        
        main.connect(self.ui.pushButton_browse_keithley, SIGNAL('clicked()'), self.Browse_keithley)
        main.connect(self.ui.pushButton_import_keithley, SIGNAL('clicked()'), self.Import_keithley)
        main.connect(self.ui.pushButton_close_keithley, SIGNAL('clicked()'), self.Close_keithley)
        main.connect(self.ui.pushButton_select_keithley, SIGNAL('clicked()'), self.Select_keithley)
        main.connect(self.ui.pushButton_update_keithley, SIGNAL('clicked()'), self.Refresh_visa)
        main.connect(self.ui.pushButton_scan_keithley, SIGNAL('clicked()'), self.Scan_keithley)
        main.connect(self.ui.pushButton_pause_keithley, SIGNAL('clicked()'), self.collect_data_thread.pause)       
        main.connect(self.ui.pushButton_stop_keithley, SIGNAL('clicked()'), self.collect_data_thread.stop)
        main.connect(self.ui.pushButton_copy_keithley, SIGNAL('clicked()'), self.Copy_keithley)
        main.connect(self.ui.pushButton_fit_keithley, SIGNAL('clicked()'), self.collect_data_thread.Fit)
        main.connect(self.ui.pushButton_browse_save_G_keithley, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButton_browse_save_O_keithley, SIGNAL('clicked()'), self.Other_browse)
        main.connect(self.ui.pushButton_check_G_keithley, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButton_Select_Directory_G_keithley, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.pushButton_Save_G_keithley, SIGNAL('clicked()'), self.G_save)
        main.connect(self.ui.pushButton_Open_G_keithley, SIGNAL('clicked()'), self.G_open)
        main.connect(self.ui.pushButton_Save_O_keithley, SIGNAL('clicked()'), self.O_save)
        main.connect(self.ui.pushButton_Open_O_keithley, SIGNAL('clicked()'), self.O_open)
        main.connect(self.ui.radioButton_timescan_keithley, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
        main.connect(self.ui.radioButton_stepscan_keithley, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
        main.connect(self.ui.checkBoxK1_dsave, SIGNAL("clicked()"), self.Pre_dsave)
        main.connect(self.ui.pushButtonK1_dsave_browse, SIGNAL('clicked()'), self.Dsave_browse)
        main.connect(self.collect_data_thread, SIGNAL("print"), self.Print_data)
        main.connect(self.collect_data_thread, SIGNAL("mpl_plot"), self.Plot_analysis)
        main.connect(self.collect_data_thread, SIGNAL("data_available"), self.Pre_save)
        # self.connect(self.Keithley_programs.collect_data_thread, SIGNAL("clear_plot"), self.Keithley_programs.Clear_plot)
        
        self.Array = []
        self.count = 0
        self.go_on = True
        self.dsave_directory = ''
        
        self.canvas_import = FigureCanvas(self.ui.mplwidget_import.figure)
        self.canvas_import.setParent(self.ui.widget_import)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_import = NavigationToolbar(self.canvas_import, self.ui.widget_import)
        
        self.canvas_analysis = FigureCanvas(self.ui.mplwidget_analysis.figure)
        self.canvas_analysis.setParent(self.ui.widget_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_analysis = NavigationToolbar(self.canvas_analysis, self.ui.widget_analysis)
        
        self.canvas_ct_analysis = FigureCanvas(self.ui.mplwidget_ct_analysis.figure)
        self.canvas_ct_analysis.setParent(self.ui.widget_ct_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_ct_analysis = NavigationToolbar(self.canvas_ct_analysis, self.ui.widget_ct_analysis)
        
        self.canvas_vt_analysis = FigureCanvas(self.ui.mplwidget_vt_analysis.figure)
        self.canvas_vt_analysis.setParent(self.ui.widget_vt_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_vt_analysis = NavigationToolbar(self.canvas_vt_analysis, self.ui.widget_vt_analysis)
        
                # Create the QVBoxLayout object and add the widget into the Layout
        vbox_import = QVBoxLayout()
        # The matplotlib canvas
        vbox_import.addWidget(self.canvas_import)
        # The matplotlib toolbar
        vbox_import.addWidget(self.mpl_toolbar_import)
        self.ui.widget_import.setLayout(vbox_import)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_analysis.addWidget(self.canvas_analysis)
        # The matplotlib toolbar
        vbox_analysis.addWidget(self.mpl_toolbar_analysis)
        self.ui.widget_analysis.setLayout(vbox_analysis)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_ct_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_ct_analysis.addWidget(self.canvas_ct_analysis)
        # The matplotlib toolbar
        vbox_ct_analysis.addWidget(self.mpl_toolbar_ct_analysis)
        self.ui.widget_ct_analysis.setLayout(vbox_ct_analysis)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_vt_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_vt_analysis.addWidget(self.canvas_vt_analysis)
        # The matplotlib toolbar
        vbox_vt_analysis.addWidget(self.mpl_toolbar_vt_analysis)
        self.ui.widget_vt_analysis.setLayout(vbox_vt_analysis)
        
        self.ui.mplwidget_import = self.canvas_import
        self.ui.mplwidget_analysis = self.canvas_analysis
        self.ui.mplwidget_ct_analysis = self.canvas_ct_analysis
        self.ui.mplwidget_vt_analysis = self.canvas_vt_analysis
        
        # Set up guiqwt plot
        self.curve_item = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidget_keithley.plot.add_item(self.curve_item)
        self.ui.curvewidget_keithley.plot.set_antialiasing(True)
        self.ui.curvewidget_keithley.plot.set_titles("Measurement and Plot Based on Array", "X-Axis", "Y-Axis")
        
        self.curve_ct_item = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidget_ct_keithley.plot.add_item(self.curve_ct_item)
        self.ui.curvewidget_ct_keithley.plot.set_antialiasing(True)
        self.ui.curvewidget_ct_keithley.plot.set_titles("Current vs Time", "Time", "Current")

        self.curve_vt_item = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidget_vt_keithley.plot.add_item(self.curve_vt_item)
        self.ui.curvewidget_vt_keithley.plot.set_antialiasing(True)
        self.ui.curvewidget_vt_keithley.plot.set_titles("Voltage vs Time", "Time", "Voltage")
        
        
        
    # Tab: Keithley
    # Group: Import
    # Search and find the directory of the file you want to import
    def Browse_keithley(self):
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getOpenFileName(None, 'Select File to Import', prev_dir, filter="Array Files (*.array)")
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
            self.ui.labelK1_condition.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
            
        else:
            self.ui.labelK1_condition.setText("Please choose valid file to import.")
    
    # Tab: Keithley
    # Group: Import
    # Import the file ends in ".array"
    def Import_keithley(self):
        divider_found = True
        count = 0
        temp = 0
        self.Array = []
        x_value = []
        y_value = []
        
        fileDir = self.ui.lineEdit_directory_keithley.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.labelK1_condition.setText("Data not found in file. Please check it.")
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
                print 'line: ' + line
                if line == '':
                    break
                value = line.split(',')
                x_value.append(temp)
                x_value.append(temp + 1)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array.append(float(value[1]))
                temp += 1
                
            self.Plot_import(x_value, y_value)
            self.ui.labelK1_condition.setText("File is imported correctly.")
            self.ui.groupBox_visa_keithley.setEnabled(True)
            
    def Copy_keithley(self):
        Values = self.copyDataFunc()
        if Values != None:
            self.ui.labelK1_condition.setText('Array has been copied and plotted.')
            self.ui.tabWidget_plot_keithely.setCurrentIndex(0)
            self.Array = []
            x_value = []
            y_value = []
            item = 0
            for i in range(0, len(Values)):
                for j in range(0, len(Values[i])):
                    x_value.append(item)
                    x_value.append(item + 1 - 0.0001)
                    y_value.append(Values[i][j])
                    y_value.append(Values[i][j])
                    self.Array.append(Values[i][j])
                    item += 1
            self.Plot_import(x_value, y_value)
            self.ui.lineEdit_directory_keithley.setText('From Array Builder Tab.')
            self.ui.groupBox_visa_keithley.setEnabled(True)
        else:
            self.ui.labelK1_condition.setText('No valid array to copy.')
        
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import.draw()
    
    def Plot_analysis(self):
        self.ui.tabWidget_plot_keithely.setCurrentIndex(3)
        self.ui.mplwidget_analysis.draw()
        self.ui.mplwidget_ct_analysis.draw()
        self.ui.mplwidget_vt_analysis.draw()
        
    def Print_data(self, item, voltage, current, time):
        self.ui.labelK1_step.setText(str(item))
        data = self.Twist_scale(voltage)
        self.ui.labelK1_1.setText(format(data[0], '.3f'))
        self.ui.labelK1_1unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(current)
        self.ui.labelK1_2.setText(format(data[0], '.3f'))
        self.ui.labelK1_2unit.setText(data[1] + 'Curr')
        self.ui.labelK1_time.setText(format(time, '.3f'))
        self.ui.curvewidget_keithley.plot.do_autoscale()
        self.ui.curvewidget_ct_keithley.plot.do_autoscale()
        self.ui.curvewidget_vt_keithley.plot.do_autoscale()
        self.curve_item.plot().replot()
        self.curve_ct_item.plot().replot()
        self.curve_vt_item.plot().replot()
    
    def Twist_scale(self, num):
        temp = abs(num)
        if temp >= 1E9:
            scale = [1E-9, "G"]
        elif temp >= 1E6 and temp < 1E9:
            scale = [1E-6, "M"]
        elif temp >= 1E3 and temp < 1E6:
            scale = [1E-3, "k"]
        elif temp >= 1 and temp < 1000:
            scale = [1, ""]
        elif temp >= 1E-3 and temp < 1:
            scale = [1E3, "m"]
        elif temp >= 1E-6 and temp < 1E-3:
            scale = [1E6, "u"]
        elif temp >= 1E-9 and temp < 1E-6:
            scale = [1E9, "n"]
        elif temp < 1E-9:
            scale = [1E12, "p"]
            
        return [num * scale[0], scale[1]]
    
    def Clear_plot(self):
        self.ui.mplwidget_analysis.draw()
        self.ui.mplwidget_ct_analysis.draw()
        self.ui.mplwidget_vt_analysis.draw()
        self.curve_item.plot().replot()
        self.curve_ct_item.plot().replot()
        self.curve_vt_item.plot().replot()
    
    # Reset the import matplot widget
    def Reset_plot_import(self):
        self.ui.mplwidget_import.figure.clear()
        self.axes_import = self.ui.mplwidget_import.figure.add_subplot(111)
    
    def Refresh_visa(self):
        self.rm = visa.ResourceManager()
        try:
            all_visas = self.rm.list_resources()
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
            self.ui.labelK1_condition.setText("Visa is selected succefully!")
            self.visa_name = inst.query("*IDN?")
            self.ui.labelK1_visaname.setText(self.visa_name)
            self.visa_chosen = inst
            self.ui.groupBoxK1_dsave.setEnabled(True)
            self.ui.checkBoxK1_dsave.setEnabled(True)
            self.ui.groupBox_scan_keithley.setEnabled(True)
            self.ui.radioButton_stepscan_keithley.setEnabled(True)
            self.ui.groupBox_voltage_keithley.setEnabled(True)
            self.ui.groupBox_output_keithley.setEnabled(True)
            self.ui.groupBox_current_keithley.setEnabled(True)
            self.ui.groupBox_time_keithley.setEnabled(True)
            self.ui.pushButton_select_keithley.setEnabled(False)
            self.ui.radioButton_timescan_keithley.setEnabled(True)
        elif self.visa_check == False:
            self.ui.labelK1_condition.setText("Invalid visa address.")
            self.ui.labelK1_visaname.setText("None.")
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
        self.ui.labelK1_condition.setText('Visa address is closed')
        self.ui.labelK1_visaname.setText('')
        self.ui.groupBox_scan_keithley.setEnabled(False)
        self.ui.pushButton_select_keithley.setEnabled(True)
        self.ui.pushButton_close_keithley.setEnabled(False)
            
    # Tab: Keithley
    # Group: Scan
    # Start to scan by the keithley
    def Scan_keithley(self):
        c_limit = 0
        self.dsave_filename = ''
        self.dsave_username = ''
        self.dsave_filetype = ''
        self.dsave_divide = ''
        try:
            if self.ui.lineEdit_climit_keithley.text() != '':
                c_limit = float(self.ui.lineEdit_climit_keithley.text())
            if self.ui.checkBoxK1_dsave.isChecked():
                self.Dsave_directory()
                if self.dsave_dir_ok:
                    self.Dsave_filename()
                    if self.dsave_filename_ok:    
                        self.Dsave_username()
                        if self.dsave_username_ok:
                            self.Dsave_filetype()
                            self.collect_data_thread.input(self.visa_chosen, self.ui, self.Array, self.go_on, self.curve_item, self.curve_ct_item, self.curve_vt_item, c_limit, self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide)
                            self.ui.pushButton_pause_keithley.setEnabled(True)
                            self.ui.pushButton_stop_keithley.setEnabled(True)
                            self.ui.pushButton_scan_keithley.setEnabled(False)
                            self.ui.groupBoxK1_parameters.setEnabled(True)
                        else:
                            self.ui.labelK1_condition.setText('Enter user name for dynamic saving.')
                    else:
                        self.ui.labelK1_condition.setText('Enter file name for dynamic saving.')
                else:
                    self.ui.labelK1_condition.setText('Choose valid directory for dynamic saving.')
            else:
                self.collect_data_thread.input(self.visa_chosen, self.ui, self.Array, self.go_on, self.curve_item, self.curve_ct_item, self.curve_vt_item, c_limit, self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide)
                self.ui.pushButton_pause_keithley.setEnabled(True)
                self.ui.pushButton_stop_keithley.setEnabled(True)
                self.ui.pushButton_scan_keithley.setEnabled(False)
                self.ui.groupBoxK1_parameters.setEnabled(True)
        except ValueError:
            self.ui.labelK1_condition.setText("Invalid current limit.")
      
    def Pre_dsave(self):
        if self.ui.checkBoxK1_dsave.isChecked():
            self.ui.labelK1_dsave_directory.setEnabled(True)
            self.ui.lineEditK1_dsave_directory.setEnabled(True)
            self.ui.pushButtonK1_dsave_browse.setEnabled(True)
            self.ui.groupBoxK1_dsave_filename.setEnabled(True)
            self.ui.radioButtonK1_dsave_timename.setEnabled(True)
            self.ui.radioButtonK1_dsave_custname.setEnabled(True)
            self.ui.lineEditK1_dsave_custname.setEnabled(True)
            self.ui.groupBoxK1_dsave_filetype.setEnabled(True)
            self.ui.radioButtonK1_csv.setEnabled(True)
            self.ui.radioButtonK1_txt.setEnabled(True)
            self.ui.labelK1_dsave_username.setEnabled(True)
            self.ui.lineEditK1_dsave_username.setEnabled(True)
            self.ui.labelK1_dsave_comment.setEnabled(True)
            self.ui.textEditK1_dsave_comment.setEnabled(True)
            self.ui.labelK1_condition.setText("Dynamic saving opened.")
        else:
            self.ui.labelK1_dsave_directory.setEnabled(False)
            self.ui.lineEditK1_dsave_directory.setEnabled(False)
            self.ui.pushButtonK1_dsave_browse.setEnabled(False)
            self.ui.groupBoxK1_dsave_filename.setEnabled(False)
            self.ui.radioButtonK1_dsave_timename.setEnabled(False)
            self.ui.radioButtonK1_dsave_custname.setEnabled(False)
            self.ui.lineEditK1_dsave_custname.setEnabled(False)
            self.ui.groupBoxK1_dsave_filetype.setEnabled(False)
            self.ui.radioButtonK1_csv.setEnabled(False)
            self.ui.radioButtonK1_txt.setEnabled(False)
            self.ui.labelK1_dsave_username.setEnabled(False)
            self.ui.lineEditK1_dsave_username.setEnabled(False)
            self.ui.labelK1_dsave_comment.setEnabled(False)
            self.ui.textEditK1_dsave_comment.setEnabled(False)
            self.ui.labelK1_condition.setText("Dynamic saving closed.")
    
    def Dsave_browse(self):
        self.dsave_directory = ''
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getExistingDirectory(None, 'Select Folder to Save', prev_dir)
        if fileDir != '':
            open_dir = ''
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            print fileDir
            self.dsave_directory = fileDir
            self.ui.lineEditK1_dsave_directory.setText(fileDir)
            self.ui.labelK1_condition.setText("Dynamic saving directory selected.")
        else:
            self.ui.lineEditK1_dsave_directory.setText('None')
            self.ui.labelK1_condition.setText('Choose a directory for dynamic saving.')
    
    def Dsave_directory(self):
        self.dsave_dir_ok = True
        if self.ui.lineEditK1_dsave_directory.text() == '' or self.ui.lineEditK1_dsave_directory.text() == 'None':
            self.dsave_dir_ok = False
        
    def Dsave_filename(self):
        self.dsave_filename_ok = True
        self.dsave_filename = ''
        if self.ui.radioButtonK1_dsave_timename.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = 'DSave' + ' ' + date + ' ' + current_time
            self.dsave_filename = str(date_and_time)
        elif self.ui.radioButtonK1_dsave_custname.isChecked():
            self.dsave_filename = str(self.ui.lineEditK1_dsave_custname.text())
            if self.dsave_filename == '':
                self.dsave_filename_ok = False
    
    def Dsave_filetype(self):
        if self.ui.radioButtonK1_csv.isChecked():
            self.dsave_filetype = '.csv'
            self.dsave_divide = ','
        elif self.ui.radioButtonK1_txt.isChecked():
            self.dsave_filetype = '.txt'
            self.dsave_divide = '\t'
            
    def Dsave_username(self):
        self.dsave_username_ok = True
        self.dsave_username = ''
        self.dsave_username = str(self.ui.lineEditK1_dsave_username.text())
        if self.dsave_username == '':
            self.dsave_username_ok = False
        
    def Google_browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select Google Drive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            # for i in range(0, len(file_list) - 1):
            #     if i < len(file_list) - 1:
            #         open_dir += file_list[i] + '\\'
            #     elif i == len(file_list) - 1:
            #         open_dir += file_list[i]
            file_dir.replace('/', '\\')
            self.ui.lineEdit_GoogleDrive_G_keithley.setText(file_dir)
            self.ui.label_condition_G_keithley.setText('Open Google Drive User Folder')
            self.ui.pushButton_check_G_keithley.setEnabled(True)
    
    def Other_browse(self):
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getExistingDirectory(None, 'Select Folder to Save', prev_dir)
        if fileDir != '':
            open_dir = ''
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            self.O_directory = fileDir
            self.ui.lineEdit_directory_O_keithley.setText(fileDir)
            self.ui.label_username_O_keithley.setEnabled(True)
            self.ui.comboBox_Name_Folder_O_keithley.setEnabled(True)
            self.ui.groupBox_Filename_O_keithley.setEnabled(True)
            self.ui.groupBox_File_Type_O_keithley.setEnabled(True)
            self.ui.label_comment_O_keithley.setEnabled(True)
            self.ui.textEdit_comment_O_keithley.setEnabled(True)
            self.ui.pushButton_Save_O_keithley.setEnabled(True)
            self.ui.lineEdit_Custom_Name_O_keithley.setEnabled(True)
            self.ui.label_condition_O_keithley.setText("Click save button to save.")
        else:
            self.ui.lineEdit_directory_O_keithley.setText('None')
            self.ui.label_condition_O_keithley.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEdit_GoogleDrive_G_keithley.text()).split('\\')
        if os.path.exists(self.ui.lineEdit_GoogleDrive_G_keithley.text()) == False:
            self.ui.label_condition_G_keithley.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.label_condition_G_keithley.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.label_namefolder_G_keithley.setEnabled(True)
                    self.ui.comboBox_Name_Folder_G_keithley.setEnabled(True)
                    self.ui.pushButton_Select_Directory_G_keithley.setEnabled(True)
                    self.ui.label_condition_G_keithley.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBox_Name_Folder_G_keithley.currentText())
        if namefolder == 'None':
            self.ui.label_condition_G_keithley.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.label_G_keithley.setText("Save to \\" + namefolder + "\Date" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Keithely with Array'
            self.ui.groupBox_File_Type_G_keithley.setEnabled(True)
            self.ui.groupBox_Filename_G_keithley.setEnabled(True)
            self.ui.label_comment_G_keithley.setEnabled(True)
            self.ui.textEdit_comment_G_keithley.setEnabled(True)
            self.ui.pushButton_Save_G_keithley.setEnabled(True)
            self.ui.lineEdit_Custom_Name_G_keithley.setEnabled(True)
            self.ui.label_condition_G_keithley.setText('Click save button to save.')
            
    def Select_type_G_keithley(self):
        if self.ui.radioButton_csv_G_keithley.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButton_txt_G_keithley.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

            
    def Select_type_O_keithley(self):
        if self.ui.radioButton_csv_O_keithley.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButton_txt_O_keithley.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'


    def Select_name_G_keithley(self):
        if self.ui.radioButton_Timename_G_keithley.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_G_keithley.isChecked():
            self.G_file_name = str(self.ui.lineEdit_Custom_Name_G_keithley.text())
            
    def Select_name_O_keithley(self):
        if self.ui.radioButton_Timename_O_keithley.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_O_keithley.isChecked():
            self.O_file_name = str(self.ui.lineEdit_Custom_Name_O_keithley.text())
            
    def Pre_save(self, date_value, t_value, x_value, y_value, array):
        self.date_value = date_value
        self.t_value = t_value
        self.x_value = x_value
        self.y_value = y_value
        self.array = array
    
    def G_save(self):
        if self.ui.radioButton_Custom_Name_G_keithley.isChecked() and self.ui.lineEdit_Custom_Name_G_keithley.text() == '':
            self.ui.label_condition_G_keithley.setText('Enter a valid file name.')
        else:
            self.Select_type_G_keithley()
            self.Select_name_G_keithley()
            
            # It contains the measurement information, including user name, date, measurement type, time step etc.
            # This is a two dimensional list. Each sub list related to a single line.
            comments = []
            # For QMDlab data file it is "Collected Data"
            divider = 'Collected Data'
            # Parameters' names, such as VOLTAGE, CURRENT, TIME
            parameters = []
            # Parameters' units
            units = []
            # Include all the data
            data = []
            # Contains file type, divider, name and directory
            file_info = []
            
            # First line user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_G_keithley.currentText()))
            comments.append(temp)
            # Second line edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Third line array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_keithley.text()))
            comments.append(temp)
            # Fourth line visa address
            temp = []
            temp.append('Visa Address:')
            temp.append(str(self.ui.comboBox_visa_keithley.currentText()))
            comments.append(temp)
            # Fifth line visa name
            temp = []
            temp.append('Visa Name:')
            visa_name = self.visa_name.rstrip('\n')
            visa_name = visa_name.replace(',', ' ')
            temp.append(str(visa_name))
            comments.append(temp)
            # Sixth line scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Voltage')
            comments.append(temp)
            # Seventh line time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEdit_tstep_keithley.text()))
            comments.append(temp)
            # Eighth line comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_G_keithley.toPlainText()))
            comments.append(temp)
            
            # Do parameters, units and data together
            parameters.append('Date')
            units.append('String')
            data.append(self.date_value)
            
            parameters.append('Time')
            units.append('s')
            data.append(self.t_value)
            
            parameters.append('Step')
            units.append('1')
            temp = []
            for i in range(0, len(self.array)):
                temp.append(i)
            data.append(temp)
            
            parameters.append('Array')
            units.append('1')
            data.append(self.array)
            parameters.append('Voltage')
            units.append('Volts')
            data.append(self.x_value)
            parameters.append('Current')
            units.append('Amps')
            data.append(self.y_value)
            
            # File_info
            # First is file name
            file_info.append(self.G_file_name)
            # csv or txt file
            file_info.append(self.G_type)
            # the divide of csv is "," while for txt its "\t"
            file_info.append(self.G_divide)
            # Always "Collected Data"
            file_info.append(divider)
            # The saving directory
            file_info.append(self.G_directory)
            
            self.save_thread.input(comments, parameters, units, data, file_info)
            self.ui.pushButton_Open_G_keithley.setEnabled(True)
            self.ui.label_condition_G_keithley.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBox_Name_Folder_O_keithley.currentText() == 'None':
            self.ui.label_condition_O_keithley.setText('Pleanse choose a user name.')
        elif self.ui.radioButton_Custom_Name_O_keithley.isChecked() and self.ui.lineEdit_Custom_Name_O_keithley.text() == '':
            self.ui.label_condition_O_keithley.setText('Please enter a file name.')
        else:
            self.Select_type_O_keithley()
            self.Select_name_O_keithley()
            
            # It contains the measurement information, including user name, date, measurement type, time step etc.
            # This is a two dimensional list. Each sub list related to a single line.
            comments = []
            # For QMDlab data file it is "Collected Data"
            divider = 'Collected Data'
            # Parameters' names, such as VOLTAGE, CURRENT, TIME
            parameters = []
            # Parameters' units
            units = []
            # Include all the data
            data = []
            # Contains file type, divider, name and directory
            file_info = []
            
            # First line user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_O_keithley.currentText()))
            comments.append(temp)
            # Second line edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Third line array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_keithley.text()))
            comments.append(temp)
            # Fourth line visa address
            temp = []
            temp.append('Visa Address:')
            temp.append(str(self.ui.comboBox_visa_keithley.currentText()))
            comments.append(temp)
            # Fifth line visa name
            temp = []
            temp.append('Visa Name:')
            visa_name = self.visa_name.rstrip('\n')
            visa_name = visa_name.replace(',', ' ')
            temp.append(str(visa_name))
            comments.append(temp)
            # Sixth line scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Voltage')
            comments.append(temp)
            # Seventh line time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEdit_tstep_keithley.text()))
            comments.append(temp)
            # Eighth line comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_O_keithley.toPlainText()))
            comments.append(temp)
            
            # Do parameters, units and data together
            parameters.append('Date')
            units.append('String')
            data.append(self.date_value)
            parameters.append('Time')
            units.append('s')
            data.append(self.t_value)
            parameters.append('Step')
            units.append('1')
            temp = []
            for i in range(0, len(self.array)):
                temp.append(i)
            data.append(temp)
            parameters.append('Array')
            units.append('1')
            data.append(self.array)
            parameters.append('Voltage')
            units.append('Volts')
            data.append(self.x_value)
            parameters.append('Current')
            units.append('Amps')
            data.append(self.y_value)
            
            # File_info
            # First is file name
            file_info.append(self.O_file_name)
            # csv or txt file
            file_info.append(self.O_type)
            # the divide of csv is "," while for txt its "\t"
            file_info.append(self.O_divide)
            # Always "Collected Data"
            file_info.append(divider)
            # The saving directory
            file_info.append(self.O_directory)
            
            self.save_thread.input(comments, parameters, units, data, file_info)
            self.ui.pushButton_Open_O_keithley.setEnabled(True)
            self.ui.label_condition_O_keithley.setText('File has been saved.')
    
    def G_open(self):
        opendir = self.G_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
    def O_open(self):
        opendir = self.O_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
    
class Collect_data(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def input(self, inst, ui, Array, go_on, curve, curve_ct, curve_vt, c_limit, dsave_directory, dsave_filename, dsave_username, dsave_thread, dsave_filetype, dsave_divide):
        self.inst = inst
        self.ui = ui
        self.Array = np.array(Array)
        self.go_on = go_on
        self.curve = curve
        self.curve_ct = curve_ct
        self.curve_vt = curve_vt
        self.c_limit = c_limit
        self.dsave_directory = dsave_directory
        self.dsave_filename = dsave_filename
        self.dsave_username = dsave_username
        self.dsave_thread = dsave_thread
        self.dsave_filetype = dsave_filetype
        self.dsave_divide = dsave_divide
        self.time_step = float(self.ui.lineEdit_tstep_keithley.text())
        self.voltage_scale = [1, 'Volts']
        self.current_scale = [1, 'Amps']
        self.start()
        
    def pause(self):
        if self.go_on:
            self.ui.pushButton_pause_keithley.setText('Continue')
            self.go_on = False
        else:
            self.ui.pushButton_pause_keithley.setText('Pause')
            self.go_on = True
    
    def stop(self):
        self.go_on = True
        self.pause = True
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        
    def run(self):
        # Collecte raw x values
        x_value = []
        # Collect raw y values
        y_value = []
        # Collect time in seconds
        t_value = []
        # Collect steps
        self.s_value = []
        # Collect date and time information
        date_value = []
        self.x_plot = np.array([])
        self.y_plot = np.array([])
        self.t_plot = np.array([])
        item = 0
        self.current_scale = [1, "Amps"]
        self.voltage_scale = [1, 'Volts']
        self.time_scale = [1, "Sec"]
        self.np_Array = []
        self.date_and_time = ''
        self.voltage = ''
        self.current = ''
        self.pause = False
        
        self.turn_on_voltage()
        self.ui.tabWidget_plot_keithely.setCurrentIndex(2)
        
        if self.ui.radioButton_voltage_keithley.isChecked():
            if self.ui.radioButton_mv_keithley.isChecked():
                self.voltage_scale = [1E-3, 'mVolts']
            elif self.ui.radioButton_uv_keithley.isChecked():
                self.voltage_scale = [1E-6, 'mVolts']
            elif self.ui.radioButton_v_keithley.isChecked():
                self.voltage_scale = [1, 'Volts']
            self.np_Array = self.Array * float(self.voltage_scale[0])
            t1_ = 0
             
            self.inst.query('READ? "defbuffer2", SOUR')
            start_time = time.time()
            
            while True:
                if float(time.time() - t1_) > self.time_step:
                    #self.ui.lineEdit_tstep_keithley.setText(str(round(time.time() - t1_, 2)))
                    t1_ = time.time()
                    if self.go_on:
                            
                        if self.pause:
                            self.MPL_Plot()
                            
                            self.ui.labelK1_condition.setText('Reading paused.')
                            
                            self.ui.tabWidget_save_keithley.setEnabled(True)
                            self.ui.pushButton_stop_keithley.setEnabled(False)
                            # Send all the data back to the keithley class
                            self.emit(SIGNAL("data_available"), date_value, t_value, x_value, y_value, self.Array)
                            self.emit(SIGNAL("fit_available"), self.x_plot, self.y_plot, self.t_plot, self.s_value)
                            self.Pre_dynamic_save(item, True)
                            break
                        if item == len(self.np_Array):
                            self.MPL_Plot()
                            
                            self.ui.pushButton_scan_keithley.setEnabled(True)
                            self.ui.pushButton_pause_keithley.setEnabled(False)
                            self.ui.pushButton_stop_keithley.setEnabled(False)
                            self.ui.labelK1_condition.setText('Scan complete.')
                            self.ui.tabWidget_save_keithley.setEnabled(True)
                            # Send all the data back to the keithley class
                            self.emit(SIGNAL("data_available"), date_value, t_value, x_value, y_value, self.Array)
                            self.Pre_dynamic_save(item, True)
                            break
                        
                        self.set_voltage(self.np_Array[item])
                        self.read_data_write()
                        self.data = self.read_data_read()
                        #end_time = time.time()
                        x_value.append(float(self.data[0]))
                        self.x_plot = np.array(x_value)
                        self.x_plot = self.x_plot / self.voltage_scale[0]
                        y_value.append(float(self.data[1]))
                        self.y_plot = np.array(y_value)
                        self.s_value.append(item)
                        #end_time = time.time()
                        if abs(max(self.y_plot)) >= 1:
                            self.current_scale = [1, "Amps"]
                        elif abs(max(self.y_plot)) >= 1E-3 and abs(max(self.y_plot)) < 1:
                            self.current_scale = [1E-3, "mAmps"]
                        elif abs(max(self.y_plot)) >= 1E-6 and abs(max(self.y_plot)) < 1E-3:
                            self.current_scale = [1E-6, "uAmps"]
                        elif abs(max(self.y_plot)) >= 1E-9 and abs(max(self.y_plot)) < 1E-6:
                            self.current_scale = [1E-9, "nAmps"]
                        elif abs(max(self.y_plot)) >= 1E-12 and abs(max(self.y_plot)) < 1E-9:
                            self.current_scale = [1E-12, "pAmps"]
                        self.ui.curvewidget_keithley.plot.set_titles("Keithely Voltage Source Measurement", "Voltage (" + self.voltage_scale[1] + ")", "Current (" + self.current_scale[1] + ")")
                        self.y_plot = self.y_plot / self.current_scale[0]
                        self.curve.set_data(self.x_plot, self.y_plot)
                        self.ui.labelK1_condition.setText('Reading...')
                        #time.sleep(self.time_step)
                        
                        end_time = time.time()
                        self.during = end_time - start_time
                        t_value.append(self.during)
                        self.t_plot = t_value
                        
                        if self.ui.radioButton_timescan_keithley.isChecked():
                            self.ui.curvewidget_ct_keithley.plot.set_titles("Keithely Voltage Source Current vs Time", "Time (" + self.time_scale[1] + ")", "Current (" + self.current_scale[1] + ")")
                            self.curve_ct.set_data(self.t_plot, self.y_plot)
                            self.ui.curvewidget_vt_keithley.plot.set_titles("Keithely Voltage Source Voltage vs Time", "Time (" + self.time_scale[1] + ")", "Voltage (" + self.voltage_scale[1] + ")")
                            self.curve_vt.set_data(self.t_plot, self.x_plot)
                        elif self.ui.radioButton_stepscan_keithley.isChecked():
                            self.ui.curvewidget_ct_keithley.plot.set_titles("Keithely Voltage Source Current vs Step", "Step (1)", "Current (" + self.current_scale[1] + ")")
                            self.curve_ct.set_data(self.s_value, self.y_plot)
                            self.ui.curvewidget_vt_keithley.plot.set_titles("Keithely Voltage Source Voltage vs Time", "Step (1)", "Voltage (" + self.voltage_scale[1] + ")")
                            self.curve_vt.set_data(self.s_value, self.x_plot)
                        self.emit(SIGNAL("print"), item, float(self.data[0]), float(self.data[1]), self.during)
                        
                        now = datetime.datetime.now()
                        date = '%s-%s-%s' % (now.year, now.month, now.day)
                        current_time = '%s:%s:%s' % (now.hour, now.minute, now.second)
                        self.date_and_time = date + ' ' + current_time
                        date_value.append(self.date_and_time)
                        self.Pre_dynamic_save(item, False)
                        item += 1
    
                    else:
                        self.ui.labelK1_condition.setText('Reading stoped.')
            self.turn_off_voltage()
    
    def set_voltage(self, voltage):
        self.inst.write('TRACE:CLEar "defbuffer1"')
        # Select the front-panel terminals for the measurement
        self.inst.write('ROUT:TERM FRONT')
        # Set the instrument to measure the current
        self.inst.write('SENS:FUNC "CURR"')
        # Set the voltage limitation
        if self.c_limit != 0:
            self.inst.write("SOUR:VOLT:ILIM " + str(self.c_limit))
        # Set the voltage range to be auto
        self.inst.write('SOUR:VOLT:RANG:AUTO ON')
        # Set to source voltage
        self.inst.write('SOUR:FUNC VOLT')
        # Turn on the source read back
        self.inst.write('SOUR:VOLT:READ:BACK 1')
        # Input the individual voltage to start the measurement
        self.inst.write("SOUR:VOLT " + str(voltage))
    
    def turn_on_voltage(self):
        #ON = 4 Contact   OFF = 2 Contact
        if self.ui.radioButton_Lead4_keithley.isChecked():
            self.inst.write('SENS:CURR:RSEN ' + 'ON')
        elif self.ui.radioButton_Lead2_keithley.isChecked():
            self.inst.write('SENS:CURR:RSEN ' + 'OFF')
        self.inst.write('OUTP ON')
    
    def turn_off_voltage(self):
        if not self.ui.checkBoxK1_Output_on.isChecked():
            self.inst.write("OUTP OFF")
    
    def read_data_write(self):
        self.inst.write('READ? "defbuffer1", SOUR, READ')
        
    def read_data_read(self):
        voltage, current = self.inst.read().replace("\n", "").split(",")
        return [voltage, current]
    
    def Pre_dynamic_save(self, num, is_last):
        if self.ui.checkBoxK1_dsave.isChecked():
            is_first = False
            comments = []
            parameters = []
            units = []
            data = []
            file_info = []
            
            # File_info
            # First is file name
            file_info.append(self.dsave_filename)
            # csv file
            file_info.append(self.dsave_filetype)
            # the divide of csv is ","
            file_info.append(self.dsave_divide)
            # Always "Collected Data"
            file_info.append('Collected Data')
            # The saving directory
            file_info.append(self.dsave_directory)
            
            if is_last:
                self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
            else:
                data.append(self.date_and_time)
                data.append(self.during)
                data.append(num)
                data.append(self.Array[num])
                data.append(self.data[0].strip('\n'))
                data.append(self.data[1].rstrip('\n'))
                
                if num == 0:
                    is_first = True
                    
                    temp = []
                    temp.append('User Name:')
                    temp.append(self.dsave_username)
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Edit Time:')
                    temp.append(str(datetime.datetime.now()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Array Source:')
                    temp.append(str(self.ui.lineEdit_directory_keithley.text()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Visa Address:')
                    temp.append(str(self.ui.comboBox_visa_keithley.currentText()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Visa Name:')
                    visa = str(self.ui.labelK1_visaname.text())
                    visa_name = visa.rstrip('\n')
                    visa_name = visa_name.replace(',', ' ')
                    temp.append(str(visa_name))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Scan Source:')
                    temp.append('Voltage')
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Time Step(sec):')
                    temp.append(str(self.ui.lineEdit_tstep_keithley.text()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Comments:')
                    temp.append(str(self.ui.textEditK1_dsave_comment.toPlainText()))
                    comments.append(temp)
                    #####################
                    parameters.append('Date')
                    units.append('String')
                    parameters.append('Time')
                    units.append('s')
                    parameters.append('Step')
                    units.append('1')
                    parameters.append('Array')
                    units.append('1')
                    parameters.append('Voltage')
                    units.append('Volts')
                    parameters.append('Current')
                    units.append('Amps')
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
                else:
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
    
    def MPL_Plot(self):        
        if self.ui.radioButton_timescan_keithley.isChecked():
            self.ui.label_start_end_keithley.setText('(' + str(format(self.t_plot[0], '.2f')) + ', ' + str(format(self.t_plot[len(self.t_plot) - 1], '.2f')) + ')')
            self.Reset_plot_ct_analysis()
            self.axes_ct_analysis.grid()
            self.axes_ct_analysis.set_title('Keithley Current Value in Time scale')
            self.axes_ct_analysis.set_ylabel("Current (" + self.current_scale[1] + ")")
            self.axes_ct_analysis.set_xlabel("Time (" + self.time_scale[1] + ")")
            self.axes_ct_analysis.plot(self.t_plot, self.y_plot, marker = '.', linestyle = '-')
            
            self.Reset_plot_vt_analysis()
            self.axes_vt_analysis.grid()
            self.axes_vt_analysis.set_title('Keithely Voltage Source in Time scale')
            self.axes_vt_analysis.set_ylabel("Voltage (" + self.voltage_scale[1] + ")")
            self.axes_vt_analysis.set_xlabel("Time (" + self.time_scale[1] + ")")
            self.axes_vt_analysis.plot(self.t_plot, self.x_plot, marker = '.', linestyle = '-')
        elif self.ui.radioButton_stepscan_keithley.isChecked():
            self.ui.label_start_end_keithley.setText('(' + str(self.s_value[0]) + ', ' + str(self.s_value[len(self.s_value) - 1]) + ')')
            self.Reset_plot_ct_analysis()
            self.axes_ct_analysis.grid()
            self.axes_ct_analysis.set_title('Keithley Current Value in Step scale')
            self.axes_ct_analysis.set_ylabel("Current (" + self.current_scale[1] + ")")
            self.axes_ct_analysis.set_xlabel("Step (1)")
            self.axes_ct_analysis.plot(self.s_value, self.y_plot, marker = '.', linestyle = '-')
            
            self.Reset_plot_vt_analysis()
            self.axes_vt_analysis.grid()
            self.axes_vt_analysis.set_title('Keithely Voltage Source in Step scale')
            self.axes_vt_analysis.set_ylabel("Voltage (" + self.voltage_scale[1] + ")")
            self.axes_vt_analysis.set_xlabel("Step (1)")
            self.axes_vt_analysis.plot(self.s_value, self.x_plot, marker = '.', linestyle = '-')
        
        self.Reset_plot_analysis()
        self.axes_analysis.grid()
        self.axes_analysis.set_title('Keithely Voltage Source Measurement')
        self.axes_analysis.set_ylabel("Current (" + self.current_scale[1] + ")")
        self.axes_analysis.set_xlabel("Voltage (" + self.voltage_scale[1] + ")")
        self.axes_analysis.plot(self.x_plot, self.y_plot, marker = '.', linestyle = '-')
        
        self.emit(SIGNAL("mpl_plot"))
    
    def Clear_keithley(self):
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        self.ui.pushButton_stop_keithley.setEnabled(False)
        self.ui.curvewidget_keithley.plot.set_titles('', '', '')
        self.ui.curvewidget_vt_keithley.plot.set_titles('', '', '')
        self.ui.curvewidget_ct_keithley.plot.set_titles('', '', '')
        self.curve.set_data([], [])
        self.curve_ct.set_data([], [])
        self.curve_vt.set_data([], [])
        self.Reset_plot_analysis()
        self.axes_analysis.grid()
        self.Reset_plot_ct_analysis()
        self.axes_ct_analysis.grid()
        self.Reset_plot_vt_analysis()
        self.axes_vt_analysis.grid()
        self.emit(SIGNAL("clear_plot"))
    
    def Fit(self):
        try:
            warnings.simplefilter('ignore', np.RankWarning)
            user_input = self.ui.lineEdit_fit_keithley.text()
            input_list = user_input.split(',')
            start_input = float(input_list[0])
            end_input = float(input_list[1])
            if self.ui.radioButton_timescan_keithley.isChecked():
                # start point
                if start_input < self.t_plot[0]:
                    start = 0
                elif start_input > self.t_plot[len(self.t_plot) - 1]:
                    start = len(self.t_plot) - 1
                else:
                    for i in range(0, len(self.t_plot)):
                        if start_input <= self.t_plot[i]:
                            start = i
                            break
                # end point
                if end_input < self.t_plot[0]:
                    end = 0
                elif end_input > self.t_plot[len(self.t_plot) - 1]:
                    end = len(self.t_plot) - 1
                else:
                    for i in range(0, len(self.t_plot)):
                        if end_input <= self.t_plot[i]:
                            end = i + 1
                            break
                
            elif self.ui.radioButton_stepscan_keithley.isChecked():
                # start point
                if start_input < self.s_value[0]:
                    start = 0
                elif start_input > self.s_value[len(self.s_value) - 1]:
                    start = len(self.s_value) - 1
                else:
                    for i in range(0, len(self.s_value)):
                        if start_input <= self.s_value[i]:
                            start = i
                            break
                # end point
                if end_input < self.s_value[0]:
                    end = 0
                elif end_input > self.s_value[len(self.s_value) - 1]:
                    end = len(self.s_value) - 1
                else:
                    for i in range(0, len(self.s_value)):
                        if end_input <= self.s_value[i]:
                            end = i + 1
                            break
            
            numpy_fit = np.polyfit(self.x_plot[start:end], self.y_plot[start:end], 1)
                
            self.ui.label_IV_keithley.setText(str(format(numpy_fit[0], '.5f')))
            self.ui.label_VI_keithley.setText(str(format(1 / numpy_fit[0], '.5f')))
            self.ui.label_intercept_keithley.setText(str(format(numpy_fit[1], '.5f')))
            self.ui.labelK1_condition.setText('Linear fit done.')
        except Exception, e:
            self.ui.labelK1_condition.setText('Please enter valid start/end value')
        
    # Reset the analysis matplot widget        
    def Reset_plot_ct_analysis(self):
        self.ui.mplwidget_ct_analysis.figure.clear()
        self.axes_ct_analysis = self.ui.mplwidget_ct_analysis.figure.add_subplot(111)
        
    def Reset_plot_vt_analysis(self):
        self.ui.mplwidget_vt_analysis.figure.clear()
        self.axes_vt_analysis = self.ui.mplwidget_vt_analysis.figure.add_subplot(111)
    
    def Reset_plot_analysis(self):
        self.ui.mplwidget_analysis.figure.clear()
        self.axes_analysis = self.ui.mplwidget_analysis.figure.add_subplot(111)
        
    def __del__(self):
        self.exiting = True
        self.wait()
        