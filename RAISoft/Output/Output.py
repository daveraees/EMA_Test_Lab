# this module integrates classes for data handling and storage


from Datagram import MainData 
from OutputFile import OutputFileHandler
from RAISoft.instruments.ActiveDevicesList import devList
from DataAnalysis import Analysis
import time
import os
from sys import argv

class OutputHandler:
    """ Combines the function of 
        - datagram : projects main data structure
        - datafile : the file with sored measurement results
        - online data evaluation and analysis
        - and possibly graphical output
     """
    def __init__(self):
        self.deviceList = devList.list() # list of currently activated devices
        self.datagram = MainData(self.deviceList) # create the main data structure
        self.analysis = Analysis(self.datagram)    # initiate the analysis module
        return
    def setDataFileName(self, filename=''):
        if filename == '':
            # obtain the data filename from commandline argument (first after the script name)
            self.dataFileName = argv[1] 
        else:
            self.dataFileName = filename
        #initialize the output file:
        self.outputFile = OutputFileHandler(self.datagram, self.dataFileName)
    def acquireData(self):
        self.datagram.add_data()
        self.outputFile.writeData()
    def separateData(self):
        self.outputFile.writeSeparator()
        return
    def report(self, message, file='report.info'):
        workingDir = os.path.dirname(self.dataFileName)
        filename = os.path.join(workingDir,file)
        date = time.asctime(time.localtime())
        message = ('%(date)s: %(message)s \n' % \
                {'date':date, 'message':message})
        print message,
        f = open(filename, 'a')
        f.write(message)
        f.close()
        return

