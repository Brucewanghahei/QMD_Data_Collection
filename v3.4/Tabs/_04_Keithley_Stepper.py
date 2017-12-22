""""Written by Landry Horimbere
    Contact landryh91@gmail.com for any question."""


""" To compile the .ui file created with Qt Designer into a  Python file do the following:
    1. Open Command Prompt and change the directory, using "chdir" command, to the directory that contains the .ui file
    2. Type: pyuic4 example.ui>example.py
      (use your .ui name instead of example above)
    3. That is all there is to it. Now there is python module "example.py"  with all the code from the .ui file that one can import
    4. Do not change any of the code in the new "example.py" file because recompiling any new changed in the .ui file will delete your changes
    C:\Users\QMDla\Google Drive\03 User Accounts\Horimbere\Measure\GUI> pyuic4 Measure.ui>Measure.py"""

# Import the visa library
try:
    import visa
    VISA_MOD_AVAILABLE = True
except:
    VISA_MOD_AVAILABLE = False

# System library is imported
import os
import sys
import time
import numpy
import datetime

# Import the PyQt4 modules for all the commands that control the GUI.
# Note: Importing as from "Module" import * implies that everything from that module is not part of this module.
# And one does not have to put the module name before its commands. (Example: import numpy as np --> np.sin(x)   where as: from numpy import * --> sin(x))
from PyQt4.QtCore import * 
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QTAgg as NavigationToolbar)
from matplotlib.figure import Figure

# This imports the GUI created earlier using Qt Designer
# This is how to import from a sub directory in python.
# To do this though, one must create a __init__.py file in sub folder. It does not have to have anything in it, but just has to have that name.
# It is how python know that this is a sub directory to import from. Just create a new text file and save it to this folder than rename it to __init__.py
# The syntax to import from a sub folder is as follows: SUB_FOLDER_NAME.MODULE_NAME
#from GUI.Keithley_Stepper import Ui_MainWindow

