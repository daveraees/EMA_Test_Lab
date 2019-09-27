#!/usr/bin/python
# this is script meant to be executable file 
# allowing to perform measurments
# EXAMPLE file

# project libraries imports:
# instruments:
from instruments.DummyMeter import GeneratorLine
from instruments.TimeMeter import MainTimerClass
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

Line = GeneratorLine()
Line.Activate()


# dont forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName('test-01.dat')

Data.analysis.mark_from()
#begin DATA ACQUISITION script here:
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 5:
    Stopwatch.Wait(0.1)
    Stopwatch.Measure()
    Line.Measure()
    Data.acquireData()
#end

Data.analysis.mark_to()
#print Data.analysis.average_marked("U(V)")
print Data.analysis.linear_regres_marked("time(s)", "U(V)")

