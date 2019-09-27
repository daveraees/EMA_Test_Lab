#DMMtest.py

Stopwatch.zeroTimer()
for voltage in range(20):
    Electrometer.set_volts( (-1)*voltage )
    Stopwatch.Wait(0)
    Stopwatch.Measure()
    Electrometer.Measure()
    datagram.add_data()
    DataStore.writeData()
