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

# Import the PyQt4 modules for all the commands that control the GUI. Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Save import Save_Thread

# These are the modules required for the guiqwt widgets. Import plot widget base class
from guiqwt.pyplot import *
from guiqwt.plot import CurveWidget
from guiqwt.builder import make

class Agilent_Yokogawa():
    def __init__(self, main, ui):
        self.ui = ui
        self.copyData = main.copyData
        self.collectDataThread = CollectData()
        self.save_thread = Save_Thread()
        
        self.rm = visa.ResourceManager()
        self.update_visa()
        
        self.ui.startButton.setDisabled(True)
        self.ui.closeVisaButton1.setDisabled(True)
        self.ui.closeVisaButton2.setDisabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.startButton.setEnabled(False)
        
        self.x_value = []
        self.y_value = []
        self.item = 0
        self.Array = []
        self.frontX = 0.0
        self.frontY = 0.0
        self.backX = 0.0
        self.backY = 0.0
        self.x_plot = [-1.0,1.0]
        self.y_plot = [-1.0,1.0]
        
        self.timeStep = .1
        self.ui.timeStepValue.setText(str(self.timeStep))
        
        self.directory = ''
        self.temp = []

        # Sets up Current v. Voltage guiqwt plot
        self.curve_item_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_scanPlot_ay.plot.add_item(self.curve_item_ay)
        self.ui.curvewidget_scanPlot_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_scanPlot_ay.plot.set_titles("Current v. Voltage", "Current (A)", "Voltage (V)")
        
        # Sets up Voltage v. Time Step guiqwt plot
        self.curve_item_vt_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_vt_ay.plot.add_item(self.curve_item_vt_ay)
        self.ui.curvewidget_vt_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_vt_ay.plot.set_titles("Voltage v. Time Step", "Time Step", "Voltage (V)")
        
         # Sets up Current v. Time Step guiqwt plot
        self.curve_item_ct_ay = make.curve([], [], color='b', marker = "o")
        self.ui.curvewidget_ct_ay.plot.add_item(self.curve_item_ct_ay)
        self.ui.curvewidget_ct_ay.plot.set_antialiasing(True)
        self.ui.curvewidget_ct_ay.plot.set_titles("Current v. Time Step", "Time Step", "Current (A)")
        
        # For the canvas.
        self.canvas_import_ay = FigureCanvas(self.ui.mplwidget_import_ay.figure)
        self.canvas_import_ay.setParent(self.ui.widget_import_ay)
        self.mpl_toolbar_import_ay = NavigationToolbar(self.canvas_import_ay, self.ui.widget_import_ay)
        self.canvas_analysis_ay = FigureCanvas(self.ui.mplwidget_analysis_ay.figure)
        self.canvas_analysis_ay.setParent(self.ui.widget_analysis_ay)
        self.mpl_toolbar_analysis_ay = NavigationToolbar(self.canvas_analysis_ay, self.ui.widget_analysis_ay)
        self.canvas_analysis_ct_ay = FigureCanvas(self.ui.mplwidget_analysis_ct_ay.figure)
        self.canvas_analysis_ct_ay.setParent(self.ui.widget_analysis_ct_ay)
        self.mpl_toolbar_analysis_ct_ay = NavigationToolbar(self.canvas_analysis_ct_ay, self.ui.widget_analysis_ct_ay)
        self.canvas_analysis_vt_ay = FigureCanvas(self.ui.mplwidget_analysis_vt_ay.figure)
        self.canvas_analysis_vt_ay.setParent(self.ui.widget_analysis_vt_ay)
        self.mpl_toolbar_analysis_vt_ay = NavigationToolbar(self.canvas_analysis_vt_ay, self.ui.widget_analysis_vt_ay)
        
        # Create the QVBoxLayout object and add the widget into the layout
        vbox_import_ay = QVBoxLayout()
        vbox_import_ay.addWidget(self.canvas_import_ay)
        vbox_import_ay.addWidget(self.mpl_toolbar_import_ay)
        self.ui.widget_import_ay.setLayout(vbox_import_ay)
        vbox_analysis_ay = QVBoxLayout()
        vbox_analysis_ay.addWidget(self.canvas_analysis_ay)
        vbox_analysis_ay.addWidget(self.mpl_toolbar_analysis_ay)
        self.ui.widget_analysis_ay.setLayout(vbox_analysis_ay)
        vbox_analysis_ct_ay = QVBoxLayout()
        vbox_analysis_ct_ay.addWidget(self.canvas_analysis_ct_ay)
        vbox_analysis_ct_ay.addWidget(self.mpl_toolbar_analysis_ct_ay)
        self.ui.widget_analysis_ct_ay.setLayout(vbox_analysis_ct_ay)
        vbox_analysis_vt_ay = QVBoxLayout()
        vbox_analysis_vt_ay.addWidget(self.canvas_analysis_vt_ay)
        vbox_analysis_vt_ay.addWidget(self.mpl_toolbar_analysis_vt_ay)
        self.ui.widget_analysis_vt_ay.setLayout(vbox_analysis_vt_ay)
        
        # Connect the mplwidget with canvass
        self.ui.mplwidget_import_ay = self.canvas_import_ay
        self.ui.mplwidget_analysis_ay = self.canvas_analysis_ay
        self.ui.mplwidget_analysis_ct_ay = self.canvas_analysis_ct_ay
        self.ui.mplwidget_analysis_vt_ay = self.canvas_analysis_vt_ay
        
        main.connect(self.ui.startButton, SIGNAL("clicked()"), self.start)
        main.connect(self.ui.stopButton, SIGNAL("clicked()"), self.stop)
        main.connect(self.ui.slopeButton_ay, SIGNAL("clicked()"), self.slopeTriger)
        main.connect(self.collectDataThread, SIGNAL("stop"), self.stop)
        main.connect(self.collectDataThread, SIGNAL("plot"), self.plotData)
        main.connect(self.collectDataThread, SIGNAL("analyse"), self.analyse)

        main.connect(self.ui.pushButton_browse_ay, SIGNAL('clicked()'), self.browse_ay)
        main.connect(self.ui.pushButton_import_ay, SIGNAL('clicked()'), self.import_ay)
        main.connect(self.ui.pushButton_copy_ay, SIGNAL('clicked()'), self.copy_ay)
        main.connect(self.ui.selectVisaButton, SIGNAL("clicked()"), self.select_visa)
        main.connect(self.ui.updateVisaButton, SIGNAL("clicked()"), self.update_visa)
        main.connect(self.ui.closeVisaButton1, SIGNAL("clicked()"), self.close_visa1)
        main.connect(self.ui.closeVisaButton2, SIGNAL("clicked()"), self.close_visa2)
        
        main.connect(self.ui.pushButton_browse_save_G_ay, SIGNAL('clicked()'), self.Google_browse)
        main.connect(self.ui.pushButton_browse_save_O_ay, SIGNAL('clicked()'), self.Other_browse)
        main.connect(self.ui.pushButton_check_G_ay, SIGNAL('clicked()'), self.Check)
        main.connect(self.ui.pushButton_Select_Directory_G_ay, SIGNAL('clicked()'), self.Google_select_namefolder)
        main.connect(self.ui.pushButton_Save_G_ay, SIGNAL('clicked()'), self.G_save)
        main.connect(self.ui.pushButton_Open_G_ay, SIGNAL('clicked()'), self.G_open)
        main.connect(self.ui.pushButton_Save_O_ay, SIGNAL('clicked()'), self.O_save)
        main.connect(self.ui.pushButton_Open_O_ay, SIGNAL('clicked()'), self.O_open)
        
        main.ui.mplwidget_analysis_ay.figure.canvas.mpl_connect('button_release_event', self.slope)
        
    def browse_ay(self):
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

    def import_ay(self):
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
            
            self.plot_import(x_value, y_value)
            self.ui.output.setText("File was imported correctly.")
            
    def copy_ay(self):
        Values = self.copyData()
        if not Values == False:
            for i in range(0, len(Values)):
                for j in range(0, len(Values[i])):
                    self.x_value.append(self.item)
                    self.x_value.append(self.item + 1)
                    self.y_value.append(Values[i][j])
                    self.y_value.append(Values[i][j])
                    self.Array.append(Values[i][j])
                    self.item += 1
        self.plot_import(self.x_value, self.y_value)

    def check_visa(self, inst):
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
        
        current_visa1 = self.ui.visa1.text()
        current_visa2 = self.ui.visa2.text()
        
        check_current1 = False
        check_current2 = False
        
        self.ui.selectVisa1.clear()
        self.ui.selectVisa2.clear()
        
        self.insts = range(1, len(visas))
        self.inst_names = self.insts
        #try:
        for i in range(0, len(visas)-1):
            self.insts[i] = self.rm.open_resource(visas[i])
            #self.inst_names[i] = self.insts[i].ask('*IDN?')
        #except:
            #self.ui.output.setText("Error in updata visa")
            #self.ui.visa1.setText(visas[1])
            #self.ui.visa2.setText(visas[2])
            
        self.ui.output.setText(str(self.inst_names))
            
        for each_visa in visas:
            if current_visa1 == each_visa:
                check_current1 = True
            self.ui.selectVisa1.addItem(each_visa)
            
        for each_visa in visas:
            if current_visa2 == each_visa:
                check_current2 = True
            self.ui.selectVisa2.addItem(each_visa)
        
        if check_current1 == False:
            self.ui.visa1.setText("None")
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton1.setDisabled(True)
        
        if check_current2 == False:
            self.ui.visa2.setText("None")
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton2.setDisabled(True)

    def select_visa(self):
        visa_chosen1 = str(self.ui.selectVisa1.currentText())
        visa_chosen2 = str(self.ui.selectVisa2.currentText())
        valid = False

        try:
            inst1 = self.rm.open_resource(visa_chosen1)
            inst2 = self.rm.open_resource(visa_chosen2)
            valid = True
        except:
            valid = False

        if valid:
            self.ui.visa1.setText(visa_chosen1)
            self.ui.visa2.setText(visa_chosen2)
            self.visa_chosen1 = inst1
            self.visa_chosen2 = inst2
            self.visa1_name = self.visa_chosen1.ask('*IDN?')
            self.visa2_name = self.visa_chosen2.ask('*IDN?')
            self.ui.output.setText(self.visa1_name + self.visa2_name)
            self.ui.error.setText("None")
            self.ui.startButton.setDisabled(False)
            self.ui.stopButton.setDisabled(False)
            self.ui.closeVisaButton1.setDisabled(False)
            self.ui.closeVisaButton2.setDisabled(False)

            self.visa_chosen1.write('SOUR:FUNC CURR')
            self.visa_chosen1.write('SOUR:PROT:VOLT 30')
        elif not valid:
            self.ui.error.setText("Invalid Visa Port.")
            self.ui.visa1.setText("None")
            self.ui.visa2.setText("None")
            self.visa_chosen1 = False
            self.ui.startButton.setDisabled(True)
            self.ui.closeVisaButton1.setDisabled(True)
            self.ui.closeVisaButton2.setDisabled(True)
    
    def close_visa1(self):
        self.collectDataThread.stop()
        try:
            self.ui.output.setText(self.visa_chosen1.ask("*IDN?"))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa1.setText("None")
            self.ui.error.setText("None")
            self.visa_chosen1.close()
        
        elif valid == False:
            self.ui.error.setText("No visa connected.")
            self.ui.visa1.setText("None")
            
        self.visa_chosen1 = False
        self.ui.startButton.setDisabled(True)
        self.ui.stopButton.setDisabled(True)
        self.ui.closeVisaButton1.setDisabled(True)
        
    def close_visa2(self):
        self.collectDataThread.stop()
        try:
            self.ui.output.setText(self.visa_chosen2.ask('*IDN?'))
            valid = True
        except:
            valid = False

        if valid == True:
            self.ui.visa2.setText('None')
            self.ui.error.setText("None")
            self.visa_chosen2.close()
        
        elif valid == False:
            self.ui.error.setText("No visa connected.")
            self.ui.visa2.setText("None")
        
        self.visa_chosen2 = False
        self.ui.startButton.setDisabled(True)
        self.ui.stopButton.setDisabled(True)
        self.ui.closeVisaButton2.setDisabled(True)
    
    def start(self):
        if self.ui.startButton.text() == 'Start' and float(self.ui.timeStepValue.text()) >= 0:
            self.visa_chosen1.write('OUTP ON')
            self.timeStep = float(self.ui.timeStepValue.text())
            self.ui.timeStepValue.setDisabled(True)
            self.collectDataThread.input(self.ui, self.visa_chosen1, self.visa_chosen2, self.Array, self.timeStep, self.curve_item_ay, self.curve_item_vt_ay, self.curve_item_ct_ay, [], [], [])
            self.ui.stopButton.setEnabled(True)
            self.ui.output.setText("Running")
            self.ui.startButton.setText("Pause")
        elif self.ui.startButton.text() == 'Pause':
            self.collectDataThread.pause()
            
    def stop(self):
        if self.ui.stopButton.text() == 'Stop':
            self.collectDataThread.stop()
                
    def plot_import(self, x, y):
        self.ui.mplwidget_import_ay.figure.clear()
        self.axes_import = self.ui.mplwidget_import_ay.figure.add_subplot(111)
        self.axes_import.plot(x, y, marker = '.', linestyle = '-')
        self.axes_import.grid()
        self.axes_import.set_title("Array Import Plot")
        self.axes_import.set_xlabel("Steps")
        self.axes_import.set_ylabel("Values")
        self.ui.mplwidget_import_ay.draw()

    def plotData(self):
        self.ui.curvewidget_scanPlot_ay.plot.do_autoscale()
        self.ui.curvewidget_vt_ay.plot.do_autoscale()
        self.ui.curvewidget_ct_ay.plot.do_autoscale()
        self.curve_item_ay.plot().replot()
        self.curve_item_vt_ay.plot().replot()
        self.curve_item_ct_ay.plot().replot()

    def analyse(self, date_value, t_value, x_plot, y_plot):
        self.date_value = date_value
        self.t_value = t_value
        self.x_plot = x_plot
        self.y_plot = y_plot
        self.ui.mplwidget_analysis_ay.figure.clear()
        self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
        self.axes_analysis_ay.grid()
        self.axes_analysis_ay.set_title('Voltage v. Current')
        self.axes_analysis_ay.set_ylabel("Voltage (V)")
        self.axes_analysis_ay.set_xlabel("Current (A)")
        self.axes_analysis_ay.plot(x_plot, y_plot, marker = '.', linestyle = '-')
        self.ui.mplwidget_analysis_ay.draw()
        self.frontX = self.x_plot[0]
        self.frontY = self.y_plot[0]
        self.ui.tabWidget_save_ay.setEnabled(True)
        
        self.ui.mplwidget_analysis_ct_ay.figure.clear()
        self.axes_analysis_ct_ay = self.ui.mplwidget_analysis_ct_ay.figure.add_subplot(111)
        self.axes_analysis_ct_ay.grid()
        self.axes_analysis_ct_ay.set_title('Current v. Step')
        self.axes_analysis_ct_ay.set_ylabel("Current (A)")
        self.axes_analysis_ct_ay.set_xlabel("Step")
        self.axes_analysis_ct_ay.plot(t_value, y_plot, marker = '.', linestyle = '-')
        self.ui.mplwidget_analysis_ct_ay.draw()
        
        self.ui.mplwidget_analysis_vt_ay.figure.clear()
        self.axes_analysis_vt_ay = self.ui.mplwidget_analysis_vt_ay.figure.add_subplot(111)
        self.axes_analysis_vt_ay.grid()
        self.axes_analysis_vt_ay.set_title('Voltage v. Step')
        self.axes_analysis_vt_ay.set_ylabel("Voltage (V)")
        self.axes_analysis_vt_ay.set_xlabel("Step")
        self.axes_analysis_vt_ay.plot(t_value, x_plot, marker = '.', linestyle = '-')
        self.ui.mplwidget_analysis_vt_ay.draw()

    def slopeTriger(self):
        if self.ui.slope_ay.isChecked():
            self.ui.slope_ay.setChecked(False)
        else:
            self.ui.slope_ay.setChecked(True)

    def slope(self, event=None):
        if self.ui.slope_ay.isChecked():
            self.backX = self.frontX 
            self.backY = self.frontY
            self.frontX = event.xdata
            self.frontY = event.ydata
            
            index= min(range(len(self.x_plot)), key=lambda i: math.sqrt((self.x_plot[i]-self.frontX)**2+(self.y_plot[i]-self.frontY)**2))
            
            self.frontX = self.x_plot[index]
            self.frontY = self.y_plot[index]
            
            if not ((self.frontX == self.backX) or (self.frontY == self.backY)):
                try:
                    VI = (self.frontY-self.backY)/(self.frontX-self.backX)
                except:
                    VI = "None"
                
                try:
                    IV = (self.frontX-self.backX)/(self.frontY-self.backY)
                except:
                    IV = "None"
                    
                self.ui.output.setText("Resistance: " + str(VI) + " Ohm")
                self.ui.slop_VI_ay.setText(str(VI))
                self.ui.slop_IV_ay.setText(str(IV))
            
            x = [self.backX, self.frontX]
            y = [self.backY, self.frontY]
            
            self.ui.start_end_fit_ay.setText("(" + str(self.backX) + ", " + str(self.backY) + "), " +"(" + str(self.frontX) + ", " + str(self.frontY) + ")")
            
            self.ui.mplwidget_analysis_ay.figure.clear()
            self.axes_analysis_ay = self.ui.mplwidget_analysis_ay.figure.add_subplot(111)
            self.axes_analysis_ay.grid()
            self.axes_analysis_ay.set_title('Voltage v. Current')
            self.axes_analysis_ay.set_ylabel("Voltage (V)")
            self.axes_analysis_ay.set_xlabel("Current (A)")
            self.axes_analysis_ay.plot(self.x_plot, self.y_plot, 'b.-', x, y, 'r')
            self.ui.mplwidget_analysis_ay.draw()

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

    def select_type_ay(self):
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

    def select_name_ay(self):
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
        try:
            self.folder_name = str(self.ui.folderName.currentText())
        except ValueError:
            self.folder_name = False
        if self.folder_name == 'None' or self.folder_name == '' :
            self.folder_name = False

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
            self.ui.lineEdit_GoogleDrive_G_ay.setText(file_dir)
            self.ui.label_condition_G_ay.setText('Open Google Drive User Folder')
            self.ui.pushButton_check_G_ay.setEnabled(True)
    
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
            self.ui.lineEdit_directory_O_ay.setText(fileDir)
            self.ui.label_username_O_ay.setEnabled(True)
            self.ui.comboBox_Name_Folder_O_ay.setEnabled(True)
            self.ui.groupBox_Filename_O_ay.setEnabled(True)
            self.ui.groupBox_File_Type_O_ay.setEnabled(True)
            self.ui.label_comment_O_ay.setEnabled(True)
            self.ui.textEdit_comment_O_ay.setEnabled(True)
            self.ui.pushButton_Save_O_ay.setEnabled(True)
            self.ui.lineEdit_Custom_Name_O_ay.setEnabled(True)
            self.ui.label_condition_O_ay.setText("Click save button to save.")
        else:
            self.ui.lineEdit_directory_O_ay.setText('None')
            self.ui.label_condition_O_ay.setText('Failed to Read File')
        
    def Check(self):
        self.G_directory = ''
        file_list = []
        file_list = str(self.ui.lineEdit_GoogleDrive_G_ay.text()).split('\\')
        if os.path.exists(self.ui.lineEdit_GoogleDrive_G_ay.text()) == False:
            self.ui.label_condition_G_ay.setText('Incorrect Google Drive Directory.')
        else:
            self.ui.label_condition_G_ay.setText('Please click browse to the "03 User Accounts" folder')
            for i in range(0, len(file_list)):
                self.G_directory += file_list[i] + '\\'
                if file_list[i].upper() == '03 User Accounts'.upper():
                    self.ui.label_namefolder_G_ay.setEnabled(True)
                    self.ui.comboBox_Name_Folder_G_ay.setEnabled(True)
                    self.ui.pushButton_Select_Directory_G_ay.setEnabled(True)
                    self.ui.label_condition_G_ay.setText('Choose name folder in Google Drive to save.')                   
                    break
    
    def Google_select_namefolder(self):
        namefolder = str(self.ui.comboBox_Name_Folder_G_ay.currentText())
        if namefolder == 'None':
            self.ui.label_condition_G_ay.setText('Please choose a name folder to save.')
        else:
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            self.ui.label_G_ay.setText("Save to \\" + namefolder + "\Date" + '\\' + date)
            self.G_directory += namefolder + "\Data" + '\\' + date + '\\' + 'Agilent Yokogawa with Array'
            self.ui.groupBox_File_Type_G_ay.setEnabled(True)
            self.ui.groupBox_Filename_G_ay.setEnabled(True)
            self.ui.label_comment_G_ay.setEnabled(True)
            self.ui.textEdit_comment_G_ay.setEnabled(True)
            self.ui.pushButton_Save_G_ay.setEnabled(True)
            self.ui.lineEdit_Custom_Name_G_ay.setEnabled(True)
            self.ui.label_condition_G_ay.setText('Click save button to save.')
            
    def Select_type_G_ay(self):
        if self.ui.radioButton_csv_G_ay.isChecked():
            self.G_type = '.csv'
            self.G_divide = ','

        elif self.ui.radioButton_txt_G_ay.isChecked():
            self.G_type = '.txt'
            self.G_divide = '\t'

    def Select_type_O_ay(self):
        if self.ui.radioButton_csv_O_ay.isChecked():
            self.O_type = '.csv'
            self.O_divide = ','

        elif self.ui.radioButton_txt_O_ay.isChecked():
            self.O_type = '.txt'
            self.O_divide = '\t'

    def Select_name_G_ay(self):
        if self.ui.radioButton_Timename_G_ay.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.G_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_G_ay.isChecked():
            self.G_file_name = str(self.ui.lineEdit_Custom_Name_G_ay.text())
            
    def Select_name_O_ay(self):
        if self.ui.radioButton_Timename_O_ay.isChecked():
            now = datetime.datetime.now()
            date = '%s-%s-%s' % (now.year, now.month, now.day)
            current_time = '%s.%s.%s' % (now.hour, now.minute, now.second)
            date_and_time = date + ' ' + current_time
            self.O_file_name = str(date_and_time)
        elif self.ui.radioButton_Custom_Name_O_ay.isChecked():
            self.O_file_name = str(self.ui.lineEdit_Custom_Name_O_ay.text())
            
    def Pre_save(self, date_value, t_value, x_value, y_value, array):
        self.date_value = date_value
        self.t_value = t_value
        self.x_value = x_value
        self.y_value = y_value
        self.array = array
    
    def G_save(self):
        if self.ui.radioButton_Custom_Name_G_ay.isChecked() and self.ui.lineEdit_Custom_Name_G_ay.text() == '':
            self.ui.label_condition_G_ay.setText('Enter a valid file name.')
        else:
            self.Select_type_G_ay()
            self.Select_name_G_ay()
            
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
            
            # Line 1: user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_G_ay.currentText()))
            comments.append(temp)
            # Line 2: edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Line 3: array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_ay.text()))
            comments.append(temp)
            # Line 4: visa1 address
            temp = []
            temp.append('Visa 1 Address:')
            temp.append(str(self.ui.visa1.text()))
            comments.append(temp)
            # Line 5: visa2 address
            temp = []
            temp.append('Visa 2 Address:')
            temp.append(str(self.ui.visa2.text()))
            comments.append(temp)
            # Line 6: visa1 name
            temp = []
            temp.append('Visa 1 Name:')
            visa1_name = self.visa1_name.rstrip('\n')
            visa1_name = visa1_name.replace(',', ' ')
            temp.append(str(visa1_name))
            comments.append(temp)
            # Line 7: visa2 name
            temp = []
            temp.append('Visa 2 Name:')
            visa2_name = self.visa2_name.rstrip('\n')
            visa2_name = visa2_name.replace(',', ' ')
            temp.append(str(visa2_name))
            comments.append(temp)
            # Line 8: scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Voltage')
            comments.append(temp)
            # Line 9: time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.timeStep))
            comments.append(temp)
            # Line 10: comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_G_ay.toPlainText()))
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
            temp = []
            for i in range(0, len(self.y_plot)):
                temp.append(i)
            data.append(temp)
            parameters.append('Array')
            units.append('1')
            data.append(self.x_value)
            parameters.append('Voltage')
            units.append('Volts')
            data.append(self.x_plot)
            parameters.append('Current')
            units.append('Amps')
            data.append(self.y_plot)
            
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
            self.ui.pushButton_Open_G_ay.setEnabled(True)
            self.ui.label_condition_G_ay.setText('File has been saved.')
    
    def O_save(self):
        if self.ui.comboBox_Name_Folder_O_ay.currentText() == 'None':
            self.ui.label_condition_O_ay.setText('Pleanse choose a user name.')
        elif self.ui.radioButton_Custom_Name_O_ay.isChecked() and self.ui.lineEdit_Custom_Name_O_ay.text() == '':
            self.ui.label_condition_O_ay.setText('Please enter a file name.')
        else:
            self.Select_type_O_ay()
            self.Select_name_O_ay()
            
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
            
            # Line 1: user name
            temp = []
            temp.append('User Name:')
            temp.append(str(self.ui.comboBox_Name_Folder_G_ay.currentText()))
            comments.append(temp)
            # Line 2: edit time
            temp = []
            temp.append('Edit Time:')
            temp.append(str(datetime.datetime.now()))
            comments.append(temp)
            # Line 3: array source
            temp = []
            temp.append('Array Source:')
            temp.append(str(self.ui.lineEdit_directory_ay.text()))
            comments.append(temp)
            # Line 4: visa1 address
            temp = []
            temp.append('Visa 1 Address:')
            temp.append(str(self.ui.visa1.text()))
            comments.append(temp)
            # Line 5: visa2 address
            temp = []
            temp.append('Visa 2 Address:')
            temp.append(str(self.ui.visa2.text()))
            comments.append(temp)
            # Line 6: visa1 name
            temp = []
            temp.append('Visa 1 Name:')
            visa1_name = self.visa1_name.rstrip('\n')
            visa1_name = visa1_name.replace(',', ' ')
            temp.append(str(visa1_name))
            comments.append(temp)
            # Line 7: visa2 name
            temp = []
            temp.append('Visa 2 Name:')
            visa2_name = self.visa2_name.rstrip('\n')
            visa2_name = visa2_name.replace(',', ' ')
            temp.append(str(visa2_name))
            comments.append(temp)
            # Line 8: scan source
            temp = []
            temp.append('Scan Source:')
            temp.append('Voltage')
            comments.append(temp)
            # Line 9: time step
            temp = []
            temp.append('Time Step(sec):')
            temp.append(str(self.timeStep))
            comments.append(temp)
            # Line 10: comments
            temp = []
            temp.append('Comments:')
            temp.append(str(self.ui.textEdit_comment_G_ay.toPlainText()))
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
            temp = []
            for i in range(0, len(self.y_plot)):
                temp.append(i)
            data.append(temp)
            parameters.append('Array')
            units.append('1')
            data.append(self.x_value)
            parameters.append('Voltage')
            units.append('Volts')
            data.append(self.x_plot)
            parameters.append('Current')
            units.append('Amps')
            data.append(self.y_plot)
            
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
            self.ui.pushButton_Open_O_ay.setEnabled(True)
            self.ui.label_condition_O_ay.setText('File has been saved.')
    
    def G_open(self):
        opendir = self.G_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)
        
    def O_open(self):
        opendir = self.O_directory
        open_path = 'explorer "' + opendir + '"'
        subprocess.Popen(open_path)

