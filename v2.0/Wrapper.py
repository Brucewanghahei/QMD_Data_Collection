# This is very important because it imports the GUI created earlier using Qt Designer
# To import the GUI from another python file, it is very somple. Just following the following steps:
# 1. Creat an empty file called __init__.py in the same directory as the GUI file
# 2. If the GUI file and __init__.py file are in the same directory as this file, just type "from .GUIfilename import classname"
# 3. If the GUI file and __init__.py file are in the sub file of this file, then type "from subfilename.GUIfilename.GUIfilename import classname"
# classname is the name of the class in the GUI file, usually it should be 'Ui_MainWindow'

from Sub_Scripts.GUI import Ui_MainWindow

from Array_Builder.Keithley import Keithley
from Array_Builder.General import General

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
        
        self.canvas_scan = FigureCanvas(self.ui.mplwidget_scan.figure)
        self.canvas_scan.setParent(self.ui.widget_scan)
        # This is the toolbar widget for the scan canvas
        self.mpl_toolbar_scan = NavigationToolbar(self.canvas_scan, self.ui.widget_scan)
        
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
        vbox_scan = QVBoxLayout()
        # The matplotlib canvas
        vbox_scan.addWidget(self.canvas_scan)
        # The matplotlib toolbar
        vbox_scan.addWidget(self.mpl_toolbar_scan)
        self.ui.widget_scan.setLayout(vbox_scan)
        
        # Connect the mplwidget with canvas
        self.ui.mplwidget_general = self.canvas_general
        self.ui.mplwidget_import = self.canvas_import
        self.ui.mplwidget_scan = self.canvas_scan
        
        self.General_programs = General(self.ui)
        # Connect buttons in the General Array tab
        self.connect(self.ui.pushButton_plot, SIGNAL('clicked()'), self.General_programs.Plot_general)
        self.connect(self.ui.pushButton_clear, SIGNAL('clicked()'), self.General_programs.Clear)
        self.connect(self.ui.pushButton_save, SIGNAL('clicked()'), self.General_programs.Save)
        self.connect(self.ui.pushButton_browse_save, SIGNAL('clicked()'), self.General_programs.Browse_save)
        
        self.Keithley_programs = Keithley(self.ui)
        self.Keithley_programs.Refresh_visa()
        # Connect buttons in the Keithely tab
        self.connect(self.ui.pushButton_browse_keithley, SIGNAL('clicked()'), self.Keithley_programs.Browse_keithley)
        self.connect(self.ui.pushButton_import_keithley, SIGNAL('clicked()'), self.Keithley_programs.Import_keithley)
        self.connect(self.ui.pushButton_close_keithley, SIGNAL('clicked()'), self.Keithley_programs.Close_keithley)
        self.connect(self.ui.pushButton_select_keithley, SIGNAL('clicked()'), self.Keithley_programs.Select_keithley)
        self.connect(self.ui.pushButton_scan_keithley, SIGNAL('clicked()'), self.Keithley_programs.Scan_keithley)
        self.connect(self.ui.pushButton_stop_keithley, SIGNAL('clicked()'), self.Keithley_programs.Stop_keithley)
        self.connect(self.ui.pushButton_clear_keithley, SIGNAL('clicked()'), self.Keithley_programs.Clear_keithley)
        
        self.Values = []
        self.Step = []
        self.Peak = []
        self.round = 0
        self.new_start = 0
        
        self.ui.lineEdit_directory_save.setText(os.getcwd())

    # Make sure the user is going to quit the program
    def closeEvent(self, event):
        quit_msg = "DO you want to quit the program?"
        reply = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            question.accept()
        else:
            question.ignore()
    
if __name__ == "__main__":
    # To open the GUI
    app = QApplication(sys.argv)
    myapp = MyForm()
    
    # It shows the GUI
    myapp.show()
    
    # Exit the GUI when "x" button is clicked
    sys.exit(app.exec_()) 
        
