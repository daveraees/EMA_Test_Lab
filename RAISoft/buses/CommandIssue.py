import Queue
import threading


class DummyBus:
    def __init__(self):
        self.CMDqueue = Queue.Queue(1)    # arbitrary commnad queue
        self.CMDdaemon = threading.Thread(target=self._issueRoutine, name='Command Issue Routine')
        self.CMDdaemon.setDaemon(True)
        self.CMDdaemon.start()
        self.OUTqueue = Queue.Queue(1)    # returned messages queue
        return
    def close(self):
        self.CMDqueue.join()
        return
    def _issueRoutine(self):    
        " daemon for commiting commands in commnad queue:"
        while True:
            task = self.CMDqueue.get()
            if not task == None:
                command = task[0]
                params = task[1]
                if not command == None:
                    if params == None:
                        command()
                    else:
                        command(params)
                    pass
            self.CMDqueue.task_done()
        return
