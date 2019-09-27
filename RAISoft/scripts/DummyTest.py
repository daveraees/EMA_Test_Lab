
# project libraries imports:
# instruments:
from instruments.DummyMeter import GeneratorLine
from instruments.TimeMeter import MainTimerClass
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
def Test(slopeList, acquizDelay=0.1, acquizTime=6):
    Stopwatch = MainTimerClass()
    Stopwatch.Activate()
    
    Line = GeneratorLine()
    Line.Activate()
    
    
    # dont forget to activate the instruments before opening the output file:
    Data = OutputHandler()
    Data.setDataFileName()
    
    for slope in slopeList:
        intercept = slope / 10.0
        Data.analysis.mark_from()
        #begin DATA ACQUISITION script here:
        print 'starteing data generation. Slope>', slope, 'intercept:', intercept 
        Stopwatch.zeroTimer()
        while Stopwatch.getSinceLastZeroed() < 1.2:
            Stopwatch.Wait(0.1)
            Stopwatch.Measure()
            Line.Measure(slope, intercept)
            Data.acquireData()
        print 'data gen finished, starting analysis'
        Data.analysis.mark_to()
        print 'analysing data in range', Data.analysis.get_markers()
        print 'average:', Data.analysis.average_marked("U(V)")
        print 'average last 10 points:', Data.analysis.average_last('U(V)',10)
        print 'linear regression:', Data.analysis.linear_regres_marked("time(s)", "U(V)")

    
