

#begin
piezo = PowerSource._get_volts()
shift = 0
while not (piezo <= 0):
    piezo = piezo - (shift / 50.0)
    PowerSource.set_volts(piezo)
    shift = shift + 1
    Stopwatch.Wait(0.2)
    Stopwatch.Measure()
    PowerSource.Measure()
    SweeperV.Measure(start=1e-4, stop=1e-3, number=6, delay=0.1)
    datagram.add_data()
    DataStore.writeData()

#end
