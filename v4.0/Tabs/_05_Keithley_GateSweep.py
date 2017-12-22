# Import numpy library
import numpy as np
import os
import sys
import datetime
import visa
import math
import time
import warnings

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Save import Save_Thread
from D_save import Dynamic_Save_Thread

# These are the modules required for the guiqwt widgets.
# Import plot widget base class
from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

import subprocess

class KeithleyGateSweep():
    
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.collect_data_thread = Collect_data()
        self.save_thread = Save_Thread()
        self.dsave_thread = Dynamic_Save_Thread()
        
        main.connect(self.ui.pushButtonK2_browseGate, SIGNAL('clicked()'), self.Browse_Array)
        main.connect(self.ui.pushButtonK2_importGate, SIGNAL('clicked()'), self.Import_Array)
        main.connect(self.ui.pushButtonK2_copyGate, SIGNAL('clicked()'), self.Copy_Array)
        main.connect(self.ui.pushButtonK2_updateGate, SIGNAL('clicked()'), self.update_visas)
        main.connect(self.ui.pushButtonK2_updateLead, SIGNAL('clicked()'), self.update_visas)
        main.connect(self.ui.pushButtonK2_selectGate, SIGNAL('clicked()'), lambda : self.Select_visa("gate", self.gate_visa, self.ui.comboBoxK2_gateVisa, self.ui.labelK2_gatevisa, [self.ui.pushButtonK2_selectGate, self.ui.pushButtonK2_closeGate]))
        main.connect(self.ui.pushButtonK2_selectLead, SIGNAL('clicked()'), lambda : self.Select_visa("lead", self.lead_visa, self.ui.comboBoxK2_leadVisa, self.ui.labelK2_leadvisa, [self.ui.pushButtonK2_selectLead, self.ui.pushButtonK2_closeLead]))
        main.connect(self.ui.pushButtonK2_closeGate, SIGNAL('clicked()'), lambda : self.Close_visa("gate", self.gate_visa, self.ui.labelK2_gatevisa, [self.ui.pushButtonK2_selectGate, self.ui.pushButtonK2_closeGate]))
        main.connect(self.ui.pushButtonK2_closeLead, SIGNAL('clicked()'), lambda : self.Close_visa("lead", self.lead_visa, self.ui.labelK2_leadvisa, [self.ui.pushButtonK2_selectLead, self.ui.pushButtonK2_closeLead]))
        main.connect(self.ui.pushButtonK2_Start, SIGNAL('clicked()'), self.start)
        main.connect(self.ui.pushButtonK2_Stop, SIGNAL('clicked()'), self.collect_data_thread.stop)
        main.connect(self.ui.pushButtonK2_Pause, SIGNAL('clicked()'), self.collect_data_thread.pause)
        main.connect(self.ui.pushButtonK2_browse_save_G, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButtonK2_browse_save_O, SIGNAL('clicked()'), self.Other_browse)
        main.connect(self.ui.pushButtonK2_check_G, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButtonK2_Select_Directory_G, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.pushButtonK2_Save_G, SIGNAL('clicked()'), self.G_save)
        main.connect(self.ui.pushButtonK2_Open_G, SIGNAL('clicked()'), self.G_open)
        main.connect(self.ui.pushButtonK2_Save_O, SIGNAL('clicked()'), self.O_save)
        main.connect(self.ui.pushButtonK2_Open_O, SIGNAL('clicked()'), self.O_open)
        main.connect(self.collect_data_thread, SIGNAL("curve_plot"), self.curvePlots_update)
        main.connect(self.collect_data_thread, SIGNAL("mpl_plot"), self.mplPlots)
        main.connect(self.collect_data_thread, SIGNAL("data_available"), self.Pre_save)
        main.connect(self.collect_data_thread, SIGNAL("print"), self.Print_data)
        main.connect(self.ui.checkBoxK2_dsave, SIGNAL("clicked()"), self.Pre_dsave)
        main.connect(self.ui.pushButtonK2_dsave_browse, SIGNAL('clicked()'), self.Dsave_browse)
        main.connect(self.ui.radioButtonK2_timescan, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
        main.connect(self.ui.radioButtonK2_stepscan, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
    
        self.Array = []
        self.count = 0
        self.go_on = True
        self.dsave_directory = ''
        
        self.ui.mplwidgetK2_gateArray = self.make_mplToolBar(self.ui.mplwidgetK2_gateArray, self.ui.widgetK2_gateArray)
        self.ui.mplwidgetK2_AgateVoltage = self.make_mplToolBar(self.ui.mplwidgetK2_AgateVoltage, self.ui.widgetK2_AgateVoltage)
        self.ui.mplwidgetK2_AleadCurrent = self.make_mplToolBar(self.ui.mplwidgetK2_AleadCurrent, self.ui.widgetK2_AleadCurrent)
        self.ui.mplwidgetK2_AgateCurrent = self.make_mplToolBar(self.ui.mplwidgetK2_AgateCurrent, self.ui.widgetK2_AgateCurrent)
        self.ui.mplwidgetK2_ALeadResistance = self.make_mplToolBar(self.ui.mplwidgetK2_ALeadResistance, self.ui.widgetK2_ALeadResistance)
        self.ui.mplwidgetK2_ALeadCurrentGateVoltage = self.make_mplToolBar(self.ui.mplwidgetK2_ALeadCurrentGateVoltage, self.ui.widgetK2_ALeadCurrentGateVoltage)
        self.ui.mplwidgetK2_ALeadResistanceGateVoltage = self.make_mplToolBar(self.ui.mplwidgetK2_ALeadResistanceGateVoltage, self.ui.widgetK2_ALeadResistanceGateVoltage)
        
        self.axes_gateArray = None
        self.axes_AgateVoltage = None
        self.axes_AleadCurrent = None
        self.axes_AgateCurrent = None
        self.axes_ALeadResistance = None
        self.axes_ALeadCurrentGateVoltage = None
        self.axes_ALeadResistanceGateVoltage = None
        
        self.curve_itemK2_SgateVoltage = self.make_curveWidgets(self.ui.curvewidgetK2_SgateVoltage, "b", titles = ["Gate Voltage", "Steps", "Gate Voltage (V)"])
        self.curve_itemK2_SleadCurrent = self.make_curveWidgets(self.ui.curvewidgetK2_SleadCurrent, "b", titles = ["Lead Current", "Steps", "Lead Current (A)"])
        self.curve_itemK2_SgateCurrent = self.make_curveWidgets(self.ui.curvewidgetK2_SgateCurrent, "b", titles = ["Gate Current", "Steps", "Gate Current (A)"])
        self.curve_itemK2_SleadResistance = self.make_curveWidgets(self.ui.curvewidgetK2_SleadResistance, "b", titles = ["Lead Resistance", "Steps", "Lead Resistance (Ohms)"])
        self.curve_itemK2_SleadCurrentGateVoltage = self.make_curveWidgets(self.ui.curvewidgetK2_SleadCurrentGateVoltage, "b", titles = ["Lead Current vs Gate Voltage", "Gate Voltage (V)", "Lead Current (A)"])
        self.curve_itemK2_SleadResistanceGateVoltage = self.make_curveWidgets(self.ui.curvewidgetK2_SleadResistanceGateVoltage, "b", titles = ["Lead Resistane vs Gate Voltage", "Gate Voltage (V)", "Lead Resistance (Ohms)"])
        
        self.ui.pushButtonK2_Pause.setEnabled(False)
        self.ui.pushButtonK2_Stop.setEnabled(False)
        self.gate_visa = None
        self.lead_visa = None
        self.update_visas()
        self.gate_visa_ok = False
        self.lead_visa_ok = False
        self.array_ok = False
        
        self.uiSavingGDpushButtons = [ self.ui.pushButtonK2_browse_save_G, self.ui.pushButtonK2_check_G, self.ui.pushButtonK2_Select_Directory_G, self.ui.pushButtonK2_Save_G, self.ui.pushButtonK2_Open_G]
        self.uiSavingGDradioButton = [self.ui.radioButtonK2_csv_G, self.ui.radioButtonK2_txt_G, self.ui.radioButtonK2_Timename_G, self.ui.radioButtonK2_Custom_Name_G]
        self.uiSavingGDtextEdit = [self.ui.textEditK2_comment_G]
        self.uiSavingGDcomboBox = [self.ui.comboBoxK2_Name_Folder_G]
        self.uiSavingGDlineEdit = [self.ui.lineEditK2_GoogleDrive_G, self.ui.lineEditK2_Custom_Name_G]
        self.uiSavingGDlabel = [self.ui.labelK2_condition_G]
        
    def make_mplToolBar(self, mplwidget, widget):
        canvas_mpl = FigureCanvas(mplwidget.figure)
        canvas_mpl.setParent(widget)
        # This is the toolbar widget for the import canvas
        mpl_toolbar = NavigationToolbar(canvas_mpl, mplwidget)
        vbox_ = QVBoxLayout()
        # The matplotlib canvas
        vbox_.addWidget(canvas_mpl)
        # The matplotlib toolbar
        vbox_.addWidget(mpl_toolbar)
        widget.setLayout(vbox_)
        return canvas_mpl
    
    def make_curveWidgets(self, curvewidget, color, titles):
        curve_item = make.curve([], [], color = 'b', marker = "o")
        curvewidget.plot.add_item(curve_item)
        curvewidget.plot.set_antialiasing(True)
        curvewidget.plot.set_titles(titles[0], titles[1], titles[2])
        return curve_item

    def Browse_Array(self):
        prev_dir = os.getcwd()
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
            self.ui.lineEditK2_directoryGate.setText(fileDir)
            self.ui.pushButtonK2_importGate.setEnabled(True)
            self.ui.labelK2_condition.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
        else:
            self.ui.labelK2_condition.setText("Please choose valid file to import.")

    def Import_Array(self):
        divider_found = True
        count = 0
        temp = 0
        self.Array = []
        x_value = []
        y_value = []
        fileDir = self.ui.lineEditK2_directoryGate.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.labelK2_condition.setText("Data not found in file. Please check it.")
                divider_found = False
                break
            line = fp.readline()
            line_list = line.split(',')
            if line_list[0].upper() == "Array Data".upper() + '\n':
                break
            count += 1
        if divider_found == True:
            self.array_ok = True
            line = fp.readline()
            while True:
                line = fp.readline().replace('\n', '')
                #print 'line: ' + line
                if line == '':
                    break
                value = line.split(',')
                x_value.append(temp)
                x_value.append(temp + 1)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array.append(float(value[1]))
                temp += 1
            self.plot_data(self.axes_gateArray, x_value, y_value, ["Array Import Plot", "Steps", "Values"], self.ui.mplwidgetK2_gateArray)
            self.ui.labelK2_condition.setText("File is imported correctly.")
            self.ui.groupBoxK2_yvalue_units.setEnabled(True)
            self.ui.groupBoxK2_lead_output.setEnabled(True)
            self.ui.groupBoxK2_dsave.setEnabled(True)
            self.ui.checkBoxK2_dsave.setEnabled(True)
        if self.gate_visa_ok and self.lead_visa_ok and self.array_ok:
            self.ui.groupBoxK2_control.setEnabled(True)
            
    def Copy_Array(self):
        Values = self.copyDataFunc()
        if Values != None:
            self.array_ok = True
            self.ui.labelK2_condition.setText('Array has been copied and plotted.')
            #self.ui.tabWidget_plot_keithely.setCurrentIndex(0)
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
            self.plot_data(self.axes_gateArray, x_value, y_value, ["Array Import Plot", "Steps", "Values"], self.ui.mplwidgetK2_gateArray)
            self.ui.lineEditK2_directoryGate.setText('From Array Builder Tab.')
            self.ui.groupBoxK2_yvalue_units.setEnabled(True)
            self.ui.groupBoxK2_lead_output.setEnabled(True)
            self.ui.groupBoxK2_dsave.setEnabled(True)
            self.ui.checkBoxK2_dsave.setEnabled(True)
        else:
            self.ui.labelK2_condition.setText('No valid array to copy.')
        if self.gate_visa_ok and self.lead_visa_ok and self.array_ok:
            self.ui.groupBoxK2_control.setEnabled(True)
        
    def plot_reset(self, axes, mplwidget):
        mplwidget.figure.clear()
        axes = mplwidget.figure.add_subplot(111)
        return axes
        
    def plot_data(self, axes, x, y, titles, mplwidget):
        axes = self.plot_reset(axes, mplwidget)
        axes.plot(x, y, marker = '.', linestyle = '-')
        axes.grid()
        axes.set_title("Array Import Plot")
        axes.set_xlabel("Steps")
        axes.set_ylabel("Values")
        mplwidget.draw()
    
    def Print_data(self, i, during, gate_Volt, gate_Curr, lead_Curr, Resistance):
        self.ui.labelK2_step.setText(str(i))
        self.ui.labelK2_time.setText(format(during, '.3f'))
        data = self.Twist_scale(gate_Volt)
        self.ui.labelK2_1.setText(format(data[0], '.3f'))
        self.ui.labelK2_1unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(gate_Curr)
        self.ui.labelK2_2.setText(format(data[0], '.3f'))
        self.ui.labelK2_2unit.setText(data[1] + 'Curr')
        data = self.Twist_scale(lead_Curr)
        self.ui.labelK2_3.setText(format(data[0], '.3f'))
        self.ui.labelK2_3unit.setText(data[1] + 'Curr')
        data = self.Twist_scale(Resistance)
        self.ui.labelK2_4.setText(format(data[0], '.3f'))
        self.ui.labelK2_4unit.setText(data[1] + 'Ohms')
        
    def Twist_scale(self, num):
        temp = abs(num)
        if temp >= 1E9:
            scale = [1E-9, "G"]
        elif temp >= 1E6 and temp < 1E9:
            scale = [1E-6, "M"]
        elif temp >= 1E3 and temp < 1E6:
            scale = [1E-3, "k"]
        elif temp >= 1 and temp < 1000:
            scale = [1, ""]
        elif temp >= 1E-3 and temp < 1:
            scale = [1E3, "m"]
        elif temp >= 1E-6 and temp < 1E-3:
            scale = [1E6, "u"]
        elif temp >= 1E-9 and temp < 1E-6:
            scale = [1E9, "n"]
        elif temp < 1E-9:
            scale = [1E12, "p"]
            
        return [num * scale[0], scale[1]]
        
    def update_visas(self):
        rm = visa.ResourceManager()
        try:
            all_visas = rm.list_resources()
        except:
            all_visas = "No Visa Available."
        self.ui.comboBoxK2_gateVisa.clear()
        self.ui.comboBoxK2_leadVisa.clear()
        
        for item in all_visas:
            self.ui.comboBoxK2_gateVisa.addItem(item)
            self.ui.comboBoxK2_leadVisa.addItem(item)
        
    def Select_visa(self, gateLead, visa_chosen, comboBoxVisa, lineEditVisa, selectClose):
        visa_address = str(comboBoxVisa.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource(visa_address)
        visa_check = self.Check_visa(inst)
        if visa_check == True:
            self.ui.labelK2_condition.setText("Visa is selected succefully!")
            visa_name = inst.query("*IDN?")
            name_list = visa_name.split(',')
            first_name = name_list[0]
            if gateLead == "gate":
                if self.lead_visa_ok:
                    if self.ui.comboBoxK2_leadVisa.currentText() == visa_address:
                        self.ui.labelK2_condition.setText('Select a different Keithley.')
                    else:
                        self.gate_visa = inst
                        self.gate_visa_ok = True
                        lineEditVisa.setText(visa_name)
                        selectClose[0].setEnabled(False)
                        selectClose[1].setEnabled(True)
                else:
                    self.gate_visa = inst
                    self.gate_visa_ok = True
                    lineEditVisa.setText(visa_name)
                    selectClose[0].setEnabled(False)
                    selectClose[1].setEnabled(True)
            elif gateLead == "lead":
                if self.gate_visa_ok:
                    if self.ui.comboBoxK2_gateVisa.currentText() == visa_address:
                        self.ui.labelK2_condition.setText('Select a different Keithley.')
                    else:
                        self.lead_visa = inst
                        self.lead_visa_ok = True
                        lineEditVisa.setText(visa_name)
                        selectClose[0].setEnabled(False)
                        selectClose[1].setEnabled(True)
                else:
                    self.lead_visa = inst
                    self.lead_visa_ok = True
                    lineEditVisa.setText(visa_name)
                    selectClose[0].setEnabled(False)
                    selectClose[1].setEnabled(True)
            #self.ui.groupBox_scan_keithley.setEnabled(True)
        elif visa_check == False:
            self.ui.labelK2_condition.setText("Invalid visa address.")
            lineEditVisa.setText("None.")
            visa_chosen = False
        if self.gate_visa_ok and self.lead_visa_ok:
            self.ui.groupBoxK2_mode.setEnabled(True)
            self.ui.radioButtonK2_stepscan.setEnabled(True)
        if self.gate_visa_ok and self.lead_visa_ok and self.array_ok:
            self.ui.groupBoxK2_control.setEnabled(True)
            
    def Check_visa(self, inst):
        try:
            inst.ask("*IDN?")
            valid = True
        except:
            valid = False
        return valid
        
    def Close_visa(self, gateLead, visa_chosen, lineEditVisa, selectClose):
        self.ui.labelK2_condition.setText('Visa address is closed')
        lineEditVisa.setText('')
        selectClose[0].setEnabled(True)
        selectClose[1].setEnabled(False)
        if gateLead == "gate":
            self.gate_visa = None
            self.gate_visa_ok = False
            visa_chosen.close()
        elif gateLead == "lead":
            self.lead_visa = None
            self.lead_visa_ok = False
            visa_chosen.close()
        #self.ui.groupBox_scan_keithley.setEnabled(False)
     
    def start(self):
        self.dsave_filename = ''
        self.dsave_username = ''
        self.dsave_filetype = ''
        self.dsave_divide = ''
        gate_set = set(str(self.gate_visa).split(' '))
        lead_set = set(str(self.lead_visa).split(' '))
        if gate_set == lead_set:
            self.ui.labelK2_condition.setText('Two visa addresses cannot be same.')
        else:
            instruments = [self.gate_visa, self.lead_visa]
            curves = [self.curve_itemK2_SgateVoltage, self.curve_itemK2_SleadCurrent, self.curve_itemK2_SgateCurrent, self.curve_itemK2_SleadResistance, self.curve_itemK2_SleadCurrentGateVoltage, self.curve_itemK2_SleadResistanceGateVoltage]
            curveWidgets =[self.ui.curvewidgetK2_SgateVoltage, self.ui.curvewidgetK2_SleadCurrent, self.ui.curvewidgetK2_SgateCurrent, self.ui.curvewidgetK2_SleadResistance, self.ui.curvewidgetK2_SleadCurrentGateVoltage, self.ui.curvewidgetK2_SleadResistanceGateVoltage]
            dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
            go_on = None
            if self.ui.checkBoxK2_dsave.isChecked():
                self.Dsave_directory()
                if self.dsave_dir_ok:
                    self.Dsave_filename()
                    if self.dsave_filename_ok:    
                        self.Dsave_username()
                        if self.dsave_username_ok:
                            self.Dsave_filetype()
                            dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
                            self.collect_data_thread.input(instruments, self.ui, self.Array, go_on , curves, curveWidgets, dsave)
                            self.ui.tabWidgetK2.setCurrentIndex(2)
                            self.ui.pushButtonK2_Start.setEnabled(False)
                            self.ui.pushButtonK2_Pause.setEnabled(True)
                            self.ui.pushButtonK2_Stop.setEnabled(True)
                            self.ui.groupBoxK2_parameters.setEnabled(True)
                            self.ui.labelK2_condition.setText('Running...')
                        else:
                            self.ui.labelK2_condition.setText('Enter user name for dynamic saving.')
                    else:
                        self.ui.labelK2_condition.setText('Enter file name for dynamic saving.')
                else:
                    self.ui.labelK2_condition.setText('Choose valid directory for dynamic saving.')
            else:
                self.collect_data_thread.input(instruments, self.ui, self.Array, go_on , curves, curveWidgets, dsave)
                self.ui.tabWidgetK2.setCurrentIndex(2)
                self.ui.pushButtonK2_Start.setEnabled(False)
                self.ui.pushButtonK2_Pause.setEnabled(True)
                self.ui.pushButtonK2_Stop.setEnabled(True)
                self.ui.groupBoxK2_parameters.setEnabled(True) 
                self.ui.labelK2_condition.setText('Running...')
                           
    def curvePlots_update(self, curveInfo):
        curveWidget = curveInfo[0]
        curve = curveInfo[1]
        curveWidget.plot.do_autoscale()
        curve.plot().replot()
        
    def mplPlots(self):
        self.ui.tabWidgetK2.setCurrentIndex(3)
        self.ui.mplwidgetK2_AgateVoltage.draw()
        self.ui.mplwidgetK2_AleadCurrent.draw()
        self.ui.mplwidgetK2_AgateCurrent.draw()
        self.ui.mplwidgetK2_ALeadResistance.draw()
        self.ui.mplwidgetK2_ALeadCurrentGateVoltage.draw()
        self.ui.mplwidgetK2_ALeadResistanceGateVoltage.draw()
    
    def Plot_analysis(self):
        self.ui.tabWidget_plot_keithely.setCurrentIndex(3)
        self.ui.mplwidget_analysis.draw()
        self.ui.mplwidget_ct_analysis.draw()
        self.ui.mplwidget_vt_analysis.draw()
        
    def Google_browse(self):
        prev_dir = 'C:\\'
        file_list = []
        file_dir = QFileDialog.getExistingDirectory(None, 'Select Google Drive Folder', prev_dir)
        if file_dir != '':
            file_list = str(file_dir).split('/')
            # for i in range(0, len(file_list) - 1):
            #     if i < len(file_list) - 1:
            #         open_dir += file_list[i] + '\\'
            #     elif i == len(file_list) - 1:
            #         open_dir += file_list[i]
            file_dir.replace('/', '\\')
            self.ui.lineEditK2_GoogleDrive_G.setText(file_dir)
            self.ui.labelK2_condition_G.setText('Open Google Drive User Folder')
            self.ui.pushButtonK2_check_G.setEnabled(True)
    
    def Other_browse(self):
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getExistingDirectory(None, 'Select Folder to Save', prev_dir)
        if fileDir != '':
            open_dir = ''
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            self.O_directory = fileDir
            self.ui.lineEditK2_directory_O.setText(fileDir)
            self.ui.labelK2_username_O.setEnabled(True)
            self.ui.comboBoxK2_Name_Folder_O.setEnabled(True)
            self.ui.groupBoxK2_Filename_O.setEnabled(True)
            self.ui.groupBoxK2_File_Type_O.setEnabled(True)
            self.ui.labelK2_comment_O.setEnabled(True)
            self.ui.textEditK2_comment_O.setEnabled(True)
            self.ui.pushButtonK2_Save_O.setEnabled(True)
            self.ui.lineEditK2_Custom_Name_O.setEnabled(True)
            self.ui.labelK2_condition_O.setText("Click save button to save.")
        else:
            self.ui.lineEditK2_directory_O.setText('None')
            self.ui.labelK2_condition_O.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEditK2_GoogleDrive_G.text()).split('\\')
        if os.path.exists(self.ui.lineEditK2_GoogleDrive_G.text()) == False:
            self.ui.labelK2_condition_G.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.labelK2_condition_G.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.labelK2_namefolder_G.setEnabled(True)
                    self.ui.comboBoxK2_Name_Folder_G.setEnabled(True)
                    self.ui.pushButtonK2_Select_Directory_G.setEnabled(True)
                    self.ui.labelK2_condition_G.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBoxK2_Name_Folder_G.currentText())
        if namefolder == 'None':
            self.ui.labelK2_condition_G.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.labelK2_G.setText("Save to \\" + namefolder + "\Date" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Keithely with Array'
            self.ui.groupBoxK2_File_Type_G.setEnabled(True)
            self.ui.groupBoxK2_Filename_G.setEnabled(True)
            self.ui.labelK2_comment_G.setEnabled(True)
            self.ui.textEditK2_comment_G.setEnabled(True)
            self.ui.pushButtonK2_Save_G.setEnabled(True)
            self.ui.lineEditK2_Custom_Name_G.setEnabled(True)
            self.ui.labelK2_condition_G.setText('Click save button to save.')
            
    def Select_type_G(self):
        if self.ui.radioButtonK2_csv_G.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButtonK2_txt_G.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

            
    def Select_type_O(self):
        if self.ui.radioButtonK2_csv_O.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButtonK2_txt_O.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'


    def Select_name_G(self):
        if self.ui.radioButtonK2_Timename_G.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButtonK2_Custom_Name_G.isChecked():
            self.G_file_name = str(self.ui.lineEditK2_Custom_Name_G.text())
            
    def Select_name_O(self):
        if self.ui.radioButtonK2_Timename_O.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButtonK2_Custom_Name_O.isChecked():
            self.O_file_name = str(self.ui.lineEditK2_Custom_Name_O.text())
    
    def Pre_dsave(self):
        if self.ui.checkBoxK2_dsave.isChecked():
            self.ui.labelK2_dsave_directory.setEnabled(True)
            self.ui.lineEditK2_dsave_directory.setEnabled(True)
            self.ui.pushButtonK2_dsave_browse.setEnabled(True)
            self.ui.groupBoxK2_dsave_filename.setEnabled(True)
            self.ui.radioButtonK2_dsave_timename.setEnabled(True)
            self.ui.radioButtonK2_dsave_custname.setEnabled(True)
            self.ui.lineEditK2_dsave_custname.setEnabled(True)
            self.ui.groupBoxK2_dsave_filetype.setEnabled(True)
            self.ui.radioButtonK2_csv.setEnabled(True)
            self.ui.radioButtonK2_txt.setEnabled(True)
            self.ui.labelK2_dsave_username.setEnabled(True)
            self.ui.lineEditK2_dsave_username.setEnabled(True)
            self.ui.labelK2_dsave_comment.setEnabled(True)
            self.ui.textEditK2_dsave_comment.setEnabled(True)
            self.ui.labelK2_condition.setText("Dynamic saving opened.")
        else:
            self.ui.labelK2_dsave_directory.setEnabled(False)
            self.ui.lineEditK2_dsave_directory.setEnabled(False)
            self.ui.pushButtonK2_dsave_browse.setEnabled(False)
            self.ui.groupBoxK2_dsave_filename.setEnabled(False)
            self.ui.radioButtonK2_dsave_timename.setEnabled(False)
            self.ui.radioButtonK2_dsave_custname.setEnabled(False)
            self.ui.lineEditK2_dsave_custname.setEnabled(False)
            self.ui.groupBoxK2_dsave_filetype.setEnabled(False)
            self.ui.radioButtonK2_csv.setEnabled(False)
            self.ui.radioButtonK2_txt.setEnabled(False)
            self.ui.labelK2_dsave_username.setEnabled(False)
            self.ui.lineEditK2_dsave_username.setEnabled(False)
            self.ui.labelK2_dsave_comment.setEnabled(False)
            self.ui.textEditK2_dsave_comment.setEnabled(False)
            self.ui.labelK2_condition.setText("Dynamic saving closed.")
    
    def Dsave_browse(self):
        self.dsave_directory = ''
        prev_dir = os.getcwd()
        fileDir = QFileDialog.getExistingDirectory(None, 'Select Folder to Save', prev_dir)
        if fileDir != '':
            open_dir = ''
            file_list = str(fileDir).split('/')
            for i in range(0, len(file_list) - 1):
                if i < len(file_list) - 1:
                    open_dir += file_list[i] + '\\'
                elif i == len(file_list) - 1:
                    open_dir += file_list[i]
            fileDir.replace('/', '\\')
            self.dsave_directory = fileDir
            self.ui.lineEditK2_dsave_directory.setText(fileDir)
            self.ui.labelK2_condition.setText("Dynamic saving directory selected.")
        else:
            self.ui.lineEditK2_dsave_directory.setText('None')
            self.ui.labelK2_condition.setText('Choose a directory for dynamic saving.')
            
    def Dsave_directory(self):
        self.dsave_dir_ok = True
        if self.ui.lineEditK2_dsave_directory.text() == '' or self.ui.lineEditK2_dsave_directory.text() == 'None':
            self.dsave_dir_ok = False
        
    def Dsave_filename(self):
        self.dsave_filename_ok = True
        self.dsave_filename = ''
        if self.ui.radioButtonK2_dsave_timename.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = 'DSave' + ' ' + date + ' ' + current_time
            self.dsave_filename = str(date_and_time)
        elif self.ui.radioButtonK2_dsave_custname.isChecked():
            self.dsave_filename = str(self.ui.lineEditK2_dsave_custname.text())
            if self.dsave_filename == '':
                self.dsave_filename_ok = False
    
    def Dsave_filetype(self):
        if self.ui.radioButtonK2_csv.isChecked():
            self.dsave_filetype = '.csv'
            self.dsave_divide = ','
        elif self.ui.radioButtonK2_txt.isChecked():
            self.dsave_filetype = '.txt'
            self.dsave_divide = '\t'
            
    def Dsave_username(self):
        self.dsave_username_ok = True
        self.dsave_username = ''
        self.dsave_username = str(self.ui.lineEditK2_dsave_username.text())
        if self.dsave_username == '':
            self.dsave_username_ok = False
    
    def Pre_save(self, date_value, t_value, stepData, Array, gateVolt_data, gateCurr_data, lead_voltage, curr_data, resistance_data):
        self.date_value = date_value
        self.t_value = t_value
        self.stepData = stepData
        self.Array = Array
        self.gateVolt_data = gateVolt_data
        self.curr_data = curr_data
        self.gateCurr_data = gateCurr_data
        self.lead_voltage = lead_voltage
        self.resistance_data = resistance_data
        
    def G_save(self):
        if self.uiSavingGDradioButton[3].isChecked() and self.uiSavingGDlineEdit[1].text() == '':
            self.uiSavingGDlabel[0].setText('Enter a valid file name.')
        else:
            self.Select_type_G()
            self.Select_name_G()
            
            # It contains the measurement information, including user name, date, measurement type, time step etc.
            # This is a two dimensional list. Each sub list related to a single line.
            comments = []
            # For QMDlab data file it is "Collected Data"
            divider = 'Collected Data'
            # Parameters' names, such as VOLTAGE, CURRENT, TIME
            parameters = []
            # Parameters' units
            units = []
            # Include all the data
            data = []
            # Contains file type, divider, name and directory
            file_info = []
            
            # First line user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.uiSavingGDcomboBox[0].currentText()))
            comments.append(temp)
            # Second line edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Third line array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEditK2_directoryGate.text()))
            comments.append(temp)
            # Fourth line visa address
            temp = []
            temp.append('Gate Visa Address:')
            temp.append(str(self.ui.comboBoxK2_gateVisa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate Visa Name:')
            name = str(self.ui.labelK2_gatevisa.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Fifth line visa address
            temp = []
            temp.append('Lead Visa Address:')
            temp.append(str(self.ui.comboBoxK2_leadVisa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Lead Visa Name:')
            name = str(self.ui.labelK2_leadvisa.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Sixth line scan source
            temp = []
            temp.append('Y-Values Units:')
            if self.ui.radioButtonK2_Volts.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonK2_mVolts.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonK2_uVolts.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonK2_nVolts.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Seventh line time step
            temp = []
            temp.append('Lead Output:')
            if self.ui.radioButtonK2_Lead4.isChecked():
                temp.append('4-Terminal')
            elif self.ui.radioButtonK2_Lead2.isChecked():
                temp.append('2-Terminal')
            comments.append(temp)
            # Eighth line output voltage
            temp = []
            temp.append('Output Voltage:')
            temp.append(self.ui.lineEditK2_LeadOutput.text())
            temp.append(self.ui.comboBoxK2_LeadOutput.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditK2_tstep.text()))
            comments.append(temp)
            # Nineth line comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditK2_comment_G.toPlainText()))
            comments.append(temp)
            
            # Do parameters, units and data together
            parameters.append('Date')
            units.append('String')
            data.append(self.date_value)
            parameters.append('Time')
            units.append('s')
            data.append(self.t_value)
            parameters.append('Step')
            units.append('1')
            data.append(self.stepData)
            parameters.append('Step Value')
            units.append('1')
            data.append(self.Array)
            parameters.append('Gate Voltage')
            units.append('Volts')
            data.append(self.gateVolt_data)
            parameters.append('Gate Current')
            units.append('Amps')
            data.append(self.gateCurr_data)
            parameters.append('Lead Voltage')
            units.append('Volts')
            data.append(self.lead_voltage)
            parameters.append('Lead Current')
            units.append('Amps')
            data.append(self.curr_data)
            parameters.append('Lead Resistance')
            units.append('Ohms')
            data.append(self.resistance_data)
            
            # File_info
            # First is file name
            file_info.append(self.G_file_name)
            # csv or txt file
            file_info.append(self.G_type)
            # the divide of csv is "," while for txt its "\t"
            file_info.append(self.G_divide)
            # Always "Collected Data"
            file_info.append(divider)
            # The saving directory
            file_info.append(self.G_directory)
            print file_info
            self.save_thread.input(comments, parameters, units, data, file_info)
            self.ui.pushButtonK2_Open_G.setEnabled(True)
            self.ui.labelK2_condition_G.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBoxK2_Name_Folder_O.currentText() == 'None':
            self.ui.labelK2_condition_O.setText('Pleanse choose a user name.')
        elif self.ui.radioButtonK2_Custom_Name_O.isChecked() and self.ui.lineEdit_Custom_Name_O.text() == '':
            self.ui.labelK2_condition_O.setText('Please enter a file name.')
        else:
            self.Select_type_O()
            self.Select_name_O()
            
            # It contains the measurement information, including user name, date, measurement type, time step etc.
            # This is a two dimensional list. Each sub list related to a single line.
            comments = []
            # For QMDlab data file it is "Collected Data"
            divider = 'Collected Data'
            # Parameters' names, such as VOLTAGE, CURRENT, TIME
            parameters = []
            # Parameters' units
            units = []
            # Include all the data
            data = []
            # Contains file type, divider, name and directory
            file_info = []
            
            # First line user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBoxK2_Name_Folder_O.currentText()))
            comments.append(temp)
            # Second line edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Third line array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEditK2_directoryGate.text()))
            comments.append(temp)
            # Fourth line visa address
            temp = []
            temp.append('Gate Visa Address:')
            temp.append(str(self.ui.comboBoxK2_gateVisa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate Visa Name:')
            name = str(self.ui.labelK2_gatevisa.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Fifth line visa address
            temp = []
            temp.append('Lead Visa Address:')
            temp.append(str(self.ui.comboBoxK2_leadVisa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Lead Visa Name:')
            name = str(self.ui.labelK2_leadvisa.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Sixth line scan source
            temp = []
            temp.append('Y-Values Units:')
            if self.ui.radioButtonK2_Volts.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonK2_mVolts.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonK2_uVolts.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonK2_nVolts.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Seventh line time step
            temp = []
            temp.append('Lead Output:')
            if self.ui.radioButtonK2_Lead4.isChecked():
                temp.append('4-Terminal')
            elif self.ui.radioButtonK2_Lead2.isChecked():
                temp.append('2-Terminal')
            comments.append(temp)
            # Eighth line output voltage
            temp = []
            temp.append('Output Voltage:')
            temp.append(self.ui.lineEditK2_LeadOutput.text())
            temp.append(self.ui.comboBoxK2_LeadOutput.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditK2_tstep.text()))
            comments.append(temp)
            # Nineth line comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditK2_comment_O.toPlainText()))
            comments.append(temp)
            
            # Do parameters, units and data together
            parameters.append('Date')
            units.append('String')
            data.append(self.date_value)
            parameters.append('Time')
            units.append('s')
            data.append(self.t_value)
            parameters.append('Step')
            units.append('1')
            data.append(self.stepData)
            parameters.append('Step Value')
            units.append('1')
            data.append(self.Array)
            parameters.append('Gate Voltage')
            units.append('Volts')
            data.append(self.gateVolt_data)
            parameters.append('Gate Current')
            units.append('Amps')
            data.append(self.gateCurr_data)
            parameters.append('Lead Voltage')
            units.append('Volts')
            data.append(self.lead_voltage)
            parameters.append('Lead Current')
            units.append('Amps')
            data.append(self.curr_data)
            parameters.append('Lead Resistance')
            units.append('Ohms')
            data.append(self.resistance_data)
            
            # File_info
            # First is file name
            file_info.append(self.O_file_name)
            # csv or txt file
            file_info.append(self.O_type)
            # the divide of csv is "," while for txt its "\t"
            file_info.append(self.O_divide)
            # Always "Collected Data"
            file_info.append(divider)
            # The saving directory
            file_info.append(self.O_directory)
            
            self.save_thread.input(comments, parameters, units, data, file_info)
            self.ui.pushButtonK2_Open_O.setEnabled(True)
            self.ui.labelK2_condition_O.setText('File has been saved.')
    
    def G_open(self):
        opendir = self.G_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
    def O_open(self):
        opendir = self.O_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
    
class Collect_data(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def input(self, instruments, ui, Array, go_on, curves, curveWidgets, dsave):
        self.gate = instruments[0]
        self.lead = instruments[1]
        self.ui = ui
        self.Array = np.array(Array)
        self.go_on = go_on
        self.curves = curves
        self.curveWidgets = curveWidgets
        self.dsave_directory = dsave[0]
        self.dsave_filename = dsave[1]
        self.dsave_username = dsave[2]
        self.dsave_thread = dsave[3]
        self.dsave_filetype = dsave[4]
        self.dsave_divide = dsave[5]
        
        lead_index = int(self.ui.comboBoxK2_LeadOutput.currentIndex())
        if lead_index == 0:
            self.lead_voltage_scale = [1, 'Volts']
        elif lead_index == 1:
            self.lead_voltage_scale = [1E-3, 'mVolts']
        elif lead_index == 2:
            self.lead_voltage_scale = [1E-6, 'uVolts']
        elif lead_index == 3:
            self.lead_voltage_scale = [1E-9, 'nVolts']
        self.lead_voltage = float(self.ui.lineEditK2_LeadOutput.text())*self.lead_voltage_scale[0]
        
        
        #self.time_step = float(self.ui.lineEdit_tstep.text())
        if self.ui.radioButtonK2_Volts.isChecked():
            self.gate_voltage_scale = [1, 'Volts']
        elif self.ui.radioButtonK2_mVolts.isChecked():
            self.gate_voltage_scale = [1E-3, 'mVolts']
        elif self.ui.radioButtonK2_uVolts.isChecked():
            self.gate_voltage_scale = [1E-6, 'uVolts']
        elif self.ui.radioButtonK2_nVolts.isChecked():
            self.gate_voltage_scale = [1E-9, 'nVolts']
        self.current_scale = [1, 'Amps']
        self.Array = self.Array*self.gate_voltage_scale[0]
        
        self.stop_collecting = False
        self.pause_collecting = False
        self.time_step = float(self.ui.lineEditK2_tstep.text())
        self.start()
    
    def stop(self):
        self.stop_collecting = True
        self.ui.labelK2_condition.setText('Stopped.')
        self.ui.pushButtonK2_Start.setEnabled(True)
        self.ui.pushButtonK2_Pause.setEnabled(False)
        self.ui.pushButtonK2_Stop.setEnabled(False)
    
    def pause(self):
        if self.pause_collecting:
            self.ui.labelK2_condition.setText('Running...')
            self.ui.pushButtonK2_Pause.setText("Pause")
            self.pause_collecting = False
        else:
            self.ui.labelK2_condition.setText('Paused. Click continue to run.')
            self.ui.pushButtonK2_Pause.setText("Continue")
            self.pause_collecting = True
    
    def run(self):
        self.gateVolt_data = []
        self.gateCurr_data = []
        self.leadVolt_data = []
        self.curr_data = []
        self.resistance_data = []
        self.stepData = []
        self.t_value = []
        date_value = []
        gvd = []
        gcd = []
        lvd = []
        lcd = []
        r = []
        t = []
        
        self.turn_on_gate_voltage()
        self.turn_on_lead_voltage()
        
        start_time = time.time()
        t1_ = 0
        
        for i in range(0, len(self.Array)):
            status = True
            
            while status:
                if float(time.time() - t1_) > self.time_step or self.stop_collecting:
                    t1_ = time.time()
                    while self.pause_collecting:
                        if self.stop_collecting:
                            self.Pre_dynamic_save(i, True)
                            break
                        else:
                            pass
                        
                    if not self.stop_collecting:
                        self.stepData.append(i)
                        self.set_gate_voltage(self.Array[i])
                        self.set_lead_voltage(self.lead_voltage)
                        self.read_data_write()
                        self.data = self.read_data_read()
                        gvd.append(self.data[0])
                        self.gateVolt_data = np.array(gvd)
                        gcd.append(self.data[1])
                        self.gateCurr_data = np.array(gcd)
                        lvd.append(self.lead_voltage)
                        self.leadVolt_data = np.array(lvd)
                        lcd.append(self.data[3])
                        self.curr_data = np.array(lcd)
                        self.resistance = self.data[2]/self.data[3]
                        r.append(self.resistance)
                        self.resistance_data = np.array(r)
                        
                        end_time = time.time()
                        self.during = end_time - start_time
                        t.append(self.during)
                        self.t_value = np.array(t)
                        self.t_plot_scale()
                        if self.ui.radioButtonK2_stepscan.isChecked():
                            self.xlabel = "Steps"
                            self.xdata = self.stepData
                        elif self.ui.radioButtonK2_timescan.isChecked():
                            self.xlabel = 'Time (' + self.time_scale[1] + ')'
                            self.xdata = self.t_value / self.time_scale[0]
                        self.data1 = self.Switch_scale(abs(max(self.gateVolt_data)))
                        self.setup_plot(self.curveWidgets[0], self.curves[0], [self.xdata, self.gateVolt_data * self.data1[0]], ["Gate Voltage", self.xlabel, "Gate Voltage (" + self.data1[1] + "V)"])
                        self.data2 = self.Switch_scale(abs(max(self.curr_data)))
                        self.setup_plot(self.curveWidgets[1], self.curves[1], [self.xdata, self.curr_data * self.data2[0]], ["Lead Current", self.xlabel, "Lead Current (" + self.data2[1] + "A)"])
                        self.data3 = self.Switch_scale(abs(max(self.gateCurr_data)))
                        self.setup_plot(self.curveWidgets[2], self.curves[2], [self.xdata, self.gateCurr_data * self.data3[0]], ["Gate Current", self.xlabel, "Gate Current (" + self.data3[1] + "A)"])
                        self.data4 = self.Switch_scale(abs(max(self.resistance_data)))
                        self.setup_plot(self.curveWidgets[3], self.curves[3], [self.xdata, self.resistance_data * self.data4[0]], ["Lead Resistance", self.xlabel, "Lead Resistance (" + self.data4[1] + "Ohms)"])
                        self.setup_plot(self.curveWidgets[4], self.curves[4], [self.gateVolt_data * self.data1[0], self.curr_data * self.data2[0]], ["Lead Current vs Gate Voltage", "Gate Voltage (" + self.data1[1] + "V)", "Lead Current (" + self.data2[1] + "A)"])
                        self.setup_plot(self.curveWidgets[5], self.curves[5], [self.gateVolt_data * self.data1[0], self.resistance_data * self.data4[0]], ["Lead Resistance vs Gate Voltage", "Gate Voltage (" + self.data1[1] + "V)", "Lead Resistance (" + self.data4[1] + "Ohms)"])
                    
                        self.emit(SIGNAL("print"), i, self.during, self.data[0], self.data[1], self.data[3], self.resistance)

                        now = datetime.datetime.now()
                        date = '%s-%s-%s' % (now.year, now.month, now.day)
                        current_time = '%s:%s:%s' % (now.hour, now.minute, now.second)
                        self.date_and_time = date + ' ' + current_time
                        date_value.append(self.date_and_time)
                        self.Pre_dynamic_save(i, False)
                    else:
                        self.Pre_dynamic_save(i, True)
                        break
                    
                    status = False
                    
        self.Pre_dynamic_save(len(self.Array), True)
        self.turn_off_gate_voltage()
        self.turn_off_lead_voltage()
        self.ui.pushButtonK2_Start.setEnabled(True)
        self.ui.pushButtonK2_Pause.setEnabled(False)
        self.ui.pushButtonK2_Stop.setEnabled(False)
        self.ui.tabWidgetK2_save_keithley.setEnabled(True)
        self.ui.labelK2_condition.setText('Scan completed.')
        self.emit(SIGNAL("data_available"), date_value, self.t_value, self.stepData, self.Array, self.gateVolt_data, self.gateCurr_data, self.leadVolt_data, self.curr_data, self.resistance_data)
        self.MPL_Plot()
    
    def Pre_dynamic_save(self, num, is_last):
        if self.ui.checkBoxK2_dsave.isChecked():
            is_first = False
            comments = []
            parameters = []
            units = []
            data = []
            file_info = []
            
            # File_info
            # First is file name
            file_info.append(self.dsave_filename)
            # csv file
            file_info.append(self.dsave_filetype)
            # the divide of csv is ","
            file_info.append(self.dsave_divide)
            # Always "Collected Data"
            file_info.append('Collected Data')
            # The saving directory
            file_info.append(self.dsave_directory)
            
            if is_last:
                self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
            else:
                data.append(self.date_and_time)
                data.append(self.during)
                data.append(num)
                data.append(self.Array[num])
                data.append(self.data[0].strip('\n'))
                data.append(self.data[1].strip('\n'))
                data.append(self.data[2])
                data.append(self.data[3])
                data.append(self.resistance)
                
                if num == 0:
                    is_first = True
                    
                    temp = []
                    temp.append('User Name:')
                    temp.append(self.dsave_username)
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Edit Time:')
                    temp.append(str(datetime.datetime.now()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Array Source:')
                    temp.append(str(self.ui.lineEditK2_directoryGate.text()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Gate Visa Address:')
                    temp.append(str(self.ui.comboBoxK2_gateVisa.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Gate Visa Name:')
                    name = str(self.ui.labelK2_gatevisa.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Lead Visa Address:')
                    temp.append(str(self.ui.comboBoxK2_leadVisa.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Lead Visa Name:')
                    name = str(self.ui.labelK2_leadvisa.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Y-Values Units:')
                    if self.ui.radioButtonK2_Volts.isChecked():
                        temp.append('Volts')
                    elif self.ui.radioButtonK2_mVolts.isChecked():
                        temp.append('mVolts')
                    elif self.ui.radioButtonK2_uVolts.isChecked():
                        temp.append('uVolts')
                    elif self.ui.radioButtonK2_nVolts.isChecked():
                        temp.append('nVolts')
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Lead Output:')
                    if self.ui.radioButtonK2_Lead4.isChecked():
                        temp.append('4-Terminal')
                    elif self.ui.radioButtonK2_Lead2.isChecked():
                        temp.append('2-Terminal')
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Output Voltage:')
                    temp.append(self.ui.lineEditK2_LeadOutput.text())
                    temp.append(self.ui.comboBoxK2_LeadOutput.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Time Step(sec):')
                    temp.append(str(self.ui.lineEditK2_tstep.text()))
                    comments.append(temp)
                    #####################
                    temp = []
                    temp.append('Comments:')
                    temp.append(str(self.ui.textEditK2_dsave_comment.toPlainText()))
                    comments.append(temp)
                    #####################
                    parameters.append('Date')
                    units.append('String')
                    parameters.append('Time')
                    units.append('s')
                    parameters.append('Step')
                    units.append('1')
                    parameters.append('Step Value')
                    units.append('1')
                    parameters.append('Gate Voltage')
                    units.append('Volts')
                    parameters.append('Gate Current')
                    units.append('Amps')
                    parameters.append('Lead Voltage')
                    units.append('Volts')
                    parameters.append('Lead Current')
                    units.append('Amps')
                    parameters.append('Lead Resistance')
                    units.append('Ohms')
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
                else:
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
      
    def MPL_Plot(self):
        if self.ui.radioButtonK2_stepscan.isChecked():
            self.xlabel = "Steps"
            self.xdata = self.stepData
        elif self.ui.radioButtonK2_timescan.isChecked():
            self.xlabel = 'Time (' + self.time_scale[1] + ')'
            self.xdata = self.t_value / self.time_scale[0]
        
        self.Reset_plot_gate_voltage()
        self.axes_AgateVoltage.grid()
        self.axes_AgateVoltage.set_title("Gate Voltage")
        self.axes_AgateVoltage.set_ylabel("Gate Voltage (" + self.data1[1] + "V)")
        self.axes_AgateVoltage.set_xlabel(self.xlabel)
        self.axes_AgateVoltage.plot(self.xdata, self.gateVolt_data * self.data1[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lead_current()
        self.axes_AleadCurrent.grid()
        self.axes_AleadCurrent.set_title("Lead Current")
        self.axes_AleadCurrent.set_ylabel("Lead Current (" + self.data2[1] + "A)")
        self.axes_AleadCurrent.set_xlabel(self.xlabel)
        self.axes_AleadCurrent.plot(self.xdata, self.curr_data * self.data2[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_gate_current()
        self.axes_AgateCurrent.grid()
        self.axes_AgateCurrent.set_title("Gate Current")
        self.axes_AgateCurrent.set_ylabel("Gate Current (" + self.data3[1] + "A)")
        self.axes_AgateCurrent.set_xlabel(self.xlabel)
        self.axes_AgateCurrent.plot(self.xdata, self.gateCurr_data * self.data3[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lead_resistance()
        self.axes_ALeadResistance.grid()
        self.axes_ALeadResistance.set_title("Lead Resistance")
        self.axes_ALeadResistance.set_ylabel("Lead Resistance (" + self.data4[1] + "Ohms)")
        self.axes_ALeadResistance.set_xlabel(self.xlabel)
        self.axes_ALeadResistance.plot(self.xdata, self.resistance_data * self.data4[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_leadcurrent_gatevoltage()
        self.axes_ALeadCurrentGateVoltage.grid()
        self.axes_ALeadCurrentGateVoltage.set_title("Lead Current vs Gate Voltage")
        self.axes_ALeadCurrentGateVoltage.set_ylabel("Lead Current (" + self.data2[1] + "A)")
        self.axes_ALeadCurrentGateVoltage.set_xlabel("Gate Voltage (" + self.data1[1] + "V)")
        self.axes_ALeadCurrentGateVoltage.plot(self.gateVolt_data * self.data1[0], self.curr_data * self.data2[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_leadresistance_gatevoltage()
        self.axes_ALeadResistanceGateVoltage.grid()
        self.axes_ALeadResistanceGateVoltage.set_title("Lead Resistance vs Gate Voltage")
        self.axes_ALeadResistanceGateVoltage.set_ylabel("Lead Resistance (" + self.data4[1] + "Ohms)")
        self.axes_ALeadResistanceGateVoltage.set_xlabel("Gate Voltage (" + self.data1[1] + "V)")
        self.axes_ALeadResistanceGateVoltage.plot(self.gateVolt_data * self.data1[0], self.resistance_data * self.data4[0], marker = 'o', linestyle = '-')
        
        self.emit(SIGNAL("mpl_plot"))
        
    def Reset_plot_gate_voltage(self):
        self.ui.mplwidgetK2_AgateVoltage.figure.clear()
        self.axes_AgateVoltage = self.ui.mplwidgetK2_AgateVoltage.figure.add_subplot(111)
        
    def Reset_plot_lead_current(self):
        self.ui.mplwidgetK2_AleadCurrent.figure.clear()
        self.axes_AleadCurrent = self.ui.mplwidgetK2_AleadCurrent.figure.add_subplot(111)

    def Reset_plot_gate_current(self):
        self.ui.mplwidgetK2_AgateCurrent.figure.clear()
        self.axes_AgateCurrent = self.ui.mplwidgetK2_AgateCurrent.figure.add_subplot(111)
        
    def Reset_plot_lead_resistance(self):
        self.ui.mplwidgetK2_ALeadResistance.figure.clear()
        self.axes_ALeadResistance = self.ui.mplwidgetK2_ALeadResistance.figure.add_subplot(111)
        
    def Reset_plot_leadcurrent_gatevoltage(self):
        self.ui.mplwidgetK2_ALeadCurrentGateVoltage.figure.clear()
        self.axes_ALeadCurrentGateVoltage = self.ui.mplwidgetK2_ALeadCurrentGateVoltage.figure.add_subplot(111)
        
    def Reset_plot_leadresistance_gatevoltage(self):
        self.ui.mplwidgetK2_ALeadResistanceGateVoltage.figure.clear()
        self.axes_ALeadResistanceGateVoltage = self.ui.mplwidgetK2_ALeadResistanceGateVoltage.figure.add_subplot(111)
        
    def setup_plot(self, curveWidget, curve, data, titles):
        curveWidget.plot.set_titles(titles[0], titles[1], titles[2])
        curve.set_data(data[0], data[1])
        self.emit(SIGNAL("curve_plot"), [curveWidget, curve])
    

    def set_gate_voltage(self, gate_voltage):
        self.gate.write('TRACE:CLEar "defbuffer1"')
        self.gate.write("ROUT:TERM FRONT")
        self.gate.write('SENS:FUNC "CURR"')
        #self.gate.write('SOUR:VOLT:RANG AUTO')
        self.gate.write("SOUR:FUNC VOLT")
        self.gate.write("SOUR:VOLT:READ:BACK 1")
        self.gate.write("SOUR:VOLT " + str(gate_voltage))
    
    def turn_on_gate_voltage(self):
        self.gate.write('SENS:CURR:RSEN OFF' )    #ON = 4 Contact   OFF = 2 Contact
        self.gate.write("OUTP ON")
    
    def turn_off_gate_voltage(self):
        self.gate.write("OUTP OFF")

    def read_data_write(self):
        self.gate.write('READ? "defbuffer1", SOUR, READ')
        self.lead.write('READ? "defbuffer1", SOUR, READ')
        
    def read_data_read(self):
        voltage1, current1 = self.gate.read().replace("\n", "").split(",")
        voltage2, current2 = self.lead.read().replace("\n", "").split(",")
        return [float(voltage1), float(current1), float(voltage2), float(current2)]
    
    ##MEASURE RESISTANCE ON INSTRUMENT 1#####
    ## 4-Terminal Across the Silicon###    
    def set_lead_voltage(self, lead_voltage):
        self.lead.write('TRACE:CLEar "defbuffer1"')
        self.lead.write("ROUT:TERM FRONT")
        self.lead.write('SENS:FUNC "CURR"')
        self.lead.write("SOUR:FUNC VOLT")
        self.lead.write("SOUR:VOLT:READ:BACK 1")
        self.lead.write("SOUR:VOLT " + str(lead_voltage))
    
    def turn_on_lead_voltage(self):
        if self.ui.radioButtonK2_Lead4.isChecked():
            self.lead.write('SENS:CURR:RSEN ON' )    #ON = 4 Contact   OFF = 2 Contact
        elif self.ui.radioButtonK2_Lead2.isChecked():
            self.lead.write('SENS:CURR:RSEN OFF' ) 
        self.lead.write("OUTP ON")
    
    def turn_off_lead_voltage(self):
        if not self.ui.checkBoxK2_Output_on.isChecked():
            self.lead.write("OUTP OFF")

    def t_plot_scale(self):
        if abs(self.during) < 2000:
            self.time_scale = [1, "Secs"]
        elif abs(self.during) >= 2000 and abs(max(self.t_plot)) < 20000:
            self.time_scale = [60, "Mins"]
        elif abs(self.during) > 20000:
            self.time_scale = [3600, "Hours"]
            
    def Switch_scale(self, temp):
        if temp >= 1:
            scale = [1, ""]
        elif temp >= 1E-3 and temp < 1:
            scale = [1E3, "m"]
        elif temp >= 1E-6 and temp < 1E-3:
            scale = [1E6, "u"]
        elif temp >= 1E-9 and temp < 1E-6:
            scale = [1E9, "n"]
        elif temp < 1E-9:
            scale = [1E12, "p"]
        return scale
    
    def __del__(self):
        self.exiting = True
        self.wait()
        