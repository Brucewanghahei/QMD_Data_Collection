""" To compile the .ui file created with Qt Designer into a  Python file do the following:
    1. Open Command Prompt and change the directory, using "chdir" command, to the directory that contains the .ui file
    2. Type: pyuic4 example.ui>example.py
      (use your .ui name instead of example above)
    3. That is all there is to ipt. Now there is python module "example.py"  with all the code from the .ui file that one can import
    4. Do not change any of the code in the new "example.py" file because recompiling any new changed in the .ui file will delete your changes
    C:\Users\QMDla\Documents\Python Scripts\04 Array Builder\v3.2\Sub_Scripts pyuic4 GUI.ui>GUI.py"""
    
# This is very important because it imports the GUI created earlier using Qt Designer
# To import the GUI from another python file, it is very simple. Just following the following steps:
# 1. Creat an empty file called __init__.py in the same directory as the GUI file
# 2. If the GUI file and __init__.py file are in the same directory as this file, just type "from .GUIfilename import classname"
# 3. If the GUI file and __init__.py file are in the sub file of this file, then type "from subfilename.GUIfilename.GUIfilename import classname"
# classname is the name of the class in the GUI file, usually it should be 'Ui_MainWindow'

from Sub_Scripts.GUI import Ui_MainWindow

from Tabs.Keithley import Keithley
from Tabs.Agilent_Yokogawa import Agilent_Yokogawa
from Tabs.Array_Builder import Array_Builder
from Tabs.Resonance_Sweep import Resonance_Sweep
from Tabs.Lock_In import Lock_In

# Import numpy library
import numpy
import os
import sys
import datetime
import visa
import math

