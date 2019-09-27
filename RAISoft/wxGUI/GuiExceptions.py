import exceptions
class JobTerminationException(exceptions.Exception):
    def __init__(self):
        return
        
    def __str__(self):
        print "","Test was interrupted by user!"
    
def main():
    raise Expletive
    
if __name__=="__main__":
    try:
        main()
    except ImportError:
        print "Unable to import something..."
    except Exception, e:
        raise e
