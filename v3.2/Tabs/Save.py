# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os

class Save_Thread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
    
    # comments is the list that contains all the information you want to show before the data
    # To make file writing easier, comments is designed to be a two dimensional list.
    # Each sublist in comments is one single line when write the file.
    # For example the first line may be ["User Name: ", "Vannucci"], the second line may be ["Edit Time:", "2016-2-11 11:11:11"]
    # Store the measurement details in this list so that they can be shown before the data, such as visa name, time step
    # User's comments are also included in this list.
    
    # parameters is a list contains the name of the data values, for example ["Date and Time", "Array", "Voltages", "Current"]
    
    # units is a list contains the corresponding units of the parameters, for example ["String", "1", "Volts", "Amps"]
    
    # file_info is a list contains the information about this current file and the format is fixed.
    # First item is file name
    # Second item is file type (csv or txt), for example ".csv" ot ".txt"
    # Third item is the corresponding divide mark. For csv it is "," and for txt it is "\t"
    # Fourth item is the divider and it is set to be "Collected Data" for all saving files
    # Fifth item is the saving directory of the folder
    def input(self, comments, parameters, units, data, file_info):
        self.comments = comments
        self.parameters = parameters
        self.units = units
        self.data = data
        self.file_info = file_info
        self.start()
        
    def run(self):
        # Create a folder at this address
        if not os.path.isdir(self.file_info[4]):
            os.makedirs(self.file_info[4])
        f_name = self.file_info[4] + '\\' + self.file_info[0] + self.file_info[1]
        
        f = open(f_name, 'w')
        for i in range(0, len(self.comments)):
            for j in range(0, len(self.comments[i])):
                f.write(self.comments[i][j] + ' ')
            f.write('\n')
        
        f.write('\n')
        
        f.write(self.file_info[3] + '\n')
        
        for i in range(0, len(self.parameters) - 1):
            f.write(self.parameters[i] + self.file_info[2])
        f.write(self.parameters[len(self.parameters) - 1] + '\n')
        
        for i in range(0, len(self.units) - 1):
            f.write(self.units[i] + self.file_info[2])
        f.write(self.units[len(self.units) - 1] + '\n')
        
        for i in range(0, len(self.data[0])):
            for j in range(0, len(self.data) - 1):
                f.write(str(self.data[j][i]) + self.file_info[2])
            f.write(str(self.data[len(self.data) - 1][i]) + '\n')
            
        f.close()
        
    def __del__(self):
        self.exiting = True
        self.wait()