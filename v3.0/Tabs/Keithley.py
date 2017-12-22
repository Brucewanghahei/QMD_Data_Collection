# Import numpy library
import numpy as np
import os
import sys
import datetime
import visa
import math
import time

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# These are the modules required for the guiqwt widgets.
# Import plot widget base class
from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

class Keithley():
    
    def __init__(self, ui):
        
        self.collect_data_thread = Collect_data()
        self.Array = []
        self.ui = ui
        self.count = 0
        self.go_on = True

        # Set up guiqwt plot
        self.curve_item = make.curve([], [], color = 'b')
        self.ui.curvewidget_keithley.plot.add_item(self.curve_item)
        self.ui.curvewidget_keithley.plot.set_antialiasing(True)
        self.ui.curvewidget_keithley.plot.set_titles("Measurement and Plot Based on Array", "X-Axis", "Y-Axis")
        
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
                self.Array.append(value[1])
                temp += 1
                
            
            self.Plot_import(x_value, y_value)
            self.ui.lineEdit_condition_keithley.setText("File is imported correctly.")
            self.ui.groupBox_visa_keithley.setEnabled(True)
            
    def Copy_keithley(self, Values):
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
        
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import.draw()
    
    def Plot_data(self, voltage, current):
        self.ui.label_yvalue_keithley.setText(format(current, '.3f'))
        self.ui.label_xvalue_keithley.setText(format(voltage, '.3f'))
        self.curve_item.plot().replot()
        
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
        self.collect_data_thread.input(self.visa_chosen, self.ui, self.Array, self.go_on, self.curve_item)
        self.ui.pushButton_pause_keithley.setEnabled(True)
        self.ui.pushButton_stop_keithley.setEnabled(True)
        self.ui.pushButton_scan_keithley.setEnabled(False)
    
    
    # Tab: Keithley
    # Group: Scan
    # Clear the scan result and ready to start again
    def Clear_keithley(self):
        self.ui.pushButton_clear_keithley.setEnabled(False)
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        self.ui.pushButton_stop_keithley.setEnabled(False)

