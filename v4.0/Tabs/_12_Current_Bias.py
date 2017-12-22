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

import subprocess

from Save import Save_Thread

class Current_Bias():
    def __init__ (self, main, ui):

        self.ui = ui
        self.update_visas()
        self.collectDataThread = CollectData()
        self.save_thread = Save_Thread()
        # Set up guiqwt plot
        self.curve_item_current = make.curve([], [], color = 'b')
        self.ui.curvewidgetCurrent_CB.plot.add_item(self.curve_item_current)
        self.ui.curvewidgetCurrent_CB.plot.set_antialiasing(True)
        
        self.curve_item_voltage = make.curve([], [], color = 'b')
        self.ui.curvewidgetVoltage_CB.plot.add_item(self.curve_item_voltage)
        self.ui.curvewidgetVoltage_CB.plot.set_antialiasing(True)
        
        self.curve_item_conductance = make.curve([], [], color = 'b')
        self.ui.curvewidgetConductance_CB.plot.add_item(self.curve_item_conductance)
        self.ui.curvewidgetConductance_CB.plot.set_antialiasing(True)
        
        self.curve_item_resistance = make.curve([], [], color = 'b')
        self.ui.curvewidgetResistance_CB.plot.add_item(self.curve_item_resistance)
        self.ui.curvewidgetResistance_CB.plot.set_antialiasing(True)
        
        self.ui.pushButtonStart_CB.setEnabled(False)
        self.ui.pushButtonStop_CB.setEnabled(False)
        self.ui.pushButtonPause_CB.setEnabled(False)
        self.ui.pushButtonClear_CB.setEnabled(False)
        self.ui.pushButtonCloseAgilent_CB.setEnabled(False)
        self.ui.pushButtonCloseLockIn_CB.setEnabled(False)
        
        main.connect(self.ui.pushButtonUpdateVisas_CB, SIGNAL('clicked()'), self.update_visas)
        main.connect(self.ui.pushButtonSelectVisas_CB, SIGNAL('clicked()'), self.select_visas)
        main.connect(self.ui.pushButtonCloseAgilent_CB, SIGNAL('clicked()'), self.closeAgilent)
        main.connect(self.ui.pushButtonCloseLockIn_CB, SIGNAL('clicked()'), self.closeLockIn)
        main.connect(self.ui.pushButtonRetrieveVoltage_CB, SIGNAL('clicked()'), self.retrieve_inputs)
        
        
        main.connect(self.ui.pushButtonStart_CB, SIGNAL('clicked()'), self.start)
        main.connect(self.ui.pushButtonPause_CB, SIGNAL('clicked()'), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonStop_CB, SIGNAL('clicked()'), self.stop)
        main.connect(self.ui.pushButtonPause_CB, SIGNAL('clicked()'), self.append_parameters)
        main.connect(self.ui.pushButtonStop_CB, SIGNAL('clicked()'), self.append_parameters)
        main.connect(self.ui.pushButtonClear_CB, SIGNAL('clicked()'), self.reset_plots)
        
        main.connect(self.collectDataThread, SIGNAL('Plot'), self.plotData)
        main.connect(self.collectDataThread, SIGNAL('PreSave'), self.PreSave)
        
        main.connect(self.ui.pushButtonBrowse_CB, SIGNAL("clicked()"), self.browse)
        main.connect(self.ui.pushButtonSelectFolder_CB, SIGNAL("clicked()"), self.select_name)
        main.connect(self.ui.radioButtonCSV_CB, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.radioButtonTXT_CB, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.pushButtonSave_CB, SIGNAL("clicked()"), self.save)
        #Variables and Arrays
        self.lock_in_sens_list = [100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3]
        
        self.sens= []
        self.frequency= []
        self.amplitude= []
        self.phase = []
        self.QFactor = []
        self.filter = []
        self.trim_frequency = []
        self.slope = []
        self.reserve = []
        self.quadrant = []
        self.mode = []
        self.range = []
        self.coupling = []
        self.inputType = []
        self.floatground = []
        self.TimeConstant = []
        
    def update_visas(self):  
        visas = rm.list_resources()
        self.ui.comboBoxAgilent_CB.clear()
        self.ui.comboBoxLockIn_CB.clear()
        self.ui.labelCurrentAgilent_CB.setText("")
        self.ui.labelCurrentLockIn_CB.setText("")
        
        for i in visas:
            self.ui.comboBoxAgilent_CB.addItem(i)
            self.ui.comboBoxLockIn_CB.addItem(i)
        
    def select_visas(self):
        Agilent = str(self.ui.comboBoxAgilent_CB.currentText())
        self.Agilent = rm.open_resource(Agilent)
        LockIn = str(self.ui.comboBoxLockIn_CB.currentText())
        self.LockIn = rm.open_resource(LockIn)
        
        try:
            valid = self.check_Visas()
        except:
            valid = False
            
        if valid == True:
            self.ui.labelCurrentAgilent_CB.setText(str(self.Agilent.ask('*IDN?')))
            self.ui.labelCurrentLockIn_CB.setText(str(self.LockIn.ask('*IDN?')))
            self.ui.lineEditCondition_CB.setText('No errors with selected visas')
            self.ui.pushButtonStart_CB.setEnabled(True)
            self.ui.pushButtonCloseAgilent_CB.setEnabled(True)
            self.ui.pushButtonCloseLockIn_CB.setEnabled(True)
        else:
            self.ui.lineEditCondition_CB.setText('Error with visas')
    
    def check_Visas(self):
        try:
            self.Agilent.ask('*IDN?')
            self.LockIn.ask('*IDN?')
            valid = True
        except:
            valid = False
            
        return valid
    
    def closeAgilent(self):
        self.Agilent.close()
        self.ui.lineEditCondition_CB.setText('The visa for Agilent has been closed')
        self.ui.labelCurrentAgilent_CB.setText('')
    
    def closeLockIn(self):
        self.LockIn.close()
        self.ui.lineEditCondition_CB.setText('The visa for Lock In has been closed')
        self.ui.labelCurrentLockIn_CB.setText('')
        
    def retrieve_inputs(self):
        #Reading from the lock-in will return values of integers, these integers correspond to the actual settings read from the lock in. These arrays make sure the integers are converted to what the
        #settings were placed to.
        self.sens_conversion= ['100','200','500','1','2','5','10','20','50','100','200','500','1','2','5','10','20','50','100','200','500']
        self.tc_values = ['500 us','1 ms','3 ms','10 ms','30 ms', '100 ms','300 ms','1 s','3 s','10 s','30 s','100 s','300 s']
        self.qfactor_values = ['1','2','5','10','20','50','100']

            
        self.temp1 = self.sens_conversion[int(self.LockIn.ask('SENS?'))]
        if int(self.LockIn.ask('SENS?')) < 3:
            self.temp1 = self.temp1 + ' ' + 'nV'
        elif int(self.LockIn.ask('SENS?')) >= 3 and int(self.LockIn.ask('SENS ?')) < 12:
            self.temp1 = self.temp1 + ' ' + 'uV'
        else:
            self.temp1 = self.temp1 + ' ' + 'mV'
            
        self.ui.lineEditVoltageLockInSens_CB.setText(self.temp1)
        
        self.ui.lineEditFreq_CB.setText(str(self.LockIn.ask("FREQ?")).replace("\r\n", ""))
        self.ui.lineEditTrimFreq_CB.setText(str(self.LockIn.ask("IFFR?")).replace("\r\n", ""))
        self.ui.lineEditPhase_CB.setText(str(self.LockIn.ask("PHAS?")).replace("\r\n", ""))
        self.ui.lineEditAmplitude_CB.setText(str(self.LockIn.ask("SLVL?")).replace("\r\n", ""))
        self.ui.lineEditQFactor_CB.setText(self.qfactor_values[int(self.LockIn.ask("QFCT?"))])
        self.ui.lineEditTimeConstant_CB.setText(self.tc_values[int((self.LockIn.ask("OFLT?")))])
        
        #Depending on the integer returned from the lock-in, certain buttons will be pushed.
        if int(self.LockIn.ask('ISRC?')) == 0:
            self.ui.radioButtonA_CB.setChecked(True)
        else:
            self.ui.radioButtonAB_CB.setChecked(True)
            
        if int(self.LockIn.ask('ICPL?')) == 0:
            self.ui.radioButtonAC_CB.setChecked(True)
        else:
            self.ui.radioButtonDC_CB.setChecked(True)
            
        if int(self.LockIn.ask('IGND?')) == 0:
            self.ui.radioButtonFloat_CB.setChecked(True)
        else:
            self.ui.radioButtonGround_CB.setChecked(True)
        
        if int(self.LockIn.ask('TYPF?')) == 0:
            self.ui.radioButtonBandPass_CB.setChecked(True)
        elif int(self.LockIn.ask('TYPF?')) == 1:
            self.ui.radioButtonHighPass_CB.setChecked(True)
        elif int(self.LockIn.ask('TYPF?')) == 2:
            self.ui.radioButtonLowPass_CB.setChecked(True)
        elif int(self.LockIn.ask('TYPF?')) == 3:
            self.ui.radioButtonNotch_CB.setChecked(True)
        else:
            self.ui.radioButtonFlat_CB.setChecked(True)
            
        if int(self.LockIn.ask('QUAD?')) == 0:
            self.ui.radioButtonQuadrant1_CB.setChecked(True)
        elif int(self.LockIn.ask('QUAD?')) == 1:
            self.ui.radioButtonQuadrant2_CB.setChecked(True)
        elif int(self.LockIn.ask('QUAD?')) == 2:
            self.ui.radioButtonQuadrant3_CB.setChecked(True)
        else:
            self.ui.radioButtonQuadrant4_CB.setChecked(True)
            
        if int(self.LockIn.ask('FMOD?')) == 0:
            self.ui.radioButtonfMode_CB.setChecked(True)
        elif int(self.LockIn.ask('FMOD?')) == 1:
            self.ui.radioButtonInternalMode_CB.setChecked(True)
        elif int(self.LockIn.ask('FMOD?')) == 2:
            self.ui.radioButton2fMode_CB.setChecked(True)
        elif int(self.LockIn.ask('FMOD?')) == 3:
            self.ui.radioButton3fMode_CB.setChecked(True)
        else:
            self.ui.radioButtonReadMode_CB.setChecked(True)
            
        if int(self.LockIn.ask('FRNG?')) == 0:
            self.ui.radioButtonRange1_CB.setChecked(True)
        elif int(self.LockIn.ask('FRNG?')) == 1:
            self.ui.radioButtonRange2_CB.setChecked(True)
        elif int(self.LockIn.ask('FRNG?')) == 2:
            self.ui.radioButtonRange3_CB.setChecked(True)
        elif int(self.LockIn.ask('FRNG?')) == 3:
            self.ui.radioButtonRange4_CB.setChecked(True)
        else:
            self.ui.radioButtonRange5_CB.setChecked(True)
            
        if int(self.LockIn.ask('RMOD?')) == 0:
            self.ui.radioButtonHighRes_CB.setChecked(True)
        elif int(self.LockIn.ask('RMOD?')) == 1:
            self.ui.radioButtonNormal_CB.setChecked(True)
        else:
            self.ui.radioButtonLowNoise_CB.setChecked(True)
            
        if int(self.LockIn.ask('OFSL?')) == 0:
            self.ui.radioButton6dB_CB.setChecked(True)
        else:
            self.ui.radioButton12dB_CB.setChecked(True)
        self.LockIn.write('LOCL LOCAL')
        
        
    def start(self):
        self.ui.tabWidgetCB.setCurrentIndex(1)
        if self.ui.dialVoltageLockIn_CB.value() >=0 and self.ui.dialVoltageLockIn_CB.value() <= 2:
            self.LockIn_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_CB.value()]
            self.LockIn_magn = ['nV', 1E-9]
        elif self.ui.dialVoltageLockIn_CB.value() >=3 and self.ui.dialVoltageLockIn_CB.value() <= 11:
            self.LockIn_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_CB.value()]
            self.LockIn_magn = ['uV', 1E-6]
        else:
            self.LockIn_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_CB.value()]
            self.LockIn_magn = ['mV', 1E-3]
            
        self.ui.pushButtonStart_CB.setEnabled(False)
        self.ui.pushButtonPause_CB.setEnabled(True)
        self.ui.pushButtonStop_CB.setEnabled(True)
        self.ui.lineEditCondition_CB.setText('Running...')
        self.collectDataThread.input(self.ui, self.curve_item_current, self.curve_item_voltage, self.curve_item_conductance, self.curve_item_resistance, self.LockIn_sens, self.LockIn_magn, self.Agilent, self.LockIn)
        
    def plotData(self):
        self.curve_item_current.plot().replot()
        self.curve_item_voltage.plot().replot()
        self.curve_item_conductance.plot().replot()
        self.curve_item_resistance.plot().replot()
        self.ui.curvewidgetCurrent_CB.plot.do_autoscale()
        self.ui.curvewidgetVoltage_CB.plot.do_autoscale()
        self.ui.curvewidgetConductance_CB.plot.do_autoscale()
        self.ui.curvewidgetResistance_CB.plot.do_autoscale()

    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonClear_CB.setEnabled(True)
        self.ui.pushButtonStop_CB.setEnabled(False)
        self.ui.pushButtonPause_CB.setEnabled(False)
        self.ui.lineEditCondition_CB.setText("Stopped")
        
    def append_parameters(self):
        self.sens.append(self.temp1)
        self.frequency.append(str(self.ui.lineEditFreq_CB.text()))
        self.trim_frequency.append(str(self.ui.lineEditTrimFreq_CB.text()))
        self.amplitude.append(str(self.ui.lineEditAmplitude_CB.text()))
        self.phase.append(str(self.ui.lineEditPhase_CB.text()))
        self.QFactor.append(str(self.ui.lineEditQFactor_CB.text()))
        self.TimeConstant.append(str(self.ui.lineEditTimeConstant_CB.text()))
        
        if self.ui.radioButtonBandPass_CB.isChecked():
            self.filter.append('Band Pass')
        elif self.ui.radioButtonHighPass_CB.isChecked():
            self.filter.append('High Pass')
        elif self.ui.radioButtonLowPass_CB.isChecked():
            self.filter.append('Low Pass')
        elif self.ui.radioButtonNotch_CB.isChecked():
            self.filter.append('Notch')
        elif self.ui.radioButtonFlat_CB.isChecked():
            self.filter.append('Flat')
        else:
            self.filter = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Filter Type For Voltage')
            
        if self.ui.radioButton6dB_CB.isChecked():
            self.slope.append('6 dB/oct.')
        elif self.ui.radioButton12dB_CB.isChecked():
            self.slope.append('12 dB/oct.')
        else:
            self.slope = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Slope For Voltage')
            
        if self.ui.radioButtonHighRes_CB.isChecked():
            self.reserve.append('High Res')
        elif self.ui.radioButtonNormal_CB.isChecked():
            self.reserve.append('Normal')
        elif self.ui.radioButtonLowNoise_CB.isChecked():
            self.reserve.append('Low Noise')
        else:
            self.reserve = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Reserve For Voltage')
        
        if self.ui.radioButtonQuadrant1_CB.isChecked():
            self.quadrant.append('0-90')
        elif self.ui.radioButtonQuadrant2_CB.isChecked():
            self.quadrant.append('90-180')
        elif self.ui.radioButtonQuadrant3_CB.isChecked():
            self.quadrant.append('180-270')
        elif self.ui.radioButtonQuadrant4_CB.isChecked():
            self.quadrant.append('270-360')
        else:
            self.quadrant = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Quadrant For Voltage')
            
        if self.ui.radioButtonfMode_CB.isChecked():
            self.mode.append('f External')
        elif self.ui.radioButton2fMode_CB.isChecked():
            self.mode.append('2f External')
        elif self.ui.radioButton3fMode_CB.isChecked():
            self.mode.append('3f External')
        elif self.ui.radioButtonInternalMode_CB.isChecked():
            self.mode.append('Internal')
        elif self.ui.radioButtonRearMode_CB.isChecked():
            self.mode.append('Rear VCO')
        else:
            self.mode = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Mode For Voltage')
            
        if self.ui.radioButtonRange1_CB.isChecked():
            self.range.append('0.2-21 Hz')
        elif self.ui.radioButtonRange2_CB.isChecked():
            self.range.append('2.0-210 Hz')
        elif self.ui.radioButtonRange3_CB.isChecked():
            self.range.append('20-2.1k Hz')
        elif self.ui.radioButtonRange4_CB.isChecked():
            self.range.append('200-21k Hz')
        elif self.ui.radioButtonRange5_CB.isChecked():
            self.range.append('2.0k-210k Hz')
        else:
            self.range = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Frequency Range For Voltage')
            
        if self.ui.radioButtonAC_CB.isChecked():
            self.coupling.append('AC')
        elif self.ui.radioButtonDC_CB.isChecked():
            self.coupling.append('DC')
        else:
            self.coupling = ''
            self.ui.lineEditCondition.setText('Please Choose A Coupling For Voltage')
            
        if self.ui.radioButtonA_CB.isChecked():
            self.inputType.append('A')
        elif self.ui.radioButtonAB_CB.isChecked():
            self.inputType.append('A-B')
        else:
            self.inputType = ''
            self.ui.lineEditCondition_CB.setText('Please Choose An Input Type For Voltage')
            
        if self.ui.radioButtonFloat_CB.isChecked():
            self.floatground.append('Float')
        elif self.ui.radioButtonGround_CB.isChecked():
            self.floatground.append('Ground')
        else:
            self.floatground = ''
            self.ui.lineEditCondition_CB.setText('Please Choose A Float/Ground For Voltage')
            
        if self.ui.radioButtonOhms_CB.isChecked():
            self.resistor_unit = 'Ohms'
        elif self.ui.radioButtonkOhms_CB.isChecked():
            self.resistor_unit = 'kOhms'
        elif self.ui.radioButtonMOhms_CB.isChecked():
            self.resistor_unit = 'MOhms'
        else:
            self.resistor_unit = 'GOhms'
            
    def PreSave(self, Time, Steps, Current, Voltage, Conductance, Resistance):
        self.Time = Time
        self.Steps = Steps
        self.Current = Current
        self.Voltage = Voltage
        self.Conductance = Conductance
        self.Resistance = Resistance
        self.collectDataThread.save_ready == False
        
    def reset_plots(self):
        self.ui.pushButtonStart_CB.setEnabled(True)
        self.curve_item_current.set_data([],[])
        self.curve_item_voltage.set_data([],[])
        self.curve_item_conductance.set_data([],[])
        self.curve_item_resistance.set_data([],[])
        self.curve_item_current.plot().replot()
        self.curve_item_voltage.plot().replot()
        self.curve_item_conductance.plot().replot()
        self.curve_item_resistance.plot().replot()
        self.reset_check = True
        
    def browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select The GoogleDrive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEditDirectory_CB.setText(file_dir)
        self.directory = ''
        
    def select_name(self):
        file_list= []
        file_list = str(self.ui.lineEditDirectory_CB.text()).split('\\')
        for i in range(0, len(file_list)):
            self.directory += file_list[i] + '\\'
        namefolder = str(self.ui.comboBoxFolders_CB.currentText())
        if namefolder == 'None':
            self.ui.lineEditCondition_CB.setText('Please Choose A Folder To Save To.')
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
        if self.ui.radioButtonCSV_CB.isChecked() == True:
            self.type = '.csv'
            self.divide = ','
        elif self.ui.radioButtonTXT_CB.isChecked() == True:
            self.type = '.txt'
            self.divide = '\t'
            
    def save_name(self):
        if self.ui.radioButtonDateTime_CB.isChecked():
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            date_and_time = date + ' ' + current_time
            self.file_name = str(date_and_time)
        elif self.ui.radioButtonCustomName_CB.isChecked():
            self.file_name = str(self.ui.lineEditCustom_CB.text())
            
    def save(self):
        if self.ui.radioButtonCustomName_CB.isChecked() and self.ui.lineEditCustom_CB.text() == ' ':
            self.ui.lineEditStatus_CB.setText('Please Enter A Custom File Name')
        else:
            self.save_type()
            self.save_name()
        import datetime
        parameters_s = ['Sensitivity:', 'Frequency:', 'Amplitude:','Phase:','Trim Frequency:','Reserve:','Slope:', 'Q Factor:', 'Time Constant:', 'Filter Type:', 'Coupling:', 'Input:', 'Float/Ground:', 'Quadrant:','Mode:', 'Frequency Range:']
        parametersValue =[self.sens, self.frequency, self.amplitude, self.phase, self.trim_frequency, self.reserve, self.slope, self.QFactor, self.TimeConstant, self.filter, self.coupling, self.inputType, self.floatground, self.quadrant, self.mode,  self.range]
        
        comments = []
        parameters = []
        file_info = []
        units = []
        data = []
        divider = 'Collected Data'
        
        # First line user name
        temp = []
        temp.append('User Name:')
        temp.append(str(self.ui.comboBoxFolders_CB.currentText()))
        comments.append(temp)
        
        temp = []
        temp.append('Edit Time:')
        temp.append(str(datetime.datetime.now()))
        comments.append(temp)
        # Fourth line visa address
        temp = []
        temp.append('Agilent Visa Address:')
        temp.append(str(self.ui.comboBoxAgilent_CB.currentText()))
        comments.append(temp)
        # Fifth line visa name
        temp = []
        temp.append('Visa Name:')
        visa_name = self.Agilent.ask('*IDN?').rstrip('\n')
        visa_name = visa_name.replace(',', ' ')
        temp.append(visa_name)
        comments.append(temp)
        
        temp = []
        temp.append('Lock-In Visa Address:')
        temp.append(str(self.ui.comboBoxLockIn_CB.currentText()))
        comments.append(temp)

        temp = []
        temp.append('Visa Name:')
        visa_name = self.LockIn.ask('*IDN?').rstrip('\n')
        visa_name = visa_name.replace(',', ' ')
        temp.append(visa_name)
        comments.append(temp)

        # Sixth line scan source
        temp = []
        temp.append('Scan Source:')
        temp.append('Voltage')
        comments.append(temp)
        # Seventh line time step
        temp = []
        temp.append('Time Step(sec):')
        temp.append(str(self.ui.lineEditTimestep_VB.text()))
        comments.append(temp)
        
        temp = []
        temp.append('Output Voltage:')
        temp.append(str(self.ui.lineEditAmplitude_CB.text()) + ' ' + 'V')
        comments.append(temp)
        
        temp = []
        temp.append('Large Resistor Value:')
        temp.append(str(self.ui.lineEditResistor_CB.text()) + ' ' + self.resistor_unit)
        comments.append(temp)
        temp = []
        temp.append('Lock-In Parameters:')
        temp.append('')
        comments.append(temp)
              
        for i in range(0, len(parameters_s)):
            temp = []
            for j in range(0, len(self.sens)):
                temp.append(parameters_s[i])
                temp.append(parametersValue[i][j])
                comments.append(temp)
                
        # Eighth line comments
        temp = []
        temp.append('Comments:')
        temp.append(str(self.ui.textEditComments_CB.toPlainText()))
        comments.append(temp)
        
        parameters.append('Time')
        units.append('s')
        data.append(self.Time)
        
        parameters.append('Steps')
        units.append(' ')
        data.append(self.Steps)
        
        parameters.append('Current')
        units.append('A')
        data.append(self.Current)
        
        parameters.append('Voltage')
        units.append(self.LockIn_magn[0])
        data.append(self.Voltage)
        
        parameters.append('Conductance')
        units.append('S')
        data.append(self.Conductance)
        
        parameters.append('Resistance')
        units.append('Ohm')
        data.append(self.Resistance)
        
        file_info.append(self.file_name)
        file_info.append(self.type)
        file_info.append(self.divide)
        file_info.append(divider)
        file_info.append(self.directory)
        
        self.save_thread.input(comments, parameters, units, data, file_info)
        self.ui.lineEditCondition_CB.setText("Data has been saved")
        
