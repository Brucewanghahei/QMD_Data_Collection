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
        self.Array = []
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
        
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import.draw()
    
    def Plot_analysis(self):
        self.ui.mplwidget_analysis.draw()
        
    def Plot_data(self, voltage, current, time):
        self.ui.label_yvalue_keithley.setText(format(current, '.3f'))
        self.ui.label_xvalue_keithley.setText(format(voltage, '.3f'))
        self.ui.label_tvalue_keithley.setText(format(time, '.3f'))
        self.ui.curvewidget_keithley.plot.do_autoscale()
        self.ui.curvewidget_ct_keithley.plot.do_autoscale()
        self.ui.curvewidget_vt_keithley.plot.do_autoscale()
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
        self.collect_data_thread.input(self.visa_chosen, self.ui, self.Array, self.go_on, self.curve_item, self.curve_ct_item, self.curve_vt_item)
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

    def input(self, inst, ui, Array, go_on, curve, curve_ct, curve_vt):
        self.inst = inst
        self.ui = ui
        self.Array = np.array(Array)
        self.go_on = go_on
        self.curve = curve
        self.curve_ct = curve_ct
        self.curve_vt = curve_vt
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
        self.go_on = True
        self.pause = True
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        self.ui.pushButton_clear_keithley.setEnabled(True)
        
    def run(self):
        x_value = []
        y_value = []
        t_value = []
        x_plot = np.array([])
        y_plot = np.array([])
        t_plot = np.array([])
        item = 0
        self.current_scale = [1, "Amps"]
        self.voltage_scale = [1, 'Volts']
        self.time_scale = [1, "Sec"]
        self.np_Array = []
        self.pause = False
        
        self.ui.tabWidget_plot_keithely.setCurrentIndex(1)
        
        if self.ui.radioButton_voltage_keithley.isChecked():
            if self.ui.radioButton_mv_keithley.isChecked():
                self.voltage_scale = [1E-3, 'mVolts']
            elif self.ui.radioButton_uv_keithley.isChecked():
                self.voltage_scale = [1E-6, 'mVolts']
            elif self.ui.radioButton_v_keithley.isChecked():
                self.voltage_scale = [1, 'Volts']
            self.np_Array = self.Array * float(self.voltage_scale[0])
            self.ui.label_yname_keithley.setText('Current:')
            self.ui.label_xname_keithley.setText('Voltage:')
            self.ui.label_xunit_keithley.setText(self.voltage_scale[1])
            t1_ = 0
            start_time = time.time()
            while True:
                if float(time.time() - t1_) > self.time_step:
                    #self.ui.lineEdit_tstep_keithley.setText(str(round(time.time() - t1_, 2)))
                    t1_ = time.time()
                    if self.go_on:
                        if self.pause:
                            self.Reset_plot_analysis()
                            self.axes_analysis.grid()
                            self.axes_analysis.set_title('Keithely Voltage Source Measurement')
                            self.axes_analysis.set_ylabel("Current (" + self.current_scale[1] + ")")
                            self.axes_analysis.set_xlabel("Voltage (" + self.voltage_scale[1] + ")")
                            self.axes_analysis.plot(x_plot, y_plot, marker = '.', linestyle = '-')
                            self.ui.lineEdit_condition_keithley.setText('Reading paused.')
                            self.emit(SIGNAL("mpl_plot"))
                            self.ui.groupBox_save_keithley.setEnabled(True)
                            break
                        if item == len(self.np_Array):
                            self.Reset_plot_analysis()
                            self.axes_analysis.grid()
                            self.axes_analysis.set_title('Keithely Voltage Source Measurement')
                            self.axes_analysis.set_ylabel("Current (" + self.current_scale[1] + ")")
                            self.axes_analysis.set_xlabel("Voltage (" + self.voltage_scale[1] + ")")
                            self.axes_analysis.plot(x_plot, y_plot, marker = '.', linestyle = '-')
                            self.ui.pushButton_scan_keithley.setEnabled(True)
                            self.ui.pushButton_pause_keithley.setEnabled(False)
                            self.ui.pushButton_clear_keithley.setEnabled(True)
                            self.ui.lineEdit_condition_keithley.setText('Scan complete.')
                            self.emit(SIGNAL("mpl_plot"))
                            self.ui.groupBox_save_keithley.setEnabled(True)
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
                        x_value.append(float(voltage))
                        x_plot = np.array(x_value)
                        x_plot = x_plot / self.voltage_scale[0]
                        current = self.inst.query('READ? "defbuffer1", READ')
                        y_value.append(float(current))
                        y_plot = np.array(y_value)
                        
                        if abs(max(y_plot)) >= 1:
                            self.current_scale = [1, "Amps"]
                        elif abs(max(y_plot)) >= 1E-3 and abs(max(y_plot)) < 1:
                            self.current_scale = [1E-3, "mAmps"]
                        elif abs(max(y_plot)) >= 1E-6 and abs(max(y_plot)) < 1E-3:
                            self.current_scale = [1E-6, "uAmps"]
                        elif abs(max(y_plot)) >= 1E-9 and abs(max(y_plot)) < 1E-6:
                            self.current_scale = [1E-9, "nAmps"]
                        elif abs(max(y_plot)) >= 1E-12 and abs(max(y_plot)) < 1E-9:
                            self.current_scale = [1E-12, "pAmps"]
                        self.ui.label_yunit_keithley.setText(self.current_scale[1])
                        self.ui.curvewidget_keithley.plot.set_titles("Keithely Voltage Source Measurement", "Voltage (" + self.voltage_scale[1] + ")", "Current (" + self.current_scale[1] + ")")
                        y_plot = y_plot / self.current_scale[0]
                        self.curve.set_data(x_plot, y_plot)
                        self.ui.label_yunit_keithley.setText(self.current_scale[1])
                        self.ui.lineEdit_condition_keithley.setText('Reading')
                        #time.sleep(self.time_step)
                        
                        end_time = time.time()
                        t_value.append(end_time - start_time)
                        t_plot = np.array(t_value)
                        if abs(max(t_plot)) < 300:
                            self.time_scale = [1, "Secs"]
                        elif abs(max(t_plot)) >= 300 and abs(max(t_plot)) < 18000:
                            self.time_scale = [60, "Mins"]
                        elif abs(max(y_plot)) > 1E-6 and abs(max(y_plot)) < 1E-3:
                            self.time_scale = [3600, "Hours"]
                        t_plot = t_plot / self.time_scale[0]
                        self.ui.curvewidget_ct_keithley.plot.set_titles("Keithely Voltage Source Current vs Time", "Time (" + self.time_scale[1] + ")", "Current (" + self.current_scale[1] + ")")
                        self.curve_ct.set_data(t_plot, y_plot)
                        self.ui.curvewidget_vt_keithley.plot.set_titles("Keithely Voltage Source Voltage vs Time", "Time (" + self.time_scale[1] + ")", "Voltage (" + self.voltage_scale[1] + ")")
                        self.curve_vt.set_data(t_plot, x_plot)
                        self.emit(SIGNAL("plot"), x_plot[len(x_plot) - 1], y_plot[len(y_plot) - 1], t_plot[len(t_plot) - 1])
                        self.ui.label_tunit_keithley.setText(self.time_scale[1])
                        item += 1
    
                    
                    else:
                        self.ui.lineEdit_condition_keithley.setText('Reading stoped.')
            self.inst.write("OUTP OFF")
        
    # Reset the analysis matplot widget
    def Reset_plot_analysis(self):
        self.ui.mplwidget_analysis.figure.clear()
        self.axes_analysis = self.ui.mplwidget_analysis.figure.add_subplot(111)
        
    def __del__(self):
        self.exiting = True
        self.wait()
        