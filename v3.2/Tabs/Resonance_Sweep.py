import visa
rm = visa.ResourceManager()
visas = rm.list_resources()
import string
import numpy as np
import matplotlib.pyplot as plt

import time
from datetime import datetime

from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from Resonant_GUI.GUI import Ui_MainWindow
import subprocess

class Resonance_Sweep():
    def __init__ (self, main, ui):

        self.ui = ui
        self.update_visa()
        
        self.collectDataThread = CollectData()
        
        self.curve_item = make.curve([], [], color='b')
        self.ui.curvewidgetPlot.plot.add_item(self.curve_item)
        self.ui.curvewidgetPlot.plot.set_antialiasing(True)
        self.ui.curvewidgetPlot.plot.set_titles("Title", "X-Axis", "Y-Axis")
        
        self.ui.pushButtonStopRS.setEnabled(False)
        self.ui.pushButtonPauseRS.setEnabled(False)
        
        main.connect(self.ui.pushButtonSelectRS, SIGNAL("clicked()"), self.choose_visa)
        main.connect(self.ui.pushButtonUpdateRS, SIGNAL("clicked()"), self.update_visa)
        main.connect(self.ui.pushButtonSourceSelectRS, SIGNAL("clicked()"), self.choose_visa)
        main.connect(self.ui.pushButtonSourceUpdateRS, SIGNAL("clicked()"), self.update_visa)
        main.connect(self.ui.pushButtonStartRS, SIGNAL("clicked()"), self.start)
        main.connect(self.ui.pushButtonStopRS, SIGNAL("clicked()"), self.stop)
        main.connect(self.ui.pushButtonPauseRS, SIGNAL("clicked()"), self.collectDataThread.pause)
        main.connect(self.collectDataThread, SIGNAL("plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("stop"), self.stop)
        
        
    def update_visa(self):
        rm = visa.ResourceManager()
        try:
            visas = rm.list_resources()
        except:
            visas = "There are currently no connected visas."
            
        #Clears previous items in list
        self.ui.comboBoxReadList.clear()
        self.ui.labelCurrentVisa.clear()
        self.ui.comboBoxSourceList.clear()
        self.ui.labelCurrentSourceVisa.clear()
        #Adds all currently connected visas into comboBox
        for each_visa in visas:
            self.ui.comboBoxReadList.addItem(each_visa)
            self.ui.comboBoxSourceList.addItem(each_visa)
            
            
    def choose_visa(self):
        current_visa = str(self.ui.comboBoxReadList.currentText())
        current_visa2 = str(self.ui.comboBoxSourceList.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst1 = rm.open_resource(current_visa)
        inst2 = rm.open_resource(current_visa2)
        try:
            valid = self.check_visa(inst1,inst2)
        except:
            self.ui.labelCurrentVisa.setText("")
            
        
        if valid == True:
            self.ui.labelCurrentVisa.setText(current_visa)
            self.chosen_visa = inst1
            self.ui.labelCurrentSourceVisa.setText(current_visa2)
            self.chosen_visa2 = inst2
            self.ui.pushButtonStartRS.setDisabled(False)

        elif valid == False:
            self.ui.labelCurrentVisa.setText("Error")
            self.ui.labelCurrentSourceVisa.setText("Error")
            self.ui.pushButtonStartRS.setDisabled(True)
            
    #Makes sure the visa is valid/functioning before selecting it
    def check_visa(self,inst1, inst2):
        try:
            inst1.ask("*IDN?")
            inst2.ask("*IDN?")
            valid = True
        except:
            valid = False
            
        return valid

    def start(self):
        self.collectDataThread.input(self.ui, self.curve_item, [], [])
        self.ui.pushButtonStartRS.setEnabled(False)
        self.ui.pushButtonStopRS.setEnabled(True)
        self.ui.pushButtonPauseRS.setEnabled(True)
        
    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()
        self.collectDataThread.visa2.write('OUTP OFF')
        self.ui.pushButtonStartRS.setEnabled(True)
        self.ui.pushButtonStopRS.setEnabled(False)
        self.ui.pushButtonPauseRS.setEnabled(False)
        
    def plotData(self, dataX, dataY):
        self.curve_item.plot().replot()
        self.ui.curvewidgetPlot.plot.do_autoscale()
        
    # def closeEvent(self, question):
    #     print question
    #     quit_msg = "Do you want to quit this program?"
    #     reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         question.accept()
    #     else:
    #         question.ignore()
            
class CollectData(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, curve, dataX, dataY):
        self.curve = curve
        self.dataX = np.array([], dtype = float)
        self.dataY = np.array([], dtype = float)
        self.ui = ui
        self.t1 = time.clock()
        self.pauseLoop = False
        self.temp = np.array([], dtype = str)
        self.plot_check = True
        self.start()
        self.n = 0
        self.initial = True

    #Lets the collectDataThread know that the visa is good
    def check_visa(self,inst1, inst2):
        try:
            inst1.ask('*IDN?')
            inst2.ask('*IDN?')
            valid = True
        except:
            valid = False
        return valid
        
    def run(self):
        while True:
            if self.pauseLoop == False:
                collect_check = True
                
                current_visa = str(self.ui.comboBoxReadList.currentText())
                current_visa2 = str(self.ui.comboBoxSourceList.currentText())
                rm = visa.ResourceManager()
                rm.list_resources()
                inst1 = rm.open_resource(current_visa)
                inst2 = rm.open_resource(current_visa2)
                self.visa1 = inst1
                self.visa2 = inst2
                #Reads the lines of certain inputs before collecting to make sure they are valid
                try:
                    self.timestep = float(self.ui.lineEditTimestepRS.text())
                    self.sweepstep = float(self.ui.lineEditSweepStepRS.text())
                    
                except:
                    self.timestep = -1
                    
                if self.timestep <= 0:
                    #Lets the program know that it is not okay to start collecting data
                    collect_check = False
                #If the program is given the okay to collect data, this is run    
                if collect_check == True:
                    #Ensures that the visa data is collected from is valid
                    valid = self.check_visa(inst1,inst2)
                    
                    if valid == True:
                        #self.ui.labelErrorStatus.setText("Running...No errors")
                        #Established the command that the visa is going to be asked
                        self.command = "Read?"
                

                        #Defines the array, magnitude, that contains information that will used for data analysis and other functions
                        if self.ui.radioButtonHz_RS.isChecked() == True:
                            magnitude = ['HZ', 1]
                        elif self.ui.radioButtonkHz_RS.isChecked() == True:
                            magnitude = ['KHZ', 1E3]
                        elif self.ui.radioButtonMHz_RS.isChecked() == True:
                            magnitude = ['MHZ', 1E6]
                        if self.ui.radioButtonEndHzRS.isChecked() == True:
                            magnitude2 = ['HZ', 1]
                        elif self.ui.radioButtonEndkHzRS.isChecked() == True:
                            magnitude2 = ['KHZ', 1E3]
                        elif self.ui.radioButtonEndMHzRS.isChecked() == True:
                            magnitude2 = ['MHZ', 1E6]
                            
                        #Sets the axes of the plots
                        self.ui.curvewidgetPlot.plot.set_titles("Resonance Sweep", "Frequency (Hz)", "Voltage(V)")
                        start = float(self.ui.lineEditStartFrequencyRS.text())
                        end = float(self.ui.lineEditEndFrequencyRS.text())

                        try:
                            #Collects the data, ensuring that it will in the units of Volts
                            reading = float(self.visa1.ask(self.command))
                            check = True
                        except:
                            #If the visa fails to respond to the command, this will shut down the process and lets the user know of an error
                            check = False
                            valid = self.check_visa(self.chosen_visa)
                            
                        #Otherwise if given the okay, the program is told to append arrays for plotting and analysis
                        if check == True:

                            self.visa2.write('OUTP ON')
                            i = int((end-start)/self.sweepstep)
                            print i
                            if self.initial == True:
                                self.initial = False
                                for n in range(1,i+1):
                                    self.dataX = np.append(self.dataX, (float(self.ui.lineEditStartFrequencyRS.text()) + self.sweepstep*n))
                                    self.temp = np.append(self.temp, (str(float(self.ui.lineEditStartFrequencyRS.text()) + self.sweepstep*n) + ' ' + magnitude[0]))
                            elif self.initial == False:
                                pass
                                
                            
                            #Appends the data into the appropriate array
                            self.visa2.write('FREQ' + ' ' + self.temp[self.n])
                            self.dataY = np.append(self.dataY, float(str(self.visa1.ask('READ?'))))
                            self.curve.set_data(self.dataX, self.dataY)
                            dataX = self.dataX
                            dataY = self.dataY
                            
                            if len(self.dataY) < len(self.dataX):
                                self.n += 1
                            elif len(self.dataY) == len(self.dataX):
                                self.n +=0
                                self.visa2.write('OUTP OFF')
                                self.emit(SIGNAL("stop"))



                                
                            #dataX = self.dataX
                            #dataY = self.dataX

                            # print len(self.dataY)
                            # print len(self.dataX)
                            # print self.temp
                            # print self.dataY
                        # if self.plot_check == True:
                        #     if len(self.dataY) == len(self.dataX):
                        #         self.visa2.write('OUTP OFF')
                        #         self.emit(SIGNAL("stop"))




                            # if self.i_plot >= int(self.ui.lineEditPlotEvery.text()) and scale == 'Time':
                            #     self.curve.set_data(self.dataX, self.dataY/magnitude[1])                                
                            #     self.i_plot = 0
                            #     #Redefines the self variables to normal variables so they can be emitted through a signal
                            #     dataPoints = self.dataY/magnitude[1]
                            #     dataTime = self.dataX
                            #     sessionData = self.sessionData
                            # elif self.i_plot >=  int(self.ui.lineEditPlotEvery.text()) and scale == 'Steps':
                            #     self.curve.set_data(self.Steps, self.dataY/magnitude[1])                                
                            #     self.i_plot = 0
                            #     #Redefines the self variables to normal variables so they can be emitted through a signal
                            #     dataPoints = self.dataY/magnitude[1]
                            #     dataTime = self.dataX
                            #     sessionData = self.sessionData
                            # else:
                            #     self.i_plot += 1
                            #     
                        else:
                            self.stop() 
                self.emit(SIGNAL("plot"), dataX, dataY)
                # if len(self.dataY) == len(self.dataX):
                #     self.visa2.write('OUTP OFF')
                #     self.emit(SIGNAL("stop"))
                time.sleep(self.timestep)
            else:
                pass
                           
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
        else:
            self.pauseLoop = True
            self.visa2.write('OUTP OFF')



    
    def __del__(self):
        self.exiting = True
        self.wait()
        