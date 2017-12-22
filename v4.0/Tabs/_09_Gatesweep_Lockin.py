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

class Gatesweep_Lockin():
    
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.collect_data_thread = Collect_data()
        self.save_thread = Save_Thread()
        self.dsave_thread = Dynamic_Save_Thread()
        
        main.connect(self.ui.pushButtonGL_browse_array1, SIGNAL('clicked()'), self.Browse_Array1)
        main.connect(self.ui.pushButtonGL_import_gate1, SIGNAL('clicked()'), self.Import_Array1)
        main.connect(self.ui.pushButtonGL_copy_array1, SIGNAL('clicked()'), self.Copy_Array1)
        main.connect(self.ui.pushButtonGL_back, SIGNAL('clicked()'), self.Back)
        main.connect(self.ui.pushButtonGL_browse_array2, SIGNAL('clicked()'), self.Browse_Array2)
        main.connect(self.ui.pushButtonGL_import_gate2, SIGNAL('clicked()'), self.Import_Array2)
        main.connect(self.ui.pushButtonGL_copy_array2, SIGNAL('clicked()'), self.Copy_Array2)
        main.connect(self.ui.pushButtonGL_update_gate1, SIGNAL('clicked()'), lambda : self.Update_visa("gate1", self.ui.comboBoxGL_gate1))
        main.connect(self.ui.pushButtonGL_update_gate2, SIGNAL('clicked()'), lambda : self.Update_visa("gate2", self.ui.comboBoxGL_gate2))
        main.connect(self.ui.pushButtonGL_a_update, SIGNAL('clicked()'), lambda : self.Update_visa("agilent", self.ui.comboBoxGL_a_visa))
        main.connect(self.ui.pushButtonGL_select_gate1, SIGNAL('clicked()'), lambda : self.Select_visa("gate1", self.gate1_visa, self.ui.comboBoxGL_gate1, self.ui.labelGL_visaname_gate1, [self.ui.pushButtonGL_select_gate1, self.ui.pushButtonGL_close_gate1]))
        main.connect(self.ui.pushButtonGL_select_gate2, SIGNAL('clicked()'), lambda : self.Select_visa("gate2", self.gate2_visa, self.ui.comboBoxGL_gate2, self.ui.labelGL_visaname_gate2, [self.ui.pushButtonGL_select_gate2, self.ui.pushButtonGL_close_gate2]))
        main.connect(self.ui.pushButtonGL_a_select, SIGNAL('clicked()'), lambda : self.Select_visa("agilent", self.agilent_visa, self.ui.comboBoxGL_a_visa, self.ui.labelGL_a_visaname, [self.ui.pushButtonGL_a_select, self.ui.pushButtonGL_a_close]))
        main.connect(self.ui.pushButtonGL_close_gate1, SIGNAL('clicked()'), lambda : self.Close_visa("gate1", self.gate1_visa, self.ui.labelGL_visaname_gate1, [self.ui.pushButtonGL_select_gate1, self.ui.pushButtonGL_close_gate1]))
        main.connect(self.ui.pushButtonGL_close_gate2, SIGNAL('clicked()'), lambda : self.Close_visa("gate2", self.gate2_visa, self.ui.labelGL_visaname_gate2, [self.ui.pushButtonGL_select_gate2, self.ui.pushButtonGL_close_gate2]))
        main.connect(self.ui.pushButtonGL_a_close, SIGNAL('clicked()'), lambda : self.Close_visa("agilent", self.agilent_visa, self.ui.labelGL_a_visaname, [self.ui.pushButtonGL_a_select, self.ui.pushButtonGL_a_close]))
        main.connect(self.ui.pushButtonGL_Start, SIGNAL('clicked()'), self.start)
        main.connect(self.ui.pushButtonGL_Stop, SIGNAL('clicked()'), self.collect_data_thread.stop)
        main.connect(self.ui.pushButtonGL_Pause, SIGNAL('clicked()'), self.collect_data_thread.pause)
        main.connect(self.ui.pushButtonGL_browse_save_G, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButtonGL_browse_save_O, SIGNAL('clicked()'), self.Other_browse)
        main.connect(self.ui.pushButtonGL_check_G, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButtonGL_Select_Directory_G, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.pushButtonGL_Save_G, SIGNAL('clicked()'), self.G_save)
        main.connect(self.ui.pushButtonGL_Open_G, SIGNAL('clicked()'), self.G_open)
        main.connect(self.ui.pushButtonGL_Save_O, SIGNAL('clicked()'), self.O_save)
        main.connect(self.ui.pushButtonGL_Open_O, SIGNAL('clicked()'), self.O_open)
        main.connect(self.ui.pushButtonGL_confirm, SIGNAL('clicked()'), self.Confirm)
        main.connect(self.collect_data_thread, SIGNAL("curve_plot"), self.curvePlots_update)
        main.connect(self.collect_data_thread, SIGNAL("mpl_plot"), self.mplPlots)
        main.connect(self.collect_data_thread, SIGNAL("data_available"), self.Pre_save)
        main.connect(self.collect_data_thread, SIGNAL("print"), self.Print_data)
        main.connect(self.ui.checkBoxGL_dsave, SIGNAL("clicked()"), self.Pre_dsave)
        main.connect(self.ui.pushButtonGL_dsave_browse, SIGNAL('clicked()'), self.Dsave_browse)
        main.connect(self.ui.radioButtonGL_timescan, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
        main.connect(self.ui.radioButtonGL_stepscan, SIGNAL("clicked()"), self.collect_data_thread.MPL_Plot)
        
        self.ui.mplwidgetGL_array1 = self.make_mplToolBar(self.ui.mplwidgetGL_array1, self.ui.widgetGL_array1)
        self.ui.mplwidgetGL_array2 = self.make_mplToolBar(self.ui.mplwidgetGL_array2, self.ui.widgetGL_array2)
        self.ui.mplwidgetGL_gate1_voltage = self.make_mplToolBar(self.ui.mplwidgetGL_gate1_voltage, self.ui.widgetGL_gate1_voltage)
        self.ui.mplwidgetGL_gate1_current = self.make_mplToolBar(self.ui.mplwidgetGL_gate1_current, self.ui.widgetGL_gate1_current)
        self.ui.mplwidgetGL_gate2_voltage = self.make_mplToolBar(self.ui.mplwidgetGL_gate2_voltage, self.ui.widgetGL_gate2_voltage)
        self.ui.mplwidgetGL_gate2_current = self.make_mplToolBar(self.ui.mplwidgetGL_gate2_current, self.ui.widgetGL_gate2_current)
        self.ui.mplwidgetGL_agilent_voltage = self.make_mplToolBar(self.ui.mplwidgetGL_agilent_voltage, self.ui.widgetGL_agilent_voltage)
        self.ui.mplwidgetGL_lockin_voltage = self.make_mplToolBar(self.ui.mplwidgetGL_lockin_voltage, self.ui.widgetGL_lockin_voltage)
        self.ui.mplwidgetGL_lockin_gate1 = self.make_mplToolBar(self.ui.mplwidgetGL_lockin_gate1, self.ui.widgetGL_lockin_gate1)
        self.ui.mplwidgetGL_lockin_gate2 = self.make_mplToolBar(self.ui.mplwidgetGL_lockin_gate2, self.ui.widgetGL_lockin_gate2)

        self.axes_gateArray1 = None
        self.axes_gateArray2 = None
        self.axes_gate1_voltage = None
        self.axes_gate1_current = None
        self.axes_gate2_voltage = None
        self.axes_gate2_current = None
        self.axes_agilent_voltage = None
        self.axes_lockin_voltage = None
        self.axes_lockin_gate1 = None
        self.axes_lockin_gate2 = None
        
        self.curve_itemGL_gate1_voltage = self.make_curveWidgets(self.ui.curvewidgetGL_gate1_voltage, "b", titles = ["Gate1 Voltage", "Steps", "Gate1 Voltage (V)"])
        self.curve_itemGL_gate1_current = self.make_curveWidgets(self.ui.curvewidgetGL_gate1_current, "b", titles = ["Gate1 Current", "Steps", "Gate1 Current (A)"])
        self.curve_itemGL_gate2_voltage = self.make_curveWidgets(self.ui.curvewidgetGL_gate2_voltage, "b", titles = ["Gate2 Voltage", "Steps", "Gate2 Voltage (V)"])
        self.curve_itemGL_gate2_current = self.make_curveWidgets(self.ui.curvewidgetGL_gate2_current, "b", titles = ["Gate2 Current", "Steps", "Gate2 Current (A)"])
        self.curve_itemGL_agilent_voltage = self.make_curveWidgets(self.ui.curvewidgetGL_agilent_voltage, "b", titles = ["Agilent Voltage", "Steps", "Agilent Voltage (V)"])
        self.curve_itemGL_lockin_voltage = self.make_curveWidgets(self.ui.curvewidgetGL_lockin_voltage, "b", titles = ["Lock-in Voltage", "Steps", "Lock-in Voltage (V)"])
        self.curve_itemGL_lockin_gate1 = self.make_curveWidgets(self.ui.curvewidgetGL_lockin_gate1, "b", titles = ["Lock-in Voltage vs Gate1 Voltage", "Gate1 Voltage (V)", "Lock-in Voltage (V)"])
        self.curve_itemGL_lockin_gate2 = self.make_curveWidgets(self.ui.curvewidgetGL_lockin_gate2, "b", titles = ["Lock-in Voltage vs Gate2 Voltage", "Gate2 Voltage (V)", "Lock-in Voltage (V)"])
        
        self.gate1_visa = None
        self.gate2_visa = None
        self.agilent_visa = None
        self.Update_visa("gate1", self.ui.comboBoxGL_gate1)
        self.Update_visa("gate2", self.ui.comboBoxGL_gate2)
        self.Update_visa("agilent", self.ui.comboBoxGL_a_visa)

        self.Array1 = []
        self.Array2 = []
        self.len_Array1 = 0
        self.len_Array2 = 0
        self.count = 0
        self.go_on = True
        self.dsave_directory = ''
        self.array1_imported = False
        self.array2_imported = False
        self.gate1_visa_ok = False
        self.gate2_visa_ok = False
        self.a_visa_ok = False
        self.lockin_ok = False
        
        self.uiSavingGDpushButtons = [ self.ui.pushButtonGL_browse_save_G, self.ui.pushButtonGL_check_G, self.ui.pushButtonGL_Select_Directory_G, self.ui.pushButtonGL_Save_G, self.ui.pushButtonGL_Open_G]
        self.uiSavingGDradioButton = [self.ui.radioButtonGL_csv_G, self.ui.radioButtonGL_txt_G, self.ui.radioButtonGL_Timename_G, self.ui.radioButtonGL_Custom_Name_G]
        self.uiSavingGDtextEdit = [self.ui.textEditGL_comment_G]
        self.uiSavingGDcomboBox = [self.ui.comboBoxGL_Name_Folder_G]
        self.uiSavingGDlineEdit = [self.ui.lineEditGL_GoogleDrive_G, self.ui.lineEditGL_Custom_Name_G]
        self.uiSavingGDlabel = [self.ui.labelGL_condition_G]

        self.sens_list = [100, 200, 500, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1, 2, 5, 10, 20, 50, 100, 200, 500]
        self.sens_labels = [self.ui.GL0, self.ui.GL1, self.ui.GL2, self.ui.GL3, self.ui.GL4, self.ui.GL5, self.ui.GL6, self.ui.GL7, self.ui.GL8, self.ui.GL9, self.ui.GL10, self.ui.GL11, self.ui.GL12, self.ui.GL13, self.ui.GL14, self.ui.GL15, self.ui.GL16, self.ui.GL17, self.ui.GL18, self.ui.GL19, self.ui.GL20]
        self.blue = 0
        self.confirm_num = 0
        
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
    
    def Browse_Array1(self):
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
            self.ui.lineEditGL_array1.setText(fileDir)
            self.ui.pushButtonGL_import_gate1.setEnabled(True)
            self.ui.labelGL_condition.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
        else:
            self.ui.labelGL_condition.setText("Please choose valid file to import.")

    def Import_Array1(self):
        self.array1_imported = False
        divider_found = True
        count = 0
        temp = 0
        self.Array1 = []
        x_value = []
        y_value = []
        fileDir = self.ui.lineEditGL_array1.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.labelGL_condition.setText("Data not found in file. Please check it.")
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
                self.Array1.append(float(value[1]))
                temp += 1
            self.len_Array1 = temp
            if self.len_Array2 != 0:
                if self.len_Array1 == self.len_Array2:
                    self.plot_data(self.axes_gateArray1, x_value, y_value, ["Array1 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array1)
                    self.array1_imported = True
                    self.ui.labelGL_condition.setText("File is imported correctly.")
                    if self.array1_imported and self.array2_imported:
                        self.ui.scrollAreaGL_lockin.setEnabled(True)
                        self.ui.pushButtonGL_confirm.setEnabled(True)
                    if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                        self.ui.groupBoxGL_dsave.setEnabled(True)
                        self.ui.checkBoxGL_dsave.setEnabled(True)
                        self.ui.groupBoxGL_control.setEnabled(True)
                        self.ui.pushButtonGL_Pause.setEnabled(False)
                        self.ui.pushButtonGL_Stop.setEnabled(False)
                        self.ui.groupBoxGL_scan.setEnabled(True)
                        self.ui.radioButtonGL_stepscan.setEnabled(True)
                else:
                    self.ui.labelGL_condition.setText('Different array step numbers.')
            elif self.len_Array2 == 0:
                self.plot_data(self.axes_gateArray1, x_value, y_value, ["Array1 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array1)
                self.array1_imported = True
                self.ui.labelGL_condition.setText("File is imported correctly.")
                if self.array1_imported and self.array2_imported:
                    self.ui.scrollAreaGL_lockin.setEnabled(True)
                    self.ui.pushButtonGL_confirm.setEnabled(True)
                if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                    self.ui.groupBoxGL_dsave.setEnabled(True)
                    self.ui.checkBoxGL_dsave.setEnabled(True)
                    self.ui.groupBoxGL_control.setEnabled(True)
                    self.ui.pushButtonGL_Pause.setEnabled(False)
                    self.ui.pushButtonGL_Stop.setEnabled(False)
                    self.ui.groupBoxGL_scan.setEnabled(True)
                    self.ui.radioButtonGL_stepscan.setEnabled(True)
                    
    def Copy_Array1(self):
        self.array1_imported = False
        Values = self.copyDataFunc()
        if Values != None:
            self.ui.labelGL_condition.setText('Array has been copied and plotted.')
            #self.ui.tabWidget_plot_keithely.setCurrentIndex(0)
            self.Array1 = []
            x_value = []
            y_value = []
            item = 0
            for i in range(0, len(Values)):
                for j in range(0, len(Values[i])):
                    x_value.append(item)
                    x_value.append(item + 1)
                    y_value.append(Values[i][j])
                    y_value.append(Values[i][j])
                    self.Array1.append(Values[i][j])
                    item += 1
            self.len_Array1 = item
            if self.len_Array2 != 0:
                if self.len_Array1 == self.len_Array2:
                    self.plot_data(self.axes_gateArray1, x_value, y_value, ["Array1 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array1)
                    self.ui.lineEditGL_array1.setText('From Array Builder Tab.')
                    self.array1_imported = True
                    if self.array1_imported and self.array2_imported:
                        self.ui.scrollAreaGL_lockin.setEnabled(True)
                        self.ui.pushButtonGL_confirm.setEnabled(True)
                    if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                        self.ui.groupBoxGL_dsave.setEnabled(True)
                        self.ui.checkBoxGL_dsave.setEnabled(True)
                        self.ui.groupBoxGL_control.setEnabled(True)
                        self.ui.pushButtonGL_Pause.setEnabled(False)
                        self.ui.pushButtonGL_Stop.setEnabled(False)
                        self.ui.groupBoxGL_scan.setEnabled(True)
                        self.ui.radioButtonGL_stepscan.setEnabled(True)
                else:
                    self.ui.labelGL_condition.setText('Different array step numbers.')
            elif self.len_Array2 == 0:
                self.plot_data(self.axes_gateArray1, x_value, y_value, ["Array1 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array1)
                self.ui.lineEditGL_array1.setText('From Array Builder Tab.')
                self.array1_imported = True
                if self.array1_imported and self.array2_imported:
                    self.ui.scrollAreaGL_lockin.setEnabled(True)
                    self.ui.pushButtonGL_confirm.setEnabled(True)
                if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                    self.ui.groupBoxGL_dsave.setEnabled(True)
                    self.ui.checkBoxGL_dsave.setEnabled(True)
                    self.ui.groupBoxGL_control.setEnabled(True)
                    self.ui.pushButtonGL_Pause.setEnabled(False)
                    self.ui.pushButtonGL_Stop.setEnabled(False)
                    self.ui.groupBoxGL_scan.setEnabled(True)
                    self.ui.radioButtonGL_stepscan.setEnabled(True)
        else:
            self.ui.labelGL_condition.setText('No valid array to copy.')
    
    def Back(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def Browse_Array2(self):
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
            self.ui.lineEditGL_array2.setText(fileDir)
            self.ui.pushButtonGL_import_gate2.setEnabled(True)
            self.ui.labelGL_condition.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
        else:
            self.ui.labelGL_condition.setText("Please choose valid file to import.")

    def Import_Array2(self):
        self.array2_imported = False
        divider_found = True
        count = 0
        temp = 0
        self.Array2 = []
        x_value = []
        y_value = []
        fileDir = self.ui.lineEditGL_array2.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.lineEditGL_array2.setText("Data not found in file. Please check it.")
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
                #print 'line: ' + line
                if line == '':
                    break
                value = line.split(',')
                x_value.append(temp)
                x_value.append(temp + 1)
                y_value.append(value[1])
                y_value.append(value[1])
                self.Array2.append(float(value[1]))
                temp += 1
            self.len_Array2 = temp
            if self.len_Array1 != 0:
                if self.len_Array1 == self.len_Array2:
                    self.plot_data(self.axes_gateArray2, x_value, y_value, ["Array2 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array2)
                    self.array2_imported = True
                    self.ui.labelGL_condition.setText("File is imported correctly.")
                    if self.array1_imported and self.array2_imported:
                        self.ui.scrollAreaGL_lockin.setEnabled(True)
                        self.ui.pushButtonGL_confirm.setEnabled(True)
                    if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                        self.ui.groupBoxGL_dsave.setEnabled(True)
                        self.ui.checkBoxGL_dsave.setEnabled(True)
                        self.ui.groupBoxGL_control.setEnabled(True)
                        self.ui.pushButtonGL_Pause.setEnabled(False)
                        self.ui.pushButtonGL_Stop.setEnabled(False)
                        self.ui.groupBoxGL_scan.setEnabled(True)
                        self.ui.radioButtonGL_stepscan.setEnabled(True)
                else:
                    self.ui.labelGL_condition.setText('Different array step numbers.')
            elif self.len_Array1 == 0:
                self.plot_data(self.axes_gateArray2, x_value, y_value, ["Array2 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array2)
                self.array2_imported = True
                self.ui.labelGL_condition.setText("File is imported correctly.")
                if self.array1_imported and self.array2_imported:
                    self.ui.scrollAreaGL_lockin.setEnabled(True)
                    self.ui.pushButtonGL_confirm.setEnabled(True)
                if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                    self.ui.groupBoxGL_dsave.setEnabled(True)
                    self.ui.checkBoxGL_dsave.setEnabled(True)
                    self.ui.groupBoxGL_control.setEnabled(True)
                    self.ui.pushButtonGL_Pause.setEnabled(False)
                    self.ui.pushButtonGL_Stop.setEnabled(False)
                    self.ui.groupBoxGL_scan.setEnabled(True)
                    self.ui.radioButtonGL_stepscan.setEnabled(True)
            
    def Copy_Array2(self):
        self.array2_imported = False
        Values = self.copyDataFunc()
        if Values != None:
            self.ui.labelGL_condition.setText('Array has been copied and plotted.')
            #self.ui.tabWidget_plot_keithely.setCurrentIndex(0)
            self.Array2 = []
            x_value = []
            y_value = []
            item = 0
            for i in range(0, len(Values)):
                for j in range(0, len(Values[i])):
                    x_value.append(item)
                    x_value.append(item + 1 - 0.0001)
                    y_value.append(Values[i][j])
                    y_value.append(Values[i][j])
                    self.Array2.append(Values[i][j])
                    item += 1
            self.len_Array2 = item
            if self.len_Array1 != 0:
                if self.len_Array1 == self.len_Array2:
                    self.plot_data(self.axes_gateArray2, x_value, y_value, ["Array2 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array2)
                    self.ui.lineEditGL_array2.setText('From Array Builder Tab.')
                    self.array2_imported = True
                    if self.array1_imported and self.array2_imported:
                        self.ui.scrollAreaGL_lockin.setEnabled(True)
                        self.ui.pushButtonGL_confirm.setEnabled(True)
                    if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                        self.ui.groupBoxGL_dsave.setEnabled(True)
                        self.ui.checkBoxGL_dsave.setEnabled(True)
                        self.ui.groupBoxGL_control.setEnabled(True)
                        self.ui.pushButtonGL_Pause.setEnabled(False)
                        self.ui.pushButtonGL_Stop.setEnabled(False)
                        self.ui.groupBoxGL_scan.setEnabled(True)
                        self.ui.radioButtonGL_stepscan.setEnabled(True)
                else:
                    self.ui.labelGL_condition.setText('Different array step numbers.')
            elif self.len_Array1 == 0:
                self.plot_data(self.axes_gateArray2, x_value, y_value, ["Array2 Import Plot", "Steps", "Values"], self.ui.mplwidgetGL_array2)
                self.ui.lineEditGL_array2.setText('From Array Builder Tab.')
                self.array2_imported = True
                if self.array1_imported and self.array2_imported:
                    self.ui.scrollAreaGL_lockin.setEnabled(True)
                    self.ui.pushButtonGL_confirm.setEnabled(True)
                if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
                    self.ui.groupBoxGL_dsave.setEnabled(True)
                    self.ui.checkBoxGL_dsave.setEnabled(True)
                    self.ui.groupBoxGL_control.setEnabled(True)
                    self.ui.pushButtonGL_Pause.setEnabled(False)
                    self.ui.pushButtonGL_Stop.setEnabled(False)
                    self.ui.groupBoxGL_scan.setEnabled(True)
                    self.ui.radioButtonGL_stepscan.setEnabled(True)
        else:
            self.ui.labelGL_condition.setText('No valid array to copy.')
    
    def plot_reset(self, axes, mplwidget):
        mplwidget.figure.clear()
        axes = mplwidget.figure.add_subplot(111)
        return axes
    
    def plot_data(self, axes, x, y, titles, mplwidget):
        axes = self.plot_reset(axes, mplwidget)
        axes.plot(x, y, marker = '.', linestyle = '-')
        axes.grid()
        axes.set_title(titles[0])
        axes.set_xlabel(titles[1])
        axes.set_ylabel(titles[2])
        mplwidget.draw()
    
    def Print_data(self, i, during, gate1_Vdata, gate1_Cdata, gate2_Vdata, gate2_Cdata, agilent_Vdata, lockin_Vdata, sens_scale):
        self.ui.labelGL_step.setText(str(i))
        self.ui.labelGL_time.setText(format(during, '.3f'))
        self.ui.labelGL_time_unit.setText('s')
        data = self.Twist_scale(gate1_Vdata)
        self.ui.labelGL_1.setText(format(data[0], '.3f'))
        self.ui.labelGL_1unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(gate1_Cdata)
        self.ui.labelGL_2.setText(format(data[0], '.3f'))
        self.ui.labelGL_2unit.setText(data[1] + 'Curr')
        data = self.Twist_scale(gate2_Vdata)
        self.ui.labelGL_3.setText(format(data[0], '.3f'))
        self.ui.labelGL_3unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(gate2_Cdata)
        self.ui.labelGL_4.setText(format(data[0], '.3f'))
        self.ui.labelGL_4unit.setText(data[1] + 'Curr')
        data = self.Twist_scale(agilent_Vdata)
        self.ui.labelGL_5.setText(format(data[0], '.3f'))
        self.ui.labelGL_5unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(lockin_Vdata)
        self.ui.labelGL_6.setText(format(data[0], '.3f'))
        self.ui.labelGL_6unit.setText(data[1] + 'Volt')
        self.ui.labelGL_7.setText(str(sens_scale[0]))
        self.ui.labelGL_7unit.setText(str(sens_scale[1]))
        
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
    
    def Update_visa(self, gateLead, comboBoxVisa):
        rm = visa.ResourceManager()
        try:
            all_visas = rm.list_resources()
        except:
            all_visas = "No Visa Available."
        if gateLead == "gate1":
            self.ui.comboBoxGL_gate1.clear()
            self.gate1_visa_ok = False
        elif gateLead == "gate2":
            self.ui.comboBoxGL_gate2.clear()
            self.gate2_visa_ok = False
        elif gateLead == "agilent":
            self.ui.comboBoxGL_a_visa.clear()
            self.a_visa_ok = False
        
        for item in all_visas:
            if gateLead == "gate1":
                self.ui.comboBoxGL_gate1.addItem(item)
            elif gateLead == "gate2":
                self.ui.comboBoxGL_gate2.addItem(item)
            elif gateLead == "agilent":
                self.ui.comboBoxGL_a_visa.addItem(item)
    
    def Select_visa(self, gateLead, visa_chosen, comboBoxVisa, lineEditVisa, selectClose):
        visa_address = str(comboBoxVisa.currentText())
        rm = visa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource(visa_address)
        visa_check = self.Check_visa(inst)
        if visa_check == True:
            self.ui.labelGL_condition.setText("Visa is selected succefully!")
            visa_name = inst.query("*IDN?")
            name_list = visa_name.split(',')
            first_name = name_list[0]
            if gateLead == "gate1":
                if first_name == 'KEITHLEY INSTRUMENTS INC.':
                    if self.gate2_visa_ok:
                        if self.ui.comboBoxGL_gate2.currentText() == visa_address:
                            self.ui.labelGL_condition.setText('Select a different Keithley.')
                        else:
                            self.gate1_visa_ok = True
                            lineEditVisa.setText(visa_name)
                            selectClose[0].setEnabled(False)
                            selectClose[1].setEnabled(True)
                            self.Enable(gateLead)
                            self.gate1_visa = inst
                    else:
                        self.gate1_visa_ok = True
                        lineEditVisa.setText(visa_name)
                        selectClose[0].setEnabled(False)
                        selectClose[1].setEnabled(True)
                        self.Enable(gateLead)
                        self.gate1_visa = inst
                else:
                    self.ui.labelGL_condition.setText('Invalid Keitley visa.')
            elif gateLead == "gate2":
                if first_name == 'KEITHLEY INSTRUMENTS INC.':
                    if self.gate1_visa_ok:
                        if self.ui.comboBoxGL_gate1.currentText() == visa_address:
                            self.ui.labelGL_condition.setText('Select a different Keithley.')
                        else:
                            self.gate2_visa_ok = True
                            lineEditVisa.setText(visa_name)
                            selectClose[0].setEnabled(False)
                            selectClose[1].setEnabled(True)
                            self.Enable(gateLead)
                            self.gate2_visa = inst
                    else:
                        self.gate2_visa_ok = True
                        lineEditVisa.setText(visa_name)
                        selectClose[0].setEnabled(False)
                        selectClose[1].setEnabled(True)
                        self.gate2_visa = inst
                        self.Enable(gateLead)
                else:
                    self.ui.labelGL_condition.setText('Invalid Keithley visa.')
            elif gateLead == "agilent":
                if first_name == 'Agilent Technologies':
                    self.a_visa_ok = True
                    lineEditVisa.setText(visa_name)
                    selectClose[0].setEnabled(False)
                    selectClose[1].setEnabled(True)
                    self.agelient_visa = inst
                else:
                    self.ui.labelGL_condition.setText('Invalid Agilent visa.')
        elif visa_check == False:
            self.ui.labelGL_condition.setText("Invalid visa address.")
            lineEditVisa.setText("None.")
            visa_chosen = False
            
        if self.gate1_visa_ok and self.gate2_visa_ok:
            self.ui.labelGL_timestep.setEnabled(True)
            self.ui.lineEditGL_tstep.setEnabled(True)
        if self.gate1_visa_ok and self.gate2_visa_ok and self.a_visa_ok and self.array1_imported and self.array2_imported and self.lockin_ok:
            self.ui.groupBoxGL_control.setEnabled(True)
            self.ui.pushButtonGL_Pause.setEnabled(False)
            self.ui.pushButtonGL_Stop.setEnabled(False)
            self.ui.groupBoxGL_scan.setEnabled(True)
            self.ui.radioButtonGL_stepscan.setEnabled(True)
    
    def Close_visa(self, gateLead, visa_chosen, lineEditVisa, selectClose):
        self.ui.labelGL_condition.setText('Visa address is closed')
        lineEditVisa.setText('')
        selectClose[0].setEnabled(True)
        selectClose[1].setEnabled(False)
        if gateLead == "gate1":
            visa_chosen.close()
            self.gate1_visa_ok = False
            self.gate1_visa = None
            self.Disable(gateLead)
            self.ui.labelGL_timestep.setEnabled(False)
            self.ui.lineEditGL_tstep.setEnabled(False)
        elif gateLead == "gate2":
            self.gate2_visa_ok = False
            visa_chosen.close()
            self.gate2_visa = None
            self.Disable(gateLead)
            self.ui.labelGL_timestep.setEnabled(False)
            self.ui.lineEditGL_tstep.setEnabled(False)
        elif gateLead == "agilent":
            self.a_visa_ok = False
            self.agelient_visa = None
            
    def Check_visa(self, inst):
        try:
            inst.ask("*IDN?")
            valid = True
        except:
            valid = False
        return valid
    
    def Enable(self, gateLead):
        if gateLead == 'gate1':
            self.ui.groupBoxGL_units_gate1.setEnabled(True)
        elif gateLead == 'gate2':
            self.ui.groupBoxGL_units_gate2.setEnabled(True)
            
    def Disable(self, gateLead):
        if gateLead == 'gate1':
            self.ui.groupBoxGL_units_gate1.setEnabled(False)
        elif gateLead == 'gate2':
            self.ui.groupBoxGL_units_gate2.setEnabled(False)
            
    def start(self):
        self.dsave_filename = ''
        self.dsave_username = ''
        self.dsave_filetype = ''
        self.dsave_divide = ''
        instruments = [self.gate1_visa, self.gate2_visa, self.agelient_visa]
        curves = [self.curve_itemGL_gate1_voltage, self.curve_itemGL_gate1_current, self.curve_itemGL_gate2_voltage, self.curve_itemGL_gate2_current, self.curve_itemGL_agilent_voltage, self.curve_itemGL_lockin_voltage, self.curve_itemGL_lockin_gate1, self.curve_itemGL_lockin_gate2]
        curveWidgets =[self.ui.curvewidgetGL_gate1_voltage, self.ui.curvewidgetGL_gate1_current, self.ui.curvewidgetGL_gate2_voltage, self.ui.curvewidgetGL_gate2_current, self.ui.curvewidgetGL_agilent_voltage, self.ui.curvewidgetGL_lockin_voltage, self.ui.curvewidgetGL_lockin_gate1, self.ui.curvewidgetGL_lockin_gate2]
        dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
        go_on = None
        if self.ui.checkBoxGL_dsave.isChecked():
            self.Dsave_directory()
            if self.dsave_dir_ok:
                self.Dsave_filename()
                if self.dsave_filename_ok:    
                    self.Dsave_username()
                    if self.dsave_username_ok:
                        self.Dsave_filetype()
                        dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
                        self.collect_data_thread.input(instruments, self.ui, self.Array1, self.Array2, go_on , curves, curveWidgets, dsave)
                        self.ui.tabWidgetGL.setCurrentIndex(2)
                        self.ui.pushButtonGL_Start.setEnabled(False)
                        self.ui.pushButtonGL_Pause.setEnabled(True)
                        self.ui.pushButtonGL_Stop.setEnabled(True)
                        self.ui.groupBoxGL_parameters.setEnabled(True)
                        self.ui.labelGL_condition.setText('Running...')
                    else:
                        self.ui.labelGL_condition.setText('Enter user name for dynamic saving.')
                else:
                    self.ui.labelGL_condition.setText('Enter file name for dynamic saving.')
            else:
                self.ui.labelGL_condition.setText('Choose valid directory for dynamic saving.')
        else:
            self.collect_data_thread.input(instruments, self.ui, self.Array1, self.Array2, go_on , curves, curveWidgets, dsave)
            self.ui.tabWidgetGL.setCurrentIndex(2)
            self.ui.pushButtonGL_Start.setEnabled(False)
            self.ui.pushButtonGL_Pause.setEnabled(True)
            self.ui.pushButtonGL_Stop.setEnabled(True)
            self.ui.groupBoxGL_parameters.setEnabled(True)
            self.ui.labelGL_condition.setText('Running...')
    
    def curvePlots_update(self, curveInfo):
        curveWidget = curveInfo[0]
        curve = curveInfo[1]
        curveWidget.plot.do_autoscale()
        curve.plot().replot()
    
    def mplPlots(self):
        self.ui.tabWidgetGL.setCurrentIndex(3)
        self.ui.mplwidgetGL_gate1_voltage.draw()
        self.ui.mplwidgetGL_gate1_current.draw()
        self.ui.mplwidgetGL_gate2_voltage.draw()
        self.ui.mplwidgetGL_gate2_current.draw()
        self.ui.mplwidgetGL_agilent_voltage.draw()
        self.ui.mplwidgetGL_lockin_voltage.draw()
        self.ui.mplwidgetGL_lockin_gate1.draw()
        self.ui.mplwidgetGL_lockin_gate2.draw()
        
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
            self.ui.lineEditGL_GoogleDrive_G.setText(file_dir)
            self.ui.labelGL_condition_G.setText('Open Google Drive User Folder')
            self.ui.pushButtonGL_check_G.setEnabled(True)
    
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
            self.ui.lineEditGL_directory_O.setText(fileDir)
            self.ui.labelGL_username_O.setEnabled(True)
            self.ui.comboBoxGL_Name_Folder_O.setEnabled(True)
            self.ui.groupBoxGL_Filename_O.setEnabled(True)
            self.ui.groupBoxGL_File_Type_O.setEnabled(True)
            self.ui.labelGL_comment_O.setEnabled(True)
            self.ui.textEditGL_comment_O.setEnabled(True)
            self.ui.pushButtonGL_Save_O.setEnabled(True)
            self.ui.lineEditGL_Custom_Name_O.setEnabled(True)
            self.ui.labelGL_condition_O.setText("Click save button to save.")
        else:
            self.ui.lineEditGL_directory_O.setText('None')
            self.ui.labelGL_condition_O.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEditGL_GoogleDrive_G.text()).split('\\')
        if os.path.exists(self.ui.lineEditGL_GoogleDrive_G.text()) == False:
            self.ui.labelGL_condition_G.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.labelGL_condition_G.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.labelGL_namefolder_G.setEnabled(True)
                    self.ui.comboBoxGL_Name_Folder_G.setEnabled(True)
                    self.ui.pushButtonGL_Select_Directory_G.setEnabled(True)
                    self.ui.labelGL_condition_G.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBoxGL_Name_Folder_G.currentText())
        if namefolder == 'None':
            self.ui.labelGL_condition_G.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.labelGL_G.setText("Save to \\" + namefolder + "\Date" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Keithely with Array'
            self.ui.groupBoxGL_File_Type_G.setEnabled(True)
            self.ui.groupBoxGL_Filename_G.setEnabled(True)
            self.ui.labelGL_comment_G.setEnabled(True)
            self.ui.textEditGL_comment_G.setEnabled(True)
            self.ui.pushButtonGL_Save_G.setEnabled(True)
            self.ui.lineEditGL_Custom_Name_G.setEnabled(True)
            self.ui.labelGL_condition_G.setText('Click save button to save.')
            
    def Select_type_G(self):
        if self.ui.radioButtonGL_csv_G.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButtonGL_txt_G.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

            
    def Select_type_O(self):
        if self.ui.radioButtonGL_csv_O.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButtonGL_txt_O.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'


    def Select_name_G(self):
        if self.ui.radioButtonGL_Timename_G.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButtonGL_Custom_Name_G.isChecked():
            self.G_file_name = str(self.ui.lineEditGL_Custom_Name_G.text())
            
    def Select_name_O(self):
        if self.ui.radioButtonGL_Timename_O.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButtonGL_Custom_Name_O.isChecked():
            self.O_file_name = str(self.ui.lineEditGL_Custom_Name_O.text())
    
    def Pre_dsave(self):
        if self.ui.checkBoxGL_dsave.isChecked():
            self.ui.labelGL_dsave_directory.setEnabled(True)
            self.ui.lineEditGL_dsave_directory.setEnabled(True)
            self.ui.pushButtonGL_dsave_browse.setEnabled(True)
            self.ui.groupBoxGL_dsave_filename.setEnabled(True)
            self.ui.radioButtonGL_dsave_timename.setEnabled(True)
            self.ui.radioButtonGL_dsave_custname.setEnabled(True)
            self.ui.lineEditGL_dsave_custname.setEnabled(True)
            self.ui.groupBoxGL_dsave_filetype.setEnabled(True)
            self.ui.radioButtonGL_csv.setEnabled(True)
            self.ui.radioButtonGL_txt.setEnabled(True)
            self.ui.labelGL_dsave_username.setEnabled(True)
            self.ui.lineEditGL_dsave_username.setEnabled(True)
            self.ui.labelGL_dsave_comment.setEnabled(True)
            self.ui.textEditGL_dsave_comment.setEnabled(True)
            self.ui.labelGL_condition.setText("Dynamic saving opened.")
        else:
            self.ui.labelGL_dsave_directory.setEnabled(False)
            self.ui.lineEditGL_dsave_directory.setEnabled(False)
            self.ui.pushButtonGL_dsave_browse.setEnabled(False)
            self.ui.groupBoxGL_dsave_filename.setEnabled(False)
            self.ui.radioButtonGL_dsave_timename.setEnabled(False)
            self.ui.radioButtonGL_dsave_custname.setEnabled(False)
            self.ui.lineEditGL_dsave_custname.setEnabled(False)
            self.ui.groupBoxGL_dsave_filetype.setEnabled(False)
            self.ui.radioButtonGL_csv.setEnabled(False)
            self.ui.radioButtonGL_txt.setEnabled(False)
            self.ui.labelGL_dsave_username.setEnabled(False)
            self.ui.lineEditGL_dsave_username.setEnabled(False)
            self.ui.labelGL_dsave_comment.setEnabled(False)
            self.ui.textEditGL_dsave_comment.setEnabled(False)
            self.ui.labelGL_condition.setText("Dynamic saving closed.")
    
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
            self.ui.lineEditGL_dsave_directory.setText(fileDir)
            self.ui.labelGL_condition.setText("Dynamic saving directory selected.")
        else:
            self.ui.lineEditGL_dsave_directory.setText('None')
            self.ui.labelGL_condition.setText('Choose a directory for dynamic saving.')
            
    def Dsave_directory(self):
        self.dsave_dir_ok = True
        if self.ui.lineEditGL_dsave_directory.text() == '' or self.ui.lineEditGL_dsave_directory.text() == 'None':
            self.dsave_dir_ok = False
        
    def Dsave_filename(self):
        self.dsave_filename_ok = True
        self.dsave_filename = ''
        if self.ui.radioButtonGL_dsave_timename.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = 'DSave' + ' ' + date + ' ' + current_time
            self.dsave_filename = str(date_and_time)
        elif self.ui.radioButtonGL_dsave_custname.isChecked():
            self.dsave_filename = str(self.ui.lineEditGL_dsave_custname.text())
            if self.dsave_filename == '':
                self.dsave_filename_ok = False
    
    def Dsave_filetype(self):
        if self.ui.radioButtonGL_csv.isChecked():
            self.dsave_filetype = '.csv'
            self.dsave_divide = ','
        elif self.ui.radioButtonGL_txt.isChecked():
            self.dsave_filetype = '.txt'
            self.dsave_divide = '\t'
            
    def Dsave_username(self):
        self.dsave_username_ok = True
        self.dsave_username = ''
        self.dsave_username = str(self.ui.lineEditGL_dsave_username.text())
        if self.dsave_username == '':
            self.dsave_username_ok = False
    
    def Pre_save(self, date_value, t_value, stepData, Array1, Array2, gate1Volt_data, gate1Curr_data, gate2Volt_data, gate2Curr_data, agilentVolt_data, lockinVolt_data, sens_scale):
        self.date_value = date_value
        self.t_value = t_value
        self.stepData = stepData
        self.Array1 = Array1
        self.Array2 = Array2
        self.gate1Volt_data = gate1Volt_data
        self.gate1Curr_data = gate1Curr_data
        self.gate2Volt_data = gate2Volt_data
        self.gate2Curr_data = gate2Curr_data
        self.agilentVolt_data = agilentVolt_data
        self.lockinVolt_data = lockinVolt_data
        self.sens_scale = sens_scale
        
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
            
            # User name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.uiSavingGDcomboBox[0].currentText()))
            comments.append(temp)
            # Edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Array1 source
            temp = []
            temp.append('Array1 Source:')
            temp.append(str(self.ui.lineEditGL_array1.text()))
            comments.append(temp)
            # Gate1 visa address
            temp = []
            temp.append('Gate1 Visa Address:')
            temp.append(str(self.ui.comboBoxGL_gate1.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate1 Visa Name:')
            name = str(self.ui.labelGL_visaname_gate1.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Array2 source
            temp = []
            temp.append('Array2 Source:')
            temp.append(str(self.ui.lineEditGL_array2.text()))
            comments.append(temp)
            # Gate2 visa address
            temp = []
            temp.append('Gate2 Visa Address:')
            temp.append(str(self.ui.comboBoxGL_gate2.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate2 Visa Name:')
            name = str(self.ui.labelGL_visaname_gate2.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Agilent visa address
            temp = []
            temp.append('Agilent Address:')
            temp.append(str(self.ui.comboBoxGL_a_visa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Agilent Visa Name:')
            name = str(self.ui.labelGL_a_visaname.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Gate1 Y-Values Units
            temp = []
            temp.append('Gate1 Y-Values Units:')
            if self.ui.radioButtonGL_Volts_gate1.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonGL_mVolts_gate1.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonGL_uVolts_gate1.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonGL_nVolts_gate1.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate1 Lead Output
            temp = []
            temp.append('Gate1 Lead Output:')
            temp.append('2-Terminal')
            comments.append(temp)
            
            # Gate2 Y-Values Units
            temp = []
            temp.append('Gate2 Y-Values Units:')
            if self.ui.radioButtonGL_Volts_gate2.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonGL_mVolts_gate2.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonGL_uVolts_gate2.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonGL_nVolts_gate2.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate2 Lead Output
            temp = []
            temp.append('Gate2 Lead Output:')
            temp.append('2-Terminal')
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditGL_tstep.text()))
            comments.append(temp)
            # Comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditGL_comment_G.toPlainText()))
            comments.append(temp)
            # New line
            temp = []
            temp.append('')
            comments.append(temp)
            # Lock-in Parameters
            temp = []
            temp.append('Lock-in Parameters')
            comments.append(temp)
            temp = []
            temp.append('Lock-in Sensitivity:')
            temp.append(str(sens_scale[0]))
            temp.append(str(sens_scale[1]))
            comments.append(temp)
            temp = []
            temp.append('Signal Input:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Input:')
            temp.append(self.ui.comboBoxGL_input.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Couple:')
            temp.append(self.ui.comboBoxGL_couple.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Ground:')
            temp.append(self.ui.comboBoxGL_ground.currentText())
            comments.append(temp)
            temp = []
            temp.append('Input Filter:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Q-factor:')
            temp.append(self.ui.comboBoxGL_Q.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Trim Frequency:')
            temp.append(self.ui.lineEditGL_TF.text())
            temp.append(self.ui.comboBoxGL_TF_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Fliter Type:')
            temp.append(self.ui.comboBoxGL_FT.currentText())
            comments.append(temp)
            temp = []
            temp.append('Reverse:')
            temp.append(self.ui.comboBoxGL_reverse.currentText())
            comments.append(temp)
            temp = []
            temp.append('Slope:')
            temp.append(self.ui.comboBoxGL_slope.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Constant:')
            temp.append(self.ui.comboBoxGL_TC.currentText())
            temp.append(self.ui.comboBoxGL_TC_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Output Mode:')
            temp.append(self.ui.comboBoxGL_output_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Phase:')
            temp.append(self.ui.lineEditGL_phase.text())
            temp.append('degree')
            comments.append(temp)
            temp = []
            temp.append('Frequency:')
            temp.append(self.ui.lineEditGL_freq.text())
            temp.append(self.ui.comboBoxGL_freq_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Amplitude:')
            temp.append(self.ui.lineEditGL_amp.text())
            temp.append(self.ui.comboBoxGL_amp_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Quadrant:')
            temp.append(self.ui.comboBoxGL_quadrant.currentText())
            comments.append(temp)
            temp = []
            temp.append('Mode:')
            temp.append(self.ui.comboBoxGL_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Range:')
            temp.append(self.ui.comboBoxGL_range.currentText())
            temp.append('Hz')
            comments.append(temp)
            temp = []
            temp.append('Ref. Out:')
            temp.append(self.ui.comboBoxGL_refout.currentText())
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
            parameters.append('Array1 Value')
            units.append('1')
            data.append(self.Array1)
            parameters.append('Gate1 Voltage')
            units.append('Volts')
            data.append(self.gate1Volt_data)
            parameters.append('Gate1 Current')
            units.append('Amps')
            data.append(self.gate1Curr_data)
            parameters.append('Array2 Value')
            units.append('1')
            data.append(self.Array2)
            parameters.append('Gate2 Voltage')
            units.append('Volts')
            data.append(self.gate2Volt_data)
            parameters.append('Gate2 Current')
            units.append('Amps')
            data.append(self.gate2Curr_data)
            parameters.append('Agilent Voltage')
            units.append('Volts')
            data.append(self.agilentVolt_data)
            parameters.append('Lock-in Voltage')
            units.append('Volts')
            data.append(self.lockinVolt_data)
            
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
            
            self.save_thread.input(comments, parameters, units, data, file_info)
            self.ui.pushButtonGL_Open_G.setEnabled(True)
            self.ui.labelGL_condition_G.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBoxGL_Name_Folder_O.currentText() == 'None':
            self.ui.labelGL_condition_O.setText('Pleanse choose a user name.')
        elif self.ui.radioButtonGL_Custom_Name_O.isChecked() and self.ui.lineEdit_Custom_Name_O.text() == '':
            self.ui.labelGL_condition_O.setText('Please enter a file name.')
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
            
            # User name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.uiSavingGDcomboBox[0].currentText()))
            comments.append(temp)
            # Edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Array1 source
            temp = []
            temp.append('Array1 Source:')
            temp.append(str(self.ui.lineEditGL_array1.text()))
            comments.append(temp)
            # Gate1 visa address
            temp = []
            temp.append('Gate1 Visa Address:')
            temp.append(str(self.ui.comboBoxGL_gate1.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate1 Visa Name:')
            name = str(self.ui.labelGL_visaname_gate1.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Array2 source
            temp = []
            temp.append('Array2 Source:')
            temp.append(str(self.ui.lineEditGL_array2.text()))
            comments.append(temp)
            # Gate2 visa address
            temp = []
            temp.append('Gate2 Visa Address:')
            temp.append(str(self.ui.comboBoxGL_gate2.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate2 Visa Name:')
            name = str(self.ui.labelGL_visaname_gate2.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Agilent visa address
            temp = []
            temp.append('Agilent Address:')
            temp.append(str(self.ui.comboBoxGL_a_visa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Agilent Visa Name:')
            name = str(self.ui.labelGL_a_visaname.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Gate1 Y-Values Units
            temp = []
            temp.append('Gate1 Y-Values Units:')
            if self.ui.radioButtonGL_Volts_gate1.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonGL_mVolts_gate1.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonGL_uVolts_gate1.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonGL_nVolts_gate1.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate1 Lead Output
            temp = []
            temp.append('Gate1 Lead Output:')
            if self.ui.radioButtonGL_Lead4_gate1.isChecked():
                temp.append('4-Terminal')
            elif self.ui.radioButtonGL_Lead2_gate1.isChecked():
                temp.append('2-Terminal')
            comments.append(temp)
            
            # Gate2 Y-Values Units
            temp = []
            temp.append('Gate2 Y-Values Units:')
            if self.ui.radioButtonGL_Volts_gate2.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonGL_mVolts_gate2.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonGL_uVolts_gate2.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonGL_nVolts_gate2.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate2 Lead Output
            temp = []
            temp.append('Gate2 Lead Output:')
            temp.append('2-Terminal')
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditGL_tstep.text()))
            comments.append(temp)
            # Comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditGL_comment_G.toPlainText()))
            comments.append(temp)
            # New line
            temp = []
            temp.append('')
            comments.append(temp)
            # Lock-in Parameters
            temp = []
            temp.append('Lock-in Parameters')
            comments.append(temp)
            temp = []
            temp.append('Lock-in Sensitivity:')
            temp.append(str(sens_scale[0]))
            temp.append(str(sens_scale[1]))
            comments.append(temp)
            temp = []
            temp.append('Signal Input:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Input:')
            temp.append(self.ui.comboBoxGL_input.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Couple:')
            temp.append(self.ui.comboBoxGL_couple.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Ground:')
            temp.append(self.ui.comboBoxGL_ground.currentText())
            comments.append(temp)
            temp = []
            temp.append('Input Filter:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Q-factor:')
            temp.append(self.ui.comboBoxGL_Q.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Trim Frequency:')
            temp.append(self.ui.lineEditGL_TF.text())
            temp.append(self.ui.comboBoxGL_TF_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Fliter Type:')
            temp.append(self.ui.comboBoxGL_FT.currentText())
            comments.append(temp)
            temp = []
            temp.append('Reverse:')
            temp.append(self.ui.comboBoxGL_reverse.currentText())
            comments.append(temp)
            temp = []
            temp.append('Slope:')
            temp.append(self.ui.comboBoxGL_slope.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Constant:')
            temp.append(self.ui.comboBoxGL_TC.currentText())
            temp.append(self.ui.comboBoxGL_TC_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Output Mode:')
            temp.append(self.ui.comboBoxGL_output_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Phase:')
            temp.append(self.ui.lineEditGL_phase.text())
            temp.append('degree')
            comments.append(temp)
            temp = []
            temp.append('Frequency:')
            temp.append(self.ui.lineEditGL_freq.text())
            temp.append(self.ui.comboBoxGL_freq_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Amplitude:')
            temp.append(self.ui.lineEditGL_amp.text())
            temp.append(self.ui.comboBoxGL_amp_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Quadrant:')
            temp.append(self.ui.comboBoxGL_quadrant.currentText())
            comments.append(temp)
            temp = []
            temp.append('Mode:')
            temp.append(self.ui.comboBoxGL_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Range:')
            temp.append(self.ui.comboBoxGL_range.currentText())
            temp.append('Hz')
            comments.append(temp)
            temp = []
            temp.append('Ref. Out:')
            temp.append(self.ui.comboBoxGL_refout.currentText())
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
            parameters.append('Array1 Value')
            units.append('1')
            data.append(self.Array1)
            parameters.append('Gate1 Voltage')
            units.append('Volts')
            data.append(self.gate1Volt_data)
            parameters.append('Gate1 Current')
            units.append('Amps')
            data.append(self.gate1Curr_data)
            parameters.append('Array2 Value')
            units.append('1')
            data.append(self.Array2)
            parameters.append('Gate2 Voltage')
            units.append('Volts')
            data.append(self.gate2Volt_data)
            parameters.append('Gate2 Current')
            units.append('Amps')
            data.append(self.gate2Curr_data)
            parameters.append('Agilent Voltage')
            units.append('Volts')
            data.append(self.agilentVolt_data)
            parameters.append('Lock-in Voltage')
            units.append('Volts')
            data.append(self.lockinVolt_data)
            
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
            self.ui.pushButtonGL_Open_O.setEnabled(True)
            self.ui.labelGL_condition_O.setText('File has been saved.')
    
    def G_open(self):
        opendir = self.G_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
    def O_open(self):
        opendir = self.O_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)

    def Confirm(self):
        
        self.ui.GL_mV.setStyleSheet('color: black')
        self.ui.GL_uV.setStyleSheet('color: black')
        self.ui.GL_nV.setStyleSheet('color: black')
        self.sens_labels[self.blue].setStyleSheet('color: black')
        self.blue = self.ui.dialSensGL_lockin1.value()
        if self.blue >= 0 and self.blue <= 2:
            self.ui.GL_nV.setStyleSheet('color: blue')
        elif self.blue >= 3 and self.blue <= 11:
            self.ui.GL_uV.setStyleSheet('color: blue')
        elif self.blue >= 12:
            self.ui.GL_mV.setStyleSheet('color: blue')
        self.sens_labels[self.blue].setStyleSheet('color: blue')
        
        if self.confirm_num == 0:
            self.lockin_ok = True
            self.ui.groupBoxGL_SI.setEnabled(True)
            self.ui.groupBoxGL_IF.setEnabled(True)
            self.ui.labelGL_Reverse.setEnabled(True)
            self.ui.comboBoxGL_reverse.setEnabled(True)
            self.ui.labelGL_Slope.setEnabled(True)
            self.ui.comboBoxGL_slope.setEnabled(True)
            self.ui.labelGL_TC.setEnabled(True)
            self.ui.comboBoxGL_TC.setEnabled(True)
            self.ui.comboBoxGL_TC_unit.setEnabled(True)
            self.ui.groupBoxGL_output.setEnabled(True)
            self.ui.labelGL_phase.setEnabled(True)
            self.ui.lineEditGL_phase.setEnabled(True)
            self.ui.labelGL_freq.setEnabled(True)
            self.ui.lineEditGL_freq.setEnabled(True)
            self.ui.comboBoxGL_freq_unit.setEnabled(True)
            self.ui.labelGL_amp.setEnabled(True)
            self.ui.lineEditGL_amp.setEnabled(True)
            self.ui.comboBoxGL_amp_unit.setEnabled(True)
            self.ui.comboBoxGL_quadrant.setEnabled(True)
            self.ui.labelGL_mode.setEnabled(True)
            self.ui.comboBoxGL_mode.setEnabled(True)
            self.ui.labelGL_range.setEnabled(True)
            self.ui.comboBoxGL_range.setEnabled(True)
            self.ui.labelGL_refout.setEnabled(True)
            self.ui.comboBoxGL_refout.setEnabled(True)
            self.confirm_num += 1
            
        self.ui.labelGL_condition.setText('Lock-in sensitivity selected.')
        
class Collect_data(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def input(self, instruments, ui, Array1, Array2, go_on, curves, curveWidgets, dsave):
        self.gate1 = instruments[0]
        self.gate2 = instruments[1]
        self.agilent = instruments[2]
        self.ui = ui
        self.Array1 = np.array(Array1)
        self.Array2 = np.array(Array2)
        self.go_on = go_on
        self.curves = curves
        self.curveWidgets = curveWidgets
        self.dsave_directory = dsave[0]
        self.dsave_filename = dsave[1]
        self.dsave_username = dsave[2]
        self.dsave_thread = dsave[3]
        self.dsave_filetype = dsave[4]
        self.dsave_divide = dsave[5]
        
        if self.ui.radioButtonGL_Volts_gate1.isChecked():
            self.gate1_voltage_scale = [1, 'Volts']
        elif self.ui.radioButtonGL_mVolts_gate1.isChecked():
            self.gate1_voltage_scale = [1E-3, 'mVolts']
        elif self.ui.radioButtonGL_uVolts_gate1.isChecked():
            self.gate1_voltage_scale = [1E-6, 'uVolts']
        elif self.ui.radioButtonGL_nVolts_gate1.isChecked():
            self.gate1_voltage_scale = [1E-9, 'nVolts']
        self.gate1_current_scale = [1, 'Amps']
        self.Array1 = self.Array1 * self.gate1_voltage_scale[0]
        
        if self.ui.radioButtonGL_Volts_gate2.isChecked():
            self.gate2_voltage_scale = [1, 'Volts']
        elif self.ui.radioButtonGL_mVolts_gate2.isChecked():
            self.gate2_voltage_scale = [1E-3, 'mVolts']
        elif self.ui.radioButtonGL_uVolts_gate2.isChecked():
            self.gate2_voltage_scale = [1E-6, 'uVolts']
        elif self.ui.radioButtonGL_nVolts_gate2.isChecked():
            self.gate2_voltage_scale = [1E-9, 'nVolts']
        self.gate2_current_scale = [1, 'Amps']
        self.Array2 = self.Array2 * self.gate2_voltage_scale[0]
        
        self.sens_list = [100, 200, 500, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1, 2, 5, 10, 20, 50, 100, 200, 500]
        self.sens_scale = []
        
        self.sens_scale.append(self.sens_list[self.ui.dialSensGL_lockin1.value()])
        
        if self.ui.dialSensGL_lockin1.value() >= 0 and self.ui.dialSensGL_lockin1.value() <= 2:
            self.sens_scale.append(1E-9)
        elif self.ui.dialSensGL_lockin1.value() >= 3 and self.ui.dialSensGL_lockin1.value() <= 11:
            self.sens_scale.append(1E-6)
        elif self.ui.dialSensGL_lockin1.value() >= 12:
            self.sens_scale.append(1E-3)
            
        self.stop_collecting = False
        self.pause_collecting = False
        self.time_step = float(self.ui.lineEditGL_tstep.text())
        
        self.start()
    
    def stop(self):
        self.stop_collecting = True
        self.ui.labelGL_condition.setText('Stopped.')
        self.ui.pushButtonGL_Start.setEnabled(True)
        self.ui.pushButtonGL_Pause.setEnabled(False)
        self.ui.pushButtonGL_Stop.setEnabled(False)
    
    def pause(self):
        if self.pause_collecting:
            self.ui.labelGL_condition.setText('Running...')
            self.ui.pushButtonGL_Pause.setText("Pause")
            self.pause_collecting = False
        else:
            self.ui.labelGL_condition.setText('Paused. Click continue to run.')
            self.ui.pushButtonGL_Pause.setText("Continue")
            self.pause_collecting = True
    
    def run(self):
        import time
        g1v = []
        g1c = []
        g2v = []
        g2c = []
        av = []
        lv = []
        t = []
        self.gate1Volt_data = np.array([])
        self.gate1Curr_data = np.array([])
        self.gate2Volt_data = np.array([])
        self.gate2Curr_data = np.array([])
        self.agilentVolt_data = np.array([])
        self.lockinVolt_data = np.array([])
        self.stepData = []
        self.t_value = np.array([])
        date_value = []
        
        self.turn_on_gate1_voltage()
        self.turn_on_gate2_voltage()
        
        self.agilent_Vdata = self.agilent.ask('MEAS:VOLT?')
        
        start_time = time.time()
        t1_ = 0
        
        for i in range(0, len(self.Array1)):
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
                        self.set_gate1_voltage(self.Array1[i])
                        self.set_gate2_voltage(self.Array2[i])
                        self.read_data_write()
                        data = self.read_data_read()
                        self.gate1_Vdata = float(data[0])
                        self.gate1_Cdata = float(data[1])
                        g1v.append(self.gate1_Vdata)
                        g1c.append(self.gate1_Cdata)
                        self.gate1Volt_data = np.array(g1v)
                        self.gate1Curr_data = np.array(g1c)
                        self.gate2_Vdata = float(data[2])
                        self.gate2_Cdata = float(data[3])
                        g2v.append(self.gate2_Vdata)
                        g2c.append(self.gate2_Cdata)
                        self.gate2Volt_data = np.array(g2v)
                        self.gate2Curr_data = np.array(g2c)
                        self.agilent_Vdata = float(data[4])
                        av.append(self.agilent_Vdata)
                        self.agilentVolt_data = np.array(av)
                        self.lockin_Vdata = self.agilent_Vdata * self.sens_scale[0] * self.sens_scale[1] / 10
                        lv.append(self.lockin_Vdata)
                        self.lockinVolt_data = np.array(lv)
                        
                        end_time = time.time()
                        self.during = end_time - start_time
                        t.append(self.during)
                        self.t_value = np.array(t)
                        self.t_plot_scale()
                        if self.ui.radioButtonGL_stepscan.isChecked():
                            self.xlabel = "Steps"
                            self.xdata = self.stepData
                        elif self.ui.radioButtonGL_timescan.isChecked():
                            self.xlabel = 'Time (' + self.time_scale[1] + ')'
                            self.xdata = self.t_value / self.time_scale[0]
                        self.data1 = self.Switch_scale(abs(max(self.gate1Volt_data)))
                        self.setup_plot(self.curveWidgets[0], self.curves[0], [self.xdata, self.gate1Volt_data * self.data1[0]], ["Gate1 Voltage", self.xlabel, "Gate1 Voltage (" + self.data1[1] + "V)"])
                        self.data2 = self.Switch_scale(abs(max(self.gate1Curr_data)))
                        self.setup_plot(self.curveWidgets[1], self.curves[1], [self.xdata, self.gate1Curr_data * self.data2[0]], ["Gate1 Current", self.xlabel, "Gate1 Current (" + self.data2[1] + "A)"])
                        self.data3 = self.Switch_scale(abs(max(self.gate2Volt_data)))
                        self.setup_plot(self.curveWidgets[2], self.curves[2], [self.xdata, self.gate2Volt_data * self.data3[0]], ["Gate2 Voltage", self.xlabel, "Gate2 Voltage (" + self.data3[1] + "V)"])
                        self.data4 = self.Switch_scale(abs(max(self.gate2Curr_data)))
                        self.setup_plot(self.curveWidgets[3], self.curves[3], [self.xdata, self.gate2Curr_data * self.data4[0]], ["Gate2 Current", self.xlabel, "Gate2 Current (" + self.data4[1] + "A)"])
                        self.data5 = self.Switch_scale(abs(max(self.agilentVolt_data)))
                        self.setup_plot(self.curveWidgets[4], self.curves[4], [self.xdata, self.agilentVolt_data * self.data5[0]], ["Agilent Voltage", self.xlabel, "Agilent Voltage (" + self.data5[1] + "V)"])
                        self.data6 = self.Switch_scale(abs(max(self.lockinVolt_data)))
                        self.setup_plot(self.curveWidgets[5], self.curves[5], [self.xdata, self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage", self.xlabel, "Lock-in Voltage (" + self.data6[1] + "V)"])
                        self.setup_plot(self.curveWidgets[6], self.curves[6], [self.gate1Volt_data * self.data1[0], self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage vs Gate1 Voltage", "Gate1 Voltage (" + self.data1[1] + "V)", "Lock-in Voltage (" + self.data6[1] + "V)"])
                        self.setup_plot(self.curveWidgets[7], self.curves[7], [self.gate2Volt_data * self.data3[0], self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage vs Gate2 Voltage", "Gate2 Voltage (" + self.data3[1] + "V)", "Lock-in Voltage (" + self.data6[1] + "V)"])
                        
                        self.emit(SIGNAL("print"), i, self.during, self.gate1_Vdata, self.gate1_Cdata, self.gate2_Vdata, self.gate2_Cdata, self.agilent_Vdata, self.lockin_Vdata, self.sens_scale)
                        
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
                    
        self.Pre_dynamic_save(len(self.Array1), True)
        self.turn_off_gate1_voltage()
        self.turn_off_gate2_voltage()
        self.ui.pushButtonGL_Start.setEnabled(True)
        self.ui.pushButtonGL_Pause.setEnabled(False)
        self.ui.pushButtonGL_Stop.setEnabled(False)
        self.ui.tabWidgetGL_save.setEnabled(True)
        self.ui.labelGL_condition.setText('Scan completed.')
        self.emit(SIGNAL("data_available"), date_value, self.t_value, self.stepData, self.Array1, self.Array2, self.gate1Volt_data, self.gate1Curr_data, self.gate2Volt_data, self.gate2Curr_data, self.agilentVolt_data, self.lockinVolt_data, self.sens_scale)
        self.MPL_Plot()
    
    def Pre_dynamic_save(self, num, is_last):
        if self.ui.checkBoxGL_dsave.isChecked():
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
                data.append(self.Array1[num])
                data.append(self.gate1_Vdata)
                data.append(self.gate1_Cdata)
                data.append(self.Array2[num])
                data.append(self.gate2_Vdata)
                data.append(self.gate2_Cdata)
                data.append(self.agilent_Vdata)
                data.append(self.lockin_Vdata)
                
                if num == 0:
                    is_first = True
                    
                    # User name
                    temp = []
                    temp.append('User Name:')
                    temp.append(self.dsave_username)
                    comments.append(temp)
                    # Edit Time
                    temp = []
                    temp.append('Edit Time:')
                    temp.append(str(datetime.datetime.now()))
                    comments.append(temp)
                    # Array1 source
                    temp = []
                    temp.append('Array1 Source:')
                    temp.append(str(self.ui.lineEditGL_array1.text()))
                    comments.append(temp)
                    # Gate1 visa address
                    temp = []
                    temp.append('Gate1 Visa Address:')
                    temp.append(str(self.ui.comboBoxGL_gate1.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Gate1 Visa Name:')
                    name = str(self.ui.labelGL_visaname_gate1.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Array2 source
                    temp = []
                    temp.append('Array2 Source:')
                    temp.append(str(self.ui.lineEditGL_array2.text()))
                    comments.append(temp)
                    # Gate2 visa address
                    temp = []
                    temp.append('Gate2 Visa Address:')
                    temp.append(str(self.ui.comboBoxGL_gate2.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Gate2 Visa Name:')
                    name = str(self.ui.labelGL_visaname_gate2.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Agilent visa address
                    temp = []
                    temp.append('Agilent Address:')
                    temp.append(str(self.ui.comboBoxGL_a_visa.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Agilent Visa Name:')
                    name = str(self.ui.labelGL_a_visaname.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Gate1 Y-Values Units
                    temp = []
                    temp.append('Gate1 Y-Values Units:')
                    if self.ui.radioButtonGL_Volts_gate1.isChecked():
                        temp.append('Volts')
                    elif self.ui.radioButtonGL_mVolts_gate1.isChecked():
                        temp.append('mVolts')
                    elif self.ui.radioButtonGL_uVolts_gate1.isChecked():
                        temp.append('uVolts')
                    elif self.ui.radioButtonGL_nVolts_gate1.isChecked():
                        temp.append('nVolts')
                    comments.append(temp)
                    # Gate1 Lead Output
                    temp = []
                    temp.append('Gate1 Lead Output:')
                    temp.append('2-Terminal')
                    comments.append(temp)
                    
                    # Gate2 Y-Values Units
                    temp = []
                    temp.append('Gate2 Y-Values Units:')
                    if self.ui.radioButtonGL_Volts_gate2.isChecked():
                        temp.append('Volts')
                    elif self.ui.radioButtonGL_mVolts_gate2.isChecked():
                        temp.append('mVolts')
                    elif self.ui.radioButtonGL_uVolts_gate2.isChecked():
                        temp.append('uVolts')
                    elif self.ui.radioButtonGL_nVolts_gate2.isChecked():
                        temp.append('nVolts')
                    comments.append(temp)
                    # Gate2 Lead Output
                    temp = []
                    temp.append('Gate2 Lead Output:')
                    temp.append('2-Terminal')
                    comments.append(temp)
                    temp = []
                    temp.append('Time Step(sec):')
                    temp.append(str(self.ui.lineEditGL_tstep.text()))
                    comments.append(temp)
                    # Comments
                    temp = []
                    temp.append('Comments:')
                    temp.append(str(self.ui.textEditGL_dsave_comment.toPlainText()))
                    comments.append(temp)
                    # New line
                    temp = []
                    temp.append('')
                    comments.append(temp)
                    # Lock-in Parameters
                    temp = []
                    temp.append('Lock-in Parameters')
                    comments.append(temp)
                    temp = []
                    temp.append('Lock-in Sensitivity:')
                    temp.append(str(sens_scale[0]))
                    temp.append(str(sens_scale[1]))
                    comments.append(temp)
                    temp = []
                    temp.append('Signal Input:')
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Input:')
                    temp.append(self.ui.comboBoxGL_input.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Couple:')
                    temp.append(self.ui.comboBoxGL_couple.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Ground:')
                    temp.append(self.ui.comboBoxGL_ground.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Input Filter:')
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Q-factor:')
                    temp.append(self.ui.comboBoxGL_Q.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Trim Frequency:')
                    temp.append(self.ui.lineEditGL_TF.text())
                    temp.append(self.ui.comboBoxGL_TF_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Fliter Type:')
                    temp.append(self.ui.comboBoxGL_FT.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Reverse:')
                    temp.append(self.ui.comboBoxGL_reverse.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Slope:')
                    temp.append(self.ui.comboBoxGL_slope.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Time Constant:')
                    temp.append(self.ui.comboBoxGL_TC.currentText())
                    temp.append(self.ui.comboBoxGL_TC_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Output Mode:')
                    temp.append(self.ui.comboBoxGL_output_mode.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Phase:')
                    temp.append(self.ui.lineEditGL_phase.text())
                    temp.append('degree')
                    comments.append(temp)
                    temp = []
                    temp.append('Frequency:')
                    temp.append(self.ui.lineEditGL_freq.text())
                    temp.append(self.ui.comboBoxGL_freq_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Amplitude:')
                    temp.append(self.ui.lineEditGL_amp.text())
                    temp.append(self.ui.comboBoxGL_amp_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Quadrant:')
                    temp.append(self.ui.comboBoxGL_quadrant.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Mode:')
                    temp.append(self.ui.comboBoxGL_mode.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Range:')
                    temp.append(self.ui.comboBoxGL_range.currentText())
                    temp.append('Hz')
                    comments.append(temp)
                    temp = []
                    temp.append('Ref. Out:')
                    temp.append(self.ui.comboBoxGL_refout.currentText())
                    comments.append(temp)

                    #####################
                    parameters.append('Date')
                    units.append('String')
                    parameters.append('Time')
                    units.append('s')
                    parameters.append('Step')
                    units.append('1')
                    parameters.append('Array1 Value')
                    units.append('1')
                    parameters.append('Gate1 Voltage')
                    units.append('Volts')
                    parameters.append('Gate1 Current')
                    units.append('Amps')
                    parameters.append('Array2 Value')
                    units.append('1')
                    parameters.append('Gate2 Voltage')
                    units.append('Volts')
                    parameters.append('Gate2 Current')
                    units.append('Amps')
                    parameters.append('Agilent Voltage')
                    units.append('Volts')
                    parameters.append('Lock-in Voltage')
                    units.append('Volts')
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
                else:
                    self.dsave_thread.input(comments, parameters, units, data, file_info, is_first, is_last)
      
    def MPL_Plot(self):
        if self.ui.radioButtonGL_stepscan.isChecked():
            self.xlabel = "Steps"
            self.xdata = self.stepData
        elif self.ui.radioButtonGL_timescan.isChecked():
            self.xlabel = 'Time (' + self.time_scale[1] + ')'
            self.xdata = self.t_value / self.time_scale[0]
            
        self.Reset_plot_gate1_voltage()
        self.axes_gate1_voltage.grid()
        self.axes_gate1_voltage.set_title("Gate1 Voltage")
        self.axes_gate1_voltage.set_ylabel("Gate1 Voltage (" + self.data1[1] + "V)")
        self.axes_gate1_voltage.set_xlabel(self.xlabel)
        self.axes_gate1_voltage.plot(self.xdata, self.gate1Volt_data * self.data1[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_gate1_current()
        self.axes_gate1_current.grid()
        self.axes_gate1_current.set_title("Gate1 Current")
        self.axes_gate1_current.set_ylabel("Gate1 Current (" + self.data2[1] + "A)")
        self.axes_gate1_current.set_xlabel(self.xlabel)
        self.axes_gate1_current.plot(self.xdata, self.gate1Curr_data * self.data2[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_gate2_voltage()
        self.axes_gate2_voltage.grid()
        self.axes_gate2_voltage.set_title("Gate2 Voltage")
        self.axes_gate2_voltage.set_ylabel("Gate2 Voltage (" + self.data3[1] + "V)")
        self.axes_gate2_voltage.set_xlabel(self.xlabel)
        self.axes_gate2_voltage.plot(self.xdata, self.gate2Volt_data * self.data3[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_gate2_current()
        self.axes_gate2_current.grid()
        self.axes_gate2_current.set_title("Gate2 Current")
        self.axes_gate2_current.set_ylabel("Gate2 Current (" + self.data4[1] + "A)")
        self.axes_gate2_current.set_xlabel(self.xlabel)
        self.axes_gate2_current.plot(self.xdata, self.gate2Curr_data * self.data4[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_agilent_voltage()
        self.axes_agilent_voltage.grid()
        self.axes_agilent_voltage.set_title("Agilent Voltage")
        self.axes_agilent_voltage.set_ylabel("Agilent Voltage (" + self.data5[1] + "V)")
        self.axes_agilent_voltage.set_xlabel(self.xlabel)
        self.axes_agilent_voltage.plot(self.xdata, self.agilentVolt_data * self.data5[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lockin_voltage()
        self.axes_lockin_voltage.grid()
        self.axes_lockin_voltage.set_title("Lock-in Voltage")
        self.axes_lockin_voltage.set_ylabel("Lock-in Voltage (" + self.data6[1] + "V)")
        self.axes_lockin_voltage.set_xlabel(self.xlabel)
        self.axes_lockin_voltage.plot(self.xdata, self.lockinVolt_data * self.data6[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lockin_gate1()
        self.axes_lockin_gate1.grid()
        self.axes_lockin_gate1.set_title("Lock-in Voltage vs Gate1 Voltage")
        self.axes_lockin_gate1.set_ylabel("Lock-in Voltage (" + self.data6[1] + "V)")
        self.axes_lockin_gate1.set_xlabel("Gate1 Voltage (" + self.data1[1] + "V)")
        self.axes_lockin_gate1.plot(self.gate1Volt_data * self.data1[0], self.lockinVolt_data * self.data6[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lockin_gate2()
        self.axes_lockin_gate2.grid()
        self.axes_lockin_gate2.set_title("Lock-in Voltage vs Gate2 Voltage")
        self.axes_lockin_gate2.set_ylabel("Lock-in Voltage (" + self.data6[1] + "V)")
        self.axes_lockin_gate2.set_xlabel("Gate2 Voltage (" + self.data3[1] + "V)")
        self.axes_lockin_gate2.plot(self.gate2Volt_data * self.data3[0], self.lockinVolt_data * self.data6[0], marker = 'o', linestyle = '-')
        
        self.emit(SIGNAL("mpl_plot"))
        
    def Reset_plot_gate1_voltage(self):
        self.ui.mplwidgetGL_gate1_voltage.figure.clear()
        self.axes_gate1_voltage = self.ui.mplwidgetGL_gate1_voltage.figure.add_subplot(111)
        
    def Reset_plot_gate1_current(self):
        self.ui.mplwidgetGL_gate1_current.figure.clear()
        self.axes_gate1_current = self.ui.mplwidgetGL_gate1_current.figure.add_subplot(111)
    
    def Reset_plot_gate2_voltage(self):
        self.ui.mplwidgetGL_gate2_voltage.figure.clear()
        self.axes_gate2_voltage = self.ui.mplwidgetGL_gate2_voltage.figure.add_subplot(111)
        
    def Reset_plot_gate2_current(self):
        self.ui.mplwidgetGL_gate2_current.figure.clear()
        self.axes_gate2_current = self.ui.mplwidgetGL_gate2_current.figure.add_subplot(111)
        
    def Reset_plot_agilent_voltage(self):
        self.ui.mplwidgetGL_agilent_voltage.figure.clear()
        self.axes_agilent_voltage = self.ui.mplwidgetGL_agilent_voltage.figure.add_subplot(111)
        
    def Reset_plot_lockin_voltage(self):
        self.ui.mplwidgetGL_lockin_voltage.figure.clear()
        self.axes_lockin_voltage = self.ui.mplwidgetGL_lockin_voltage.figure.add_subplot(111)
        
    def Reset_plot_lockin_gate1(self):
        self.ui.mplwidgetGL_lockin_gate1.figure.clear()
        self.axes_lockin_gate1 = self.ui.mplwidgetGL_lockin_gate1.figure.add_subplot(111)
        
    def Reset_plot_lockin_gate2(self):
        self.ui.mplwidgetGL_lockin_gate2.figure.clear()
        self.axes_lockin_gate2 = self.ui.mplwidgetGL_lockin_gate2.figure.add_subplot(111)
        
    def setup_plot(self, curveWidget, curve, data, titles):
        curveWidget.plot.set_titles(titles[0], titles[1], titles[2])
        curve.set_data(data[0], data[1])
        self.emit(SIGNAL("curve_plot"), [curveWidget, curve])

    def set_gate1_voltage(self, gate1_voltage):
        self.gate1.write('TRACE:CLEar "defbuffer1"')
        self.gate1.write("ROUT:TERM FRONT")
        self.gate1.write('SENS:FUNC "CURR"')
        #self.gate1.write('SOUR:VOLT:RANG AUTO')
        self.gate1.write("SOUR:FUNC VOLT")
        self.gate1.write("SOUR:VOLT:READ:BACK 1")
        self.gate1.write("SOUR:VOLT " + str(gate1_voltage))
    
    def turn_on_gate1_voltage(self):
        self.gate1.write('SENS:CURR:RSEN ON' )
        self.gate1.write("OUTP ON")
    
    def read_gate1_voltage(self):
        voltage = self.gate1.query('READ? "defbuffer1", SOUR')
        current = self.gate1.query('READ? "defbuffer1", READ')
        return [voltage, current]
    
    def read_data_write(self):
        self.gate1.write('READ? "defbuffer1", SOUR, READ')
        self.gate2.write('READ? "defbuffer1", SOUR, READ')
        self.agilent.write('READ?')
        
    def read_data_read(self):
        voltage1, current1 = self.gate1.read().replace("\n", "").split(",")
        voltage2, current2 = self.gate2.read().replace("\n", "").split(",")
        a_voltage = self.agilent.read()
        return [voltage1, current1, voltage2, current2, a_voltage]
    
    def turn_off_gate1_voltage(self):
        if not self.ui.checkBoxGL_Output_on.isChecked():
            self.gate1.write("OUTP OFF")
    
    ##MEASURE RESISTANCE ON INSTRUMENT 1#####
    ## 4-Terminal Across the Silicon###    
    def set_gate2_voltage(self, gate2_voltage):
        self.gate2.write('TRACE:CLEar "defbuffer1"')
        self.gate2.write("ROUT:TERM FRONT")
        self.gate2.write('SENS:FUNC "CURR"')
        self.gate2.write("SOUR:FUNC VOLT")
        self.gate2.write("SOUR:VOLT:READ:BACK 1")
        self.gate2.write("SOUR:VOLT " + str(gate2_voltage))
    
    def turn_on_gate2_voltage(self):
        self.gate2.write('SENS:CURR:RSEN OFF' ) 
        self.gate2.write("OUTP ON")
        
    def read_gate2_voltage(self):
        voltage = self.gate2.query('READ? "defbuffer1", SOUR')
        current = self.gate2.query('READ? "defbuffer1", READ')
        return [voltage, current]
    
    def turn_off_gate2_voltage(self):
        self.gate2.write("OUTP OFF")
    
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