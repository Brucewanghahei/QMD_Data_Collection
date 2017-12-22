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
        main.connect(self.ui.pushButtonStartLI, SIGNAL("clicked()"), self.initialize)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.pre_stop)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.final_append)
        main.connect(self.ui.pushButtonRetrieve, SIGNAL("clicked()"), self.retrieve_parameters)
        main.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.close_visa)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL("clicked()"), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.collectDataThread.appendSessionData)
        main.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.collectDataThread.appendSessionData)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.collectDataThread.reset_array)
        main.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.tableAppend)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.tempDisable)
        main.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.reenable)

        
        main.connect(self.ui.pushButtonSaveLI, SIGNAL('clicked()'), self.save)
        main.connect(self.ui.pushButtonBrowseLI, SIGNAL('clicked()'), self.browse)
        main.connect(self.ui.pushButtonFolderSelectLI, SIGNAL('clicked()'), self.select_name)
                     
        main.connect(self.ui.radioButton_csvLI, SIGNAL('clicked()'), self.save_type)
        main.connect(self.ui.radioButton_txtLI, SIGNAL('clicked()'), self.save_type)
        
        main.connect(self.collectDataThread, SIGNAL("plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("Begin_Save"), self.pre_save)
        main.connect(self.collectDataThread, SIGNAL("append"), self.append_parameters)

        #Initial variable that let's the program know which row of the table to begin with
        self.tableRowNumber = 0
        
        self.ui.pushButtonStartLI.setDisabled(True)
        self.j = 0
        self.autosaveIndex = 0
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
        #Adds all currently connected visas into comboBoxes
        for each_visa in visas:
            self.ui.comboBoxVisaListLI.addItem(each_visa)
            self.ui.comboBoxRetrieveVisa.addItem(each_visa)
    #Ensures that the visa chosen to be read from is valid
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
            self.ui.labelCurrentVisaLI.setText(rm.open_resource(current_visa).ask("*IDN?"))
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
    #is the function that talks to the lock-in to fill in the parameters
    def retrieve_parameters(self):
        #temporary defines the lock-in to a variable that can be talked to
        retrieve_visa = str(self.ui.comboBoxRetrieveVisa.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource(retrieve_visa)
        #Reading from the lock-in will return values of integers, these integers correspond to the actual settings read from the lock in. These arrays make sure the integers are converted to what the
        #settings were placed to.
        self.sens_conversion= ['100','200','500','1','2','5','10','20','50','100','200','500','1','2','5','10','20','50','100','200','500']
        self.tc_values = ['500 us','1 ms','3 ms','10 ms','30 ms', '100 ms','300 ms','1 s','3 s','10 s','30 s','100 s','300 s']
        self.qfactor_values = ['1','2','5','10','20','50','100']

        #Makes sure that the parameters are inputted to their respective slots
        self.ui.lineEditSensLI.setText(self.sens_conversion[int(inst.ask('SENS?'))])
        
        if int(inst.ask('SENS?')) < 3:
            self.ui.radioButtonUnit_nVLI.setChecked(True)
        elif int(inst.ask('SENS?')) >= 3 and int(inst.ask('SENS ?')) < 12:
            self.ui.radioButtonUnit_uVLI.setChecked(True)
        else:
            self.ui.radioButtonUnit_mVLI.setChecked(True)
            
        self.ui.lineEditFrequencyLI.setText(str(inst.ask("FREQ?")).replace("\r\n", ""))
        self.ui.lineEditTrimFrequencyLI.setText(str(inst.ask("IFFR?")).replace("\r\n", ""))
        self.ui.lineEditPhaseLI.setText(str(inst.ask("PHAS?")).replace("\r\n", ""))
        self.ui.lineEditAmplitudeLI.setText(str(inst.ask("SLVL?")).replace("\r\n", ""))
        self.ui.lineEditQFactorLI.setText(self.qfactor_values[int(inst.ask("QFCT?"))])
        self.ui.lineEditTimeConstantLI.setText(self.tc_values[int((inst.ask("OFLT?")))])
        
        #Depending on the integer returned from the lock-in, certain buttons will be pushed.
        if int(inst.ask('ISRC?')) == 0:
            self.ui.radioButtonALI.setChecked(True)
        else:
            self.ui.radioButtonABLI.setChecked(True)
            
        if int(inst.ask('ICPL?')) == 0:
            self.ui.radioButtonACLI.setChecked(True)
        else:
            self.ui.radioButtonDCLI.setChecked(True)
            
        if int(inst.ask('IGND?')) == 0:
            self.ui.radioButtonFloatLI.setChecked(True)
        else:
            self.ui.radioButtonGroundLI.setChecked(True)
        
        if int(inst.ask('TYPF?')) == 0:
            self.ui.radioButtonBandPassLI.setChecked(True)
        elif int(inst.ask('TYPF?')) == 1:
            self.ui.radioButtonHighPassLI.setChecked(True)
        elif int(inst.ask('TYPF?')) == 2:
            self.ui.radioButtonLowPassLI.setChecked(True)
        elif int(inst.ask('TYPF?')) == 3:
            self.ui.radioButtonNotchLI.setChecked(True)
        else:
            self.ui.radioButtonFlatLI.setChecked(True)
            
        if int(inst.ask('QUAD?')) == 0:
            self.ui.radioButtonQuadrant1.setChecked(True)
        elif int(inst.ask('QUAD?')) == 1:
            self.ui.radioButtonQuadrant2.setChecked(True)
        elif int(inst.ask('QUAD?')) == 2:
            self.ui.radioButtonQuadrant3.setChecked(True)
        else:
            self.ui.radioButtonQuadrant4.setChecked(True)
            
        if int(inst.ask('FMOD?')) == 0:
            self.ui.radioButtonfModeLI.setChecked(True)
        elif int(inst.ask('FMOD?')) == 1:
            self.ui.radioButtonInternalModeLI.setChecked(True)
        elif int(inst.ask('FMOD?')) == 2:
            self.ui.radioButton2fModeLI.setChecked(True)
        elif int(inst.ask('FMOD?')) == 3:
            self.ui.radioButton3fModeLI.setChecked(True)
        else:
            self.ui.radioButtonReadModeLI.setChecked(True)
            
        if int(inst.ask('FRNG?')) == 0:
            self.ui.radioButtonRange1.setChecked(True)
        elif int(inst.ask('FRNG?')) == 1:
            self.ui.radioButtonRange2.setChecked(True)
        elif int(inst.ask('FRNG?')) == 2:
            self.ui.radioButtonRange3.setChecked(True)
        elif int(inst.ask('FRNG?')) == 3:
            self.ui.radioButtonRange4.setChecked(True)
        else:
            self.ui.radioButtonRange5.setChecked(True)
            
        if int(inst.ask('RMOD?')) == 0:
            self.ui.radioButtonHighResLI.setChecked(True)
        elif int(inst.ask('RMOD?')) == 1:
            self.ui.radioButtonNormalLI.setChecked(True)
        else:
            self.ui.radioButtonLowNoiseLI.setChecked(True)
            
        if int(inst.ask('OFSL?')) == 0:
            self.ui.radioButton6dBLI.setChecked(True)
        else:
            self.ui.radioButton12dBLI.setChecked(True)
            
        self.start_check = True
        
        
        
    #The function that does all the plotting functionality and data analysis
    def plotData(self, reading, magnitude, statData):
        self.ui.labelLastReadingLI.setText(str(round(reading/magnitude[1], 10)) + " " + magnitude[0])
        self.ui.lineEditSTDEVLI.setText(str(round(np.std(statData), 10)) + " " + magnitude[0])
        self.ui.lineEditMaxMinLI.setText(str(round(np.max(statData) - np.min(statData), 10)) + " " + magnitude[0])
        self.curve_item.plot().replot()
        self.ui.curvewidgetPlotLI.plot.do_autoscale()
        
    def initialize(self):
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
        self.units = []
        self.color = ['Blue','Green', 'Red',' Black', 'Magenta']
        
    def start(self):
        self.ui.tabWidgetLockIn.setCurrentIndex(1)
        self.save_preference()
        #First try sets this variable to false
        self.clear_plot = False
        #After stop is pressed at least once, the variable above is set to true. This resets the plot of the previous run.
        if self.clear_plot == True:
            self.ui.curveWidgetPlotLI.plot.set_titles('','','')
            self.curve_item.set_data([],[])
            self.curve_item.plot.replot()
        else:
            pass
        
        #Makes sure that there is a proper scale to plot in, otherwise the program doesn't run
        if self.ui.radioButtonStepScaleLI.isChecked() == True or self.ui.radioButtonTimeScaleLI.isChecked() == True:
            self.start_check = True
        else:
            self.start_check = False
            
        #If there is a proper scale, the program begins collecting data
        if self.start_check == True:
            #Sends parameters into the CollectDataThread, initiating it
            self.collectDataThread.input(self.ui, self.curve_item, [], [])
            self.ui.pushButtonStartLI.setEnabled(False)
            self.ui.pushButtonStopLI.setEnabled(True)
            self.ui.pushButtonPauseLI.setEnabled(True)
            self.ui.labelErrorStatusLI.setText("Running")
            self.ui.pushButtonPauseLI.setText("Pause")
        else:
            self.ui.labelErrorStatusLI.setText("Error:Empty Parameter")
            
    #This function is active to make sure the data is added to the table before stopping  
    def pre_stop(self):
        self.stop_check = True
        self.append_parameters()
        self.collectDataThread.pauseLoop = True
        self.stop()
        
    #This function stops the program
    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonStartLI.setEnabled(True)
        self.ui.pushButtonStopLI.setEnabled(False)
        self.ui.pushButtonPauseLI.setEnabled(False)
        self.ui.labelErrorStatusLI.setText("Stopped")
        self.ui.pushButtonPauseLI.setText("Pause")
    
    #This function closes the visa that is chosen to be read from
    def close_visa(self):
        self.chosen_visa.close()
        
    #Clears the table after the user has decided to stop the previous run and begins a new one
    def clearTable(self):
        for i in range(1,20):
            self.ui.tableWidgetDataAnalysisLI.removeRow(i)
            
    # def dynamicSave(self):
    #     if self.first_save == True:
            
        
    #Allows the user to find the destination they desire to save the data in
    def browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select The GoogleDrive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEditOneDriveLI.setText(file_dir)
        self.directory = ''
    
    #Allows the user to select the folder belonging to Google Drive
    def select_name(self):
        file_list= []
        file_list = str(self.ui.lineEditOneDriveLI.text()).split('\\')
        for i in range(0, len(file_list)):
            self.directory += file_list[i] + '\\'
        namefolder = str(self.ui.comboBoxFoldersLI.currentText())
        if namefolder == 'None':
            self.ui.labelSaveStatusLI.setText('Please Choose A Folder To Save To.')
        else:
            #Sets the name of the file to current date and time by default
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.directory += namefolder + "\Data" + '\\' + date
            self.current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            self.date_and_time = date + ' ' + self.current_time
            self.file_name = (self.date_and_time)
            print self.directory
            
    #Allows the user to select what type of file they want their data to be saved in
    def save_type(self):
        if self.ui.radioButton_csvLI.isChecked() == True:
            self.type = '.csv'
            self.divide = ','
        elif self.ui.radioButton_txtLI.isChecked() == True:
            self.type = '.txt'
            self.divide = '\t'
            
    #Allows the user to customize the name of their data's file according to which radiobutton they check
    def save_name(self):
        if self.ui.radioButtonDateTimeLI.isChecked():
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            date_and_time = date + ' ' + current_time
            self.file_name = str(date_and_time)
        elif self.ui.radioButtonCustomLI.isChecked():
            self.file_name = str(self.ui.lineEditCustomFileLI.text())
    def pre_save(self, dataTime, dataPoints, magnitude, sessionData):
        
        #Defines the variables for use in MainClass from the CollectDataThread
        self.dataTime = dataTime
        self.dataPoints = dataPoints
        self.magnitude = magnitude
        self.sessionData = sessionData

        
    def append_parameters(self):
        #When the function is called, and the pauseLoop is actively False, the parameters inputted by the user will become appended to the arrays established earlier.
        #if self.collectDataThread.pauseLoop == False or self.collectDataThread.check == True:
        if self.collectDataThread.check == True or self.stop_check == True:
            if self.ui.radioButtonUnit_mVLI.isChecked() == True:
                magnitude = ['mV', 1E-3]
            elif self.ui.radioButtonUnit_uVLI.isChecked() == True:
                magnitude = ['uV', 1E-6]
            elif self.ui.radioButtonUnit_nVLI.isChecked() == True:
                magnitude = ['nV', 1E-9]
                
            self.units.append(magnitude[0])   
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
            
    #Is a function that should be called after the user has decided to stop collecting data, it ensures that the last bit is appended before saving.       
    def final_append(self):
        #Sets a variable from the CollectDataThread to True, enabling it to append the final sequence of data
        self.collectDataThread.final_append = True
        self.clear_plot = True
        
    def save_preference(self):
        if self.ui.checkBoxDynamicSaveLI.isChecked():
            self.save_style = 'Dynamic'
        elif self.ui.checkBoxAutoSave.isChecked():
            self.save_style = 'Periodic'
        else:
            self.save_style = ''
    
    #Is a funcion that saves the data after the program is paused and a new run has begun
    def autoSave(self):
        self.save_name()
        parameters = ['Sensitivity:','Frequency:', 'Amplitude:', 'Q Factor:', 'Time Constant:', 'Filter Type:', 'Coupling:', 'Input:', 'Float/Ground:']
        parametersValue =[self.sens, self.frequency, self.amplitude, self.QFactor, self.TimeConstant, self.filter, self.coupling, self.inputType, self.floatground]
        comments = []
        number = []
        time= []
        data = []
        file_info = []
        divider = "Collected Data"
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
        
        file_info.append(divider)
        
        final_save = False
        
        self.saveDataThread.input(self.magnitude,number, parameters, parametersValue, time, data, file_info, self.sessionData, self.units, final_save, self.autosaveIndex)
        self.ui.labelSaveStatus.setText("Data Has Been AutoSaved.")
        
    def save(self):
        self.final_save = True
        #Calls the save_name function to receive the final name of the data file
        self.save_name()
        #Defines the arrays that will inputted into the SaveDataThread
        parameters = ['Sensitivity:','Frequency:', 'Amplitude:', 'Q Factor:', 'Time Constant:', 'Filter Type:', 'Coupling:', 'Input:', 'Float/Ground:']
        parametersValue =[self.sens, self.frequency, self.amplitude, self.QFactor, self.TimeConstant, self.filter, self.coupling, self.inputType, self.floatground]
        comments = []
        number = []
        time= []
        data = []
        file_info = []
        divider = "Collected Data"
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
        
        file_info.append(divider)
        
        final_save = True

        #Sends the newly created arrays and variables into the SaveDataThread
        self.saveDataThread.input(self.magnitude,number, parameters, parametersValue, time, data, file_info, self.sessionData, self.units, final_save, self.autosaveIndex)
        self.ui.labelSaveStatus.setText("File was successfully saved.")
        print self.sessionData
        print parameters
        print parametersValue
       
    #Function that prevents the user from accidentally clicking pause and continue too fast(Data is bugged- Program needs atleast 1 second to collect data) 
    def tempDisable(self):
        if self.collectDataThread.cont_check == True:
            self.ui.pushButtonPauseLI.setDisabled(True)
            self.tableAppend
        else:
            pass

    #Sets the pause/continue button to be true
    def reenable(self):
        self.ui.pushButtonPauseLI.setEnabled(True)
        time.sleep(0.5)

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
            
        #Makes it so the user can manually configure the lock-in settings
        # retrieve_visa = str(self.ui.comboBoxRetrieveVisa.currentText())
        # rm = visa.ResourceManager()
        # rm.list_resources()
        # #inst = rm.open_resource(retrieve_visa)
        # #inst.write('LOCL LOCAL')
        
        self.save_preference()
        if self.save_style == 'Periodic':
            #Adds one an index, allowing the appropriate array to be saved for the autosave function. Calls the autosave function
            self.autosaveIndex += 1
            self.autoSave()
        else:
            pass

        
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
        self.cont_check = False
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
                                
                        if self.ui.radioButtonContinuousLI.isChecked() == True:
                            self.cont_check = True
                        else:
                            self.cont_check = False
                            
                        if self.cont_check == False:
                            self.reset_check = False
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
                        elif self.cont_check == True:
                            self.dataY = np.append(self.dataY, reading)
                            self.temp = np.append(self.temp, reading)
                            self.Steps = np.append(self.Steps, (self.n + 1))
                            self.temp2 = np.append(self.temp2, (self.n+1))
                            self.global_time = np.append(self.global_time, self.time_now)
                            self.dataX = self.global_time
                            self.reset_check = True
                            
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
            self.ui.labelSaveStatus.setText('')
            self.append_check = False

        else:
            self.pauseLoop = True
            self.ui.pushButtonPauseLI.setText("Continue")
            self.ui.labelErrorStatusLI.setText("Paused")
            self.append_check = True
            self.check = False

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
        
    def reset_array(self):
        if self.reset_check == True:
            self.reset_check = False
            self.temp = np.array([], dtype = float)
            self.temp2 = np.array([], dtype = float)
            self.check = True
            self.appendSessionData()
            self.emit(SIGNAL("append"))
            self.curve = make.curve([], [], color=self.colors[self.i])
            self.colors.append(self.colors[self.i])
            self.ui.curvewidgetPlotLI.plot.add_item(self.curve)
            self.ui.curvewidgetPlotLI.plot.set_antialiasing(True)
            self.i += 1
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
    def input(self, magnitude, number, parameters, parametersValue, time, data, file_info, sessionData, units, final_save, autosaveIndex):
        self.magnitude = magnitude
        self.units = units
        self.number = number
        self.parameters = parameters
        self.parametersValue = parametersValue
        self.time = time
        self.data = data
        self.file_info = file_info
        self.sessionData = sessionData
        self.final_save = final_save
        self.i = autosaveIndex
        self.start()
        
    def run(self):
        if self.final_save == True:
            # Create a folder at this address
            if not os.path.isdir(self.file_info[3]):
                os.makedirs(self.file_info[3])
            f_name = self.file_info[3] + '\\' + self.file_info[0] + self.file_info[1]
            
            f = open(f_name, 'w')
            f.write('Comments:' + '\n')
            
            for i in range(0, len(self.sessionData)-1):
                f.write('Session number' + ' ' + str(i+1) + '\n')
                f.write('Points Collected In Session:' + str(int(self.sessionData[i+1] - int(self.sessionData[i]))) + '\n')
                for j in range(0, len(self.parameters)):
                    f.write(self.parameters[j] + self.parametersValue[j][i] + '\n')
                f.write('----------------------------------------------------------------' + '\n')
                
              
    
            f.write(self.file_info[4] + '\n')               
            f.write('Steps' +self.file_info[2] + 'Voltage' + '\n')
            f.write( ' ' + self.file_info[2] + self.units[i] + '\n')
            for k in range(self.sessionData[0], self.sessionData[int(len(self.sessionData)-1)]):
                f.write(str(k+1) + self.file_info[2] + str(self.data[0][k]) + self.file_info[2] + '\n')
                
            
            f.write('\n')
            
            f.write(self.file_info[3] + '\n')
            
            
            f.close()
        else:
            self.autoSave()
        
    def autoSave(self):
        self.file_info[3] += '\\Session Data For ' + '' + str(self.file_info[0])
        # Create a folder at this address
        if not os.path.isdir(self.file_info[3]):
            os.makedirs(self.file_info[3])
        f_name = self.file_info[3] + '\\' + 'Session' + '' + str(self.i) + self.file_info[1]
        
        f = open(f_name, 'w')
        f.write('Comments:' + '\n')
        
        f.write('Session Number' + ' ' + str(self.i) + '\n')
        for j in range(0, len(self.parameters)):
            f.write(self.parameters[j] + self.parametersValue[j][self.i-1] + '\n')
        f.write('----------------------------------------------------------------' + '\n')

        f.write(self.file_info[4] + '\n')               
        f.write('Steps' +self.file_info[2] + 'Voltage' + '\n')
        f.write( ' ' + self.file_info[2] + self.units[self.i-1] + '\n')
        
        for k in range(0, int(self.sessionData[self.i]-self.sessionData[self.i-1])):
            f.write(str(k+1) + self.file_info[2] + str(self.data[0][k+int(self.sessionData[self.i-1])]) + self.file_info[2] + '\n')     
        
        f.write('\n')
        
        f.write(self.file_info[3] + '\n')
        
        
        f.close()
        print self.i
        
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
