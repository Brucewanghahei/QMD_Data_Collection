# Import numpy library
import numpy
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

class Agilent_Yokogawa():
    
    def __init__(self, ui):
        #QWidget.__init__(self, parent)
        self.ui = ui
        
        self.rm = visa.ResourceManager()
        self.update_visa()
        
        self.ui.startButton.setDisabled(True)
        self.ui.closeVisaButton0.setDisabled(True)
        self.ui.closeVisaButton1.setDisabled(True)
        
        self.target = None
        self.I = None
        self.DI = None
        
        self.current = []
        self.voltage = []
        self.drawing = [0]
        self.array = []
        self.temp = []
        self.meter = []
        self.count = 0
        self.track = 0
        self.time = [0]
        self.range = [0]
        self.tik = 0
        
        self.Array = []
        
        self.timeStep = .5
        self.ui.timeStepValue.setText(str(self.timeStep))
        self.ui.defaultFile.setChecked(True)
        
        self.action_timer = QTimer()
        #self.connect(self.action_timer, SIGNAL("timeout()"), self.action)
        
        #self.reset_plot()
        
        self.directory = 'C:\\Users\\QMDla\\Google Drive\\03 User Accounts'
        self.update_folders()
        self.ui.directory.setText(self.directory)
        
    def Browse_ay(self):
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

    def Import_ay(self):
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
                x_value.append(temp + 1 - 0.0001)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array.append(value[1])
                temp += 1
                
            
            self.Plot_import(x_value, y_value)
            #self.ui.lineEdit_condition_ay.setText("File is imported correctly.")
            #self.ui.groupBox_visa_ay.setEnabled(True)
            
    def Copy_ay(self, Values):
        x_value = []
        y_value = []      
        item = 0
        for i in range(0, len(Values)):
            for j in range(0, len(Values[i])):
                x_value.append(item)
                x_value.append(item + 1)
                y_value.append(Values[i][j])
                y_value.append(Values[i][j])
                self.Array.append(Values[i][j])
                item += 1
        self.Plot_import(x_value, y_value)
        #self.ui.lineEdit_directory_ay.setText('From Array Builder Tab.')
        #self.ui.groupBox_visa_ay.setEnabled(True)
        
    def Plot_import(self, x, y):
        print 1
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import_ay.draw()
    
    def Plot_data(self, voltage, current):
        self.ui.label_yvalue_keithley.setText(str(format(float(current), '.3f')))
        self.ui.label_xvalue_keithley.setText(str(format(float(voltage), '.3f')))
        self.curve_item.plot().replot()
        
    def Reset_plot_import(self):
        self.ui.mplwidget_import_ay.figure.clear()
        self.axes_import = self.ui.mplwidget_import_ay.figure.add_subplot(111)

    def Check_visa(self, inst):
        try:
            inst.ask("*IDN?")
            valid = True
        except:
            valid = False
        return valid
    
    def update_visa(self):
        
        try:
            visas = self.rm.list_resources()
        except:
            visas = ''
        
        current_visa0 = self.ui.visa0.text()
        current_visa1 = self.ui.visa1.text()
        
        check_current0 = False
        check_current1 = False
        
        self.ui.selectVisa0.clear()
        self.ui.selectVisa1.clear()
        
        for each_visa in visas:
            if current_visa0 == each_visa:
                check_current0 = True
            self.ui.selectVisa0.addItem(each_visa)
            
        for each_visa in visas:
            if current_visa1 == each_visa:
                check_current1 = True
            self.ui.selectVisa1.addItem(each_visa)
        
        if check_current0 == False:
            self.ui.visa0.setText("None")
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton0.setDisabled(True)
        
        if check_current1 == False:
            self.ui.visa1.setText("None")
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton1.setDisabled(True)
    

    def select_visa(self):
        visa_chosen0 = str(self.ui.selectVisa0.currentText())
        visa_chosen1 = str(self.ui.selectVisa1.currentText())

        try:
            inst0 = self.rm.open_resource(visa_chosen0)
            inst1 = self.rm.open_resource(visa_chosen1)
            self.ui.output.setText(inst0.ask('*IDN?') + inst1.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa0.setText(visa_chosen0)
            self.ui.visa1.setText(visa_chosen1)
            self.ui.error.setText("None")
            self.visa_chosen0 = inst0
            self.visa_chosen1 = inst1
            self.ui.startButton.setDisabled(False)
            self.ui.stopButton.setDisabled(False)
            self.ui.closeVisaButton0.setDisabled(False)
            self.ui.closeVisaButton1.setDisabled(False)
            self.ui.drawButton.setDisabled(False)

            print self.visa_chosen0.write('SOUR:FUNC CURR')
            print self.visa_chosen0.write('SOUR:PROT:VOLT 30')

        elif valid == False:
            self.ui.error.setText("Invalid Visa Port.")
            self.ui.visa0.setText("None")
            self.ui.visa1.setText("None")
            self.visa_chosen0 = False
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton0.setDisabled(True)
            self.ui.closeVisaButton1.setDisabled(True)
    
    def close_visa0(self):
        try:
            self.ui.output.setText(self.visa_chosen0.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa0.setText('None')
            self.ui.error.setText("None")
            self.visa_chosen0.close()
        
        elif valid == False:
            self.ui.error.setText("No visa connected.")
            self.ui.visa0.setText("None")
            
        self.visa_chosen0 = False
        self.ui.startButton.setDisabled(True)
        self.ui.closeVisaButton0.setDisabled(True)
        
    def close_visa1(self):
        try:
            self.ui.output.setText(self.visa_chosen1.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa1.setText('None')
            self.ui.error.setText("None")
            self.visa_chosen1.close()
        
        elif valid == False:
            self.ui.error.setText("No visa connected.")
            self.ui.visa1.setText("None")
        
        self.visa_chosen1 = False
        self.ui.startButton.setDisabled(True)
        self.ui.closeVisaButton1.setDisabled(True)

    def ranger(self):
        self.range.append(self.tik)
        self.tik = self.tik + 1
        self.range.append(self.tik)
        return self.range
    
    def start(self):
        command = str(self.ui.input.toPlainText())
        if command != "":
            print self.visa_chosen0.write('OUTP ON')
            self.V = float(self.visa_chosen1.query('MEAS:VOLT?'))
            print self.V
            try:                    
                self.DV = float(self.ui.stepValue.text())
            except:
                self.DV = 0
            
            try:
                self.timeStep = float(self.ui.timeStepValue.text())
                self.action_timer.start(1000.0*self.timeStep)
            except:
                self.ui.error.setText("There is a problem with the time step.")   # There is no command to be sent. Thus nothing is done except for an error being displayed informing the user.
        else:
            self.ui.error.setText("No command given.")
            
    def action(self):
        if self.timeStep <= 0:
            self.ui.error.setText("Enter a positive voltage step value.")
            self.action_timer.stop()
        else:
            if self.track < len(self.temp):
                print self.visa_chosen0.write('SOUR:LEV:AUTO ' + str(self.temp[self.track]/1000000))
                vol = float(self.visa_chosen1.query('MEAS:VOLT?'))
                print vol
                self.array.append(vol)
                self.array.append(vol)
                self.voltage.append(vol)
                self.time.append(datetime.datetime.now())
                self.time.append(datetime.datetime.now())
                self.meter.append(self.count)
                self.count = self.count + 1
                self.meter.append(self.count)
                self.ui.output.setText(str(self.array))
                self.ui.voltage.setText(str(self.array[len(self.array)-1]))
                
                self.reset_plot()
                self.axes0.plot(self.range, self.drawing)
                self.axes1.plot(self.meter, self.array)
                self.ui.plot.draw()
                
                self.track = self.track + 1
            else:
                print self.visa_chosen1.write('OUTP OFF')
                self.action_timer.stop()
                self.current.append(self.temp)
                self.temp = []
                self.track = 0
    
    
    '''def reset_plot(self):
        self.ui.plot.figure.clear()
        self.axes0 = self.ui.plot.figure.add_subplot(211)
        self.axes1 = self.ui.plot.figure.add_subplot(212)
        
        self.axes0.set_title("Current vs. Steps")
        self.axes0.set_ylabel("Current")
        
        self.axes1.set_title("Voltage vs. Steps")
        self.axes1.set_xlabel("Steps")
        self.axes1.set_ylabel("Voltage")'''
    
    
    def browse(self):
        prev_dir = 'C:\\Users\\QMDla\\Google Drive\\03 User Accounts'
        try:   
            self.directory = QFileDialog.getExistingDirectory(self, 'Select Google Drive File to Open:', prev_dir)
        except ValueError:
            self.directory = False
        if self.directory != '' and self.directory != False:
            self.file_list = str(self.directory).split('/')
            for i in range(0, len(self.file_list) - 1):
                if i < len(self.file_list) - 1:
                    self.open_dir += self.file_list[i] + '\\'
                elif i == len(self.file_list) - 1:
                    self.open_dir += self.file_list[i]
            self.directory.replace('/', '\\')
            self.ui.directory.setText(self.directory)
            self.ui.output.setText('Folder reached.')
            #self.ui.directory.setText('Open Google Drive User Folder')
        else:
            self.directory = False
            self.ui.directory.setText('None')
            self.ui.output.setText('Failed to reach folder.')
        self.update_folders()
    
    def update_folders(self):
        self.ui.folderName.clear()
        self.ui.folderName.addItem('None')
        if not self.directory:
            return
        else:
            self.directories = numpy.asarray(os.listdir(self.directory))
            for folder in self.directories:
                self.ui.folderName.addItem(folder)
    
    def select_type(self):
        if self.ui.csvRadio.isChecked():
            self.type = '.csv'
            self.divide = ','
            self.form = ''
        elif self.ui.txtRadio.isChecked():
            self.type = '.txt'
            self.divide = '\t'
            self.form = '                     '
        else:
            self.type = False
    
    def select_name(self):
        now = datetime.datetime.now()
        self.date = '%s-%s-%s' % (now.year, now.month, now.day)
        self.current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
        self.date_and_time = self.date + ' ' + self.current_time
        if self.ui.defaultFile.isChecked():
            try:
                self.file = self.date_and_time
            except ValueError:
                self.file = False  
        elif self.ui.customFile.isChecked():
            try:
                self.file = str(self.ui.file.text())
            except ValueError:
                self.file = False
    
    def select_folder(self):
        #self.update_folders()
        try:
            self.folder_name = str(self.ui.folderName.currentText())
        except ValueError:
            self.folder_name = False
        if self.folder_name == 'None' or self.folder_name == '' :
            self.folder_name = False
            #self.directory = str(self.ui.directory.setText())

    
    def save(self):
        self.select_type()
        if not self.type:
            self.ui.output.setText('Please select a valid file type.')
            return
        self.select_name()
        self.select_folder()
        
        if self.file == '':
            self.ui.output.setText('Please enter a valid file name.')
            return
        else:
            self.name = self.file + self.type
            
            if not self.directory:
                self.path = self.name
            else:
                if self.folder_name == False:
                    self.path = self.ui.directory.text() + '\\' + self.name
                else:
                    self.path = self.directory + '\\' + self.folder_name + '\\' + 'Data'
                    # Create a folder at this address
                    if not os.path.isdir(self.path):
                        os.makedirs(self.path)
                    self.path = self.path + '\\' + self.date
                    # Create a folder at this address
                    if not os.path.isdir(self.path):
                        os.makedirs(self.path)
                    self.path = self.path + '\\' + 'Keithley Manual Scan'
                    # Create a folder at this address
                    if not os.path.isdir(self.path):
                        os.makedirs(self.path)
                    self.path = self.path + '\\' + self.name
                    
            f = open(self.path, 'w')
            
            f.write('Name' + self.divide + self.name + '\n')
            f.write('Time' + self.divide + str(self.date_and_time) + '\n')
            f.write('\n')
            
            f.write('Label' + self.divide + 'Parameter' + self.divide + 'Unit' + '\n')
            if len(self.voltage) >= 1:
                f.write('Start Voltage' + self.divide + str(self.voltage[0]) + self.divide + 'mV' + '\n')
                f.write('End Voltage' + self.divide + str(self.voltage[len(self.voltage) - 1]) + self.divide + 'mV' + '\n')
                f.write('Start Current' + self.divide + str(self.current[0]) + self.divide + 'mV' + '\n')
                f.write('End Current' + self.divide + str(self.current[len(self.current) - 1]) + self.divide + 'mV' + '\n')
                f.write('Final Time Step' + self.divide + str(self.ui.timeStepValue.text()) + self.divide + 's' + '\n')
                f.write('\n')
                
                f.write('Collected data' + '\n')
                f.write('Time' + self.divide + 'Voltage' + self.divide + 'Current' + '\n')
                f.write('s' + self.divide + 'Volts' + self.divide + 'Amps' + '\n')
                
                for i in range(0, len(self.voltage)):
                    data = str(self.time[i]) + self.divide +  str(self.voltage[i]) + self.divide + str(self.current[i]) + '\n'
                    f.write(data)
            else:
                f.write('No Data')
           
        f.close()
        self.ui.output.setText("Your data has been successfully saved to: " + self.path)
        
'''class Collect_data(QThread):
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
        if self.ui.radioButton_mv_keithley.isChecked():
            self.voltage_scale = [1E-3, 'mVolts']
        elif self.ui.radioButton_uv_keithley.isChecked():
            self.voltage_scale = [1E-6, 'mVolts']
        if self.ui.radioButton_na_keithley.isChecked():
            self.current_scale = [1E-9, 'nAmps']
        elif self.ui.radioButton_ua_keithley.isChecked():
            self.current_scale = [1E-6, 'uAmps']
        elif self.ui.radioButton_ma_keithley.isChecked():
            self.current_scale = [1E-3, 'mAmps']
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
        if self.go_on:
            self.go_on = False
        self.ui.pushButton_scan_keithley.setEnabled(True)
        self.ui.pushButton_pause_keithley.setEnabled(False)
        self.ui.pushButton_clear_keithley.setEnabled(True)
        
    def run(self):
        x_value = []
        y_value = []
        item = 0
        
        if self.ui.radioButton_voltage_keithley.isChecked():
            self.Array = self.Array * float(self.voltage_scale[0])
            self.ui.label_yname_keithley.setText('Current:')
            self.ui.label_xname_keithley.setText('Voltage:')
            self.ui.label_yunit_keithley.setText('nA')
            self.ui.label_xunit_keithley.setText('mV')
            while True:
                if self.go_on:
                    if item == len(self.Array):
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
                    
                    self.inst.write("SOUR:VOLT " + str(self.Array[item]))
                    self.inst.write('SENS:CURR:RSEN ' + 'OFF')
                    self.inst.write('OUTP ON')
                    
                    voltage = self.inst.query('READ? "defbuffer1", SOUR')
                    x_value.append(float(voltage))
                    current = self.inst.query('READ? "defbuffer1", READ')
                    y_value.append(float(current))
                    self.curve.set_data(x_value, y_value)
                    self.emit(SIGNAL("plot"), voltage, current)
                    print "x_value: " + x_value
                    print "y_value: " + y_value
                    time.sleep(self.time_step)
                    item += 1
                    
            self.inst.write("OUTP OFF")
        elif self.ui.radioButton_current_keithley.isChecked():
            self.Array = self.Array * float(self.current_scale[0])
            self.ui.label_yname_keithley.setText('Voltage:')
            self.ui.label_xname_keithley.setText('Current:')
        
                
    def __del__(self):
        self.exiting = True
        self.wait()'''    