from TimeMeter import MainTimerClass
from DummyMeter import GeneratorLine 


class Clock(MainTimerClass):
    def __init__(self):
        MainTimerClass.__init__(self)
        return
    
class Line(GeneratorLine):
    def __init__(self):
        GeneratorLine.__init__(self)
        return