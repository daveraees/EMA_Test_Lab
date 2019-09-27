# Classes for handling the communication
"""    
The classes can be tested by following commands:

        wrt = SimpleWriteFileDevice()
        red = SimpleReadFileDevice()
        
        for i in range(1000):
            message = 'Hello I am No. ', i
            wrt.write_string(message)
        print red.read_string(0)
        
        red.close()
        wrt.close()
"""
# major libs imports:
import threading
import Queue


class DummyStringBus:
    def __init__(self):
        self.writebuffer = Queue.Queue(1000)
        self.readbuffer = Queue.Queue(1000)
        self.writeDaemon = threading.Thread(target=self._write_string, name='writeStringDaemon')
        self.writeDaemon.setDaemon(True)
        self.writeDaemon.start()
        self.readDaemon = threading.Thread(target=self._read_string, name='readStringDaemon')
        self.readDaemon.setDaemon(True)
        self.readDaemon.start()
        self.CMDqueue = Queue.Queue(1)    # arbitrary commnad queue
        self.CMDdaemon = threading.Thread(target=self._issueRoutine, name='Command Issue Routine')
        self.CMDdaemon.setDaemon(True)
        self.CMDdaemon.start()
        self.OUTqueue = Queue.Queue(1)    # returned messages queue
        return
    def close(self):
        raise NotImplementedError
    def _write_string(self):
        pass
    def _read_string(self):
        pass
    def _issueRoutine(self):    
        " daemon for commiting commands in commnad queue:"
        while True:
            command = self.CMDqueue.get()
            if not command == None:
                command()
            self.CMDqueue.task_done()
        return
    

class SimpleFileDevice(DummyStringBus):
    filename = ''
    reading = ''
    def __init__(self, filename=None):
        DummyStringBus.__init__(self)
        if filename == None:
            filename = '/tmp/workfile'
        self.filename = filename
        self.f = open(self.filename, 'w')
        self.f.close()
        self.f = open(self.filename, 'r+')
        return
    def _write_string(self):
        while True:
            message = self.writebuffer.get()
            self.f.seek(0)
            self.f.write(message)
            self.f.write('\n') # always the message ends with newline
            self.writebuffer.task_done()

    def _read_string(self):
        while True:
            position = self.readbuffer.get()
            self.f.seek(position)
            self.reading = self.f.readline()
            self.readbuffer.task_done()
    
    def read_string(self, position):
        self.reading = ''
        self.readbuffer.put_nowait(position)
        self.readbuffer.join()
        return self.reading
    
    def write_string(self, message):
        self.writebuffer.put(str(message))
        return
    
    def close(self):
        self.readbuffer.join()
        self.writebuffer.join()
        self.f.close()
        return

class SimpleWriteFileDevice():
    filename = ''
    def __init__(self, filename=None):
        if filename == None:
            filename = '/tmp/workfile'
        self.filename = filename
        self.f = open(self.filename, 'w')
        return
    def write_string(self, message):
        self.f.write(message)
        self.f.write('\n')
        return
    def flushBuffer(self):
        self.f.flush()
    def close(self):
        self.f.close()
        return

class SimpleReadFileDevice(DummyStringBus):
    filename = ''
    reading = ''
    def __init__(self, filename=None):
        DummyStringBus.__init__(self)
        if filename == None:
            filename = '/tmp/workfile'
        self.filename = filename
        self.f = open(self.filename, 'r')
        return
    def _read_string(self):
        while True:
            position = self.readbuffer.get()
            self.f.seek(position)
            self.reading = self.f.readline()
            self.readbuffer.task_done()
    def read_string(self, position):
        self.reading = ''
        self.readbuffer.put_nowait(position)
        self.readbuffer.join()
        return self.reading
    def close(self):
        self.readbuffer.join()
        self.f.close()
        return