class CollectData(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.exiting = False
    
    def input(self, ui, visa_chosen1, visa_chosen2, Array, timeStep, curve, curve_vt, curve_ct, dataX, dataVol, dataCurr):
        self.ui = ui
        self.visa_chosen1 = visa_chosen1
        self.visa_chosen2 = visa_chosen2
        self.Array = Array
        
        self.curve = curve
        self.curve_vt = curve_vt
        self.curve_ct = curve_ct
        
        self.dataX = dataX
        self.dataVol = dataVol
        self.dataCurr = dataCurr
        
        self.timeStep = timeStep
        
        self.date_value = []
        self.t_value = []
        self.pauseLoop = False
        self.stopLoop = False
        self.track = 0
        if len(self.dataX) > 0:
            self.i = self.dataX[-1] + 1
        else:
            self.i = 0
        self.start()
    
    def run(self):
        start_time = time.time()
        while not self.stopLoop:
            if (self.timeStep > 0) and (self.pauseLoop == False):
                if self.track < len(self.Array):
                    curr = self.Array[self.track]/1000000
                    self.visa_chosen1.write('SOUR:LEV:AUTO ' + str(curr))
                    vol = float(self.visa_chosen2.ask('MEAS:VOLT?'))
                   
                    self.dataVol.append(vol)
                    self.dataCurr.append(curr)
                    self.dataX.append(self.i)
                    
                    self.curve.set_data(self.dataCurr, self.dataVol)
                    self.curve_vt.set_data(self.dataX, self.dataVol)
                    self.curve_ct.set_data(self.dataX, self.dataCurr)
                    
                    self.emit(SIGNAL("plot"))
                    
                    end_time = time.time()
                    self.t_value.append(end_time - start_time)
                    now = datetime.datetime.now()
                    date = '%s-%s-%s' % (now.year, now.month, now.day)
                    current_time = '%s:%s:%s' % (now.hour, now.minute, now.second)
                    date_and_time = date + ' ' + current_time
                    self.date_value.append(date_and_time)
                    
                    self.i += 1
                    self.track += 1
                    time.sleep(self.timeStep)
                else:
                    self.emit(SIGNAL("stop"))
        self.visa_chosen1.write('OUTP OFF')
    
    def stop(self):
        self.pauseLoop = True
        self.stopLoop = True
        self.pauseLoop = False
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.timeStepValue.setEnabled(True)
        self.ui.output.setText("Stopped")
        self.ui.startButton.setText("Start")
        self.Array = []
        self.track = 0
        if len(self.dataVol) > 0:
            y_plot = self.dataVol
            x_plot = self.dataCurr
            date_value = self.date_value
            t_value = self.t_value
            self.emit(SIGNAL("analyse"),date_value, t_value, x_plot, y_plot)
    
    def pause(self):
        if self.pauseLoop == True:
            self.pauseLoop = False
            self.ui.startButton.setText("Pause")
            self.ui.output.setText("Running")
        else:
            self.pauseLoop = True
            self.ui.startButton.setText("Continue")
            self.ui.output.setText("Paused")
            if len(self.dataVol) > 0:
                y_plot = self.dataVol
                x_plot = self.dataCurr
                date_value = self.date_value
                t_value = self.t_value
                self.emit(SIGNAL("analyse"),date_value, t_value, x_plot, y_plot)
            
    def __del__(self):
        self.exiting = True
        self.wait()