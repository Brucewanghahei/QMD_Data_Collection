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

class Voltage_Bias():
    def __init__ (self, main, ui):

        self.ui = ui
        self.update_visa()

        self.collectDataThread = CollectData()
        self.save_thread = Save_Thread()
        # Set up guiqwt plot
        self.curve_item_current = make.curve([], [], color = 'b')
        self.ui.curvewidgetCurrent_VB.plot.add_item(self.curve_item_current)
        self.ui.curvewidgetCurrent_VB.plot.set_antialiasing(True)
        
        self.curve_item_voltage = make.curve([], [], color = 'b')
        self.ui.curvewidgetVoltage_VB.plot.add_item(self.curve_item_voltage)
        self.ui.curvewidgetVoltage_VB.plot.set_antialiasing(True)
        
        self.curve_item_conductance = make.curve([], [], color = 'b')
        self.ui.curvewidgetConductance_VB.plot.add_item(self.curve_item_conductance)
        self.ui.curvewidgetConductance_VB.plot.set_antialiasing(True)
        
        self.curve_item_resistance = make.curve([], [], color = 'b')
        self.ui.curvewidgetResistance_VB.plot.add_item(self.curve_item_resistance)
        self.ui.curvewidgetResistance_VB.plot.set_antialiasing(True)
        
        self.ui.pushButtonStart_VB.setEnabled(False)
        self.ui.pushButtonStop_VB.setEnabled(False)
        self.ui.pushButtonPause_VB.setEnabled(False)
        self.ui.pushButtonClear_VB.setEnabled(False)
        self.ui.pushButtonCloseCurrentAgilent_VB.setEnabled(False)
        self.ui.pushButtonCloseCurrentLockIn_VB.setEnabled(False)
        self.ui.pushButtonCloseVoltageAgilent_VB.setEnabled(False)
        self.ui.pushButtonCloseVoltageLockIn_VB.setEnabled(False)
        
        main.connect(self.ui.pushButtonUpdateCurrentVisas_VB, SIGNAL('clicked()'), self.update_visa)
        main.connect(self.ui.pushButtonUpdateVoltageVisas_VB, SIGNAL('clicked()'), self.update_visa)
        main.connect(self.ui.pushButtonSelectCurrentVisas_VB, SIGNAL('clicked()'), self.select_CurrentVisas)
        main.connect(self.ui.pushButtonSelectVoltageVisas_VB, SIGNAL('clicked()'), self.select_VoltageVisas)
        
        main.connect(self.ui.pushButtonCloseCurrentAgilent_VB, SIGNAL('clicked()'), self.close_CurrentAgilent)
        main.connect(self.ui.pushButtonCloseCurrentLockIn_VB, SIGNAL('clicked()'), self.close_CurrentLockIn)
        main.connect(self.ui.pushButtonCloseVoltageAgilent_VB, SIGNAL('clicked()'), self.close_VoltageAgilent)
        main.connect(self.ui.pushButtonCloseVoltageLockIn_VB, SIGNAL('clicked()'), self.close_VoltageLockIn)
        
        main.connect(self.ui.pushButtonRetrieveCurrent_VB, SIGNAL('clicked()'), self.retrieve_Current_inputs)
        main.connect(self.ui.pushButtonRetrieveVoltage_VB, SIGNAL('clicked()'), self.retrieve_Voltage_inputs)
        
        main.connect(self.ui.pushButtonStart_VB, SIGNAL('clicked()'), self.start)
        main.connect(self.ui.pushButtonPause_VB, SIGNAL('clicked()'), self.collectDataThread.pause)
        main.connect(self.ui.pushButtonStop_VB, SIGNAL('clicked()'), self.stop)
        main.connect(self.ui.pushButtonPause_VB, SIGNAL('clicked()'), self.append_parameters)
        main.connect(self.ui.pushButtonStop_VB, SIGNAL('clicked()'), self.append_parameters)
        main.connect(self.ui.pushButtonClear_VB, SIGNAL('clicked()'), self.reset_plots)
        
        main.connect(self.collectDataThread, SIGNAL('Plot'), self.plotData)
        main.connect(self.collectDataThread, SIGNAL('PreSave'), self.preSave)
        
        main.connect(self.ui.pushButtonBrowse_VB, SIGNAL("clicked()"), self.browse)
        main.connect(self.ui.pushButtonSelectFolder_VB, SIGNAL("clicked()"), self.select_name)
        main.connect(self.ui.radioButtonCSV_VB, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.radioButtonTXT_VB, SIGNAL("clicked()"), self.save_type)
        main.connect(self.ui.pushButtonSave_VB, SIGNAL("clicked()"), self.save)

        
        #Variables and arrays
        self.copy_Check = False
        self.reset_check = False
        self.current_sens = [1E-3, 1E-4, 1E-5, 1E-6, 1E-7, 1E-8, 1E-9, 1E-10, 1E-11]
        self.lock_in_sens_list = [100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3]
        
        self.sens_C= []
        self.frequency_C= []
        self.amplitude_C= []
        self.phase_C = []
        self.QFactor_C= []
        self.filter_C = []
        self.trim_frequency_C = []
        self.slope_C = []
        self.reserve_C = []
        self.quadrant_C = []
        self.mode_C = []
        self.range_C = []
        self.coupling_C = []
        self.inputType_C = []
        self.floatground_C = []
        self.TimeConstant_C = []
        
        self.sens_V= []
        self.frequency_V = []
        self.amplitude_V = []
        self.phase_V = []
        self.QFactor_V = []
        self.filter_V = []
        self.trim_frequency_V = []
        self.slope_V = []
        self.reserve_V = []
        self.quadrant_V = []
        self.mode_V = []
        self.range_V = []
        self.coupling_V = []
        self.inputType_V = []
        self.floatground_V = []
        self.TimeConstant_V = []
        
    def update_visa(self):  
        visas = rm.list_resources()
        self.ui.comboBoxCurrentAgilent_VB.clear()
        self.ui.comboBoxCurrentLockIn_VB.clear()
        self.ui.comboBoxVoltageAgilent_VB.clear()
        self.ui.comboBoxVoltageLockIn_VB.clear()
        self.ui.labelCurrentAgilent_VB.setText("")
        self.ui.labelCurrentLockIn_VB.setText("")
        self.ui.labelVoltageAgilent_VB.setText("")
        self.ui.labelVoltageLockIn_VB.setText("")
        
        for i in visas:
            self.ui.comboBoxCurrentAgilent_VB.addItem(i)
            self.ui.comboBoxCurrentLockIn_VB.addItem(i)
            self.ui.comboBoxVoltageAgilent_VB.addItem(i)
            self.ui.comboBoxVoltageLockIn_VB.addItem(i)
            
    def select_CurrentVisas(self):
        CurrentAgilent = str(self.ui.comboBoxCurrentAgilent_VB.currentText())
        self.CurrentAgilent = rm.open_resource(CurrentAgilent)
        CurrentLockIn = str(self.ui.comboBoxCurrentLockIn_VB.currentText())
        self.CurrentLockIn = rm.open_resource(CurrentLockIn)
        
        if self.copy_Check == True:
            if str(self.ui.comboBoxCurrentAgilent_VB.currentText()) == str(self.ui.comboBoxVoltageAgilent_VB.currentText()) and str(self.ui.comboBoxCurrentLockIn_VB.currentText()) == str(self.ui.comboBoxVoltageLockIn_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Agilent and Lock-In')
            elif str(self.ui.comboBoxCurrentAgilent_VB.currentText()) == str(self.ui.comboBoxVoltageAgilent_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Agilent')
            elif str(self.ui.comboBoxCurrentLockIn_VB.currentText()) == str(self.ui.comboBoxVoltageLockIn_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Lock-In')
            else:
                try:
                    valid = self.check_CurrentVisas()
                except:
                    valid = False
            
                if valid == True:
                    self.ui.labelCurrentAgilent_VB.setText(str(self.CurrentAgilent.ask('*IDN?')))
                    self.ui.labelCurrentLockIn_VB.setText(str(self.CurrentLockIn.ask('*IDN?')))
                    self.ui.lineEditCondition_VB.setText('No Errors with Visas for Current')
                    self.ui.pushButtonStart_VB.setEnabled(True)
                    self.ui.pushButtonCloseCurrentAgilent_VB.setEnabled(True)
                    self.ui.pushButtonCloseCurrentLockIn_VB.setEnabled(True)
                    self.ui.lineEditCondition_VB.setText("No errors, ready to start")
                    self.ui.tabWidgetVB.setCurrentIndex(0)
                else:
                    self.ui.lineEditCondition_VB.setText('Error Visas for Current Measurement')
        else:        
            try:
                valid = self.check_CurrentVisas()
            except:
                valid = False
                print 'Error'
                
            if valid == True:
                self.ui.labelCurrentAgilent_VB.setText(str(self.CurrentAgilent.ask('*IDN?')))
                self.ui.labelCurrentLockIn_VB.setText(str(self.CurrentLockIn.ask('*IDN?')))
                self.copy_Check = True
                self.ui.lineEditCondition_VB.setText('No errors with visas for current')
                self.ui.pushButtonCloseCurrentAgilent_VB.setEnabled(True)
                self.ui.pushButtonCloseCurrentLockIn_VB.setEnabled(True)
            else:
                self.ui.lineEditCondition_VB.setText('Error with visas for current measurement')
            
    def check_CurrentVisas(self):
        try:
            self.CurrentAgilent.ask('*IDN?')
            self.CurrentLockIn.ask('*IDN?')
            valid = True
        except:
            valid = False
            
        return valid
    
    def select_VoltageVisas(self):
        VoltageAgilent = str(self.ui.comboBoxVoltageAgilent_VB.currentText())
        self.VoltageAgilent = rm.open_resource(VoltageAgilent)
        VoltageLockIn = str(self.ui.comboBoxVoltageLockIn_VB.currentText())
        self.VoltageLockIn = rm.open_resource(VoltageLockIn)
        
        if self.copy_Check == True:
            if str(self.ui.comboBoxCurrentAgilent_VB.currentText()) == str(self.ui.comboBoxVoltageAgilent_VB.currentText()) and str(self.ui.comboBoxCurrentLockIn_VB.currentText()) == str(self.ui.comboBoxVoltageLockIn_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Agilent and Lock-In')
            elif str(self.ui.comboBoxCurrentAgilent_VB.currentText()) == str(self.ui.comboBoxVoltageAgilent_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Agilent')
            elif str(self.ui.comboBoxCurrentLockIn_VB.currentText()) == str(self.ui.comboBoxVoltageLockIn_VB.currentText()):
                self.ui.lineEditCondition_VB.setText('A visa has been selected twice for Lock-In')
            else:
                try:
                    valid = self.check_VoltageVisas()
                except:
                    valid = False
                    print 'Error'
            
                if valid == True:
                    self.ui.labelVoltageAgilent_VB.setText(str(self.VoltageAgilent.ask('*IDN?')))
                    self.ui.labelVoltageLockIn_VB.setText(str(self.VoltageLockIn.ask('*IDN?')))
                    self.ui.lineEditCondition_VB.setText('No errors, ready to start')
                    self.ui.pushButtonStart_VB.setEnabled(True)
                    self.ui.pushButtonCloseVoltageAgilent_VB.setEnabled(True)
                    self.ui.pushButtonCloseVoltageLockIn_VB.setEnabled(True)
                    self.ui.tabWidgetVB.setCurrentIndex(0)
                else:
                    self.ui.lineEditCondition_VB.setText('Error with visas for voltage measurement')
        else:
            try:
                valid = self.check_VoltageVisas()
            except:
                valid = False
        
            if valid == True:
                self.ui.labelVoltageAgilent_VB.setText(str(self.VoltageAgilent.ask('*IDN?')))
                self.ui.labelVoltageLockIn_VB.setText(str(self.VoltageLockIn.ask('*IDN?')))
                self.copy_Check = True
                self.ui.lineEditCondition_VB.setText('No error with visas for voltage measurement')
                self.ui.pushButtonCloseVoltageAgilent_VB.setEnabled(True)
                self.ui.pushButtonCloseVoltageLockIn_VB.setEnabled(True)
            else:
                self.ui.lineEditCondition_VB.setText('Error with visas for voltage measurement')
                
    def check_VoltageVisas(self):
        try:
            self.VoltageAgilent.ask('*IDN?')
            self.VoltageLockIn.ask('*IDN?')
            valid = True
        except:
            valid = False
            
        return valid
    
    def close_CurrentAgilent(self):
        self.CurrentAgilent.close()
        self.ui.lineEditCondition_VB.setText("Agilent for current mesaurement has been closed")
        self.ui.labelCurrentAgilent_VB.setText("")
        
    def close_CurrentLockIn(self):
        self.CurrentLockIn.close()
        self.ui.lineEditCondition_VB.setText("Lock-In for current measurement has been closed")
        self.ui.labelCurrentLockIn_VB.setText("")
        
    def close_VoltageAgilent(self):
        self.VoltageAgilent.close()
        self.ui.lineEditCondition_VB.setText("Agilent for voltage measurement has been closed")
        self.ui.labelVoltageAgilent_VB.setText("")
        
    def close_VoltageLockIn(self):
        self.VoltageLockIn.close()
        self.ui.lineEditCondition_VB.setText("Lock-In for voltage measurement has been closed")
        self.ui.labelVoltageLockIn_VB.setText("")
        
    def retrieve_Current_inputs(self):
        #Reading from the lock-in will return values of integers, these integers correspond to the actual settings read from the lock in. These arrays make sure the integers are converted to what the
        #settings were placed to.
        self.sens_conversion= ['100','200','500','1','2','5','10','20','50','100','200','500','1','2','5','10','20','50','100','200','500']
        self.tc_values = ['500 us','1 ms','3 ms','10 ms','30 ms', '100 ms','300 ms','1 s','3 s','10 s','30 s','100 s','300 s']
        self.qfactor_values = ['1','2','5','10','20','50','100']

            
        self.temp1 = self.sens_conversion[int(self.CurrentLockIn.ask('SENS?'))]
        if int(self.CurrentLockIn.ask('SENS?')) < 3:
            self.temp1 = self.temp1 + ' ' + 'nV'
        elif int(self.CurrentLockIn.ask('SENS?')) >= 3 and int(self.CurrentLockIn.ask('SENS ?')) < 12:
            self.temp1 = self.temp1 + ' ' + 'uV'
        else:
            self.temp1 = self.temp1 + ' ' + 'mV'
            
        self.curr_sens = self.current_sens[self.ui.dialPreAmpSens_VB.value()]
        self.ui.lineEditPreAmpSens_VB.setText(str(self.curr_sens))
        self.ui.lineEditCurrentLockInSens_VB.setText(self.temp1)
        
        self.ui.lineEditFreq_Current_VB.setText(str(self.CurrentLockIn.ask("FREQ?")).replace("\r\n", ""))
        self.ui.lineEditTrimFreq_Current_VB.setText(str(self.CurrentLockIn.ask("IFFR?")).replace("\r\n", ""))
        self.ui.lineEditPhase_Current_VB.setText(str(self.CurrentLockIn.ask("PHAS?")).replace("\r\n", ""))
        self.ui.lineEditAmplitude_Current_VB.setText(str(self.CurrentLockIn.ask("SLVL?")).replace("\r\n", ""))
        self.ui.lineEditQFactor_Current_VB.setText(self.qfactor_values[int(self.CurrentLockIn.ask("QFCT?"))])
        self.ui.lineEditTimeConstant_Current_VB.setText(self.tc_values[int((self.CurrentLockIn.ask("OFLT?")))])
        
        #Depending on the integer returned from the lock-in, certain buttons will be pushed.
        if int(self.CurrentLockIn.ask('ISRC?')) == 0:
            self.ui.radioButtonA_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonAB_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('ICPL?')) == 0:
            self.ui.radioButtonAC_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonDC_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('IGND?')) == 0:
            self.ui.radioButtonFloat_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonGround_Current_VB.setChecked(True)
        
        if int(self.CurrentLockIn.ask('TYPF?')) == 0:
            self.ui.radioButtonBandPass_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('TYPF?')) == 1:
            self.ui.radioButtonHighPass_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('TYPF?')) == 2:
            self.ui.radioButtonLowPass_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('TYPF?')) == 3:
            self.ui.radioButtonNotch_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonFlat_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('QUAD?')) == 0:
            self.ui.radioButtonQuadrant1_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('QUAD?')) == 1:
            self.ui.radioButtonQuadrant2_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('QUAD?')) == 2:
            self.ui.radioButtonQuadrant3_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonQuadrant4_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('FMOD?')) == 0:
            self.ui.radioButtonfMode_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FMOD?')) == 1:
            self.ui.radioButtonInternalMode_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FMOD?')) == 2:
            self.ui.radioButton2fMode_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FMOD?')) == 3:
            self.ui.radioButton3fMode_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonReadMode_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('FRNG?')) == 0:
            self.ui.radioButtonRange1_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FRNG?')) == 1:
            self.ui.radioButtonRange2_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FRNG?')) == 2:
            self.ui.radioButtonRange3_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('FRNG?')) == 3:
            self.ui.radioButtonRange4_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonRange5_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('RMOD?')) == 0:
            self.ui.radioButtonHighRes_Current_VB.setChecked(True)
        elif int(self.CurrentLockIn.ask('RMOD?')) == 1:
            self.ui.radioButtonNormal_Current_VB.setChecked(True)
        else:
            self.ui.radioButtonLowNoise_Current_VB.setChecked(True)
            
        if int(self.CurrentLockIn.ask('OFSL?')) == 0:
            self.ui.radioButton6dB_Current_VB.setChecked(True)
        else:
            self.ui.radioButton12dB_Current_VB.setChecked(True)
        self.CurrentLockIn.write('LOCL LOCAL')
    def retrieve_Voltage_inputs(self):
        #Reading from the lock-in will return values of integers, these integers correspond to the actual settings read from the lock in. These arrays make sure the integers are converted to what the
        #settings were placed to.
        self.sens_conversion= ['100','200','500','1','2','5','10','20','50','100','200','500','1','2','5','10','20','50','100','200','500']
        self.tc_values = ['500 us','1 ms','3 ms','10 ms','30 ms', '100 ms','300 ms','1 s','3 s','10 s','30 s','100 s','300 s']
        self.qfactor_values = ['1','2','5','10','20','50','100']

        self.temp2 = self.sens_conversion[int(self.VoltageLockIn.ask('SENS?'))]
        if int(self.VoltageLockIn.ask('SENS?')) < 3:
            self.temp2 = self.temp2 + ' ' + 'nV'
        elif int(self.VoltageLockIn.ask('SENS?')) >= 3 and int(self.VoltageLockIn.ask('SENS ?')) < 12:
            self.temp2 = self.temp2 + ' ' + 'uV'
        else:
            self.temp2 = self.temp2 + ' ' + 'mV'
            
        self.ui.lineEditVoltageLockInSens_VB.setText(self.temp2)
        self.ui.lineEditFreq_Voltage_VB.setText(str(self.VoltageLockIn.ask("FREQ?")).replace("\r\n", ""))
        self.ui.lineEditTrimFreq_Voltage_VB.setText(str(self.VoltageLockIn.ask("IFFR?")).replace("\r\n", ""))
        self.ui.lineEditPhase_Voltage_VB.setText(str(self.VoltageLockIn.ask("PHAS?")).replace("\r\n", ""))
        self.ui.lineEditAmplitude_Voltage_VB.setText(str(self.VoltageLockIn.ask("SLVL?")).replace("\r\n", ""))
        self.ui.lineEditQFactor_Voltage_VB.setText(self.qfactor_values[int(self.VoltageLockIn.ask("QFCT?"))])
        self.ui.lineEditTimeConstant_Voltage_VB.setText(self.tc_values[int((self.VoltageLockIn.ask("OFLT?")))])
        
        #Depending on the integer returned from the lock-in, certain buttons will be pushed.
        if int(self.VoltageLockIn.ask('ISRC?')) == 0:
            self.ui.radioButtonA_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonAB_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('ICPL?')) == 0:
            self.ui.radioButtonAC_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonDC_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('IGND?')) == 0:
            self.ui.radioButtonFloat_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonGround_Voltage_VB.setChecked(True)
        
        if int(self.VoltageLockIn.ask('TYPF?')) == 0:
            self.ui.radioButtonBandPass_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('TYPF?')) == 1:
            self.ui.radioButtonHighPass_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('TYPF?')) == 2:
            self.ui.radioButtonLowPass_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('TYPF?')) == 3:
            self.ui.radioButtonNotch_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonFlat_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('QUAD?')) == 0:
            self.ui.radioButtonQuadrant1_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('QUAD?')) == 1:
            self.ui.radioButtonQuadrant2_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('QUAD?')) == 2:
            self.ui.radioButtonQuadrant3_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonQuadrant4_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('FMOD?')) == 0:
            self.ui.radioButtonfMode_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FMOD?')) == 1:
            self.ui.radioButtonInternalMode_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FMOD?')) == 2:
            self.ui.radioButton2fMode_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FMOD?')) == 3:
            self.ui.radioButton3fMode_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonReadMode_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('FRNG?')) == 0:
            self.ui.radioButtonRange1_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FRNG?')) == 1:
            self.ui.radioButtonRange2_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FRNG?')) == 2:
            self.ui.radioButtonRange3_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('FRNG?')) == 3:
            self.ui.radioButtonRange4_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonRange5_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('RMOD?')) == 0:
            self.ui.radioButtonHighRes_Voltage_VB.setChecked(True)
        elif int(self.VoltageLockIn.ask('RMOD?')) == 1:
            self.ui.radioButtonNormal_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButtonLowNoise_Voltage_VB.setChecked(True)
            
        if int(self.VoltageLockIn.ask('OFSL?')) == 0:
            self.ui.radioButton6dB_Voltage_VB.setChecked(True)
        else:
            self.ui.radioButton12dB_Voltage_VB.setChecked(True)
            
        self.VoltageLockIn.write('LOCL LOCAL')
        
    def start(self):
        if self.ui.radioButtonScaleSteps_VB.isChecked() or self.ui.radioButtonScaleTime_VB.isChecked() and self.ui.lineEditTimestep_VB.text() != '':
            if self.reset_check == False:
                self.ui.tabWidgetVB.setCurrentIndex(1)
                self.curr_sens = self.current_sens[self.ui.dialPreAmpSens_VB.value()]
                if self.ui.dialCurrentLockIn_VB.value() >= 0 and self.ui.dialCurrentLockIn_VB.value() <= 2:
                    self.curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
                    self.curr_LI_magnitude = ['nV', 1E-9]
                elif self.ui.dialCurrentLockIn_VB.value() >=3 and self.ui.dialCurrentLockIn_VB.value() <= 11:
                    self.curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
                    self.curr_LI_magnitude = ['uV', 1E-6]
                else:
                    self.curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
                    self.curr_LI_magnitude = ['mV', 1E-3]
                    
                if self.ui.dialVoltageLockIn_VB.value() >= 0 and self.ui.dialVoltageLockIn_VB.value() <= 2:
                    self.volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
                    self.volt_LI_magnitude = ['nV', 1E-9]
                elif self.ui.dialVoltageLockIn_VB.value() >= 3 and self.ui.dialVoltageLockIn_VB.value() <= 11:
                    self.volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
                    self.volt_LI_magnitude = ['uV', 1E-6]
                else:
                    self.volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
                    self.volt_LI_magnitude = ['mV', 1E-3]
            else:
                pass

            self.ui.pushButtonPause_VB.setEnabled(True)
            self.ui.pushButtonStart_VB.setEnabled(False)
            self.ui.pushButtonStop_VB.setEnabled(True)
            self.ui.pushButtonClear_VB.setEnabled(False)
            self.ui.lineEditCondition_VB.setText('Running...')
            
            self.collectDataThread.input(self.ui, self.curve_item_current, self.curve_item_voltage, self.curve_item_conductance, self.curve_item_resistance, self.curr_sens, self.curr_LI_sens, self.curr_LI_magnitude, self.volt_LI_sens, self.volt_LI_magnitude, self.CurrentAgilent, self.CurrentLockIn, self.VoltageAgilent, self.VoltageLockIn)
        else:
            self.ui.lineEditCondition_VB.setText('Please Choose A Scale To Plot In')
    def plotData(self):
        self.curve_item_current.plot().replot()
        self.curve_item_voltage.plot().replot()
        self.curve_item_conductance.plot().replot()
        self.curve_item_resistance.plot().replot()
        self.ui.curvewidgetCurrent_VB.plot.do_autoscale()
        self.ui.curvewidgetVoltage_VB.plot.do_autoscale()
        self.ui.curvewidgetConductance_VB.plot.do_autoscale()
        self.ui.curvewidgetResistance_VB.plot.do_autoscale()

    def stop(self):
        self.collectDataThread.pauseLoop = True
        self.collectDataThread.quit()      
        self.ui.pushButtonClear_VB.setEnabled(True)
        self.ui.pushButtonStop_VB.setEnabled(False)
        self.ui.pushButtonPause_VB.setEnabled(False)
        self.ui.lineEditCondition_VB.setText("Stopped")
        
    def append_parameters(self):
        self.sens_C.append(self.temp1)
        self.frequency_C.append(str(self.ui.lineEditFreq_Current_VB.text()))
        self.trim_frequency_C.append(str(self.ui.lineEditTrimFreq_Current_VB.text()))
        self.amplitude_C.append(str(self.ui.lineEditAmplitude_Current_VB.text()))
        self.phase_C.append(str(self.ui.lineEditPhase_Current_VB.text()))
        self.QFactor_C.append(str(self.ui.lineEditQFactor_Current_VB.text()))
        self.TimeConstant_C.append(str(self.ui.lineEditTimeConstant_Current_VB.text()))
        
        if self.ui.radioButtonBandPass_Current_VB.isChecked():
            self.filter_C.append('Band Pass')
        elif self.ui.radioButtonHighPass_Current_VB.isChecked():
            self.filter_C.append('High Pass')
        elif self.ui.radioButtonLowPass_Current_VB.isChecked():
            self.filter_C.append('Low Pass')
        elif self.ui.radioButtonNotch_Current_VB.isChecked():
            self.filter_C.append('Notch')
        elif self.ui.radioButtonFlat_Current_VB.isChecked():
            self.filter_C.append('Flat')
        else:
            self.filter_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Filter Type For Current')
            
        if self.ui.radioButton6dB_Current_VB.isChecked():
            self.slope_C.append('6 dB/oct.')
        elif self.ui.radioButton12dB_Current_VB.isChecked():
            self.slope_C.append('12 dB/oct.')
        else:
            self.slope_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Slope For Current')
            
        if self.ui.radioButtonHighRes_Current_VB.isChecked():
            self.reserve_C.append('High Res')
        elif self.ui.radioButtonNormal_Current_VB.isChecked():
            self.reserve_C.append('Normal')
        elif self.ui.radioButtonLowNoise_Current_VB.isChecked():
            self.reserve_C.append('Low Noise')
        else:
            self.reserve_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Reserve For Current')
        
        if self.ui.radioButtonQuadrant1_Current_VB.isChecked():
            self.quadrant_C.append('0-90')
        elif self.ui.radioButtonQuadrant2_Current_VB.isChecked():
            self.quadrant_C.append('90-180')
        elif self.ui.radioButtonQuadrant3_Current_VB.isChecked():
            self.quadrant_C.append('180-270')
        elif self.ui.radioButtonQuadrant4_Current_VB.isChecked():
            self.quadrant_C.append('270-360')
        else:
            self.quadrant_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Quadrant For Current')
            
        if self.ui.radioButtonfMode_Current_VB.isChecked():
            self.mode_C.append('f External')
        elif self.ui.radioButton2fMode_Current_VB.isChecked():
            self.mode_C.append('2f External')
        elif self.ui.radioButton3fMode_Current_VB.isChecked():
            self.mode_C.append('3f External')
        elif self.ui.radioButtonInternalMode_Current_VB.isChecked():
            self.mode_C.append('Internal')
        elif self.ui.radioButtonRearMode_Current_VB.isChecked():
            self.mode_C.append('Rear VCO')
        else:
            self.mode_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Mode For Current')
            
        if self.ui.radioButtonRange1_Current_VB.isChecked():
            self.range_C.append('0.2-21 Hz')
        elif self.ui.radioButtonRange2_Current_VB.isChecked():
            self.range_C.append('2.0-210 Hz')
        elif self.ui.radioButtonRange3_Current_VB.isChecked():
            self.range_C.append('20-2.1k Hz')
        elif self.ui.radioButtonRange4_Current_VB.isChecked():
            self.range_C.append('200-21k Hz')
        elif self.ui.radioButtonRange5_Current_VB.isChecked():
            self.range_C.append('2.0k-210k Hz')
        else:
            self.range_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Frequency Range For Current')
            
        if self.ui.radioButtonAC_Current_VB.isChecked():
            self.coupling_C.append('AC')
        elif self.ui.radioButtonDC_Current_VB.isChecked():
            self.coupling_C.append('DC')
        else:
            self.coupling_C = ''
            self.ui.lineEditCondition.setText('Please Choose A Coupling For Current')
            
        if self.ui.radioButtonA_Current_VB.isChecked():
            self.inputType_C.append('A')
        elif self.ui.radioBUttonAB_Current_VB.isChecked():
            self.inputType_C.append('A-B')
        else:
            self.inputType_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose An Input Type For Current')
            
        if self.ui.radioButtonFloat_Current_VB.isChecked():
            self.floatground_C.append('Float')
        elif self.ui.radioButtonGround_Current_VB.isChecked():
            self.floatground_C.append('Ground')
        else:
            self.floatground_C = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Float/Ground For Current')
        #Does the same as above for Voltage parameters    
        self.sens_V.append(self.temp2)
        self.frequency_V.append(str(self.ui.lineEditFreq_Voltage_VB.text()))
        self.trim_frequency_V.append(str(self.ui.lineEditTrimFreq_Voltage_VB.text()))
        self.amplitude_V.append(str(self.ui.lineEditAmplitude_Voltage_VB.text()))
        self.phase_V.append(str(self.ui.lineEditPhase_Voltage_VB.text()))
        self.QFactor_V.append(str(self.ui.lineEditQFactor_Voltage_VB.text()))
        self.TimeConstant_V.append(str(self.ui.lineEditTimeConstant_Voltage_VB.text()))
        
        if self.ui.radioButtonBandPass_Voltage_VB.isChecked():
            self.filter_V.append('Band Pass')
        elif self.ui.radioButtonHighPass_Voltage_VB.isChecked():
            self.filter_V.append('High Pass')
        elif self.ui.radioButtonLowPass_Voltage_VB.isChecked():
            self.filter_V.append('Low Pass')
        elif self.ui.radioButtonNotch_Voltage_VB.isChecked():
            self.filter_V.append('Notch')
        elif self.ui.radioButtonFlat_Voltage_VB.isChecked():
            self.filter_V.append('Flat')
        else:
            self.filter_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Filter Type For Voltage')
            
        if self.ui.radioButton6dB_Voltage_VB.isChecked():
            self.slope_V.append('6 dB/oct.')
        elif self.ui.radioButton12dB_Voltage_VB.isChecked():
            self.slope_V.append('12 dB/oct.')
        else:
            self.slope_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Slope For Voltage')
            
        if self.ui.radioButtonHighRes_Voltage_VB.isChecked():
            self.reserve_V.append('High Res')
        elif self.ui.radioButtonNormal_Voltage_VB.isChecked():
            self.reserve_V.append('Normal')
        elif self.ui.radioButtonLowNoise_Voltage_VB.isChecked():
            self.reserve_V.append('Low Noise')
        else:
            self.reserve_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Reserve For Voltage')
        
        if self.ui.radioButtonQuadrant1_Voltage_VB.isChecked():
            self.quadrant_V.append('0-90')
        elif self.ui.radioButtonQuadrant2_Voltage_VB.isChecked():
            self.quadrant_V.append('90-180')
        elif self.ui.radioButtonQuadrant3_Voltage_VB.isChecked():
            self.quadrant_V.append('180-270')
        elif self.ui.radioButtonQuadrant4_Voltage_VB.isChecked():
            self.quadrant_V.append('270-360')
        else:
            self.quadrant_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Quadrant For Voltage')
            
        if self.ui.radioButtonfMode_Voltage_VB.isChecked():
            self.mode_V.append('f External')
        elif self.ui.radioButton2fMode_Voltage_VB.isChecked():
            self.mode_V.append('2f External')
        elif self.ui.radioButton3fMode_Voltage_VB.isChecked():
            self.mode_V.append('3f External')
        elif self.ui.radioButtonInternalMode_Voltage_VB.isChecked():
            self.mode_V.append('Internal')
        elif self.ui.radioButtonRearMode_Voltage_VB.isChecked():
            self.mode_V.append('Rear VCO')
        else:
            self.mode_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Mode For Voltage')
            
        if self.ui.radioButtonRange1_Voltage_VB.isChecked():
            self.range_V.append('0.2-21 Hz')
        elif self.ui.radioButtonRange2_Voltage_VB.isChecked():
            self.range_V.append('2.0-210 Hz')
        elif self.ui.radioButtonRange3_Voltage_VB.isChecked():
            self.range_V.append('20-2.1k Hz')
        elif self.ui.radioButtonRange4_Voltage_VB.isChecked():
            self.range_V.append('200-21k Hz')
        elif self.ui.radioButtonRange5_Voltage_VB.isChecked():
            self.range_V.append('2.0k-210k Hz')
        else:
            self.range_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Frequency Range For Voltage')
            
        if self.ui.radioButtonAC_Voltage_VB.isChecked():
            self.coupling_V.append('AC')
        elif self.ui.radioButtonDC_Voltage_VB.isChecked():
            self.coupling_V.append('DC')
        else:
            self.coupling_V = ''
            self.ui.lineEditCondition.setText('Please Choose A Coupling For Voltage')
            
        if self.ui.radioButtonA_Voltage_VB.isChecked():
            self.inputType_V.append('A')
        elif self.ui.radioButtonAB_Voltage_VB.isChecked():
            self.inputType_V.append('A-B')
        else:
            self.inputType_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose An Input Type For Voltage')
            
        if self.ui.radioButtonFloat_Voltage_VB.isChecked():
            self.floatground_V.append('Float')
        elif self.ui.radioButtonGround_Voltage_VB.isChecked():
            self.floatground_V.append('Ground')
        else:
            self.floatground_V = ''
            self.ui.lineEditCondition_VB.setText('Please Choose A Float/Ground For Voltage')
            
    def reset_plots(self):
        self.ui.pushButtonStart_VB.setEnabled(True)
        self.curve_item_current.set_data([],[])
        self.curve_item_voltage.set_data([],[])
        self.curve_item_conductance.set_data([],[])
        self.curve_item_resistance.set_data([],[])
        self.curve_item_current.plot().replot()
        self.curve_item_voltage.plot().replot()
        self.curve_item_conductance.plot().replot()
        self.curve_item_resistance.plot().replot()
        self.reset_check = True
        
    def preSave(self, time, steps, current, voltage, conductance, resistance):
        self.Time = time
        self.Steps = steps
        self.Current = current
        self.Voltage = voltage
        self.Conductance = conductance
        self.Resistance = resistance
        self.collectDataThread.save_ready = False
        
    def browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select The GoogleDrive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            file_dir.replace('/', '\\')
            self.ui.lineEditDirectory_VB.setText(file_dir)
        self.directory = ''
        
    def select_name(self):
        file_list= []
        file_list = str(self.ui.lineEditDirectory_VB.text()).split('\\')
        for i in range(0, len(file_list)):
            self.directory += file_list[i] + '\\'
        namefolder = str(self.ui.comboBoxFolders_VB.currentText())
        if namefolder == 'None':
            self.ui.lineEditCondition_VB.setText('Please Choose A Folder To Save To.')
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
        if self.ui.radioButtonCSV_VB.isChecked() == True:
            self.type = '.csv'
            self.divide = ','
        elif self.ui.radioButtonTXT_VB.isChecked() == True:
            self.type = '.txt'
            self.divide = '\t'
            
    def save_name(self):
        if self.ui.radioButtonDateTime_VB.isChecked():
            now = datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.month, now.second)
            date_and_time = date + ' ' + current_time
            self.file_name = str(date_and_time)
        elif self.ui.radioButtonCustomName_VB.isChecked():
            self.file_name = str(self.ui.lineEditCustom_VB.text())
            
    def save(self):
        if self.ui.radioButtonCustomName_VB.isChecked() and self.ui.lineEditCustom_VB.text() == ' ':
            self.ui.lineEditStatus_VB.setText('Please Enter A Custom File Name')
        else:
            self.save_type()
            self.save_name()
        import datetime
        parameters_s = ['Sensitivity:', 'Frequency:', 'Amplitude:','Phase:','Trim Frequency:','Reserve:','Slope:', 'Q Factor:', 'Time Constant:', 'Filter Type:', 'Coupling:', 'Input:', 'Float/Ground:', 'Quadrant:','Mode:', 'Frequency Range:']
        parametersValue_C =[self.sens_C, self.frequency_C, self.amplitude_C, self.phase_C, self.trim_frequency_C, self.reserve_C, self.slope_C, self.QFactor_C, self.TimeConstant_C, self.filter_C, self.coupling_C, self.inputType_C, self.floatground_C, self.quadrant_C, self.mode_C,  self.range_C]
        parametersValue_V =[self.sens_V, self.frequency_V, self.amplitude_V, self.phase_V, self.trim_frequency_V, self.reserve_V, self.slope_V, self.QFactor_V, self.TimeConstant_V, self.filter_V, self.coupling_V, self.inputType_V, self.floatground_V, self.quadrant_V, self.mode_V,  self.range_V]
        
        comments = []
        parameters = []
        file_info = []
        units = []
        data = []
        divider = 'Collected Data'
        
        # First line user name
        temp = []
        temp.append('User Name:')
        temp.append(str(self.ui.comboBoxFolders_VB.currentText()))
        comments.append(temp)
        
        temp = []
        temp.append('Edit Time:')
        temp.append(str(datetime.datetime.now()))
        comments.append(temp)
        # Fourth line visa address
        temp = []
        temp.append('Agilent(Current) Visa Address:')
        temp.append(str(self.ui.comboBoxCurrentAgilent_VB.currentText()))
        comments.append(temp)
        # Fifth line visa name
        temp = []
        temp.append('Visa Name:')
        visa_name = self.CurrentAgilent.ask('*IDN?').rstrip('\n')
        visa_name = visa_name.replace(',', ' ')
        temp.append(visa_name)
        comments.append(temp)
        
        temp = []
        temp.append('Lock-In(Current) Visa Address:')
        temp.append(str(self.ui.comboBoxCurrentLockIn_VB.currentText()))
        comments.append(temp)

        temp = []
        temp.append('Visa Name:')
        visa_name = self.CurrentLockIn.ask('*IDN?').rstrip('\n')
        visa_name = visa_name.replace(',', ' ')
        temp.append(visa_name)
        comments.append(temp)
        
        temp = []
        temp.append('Agilent(Voltage) Visa Address:')
        temp.append(str(self.ui.comboBoxVoltageAgilent_VB.currentText()))
        comments.append(temp)
        # Fifth line visa name
        temp = []
        temp.append('Visa Name:')
        visa_name = self.VoltageAgilent.ask('*IDN?').rstrip('\n')
        visa_name = visa_name.replace(',', ' ')
        temp.append(visa_name)
        comments.append(temp)
        
        temp = []
        temp.append('Lock-In(Voltage) Visa Address:')
        temp.append(str(self.ui.comboBoxVoltageLockIn_VB.currentText()))
        comments.append(temp)

        temp = []
        temp.append('Visa Name:')
        visa_name = self.VoltageLockIn.ask('*IDN?').rstrip('\n')
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
        temp.append('Lock-In(Current) Parameters:')
        temp.append('')
        comments.append(temp)
              
        for i in range(0, len(parameters_s)):
            temp = []
            for j in range(0, len(self.sens_C)):
                temp.append(parameters_s[i])
                temp.append(parametersValue_C[i][j])
                comments.append(temp)
                
        temp = []
        temp.append('----------------')
        temp.append('')
        comments.append(temp)
        
        temp = []
        temp.append('Lock-In(Voltage) Parameters:')
        temp.append('')
        comments.append(temp)
        
        for i in range(0, len(parameters_s)):
            temp = []
            for j in range(0, len(self.sens_V)):
                temp.append(parameters_s[i])
                temp.append(parametersValue_V[i][j])
                comments.append(temp)
                
        print comments
        # Eighth line comments
        temp = []
        temp.append('Comments:')
        temp.append(str(self.ui.textEditComments_VB.toPlainText()))
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
        units.append(self.volt_LI_magnitude[0])
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
        self.ui.lineEditCondition_VB.setText("Data has been saved")
        