class Collect_data(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def input(self, inst, ui, Array, go_on, curve):
        self.inst = inst
        self.ui = ui
        self.Array = np.array(Array)
        self.go_on = go_on
        self.curve = curve
        self.time_step = float(self.ui.lineEdit_tstep_keithley.text())
        self.voltage_scale = [1, 'Volts']
        self.current_scale = [1, 'Amps']
        # if self.ui.radioButton_mv_keithley.isChecked():
        #     self.voltage_scale = [1E-3, 'mVolts']
        # elif self.ui.radioButton_uv_keithley.isChecked():
        #     self.voltage_scale = [1E-6, 'mVolts']
        # elif self.ui.radioButton_v_keithley.isChecked():
        #     self.voltage_scale = [1, 'Volts']
        #     
        # if self.ui.radioButton_na_keithley.isChecked():
        #     self.current_scale = [1E-9, 'nAmps']
        # elif self.ui.radioButton_ua_keithley.isChecked():
        #     self.current_scale = [1E-6, 'uAmps']
        # elif self.ui.radioButton_ma_keithley.isChecked():
        #     self.current_scale = [1E-3, 'mAmps']
        # self.run()
        self.start()
        
    def pause(self):
        if self.go_on:
            self.ui.pushButton_pause_keithley.setText('Continue')
            self.go_on = False
            self.ui.pushButton_clear_keithley.setEnabled(True)
        else:
            self.ui.pushButton_pause_keithley.setText('Pause')
            self.go_on = True
            self.ui.pushButton_clear_keithley.setEnabled(False)
    
    def stop(self):
        self.pause = True
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        self.ui.pushButton_clear_keithley.setEnabled(True)
        
    def run(self):
        x_value = []
        y_value = []
        item = 0
        self.np_Array = []
        self.pause = False
        self.ui.tabWidget_plot_keithely.setCurrentIndex(1)
        
        if self.ui.radioButton_voltage_keithley.isChecked():
            print 1
            if self.ui.radioButton_mv_keithley.isChecked():
                self.voltage_scale = [1E-3, 'mVolts']
            elif self.ui.radioButton_uv_keithley.isChecked():
                self.voltage_scale = [1E-6, 'mVolts']
            elif self.ui.radioButton_v_keithley.isChecked():
                self.voltage_scale = [1, 'Volts']
            print 2
            self.np_Array = self.Array * float(self.voltage_scale[0])
            self.ui.label_yname_keithley.setText('Current:')
            self.ui.label_xname_keithley.setText('Voltage:')
            self.ui.label_xunit_keithley.setText(self.voltage_scale[1])
            print 3
            while True:
                if self.go_on:
                    print 4
                    if item == len(self.np_Array):
                        self.ui.pushButton_scan_keithley.setEnabled(True)
                        self.ui.pushButton_pause_keithley.setEnabled(False)
                        self.ui.pushButton_clear_keithley.setEnabled(True)
                        break
                    if self.pause:                        
                        break
                    # Select the front-panel terminals for the measurement
                    self.inst.write('ROUT:TERM FRONT')
                    # Set the instrument to measure the current
                    self.inst.write('SENS:FUNC "CURR"')
                    # Set the voltage limitation
                    self.inst.write("SOUR:VOLT:ILIM 1.05")
                    # Set the voltage range to be auto
                    self.inst.write('SOUR:VOLT:RANG:AUTO ON')
                    # Set to source voltage
                    self.inst.write('SOUR:FUNC VOLT')
                    # Turn on the source read back
                    self.inst.write('SOUR:VOLT:READ:BACK 1')
                    # Input the individual voltage to start the measurement
                    
                    self.inst.write("SOUR:VOLT " + str(self.np_Array[item]))
                    self.inst.write('SENS:CURR:RSEN ' + 'OFF')
                    self.inst.write('OUTP ON')
                    voltage = self.inst.query('READ? "defbuffer1", SOUR')
                    voltage_values = float(voltage) / self.voltage_scale[0]
                    x_value.append(float(voltage_values))
                    current = self.inst.query('READ? "defbuffer1", READ')
                    current_values = float(current)
                    current_scale = [1, "Amps"]
                    if abs(current_values) > 1:
                        current_scale = [1, "Amps"]
                    elif abs(current_values) > 1E-3 and abs(current_values) < 1:
                        current_scale = [1E-3, "mAmps"]
                    elif abs(current_values) > 1E-6 and abs(current_values) < 1E-3:
                        current_scale = [1E-6, "uAmps"]
                    elif abs(current_values) > 1E-9 and abs(current_values) < 1E-6:
                        current_scale = [1E-9, "nAmps"]
                    elif abs(current_values) > 1E-12 and abs(current_values) < 1E-9:
                        current_scale = [1E-12, "pAmps"]
                    current_values = current_values / current_scale[0]
                    y_value.append(float(current_values))
                    self.curve.set_data(x_value, y_value)
                    self.emit(SIGNAL("plot"), voltage_values, current_values)
                    
                    if item == 0:
                        self.ui.label_yunit_keithley.setText(self.current_scale[1])
                        
                        self.ui.curvewidget_keithley.plot.set_titles("Keithely Voltage Source Measurement", "Voltage (" + self.voltage_scale[1] + ")", "Current (" + self.current_scale[1] + ")")
                    time.sleep(self.time_step)
                    item += 1
                    
            self.inst.write("OUTP OFF")
        elif self.ui.radioButton_current_keithley.isChecked():
            self.Array = self.Array * float(self.current_scale[0])
            self.ui.label_yname_keithley.setText('Voltage:')
            self.ui.label_xname_keithley.setText('Current:')
        
                
    def __del__(self):
        self.exiting = True
        self.wait()
        