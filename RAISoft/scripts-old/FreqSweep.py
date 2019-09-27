from numpy import logspace

for logFreq in logspace(1.7,6.7,40):
    frequency = logFreq
    LCR.setFreq(frequency)
    Stopwatch.Wait(1)
    Stopwatch.Measure()
    LCR.Measure()
    datagram.add_data()
    DataStore.writeData()