class CollectData(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, curve_current, curve_voltage, curve_conductance, curve_resistance, PreAmp_sens, Curr_LI_sens, Curr_LI_magn, Volt_LI_sens, Volt_LI_magn, CurrentAgilent, CurrentLockIn, VoltageAgilent, VoltageLockIn):
        self.ui = ui
        self.curve_current = curve_current
        self.curve_voltage = curve_voltage
        self.curve_conductance = curve_conductance
        self.curve_resistance = curve_resistance
        self.PreAmp_sens = PreAmp_sens
        self.Curr_LI_sens = Curr_LI_sens
        self.Curr_LI_magn = Curr_LI_magn
        self.Volt_LI_sens = Volt_LI_sens
        self.Volt_LI_magn = Volt_LI_magn
        self.CurrentAgilent = CurrentAgilent
        self.CurrentLockIn = CurrentLockIn
        self.VoltageAgilent = VoltageAgilent
        self.VoltageLockIn = VoltageLockIn
        
        self.Current = np.array([], dtype = float)
        self.Voltage = np.array([], dtype = float)
        self.Conductance = np.array([], dtype = float)
        self.Resistance = np.array([], dtype = float)
        self.Steps = np.array([], dtype = float)
        self.Time = np.array([], dtype = float)
        
        self.n = 0
        
        try:
            self.CurrentAgilent.ask('MEAS:VOLT?')
            self.VoltageAgilent.ask('MEAS:VOLT?')
        except:
            self.ui.lineEditCondition_VB.setText("Error")
        
        self.pauseLoop = False
        self.save_ready = True
        self.start()

        
    def run(self):
        import time
        start_time = time.time()
        while True:
            import time
            if not self.pauseLoop:
                self.Timestep = float(self.ui.lineEditTimestep_VB.text())
                self.CurrentReading = float(self.CurrentAgilent.ask('READ?'))*self.Curr_LI_sens*self.PreAmp_sens/10
                self.VoltageReading = (float(self.VoltageAgilent.ask('READ?'))*self.Volt_LI_sens)/10
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
                self.ui.labelCurrentValue_VB.setText(str(self.Current[self.n]) + ' ' + 'A')
                self.ui.labelVoltageValue_VB.setText(str(self.Voltage[self.n]/self.Volt_LI_magn[1]) + ' ' + self.Volt_LI_magn[0])
                self.ui.labelConductanceValue_VB.setText(str(self.Conductance[self.n]) + ' ' + 'S')
                self.ui.labelResistanceValue_VB.setText(str(self.Resistance[self.n]) + ' ' + 'Ohms')
                
                if self.ui.radioButtonScaleTime_VB.isChecked():
                    self.curve_current.set_data(self.Time, self.Current)
                    self.curve_voltage.set_data(self.Time, self.Voltage/self.Volt_LI_magn[1])
                    self.curve_conductance.set_data(self.Time, self.Conductance)
                    self.curve_resistance.set_data(self.Time, self.Resistance)
                    self.ui.curvewidgetCurrent_VB.plot.set_titles('Current vs. Time', 'Time (s)', 'Current (A)')
                    self.ui.curvewidgetVoltage_VB.plot.set_titles('Voltage vs. Time', 'Time (s)', 'Voltage ( ' + self.Volt_LI_magn[0] + ')')
                    self.ui.curvewidgetConductance_VB.plot.set_titles('Conductance vs. Time', 'Time (s)', 'Conductance (S)')
                    self.ui.curvewidgetResistance_VB.plot.set_titles('Resistance vs. Time', 'Time(s)', 'Resistance (Ohm)')
                else:
                    self.curve_current.set_data(self.Steps, self.Current)
                    self.curve_voltage.set_data(self.Steps, self.Voltage/self.Volt_LI_magn[1])
                    self.curve_conductance.set_data(self.Steps, self.Conductance)
                    self.curve_resistance.set_data(self.Steps, self.Resistance)
                    self.ui.curvewidgetCurrent_VB.plot.set_titles('Current vs. Steps', 'Steps', 'Current (A)')
                    self.ui.curvewidgetVoltage_VB.plot.set_titles('Voltage vs. Steps', 'Steps', 'Voltage ( ' + self.Volt_LI_magn[0] + ')')
                    self.ui.curvewidgetConductance_VB.plot.set_titles('Conductance vs. Steps', 'Steps', 'Conductance (S)')
                    self.ui.curvewidgetResistance_VB.plot.set_titles('Resistance vs. Steps', 'Steps', 'Resistance (Ohm)')
                    
                self.emit(SIGNAL('Plot'))
                self.n += 1
                time.sleep(self.Timestep)
            elif self.pauseLoop:
                if self.save_ready == True:
                    time = self.Time
                    steps = self.Steps
                    current = self.Current
                    voltage = self.Voltage
                    conductance = self.Conductance
                    resistance = self.Resistance
                    self.emit(SIGNAL('PreSave'), time, steps, current, voltage, conductance, resistance)
                elif self.save_ready == False:
                    pass
                self.ui.lineEditCondition_VB.setText('Paused')
                
    def pause(self):
        if self.pauseLoop == True:
            self.change_sens()
            self.pauseLoop = False
            self.ui.lineEditCondition_VB.setText("Running")
            self.ui.pushButtonPause_VB.setText('Pause')

        else:
            self.pauseLoop = True
            self.ui.lineEditCondition_VB.setText("Paused")
            self.ui.pushButtonPause_VB.setText("Continue")
            
    def change_sens(self):
        self.current_sens = [1E-3, 1E-4, 1E-5, 1E-6, 1E-7, 1E-8, 1E-9, 1E-10, 1E-11]
        self.lock_in_sens_list = [100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3]
        
        self.PreAmp_sens= self.current_sens[self.ui.dialPreAmpSens_VB.value()]
        if self.ui.dialCurrentLockIn_VB.value() >= 0 and self.ui.dialCurrentLockIn_VB.value() <= 2:
            self.Curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
            self.Curr_LI_magn = ['nV', 1E-9]
        elif self.ui.dialCurrentLockIn_VB.value() >=3 and self.ui.dialCurrentLockIn_VB.value() <= 11:
            self.Curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
            self.Curr_LI_magn = ['uV', 1E-6]
        else:
            self.Curr_LI_sens = self.lock_in_sens_list[self.ui.dialCurrentLockIn_VB.value()]
            self.Curr_LI_magn = ['mV', 1E-3]
            
        if self.ui.dialVoltageLockIn_VB.value() >= 0 and self.ui.dialVoltageLockIn_VB.value() <= 2:
            self.Volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
            self.Volt_LI_magn = ['nV', 1E-9]
        elif self.ui.dialVoltageLockIn_VB.value() >= 3 and self.ui.dialVoltageLockIn_VB.value() <= 11:
            self.Volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
            self.Volt_LI_magn = ['uV', 1E-6]
        else:
            self.Volt_LI_sens = self.lock_in_sens_list[self.ui.dialVoltageLockIn_VB.value()]
            self.Volt_LI_magn = ['mV', 1E-3]
            

            