# The classes for driving the data saving
from Buses import SimpleWriteFileDevice
from csv import writer
from numpy import array, vstack, hstack


class OutputFileHandler(SimpleWriteFileDevice):
    datagram = None
    header = []
    def __init__(self, datagram, filename=None):
        SimpleWriteFileDevice.__init__(self, filename)
        self.headerDenominator = '#'
        self.dataSeparator = ' '
        self.blockSeparator = '\n'
        self.spreadsheet = writer(self.f, delimiter=self.dataSeparator)
        self.datagram = datagram
        self.header = self._writeHeader()
        return
    def _writeHeader(self):
        header = self.datagram.extract_header()
        header.sort(cmp=None, key=None, reverse=False)    # optionly make the sorting of the file structure
        self.f.write(self.headerDenominator)
        self.spreadsheet.writerow(header)
        return header
    def writeData(self):
        data = self.datagram.extractLastReading() 
        #print data
        dataArray = None
        #print self.header
        for key in self.header:    # form a single array from the last reading ordered exactly like the header
            #print 'datakey:', key
            if dataArray == None:
                dataArray = data[key]
            else:
                dataArray = vstack((dataArray, data[key]))
      
        collumns = dataArray.shape[1]
        for row in range(collumns):
            slice = dataArray[:,row]
            self.spreadsheet.writerow(slice)
        
        self.flushBuffer()
        return
    def writeSeparator(self):
        self.f.write(self.blockSeparator)
        self._writeHeader()
        return

 
