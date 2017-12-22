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


class Lock_In():
    def __init__ (self, main, ui):

        self.ui = ui
        self.update_visa()
        
        self.collectDataThread = CollectData()
        self.saveDataThread = SaveData()

        
        self.curve_item = make.curve([], [], color='b')
        self.ui.curvewidgetPlotLI.plot.add_item(self.curve_item)
        self.ui.curvewidgetPlotLI.plot.set_antialiasing(True)
        self.ui.curvewidgetPlotLI.plot.set_titles("Title", "X-Axis", "Y-Axis")
        
        self.ui.pushButtonStopLI.setEnabled(False)
        self.ui.pushButtonPauseLI.setEnabled(False)
        
        main.connect(self.ui.pushButtonSelectLI, SIGNAL("clicked()"), self.choose_visa)
        main.connect(self.ui.pushButtonUpdateLI, SIGNAL("clicked()"), self.update_visa)

        main.connect(self.ui.pushButtonStartLI, SIGNAL("clicked()"), self.start)
        #self.connect(self.ui.pushButtonStart, SIGNAL("clicked()"), self.append_parameters)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.stop)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.final_append)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL("clicked()"), self.append_parameters)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.append_parameters)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.close_visa)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL("clicked()"), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.collectDataThread.appendSessionData)
        main.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.collectDataThread.appendSessionData)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.tableAppend)
        main.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.tableAppend)

        
        main.connect(self.ui.pushButtonSaveLI, SIGNAL('clicked()'), self.save)
        main.connect(self.ui.pushButtonBrowseLI, SIGNAL('clicked()'), self.browse)
        main.connect(self.ui.pushButtonFolderSelectLI, SIGNAL('clicked()'), self.select_name)
                     
        main.connect(self.ui.radioButtonDateTimeLI, SIGNAL('clicked()'), self.save_name)
        main.connect(self.ui.radioButtonCustomLI, SIGNAL('clicked()'), self.save_name)
                     
        main.connect(self.ui.radioButton_csvLI, SIGNAL('clicked()'), self.save_type)
        main.connect(self.ui.radioButton_txtLI, SIGNAL('clicked()'), self.save_type)
        
        main.connect(self.collectDataThread, SIGNAL("plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("Begin_Save"), self.pre_save)
        main.connect(self.collectDataThread, SIGNAL("append"), self.append_parameters)
        
        #Defines all the arrays used for saving and table functionality
        self.sessionData = []
        self.sens= []
        self.frequency= []
        self.amplitude= []
        self.QFactor= []
        self.filter = []
        self.coupling = []
        self.inputType = []
        self.floatground = []
        self.TimeConstant = []
        self.lastReading = []
        self.STDEV = []
        self.MaxMin = []
        self.color = ['Blue','Green', 'Red',' Black', 'Magenta']
        #Initial variable that let's the program know which row of the table to begin with
        self.tableRowNumber = 0
        
        self.ui.pushButtonStartLI.setDisabled(True)
        self.j = 0
    #Updates the visas displayed in the box    
    def update_visa(self):
        rm = visa.ResourceManager()
        check_current = True
        try:
            visas = rm.list_resources()
        except:
            visas = "There are currently no connected visas."
        #Clears previous items in list
        self.ui.comboBoxVisaListLI.clear()
        self.ui.labelCurrentVisaLI.clear()
        #Adds all currently connected visas into comboBox
        for each_visa in visas:
            self.ui.comboBoxVisaListLI.addItem(each_visa)

    def choose_visa(self):
        current_visa = str(self.ui.comboBoxVisaListLI.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource(current_visa)
        try:
            valid = self.check_visa(inst)
        except:
            self.ui.labelCurrentVisaLI.setText("")
        
        if valid == True:
            self.ui.labelCurrentVisaLI.setText(current_visa)
            self.chosen_visa = inst
            self.ui.pushButtonStartLI.setDisabled(False)

        elif valid == False:
            self.ui.labelCurrentVisaLI.setText("Error")
            self.ui.pushButtonStartLI.setDisabled(True)
    #Makes sure the visa is valid/functioning before selecting it
    def check_visa(self,inst):
        try:
            inst.ask('*IDN?')
            valid = True
        except:
            valid = False
        return valid
    #The function that does all the plotting functionality and data analysis
    def plotData(self, reading, magnitude, statData):
        self.ui.labelLastReadingLI.setText(str(round(reading/magnitude[1], 10)) + " " + magnitude[0])
        self.ui.lineEditSTDEVLI.setText(str(round(np.std(statData), 10)) + " " + magnitude[0])
        self.ui.lineEditMaxMinLI.setText(str(round(np.max(statData) - np.min(statData), 10)) + " " + magnitude[0])
        self.curve_item.plot().replot()
        self.ui.curvewidgetPlotLI.plot.do_autoscale()
        
    def start(self):
        startCheck = True
        try:
            str(self.ui.lineEditSensLI.currentText()) != ''
            str(self.ui.lineEditFrequencyLI.currentText()) != ''
            str(self.ui.lineEditAmplitudeLI.currentText()) != ''
            str(self.ui.lineEditQFactorLI.currentText()) != ''
            str(self.ui.lineEditTimeConstantLI.currentText()) != ''
            self.ui.radioButtonUnit_mVLI.isChecked() == True or self.ui.radioButtonUnit_uVLI.isChecked() == True or self.ui.radioButtonUnit_nVLI.isChecked() == True
            self.ui.radioButtonTimeScaleLI.isChecked() == True or self.ui.radioButtonStepScaleLI.isChecked() == True
            self.ui.radioButtonALI.isChecked() == True or self.ui.radioButtonABLI.isChecked() == True
            self.ui.radioButtonACLI.isChecked() == True or self.ui.radioButtonDCLI.isChecked() == True
            self.ui.radioButtonFloatLI.isChecked() == True or self.ui.radioButtonGroundLI.isChecked() == True
            self.ui.radioButtonBandPassLI.isChecked() == True or self.ui.radioButtonHighPassLI.isChecked() == True or self.ui.radioButtonLowPassLI.isChecked() == True or self.ui.radioButtonNotchLI.isChecked() == True or self.ui.radioButtonFlatLI.isChecked() == True
        except:
            startCheck = False

            
        if startCheck == True:
            #Sends parameters into the CollectDataThread, initiating it
            self.collectDataThread.input(self.ui, self.curve_item, [], [])
            self.ui.pushButtonStartLI.setEnabled(False)
            self.ui.pushButtonStopLI.setEnabled(True)
            self.ui.pushButtonPauseLI.setEnabled(True)
            self.ui.labelErrorStatusLI.setText("Running")
            self.ui.pushButtonPauseLI.setText("Pause")
        else:
            self.ui.labelErrorStatusLI.setText("Please make sure all parameters are there")

    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonStartLI.setEnabled(True)
        self.ui.pushButtonStopLI.setEnabled(False)
        self.ui.pushButtonPauseLI.setEnabled(False)
        self.ui.labelErrorStatusLI.setText("Stopped")
        self.ui.pushButtonPauseLI.setText("Pause")
        
    def close_visa(self):
        self.chosen_visa.close()

        
    def browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select The GoogleDrive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEditOneDriveLI.setText(file_dir)
        self.directory = ''
            
    def select_name(self):
        file_list= []
        file_list = str(self.ui.lineEditOneDriveLI.text()).split('\\')
        for i in range(0, len(file_list)):
            self.directory += file_list[i] + '\\'
        namefolder = str(self.ui.comboBoxFoldersLI.currentText())
        if namefolder == 'None':
            self.ui.labelSaveStatusLI.setText('Please Choose A Folder To Save To.')
        else:
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.directory += namefolder + "\Data" + '\\' + date
            self.current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            self.date_and_time = date + ' ' + self.current_time
            self.file_name = (self.date_and_time)
            
    def save_type(self):
        if self.ui.radioButton_csvLI.isChecked() == True:
            self.type = '.csv'
            self.divide = ','
        elif self.ui.radioButton_txtLI.isChecked() == True:
            self.type = '.txt'
            self.divide = '\t'
            
    def save_name(self):
        if self.ui.radioButtonDateTimeLI.isChecked():
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            date_and_time = date + ' ' + current_time
            self.file_name = str(date_and_time)
        elif self.ui.radioButtonCustomLI.isChecked():
            self.file_name = str(self.ui.lineEditCustomFile.text())
            
    def pre_save(self, dataTime, dataPoints, magnitude, sessionData):
        #Defines the variables for use in MainClass from the CollectDataThread
        self.dataTime = dataTime
        self.dataPoints = dataPoints
        self.magnitude = magnitude
        self.sessionData = sessionData

        
    def append_parameters(self):
        #When the function is called, and the pauseLoop is actively False, the parameters inputted by the user will become appended to the arrays etsablished earlier.
        #if self.collectDataThread.pauseLoop == False or self.collectDataThread.check == True:
        if self.collectDataThread.check == True:
            if self.ui.radioButtonUnit_mVLI.isChecked() == True:
                magnitude = ['mV', 1E-3]
            elif self.ui.radioButtonUnit_uVLI.isChecked() == True:
                magnitude = ['uV', 1E-6]
            elif self.ui.radioButtonUnit_nVLI.isChecked() == True:
                magnitude = ['nV', 1E-9]
                
            self.sens.append(str(self.ui.lineEditSensLI.text()) + "" + magnitude[0])
            self.frequency.append(str(self.ui.lineEditFrequencyLI.text()))
            self.amplitude.append(str(self.ui.lineEditAmplitudeLI.text()))
            self.QFactor.append(str(self.ui.lineEditQFactorLI.text()))
            self.TimeConstant.append(str(self.ui.lineEditTimeConstantLI.text()))
           
            if self.ui.radioButtonBandPassLI.isChecked() == True:
                self.filter.append('Band Pass')
            elif self.ui.radioButtonHighPassLI.isChecked() == True:
                self.filter.append('High Pass')
            elif self.ui.radioButtonLowPassLI.isChecked() == True:
                self.filter.append('Low Pass')
            elif self.ui.radioButtonNotchLI.isChecked() == True:
                self.filter.append('Notch')
            elif self.ui.radioButtonFlatLI.isChecked() == True:
                self.filter.append('Flat')
            else:
                self.filter = ''
                self.ui.labelErrorStatusLI.setText("Please Choose A Filter Type")
                
            if self.ui.radioButtonACLI.isChecked() == True:
                self.coupling.append('AC')
            elif self.ui.radioButtonDCLI.isChecked() == True:
                self.coupling.append('DC')
            else:
                self.ui.labelErrorStatusLI.setText("Please Choose A Coupling")
                self.coupling = ''
                
            if self.ui.radioButtonALI.isChecked() == True:
                self.inputType.append('A')
            elif self.ui.radioButtonABLI.isChecked() == True:
                self.inputType.append('A-B')
            else:
                self.inputType = ''
                self.ui.labelErrorStatusLI.setText("Please Choose An Input Type")
                
            if self.ui.radioButtonFloatLI.isChecked() == True:
                self.floatground.append('Float')
            elif self.ui.radioButtonGroundLI.isChecked() == True:
                self.floatground.append('Ground')
            else:
                self.floatground = ''
                self.ui.labelErrorStatusLI.setText("Please Choose Float Or Ground")
            #Appends the information to fill out the columns of the chart    
            self.lastReading.append(str(self.ui.labelLastReadingLI.text()))
            self.STDEV.append(str(self.ui.lineEditSTDEVLI.text()))
            self.MaxMin.append(str(self.ui.lineEditMaxMinLI.text()))
            self.tableAppend()
            #self.collectDataThread.check = False
            self.color.append(self.color[self.j])   
            self.j += 1
            print len(self.dataPoints)
    #Is a function that should be called after the user has decided to stop collecting data, it ensures that the last bit is appended before asving.       
    def final_append(self):
        #Sets a variable from the CollectDataThread to True, enabling it to append the final sequence of data
        self.collectDataThread.final_append = True

        
    def save(self):
        #Defines the arrays that will inputted into the SaveDataThread
        parameters = ['Sensitivity:','Frequency:', 'Amplitude:', 'Q Factor:', 'Time Constant:', 'Filter Type:', 'Coupling:', 'Input:', 'Float/Ground:']
        parametersValue =[self.sens, self.frequency, self.amplitude, self.QFactor, self.TimeConstant, self.filter, self.coupling, self.inputType, self.floatground]
        number = []
        time= []
        data = []
        file_info = []
        
        time.append('Time(s)')
        #Creates an array of numbers that will associated with data point values
        for i in range(0,len(self.dataPoints)):
            number.append(i)
        time.append(self.dataTime)
        data.append(self.dataPoints)
        #Appends to an empty array the necessary information to create a save file
        file_info.append(self.file_name)
        
        file_info.append(self.type)
        
        file_info.append(self.divide)
        
        file_info.append(self.directory)
        

        #Sends the newly created arrays and variables into the SaveDataThread
        self.saveDataThread.input(self.magnitude,number, parameters, parametersValue, time, data, file_info, self.sessionData)
        self.ui.labelSaveStatus.setText("File Successfully Saved")
        print self.sessionData
        print parameters
        print parametersValue
    
    def tableAppend(self):
        #Establishes the arrays to be translated into the tables
        tableValues =[self.sens, self.frequency, self.amplitude, self.QFactor, self.TimeConstant, self.lastReading, self.STDEV, self.MaxMin, self.color]
        #When the plotting is resumed after a pause, this if statement ensures/appends the most recent data collection into the first row

        if self.collectDataThread.check == True:
            print self.tableRowNumber
            self.collectDataThread.check = False
            self.ui.tableWidgetDataAnalysisLI.insertRow(self.tableRowNumber)
            for i in range(0, len(tableValues)):
                self.ui.tableWidgetDataAnalysisLI.setItem(self.tableRowNumber, i, QTableWidgetItem(tableValues[i][self.tableRowNumber]))
                #Tells the program next time this function is called to move onto the next row
            self.tableRowNumber += 1
        #This elif statement is called when the Stop button is pressed, it appends the final bit of information collected.
        elif self.collectDataThread.final_append == True:
            self.ui.tableWidgetDataAnalysisLI.insertRow(self.tableRowNumber)
            for i in range(0, len(tableValues)):
                self.ui.tableWidgetDataAnalysisLI.setItem(self.tableRowNumber, i, QTableWidgetItem(tableValues[i][self.tableRowNumber]))
            
        
    def closeEvent(self, question):
        print question
        quit_msg = "Do you want to quit this program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            question.accept()
        else:
            question.ignore()
            
            
class CollectData(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, curve, dataX, dataY):
        self.curve = curve
        self.dataX = dataX
        self.dataY = np.array([], dtype = float)
        self.Steps = np.array([], dtype = float)
        self.StatData = []
        self.temp = np.array([], dtype = float)
        self.temp2 = np.array([], dtype = float)
        self.ui = ui
        self.global_time = np.array([0], dtype = float)
        self.t1 = time.clock()
        self.pauseLoop = False
        self.start()

        #Creates necessary variables for appending data to arrays
        #The 0 index in sessionData is a placeholder to make sure the numbers and values are correctly inputted into a save file
        self.sessionData = [0]
        self.append_check = False
        self.final_append = False
        self.check = False
        self.n = 0
        self.i = 0
        self.colors = ['g','r', 'o', 'm', 'b']
    #Lets the collectDataThread know that the visa is good
    def check_visa(self,inst):
        try:
            inst.ask('*IDN?')
            valid = True
        except:
            valid = False
        return valid
        
    def run(self):
        while True:
            if self.pauseLoop == False:
                collect_check = True
                
                current_visa = str(self.ui.comboBoxVisaListLI.currentText())
                rm = visa.ResourceManager()
                rm.list_resources()
                inst = rm.open_resource(current_visa)
                self.chosen_visa = inst
                #Reads the lines of certain inputs before collecting to make sure they are valid
                try:
                    self.timestep = float(self.ui.lineEditTimestepLI.text())
                    
                except:
                    self.timestep = -1
                    
                try:
                    self.span = float(self.ui.lineEditPointsShownLI.text())
                except:
                    self.span = -1
                    
                if self.timestep <= 0 or self.span <= 0:
                    
                    if self.timestep <= 0 and self.span <= 0:
                        self.ui.labelErrorStatusLI.setText("Invalid Timestep and Points Shown")
                    elif self.timestep <= 0 :
                        self.ui.labelErrorStatusLI.setText("Invalid Timestep")
                    elif self. timestep >= 0 and self.span <=0:
                        self.ui.labelErrorStatusLI.setText("Error In Points Shown Value")
                    #Lets the program know that it is not okay to start collecting data
                    collect_check = False
                #If the program is given the okay to collect data, this is run    
                if collect_check == True:
                    #Ensures that the visa data is collected from is valid
                    valid = self.check_visa(self.chosen_visa)
                    
                    if valid == True:
                        self.ui.labelErrorStatusLI.setText("Running...No errors")
                        #Established the command that the visa is going to be asked
                        self.command = "Read?"
                        #Establishes all the necessary parameters to count time
                        self.t2 = time.clock()
                
                        self.t = self.t2 - self.t1
                
                        self.t1 = time.clock()
                
                        self.span = float(self.ui.lineEditPointsShownLI.text())
                
                        self.time_now = self.global_time[-1] + self.t
                
                        check = True
                        #Defines the array, magnitude, that contains information that will used for data analysis and other functions
                        if self.ui.radioButtonUnit_mVLI.isChecked() == True:
                            magnitude = ['mV', 1E-3]
                        elif self.ui.radioButtonUnit_uVLI.isChecked() == True:
                            magnitude = ['uV', 1E-6]
                        elif self.ui.radioButtonUnit_nVLI.isChecked() == True:
                            magnitude = ['nV', 1E-9]
                        #Sets the axes of the plots
                        if self.ui.radioButtonTimeScaleLI.isChecked() == True:
                            self.ui.curvewidgetPlotLI.plot.set_titles("Lock-in Data", "Time (s)", "Voltage (" + magnitude[0] + ")")
                            self.scale = 'Time'
                        elif self.ui.radioButtonStepScaleLI.isChecked() == True:
                            self.ui.curvewidgetPlotLI.plot.set_titles("Lock- in Data", "Steps", "Voltage (" + magnitude[0] + ")")
                            self.scale = 'Steps'
                            
                        #Defines a variable that ensures that the data collected will come out to be in the desired units    
                        self.sens = float(self.ui.lineEditSensLI.text())*magnitude[1]
                        self.i_plot = 0
                        try:
                            #Collects the data, ensuring that it will in the units of Volts
                            reading = float(self.chosen_visa.ask(self.command))*(self.sens)/10
                        except:
                            #If the visa fails to respond to the command, this will shut down the process and lets the user know of an error
                            check = False
                            valid = self.check_visa(self.chosen_visa)
                            
                            if valid == True:
                                self.ui.labelErrorStatusLI.setText("There is a problem with the response to the queried command. Improper format")
                            else:
                                self.ui.labelErrorStatusLI.setText("The Visa has become disconnected")
                        #Otherwise if given the okay, the program is told to append arrays for plotting and analysis
                        if check == True and len(self.temp) < float(self.ui.lineEditNumPointsLI.text()):
                            #Appends the data into the appropriate arrays
                            self.dataY = np.append(self.dataY, reading)
                            self.temp = np.append(self.temp, reading)
                            self.Steps = np.append(self.Steps, (self.n + 1))
                            self.temp2 = np.append(self.temp2, (self.n+1))
                            self.global_time = np.append(self.global_time, self.time_now)
                            self.dataX = self.global_time

                            if self.i_plot >= int(self.ui.lineEditPlotEveryLI.text()) and self.scale == 'Time':
                                self.curve.set_data(self.dataX, self.dataY/magnitude[1])                                
                                self.i_plot = 0
                                #Redefines the self variables to normal variables so they can be emitted through a signal
                                dataPoints = self.dataY/magnitude[1]
                                statData = self.temp/magnitude[1]
                                dataTime = self.dataX
                                sessionData = self.sessionData
                                self.n += 1
                            elif self.i_plot >=  int(self.ui.lineEditPlotEveryLI.text()) and self.scale == 'Steps':
                                self.curve.set_data(self.temp2, self.temp/magnitude[1])                                
                                self.i_plot = 0
                                #Redefines the self variables to normal variables so they can be emitted through a signal
                                dataPoints = self.dataY/magnitude[1]
                                statData = self.temp/magnitude[1]
                                dataTime = self.dataX
                                sessionData = self.sessionData
                                self.n += 1
                            else:
                                self.i_plot += 1
                        elif len(self.temp) == float(self.ui.lineEditNumPointsLI.text()):
                            self.temp = np.array([], dtype = float)
                            self.temp2 = np.array([], dtype = float)
                            self.pause()
                            self.ui.labelCollectStatusLI.setText("Please Change Inputs And Hit Continue")
                            self.check = True
                            self.appendSessionData()
                            self.emit(SIGNAL("append"))
                            self.curve = make.curve([], [], color=self.colors[self.i])
                            self.colors.append(self.colors[self.i])
                            self.ui.curvewidgetPlotLI.plot.add_item(self.curve)
                            self.ui.curvewidgetPlotLI.plot.set_antialiasing(True)
                            self.i += 1

                        else:
                            self.stop() 
                self.emit(SIGNAL("plot"), reading, magnitude, statData)
                self.emit(SIGNAL("Begin_Save"), dataTime, dataPoints, magnitude, sessionData)
                time.sleep(self.timestep)
            else:
                pass
                           
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            self.ui.pushButtonPauseLI.setText("Pause")
            self.ui.labelErrorStatusLI.setText("Running...No errors")
            self.ui.labelCollectStatusLI.setText("Collecting Data...")
            self.append_check = False

        else:
            self.pauseLoop = True
            self.ui.pushButtonPauseLI.setText("Continue")
            self.ui.labelErrorStatusLI.setText("Paused")
            self.append_check = True
            
    def appendSessionData(self):
        #Whenever the pause button is pressed to pause plotting, the length of the data is appended to an array. This ensures that the data is properly broken down by the parametesr it was taken with.
        #if self.check == True or self.append_check == False:
        if self.check == True:
            self.sessionData.append(len(self.dataY))
        #When the user decides they are done with collecting data, and the stop button is pressed, this is initiated. Appends final data.
        elif self.final_append == True:
            self.sessionData.append(len(self.dataY))
        else:
            pass


    
    def __del__(self):
        self.exiting = True
        self.wait()

class SaveData(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
    
    # comments is the list that contains all the information you want to show before the data
    # To make file writing easier, comments is designed to be a two dimensional list.
    # Each sublist in comments is one single line when write the file.
    # For example the first line may be ["User Name: ", "Vannucci"], the second line may be ["Edit Time:", "2016-2-11 11:11:11"]
    # Store the measurement details in this list so that they can be shown before the data, such as visa name, time step
    # User's comments are also included in this list.
    
    # parameters is a list contains the name of the data values, for example ["Date and Time", "Array", "Voltages", "Current"]
    
    # units is a list contains the corresponding units of the parameters, for example ["String", "1", "Volts", "Amps"]
    
    # file_info is a list contains the information about this current file and the format is fixed.
    # First item is file name
    # Second item is file type (csv or txt), for example ".csv" ot ".txt"
    # Third item is the corresponding divide mark. For csv it is "," and for txt it is "\t"
    # Fourth item is the divider and it is set to be "Collected Data" for all saving files
    # Fifth item is the saving directory of the folder
    def input(self, magnitude, number, parameters, parametersValue, time, data, file_info, sessionData):
        self.magnitude = magnitude
        self.number = number
        self.parameters = parameters
        self.parametersValue = parametersValue
        self.time = time
        self.data = data
        self.file_info = file_info
        self.sessionData = sessionData
        self.start()
        
    def run(self):
        # Create a folder at this address
        if not os.path.isdir(self.file_info[3]):
            os.makedirs(self.file_info[3])
        f_name = self.file_info[3] + '\\' + self.file_info[0] + self.file_info[1]
        
        f = open(f_name, 'w')

        for i in range(0, len(self.sessionData)):
            for j in range(0, len(self.parameters)):
                f.write(self.parameters[j] + self.parametersValue[j][i] + '\n')
                
            f.write('Steps' +self.file_info[2] + 'Voltage(V)' + '\n')
            for k in range(self.sessionData[i], self.sessionData[i+1]):
                f.write(str(k+1) + self.file_info[2] + str(self.data[0][k]) + self.file_info[2] + '\n')
            
        
        f.write('\n')
        
        f.write(self.file_info[3] + '\n')
        
        
        f.close()
        
    def __del__(self):
        self.exiting = True
        self.wait()
        
        


if __name__ == "__main__":
    # Opens the GUI
    app = QApplication(sys.argv)
    myapp = MyForm()
    
    # Shows the GUI
    myapp.show()
    
    # Exits the GUI when the x button is clicked
    sys.exit(app.exec_())