# The MyForm class only bares the minimum amount of code to pop up and run the GUI
class Keithley_Stepper():
    
    # The __init__ function is what is everything the user wants to be initialized when the class is called.
    # Here we shall define the trig functions to corresponding variables.
    # Note that the "self" variable means that the function is part of the class and can be called inside and outside the class.(Although __init__ is special.)
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        
        self.ui.sendButton.setDisabled(True)
        # The zero button is  disabled
        self.ui.zeroButton.setDisabled(True)
        # The up button is  disabled
        self.ui.upButton.setDisabled(True)
        # The down button is  disabled
        self.ui.downButton.setDisabled(True)
        # The closeVisa button is  disabled
        self.ui.closeVisaButton.setDisabled(True)
        
        self.target = None
        self.V = None
        self.DV = None
        
        self.voltage = []
        self.current = []
        self.time = []
        self.range = []
        self.tik = 0
        
        self.timeStep = .5
        self.ui.timeStepValue.setText(str(self.timeStep))
        self.ui.defaultFile.setChecked(True)
        
        """exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)"""
        
        self.action_timer = QTimer()
        self.reset_plot()
        
        self.directory = 'C:\\'
        self.update_folders()
        self.ui.directory.setText(self.directory)
        
        main.connect(self.ui.selectVisaButton, SIGNAL("clicked()"), self.select_visa)
        main.connect(self.ui.updateVisaButton, SIGNAL("clicked()"), self.update_visa)
        
        main.connect(self.ui.sendButton, SIGNAL("clicked()"), self.send)
        main.connect(self.action_timer, SIGNAL("timeout()"), self.action)
        
        main.connect(self.ui.input, SIGNAL("returnPressed()"), self.send)
        main.connect(self.ui.upButton, SIGNAL("clicked()"), self.up)
        main.connect(self.ui.downButton, SIGNAL("clicked()"), self.down)
        #main.connect(self.ui.quitButton, SIGNAL("clicked()"), self.close)
        main.connect(self.ui.zeroButton, SIGNAL("clicked()"), self.zero)
        main.connect(self.ui.closeVisaButton, SIGNAL("clicked()"), self.close_visa)
        main.connect(self.ui.browseButton, SIGNAL("clicked()"), self.browse)
        main.connect(self.ui.saveButton, SIGNAL("clicked()"), self.save)
        #self.connect(self.ui.folderName, SIGNAL("clicked()"), self.select_directory)
        
    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def ranger(self):
        self.range.append(self.tik)
        self.tik = self.tik + 1
        self.range.append(self.tik)
        return self.range

    def action(self):     
        if self.DV <= 0 or self.timeStep <= 0:
            self.ui.error.setText("Enter a positive voltage step value.")
            self.action_timer.stop()
        else:
            if (self.target - self.V) > self.DV and abs(self.target - self.V) > self.DV:
                self.up_one(self.DV)
                self.V = float(self.visa_chosen.query('MEAS:VOLT?'))
                time.sleep(self.timeStep)
                
            elif (self.target - self.V) < self.DV and abs(self.target - self.V) > self.DV:
                self.down_one(self.DV)
                self.V = float(self.visa_chosen.query('MEAS:VOLT?'))
                time.sleep(self.timeStep)
                
            else:
                self.visa_chosen.write('SOUR:VOLT ' + str(self.target))
                vol = float(self.visa_chosen.query('MEAS:VOLT?'))
                self.voltage.append(vol)
                self.voltage.append(vol)
                curr = float(self.visa_chosen.query('MEAS:CURR?'))
                self.current.append(curr)
                self.current.append(curr)
                self.time.append(datetime.datetime.now())
                self.time.append(datetime.datetime.now())
                self.ui.output.setText(str(self.voltage))
                self.ui.voltage.setText(str(self.voltage[len(self.voltage)-1]))
                self.ui.current.setText(str(self.current[len(self.current)-1]))
                
                self.reset_plot()
                self.axes0.plot(self.ranger(), self.voltage)
                self.axes1.plot(self.range, self.current)
                self.ui.plot.draw()
                self.action_timer.stop()
    
    def up(self):
        try:
            DV = float(self.ui.stepValue.text())
        except:
            DV = 0       
            
        if DV <= 0 or self.timeStep <= 0:
            self.ui.error.setText("Enter a positive voltage step value.")
            self.action_timer.stop()
        else:
            self.up_one(DV)
            
    def down(self):
        try:
            DV = float(self.ui.stepValue.text())
        except:
            DV = 0        
            
        if DV <= 0 or self.timeStep <= 0:
            self.ui.error.setText("Enter a positive voltage step value.")
            self.action_timer.stop()
        else:
            self.down_one(DV)
    
    def up_one(self,DV):
        try:
            V = float(self.visa_chosen.query('MEAS:VOLT?'))
            if DV <= 0:
                self.ui.error.setText("Enter a positive voltage step value: ")
            else:
                self.visa_chosen.write('SOUR:VOLT ' + str(V + DV))
                vol = float(self.visa_chosen.query('MEAS:VOLT?'))
                self.voltage.append(vol)
                self.voltage.append(vol)
                curr = float(self.visa_chosen.query('MEAS:CURR?'))
                self.current.append(curr)
                self.current.append(curr)
                self.time.append(datetime.datetime.now())
                self.time.append(datetime.datetime.now())
                self.ui.output.setText(str(self.voltage))
                self.ui.voltage.setText(str(self.voltage[len(self.voltage)-1]))
                self.ui.current.setText(str(self.current[len(self.current)-1]))
                
                self.reset_plot()
                self.axes0.plot(self.ranger(), self.voltage)
                self.axes1.plot(self.range, self.current)
                self.ui.plot.draw()
        except Exception, e:
            self.ui.error.setText(str(e))
        
    def down_one(self,DV):
        try:
            V = float(self.visa_chosen.query('MEAS:VOLT?'))
            if DV <= 0:
                self.ui.error.setText("Enter a positive voltage step value.")
            else:
                self.visa_chosen.write('SOUR:VOLT ' + str(V - DV))
                vol = float(self.visa_chosen.query('MEAS:VOLT?'))
                self.voltage.append(vol)
                self.voltage.append(vol)
                curr = float(self.visa_chosen.query('MEAS:CURR?'))
                self.current.append(curr)
                self.current.append(curr)
                self.time.append(datetime.datetime.now())
                self.time.append(datetime.datetime.now())
                self.ui.output.setText(str(self.voltage))
                self.ui.voltage.setText(str(self.voltage[len(self.voltage)-1]))
                self.ui.current.setText(str(self.current[len(self.current)-1]))
                
                self.reset_plot()
                self.axes0.plot(self.ranger(), self.voltage)
                self.axes1.plot(self.range, self.current)
                self.ui.plot.draw()
        except Exception, e:
            self.ui.error.setText(str(e))
    
    def zero(self):
        self.V = float(self.visa_chosen.query('MEAS:VOLT?'))
        
        try:
            self.DV = float(self.ui.stepValue.text())
        except:
            self.DV = 0
        
        try:
            self.timeStep = float(self.ui.timeStepValue.text())
        except:
            self.ui.error.setText("There is a problem with the time step.")
        
        if self.DV <= 0 or self.timeStep <= 0:
            self.ui.error.setText("Enter a positive voltage and time step value.")
        else:
            self.target = 0
            self.action_timer.start(1000.0*self.timeStep)

    def update_visa(self):
        try:
            visas = self.rm.list_resources()
        except:
            visas = ''
        
        current_visa = self.ui.visa.text()
        
        check_current = False
        
        self.ui.selectVisa.clear()

        for each_visa in visas:
            if current_visa == each_visa:
                check_current = True
            self.ui.selectVisa.addItem(each_visa)
        
        if check_current == False:
            self.ui.visa.setText("None")
            self.ui.sendButton.setDisabled(True)
            self.ui.zeroButton.setDisabled(True)
            self.ui.upButton.setDisabled(True)
            self.ui.downButton.setDisabled(True)
            self.ui.closeVisaButton.setDisabled(True)
    

    def select_visa(self):
        visa_chosen = str(self.ui.selectVisa.currentText())

        try:
            inst = self.rm.open_resource(visa_chosen)
            self.ui.output.setText(inst.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa.setText(visa_chosen)
            self.ui.error.setText("None")
            self.visa_chosen = inst
            self.ui.sendButton.setDisabled(False)
            self.ui.zeroButton.setDisabled(False)
            self.ui.upButton.setDisabled(False)
            self.ui.downButton.setDisabled(False)
            self.ui.closeVisaButton.setDisabled(False)

            self.voltage.append(float(self.visa_chosen.query('MEAS:VOLT?')))
            self.current.append(float(self.visa_chosen.query('MEAS:CURR?')))
            self.time.append(datetime.datetime.now())
            self.range.append(self.tik)
            self.ui.voltage.setText(str(self.voltage[len(self.voltage)-1]))
            self.ui.current.setText(str(self.current[len(self.current)-1]))
        
        elif valid == False:
            self.ui.error.setText("Invalid Visa Port.")
            self.ui.visa.setText("None")
            self.visa_chosen = False
            self.ui.sendButton.setDisabled(True)
            self.ui.zeroButton.setDisabled(True)
            self.ui.upButton.setDisabled(True)
            self.ui.downButton.setDisabled(True)
            self.ui.closeVisaButton.setDisabled(True)
    
    def close_visa(self):
        try:
            self.ui.output.setText(self.visa_chosen.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa.setText('None')
            self.ui.error.setText("None")
            self.visa_chosen.close()
        
        elif valid == False:
            self.ui.error.setText("No visa connected.")
            self.ui.visa.setText("None")
        
        self.update_visa()
        
        self.visa_chosen = False
        self.ui.sendButton.setDisabled(True)
        self.ui.zeroButton.setDisabled(True)
        self.ui.upButton.setDisabled(True)
        self.ui.downButton.setDisabled(True)
        self.ui.closeVisaButton.setDisabled(True)
    
    def send(self):
        command = str(self.ui.input.text())
        if command != "":
            if self.is_number(command):
                self.visa_chosen.write('OUTP ON')
                self.target = float(command)
                self.V = float(self.visa_chosen.query('MEAS:VOLT?'))
                
                try:                    
                    self.DV = float(self.ui.stepValue.text())
                except:
                    self.DV = 0
                
                try:
                    self.timeStep = float(self.ui.timeStepValue.text())
                    self.action_timer.start(1000.0*self.timeStep)
                except:
                    self.ui.error.setText("There is a problem with the time step.")
            else:
                self.ui.error.setText("There is a problem with you target.")
        else:
            self.ui.error.setText("No command given.")

    def reset_plot(self):
        self.ui.plot.figure.clear()
        self.axes0 = self.ui.plot.figure.add_subplot(211)
        self.axes1 = self.ui.plot.figure.add_subplot(212)
        
        self.axes0.set_title("Voltage vs. Steps")
        self.axes0.set_ylabel("Voltage")
        
        self.axes1.set_title("Current vs. Steps")
        self.axes1.set_xlabel("Steps")
        self.axes1.set_ylabel("Current")
    
    
    def browse(self):
        prev_dir = 'C:\\'
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
            self.ui.directory.setText('Open Google Drive User Folder')
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
            self.directories = numpy.array(os.listdir(self.directory))
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
        #self.select_directory()
        if self.file == '':
            self.ui.output.setText('Please enter a valid file name.')
            return
        else:
            # This the name of the file
            self.name = self.file + self.type
            # This the path of the file
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
                    self.path = self.path + '\\' + 'Keithley Manual Measure'
                    # Create a folder at this address
                    if not os.path.isdir(self.path):
                        os.makedirs(self.path)
                    self.path = self.path + '\\' + self.name
            #print str(self.path)
            f = open(self.path, 'w')
            # The beginning of the file is name and time
            f.write('Name' + self.divide + self.name + '\n')
            f.write('Time' + self.divide + str(self.date_and_time) + '\n')
            f.write('\n')
            
            # First part of the file is labels and parameters
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
        #self.ui.saveButton.setEnabled(True)
            
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
