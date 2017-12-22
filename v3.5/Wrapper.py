""" To compile the .ui file created with Qt Designer into a  Python file do the following:
    1. Open Command Prompt and change the directory, using "chdir" command, to the directory that contains the .ui file
    2. Type: pyuic4 example.ui>example.py
      (use your .ui name instead of example above)
    3. That is all there is to ipt. Now there is python module "example.py"  with all the code from the .ui file that one can import
    4. Do not change any of the code in the new "example.py" file because recompiling any new changed in the .ui file will delete your changes
    C:\Users\QMDla\Documents\Python Scripts\02 QMDLAB Data Collection\v3.4\Sub_Scripts pyuic4 GUI.ui>GUI.py"""
    
# This is very important because it imports the GUI created earlier using Qt Designer
# To import the GUI from another python file, it is very simple. Just following the following steps:
# 1. Creat an empty file called __init__.py in the same directory as the GUI file
# 2. If the GUI file and __init__.py file are in the same directory as this file, just type "from .GUIfilename import classname"
# 3. If the GUI file and __init__.py file are in the sub file of this file, then type "from subfilename.GUIfilename.GUIfilename import classname"
# classname is the name of the class in thre GUI file, usually it should be 'Ui_MainWindow'

from Sub_Scripts.GUI import Ui_MainWindow

from Tabs._01_Array_Builder import Array_Builder
from Tabs._02_Keithley import Keithley
from Tabs._03_Agilent_Yokogawa import Agilent_Yokogawa
#from Tabs._04_Keithley_Stepper import Keithley_Stepper
from Tabs._05_Keithley_GateSweep import KeithleyGateSweep
from Tabs._06_Lock_In import Lock_In
from Tabs._07_Resonance_Sweep import Resonance_Sweep
from Tabs._08_List_Visas import List_Visas


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
        
        # Create the QVBoxLayout object and add the widget into the layout
        vbox_general = QVBoxLayout()
        # The matplotlib canvas
        vbox_general.addWidget(self.canvas_general)
        # The matplotlib toolbar
        vbox_general.addWidget(self.mpl_toolbar_general)
        self.ui.widget_general.setLayout(vbox_general)
        
        # Connect the mplwidget with canvas
        self.ui.mplwidget_general = self.canvas_general
        
        self.connect(self.ui.actionArray_Builder, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(0))
        self.connect(self.ui.actionKeithley_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(1))
        self.connect(self.ui.actionAgilent_Single_scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(2))
        self.connect(self.ui.actionKeithley_Stepper_Single_Scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(3))
        self.connect(self.ui.actionKeithley_Gate_Sweep, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(4))
        self.connect(self.ui.actionLockIn_Single_Scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(5))
        self.connect(self.ui.actionResonant_Single_Scan, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(6))
        self.connect(self.ui.actionSee_Visa_List, SIGNAL('triggered()'), lambda : self.ui.stackedWidget.setCurrentIndex(7))
        
        self.List_Visas = List_Visas(main = self, ui = self.ui)
        self.Array_Builder_programs = Array_Builder(main = self, ui = self.ui)
        
        self.Keithley_programs = Keithley(main = self, ui = self.ui)
        self.Keithley_programs.Refresh_visa()
        
        self.Values = []
        self.Step = []
        self.Peak = []
        self.round = 0
        self.new_start = 0
        
        self.ui.lineEdit_directory_save.setText(os.getcwd())
        
        self.Agilent_Yokogawa_programs = Agilent_Yokogawa(main = self, ui = self.ui)
        
        self.Resonant_Sweeper_functions = Resonance_Sweep(main = self, ui = self.ui)
        
        self.Resonant_Sweeper_functions.update_visa()

        self.Lock_In_programs = Lock_In(main = self, ui = self.ui)
        
        self.KeithleyGateSweep = KeithleyGateSweep(main = self, ui = self.ui)
        
    # This method is to transfer the array data from the Array Builder tab to the Keithley tab
    # If the array is valid, data_available is true and execute the data transfer
    # If the array is not valid, execution cannot be done
    def CopyDataFunc(self):
        if self.Array_Builder_programs.data_available == True:
            return self.Array_Builder_programs.Values
        else:
            return None
    
    def copyData(self):
        try:
            if self.Array_Builder_programs.data_available:
                return self.Array_Builder_programs.Values
            self.ui.output.setText('Array has been copied and plotted.')
        except:
            return False
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