# Adding navigation toolbar to the figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# This class controls all the operations of the GUI. This is the main class that contains all the functions that control the GUI.
class MyForm(QMainWindow):
    
    # The __init__ function is what everything the user wants to be initialized when the class is called.
    # Here we shall define the tring functions to corresponding variables.
    # The 'self' variable means that the function is part of the class and can be called inside and outside the class.
    def __init__(self, parent = None):
        
        # Standard GUI code
        QWidget.__init__(self, parent)
        
        # All the GUI data and widgets in the Ui_MainWindow() class is defined to "self.ui"
        # Thus to do anything on the GUI, the commands must go through this variable
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # For the canvas.
        self.canvas_general = FigureCanvas(self.ui.mplwidget_general.figure)
        self.canvas_general.setParent(self.ui.widget_general)
        # We need the toolbar widget for the canvas
        self.mpl_toolbar_general = NavigationToolbar(self.canvas_general, self.ui.widget_general)
        
        self.canvas_import = FigureCanvas(self.ui.mplwidget_import.figure)
        self.canvas_import.setParent(self.ui.widget_import)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_import = NavigationToolbar(self.canvas_import, self.ui.widget_import)
        
        self.canvas_analysis = FigureCanvas(self.ui.mplwidget_analysis.figure)
        self.canvas_analysis.setParent(self.ui.widget_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_analysis = NavigationToolbar(self.canvas_analysis, self.ui.widget_analysis)
        
        self.canvas_ct_analysis = FigureCanvas(self.ui.mplwidget_ct_analysis.figure)
        self.canvas_ct_analysis.setParent(self.ui.widget_ct_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_ct_analysis = NavigationToolbar(self.canvas_ct_analysis, self.ui.widget_ct_analysis)
        
        self.canvas_vt_analysis = FigureCanvas(self.ui.mplwidget_vt_analysis.figure)
        self.canvas_vt_analysis.setParent(self.ui.widget_vt_analysis)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_vt_analysis = NavigationToolbar(self.canvas_vt_analysis, self.ui.widget_vt_analysis)
        
        # Create the QVBoxLayout object and add the widget into the layout
        vbox_general = QVBoxLayout()
        # The matplotlib canvas
        vbox_general.addWidget(self.canvas_general)
        # The matplotlib toolbar
        vbox_general.addWidget(self.mpl_toolbar_general)
        self.ui.widget_general.setLayout(vbox_general)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_import = QVBoxLayout()
        # The matplotlib canvas
        vbox_import.addWidget(self.canvas_import)
        # The matplotlib toolbar
        vbox_import.addWidget(self.mpl_toolbar_import)
        self.ui.widget_import.setLayout(vbox_import)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_analysis.addWidget(self.canvas_analysis)
        # The matplotlib toolbar
        vbox_analysis.addWidget(self.mpl_toolbar_analysis)
        self.ui.widget_analysis.setLayout(vbox_analysis)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_ct_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_ct_analysis.addWidget(self.canvas_ct_analysis)
        # The matplotlib toolbar
        vbox_ct_analysis.addWidget(self.mpl_toolbar_ct_analysis)
        self.ui.widget_ct_analysis.setLayout(vbox_ct_analysis)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_vt_analysis = QVBoxLayout()
        # The matplotlib canvas
        vbox_vt_analysis.addWidget(self.canvas_vt_analysis)
        # The matplotlib toolbar
        vbox_vt_analysis.addWidget(self.mpl_toolbar_vt_analysis)
        self.ui.widget_vt_analysis.setLayout(vbox_vt_analysis)
        
        # Connect the mplwidget with canvas
        self.ui.mplwidget_general = self.canvas_general
        self.ui.mplwidget_import = self.canvas_import
        self.ui.mplwidget_analysis = self.canvas_analysis
        self.ui.mplwidget_ct_analysis = self.canvas_ct_analysis
        self.ui.mplwidget_vt_analysis = self.canvas_vt_analysis
        
        self.connect(self.ui.actionArray_Builder, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(0))
        self.connect(self.ui.actionKeithley_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(1))
        self.connect(self.ui.actionAgilent_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(2))
        self.connect(self.ui.actionLockIn_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(3))
        self.connect(self.ui.actionResonant_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(4))
        
        self.Array_Builder_programs = Array_Builder(main = self, ui = self.ui)
        # Connect buttons in the General Array tab
        # self.connect(self.ui.pushButton_plot, SIGNAL('clicked()'), self.Array_Builder_programs.Plot_general)
        # self.connect(self.ui.pushButton_clear, SIGNAL('clicked()'), self.Array_Builder_programs.Clear)
        # self.connect(self.ui.pushButton_save, SIGNAL('clicked()'), self.Array_Builder_programs.Save)
        # self.connect(self.ui.pushButton_browse_save, SIGNAL('clicked()'), self.Array_Builder_programs.Browse_save)
        
        self.Keithley_programs = Keithley(main = self, ui = self.ui)
        self.Keithley_programs.Refresh_visa()
        # Connect buttons in the Keithely tab
        # self.connect(self.ui.pushButton_browse_keithley, SIGNAL('clicked()'), self.Keithley_programs.Browse_keithley)
        # self.connect(self.ui.pushButton_import_keithley, SIGNAL('clicked()'), self.Keithley_programs.Import_keithley)
        # self.connect(self.ui.pushButton_close_keithley, SIGNAL('clicked()'), self.Keithley_programs.Close_keithley)
        # self.connect(self.ui.pushButton_select_keithley, SIGNAL('clicked()'), self.Keithley_programs.Select_keithley)
        # self.connect(self.ui.pushButton_scan_keithley, SIGNAL('clicked()'), self.Keithley_programs.Scan_keithley)
        # self.connect(self.ui.pushButton_pause_keithley, SIGNAL('clicked()'), self.Keithley_programs.collect_data_thread.pause)       
        # self.connect(self.ui.pushButton_stop_keithley, SIGNAL('clicked()'), self.Keithley_programs.collect_data_thread.stop)
        # self.connect(self.ui.pushButton_clear_keithley, SIGNAL('clicked()'), self.Keithley_programs.collect_data_thread.Clear_keithley)
        # self.connect(self.ui.pushButton_copy_keithley, SIGNAL('clicked()'), self.CopyData)
        # self.connect(self.ui.pushButton_fit_keithley, SIGNAL('clicked()'), self.Keithley_programs.collect_data_thread.Fit)
        # self.connect(self.ui.radioButton_voltage_keithley, SIGNAL("clicked()"), lambda : self.ui.tabWidget_scan_keithley.setCurrentIndex(0))
        # self.connect(self.ui.radioButton_timescan_keithley, SIGNAL("clicked()"), self.Keithley_programs.collect_data_thread.Pre_MPL_Plot)
        # self.connect(self.ui.radioButton_stepscan_keithley, SIGNAL("clicked()"), self.Keithley_programs.collect_data_thread.Pre_MPL_Plot)
        # self.connect(self.Keithley_programs.collect_data_thread, SIGNAL("plot"), self.Keithley_programs.Plot_data)
        # self.connect(self.Keithley_programs.collect_data_thread, SIGNAL("mpl_plot"), self.Keithley_programs.Plot_analysis)
        # self.connect(self.Keithley_programs.collect_data_thread, SIGNAL("data_available"), self.Keithley_programs.Pre_save)
        # self.connect(self.Keithley_programs.collect_data_thread, SIGNAL("clear_plot"), self.Keithley_programs.Clear_plot)
        
        self.Values = []
        self.Step = []
        self.Peak = []
        self.round = 0
        self.new_start = 0
        
        self.ui.lineEdit_directory_save.setText(os.getcwd())
        
        #Agilent_Yokogawa
        self.canvas_import_ay = FigureCanvas(self.ui.mplwidget_import_ay.figure)
        self.canvas_import_ay.setParent(self.ui.widget_import_ay)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_import_ay = NavigationToolbar(self.canvas_import_ay, self.ui.widget_import_ay)
        
        #Agilent_Yokogawa
        self.canvas_analysis_ay = FigureCanvas(self.ui.mplwidget_analysis_ay.figure)
        self.canvas_analysis_ay.setParent(self.ui.widget_analysis_ay)
        # This is the toolbar widget for the import canvas
        self.mpl_toolbar_analysis_ay = NavigationToolbar(self.canvas_analysis_ay, self.ui.widget_analysis_ay)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_import_ay = QVBoxLayout()
        # The matplotlib canvas
        vbox_import_ay.addWidget(self.canvas_import_ay)
        # The matplotlib toolbar
        vbox_import_ay.addWidget(self.mpl_toolbar_import_ay)
        self.ui.widget_import_ay.setLayout(vbox_import_ay)
        
        # Create the QVBoxLayout object and add the widget into the Layout
        vbox_analysis_ay = QVBoxLayout()
        # The matplotlib canvas
        vbox_analysis_ay.addWidget(self.canvas_analysis_ay)
        # The matplotlib toolbar
        vbox_analysis_ay.addWidget(self.mpl_toolbar_analysis_ay)
        self.ui.widget_analysis_ay.setLayout(vbox_analysis_ay)
        
        # Connect the mplwidget with canvass
        self.ui.mplwidget_import_ay = self.canvas_import_ay
        self.ui.mplwidget_analysis_ay = self.canvas_analysis_ay
        
        # Connect buttons in the Agilent Yokogawa tab
        self.Agilent_Yokogawa_programs = Agilent_Yokogawa(self.ui)
        
        self.connect(self.ui.startButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.start)
        self.connect(self.ui.stopButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.stop)
        #self.connect(self.action_timer, SIGNAL("timeout()"), self.Agilent_Yokogawa_programs.action)

        self.connect(self.ui.pushButton_browse_ay, SIGNAL('clicked()'), self.Agilent_Yokogawa_programs.Browse_ay)
        self.connect(self.ui.pushButton_import_ay, SIGNAL('clicked()'), self.Agilent_Yokogawa_programs.Import_ay)
        self.connect(self.ui.pushButton_copy_ay, SIGNAL('clicked()'), self.Copy_ay)
        self.connect(self.ui.selectVisaButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.select_visa)
        self.connect(self.ui.updateVisaButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.update_visa)
        self.connect(self.ui.closeVisaButton0, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.close_visa0)
        self.connect(self.ui.closeVisaButton1, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.close_visa1)
        self.connect(self.Agilent_Yokogawa_programs.collectDataThread, SIGNAL("plot"), self.Agilent_Yokogawa_programs.plotData)
        self.connect(self.Agilent_Yokogawa_programs.collectDataThread, SIGNAL("analyse"), self.Agilent_Yokogawa_programs.analyse)
        
        self.connect(self.ui.browseButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.browse)
        self.connect(self.ui.saveButton, SIGNAL("clicked()"), self.Agilent_Yokogawa_programs.save)
        
        self.ui.mplwidget_analysis_ay.figure.canvas.mpl_connect('button_release_event', self.Agilent_Yokogawa_programs.slope)
        
        #Connects the buttons in the Resonant Sweeper Tab
        #self.Resonant_programs = Resonance_Sweep(main = self, ui = self.ui)
        self.Resonant_Sweeper_functions = Resonance_Sweep(main = self, ui = self.ui)
        
        self.Resonant_Sweeper_functions.update_visa()
        self.connect(self.ui.pushButtonSelectRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.choose_visa)
        self.connect(self.ui.pushButtonUpdateRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.update_visa)
        self.connect(self.ui.pushButtonSourceSelectRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.choose_visa)
        self.connect(self.ui.pushButtonSourceUpdateRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.update_visa)
        self.connect(self.ui.pushButtonStartRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.start)
        self.connect(self.ui.pushButtonStopRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.stop)
        self.connect(self.ui.pushButtonPauseRS, SIGNAL("clicked()"), self.Resonant_Sweeper_functions.collectDataThread.pause)
        self.connect(self.Resonant_Sweeper_functions.collectDataThread, SIGNAL("plot"), self.Resonant_Sweeper_functions.plotData)
        self.connect(self.Resonant_Sweeper_functions.collectDataThread, SIGNAL("stop"), self.Resonant_Sweeper_functions.stop)
        
        #Connects the buttons in the Lock-In Program Tab
        self.Lock_In_programs = Lock_In(main = self, ui = self.ui)
        self.connect(self.ui.pushButtonSelectLI, SIGNAL("clicked()"), self.Lock_In_programs.choose_visa)
        self.connect(self.ui.pushButtonUpdateLI, SIGNAL("clicked()"), self.Lock_In_programs.update_visa)
        self.connect(self.ui.pushButtonStartLI, SIGNAL("clicked()"), self.Lock_In_programs.start)
        self.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.Lock_In_programs.stop)
        self.connect(self.ui.pushButtonStopLI, SIGNAL("clicked()"), self.Lock_In_programs.final_append)
        self.connect(self.ui.pushButtonPauseLI, SIGNAL("clicked()"), self.Lock_In_programs.append_parameters)
        self.connect(self.ui.pushButtonPauseLI, SIGNAL("clicked()"), self.Lock_In_programs.collectDataThread.pause)
        self.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.Lock_In_programs.collectDataThread.appendSessionData)
        self.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.Lock_In_programs.collectDataThread.appendSessionData)
        self.connect(self.ui.pushButtonPauseLI, SIGNAL('clicked()'), self.Lock_In_programs.tableAppend)
        self.connect(self.ui.pushButtonStopLI, SIGNAL('clicked()'), self.Lock_In_programs.tableAppend)

        
        self.connect(self.ui.pushButtonSaveLI, SIGNAL('clicked()'), self.Lock_In_programs.save)
        self.connect(self.ui.pushButtonBrowseLI, SIGNAL('clicked()'), self.Lock_In_programs.browse)
        self.connect(self.ui.pushButtonFolderSelectLI, SIGNAL('clicked()'), self.Lock_In_programs.select_name)
                     
        self.connect(self.ui.radioButtonDateTimeLI, SIGNAL('clicked()'), self.Lock_In_programs.save_name)
        self.connect(self.ui.radioButtonCustomLI, SIGNAL('clicked()'), self.Lock_In_programs.save_name)
                     
        self.connect(self.ui.radioButton_csvLI, SIGNAL('clicked()'), self.Lock_In_programs.save_type)
        self.connect(self.ui.radioButton_txtLI, SIGNAL('clicked()'), self.Lock_In_programs.save_type)
        
        self.connect(self.Lock_In_programs.collectDataThread, SIGNAL("plot"), self.Lock_In_programs.plotData)
        self.connect(self.Lock_In_programs.collectDataThread, SIGNAL("Begin_Save"), self.Lock_In_programs.pre_save)
        
    # This method is to transfer the array data from the Array Builder tab to the Keithley tab
    # If the array is valid, data_available is true and execute the data transfer
    # If the array is not valid, execution cannot be done
    def CopyDataFunc(self):
        if self.Array_Builder_programs.data_available == True:
            return self.Array_Builder_programs.Values
        else:
            return None
    
    def Copy_ay(self):
        try:
            #self.Array_Builder_programs.data_available == True:
            self.Agilent_Yokogawa_programs.Copy_ay(self.Array_Builder_programs.Values)
            self.ui.output.setText('Array has been copied and plotted.')
        except:
            self.ui.output.setText('No valid array to copy.')
    
    # Make sure the user is going to quit the program
    def closeEvent(self, event):
        quit_msg = "Do you want to quit the program?"
        reply = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
if __name__ == "__main__":
    # To open the GUI
    app = QApplication(sys.argv)
    myapp = MyForm()
    
    # It shows the GUI
    myapp.show()
    
    # Exit the GUI when "x" button is clicked
    sys.exit(app.exec_()) 
        