class CollectData(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, curve_current, curve_voltage, curve_conductance, curve_resistance, LockIn_sens, LockIn_magn, Agilent, LockIn ):
        self.ui = ui
        self.curve_current = curve_current
        self.curve_voltage = curve_voltage
        self.curve_conductance = curve_conductance
        self.curve_resistance = curve_resistance
        self.LockIn_sens = LockIn_sens
        self.LockIn_magn = LockIn_magn
        self.Agilent = Agilent
        self.LockIn = LockIn
        
        self.Current = np.array([], dtype = float)
        self.Voltage = np.array([], dtype = float)
        self.Conductance = np.array([], dtype = float)
        self.Resistance = np.array([], dtype = float)
        self.Steps = np.array([], dtype = float)
        self.Time = np.array([], dtype = float)
        
        self.n = 0
        
        try:
            self.Agilent.ask('MEAS:VOLT?')
        except:
            self.ui.lineEditCondition_CB.setText("Error")
        if self.ui.radioButtonOhms_CB.isChecked():
            self.Resistor_Value = float(self.ui.lineEditResistor_CB.text())
        elif self.ui.radioButtonkOhms_CB.isChecked():
            self.Resistor_Value = float(self.ui.lineEditResistor_CB.text())*1E3
        elif self.ui.radioButtonMOhms_CB.isChecked():
            self.Resistor_Value = float(self.ui.lineEditResistor_CB.text())*1E6
        else:
            self.Resistor_Value = float(self.ui.lineEditResistor_CB.text())*1E9
        self.Output_Voltage = float(self.LockIn.ask("SLVL?"))
        self.pauseLoop = False
        self.save_ready = True
        self.start()
        
    def run(self):
        start_time = time.time()
        while True:
            if not self.pauseLoop:
                self.Timestep = float(self.ui.lineEditTimestep_CB.text())              
                self.CurrentReading = self.Output_Voltage/self.Resistor_Value
                self.VoltageReading = float(self.Agilent.ask('READ?'))*self.LockIn_sens/10
                self.ConductanceValue = self.CurrentReading/self.VoltageReading
                self.ResistanceValue = self.VoltageReading/self.CurrentReading
                self.Current = np.append(self.Current, self.CurrentReading)
                self.Voltage = np.append(self.Voltage, self.VoltageReading)
                self.Conductance = np.append(self.Conductance, self.ConductanceValue)
                self.Resistance = np.append(self.Resistance, self.ResistanceValue)
                end_time = time.time()
                t = end_time - start_time
                self.Time = np.append(self.Time, t)
                self.Steps = np.append(self.Steps, self.n + 1)
                self.ui.labelCurrentValue_CB.setText(str(self.Current[self.n]) + ' ' + 'A')
                self.ui.labelVoltageValue_CB.setText(str(self.Voltage[self.n]/self.LockIn_magn[1]) + ' ' + self.LockIn_magn[0])
                self.ui.labelConductanceValue_CB.setText(str(self.Conductance[self.n]) + ' ' + 'S')
                self.ui.labelResistanceValue_CB.setText(str(self.Resistance[self.n]) + ' ' + 'Ohms')
                if self.ui.radioButtonScaleTime_CB.isChecked():
                    self.curve_current.set_data(self.Time, self.Current)
                    self.curve_voltage.set_data(self.Time, self.Voltage/self.LockIn_magn[1])
                    self.curve_conductance.set_data(self.Time, self.Conductance)
                    self.curve_resistance.set_data(self.Time, self.Resistance)
                    self.ui.curvewidgetCurrent_CB.plot.set_titles('Current vs. Time', 'Time (s)', 'Current (A)')
                    self.ui.curvewidgetVoltage_CB.plot.set_titles('Voltage vs. Time', 'Time (s)', 'Voltage ( ' + self.LockIn_magn[0] + ')')
                    self.ui.curvewidgetConductance_CB.plot.set_titles('Conductance vs. Time', 'Time (s)', 'Conductance (S)')
                    self.ui.curvewidgetResistance_CB.plot.set_titles('Resistance vs. Time', 'Time(s)', 'Resistance (Ohm)')
                else:
                    self.curve_current.set_data(self.Steps, self.Current)
                    self.curve_voltage.set_data(self.Steps, self.Voltage/self.LockIn_magn[1])
                    self.curve_conductance.set_data(self.Steps, self.Conductance)
                    self.curve_resistance.set_data(self.Steps, self.Resistance)
                    self.ui.curvewidgetCurrent_CB.plot.set_titles('Current vs. Steps', 'Steps', 'Current (A)')
                    self.ui.curvewidgetVoltage_CB.plot.set_titles('Voltage vs. Steps', 'Steps', 'Voltage ( ' + self.LockIn_magn[0] + ')')
                    self.ui.curvewidgetConductance_CB.plot.set_titles('Conductance vs. Steps', 'Steps', 'Conductance (S)')
                    self.ui.curvewidgetResistance_CB.plot.set_titles('Resistance vs. Steps', 'Steps', 'Resistance (Ohm)')
                    
                self.emit(SIGNAL('Plot'))
                self.n += 1
                time.sleep(self.Timestep)
            elif self.pauseLoop:
                self.ui.lineEditCondition_VB.setText('Paused')
                if self.save_ready == True:
                    Time = self.Time
                    Steps = self.Steps
                    Current = self.Current
                    Voltage = self.Voltage
                    Conductance = self.Conductance
                    Resistance = self.Resistance
                    self.emit(SIGNAL('PreSave'), Time, Steps, Current, Voltage, Conductance, Resistance)
                else:
                    pass
                
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            self.ui.lineEditCondition_CB.setText("Running")
            self.ui.pushButtonPause_CB.setText('Pause')

        else:
            self.pauseLoop = True
            self.ui.lineEditCondition_CB.setText("Paused")
            self.ui.pushButtonPause_CB.setText("Continue")