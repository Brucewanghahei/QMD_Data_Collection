# Import numpy library
import numpy
import os
import sys
import datetime
import visa
import math
import time

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

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
    
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.collectDataThread = CollectData()
        #self.save_thread = Save_Thread()
        
        main.connect(self.ui.startButton, SIGNAL("clicked()"), self.start)
        main.connect(self.ui.stopButton, SIGNAL("clicked()"), self.stop)
        #self.connect(self.action_timer, SIGNAL("timeout()"), self.Agilent_Yokogawa_programs.action)

        main.connect(self.ui.pushButton_browse_ay, SIGNAL('clicked()'), self.Browse_ay)
        main.connect(self.ui.pushButton_import_ay, SIGNAL('clicked()'), self.Import_ay)
        main.connect(self.ui.pushButton_copy_ay, SIGNAL('clicked()'), self.Copy_ay)
        main.connect(self.ui.selectVisaButton, SIGNAL("clicked()"), self.select_visa)
        main.connect(self.ui.updateVisaButton, SIGNAL("clicked()"), self.update_visa)
        main.connect(self.ui.closeVisaButton0, SIGNAL("clicked()"), self.close_visa0)
        main.connect(self.ui.closeVisaButton1, SIGNAL("clicked()"), self.close_visa1)
        main.connect(self.collectDataThread, SIGNAL("plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("analyse"), self.analyse)
        
        main.connect(self.ui.browseButton, SIGNAL("clicked()"), self.browse)
        main.connect(self.ui.saveButton, SIGNAL("clicked()"), self.save)
        
        self.rm = visa.ResourceManager()
        self.update_visa()
        
        self.ui.startButton.setDisabled(True)
        self.ui.closeVisaButton0.setDisabled(True)
        self.ui.closeVisaButton1.setDisabled(True)
        
        self.current = []
        self.voltage = []
        self.array = []
        self.temp = []
        self.count = 0
        self.time = [0]
        self.range = [0]
        self.tik = 0
        self.Array = []
        self.frontX = 0.0
        self.frontY = 0.0
        self.backX = 0.0
        self.backY = 0.0
        self.x_plot = [-1,1]
        self.y_plot = [-1,1]
        
        self.timeStep = .1
        self.ui.timeStepValue.setText(str(self.timeStep))
        self.ui.defaultFile.setChecked(True)
        
        self.action_timer = QTimer()


        # Define the QThread class to a variable in the QMainWindow class
        self.collectDataThread = CollectData()

        # Sets up Current v. Voltage guiqwt plot
        self.curve_item = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_scanPlot_ay.plot.add_item(self.curve_item)
        self.ui.curvewidget_scanPlot_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current (uA)", "Voltage (V)")
        
        # Sets up Voltage v. Time Step guiqwt plot
        self.curve_item_vt = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_vt_ay.plot.add_item(self.curve_item_vt)
        self.ui.curvewidget_vt_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time Step", "Time Step", "Voltage (V)")
        
         # Sets up Current v. Time Step guiqwt plot
        self.curve_item_ct = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_ct_ay.plot.add_item(self.curve_item_ct)
        self.ui.curvewidget_ct_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Time Step", "Time Step", "Current (uA)")
        
        self.ui.stopButton.setEnabled(False)
        self.ui.startButton.setEnabled(False)
        
        #save stuff
        self.directory = 'C:\\Users'
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
                x_value.append(temp + 1)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array.append(value[1])
                temp += 1
                
            
            self.Plot_import(x_value, y_value)
            self.ui.output.setText("File is imported correctly.")
            #self.ui.groupBox_visa_ay.setEnabled(True)
            
    def Copy_ay(self):
        Values = self.copyDataFunc()
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
        self.ui.output.setText('From Array Builder Tab.')
        #self.ui.groupBox_visa_ay.setEnabled(True)
        
    '''def Copy_ay(self):
        if Values != None:
            self.ui.output.setText('Array has been copied and plotted.')
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
            #self.ui.groupBox_visa_keithley.setEnabled(True)
            #self.ui.groupBox_xvalue_keithley.setEnabled(True)'''
        
    def Plot_import(self, x, y):
        self.Reset_plot_import()
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import_ay.draw()
        
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
            #self.ui.drawButton.setDisabled(False)

            self.visa_chosen0.write('SOUR:FUNC CURR')
            self.visa_chosen0.write('SOUR:PROT:VOLT 30')

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
        self.visa_chosen0.write('OUTP ON')
        self.timeStep = float(self.ui.timeStepValue.text())
        self.collectDataThread.input(self.ui, self.visa_chosen0, self.visa_chosen1, self.Array, self.timeStep, self.curve_item, self.curve_item_vt, self.curve_item_ct, [], [], [])
        self.ui.startButton.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        #self.ui.pushButtonPause.setEnabled(True)
        self.ui.output.setText("Running")
        #self.ui.pushButtonPause.setText("Pause")
        
    def plotData(self):
        self.ui.curvewidget_scanPlot_ay.plot.do_autoscale()
        self.curve_item.plot().replot()
        self.ui.curvewidget_vt_ay.plot.do_autoscale()
        self.curve_item_vt.plot().replot()
        self.ui.curvewidget_ct_ay.plot.do_autoscale()
        self.curve_item_ct.plot().replot()
    
    def analyse(self, x_plot, y_plot):
        self.x_plot = x_plot
        self.y_plot = y_plot
        self.ui.mplwidget_analysis.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.axes_analysis_ay.set_title('Voltage v. Current Measurement')
        self.axes_analysis_ay.set_ylabel("Voltage")
        self.axes_analysis_ay.set_xlabel("Current")
        self.axes_analysis_ay.plot(x_plot, y_plot, marker = '.', linestyle = '-')
        self.ui.mplwidget_analysis_ay.draw()
        self.frontX = self.x_plot[0]
        self.frontY = self.y_plot[0]
        #self.ui.mplwidget_ct_analysis_ay.draw()
        #self.ui.mplwidget_vt_analysis_ay.draw()
    
    def slope(self, event=None):
        self.backX = self.frontX 
        self.backY = self.frontY
        self.frontX = event.xdata
        self.frontY = event.ydata
        
        index= min(range(len(self.x_plot)), key=lambda i: math.sqrt((self.x_plot[i]-self.frontX)**2+(self.y_plot[i]-self.frontY)**2))
        #index= min(range(len(self.y_plot)), key=lambda i: abs(self.y_plot[i]-self.frontY))
        
        #index = xindex*(abs(self.y_plot[yindex]-self.frontY) >= abs(self.x_plot[xindex]-self.frontX)) + yindex*(abs(self.x_plot[xindex]-self.frontX) > abs(self.y_plot[yindex]-self.frontY))
        
        self.frontX = self.x_plot[index]
        self.frontY = self.y_plot[index]
        
        try:
            slope = (self.frontY-self.backY)/(self.frontX-self.backX)
        except:
            slope = "none"
        
        self.ui.output.setText("Resistance: " + str(slope))
        
        x = [self.backX, self.frontX]
        y = [self.backY, self.frontY]
        
        self.ui.mplwidget_analysis_ay.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.axes_analysis_ay.set_title('Voltage v. Current Measurement')
        self.axes_analysis_ay.set_ylabel("Voltage")
        self.axes_analysis_ay.set_xlabel("Current")
        self.axes_analysis_ay.plot(self.x_plot, self.y_plot, 'b.-', x, y, 'r')
        self.ui.mplwidget_analysis_ay.draw()
        
    
    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        #self.ui.pushButtonPause.setEnabled(False)
        self.ui.output.setText("Stopped")
        #self.ui.pushButtonPause.setText("Pause")
    
    def browse(self):
        prev_dir = 'C:\\Users'
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
        
class CollectData(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    def input(self, ui, visa_chosen0, visa_chosen1, Array, timeStep, curve, curve_vt, curve_ct, dataX, dataVol, dataCurr):
        self.visa_chosen0 = visa_chosen0
        self.visa_chosen1 = visa_chosen1
        self.Array = Array
        
        self.curve = curve
        self.curve_vt = curve_vt
        self.curve_ct = curve_ct
        
        self.dataX = dataX
        self.dataVol = dataVol
        self.dataCurr = dataCurr
        self.ui = ui
        self.timeStep = timeStep
        self.pauseLoop = False
        self.track = 0
        if len(self.dataX) > 0:
            self.i = self.dataX[-1] + 1
        else:
            self.i = 0
        self.start()
    
    def run(self):
        #self.ui.tabWidget_plot_ay.setCurrentIndex(1)
        while not self.pauseLoop:
            if (self.timeStep > 0) & (self.pauseLoop == False):
                if self.track < len(self.Array):
                    curr = self.Array[self.track]/1000000
                    self.visa_chosen0.write('SOUR:LEV:AUTO ' + str(curr))
                    vol = float(self.visa_chosen1.ask('MEAS:VOLT?'))
                    
                    print 'Vol:' + str(vol) + '\nCurr:' + str(curr)
                   
                    self.dataVol.append(vol)
                    self.dataCurr.append(curr)
                    self.dataX.append(self.i)
                    
                    self.curve.set_data(self.dataCurr, self.dataVol)
                    self.curve_vt.set_data(self.dataX, self.dataVol)
                    self.curve_ct.set_data(self.dataX, self.dataCurr)
                    
                    self.emit(SIGNAL("plot"))
                    
                    self.i += 1
                    self.track += 1
                    time.sleep(self.timeStep)
                else:
                    #self.analyse()
                    y_plot = self.dataVol
                    x_plot = self.dataCurr
                    self.emit(SIGNAL("analyse"), x_plot, y_plot)
                    self.visa_chosen0.write('OUTP OFF')
                    self.pauseLoop = True
                    self.Array = []
                    self.track = 0
    
    '''def analyse(self):
        self.ui.mplwidget_analysis_ay.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.axes_analysis_ay.set_title('Voltage v. Current Measurement')
        self.axes_analysis_ay.set_ylabel("Current")
        self.axes_analysis_ay.set_xlabel("Voltage")
        self.axes_analysis_ay.plot(self.dataVol, self.dataCurr, marker = '.', linestyle = '-')
        #self.ui.mplwidget_analysis_ay.draw()'''
    
    
    def fit(self):
        try:
            warnings.simplefilter('ignore', np.RankWarning)
            user_input = self.ui.start_end_fit_ay.text()
            input_list = user_input.split(',')
            start_input = float(input_list[0])
            end_input = float(input_list[1])
            
            numpy_fit = np.polyfit(self.x_plot[start:end], self.y_plot[start:end], 1)
                
            self.ui.label_IV_keithley.setText(str(format(numpy_fit[0], '.5f')))
            self.ui.label_VI_keithley.setText(str(format(1 / numpy_fit[0], '.5f')))
            self.ui.label_intercept_keithley.setText(str(format(numpy_fit[1], '.5f')))
            self.ui.lineEdit_condition_keithley.setText('Linear fit done.')
        except Exception, e:
            self.ui.lineEdit_condition_keithley.setText('Please enter valid start/end value')
    
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            #self.ui.pushButtonPause.setText("Pause")
            self.ui.output.setText("Running")
        else:
            self.pauseLoop = True
            #self.ui.pushButtonPause.setText("Continue")
            self.ui.output.setText("Paused")
            
    def __del__(self):
        self.exiting = True
        self.wait()