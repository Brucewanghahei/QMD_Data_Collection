try:
    import visa
    VISA_MOD_AVAILABLE = True
    rm = visa.ResourceManager()
except:
    VISA_MOD_AVAILABLE = False

import sys
import os

import string
import numpy as np

import time
from datetime import datetime

from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

import subprocess

from Save import Save_Thread

class Lock_In_Sweep():
    def __init__ (self, main, ui):

        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.update_visa()

        self.collectDataThread = CollectData()
        self.save_thread = Save_Thread()
        
        main.connect(self.ui.pushButton_copy_LI, SIGNAL('clicked()'), self.Copy_LI_S)
        main.connect(self.ui.pushButtonSelectReadVisaLI_S, SIGNAL('clicked()'),self.select_ReadVisa)
        main.connect(self.ui.pushButtonSelectSweepVisaLI_S, SIGNAL('clicked()'), self.select_SweepVisa)
        main.connect(self.ui.pushButtonCloseReadVisaLI_S, SIGNAL('clicked()'), self.close_ReadVisa)
        main.connect(self.ui.pushButtonCloseSweepVisaLI_S, SIGNAL('clicked()'), self.close_SweepVisa)
        
        main.connect(self.ui.pushButtonStartLI_S, SIGNAL("clicked()"), self.start)
        main.connect(self.ui.pushButtonPauseLI_S, SIGNAL("clicked()"), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonStopLI_S, SIGNAL("clicked()"), self.stop)
        
        main.connect(self.collectDataThread, SIGNAL("Plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("StatPlot"), self.plot_Stats)
        main.connect(self.collectDataThread, SIGNAL("PreSave"), self.pre_save)
        
        main.connect(self.ui.pushButtonBrowseLI_S, SIGNAL("clicked()"), self.browse)
        main.connect(self.ui.pushButtonSelectFolderLI_S, SIGNAL("clicked()"), self.select_name)
        main.connect(self.ui.radioButtonCSV_LI_S, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.radioButtonTXT_LI_S, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.pushButtonSaveLI_S, SIGNAL("clicked()"), self.save)


        self.canvas_import_LI_S = FigureCanvas(self.ui.mplwidget_import_LI_S.figure)
        self.canvas_import_LI_S.setParent(self.ui.widgetLI_S)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_import_LI_S = NavigationToolbar(self.canvas_import_LI_S, self.ui.widgetLI_S)
        
        vbox_import_LI_S = QVBoxLayout()
        vbox_import_LI_S.addWidget(self.canvas_import_LI_S)
        vbox_import_LI_S.addWidget(self.mpl_toolbar_import_LI_S)
        self.ui.widgetLI_S.setLayout(vbox_import_LI_S)
        
        self.ui.mplwidget_import_LI_S = self.canvas_import_LI_S
        
        # Set up guiqwt plot
        self.curve_item = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidgetLI_S.plot.add_item(self.curve_item)
        self.ui.curvewidgetLI_S.plot.set_antialiasing(True)
        
        self.curve_item_STDEV = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidgetSTDEV_LI_S.plot.add_item(self.curve_item_STDEV)
        self.ui.curvewidgetSTDEV_LI_S.plot.set_antialiasing(True)
        
        self.curve_item_Mean = make.curve([], [], color = 'b', marker = "o")
        self.ui.curvewidgetMeanValue_LI_S.plot.add_item(self.curve_item_Mean)
        self.ui.curvewidgetMeanValue_LI_S.plot.set_antialiasing(True)
        
        self.ui.pushButtonStartLI_S.setEnabled(False)
        self.ui.pushButtonStopLI_S.setEnabled(False)
        self.ui.pushButtonPauseLI_S.setEnabled(False)
        self.ui.pushButtonClearLI_S.setEnabled(False)
        self.ui.pushButtonCloseReadVisaLI_S.setEnabled(False)
        self.ui.pushButtonCloseSweepVisaLI_S.setEnabled(False)
        
        self.SweepVisa_check = False
        self.ReadVisa_check = False
        

    # def Browse_LI_S(self):
    #     prev_dir = os.getcwd()
    #     fileDir = QFileDialog.getOpenFileName(None, 'Select File to Import', prev_dir, filter="Array Files (*.array)")
    #     if fileDir != '':
    #         file_list = str(fileDir).split('/')
    #         for i in range(0, len(file_list) - 1):
    #             global open_dir
    #             open_dir = ''
    #             if i < len(file_list) - 1:
    #                 open_dir += file_list[i] + '\\'
    #             elif i == len(file_list) - 1:
    #                 open_dir += file_list[i]
    #         fileDir.replace('/', '\\')        
    #     else:
    #         self.ui.lineEdit_condition_keithley.setText("Please choose valid file to import.")
    # 
    # def Import_LI_S(self):
    #     divider_found = True
    #     count = 0
    #     temp = 0
    #     self.Array = []
    #     x_value = []
    #     y_value = []
    #     
    #     fileDir = self.ui.lineEdit_directory_keithley.text()
    #     fp = open(fileDir)
    #     while True:
    #         if count == 5000:
    #             self.ui.lineEdit_condition_keithley.setText("Data not found in file. Please check it.")
    #             divider_found = False
    #             break
    #         line = fp.readline()
    #         line_list = line.split(',')
    #         if line_list[0].upper() == "Array Data".upper() + '\n':
    #             break
    #         count += 1
    #         
    #     if divider_found == True:
    #         line = fp.readline()
    #         while True:
    #             line = fp.readline().replace('\n', '')
    #             print 'line: ' + line
    #             if line == '':
    #                 break
    #             value = line.split(',')
    #             x_value.append(temp)
    #             x_value.append(temp + 1)
    #             y_value.append(value[1])
    #             y_value.append(value[1])
    #             self.Array.append(float(value[1]))
    #             temp += 1
    #             
    #         self.Plot_import(x_value, y_value)
    #         self.ui.lineEdit_condition_keithley.setText("File is imported correctly.")
    #         self.ui.groupBox_visa_keithley.setEnabled(True)
            
    def Copy_LI_S(self):
        Values = self.copyDataFunc()
        if Values != None:
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
        else:
            pass
            #self.ui.lineEdit_condition_keithley.setText('No valid array to copy.')
        
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import_LI_S.draw()
        self.ui.lineEditStatusLI_S.setText("The array has been copied")
    
    # Reset the import matplot widget
    def Reset_plot_import(self):
        self.ui.mplwidget_import_LI_S.figure.clear()
        self.axes_import = self.ui.mplwidget_import_LI_S.figure.add_subplot(111)
        
    def update_visa(self):
        try:
            visas = rm.list_resources()
        except:
            self.ui.lineEditStatusLI_S.setText("No visas are connected")
            
        self.ui.comboBoxReadVisaLI_S.clear()
        self.ui.comboBoxSweepVisaLI_S.clear()
        
        for i in visas:
            self.ui.comboBoxReadVisaLI_S.addItem(i)
            self.ui.comboBoxSweepVisaLI_S.addItem(i)
            
    def select_ReadVisa(self):
        valid = False
        
        ReadVisa = str(self.ui.comboBoxReadVisaLI_S.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        
        inst1 = rm.open_resource(ReadVisa)
        
        try:
            valid = self.check_ReadVisa(inst1)
        except:
            self.ui.lineEditStatusLI_S.setText("Error with Read visa")
            
        if valid == True:
            self.ReadVisa = inst1
            self.ui.labelReadVisaLI_S.setText(str(self.ReadVisa.ask('*IDN?')))
            self.ui.pushButtonCloseReadVisaLI_S.setEnabled(True)
            self.ui.lineEditStatusLI_S.setText("There are no errors")
            self.ReadVisa_check = True
        else:
            self.pushButtonStartLI_S.setEnabled(False)
            self.ui.labelReadVisaLI_S.setText("None")
            self.ui.labelSweepVisaLI_S.setText("None")
            self.ui.lineEditStatusLI_S.setText("There is an error with the visas")
            
        if self.SweepVisa_check == True:
            self.ui.pushButtonStartLI_S.setEnabled(True)
        else:
            self.ui.lineEditStatusLI_S.setText('Please choose other visa to start')
        
    def select_SweepVisa(self):
        valid = False
        SweepVisa = str(self.ui.comboBoxSweepVisaLI_S.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst2 = rm.open_resource(SweepVisa)
        
        try:
            valid = self.check_SweepVisa(inst2)
        except:
            self.ui.lineEditStatusLI_S.setText("Error with the Sweep visa")
            
        if valid == True:
            self.SweepVisa = inst2
            self.ui.labelSweepVisaLI_S.setText(str(self.SweepVisa.ask('*IDN?')))
            self.ui.pushButtonCloseSweepVisaLI_S.setEnabled(True)
            self.ui.lineEditStatusLI_S.setText("There are no errors")
            self.SweepVisa_check = True
        else:
            self.ui.pushButtonStartLI_S.setEnabled(False)
            self.ui.lineEditStatusLI_S.setText("Error with the Sweep visa")
            
        if self.ReadVisa_check == True:
            self.ui.pushButtonStartLI_S.setEnabled(True)
        else:
            self.ui.lineEditStatusLI_S.setText('Please choose other visa to start')
        
    def check_ReadVisa(self, inst1):
        try:
            inst1.ask('*IDN?')
            valid = True
        except:
            valid = False
        return valid
    
    def check_SweepVisa(self, inst2):
        try:
            inst2.ask('*IDN?')
            valid = True
        except:
            valid = False
        
        return valid
    
    def close_ReadVisa(self):
        self.ReadVisa.close()
        self.ui.labelReadVisaLI_S.setText("")
        self.ui.lineEditStatusLI_S.setText("The Read Visa has been closed")
        
    def close_SweepVisa(self):
        self.SweepVisa.close()
        self.ui.labelSweepVisaLI_S.setText("")
        self.ui.lineEditStatusLI_S.setText("The Sweep Visa has been closed")

    def start(self):
        self.ui.pushButtonStartLI_S.setDisabled(True)
        self.ui.pushButtonPauseLI_S.setEnabled(True)
        self.ui.pushButtonStopLI_S.setEnabled(True)
        self.ui.tabWidgetLockIn_S.setCurrentIndex(1)
        
        
        if self.Array[0] < 200:
            self.SweepVisa.write('FRNG 2')
            self.SweepVisa.write('FREQ' + ' ' + str(self.Array[0]))
        else:
            pass
        time.sleep(1)
        self.ReadVisa.ask('MEAS:VOLT?')

            
        if int(self.SweepVisa.ask('SENS?')) < 3:
            self.sens_unit = 'nV'
            self.sens_magn = 1E-9
        elif int(self.SweepVisa.ask('Sens?')) >= 3 and int(self.SweepVisa.ask('SENS?')) < 12:
            self.sens_unit = 'uV'
            self.sens_magn = 1E-6
        else:
            self.sens_unit = 'mV'
            self.sens_magn = 1E-3
            
        self.magnitude = [self.sens_magn, self.sens_unit]

        self.collectDataThread.input(self.ui, self.curve_item,self.curve_item_STDEV, self.curve_item_Mean, self.ReadVisa, self.SweepVisa, self.Array, self.magnitude)
        self.ui.lineEditStatusLI_S.setText("Running...")
        
    def plotData(self, voltage, magnitude):
        self.ui.lineEditSTDEV_LI_S.setText(str(round(np.std(voltage/self.magnitude[0]),10)) + " " + magnitude[1])
        self.ui.lineEditMaxMinLI_S.setText(str(round(np.max(voltage/self.magnitude[0])- np.min(voltage/self.magnitude[0]), 10)) + " " + magnitude[1])
        self.ui.lineEditMeanValueLI_S.setText(str(np.mean(voltage/self.magnitude[0])) + " " + magnitude[1])
        self.curve_item.plot().replot()
        self.ui.curvewidgetLI_S.plot.do_autoscale()
        
    def plot_Stats(self):
        self.curve_item_STDEV.plot().replot()
        self.ui.curvewidgetSTDEV_LI_S.plot.do_autoscale()
        self.curve_item_Mean.plot().replot()
        self.ui.curvewidgetMeanValue_LI_S.plot.do_autoscale()
        
    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonStartLI_S.setEnabled(True)
        self.ui.pushButtonStopLI_S.setEnabled(False)
        self.ui.pushButtonPauseLI_S.setEnabled(False)
        
    def pre_save(self, Freq, Mean, Stdev, StepPoints):
        self.Freq = Freq
        self.Mean = Mean
        self.Stdev = Stdev
        self.StepPoints = StepPoints
    
        
    def browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select The GoogleDrive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEditDirectoryLI_S.setText(file_dir)
        self.directory = ''
        
    def select_name(self):
        file_list= []
        file_list = str(self.ui.lineEditDirectoryLI_S.text()).split('\\')
        for i in range(0, len(file_list)):
            self.directory += file_list[i] + '\\'
        namefolder = str(self.ui.comboBoxFoldersLI_S.currentText())
        if namefolder == 'None':
            self.ui.lineEditStatusLI_S.setText('Please Choose A Folder To Save To.')
        else:
            #Sets the name of the file to current date and time by default
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.directory += namefolder + "\Data" + '\\' + date
            self.current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            self.date_and_time = date + ' ' + self.current_time
            self.file_name = (self.date_and_time)
            print self.directory
            
    def save_type(self):
        if self.ui.radioButtonCSV_LI_S.isChecked() == True:
            self.type = '.csv'
            self.divide = ','
        elif self.ui.radioButtonTXT_LI_S.isChecked() == True:
            self.type = '.txt'
            self.divide = '\t'
            
    def save_name(self):
        if self.ui.radioButtonDateTime_LI_S.isChecked():
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            date_and_time = date + ' ' + current_time
            self.file_name = str(date_and_time)
        elif self.ui.radioButtonCustomName_LI_S.isChecked():
            self.file_name = str(self.ui.lineEditCustomLI_S.text())
            
    def save(self):
        if self.ui.radioButtonCustomName_LI_S.isChecked() and self.ui.lineEditCustomLI_S.text() == ' ':
            self.ui.lineEditStatusLI_S.setText('Please Enter A Custom File Name')
        else:
            self.save_type()
            self.save_name()
            
        comments = []
        file_info = []
        parameters = []
        units = []
        data = []
        divider = 'Collected Data'
        
        parameters.append('Frequency')
        units.append('Hz')
        data.append(self.Freq)
        
        parameters.append('Points Collected')
        units.append('1')
        data.append(self.StepPoints)
        
        parameters.append('Standard Deviation')
        units.append(self.magnitude[1])
        data.append(self.Stdev)
        
        parameters.append('Mean Value')
        units.append(self.magnitude[1])
        data.append(self.Mean)
        
        file_info.append(self.file_name)
        file_info.append(self.type)
        file_info.append(self.divide)
        file_info.append(divider)
        file_info.append(self.directory)
        
        self.save_thread.input(comments, parameters, units, data, file_info)
        self.ui.lineEditStatusLI_S.setText("File has been saved")
        
        
        
class CollectData(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, curve, curve_stdev, curve_mean, ReadVisa, SweepVisa, Array, magnitude):
        self.ui = ui
        self.curve = curve
        self.curve_stdev = curve_stdev
        self.curve_mean = curve_mean
        self.ReadVisa = ReadVisa
        self.SweepVisa = SweepVisa
        self.Array = Array
        self.pauseLoop = False
        self.start()
        self.i = 0
        self.j = 0
        self.Freq = np.array([], dtype = float)
        self.Voltage = np.array([], dtype = float)
        self.steps = np.array([], dtype = float)
        self.Stdev = np.array([], dtype = float)
        self.Mean = np.array([], dtype = float)
        self.StepPoints = np.array([], dtype = float)
        self.magnitude = magnitude
        self.sens_conversion= ['100','200','500','1','2','5','10','20','50','100','200','500','1','2','5','10','20','50','100','200','500']
        try:
            self.sens = self.sens_conversion[int(self.SweepVisa.ask('SENS?'))]
        except:
            pass
    

    def run(self):
        self.points = int(self.ui.lineEditPointsPerStepLI_S.text())
        while True:
            if self.pauseLoop == False:
                self.timestep = float(self.ui.lineEditTimestep_LI_S.text())
                if self.i == 0:
                    time.sleep(1)
                    self.ReadVisa.ask('MEAS:VOLT?')
                    self.Freq = np.append(self.Freq, self.Array[self.i])
                    for j in range(0, self.points):
                        self.reading = float(self.ReadVisa.ask('MEAS:VOLT?'))*float(self.sens)*self.magnitude[0]/10
                        # if j > 1:
                        #     self.Voltage = np.append(self.Voltage, self.reading)
                        #     self.steps = np.append(self.steps, j-1)
                        # else:
                        #     self.ReadVisa.ask('READ?')
                        self.Voltage = np.append(self.Voltage, self.reading)
                        self.steps = np.append(self.steps, j+1)
                        self.curve.set_data(self.steps, self.Voltage/self.magnitude[0])
                        voltage = self.Voltage
                        self.ui.curvewidgetLI_S.plot.set_titles('Voltage vs. Step at' + " " + str(self.Freq[self.i]) + " " + "Hz", 'Steps', 'Voltage (' + self.magnitude[1] + ')')
                        time.sleep(self.timestep)
                        self.ui.labelLastReadingLI_S.setText(str(round(self.reading/self.magnitude[0], 10)) + " " + self.magnitude[1])
                        magnitude = self.magnitude
                        self.emit(SIGNAL("Plot"), voltage, magnitude)
                    print len(self.Voltage)
                    self.i +=1
                    #self.pause()
                    self.append_stats()

                elif self.i != 0 or self.i == len(self.Array):
                    self.Voltage = np.array([], dtype = float)
                    self.steps = np.array([], dtype = float)
                    self.SweepVisa.write('FREQ' + ' ' + str(self.Array[self.i]))
                    time.sleep(1)
                    self.ReadVisa.ask('READ?')
                    self.Freq = np.append(self.Freq, self.Array[self.i])
                    for j in range(0,self.points):
                        self.reading = float(self.ReadVisa.ask('READ?'))*float(self.sens)*self.magnitude[0]/10
                        self.Voltage = np.append(self.Voltage, self.reading)
                        self.steps = np.append(self.steps, j+1)
                        self.curve.set_data(self.steps, self.Voltage/self.magnitude[0])
                        voltage = self.Voltage
                        self.ui.curvewidgetLI_S.plot.set_titles('Voltage vs. Step at' + " " + str(self.Freq[self.i]) + " " + "Hz", 'Steps', 'Voltage (' + self.magnitude[1] + ')')
                        time.sleep(self.timestep)
                        self.ui.labelLastReadingLI_S.setText(str(round(self.reading/self.magnitude[0], 10)) + " " + self.magnitude[1])
                        magnitude = self.magnitude
                        self.emit(SIGNAL("Plot"), voltage, magnitude)
                    self.i +=1
                    self.j += 1
                    if self.Array[self.j] == 200:
                        self.SweepVisa.write('FRNG 3')
                        self.SweepVisa.write('FREQ' + ' ' + str(self.Array[self.j]))
                        self.ReadVisa.ask('READ?')
                        self.j = self.j - 1
                    elif self.Array[self.j] == 2000:
                        self.SweepVisa.write('FRNG 4')
                        self.SweepVisa.write('FREQ' + ' ' + str(self.Array[self.j]))
                        self.ReadVisa.ask('READ?')
                        self.j = self.j -1
                    else:
                        pass
                    #self.pause()
                    self.append_stats()
                elif self.i > len(self.Array):
                    self.pauseLoop = True
                    self.ui.lineEditStatus.setText("Collection Is Finished")
                    break
                else:
                    pass
            else:
                pass
                    
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            self.ui.lineEditStatusLI_S.setText("Running")
            self.points = int(self.ui.lineEditPointsPerStepLI_S.text())
            self.ui.tabWidgetLockIn_S.setCurrentIndex(1)
        else:
            self.pauseLoop = True
            self.ui.lineEditStatusLI_S.setText("Paused")
            self.ui.pushButtonPauseLI_S.setText("Continue")
            
    def append_stats(self):
        self.Stdev = np.append(self.Stdev, round(np.std(self.Voltage/self.magnitude[0]), 10))
        self.Mean = np.append(self.Mean, round(np.mean(self.Voltage/self.magnitude[0]),10))
        self.StepPoints = np.append(self.StepPoints, float(self.ui.lineEditPointsPerStepLI_S.text()))
        self.ui.curvewidgetMeanValue_LI_S.plot.set_titles('Mean Value vs. Frequency', 'Frequency (Hz)', 'Mean Value (' + self.magnitude[1] + ')')
        self.ui.curvewidgetSTDEV_LI_S.plot.set_titles('Standard Deviation vs. Frequency', 'Frequency (Hz)', 'Standard Deviation (' + self.magnitude[1] + ')')
        self.curve_stdev.set_data(self.Freq, self.Stdev)
        self.curve_mean.set_data(self.Freq, self.Mean)
        
        Freq = self.Freq
        Mean = self.Mean
        Stdev = self.Stdev
        StepPoints = self.StepPoints
        self.emit(SIGNAL("StatPlot"))
        self.emit(SIGNAL("PreSave"), Freq, Mean, Stdev, StepPoints)
        print self.Freq
        print self.Stdev
        print self.Mean