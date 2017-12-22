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

class Temperature_Scan():
    
    def __init__(self, main, ui):
        self.ui = ui
        self.copyDataFunc = main.CopyDataFunc
        self.collect_data_thread = Collect_data()
        self.save_thread = Save_Thread()
        self.dsave_thread = Dynamic_Save_Thread()
        
        main.connect(self.ui.pushButtonTS_browse_array, SIGNAL('clicked()'), self.Browse_Array)
        main.connect(self.ui.pushButtonTS_import_array, SIGNAL('clicked()'), self.Import_Array)
        main.connect(self.ui.pushButtonTS_copy_array, SIGNAL('clicked()'), self.Copy_Array)
        main.connect(self.ui.pushButtonTS_update_1, SIGNAL('clicked()'), lambda : self.Update_visa("visa1", self.ui.comboBoxTS_visa_1))
        main.connect(self.ui.pushButtonTS_update_2, SIGNAL('clicked()'), lambda : self.Update_visa("visa2", self.ui.comboBoxTS_visa_2))
        main.connect(self.ui.pushButtonTS_select_1, SIGNAL('clicked()'), lambda : self.Select_visa("visa1", self.L_visa, self.ui.comboBoxTS_visa_1, self.ui.labelTS_visa_1, [self.ui.pushButtonTS_select_1, self.ui.pushButtonTS_close_1]))
        main.connect(self.ui.pushButtonTS_select_2, SIGNAL('clicked()'), lambda : self.Select_visa("visa2", self.K_visa, self.ui.comboBoxTS_visa_2, self.ui.labelTS_visa_2, [self.ui.pushButtonTS_select_2, self.ui.pushButtonTS_close_2]))
        main.connect(self.ui.pushButtonTS_close_1, SIGNAL('clicked()'), lambda : self.Close_visa("visa1", self.L_visa, self.ui.labelTS_visa_1, [self.ui.pushButtonTS_select_1, self.ui.pushButtonTS_close_1]))
        main.connect(self.ui.pushButtonTS_close_2, SIGNAL('clicked()'), lambda : self.Close_visa("visa2", self.K_visa, self.ui.labelTS_visa_2, [self.ui.pushButtonTS_select_2, self.ui.pushButtonTS_close_2]))
        main.connect(self.ui.pushButtonTS_Start, SIGNAL('clicked()'), self.start)
        main.connect(self.ui.pushButtonTS_Stop, SIGNAL('clicked()'), self.collect_data_thread.stop)
        main.connect(self.ui.pushButtonTS_Pause, SIGNAL('clicked()'), self.collect_data_thread.pause)
        main.connect(self.ui.pushButtonTS_browse_save_G, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButtonTS_browse_save_O, SIGNAL('clicked()'), self.Other_browse)
        main.connect(self.ui.pushButtonTS_check_G, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButtonTS_Select_Directory_G, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.pushButtonTS_Save_G, SIGNAL('clicked()'), self.G_save)
        main.connect(self.ui.pushButtonTS_Open_G, SIGNAL('clicked()'), self.G_open)
        main.connect(self.ui.pushButtonTS_Save_O, SIGNAL('clicked()'), self.O_save)
        main.connect(self.ui.pushButtonTS_Open_O, SIGNAL('clicked()'), self.O_open)
        main.connect(self.ui.checkBoxTS_partial_scan, SIGNAL("clicked()"), self.Partial_scan)
        main.connect(self.collect_data_thread, SIGNAL("curve_plot"), self.curvePlots_update)
        main.connect(self.collect_data_thread, SIGNAL("mpl_plot"), self.mplPlots)
        main.connect(self.collect_data_thread, SIGNAL("data_available"), self.Pre_save)
        main.connect(self.collect_data_thread, SIGNAL("print"), self.Print_data)
        main.connect(self.ui.checkBoxTS_dsave, SIGNAL("clicked()"), self.Pre_dsave)
        main.connect(self.ui.pushButtonTS_dsave_browse, SIGNAL('clicked()'), self.Dsave_browse)
        
        self.ui.mplwidgetTS_array = self.make_mplToolBar(self.ui.mplwidgetTS_array, self.ui.widgetTS_array)
        self.ui.mplwidgetTS_1 = self.make_mplToolBar(self.ui.mplwidgetTS_1, self.ui.widgetTS_1)
        self.ui.mplwidgetTS_2 = self.make_mplToolBar(self.ui.mplwidgetTS_2, self.ui.widgetTS_2)
        self.ui.mplwidgetTS_3 = self.make_mplToolBar(self.ui.mplwidgetTS_3, self.ui.widgetTS_3)
        self.ui.mplwidgetTS_4 = self.make_mplToolBar(self.ui.mplwidgetTS_4, self.ui.widgetTS_4)

        self.axes_array = None
        self.axes_1 = None
        self.axes_2 = None
        self.axes_3 = None
        self.axes_4 = None
        
        self.curve_itemTS_1 = self.make_curveWidgets(self.ui.curvewidgetTS_1, "b", titles = ["Plot", "X (x)", "Y (y)"])
        self.curve_itemTS_2 = self.make_curveWidgets(self.ui.curvewidgetTS_2, "b", titles = ["Plot", "X (x)", "Y (y)"])
        self.curve_itemTS_3 = self.make_curveWidgets(self.ui.curvewidgetTS_3, "b", titles = ["Plot", "X (x)", "Y (y)"])
        self.curve_itemTS_4 = self.make_curveWidgets(self.ui.curvewidgetTS_4, "b", titles = ["Plot", "X (x)", "Y (y)"])

        self.L_visa = None
        self.K_visa = None
        self.Update_visa("visa1", self.ui.comboBoxTS_visa_1)
        self.Update_visa("visa2", self.ui.comboBoxTS_visa_2)

        self.Array = []
        self.len_Array = 0
        self.count = 0
        self.go_on = True
        self.dsave_directory = ''
        self.array_ok = False
        self.L_visa_ok = False
        self.K_visa_ok = False
        self.partial_scan = True
        
        self.uiSavingGDpushButtons = [ self.ui.pushButtonTS_browse_save_G, self.ui.pushButtonTS_check_G, self.ui.pushButtonTS_Select_Directory_G, self.ui.pushButtonTS_Save_G, self.ui.pushButtonTS_Open_G]
        self.uiSavingGDradioButton = [self.ui.radioButtonTS_csv_G, self.ui.radioButtonTS_txt_G, self.ui.radioButtonTS_Timename_G, self.ui.radioButtonTS_Custom_Name_G]
        self.uiSavingGDtextEdit = [self.ui.textEditTS_comment_G]
        self.uiSavingGDcomboBox = [self.ui.comboBoxTS_Name_Folder_G]
        self.uiSavingGDlineEdit = [self.ui.lineEditTS_GoogleDrive_G, self.ui.lineEditTS_Custom_Name_G]
        self.uiSavingGDlabel = [self.ui.labelTS_condition_G]

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
            self.ui.lineEditTS_array.setText(fileDir)
            self.ui.pushButtonTS_import_visa1.setEnabled(True)
            self.ui.labelTS_condition.setText('File: "' + file_list[len(file_list) - 1] + '" has been chosen.')
        else:
            self.ui.labelTS_condition.setText("Please choose valid file to import.")

    def Import_Array(self):
        self.array_ok = False
        divider_found = True
        count = 0
        temp = 0
        self.Array = []
        x_value = []
        y_value = []
        fileDir = self.ui.lineEditTS_array.text()
        fp = open(fileDir)
        while True:
            if count == 5000:
                self.ui.labelTS_condition.setText("Data not found in file. Please check it.")
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
                self.Array.append(float(value[1]))
                temp += 1
            if self.L_visa_ok and self.K_visa_ok and self.array_ok:    
                self.ui.groupBoxTS_dsave.setEnabled(True)
                self.ui.checkBoxTS_dsave.setEnabled(True)
                self.ui.groupBoxTS_control.setEnabled(True)
                self.ui.pushButtonTS_Pause.setEnabled(False)
                self.ui.pushButtonTS_Stop.setEnabled(False)
            self.ui.groupBoxTS_scan.setEnabled(True)
                
    def Copy_Array(self):
        self.array_ok = False
        Values = self.copyDataFunc()
        if Values != None:
            self.ui.labelTS_condition.setText('Array has been copied and plotted.')
            #self.ui.tabWidget_plot_keithely.setCurrentIndex(0)
            self.Array = []
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
            self.plot_data(self.axes_array, x_value, y_value, ["Array Import Plot", "Steps", "Values"], self.ui.mplwidgetTS_array)
            self.ui.lineEditTS_array.setText('From Array Builder Tab.')
            self.array_ok = True
            if self.L_visa_ok and self.K_visa_ok and self.array_ok:
                self.ui.groupBoxTS_dsave.setEnabled(True)
                self.ui.checkBoxTS_dsave.setEnabled(True)
                self.ui.groupBoxTS_control.setEnabled(True)
                self.ui.pushButtonTS_Pause.setEnabled(False)
                self.ui.pushButtonTS_Stop.setEnabled(False)
            self.ui.groupBoxTS_scan.setEnabled(True)
        else:
            self.ui.labelTS_condition.setText('No valid array to copy.')
    
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
    
    def Print_data(self, i, during, visa1_Vdata, visa1_Cdata, visa2_Vdata, visa2_Cdata, agilent_Vdata, lockin_Vdata, sens_scale):
        self.ui.labelTS_step.setText(str(i))
        self.ui.labelTS_time.setText(format(during, '.3f'))
        self.ui.labelTS_time_unit.setText('s')
        data = self.Twist_scale(visa1_Vdata)
        self.ui.labelTS_1.setText(format(data[0], '.3f'))
        self.ui.labelTS_1unit.setText(data[1] + 'Volt')
        data = self.Twist_scale(visa1_Cdata)
        self.ui.labelTS_2.setText(format(data[0], '.3f'))
        self.ui.labelTS_2unit.setText(data[1] + 'Curr')
        
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
        if gateLead == "visa1":
            self.ui.comboBoxTS_visa_1.clear()
            self.L_visa_ok = False
        elif gateLead == "visa2":
            self.ui.comboBoxTS_visa_2.clear()
            self.K_visa_ok = False
        
        for item in all_visas:
            if gateLead == "visa1":
                self.ui.comboBoxTS_visa_1.addItem(item)
            elif gateLead == "visa2":
                self.ui.comboBoxTS_visa_2.addItem(item)
    
    def Select_visa(self, gateLead, visa_chosen, comboBoxVisa, lineEditVisa, selectClose):
        visa_address = str(comboBoxVisa.currentText())
        rm = visa.ResourceManager()
        if visa_address == 'ASRL62::INSTR':
            inst = rm.open_resource('ASRL62::INSTR', baud_rate = 57600, data_bits = 7, parity = visa.constants.Parity.odd)
        else:
            inst = rm.open_resource(visa_address)
        visa_check = self.Check_visa(inst)
        if visa_check == True:
            self.ui.labelTS_condition.setText("Visa is selected succefully!")
            visa_name = inst.query("*IDN?")
            name_list = visa_name.split(',')
            first_name = name_list[0]
            if gateLead == "visa1":
                if first_name != 'LSCI':
                    self.ui.labelTS_condition.setText('Please select LakeShore.')
                else:
                    self.L_visa_ok = True
                    lineEditVisa.setText(visa_name)
                    selectClose[0].setEnabled(False)
                    selectClose[1].setEnabled(True)
                    self.Enable(gateLead)
                    self.L_visa = inst
            elif gateLead == "visa2":
                if first_name != 'KEITHLEY INSTRUMENTS INC.':
                    self.ui.labelTS_condition.setText('Please select Keithley.')
                else:
                    self.K_visa_ok = True
                    lineEditVisa.setText(visa_name)
                    selectClose[0].setEnabled(False)
                    selectClose[1].setEnabled(True)
                    self.Enable(gateLead)
                    self.K_visa = inst
        elif visa_check == False:
            self.ui.labelTS_condition.setText("Invalid visa address.")
            lineEditVisa.setText("None.")
            visa_chosen = False
            
        if self.L_visa_ok and self.K_visa_ok and self.array_ok:
            self.ui.groupBoxTS_dsave.setEnabled(True)
            self.ui.checkBoxTS_dsave.setEnabled(True)
            self.ui.groupBoxTS_control.setEnabled(True)
            self.ui.pushButtonTS_Pause.setEnabled(False)
            self.ui.pushButtonTS_Stop.setEnabled(False)
            
    def Close_visa(self, gateLead, visa_chosen, lineEditVisa, selectClose):
        self.ui.labelTS_condition.setText('Visa address is closed')
        lineEditVisa.setText('')
        selectClose[0].setEnabled(True)
        selectClose[1].setEnabled(False)
        if gateLead == "visa1":
            visa_chosen.close()
            self.L_visa_ok = False
            self.L_visa = None
            self.Disable(gateLead)
            self.ui.labelTS_timestep.setEnabled(False)
            self.ui.lineEditTS_tstep.setEnabled(False)
        elif gateLead == "visa2":
            self.K_visa_ok = False
            visa_chosen.close()
            self.K_visa = None
            self.Disable(gateLead)
            self.ui.labelTS_timestep.setEnabled(False)
            self.ui.lineEditTS_tstep.setEnabled(False)

    def Check_visa(self, inst):
        try:
            inst.ask("*IDN?")
            valid = True
        except:
            valid = False
        return valid
    
    def Enable(self, gateLead):
        if gateLead == 'visa1':
            self.ui.groupBoxTS_units_visa1.setEnabled(True)
        elif gateLead == 'visa2':
            self.ui.groupBoxTS_units_visa2.setEnabled(True)
            
    def Disable(self, gateLead):
        if gateLead == 'visa1':
            self.ui.groupBoxTS_units_visa1.setEnabled(False)
        elif gateLead == 'visa2':
            self.ui.groupBoxTS_units_visa2.setEnabled(False)
    
    def Partial_scan(self):
        if self.partial_scan:
            self.ui.label_from.setEnabled(True)
            self.ui.lineEditTS_from.setEnabled(True)
            self.ui.label_to.setEnabled(True)
            self.ui.lineEditTS_to.setEnabled(True)
            self.ui.label_K.setEnabled(True)
            self.partial_scan = False
        else:
            self.ui.label_from.setEnabled(False)
            self.ui.lineEditTS_from.setEnabled(False)
            self.ui.label_to.setEnabled(False)
            self.ui.lineEditTS_to.setEnabled(False)
            self.ui.label_K.setEnabled(False)
            self.partial_scan = True
        
        
    def start(self):
        self.dsave_filename = ''
        self.dsave_username = ''
        self.dsave_filetype = ''
        self.dsave_divide = ''
        instruments = [self.L_visa, self.K_visa]
        curves = [self.curve_itemTS_1, self.curve_itemTS_2, self.curve_itemTS_3, self.curve_itemTS_4]
        curveWidgets =[self.ui.curvewidgetTS_1, self.ui.curvewidgetTS_2, self.ui.curvewidgetTS_3, self.ui.curvewidgetTS_4]
        dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
        go_on = None
        if self.ui.checkBoxTS_dsave.isChecked():
            self.Dsave_directory()
            if self.dsave_dir_ok:
                self.Dsave_filename()
                if self.dsave_filename_ok:    
                    self.Dsave_username()
                    if self.dsave_username_ok:
                        self.Dsave_filetype()
                        dsave = [self.dsave_directory, self.dsave_filename, self.dsave_username, self.dsave_thread, self.dsave_filetype, self.dsave_divide]
                        self.collect_data_thread.input(instruments, self.ui, self.Array, go_on , curves, curveWidgets, dsave)
                        self.ui.tabWidgetTS.setCurrentIndex(2)
                        self.ui.pushButtonTS_Start.setEnabled(False)
                        self.ui.pushButtonTS_Pause.setEnabled(True)
                        self.ui.pushButtonTS_Stop.setEnabled(True)
                        self.ui.groupBoxTS_parameters.setEnabled(True)
                        self.ui.labelTS_condition.setText('Running...')
                    else:
                        self.ui.labelTS_condition.setText('Enter user name for dynamic saving.')
                else:
                    self.ui.labelTS_condition.setText('Enter file name for dynamic saving.')
            else:
                self.ui.labelTS_condition.setText('Choose valid directory for dynamic saving.')
        else:
            self.collect_data_thread.input(instruments, self.ui, self.Array, go_on , curves, curveWidgets, dsave)
            self.ui.tabWidgetTS.setCurrentIndex(2)
            self.ui.pushButtonTS_Start.setEnabled(False)
            self.ui.pushButtonTS_Pause.setEnabled(True)
            self.ui.pushButtonTS_Stop.setEnabled(True)
            self.ui.groupBoxTS_parameters.setEnabled(True)
            self.ui.labelTS_condition.setText('Running...')
    
    def curvePlots_update(self, curveInfo):
        curveWidget = curveInfo[0]
        curve = curveInfo[1]
        curveWidget.plot.do_autoscale()
        curve.plot().replot()
    
    def mplPlots(self):
        self.ui.tabWidgetTS.setCurrentIndex(3)
        self.ui.mplwidgetTS_visa1_voltage.draw()
        self.ui.mplwidgetTS_visa1_current.draw()
        self.ui.mplwidgetTS_visa2_voltage.draw()
        self.ui.mplwidgetTS_visa2_current.draw()
        self.ui.mplwidgetTS_agilent_voltage.draw()
        self.ui.mplwidgetTS_lockin_voltage.draw()
        self.ui.mplwidgetTS_lockin_visa1.draw()
        self.ui.mplwidgetTS_lockin_visa2.draw()
        
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
            self.ui.lineEditTS_GoogleDrive_G.setText(file_dir)
            self.ui.labelTS_condition_G.setText('Open Google Drive User Folder')
            self.ui.pushButtonTS_check_G.setEnabled(True)
    
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
            self.ui.lineEditTS_directory_O.setText(fileDir)
            self.ui.labelTS_username_O.setEnabled(True)
            self.ui.comboBoxTS_Name_Folder_O.setEnabled(True)
            self.ui.groupBoxTS_Filename_O.setEnabled(True)
            self.ui.groupBoxTS_File_Type_O.setEnabled(True)
            self.ui.labelTS_comment_O.setEnabled(True)
            self.ui.textEditTS_comment_O.setEnabled(True)
            self.ui.pushButtonTS_Save_O.setEnabled(True)
            self.ui.lineEditTS_Custom_Name_O.setEnabled(True)
            self.ui.labelTS_condition_O.setText("Click save button to save.")
        else:
            self.ui.lineEditTS_directory_O.setText('None')
            self.ui.labelTS_condition_O.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEditTS_GoogleDrive_G.text()).split('\\')
        if os.path.exists(self.ui.lineEditTS_GoogleDrive_G.text()) == False:
            self.ui.labelTS_condition_G.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.labelTS_condition_G.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.labelTS_namefolder_G.setEnabled(True)
                    self.ui.comboBoxTS_Name_Folder_G.setEnabled(True)
                    self.ui.pushButtonTS_Select_Directory_G.setEnabled(True)
                    self.ui.labelTS_condition_G.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBoxTS_Name_Folder_G.currentText())
        if namefolder == 'None':
            self.ui.labelTS_condition_G.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.labelTS_G.setText("Save to \\" + namefolder + "\Date" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Keithely with Array'
            self.ui.groupBoxTS_File_Type_G.setEnabled(True)
            self.ui.groupBoxTS_Filename_G.setEnabled(True)
            self.ui.labelTS_comment_G.setEnabled(True)
            self.ui.textEditTS_comment_G.setEnabled(True)
            self.ui.pushButtonTS_Save_G.setEnabled(True)
            self.ui.lineEditTS_Custom_Name_G.setEnabled(True)
            self.ui.labelTS_condition_G.setText('Click save button to save.')
            
    def Select_type_G(self):
        if self.ui.radioButtonTS_csv_G.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButtonTS_txt_G.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

            
    def Select_type_O(self):
        if self.ui.radioButtonTS_csv_O.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButtonTS_txt_O.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'


    def Select_name_G(self):
        if self.ui.radioButtonTS_Timename_G.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButtonTS_Custom_Name_G.isChecked():
            self.G_file_name = str(self.ui.lineEditTS_Custom_Name_G.text())
            
    def Select_name_O(self):
        if self.ui.radioButtonTS_Timename_O.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButtonTS_Custom_Name_O.isChecked():
            self.O_file_name = str(self.ui.lineEditTS_Custom_Name_O.text())
    
    def Pre_dsave(self):
        if self.ui.checkBoxTS_dsave.isChecked():
            self.ui.labelTS_dsave_directory.setEnabled(True)
            self.ui.lineEditTS_dsave_directory.setEnabled(True)
            self.ui.pushButtonTS_dsave_browse.setEnabled(True)
            self.ui.groupBoxTS_dsave_filename.setEnabled(True)
            self.ui.radioButtonTS_dsave_timename.setEnabled(True)
            self.ui.radioButtonTS_dsave_custname.setEnabled(True)
            self.ui.lineEditTS_dsave_custname.setEnabled(True)
            self.ui.groupBoxTS_dsave_filetype.setEnabled(True)
            self.ui.radioButtonTS_csv.setEnabled(True)
            self.ui.radioButtonTS_txt.setEnabled(True)
            self.ui.labelTS_dsave_username.setEnabled(True)
            self.ui.lineEditTS_dsave_username.setEnabled(True)
            self.ui.labelTS_dsave_comment.setEnabled(True)
            self.ui.textEditTS_dsave_comment.setEnabled(True)
            self.ui.labelTS_condition.setText("Dynamic saving opened.")
        else:
            self.ui.labelTS_dsave_directory.setEnabled(False)
            self.ui.lineEditTS_dsave_directory.setEnabled(False)
            self.ui.pushButtonTS_dsave_browse.setEnabled(False)
            self.ui.groupBoxTS_dsave_filename.setEnabled(False)
            self.ui.radioButtonTS_dsave_timename.setEnabled(False)
            self.ui.radioButtonTS_dsave_custname.setEnabled(False)
            self.ui.lineEditTS_dsave_custname.setEnabled(False)
            self.ui.groupBoxTS_dsave_filetype.setEnabled(False)
            self.ui.radioButtonTS_csv.setEnabled(False)
            self.ui.radioButtonTS_txt.setEnabled(False)
            self.ui.labelTS_dsave_username.setEnabled(False)
            self.ui.lineEditTS_dsave_username.setEnabled(False)
            self.ui.labelTS_dsave_comment.setEnabled(False)
            self.ui.textEditTS_dsave_comment.setEnabled(False)
            self.ui.labelTS_condition.setText("Dynamic saving closed.")
    
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
            self.ui.lineEditTS_dsave_directory.setText(fileDir)
            self.ui.labelTS_condition.setText("Dynamic saving directory selected.")
        else:
            self.ui.lineEditTS_dsave_directory.setText('None')
            self.ui.labelTS_condition.setText('Choose a directory for dynamic saving.')
            
    def Dsave_directory(self):
        self.dsave_dir_ok = True
        if self.ui.lineEditTS_dsave_directory.text() == '' or self.ui.lineEditTS_dsave_directory.text() == 'None':
            self.dsave_dir_ok = False
        
    def Dsave_filename(self):
        self.dsave_filename_ok = True
        self.dsave_filename = ''
        if self.ui.radioButtonTS_dsave_timename.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = 'DSave' + ' ' + date + ' ' + current_time
            self.dsave_filename = str(date_and_time)
        elif self.ui.radioButtonTS_dsave_custname.isChecked():
            self.dsave_filename = str(self.ui.lineEditTS_dsave_custname.text())
            if self.dsave_filename == '':
                self.dsave_filename_ok = False
    
    def Dsave_filetype(self):
        if self.ui.radioButtonTS_csv.isChecked():
            self.dsave_filetype = '.csv'
            self.dsave_divide = ','
        elif self.ui.radioButtonTS_txt.isChecked():
            self.dsave_filetype = '.txt'
            self.dsave_divide = '\t'
            
    def Dsave_username(self):
        self.dsave_username_ok = True
        self.dsave_username = ''
        self.dsave_username = str(self.ui.lineEditTS_dsave_username.text())
        if self.dsave_username == '':
            self.dsave_username_ok = False
    
    def Pre_save(self, date_value, t_value, stepData, Array, visa1Volt_data, visa1Curr_data, visa2Volt_data, visa2Curr_data, agilentVolt_data, lockinVolt_data, sens_scale):
        self.date_value = date_value
        self.t_value = t_value
        self.stepData = stepData
        self.Array = Array
        self.L_visaVolt_data = visa1Volt_data
        self.L_visaCurr_data = visa1Curr_data
        self.K_visaVolt_data = visa2Volt_data
        self.K_visaCurr_data = visa2Curr_data
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
            temp.append(str(self.ui.lineEditTS_array1.text()))
            comments.append(temp)
            # Gate1 visa address
            temp = []
            temp.append('Gate1 Visa Address:')
            temp.append(str(self.ui.comboBoxTS_visa_1.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate1 Visa Name:')
            name = str(self.ui.labelTS_visaname_visa1.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Array2 source
            temp = []
            temp.append('Array2 Source:')
            temp.append(str(self.ui.lineEditTS_array2.text()))
            comments.append(temp)
            # Gate2 visa address
            temp = []
            temp.append('Gate2 Visa Address:')
            temp.append(str(self.ui.comboBoxTS_visa_2.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate2 Visa Name:')
            name = str(self.ui.labelTS_visaname_visa2.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Agilent visa address
            temp = []
            temp.append('Agilent Address:')
            temp.append(str(self.ui.comboBoxTS_a_visa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Agilent Visa Name:')
            name = str(self.ui.labelTS_a_visaname.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Gate1 Y-Values Units
            temp = []
            temp.append('Gate1 Y-Values Units:')
            if self.ui.radioButtonTS_Volts_visa1.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonTS_mVolts_visa1.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonTS_uVolts_visa1.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonTS_nVolts_visa1.isChecked():
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
            if self.ui.radioButtonTS_Volts_visa2.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonTS_mVolts_visa2.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonTS_uVolts_visa2.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonTS_nVolts_visa2.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate2 Lead Output
            temp = []
            temp.append('Gate2 Lead Output:')
            temp.append('2-Terminal')
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditTS_tstep.text()))
            comments.append(temp)
            # Comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditTS_comment_G.toPlainText()))
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
            temp.append(self.ui.comboBoxTS_input.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Couple:')
            temp.append(self.ui.comboBoxTS_couple.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Ground:')
            temp.append(self.ui.comboBoxTS_ground.currentText())
            comments.append(temp)
            temp = []
            temp.append('Input Filter:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Q-factor:')
            temp.append(self.ui.comboBoxTS_Q.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Trim Frequency:')
            temp.append(self.ui.lineEditTS_TF.text())
            temp.append(self.ui.comboBoxTS_TF_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Fliter Type:')
            temp.append(self.ui.comboBoxTS_FT.currentText())
            comments.append(temp)
            temp = []
            temp.append('Reverse:')
            temp.append(self.ui.comboBoxTS_reverse.currentText())
            comments.append(temp)
            temp = []
            temp.append('Slope:')
            temp.append(self.ui.comboBoxTS_slope.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Constant:')
            temp.append(self.ui.comboBoxTS_TC.currentText())
            temp.append(self.ui.comboBoxTS_TC_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Output Mode:')
            temp.append(self.ui.comboBoxTS_output_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Phase:')
            temp.append(self.ui.lineEditTS_phase.text())
            temp.append('degree')
            comments.append(temp)
            temp = []
            temp.append('Frequency:')
            temp.append(self.ui.lineEditTS_freq.text())
            temp.append(self.ui.comboBoxTS_freq_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Amplitude:')
            temp.append(self.ui.lineEditTS_amp.text())
            temp.append(self.ui.comboBoxTS_amp_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Quadrant:')
            temp.append(self.ui.comboBoxTS_quadrant.currentText())
            comments.append(temp)
            temp = []
            temp.append('Mode:')
            temp.append(self.ui.comboBoxTS_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Range:')
            temp.append(self.ui.comboBoxTS_range.currentText())
            temp.append('Hz')
            comments.append(temp)
            temp = []
            temp.append('Ref. Out:')
            temp.append(self.ui.comboBoxTS_refout.currentText())
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
            data.append(self.L_visaVolt_data)
            parameters.append('Gate1 Current')
            units.append('Amps')
            data.append(self.L_visaCurr_data)
            parameters.append('Array2 Value')
            units.append('1')
            data.append(self.Array2)
            parameters.append('Gate2 Voltage')
            units.append('Volts')
            data.append(self.K_visaVolt_data)
            parameters.append('Gate2 Current')
            units.append('Amps')
            data.append(self.K_visaCurr_data)
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
            self.ui.pushButtonTS_Open_G.setEnabled(True)
            self.ui.labelTS_condition_G.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBoxTS_Name_Folder_O.currentText() == 'None':
            self.ui.labelTS_condition_O.setText('Pleanse choose a user name.')
        elif self.ui.radioButtonTS_Custom_Name_O.isChecked() and self.ui.lineEdit_Custom_Name_O.text() == '':
            self.ui.labelTS_condition_O.setText('Please enter a file name.')
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
            temp.append(str(self.ui.lineEditTS_array1.text()))
            comments.append(temp)
            # Gate1 visa address
            temp = []
            temp.append('Gate1 Visa Address:')
            temp.append(str(self.ui.comboBoxTS_visa_1.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate1 Visa Name:')
            name = str(self.ui.labelTS_visaname_visa1.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Array2 source
            temp = []
            temp.append('Array2 Source:')
            temp.append(str(self.ui.lineEditTS_array2.text()))
            comments.append(temp)
            # Gate2 visa address
            temp = []
            temp.append('Gate2 Visa Address:')
            temp.append(str(self.ui.comboBoxTS_visa_2.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Gate2 Visa Name:')
            name = str(self.ui.labelTS_visaname_visa2.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Agilent visa address
            temp = []
            temp.append('Agilent Address:')
            temp.append(str(self.ui.comboBoxTS_a_visa.currentText()))
            comments.append(temp)
            temp = []
            temp.append('Agilent Visa Name:')
            name = str(self.ui.labelTS_a_visaname.text())
            name = name.rstrip()
            temp.append(name)
            comments.append(temp)
            # Gate1 Y-Values Units
            temp = []
            temp.append('Gate1 Y-Values Units:')
            if self.ui.radioButtonTS_Volts_visa1.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonTS_mVolts_visa1.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonTS_uVolts_visa1.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonTS_nVolts_visa1.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate1 Lead Output
            temp = []
            temp.append('Gate1 Lead Output:')
            if self.ui.radioButtonTS_Lead4_visa1.isChecked():
                temp.append('4-Terminal')
            elif self.ui.radioButtonTS_Lead2_visa1.isChecked():
                temp.append('2-Terminal')
            comments.append(temp)
            
            # Gate2 Y-Values Units
            temp = []
            temp.append('Gate2 Y-Values Units:')
            if self.ui.radioButtonTS_Volts_visa2.isChecked():
                temp.append('Volts')
            elif self.ui.radioButtonTS_mVolts_visa2.isChecked():
                temp.append('mVolts')
            elif self.ui.radioButtonTS_uVolts_visa2.isChecked():
                temp.append('uVolts')
            elif self.ui.radioButtonTS_nVolts_visa2.isChecked():
                temp.append('nVolts')
            comments.append(temp)
            # Gate2 Lead Output
            temp = []
            temp.append('Gate2 Lead Output:')
            temp.append('2-Terminal')
            comments.append(temp)
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.ui.lineEditTS_tstep.text()))
            comments.append(temp)
            # Comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEditTS_comment_G.toPlainText()))
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
            temp.append(self.ui.comboBoxTS_input.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Couple:')
            temp.append(self.ui.comboBoxTS_couple.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Ground:')
            temp.append(self.ui.comboBoxTS_ground.currentText())
            comments.append(temp)
            temp = []
            temp.append('Input Filter:')
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Q-factor:')
            temp.append(self.ui.comboBoxTS_Q.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Trim Frequency:')
            temp.append(self.ui.lineEditTS_TF.text())
            temp.append(self.ui.comboBoxTS_TF_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('')
            temp.append('Fliter Type:')
            temp.append(self.ui.comboBoxTS_FT.currentText())
            comments.append(temp)
            temp = []
            temp.append('Reverse:')
            temp.append(self.ui.comboBoxTS_reverse.currentText())
            comments.append(temp)
            temp = []
            temp.append('Slope:')
            temp.append(self.ui.comboBoxTS_slope.currentText())
            comments.append(temp)
            temp = []
            temp.append('Time Constant:')
            temp.append(self.ui.comboBoxTS_TC.currentText())
            temp.append(self.ui.comboBoxTS_TC_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Output Mode:')
            temp.append(self.ui.comboBoxTS_output_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Phase:')
            temp.append(self.ui.lineEditTS_phase.text())
            temp.append('degree')
            comments.append(temp)
            temp = []
            temp.append('Frequency:')
            temp.append(self.ui.lineEditTS_freq.text())
            temp.append(self.ui.comboBoxTS_freq_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Amplitude:')
            temp.append(self.ui.lineEditTS_amp.text())
            temp.append(self.ui.comboBoxTS_amp_unit.currentText())
            comments.append(temp)
            temp = []
            temp.append('Quadrant:')
            temp.append(self.ui.comboBoxTS_quadrant.currentText())
            comments.append(temp)
            temp = []
            temp.append('Mode:')
            temp.append(self.ui.comboBoxTS_mode.currentText())
            comments.append(temp)
            temp = []
            temp.append('Range:')
            temp.append(self.ui.comboBoxTS_range.currentText())
            temp.append('Hz')
            comments.append(temp)
            temp = []
            temp.append('Ref. Out:')
            temp.append(self.ui.comboBoxTS_refout.currentText())
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
            data.append(self.L_visaVolt_data)
            parameters.append('Gate1 Current')
            units.append('Amps')
            data.append(self.L_visaCurr_data)
            parameters.append('Array2 Value')
            units.append('1')
            data.append(self.Array2)
            parameters.append('Gate2 Voltage')
            units.append('Volts')
            data.append(self.K_visaVolt_data)
            parameters.append('Gate2 Current')
            units.append('Amps')
            data.append(self.K_visaCurr_data)
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
            self.ui.pushButtonTS_Open_O.setEnabled(True)
            self.ui.labelTS_condition_O.setText('File has been saved.')
    
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
        self.L_visa = instruments[0]
        self.K_visa = instruments[1]
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
        
        self.sens_scale.append(self.sens_list[self.ui.dialSensTS_lockin1.value()])
        
        self.stop_collecting = False
        self.pause_collecting = False

        self.start()
    
    def stop(self):
        self.stop_collecting = True
        self.ui.labelTS_condition.setText('Stopped.')
        self.ui.pushButtonTS_Start.setEnabled(True)
        self.ui.pushButtonTS_Pause.setEnabled(False)
        self.ui.pushButtonTS_Stop.setEnabled(False)
    
    def pause(self):
        if self.pause_collecting:
            self.ui.labelTS_condition.setText('Running...')
            self.ui.pushButtonTS_Pause.setText("Pause")
            self.pause_collecting = False
        else:
            self.ui.labelTS_condition.setText('Paused. Click continue to run.')
            self.ui.pushButtonTS_Pause.setText("Continue")
            self.pause_collecting = True
    
    def run(self):
        import time

        self.L_visaVolt_data = np.array([])
        self.L_visaCurr_data = np.array([])
        self.K_visaVolt_data = np.array([])
        self.K_visaCurr_data = np.array([])
        self.lockinVolt_data = np.array([])
        self.stepData = []
        self.t_value = np.array([])
        date_value = []
        
        self.time_step = float(self.ui.lineEditTS_tstep.text())
        
        self.turn_on_keithley()
        
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
                        self.set_visa1_voltage(self.Array1[i])
                        self.set_visa2_voltage(self.Array2[i])
                        self.read_data_write()
                        data = self.read_data_read()
                        self.L_visa_Vdata = float(data[0])
                        self.L_visa_Cdata = float(data[1])
                        g1v.append(self.L_visa_Vdata)
                        g1c.append(self.L_visa_Cdata)
                        self.L_visaVolt_data = np.array(g1v)
                        self.L_visaCurr_data = np.array(g1c)
                        self.K_visa_Vdata = float(data[2])
                        self.K_visa_Cdata = float(data[3])
                        g2v.append(self.K_visa_Vdata)
                        g2c.append(self.K_visa_Cdata)
                        self.K_visaVolt_data = np.array(g2v)
                        self.K_visaCurr_data = np.array(g2c)
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
                        if self.ui.radioButtonTS_stepscan.isChecked():
                            self.xlabel = "Steps"
                            self.xdata = self.stepData
                        elif self.ui.radioButtonTS_timescan.isChecked():
                            self.xlabel = 'Time (' + self.time_scale[1] + ')'
                            self.xdata = self.t_value / self.time_scale[0]
                        self.data1 = self.Switch_scale(abs(max(self.L_visaVolt_data)))
                        self.setup_plot(self.curveWidgets[0], self.curves[0], [self.xdata, self.L_visaVolt_data * self.data1[0]], ["Gate1 Voltage", self.xlabel, "Gate1 Voltage (" + self.data1[1] + "V)"])
                        self.data2 = self.Switch_scale(abs(max(self.L_visaCurr_data)))
                        self.setup_plot(self.curveWidgets[1], self.curves[1], [self.xdata, self.L_visaCurr_data * self.data2[0]], ["Gate1 Current", self.xlabel, "Gate1 Current (" + self.data2[1] + "A)"])
                        self.data3 = self.Switch_scale(abs(max(self.K_visaVolt_data)))
                        self.setup_plot(self.curveWidgets[2], self.curves[2], [self.xdata, self.K_visaVolt_data * self.data3[0]], ["Gate2 Voltage", self.xlabel, "Gate2 Voltage (" + self.data3[1] + "V)"])
                        self.data4 = self.Switch_scale(abs(max(self.K_visaCurr_data)))
                        self.setup_plot(self.curveWidgets[3], self.curves[3], [self.xdata, self.K_visaCurr_data * self.data4[0]], ["Gate2 Current", self.xlabel, "Gate2 Current (" + self.data4[1] + "A)"])
                        self.data5 = self.Switch_scale(abs(max(self.agilentVolt_data)))
                        self.setup_plot(self.curveWidgets[4], self.curves[4], [self.xdata, self.agilentVolt_data * self.data5[0]], ["Agilent Voltage", self.xlabel, "Agilent Voltage (" + self.data5[1] + "V)"])
                        self.data6 = self.Switch_scale(abs(max(self.lockinVolt_data)))
                        self.setup_plot(self.curveWidgets[5], self.curves[5], [self.xdata, self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage", self.xlabel, "Lock-in Voltage (" + self.data6[1] + "V)"])
                        self.setup_plot(self.curveWidgets[6], self.curves[6], [self.L_visaVolt_data * self.data1[0], self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage vs Gate1 Voltage", "Gate1 Voltage (" + self.data1[1] + "V)", "Lock-in Voltage (" + self.data6[1] + "V)"])
                        self.setup_plot(self.curveWidgets[7], self.curves[7], [self.K_visaVolt_data * self.data3[0], self.lockinVolt_data * self.data6[0]], ["Lock-in Voltage vs Gate2 Voltage", "Gate2 Voltage (" + self.data3[1] + "V)", "Lock-in Voltage (" + self.data6[1] + "V)"])
                        
                        self.emit(SIGNAL("print"), i, self.during, self.L_visa_Vdata, self.L_visa_Cdata, self.K_visa_Vdata, self.K_visa_Cdata, self.agilent_Vdata, self.lockin_Vdata, self.sens_scale)
                        
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
        self.turn_off_visa1_voltage()
        self.turn_off_visa2_voltage()
        self.ui.pushButtonTS_Start.setEnabled(True)
        self.ui.pushButtonTS_Pause.setEnabled(False)
        self.ui.pushButtonTS_Stop.setEnabled(False)
        self.ui.tabWidgetTS_save.setEnabled(True)
        self.ui.labelTS_condition.setText('Scan completed.')
        self.emit(SIGNAL("data_available"), date_value, self.t_value, self.stepData, self.Array1, self.Array2, self.L_visaVolt_data, self.L_visaCurr_data, self.K_visaVolt_data, self.K_visaCurr_data, self.agilentVolt_data, self.lockinVolt_data, self.sens_scale)
        self.MPL_Plot()
    
    def Pre_dynamic_save(self, num, is_last):
        if self.ui.checkBoxTS_dsave.isChecked():
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
                data.append(self.L_visa_Vdata)
                data.append(self.L_visa_Cdata)
                data.append(self.Array2[num])
                data.append(self.K_visa_Vdata)
                data.append(self.K_visa_Cdata)
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
                    temp.append(str(self.ui.lineEditTS_array1.text()))
                    comments.append(temp)
                    # Gate1 visa address
                    temp = []
                    temp.append('Gate1 Visa Address:')
                    temp.append(str(self.ui.comboBoxTS_visa_1.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Gate1 Visa Name:')
                    name = str(self.ui.labelTS_visaname_visa1.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Array2 source
                    temp = []
                    temp.append('Array2 Source:')
                    temp.append(str(self.ui.lineEditTS_array2.text()))
                    comments.append(temp)
                    # Gate2 visa address
                    temp = []
                    temp.append('Gate2 Visa Address:')
                    temp.append(str(self.ui.comboBoxTS_visa_2.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Gate2 Visa Name:')
                    name = str(self.ui.labelTS_visaname_visa2.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Agilent visa address
                    temp = []
                    temp.append('Agilent Address:')
                    temp.append(str(self.ui.comboBoxTS_a_visa.currentText()))
                    comments.append(temp)
                    temp = []
                    temp.append('Agilent Visa Name:')
                    name = str(self.ui.labelTS_a_visaname.text())
                    name = name.rstrip()
                    temp.append(name)
                    comments.append(temp)
                    # Gate1 Y-Values Units
                    temp = []
                    temp.append('Gate1 Y-Values Units:')
                    if self.ui.radioButtonTS_Volts_visa1.isChecked():
                        temp.append('Volts')
                    elif self.ui.radioButtonTS_mVolts_visa1.isChecked():
                        temp.append('mVolts')
                    elif self.ui.radioButtonTS_uVolts_visa1.isChecked():
                        temp.append('uVolts')
                    elif self.ui.radioButtonTS_nVolts_visa1.isChecked():
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
                    if self.ui.radioButtonTS_Volts_visa2.isChecked():
                        temp.append('Volts')
                    elif self.ui.radioButtonTS_mVolts_visa2.isChecked():
                        temp.append('mVolts')
                    elif self.ui.radioButtonTS_uVolts_visa2.isChecked():
                        temp.append('uVolts')
                    elif self.ui.radioButtonTS_nVolts_visa2.isChecked():
                        temp.append('nVolts')
                    comments.append(temp)
                    # Gate2 Lead Output
                    temp = []
                    temp.append('Gate2 Lead Output:')
                    temp.append('2-Terminal')
                    comments.append(temp)
                    temp = []
                    temp.append('Time Step(sec):')
                    temp.append(str(self.ui.lineEditTS_tstep.text()))
                    comments.append(temp)
                    # Comments
                    temp = []
                    temp.append('Comments:')
                    temp.append(str(self.ui.textEditTS_dsave_comment.toPlainText()))
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
                    temp.append(self.ui.comboBoxTS_input.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Couple:')
                    temp.append(self.ui.comboBoxTS_couple.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Ground:')
                    temp.append(self.ui.comboBoxTS_ground.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Input Filter:')
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Q-factor:')
                    temp.append(self.ui.comboBoxTS_Q.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Trim Frequency:')
                    temp.append(self.ui.lineEditTS_TF.text())
                    temp.append(self.ui.comboBoxTS_TF_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('')
                    temp.append('Fliter Type:')
                    temp.append(self.ui.comboBoxTS_FT.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Reverse:')
                    temp.append(self.ui.comboBoxTS_reverse.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Slope:')
                    temp.append(self.ui.comboBoxTS_slope.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Time Constant:')
                    temp.append(self.ui.comboBoxTS_TC.currentText())
                    temp.append(self.ui.comboBoxTS_TC_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Output Mode:')
                    temp.append(self.ui.comboBoxTS_output_mode.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Phase:')
                    temp.append(self.ui.lineEditTS_phase.text())
                    temp.append('degree')
                    comments.append(temp)
                    temp = []
                    temp.append('Frequency:')
                    temp.append(self.ui.lineEditTS_freq.text())
                    temp.append(self.ui.comboBoxTS_freq_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Amplitude:')
                    temp.append(self.ui.lineEditTS_amp.text())
                    temp.append(self.ui.comboBoxTS_amp_unit.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Quadrant:')
                    temp.append(self.ui.comboBoxTS_quadrant.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Mode:')
                    temp.append(self.ui.comboBoxTS_mode.currentText())
                    comments.append(temp)
                    temp = []
                    temp.append('Range:')
                    temp.append(self.ui.comboBoxTS_range.currentText())
                    temp.append('Hz')
                    comments.append(temp)
                    temp = []
                    temp.append('Ref. Out:')
                    temp.append(self.ui.comboBoxTS_refout.currentText())
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
        if self.ui.radioButtonTS_stepscan.isChecked():
            self.xlabel = "Steps"
            self.xdata = self.stepData
        elif self.ui.radioButtonTS_timescan.isChecked():
            self.xlabel = 'Time (' + self.time_scale[1] + ')'
            self.xdata = self.t_value / self.time_scale[0]
            
        self.Reset_plot_visa1_voltage()
        self.axes_visa1_voltage.grid()
        self.axes_visa1_voltage.set_title("Gate1 Voltage")
        self.axes_visa1_voltage.set_ylabel("Gate1 Voltage (" + self.data1[1] + "V)")
        self.axes_visa1_voltage.set_xlabel(self.xlabel)
        self.axes_visa1_voltage.plot(self.xdata, self.L_visaVolt_data * self.data1[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_visa1_current()
        self.axes_visa1_current.grid()
        self.axes_visa1_current.set_title("Gate1 Current")
        self.axes_visa1_current.set_ylabel("Gate1 Current (" + self.data2[1] + "A)")
        self.axes_visa1_current.set_xlabel(self.xlabel)
        self.axes_visa1_current.plot(self.xdata, self.L_visaCurr_data * self.data2[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_visa2_voltage()
        self.axes_visa2_voltage.grid()
        self.axes_visa2_voltage.set_title("Gate2 Voltage")
        self.axes_visa2_voltage.set_ylabel("Gate2 Voltage (" + self.data3[1] + "V)")
        self.axes_visa2_voltage.set_xlabel(self.xlabel)
        self.axes_visa2_voltage.plot(self.xdata, self.K_visaVolt_data * self.data3[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_visa2_current()
        self.axes_visa2_current.grid()
        self.axes_visa2_current.set_title("Gate2 Current")
        self.axes_visa2_current.set_ylabel("Gate2 Current (" + self.data4[1] + "A)")
        self.axes_visa2_current.set_xlabel(self.xlabel)
        self.axes_visa2_current.plot(self.xdata, self.K_visaCurr_data * self.data4[0], marker = 'o', linestyle = '-')
        
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
        
        self.Reset_plot_lockin_visa1()
        self.axes_lockin_visa1.grid()
        self.axes_lockin_visa1.set_title("Lock-in Voltage vs Gate1 Voltage")
        self.axes_lockin_visa1.set_ylabel("Lock-in Voltage (" + self.data6[1] + "V)")
        self.axes_lockin_visa1.set_xlabel("Gate1 Voltage (" + self.data1[1] + "V)")
        self.axes_lockin_visa1.plot(self.L_visaVolt_data * self.data1[0], self.lockinVolt_data * self.data6[0], marker = 'o', linestyle = '-')
        
        self.Reset_plot_lockin_visa2()
        self.axes_lockin_visa2.grid()
        self.axes_lockin_visa2.set_title("Lock-in Voltage vs Gate2 Voltage")
        self.axes_lockin_visa2.set_ylabel("Lock-in Voltage (" + self.data6[1] + "V)")
        self.axes_lockin_visa2.set_xlabel("Gate2 Voltage (" + self.data3[1] + "V)")
        self.axes_lockin_visa2.plot(self.K_visaVolt_data * self.data3[0], self.lockinVolt_data * self.data6[0], marker = 'o', linestyle = '-')
        
        self.emit(SIGNAL("mpl_plot"))
        
    def Reset_plot_visa1_voltage(self):
        self.ui.mplwidgetTS_visa1_voltage.figure.clear()
        self.axes_visa1_voltage = self.ui.mplwidgetTS_visa1_voltage.figure.add_subplot(111)
        
    def Reset_plot_visa1_current(self):
        self.ui.mplwidgetTS_visa1_current.figure.clear()
        self.axes_visa1_current = self.ui.mplwidgetTS_visa1_current.figure.add_subplot(111)
    
    def Reset_plot_visa2_voltage(self):
        self.ui.mplwidgetTS_visa2_voltage.figure.clear()
        self.axes_visa2_voltage = self.ui.mplwidgetTS_visa2_voltage.figure.add_subplot(111)
        
    def Reset_plot_visa2_current(self):
        self.ui.mplwidgetTS_visa2_current.figure.clear()
        self.axes_visa2_current = self.ui.mplwidgetTS_visa2_current.figure.add_subplot(111)
        
    def Reset_plot_agilent_voltage(self):
        self.ui.mplwidgetTS_agilent_voltage.figure.clear()
        self.axes_agilent_voltage = self.ui.mplwidgetTS_agilent_voltage.figure.add_subplot(111)
        
    def Reset_plot_lockin_voltage(self):
        self.ui.mplwidgetTS_lockin_voltage.figure.clear()
        self.axes_lockin_voltage = self.ui.mplwidgetTS_lockin_voltage.figure.add_subplot(111)
        
    def Reset_plot_lockin_visa1(self):
        self.ui.mplwidgetTS_lockin_visa1.figure.clear()
        self.axes_lockin_visa1 = self.ui.mplwidgetTS_lockin_visa1.figure.add_subplot(111)
        
    def Reset_plot_lockin_visa2(self):
        self.ui.mplwidgetTS_lockin_visa2.figure.clear()
        self.axes_lockin_visa2 = self.ui.mplwidgetTS_lockin_visa2.figure.add_subplot(111)
        
    def setup_plot(self, curveWidget, curve, data, titles):
        curveWidget.plot.set_titles(titles[0], titles[1], titles[2])
        curve.set_data(data[0], data[1])
        self.emit(SIGNAL("curve_plot"), [curveWidget, curve])

    def set_voltage(self, inst, voltage):
        inst.write('TRACE:CLEar "defbuffer1"')
        inst.write("ROUT:TERM FRONT")
        inst.write('SENS:FUNC "CURR"')
        #inst.write('SOUR:VOLT:RANG AUTO')
        inst.write("SOUR:FUNC VOLT")
        inst.write("SOUR:VOLT:READ:BACK 1")
        inst.write("SOUR:VOLT " + voltage)
        
    def set_current(self, inst, current):
        inst.write('TRACE:CLEar "defbuffer1"')
        inst.write("ROUT:TERM FRONT")
        inst.write('SENS:FUNC "CURR"')
        #inst.write('SOUR:VOLT:RANG AUTO')
        inst.write("SOUR:FUNC VOLT")
        inst.write("SOUR:VOLT:READ:BACK 1")
        inst.write("SOUR:VOLT " + voltage)
    
    def turn_on_voltage(self, inst):
        inst.write('SENS:CURR:RSEN ON' )
        inst.write("OUTP ON")
    
    def turn_on_current(self, inst):
        inst.write('SENS:CURR:RSEN ON' )
        inst.write("OUTP ON")
    
    def read_data_write(self, inst):
        inst.write('READ? "defbuffer1", SOUR, READ')
        
    def read_data_read(self, inst):
        voltage, current = inst.read().replace("\n", "").split(",")
        return [voltage, current]
    
    def turn_off_visa1_voltage(self, inst):
        if not self.ui.checkBoxTS_Output_on.isChecked():
            inst.write("OUTP OFF")
    
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