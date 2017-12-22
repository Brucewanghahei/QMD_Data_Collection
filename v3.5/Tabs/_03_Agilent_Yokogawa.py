# Import numpy library
import numpy as np
import os
import sys
import datetime
import visa
import math
import time
import warnings
import numpy.polynomial.polynomial as poly

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

# These are the modules required for the guiqwt widgets.
# Import plot widget base class
from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

import subprocess

class Agilent_Yokogawa():
    def __init__(self, main, ui):
        self.ui = ui
        self.copyData = main.copyData
        self.collectDataThread = CollectData()
        self.save_thread = Save_Thread()
        
        self.update_visa()
        
        self.ui.pushButtonStart.setDisabled(True)
        self.ui.pushButtoncloseVisa1.setDisabled(True)
        self.ui.pushButtoncloseVisa2.setDisabled(True)
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonStart.setEnabled(False)
        
        self.x_value = []
        self.y_value = []
        self.item = 0
        self.Array = []

        self.timeStep = .1
        self.ui.lineEditTimeStep.setText(str(self.timeStep))
        
        self.directory = ''
        self.temp = []
        
        # Sets up Current v. Voltage guiqwt plot
        self.curve_item_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_scanPlot_ay.plot.add_item(self.curve_item_ay)
        self.ui.curvewidget_scanPlot_ay.plot.set_antialiasing(True)
        
        # Sets up Voltage v. Time Step guiqwt plot
        self.curve_item_vt_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_vt_ay.plot.add_item(self.curve_item_vt_ay)
        self.ui.curvewidget_vt_ay.plot.set_antialiasing(True)
        
         # Sets up Current v. Time Step guiqwt plot
        self.curve_item_ct_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_ct_ay.plot.add_item(self.curve_item_ct_ay)
        self.ui.curvewidget_ct_ay.plot.set_antialiasing(True)
        
        # For the canvas.
        self.canvas_import_ay = FigureCanvas(self.ui.mplwidget_import_ay.figure)
        self.canvas_import_ay.setParent(self.ui.widget_import_ay)
        self.mpl_toolbar_import_ay = NavigationToolbar(self.canvas_import_ay, self.ui.widget_import_ay)
        self.canvas_analysis_ay = FigureCanvas(self.ui.mplwidget_analysis_ay.figure)
        self.canvas_analysis_ay.setParent(self.ui.widget_analysis_ay)
        self.mpl_toolbar_analysis_ay = NavigationToolbar(self.canvas_analysis_ay, self.ui.widget_analysis_ay)
        self.canvas_analysis_ct_ay = FigureCanvas(self.ui.mplwidget_analysis_ct_ay.figure)
        self.canvas_analysis_ct_ay.setParent(self.ui.widget_analysis_ct_ay)
        self.mpl_toolbar_analysis_ct_ay = NavigationToolbar(self.canvas_analysis_ct_ay, self.ui.widget_analysis_ct_ay)
        self.canvas_analysis_vt_ay = FigureCanvas(self.ui.mplwidget_analysis_vt_ay.figure)
        self.canvas_analysis_vt_ay.setParent(self.ui.widget_analysis_vt_ay)
        self.mpl_toolbar_analysis_vt_ay = NavigationToolbar(self.canvas_analysis_vt_ay, self.ui.widget_analysis_vt_ay)
        
        # Create the QVBoxLayout object and add the widget into the layout
        vbox_import_ay = QVBoxLayout()
        vbox_import_ay.addWidget(self.canvas_import_ay)
        vbox_import_ay.addWidget(self.mpl_toolbar_import_ay)
        self.ui.widget_import_ay.setLayout(vbox_import_ay)
        vbox_analysis_ay = QVBoxLayout()
        vbox_analysis_ay.addWidget(self.canvas_analysis_ay)
        vbox_analysis_ay.addWidget(self.mpl_toolbar_analysis_ay)
        self.ui.widget_analysis_ay.setLayout(vbox_analysis_ay)
        vbox_analysis_ct_ay = QVBoxLayout()
        vbox_analysis_ct_ay.addWidget(self.canvas_analysis_ct_ay)
        vbox_analysis_ct_ay.addWidget(self.mpl_toolbar_analysis_ct_ay)
        self.ui.widget_analysis_ct_ay.setLayout(vbox_analysis_ct_ay)
        vbox_analysis_vt_ay = QVBoxLayout()
        vbox_analysis_vt_ay.addWidget(self.canvas_analysis_vt_ay)
        vbox_analysis_vt_ay.addWidget(self.mpl_toolbar_analysis_vt_ay)
        self.ui.widget_analysis_vt_ay.setLayout(vbox_analysis_vt_ay)
        
        # Connect the mplwidget with canvass
        self.ui.mplwidget_import_ay = self.canvas_import_ay
        self.ui.mplwidget_analysis_ay = self.canvas_analysis_ay
        self.ui.mplwidget_analysis_ct_ay = self.canvas_analysis_ct_ay
        self.ui.mplwidget_analysis_vt_ay = self.canvas_analysis_vt_ay

        main.connect(self.ui.pushButtonselectVisa, SIGNAL('clicked()'), self.select_visa)
        main.connect(self.ui.pushButtonupdateVisa, SIGNAL('clicked()'), self.update_visa)
        main.connect(self.ui.pushButtoncloseVisa1, SIGNAL('clicked()'), self.close_visaCurrent)
        main.connect(self.ui.pushButtoncloseVisa2, SIGNAL('clicked()'), self.close_visaVoltage)
        
        main.connect(self.ui.pushButton_browse_ay, SIGNAL('clicked()'), self.browse_ay)
        main.connect(self.ui.pushButton_import_ay, SIGNAL('clicked()'), self.import_ay)
        main.connect(self.ui.pushButton_copy_ay, SIGNAL('clicked()'), self.copy_ay)
        
        main.connect(self.ui.pushButtonStart, SIGNAL('clicked()'), self.pre_start)
        main.connect(self.ui.pushButtonPause, SIGNAL('clicked()'), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonStop, SIGNAL('clicked()'), self.stop)
        main.connect(self.ui.pushButtonClear, SIGNAL('clicked()'), self.clear_plots)
        main.connect(self.ui.pushButtonFit, SIGNAL('clicked()'), self.Fit)
        
        main.connect(self.collectDataThread, SIGNAL("Plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("Analyze"), self.Analyze)
        
        main.connect(self.ui.pushButton_browse_save_G_ay, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButton_check_G_ay, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButton_Select_Directory_G_ay, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.radioButton_csv_G_ay, SIGNAL('clicked()'), self.Select_type_G_ay)
        main.connect(self.ui.radioButton_txt_G_ay, SIGNAL('clicked()'), self.Select_type_G_ay)
        main.connect(self.ui.radioButton_Timename_G_ay, SIGNAL('clicked()'), self.Select_name_G_ay)
        main.connect(self.ui.radioButton_Custom_Name_G_ay, SIGNAL('clicked()'), self.Select_name_G_ay)
        main.connect(self.ui.pushButton_Save_G_ay, SIGNAL('clicked()'), self.G_save)
        
                     

    def browse_ay(self):
        prev_dir = os.getcwd()
        print prev_dir
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
            self.ui.lineEdit_directory_ay.setText(fileDir)
            self.ui.pushButton_import_ay.setEnabled(True)
            self.ui.lineEdit_condition_ay.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')   

    def import_ay(self):
        divider_found = True
        count = 0
        temp = 0
        x_value = []
        y_value = []
        
        fileDir = self.ui.lineEdit_directory_ay.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.lineEdit_condition_ay.setText("Data not found in file. Please check it.")
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
                x_value.append(temp + 1)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array.append(value[1])
                temp += 1
            
            self.plot_import(x_value, y_value)
            self.ui.output.setText("File was imported correctly.")
            
    def copy_ay(self):
        Values = self.copyData()
        if not Values == False:
            for i in range(0, len(Values)):
                for j in range(0, len(Values[i])):
                    self.x_value.append(self.item)
                    self.x_value.append(self.item + 1)
                    self.y_value.append(Values[i][j])
                    self.y_value.append(Values[i][j])
                    self.Array.append(Values[i][j])
                    self.item += 1
        self.plot_import(self.x_value, self.y_value)
        print self.Array
            
    def plot_import(self, x, y):
        self.reset_plot_import()
        self.ui.mplwidget_import_ay.figure.clear()
        self.axes_import = self.ui.mplwidget_import_ay.figure.add_subplot(111)
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import_ay.draw()
        
    def update_visa(self):
        self.rm = visa.ResourceManager()
        
        try:
            visas = self.rm.list_resources()
        except:
            visas = ''
            
        self.ui.comboBoxSelectVisa1.clear()
        self.ui.comboBoxSelectVisa2.clear()
        
        check_current1 = False
        check_current2 = False

        for each_visa in visas:
            self.ui.comboBoxSelectVisa1.addItem(each_visa)
            
        for each_visa in visas:
            self.ui.comboBoxSelectVisa2.addItem(each_visa)
        
        if check_current1 == False:
            self.ui.labelVisa1.setText("None")
            self.ui.pushButtonStart.setDisabled(True)
            self.ui.pushButtoncloseVisa1.setDisabled(True)
        else:
            pass
        
        if check_current2 == False:
            self.ui.labelVisa2.setText("None")
            self.ui.pushButtonStart.setDisabled(True)
            self.ui.pushButtoncloseVisa2.setDisabled(True)
        else:
            pass
        
    def select_visa(self):
        self.rm = visa.ResourceManager()
        visa1 = str(self.ui.comboBoxSelectVisa1.currentText())
        visa2 = str(self.ui.comboBoxSelectVisa2.currentText())
        valid = False

        
        inst1 = self.rm.open_resource(visa1)
        inst2 = self.rm.open_resource(visa2)
        
        try:
            valid = self.check_Visa(inst1,inst2)
        except:
            self.ui.lineEditError.setText("Error In Selected Visas")
        
        if valid == True:
            visa1_name = str(inst1.ask("*IDN?"))
            visa2_name = str(inst2.ask("*IDN?"))
            self.ui.labelVisa1.setText(visa1_name)
            self.ui.labelVisa2.setText(visa2_name)
            self.visaCurrent = inst1
            self.visaVoltage = inst2
            self.ui.lineEditError.setText("None")
            self.ui.pushButtonStart.setDisabled(False)
            self.ui.pushButtonStop.setDisabled(False)
            self.ui.pushButtoncloseVisa1.setDisabled(False)
            self.ui.pushButtoncloseVisa2.setDisabled(False)
        else:
            self.ui.labelVisa1.setText("None")
            self.ui.labelVisa2.setText("None")
            self.ui.pushButtonStart.setDisabled(True)
            self.ui.pushButtoncloseVisa1.setDisabled(True)
            self.ui.pushButtoncloseVisa2.setDisabled(True)
            self.ui.lineEditError.setText("Invalid Visas")
        
    def check_Visa(self,inst1,inst2):
        try:
            inst1.ask('*IDN?')
            inst2.ask('*IDN?')
            valid = True
        except:
            valid = False
            
        return valid
    
    def close_visaCurrent(self):
        self.visaCurrent.close()
        self.ui.lineEditOutput.setText("Visa For Current Has Been Closed")
        
    def close_visaVoltage(self):
        self.visaVoltage.close()
        self.ui.lineEditOutput.setText("Visa For Voltage Has Been Closed")
        
    def pre_start(self):
        first_value = self.Array[0]
        i = 0
        while self.Array[i] == first_value:
            i = i + 1
        self.repeat = i
        
        if len(self.Array)/self.repeat >= 200 and self.ui.radioButtonCurrent_mA.isChecked():
            self.ui.lineEditError.setText("Please make sure that Array peak is less than 200 for mA current.")
        else:
            self.first_plot = True
            self.start()
        
    def start(self):
        self.ui.pushButtonStart.setEnabled(False)
        self.ui.pushButtonPause.setEnabled(True)
        self.ui.pushButtonStop.setEnabled(True)
        if float(self.ui.lineEditTimeStep.text()) > 0 or self.first_plot == True or self.clear_check == True:
            self.visaCurrent.write('OUTP ON')
            self.timeStep = float(self.ui.lineEditTimeStep.text())
            self.collectDataThread.input(self.ui, self.visaCurrent, self.visaVoltage, self.Array, self.timeStep, self.curve_item_ay, self.curve_item_vt_ay, self.curve_item_ct_ay)
            self.ui.pushButtonStart.setEnabled(True)
            self.ui.lineEditOutput.setText("Running")
            self.ui.tabWidget_plot_ay.setCurrentIndex(2)
        else:
            self.ui.lineEditError.setText("Error")
            
    def plotData(self):
        self.curve_item_ay.plot().replot()
        self.curve_item_ct_ay.plot().replot()
        self.curve_item_vt_ay.plot().replot()
        self.ui.curvewidget_ct_ay.plot.do_autoscale()
        self.ui.curvewidget_vt_ay.plot.do_autoscale()
        self.ui.curvewidget_scanPlot_ay.plot.do_autoscale()
        
    def Analyze(self, current, voltage, steps, time, date_value):
        self.ui.pushButtonStart.setEnabled(False)
        self.ui.pushButtonPause.setEnabled(False)
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonClear.setEnabled(True)

        self.ui.tabWidget_save_ay.setEnabled(True)
        
        self.ui.lineEditOutput.setText('Data Collection Is Done')
        self.current = current
        self.voltage = voltage
        self.steps = steps
        self.time = time
        self.date_value = date_value
        self.ui.mplwidget_analysis_ay.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.axes_analysis_ay.set_title('Voltage v. Current')
        self.axes_analysis_ay.set_ylabel("Voltage (V)")
        self.axes_analysis_ay.set_xlabel("Current (A)")
        self.axes_analysis_ay.plot(self.current, self.voltage, marker = '.', linestyle = '-')
        self.ui.mplwidget_analysis_ay.draw()
        
        if self.collectDataThread.time_scale == True:
            self.ui.mplwidget_analysis_ct_ay.figure.clear()
            self.axes_analysis_ct_ay = self.ui.mplwidget_analysis_ct_ay.figure.add_subplot(111)
            self.axes_analysis_ct_ay.grid()
            self.axes_analysis_ct_ay.set_title('Current v. Time')
            self.axes_analysis_ct_ay.set_ylabel("Current (A)")
            self.axes_analysis_ct_ay.set_xlabel("Time (s)")
            self.axes_analysis_ct_ay.plot(self.time, self.current, marker = '.', linestyle = '-')
            self.ui.mplwidget_analysis_ct_ay.draw()
            
            self.ui.mplwidget_analysis_vt_ay.figure.clear()
            self.axes_analysis_vt_ay = self.ui.mplwidget_analysis_vt_ay.figure.add_subplot(111)
            self.axes_analysis_vt_ay.grid()
            self.axes_analysis_vt_ay.set_title('Voltage v. Time')
            self.axes_analysis_vt_ay.set_ylabel("Voltage (V)")
            self.axes_analysis_vt_ay.set_xlabel("Time (s)")
            self.axes_analysis_vt_ay.plot(self.time, self.voltage, marker = '.', linestyle = '-')
            self.ui.mplwidget_analysis_vt_ay.draw()
            
        else:
            self.ui.mplwidget_analysis_ct_ay.figure.clear()
            self.axes_analysis_ct_ay = self.ui.mplwidget_analysis_ct_ay.figure.add_subplot(111)
            self.axes_analysis_ct_ay.grid()
            self.axes_analysis_ct_ay.set_title('Current v. Steps')
            self.axes_analysis_ct_ay.set_ylabel("Current (A)")
            self.axes_analysis_ct_ay.set_xlabel("Steps")
            self.axes_analysis_ct_ay.plot(self.steps, self.current, marker = '.', linestyle = '-')
            self.ui.mplwidget_analysis_ct_ay.draw()
        
            self.ui.mplwidget_analysis_vt_ay.figure.clear()
            self.axes_analysis_vt_ay = self.ui.mplwidget_analysis_vt_ay.figure.add_subplot(111)
            self.axes_analysis_vt_ay.grid()
            self.axes_analysis_vt_ay.set_title('Voltage v. Steps')
            self.axes_analysis_vt_ay.set_ylabel("Voltage (V)")
            self.axes_analysis_vt_ay.set_xlabel("Steps")
            self.axes_analysis_vt_ay.plot(self.steps, self.voltage, marker = '.', linestyle = '-')
            self.ui.mplwidget_analysis_vt_ay.draw()
            
    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonStartLI.setEnabled(True)
        self.ui.pushButtonStopLI.setEnabled(False)
        self.ui.pushButtonPauseLI.setEnabled(False)
        self.ui.lineEditOutput.setText("Stopped")
        self.ui.pushButtonPauseLI.setText("Pause")
        self.visaCurrent.write('OUTP OFF')
        
    def reset_plot_import(self):
        self.ui.mplwidget_import_ay.figure.clear()
        self.axes_import = self.ui.mplwidget_import.figure.add_subplot(111)
        
    def clear_plots(self):
        self.ui.pushButtonStart.setEnabled(True)
        #Clears the analysis plots
        self.ui.mplwidget_analysis_ay.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.ui.mplwidget_analysis_ay.draw()
        self.ui.mplwidget_analysis_ct_ay.figure.clear()
        self.axes_analysis_ct_ay = self.ui.mplwidget_analysis_ct_ay.figure.add_subplot(111)
        self.axes_analysis_ct_ay.grid()
        self.ui.mplwidget_analysis_ct_ay.draw()
        self.ui.mplwidget_analysis_vt_ay.figure.clear()
        self.axes_analysis_vt_ay = self.ui.mplwidget_analysis_vt_ay.figure.add_subplot(111)
        self.axes_analysis_vt_ay.grid()
        self.ui.mplwidget_analysis_vt_ay.draw()
        #Clears the scan plots
        self.ui.curvewidget_scanPlot_ay.plot.set_titles('', '', '')
        self.ui.curvewidget_vt_ay.plot.set_titles('', '', '')
        self.ui.curvewidget_ct_ay.plot.set_titles('', '', '')
        self.curve_item_ay.set_data([], [])
        self.curve_item_ct_ay.set_data([], [])
        self.curve_item_vt_ay.set_data([], [])
        self.curve_item_ay.plot().replot()
        self.curve_item_ct_ay.plot().replot()
        self.curve_item_vt_ay.plot().replot()
        
        self.clear_check = True
        self.ui.lineEditOutput.setText("Plots have been cleared")
        
    def Fit(self):
            try:
                warnings.simplefilter('ignore', np.RankWarning)
                user_input = self.ui.lineEdit_fit_ay.text()
                input_list = user_input.split(',')
                start_input = float(input_list[0])
                end_input = float(input_list[1])
                if self.ui.radioButtonTimeScale.isChecked():
                    # start point
                    if start_input < self.time[0]:
                        start = 0
                    elif start_input > self.time[len(self.time) - 1]:
                        start = len(self.time) - 1
                    else:
                        for i in range(0, len(self.time)):
                            if start_input <= self.time[i]:
                                start = i
                                break
                    # end point
                    if end_input < self.time[0]:
                        end = 0
                    elif end_input > self.time[len(self.time) - 1]:
                        end = len(self.time) - 1
                    else:
                        for i in range(0, len(self.time)):
                            if end_input <= self.time[i]:
                                end = i + 1
                                break
                    
                elif self.ui.radioButtonStepScale.isChecked():
                    # start point
                    if start_input < self.steps[0]:
                        start = 0
                    elif start_input > self.steps[len(self.steps) - 1]:
                        start = len(self.steps) - 1
                    else:
                        for i in range(0, len(self.steps)):
                            if start_input <= self.steps[i]:
                                start = i
                                break
                    # end point
                    if end_input < self.steps[0]:
                        end = 0
                    elif end_input > self.steps[len(self.steps) - 1]:
                        end = len(self.steps) - 1
                    else:
                        for i in range(0, len(self.steps)):
                            if end_input <= self.steps[i]:
                                end = i + 1
                                break
                
                numpy_fit = np.polyfit(self.current[start:end], self.voltage[start:end], 1)
                    
                self.ui.label_VI_ay.setText(str(format(numpy_fit[0], '.5f')))
                self.ui.label_IV_ay.setText(str(format(1 / numpy_fit[0], '.5f')))
                self.ui.label_intercept_ay.setText(str(format(numpy_fit[1], '.5f')))
                self.ui.lineEditOutput.setText('Linear fit done.')
                fit = np.poly1d(numpy_fit)
                self.axes_analysis_ay.plot(self.current, fit(self.current))
                self.ui.mplwidget_analysis_ay.draw()
                
            except Exception, e:
                self.ui.lineEditOutput.setText('Please enter valid start/end value')

    def select_type_ay(self):
        if self.ui.radioButton_csv_G_ay.isChecked():
            self.type = '.csv'
            self.divide = ','
            self.form = ''
        elif self.ui.radioButton_txt_G_ay.isChecked():
            self.type = '.txt'
            self.divide = '\t'
            self.form = '                     '
        else:
            self.type = False

    def select_name_ay(self):
        now = datetime.datetime.now()
        self.date = '%s-%s-%s' % (now.year, now.month, now.day)
        self.current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
        self.date_and_time = self.date + ' ' + self.current_time
        if self.ui.radioButton_Timename_G_ay.isChecked():
            try:
                self.file = self.date_and_time
            except:
                self.file = False  
        elif self.ui.radioButton_Custom_Name_G_ay.isChecked():
            try:
                self.file = str(self.ui.file.text())
            except:
                self.file = False

    def Google_browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select Google Drive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEdit_GoogleDrive_G_ay.setText(file_dir)
            self.ui.label_condition_G_ay.setText('Open Google Drive User Folder')
            self.ui.pushButton_check_G_ay.setEnabled(True)
    
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
            self.ui.lineEdit_directory_O_ay.setText(fileDir)
            self.ui.label_username_O_ay.setEnabled(True)
            self.ui.comboBox_Name_Folder_O_ay.setEnabled(True)
            self.ui.groupBox_Filename_O_ay.setEnabled(True)
            self.ui.groupBox_File_Type_O_ay.setEnabled(True)
            self.ui.label_comment_O_ay.setEnabled(True)
            self.ui.textEdit_comment_O_ay.setEnabled(True)
            self.ui.pushButton_Save_O_ay.setEnabled(True)
            self.ui.lineEdit_Custom_Name_O_ay.setEnabled(True)
            self.ui.label_condition_O_ay.setText("Click save button to save.")
        else:
            self.ui.lineEdit_directory_O_ay.setText('None')
            self.ui.label_condition_O_ay.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEdit_GoogleDrive_G_ay.text()).split('\\')
        if os.path.exists(self.ui.lineEdit_GoogleDrive_G_ay.text()) == False:
            self.ui.label_condition_G_ay.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.label_condition_G_ay.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.label_namefolder_G_ay.setEnabled(True)
                    self.ui.comboBox_Name_Folder_G_ay.setEnabled(True)
                    self.ui.pushButton_Select_Directory_G_ay.setEnabled(True)
                    self.ui.label_condition_G_ay.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBox_Name_Folder_G_ay.currentText())
        if namefolder == 'None':
            self.ui.label_condition_G_ay.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.label_G_ay.setText("Save to \\" + namefolder + "\Data" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Agilent Yokogawa with Array'
            self.ui.groupBox_File_Type_G_ay.setEnabled(True)
            self.ui.groupBox_Filename_G_ay.setEnabled(True)
            self.ui.label_comment_G_ay.setEnabled(True)
            self.ui.textEdit_comment_G_ay.setEnabled(True)
            self.ui.radioButton_Timename_G_ay.setEnabled(True)
            self.ui.pushButton_Save_G_ay.setEnabled(True)
            self.ui.lineEdit_Custom_Name_G_ay.setEnabled(True)
            self.ui.label_condition_G_ay.setText('Click save button to save.')
            
    def Select_type_G_ay(self):
        if self.ui.radioButton_csv_G_ay.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButton_txt_G_ay.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

    def Select_type_O_ay(self):
        if self.ui.radioButton_csv_O_ay.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButton_txt_O_ay.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'

    def Select_name_G_ay(self):
        if self.ui.radioButton_Timename_G_ay.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_G_ay.isChecked():
            self.G_file_name = str(self.ui.lineEdit_Custom_Name_G_ay.text())
            
    def Select_name_O_ay(self):
        if self.ui.radioButton_Timename_O_ay.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_O_ay.isChecked():
            self.O_file_name = str(self.ui.lineEdit_Custom_Name_O_ay.text())
            
    def G_save(self):
        if self.ui.radioButton_Custom_Name_G_ay.isChecked() and self.ui.lineEdit_Custom_Name_G_ay.text() == '':
            self.ui.label_condition_G_ay.setText('Enter a valid file name.')
        else:          
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
            
            # Line 1: user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_G_ay.currentText()))
            comments.append(temp)
            # Line 2: edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Line 3: array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_ay.text()))
            comments.append(temp)
            # Line 8: scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Current')
            comments.append(temp)
            # Line 9: time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditTimeStep.text()))
            comments.append(temp)
            # Line 10: comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_G_ay.toPlainText()))
            comments.append(temp)
            
            # Do parameters, units and data together
            parameters.append('Date')
            units.append('String')
            data.append(self.date_value)
            
            parameters.append('Time')
            units.append('s')
            data.append(self.time)
            
            parameters.append('Step')
            units.append('1')
            temp = []
            for i in range(0, len(self.voltage)):
                temp.append(i)
            data.append(temp)
            parameters.append('Array')
            units.append('1')
            data.append(self.x_value)
            parameters.append('Voltage')
            units.append('V')
            data.append(self.voltage)
            parameters.append('Current')
            units.append('A')
            data.append(self.current)
            
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
            self.ui.pushButton_Open_G_ay.setEnabled(True)
            self.ui.label_condition_G_ay.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBox_Name_Folder_O_ay.currentText() == 'None':
            self.ui.label_condition_O_ay.setText('Pleanse choose a user name.')
        elif self.ui.radioButton_Custom_Name_O_ay.isChecked() and self.ui.lineEdit_Custom_Name_O_ay.text() == '':
            self.ui.label_condition_O_ay.setText('Please enter a file name.')
        else:
            self.Select_type_O_ay()
            self.Select_name_O_ay()
            
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
            
            # Line 1: user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_G_ay.currentText()))
            comments.append(temp)
            # Line 2: edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Line 3: array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_ay.text()))
            comments.append(temp)
            # Line 4: visa1 address
            temp = []
            temp.append('Visa 1 Address:')
            temp.append(str(self.ui.labelVisa1.text()))
            comments.append(temp)
            # Line 5: visa2 address
            temp = []
            temp.append('Visa 2 Address:')
            temp.append(str(self.ui.labelVisa2.text()))
            comments.append(temp)
            # Line 6: visa1 name
            temp = []
            temp.append('Visa 1 Name:')
            visa1_name = self.visa1_name.rstrip('\n')
            visa1_name = visa1_name.replace(',', ' ')
            temp.append(str(visa1_name))
            comments.append(temp)
            # Line 7: visa2 name
            temp = []
            temp.append('Visa 2 Name:')
            visa2_name = self.visa2_name.rstrip('\n')
            visa2_name = visa2_name.replace(',', ' ')
            temp.append(str(visa2_name))
            comments.append(temp)
            # Line 8: scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Current')
            comments.append(temp)
            # Line 9: time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.Timestep))
            comments.append(temp)
            # Line 10: comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_G_ay.toPlainText()))
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
            for i in range(0, len(self.y_plot)):
                temp.append(i)
            data.append(temp)
            parameters.append('Array')
            units.append('1')
            data.append(self.x_value)
            parameters.append('Voltage')
            units.append('Volts')
            data.append(self.x_plot)
            parameters.append('Current')
            units.append('Amps')
            data.append(self.y_plot)
            
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
            self.ui.pushButton_Open_O_ay.setEnabled(True)
            self.ui.label_condition_O_ay.setText('File has been saved.')
    
    def G_open(self):
        opendir = self.G_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
    def O_open(self):
        opendir = self.O_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
class CollectData(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        
    def input(self, ui, visaCurrent, visaVoltage, Array, timeStep, curve, curve_vt, curve_ct):
        self.ui = ui
        self.visaCurrent = visaCurrent
        self.visaVoltage = visaVoltage
        self.Array = np.array(Array)
        self.timeStep = timeStep
        self.curve = curve
        self.curve_vt = curve_vt
        self.curve_ct = curve_ct
        
        self.dataX = np.array([], dtype = float)
        self.current = np.array([], dtype = float)
        self.voltage = np.array([], dtype = float)
        self.time = np.array([], dtype = float)
        self.steps = np.array([], dtype = float)
        
        self.date_value = []
        
        self.n = 0
        self.magnitude = []
        
        if self.ui.radioButtonCurrent_nA.isChecked():
            self.magnitude= ['nA', 1E-09]
        elif self.ui.radioButtonCurrent_uA.isChecked():
            self.magnitude = ['uA', 1E-06]
        else:
            self.magnitude = ['mA', 1E-03]
            
        self.sweepValues = self.Array * float(self.magnitude[1])
        self.y_axis_label = self.magnitude[0]
        
        self.pauseLoop = False
        #self.run()
        self.start()
        
    def run(self):
        import time
        t1 = 0
        start_time = time.time()
        while True:
            if float(time.time() - t1) > self.timeStep:
                t1 = time.time()
                if self.pauseLoop == False:
                    if self.ui.radioButtonTimeScale.isChecked():
                        self.x_axis_label = 'Time (s)'
                        self.time_scale = True
                    else:
                        self.x_axis_label = 'Steps'
                        self.time_scale = False
                    if self.n == 0:
                        self.visaCurrent.write('SOUR:FUNC CURR')
                        current_value = self.visaCurrent.write('SOUR:LEV:AUTO ' + str(self.sweepValues[self.n]))
                        self.reading = float(self.visaVoltage.ask('MEAS:VOLT?'))
                        self.current = np.append(self.current, float(self.sweepValues[self.n]))
                        self.voltage = np.append(self.voltage, self.reading)
                        end_time = time.time()
                        t = end_time - start_time
                        self.time = np.append(self.time, t)
                        self.steps = np.append(self.steps, self.n)
                        if self.time_scale == True:
                            self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Time", "Time (s)", "Current(" + self.magnitude[0] + ")")
                            self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time", "Time (s)", "Voltage(V)")
                            self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current(" + self.magnitude[0] + ")", "Voltage (V)")
                            self.curve.set_data(self.current, self.voltage)
                            self.curve_ct.set_data(self.time, self.current)
                            self.curve_vt.set_data(self.time, self.voltage)
                        else:
                            self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Steps", "Steps", "Current(" + self.magnitude[0] + ")")
                            self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time", "Steps", "Voltage(V)")
                            self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current(" + self.magnitude[0] + ")", "Voltage (V)")
                            self.curve.set_data(self.current, self.voltage)
                            self.curve_ct.set_data(self.steps, self.current)
                            self.curve_vt.set_data(self.steps, self.voltage)
                        now = datetime.datetime.now()
                        date = '%s-%s-%s' % (now.year, now.month, now.day)
                        current_time = '%s:%s:%s' % (now.hour, now.minute, now.second)
                        date_and_time = date + ' ' + current_time
                        self.date_value.append(date_and_time)
                            
                        self.emit(SIGNAL("Plot"))
                        self.n += 1
                        time.sleep(self.timeStep)
                            
                    elif len(self.Array) > len(self.current):
                        self.visaCurrent.write('SOUR:FUNC CURR')
                        self.visaCurrent.write('SOUR:LEV:AUTO ' + str(self.sweepValues[self.n]))
                        self.reading = float(self.visaVoltage.ask('READ?'))
                        self.current = np.append(self.current, float(self.sweepValues[self.n]))
                        self.voltage = np.append(self.voltage, self.reading)
                        
                        end_time = time.time()
                        t = end_time - start_time
                        self.time = np.append(self.time, t)
                        self.steps = np.append(self.steps, self.n)
                        
                        if self.time_scale == True:
                            self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Time", "Time (s)", "Current(" + self.magnitude[0] + ")")
                            self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time", "Time (s)", "Voltage(V)")
                            self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current(" + self.magnitude[0] + ")", "Voltage (V)")
                            self.curve.set_data(self.current, self.voltage)
                            self.curve_ct.set_data(self.time, self.current)
                            self.curve_vt.set_data(self.time, self.voltage)
                        else:
                            self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Steps", "Steps", "Current(" + self.magnitude[0] + ")")
                            self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time", "Steps", "Voltage(V)")
                            self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current(" + self.magnitude[0] + ")", "Voltage (V)")
                            self.curve.set_data(self.current, self.voltage)
                            self.curve_ct.set_data(self.steps, self.current)
                            self.curve_vt.set_data(self.steps, self.voltage)
                            
                        date = '%s-%s-%s' % (now.year, now.month, now.day)
                        current_time = '%s:%s:%s' % (now.hour, now.minute, now.second)
                        date_and_time = date + ' ' + current_time
                        self.date_value.append(date_and_time)
                            
                        self.emit(SIGNAL("Plot"))
                        self.n += 1
                        time.sleep(self.timeStep)
                    else:
                        self.visaCurrent.write('OUTP OFF')
                        current = self.current
                        voltage = self.voltage
                        steps = self.steps
                        time = self.time
                        date_value = self.date_value
                        self.ui.tabWidget_plot_ay.setCurrentIndex(3)
                        self.emit(SIGNAL("Analyze"), current, voltage, steps, time, date_value)
                        break
                else:
                    pass
            
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            self.ui.lineEditOutput.setText("Running")
        else:
            self.pauseLoop = True
            self.ui.pushButtonPause.setText('Continue')
            self.ui.lineEditOutput.setText("Paused")
    
    def __del__(self):
        self.exiting = True
        self.wait()
            
