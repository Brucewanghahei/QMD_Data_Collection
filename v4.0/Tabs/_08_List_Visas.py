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



class List_Visas():
        
    def __init__(self, main, ui):
        self.ui = ui
        self.rm = visa.ResourceManager()
        self.visa_names_thread = Visa_Name()
        self.collectNames()
        # Connect buttons in the General Array tab
        main.connect(self.ui.pushButtonV_update, SIGNAL('clicked()'), self.collectNames)
    
    def collectNames(self):
        self.visa_names_thread.input(self.ui)
        
class Visa_Name(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
    def input(self, ui):
        self.ui = ui
        self.ui.textEditV_list.clear()
        self.ui.textEditV_list.setReadOnly(True)
        self.rm = visa.ResourceManager()
        self.start()
    def run(self):
        visa_existed = False
        visas = self.rm.list_resources()
        for visa in visas:
            try:
                self.instr = self.rm.open_resource(visa)
                self.instr.timeout = 500
                name = self.instr.query("*IDN?")
                visa_existed = True
            except:
                name = "NA"
            self.ui.textEditV_list.insertPlainText(str(visa) + "\n" + str(name) + "\n\n")
        if visa_existed:
            self.instr.close()