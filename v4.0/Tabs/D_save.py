# Import the PyQt4 modules for all the commands that control the GUI.
# Importing as from "Module" import 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os

class Dynamic_Save_Thread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        
    def input(self, comments, parameters, units, data, file_info, is_first, is_last):
        self.comments = comments
        self.parameters = parameters
        self.units = units
        self.data = data
        self.file_info = file_info
        self.is_first = is_first
        self.is_last = is_last
        self.start()
    
    def run(self):
        f_name = self.file_info[4] + '\\' + self.file_info[0] + self.file_info[1]

        if not self.is_last:
            if self.is_first:
                # Create a folder at this address
                if not os.path.isdir(self.file_info[4]):
                    os.makedirs(self.file_info[4])
            
                f = open(f_name, 'a')
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
                
                for i in range(0, len(self.data) - 1):
                    f.write(str(self.data[i]) + self.file_info[2])
                f.write(str(self.data[len(self.data) - 1]) + '\n')
            else:
                f = open(f_name, 'a')
                for i in range(0, len(self.data) - 1):
                    f.write(str(self.data[i]) + self.file_info[2])
                f.write(str(self.data[len(self.data) - 1]) + '\n')
        else:
            f = open(f_name, 'a')
            f.close()
                
    def __del__(self):
        self.exiting = True
        self.wait()