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

class Array_Builder():
        
    def __init__(self, ui):
        self.ui = ui
        
    def Plot_general(self):
        first_available = True
        self.data_available = False
        
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
                            
                    self.data_available = True
                    self.Plot()
                    self.ui.textEdit_condition.setText('Array has been plotted')
                    self.ui.pushButton_clear.setEnabled(True)
                    self.ui.pushButton_save.setEnabled(True)
    
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
    
    def Reset_plot_general(self):
        self.ui.mplwidget_general.figure.clear()
        self.axes_general = self.ui.mplwidget_general.figure.add_subplot(111)
        
    def Reset_plot_import(self):
        self.ui.mplwidget_import.figure.clear()
        self.axes_import = self.ui.mplwidget_import.figure.add_subplot(111)
    
    def Reset_plot_scan(self):
        self.ui.mplwidget_scan.figure.clear()
        self.axes_scan = self.ui.mplwidget_scan.figure.add_subplot(111)
                        
    def Clear(self):
        self.data_available = False
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
            self.data_available = False
            self.ui.lineEdit_directory_save.setText("None")
            self.ui.textEdit_condition.setText("Please choose valid saving directory.") 