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

class Keithley():
    
    def __init__(self, ui):
        self.ui = ui
    
    # Tab: Keithley
    # Group: Import
    # Search and find the directory of the file you want to import
    def Browse_keithley(self):
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
