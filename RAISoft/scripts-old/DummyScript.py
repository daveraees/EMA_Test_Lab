

#begin
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 20:
    Stopwatch.Wait(0.1)
    Line.Measure()
    datagram.add_data()
    DataStore.writeData()
    DataStore.writeSeparator()

#end
