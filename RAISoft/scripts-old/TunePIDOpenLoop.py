# Script for estimation of the Constants of the PID regulation
# by transinent probing of the system up and down withouth feedback

PowerSource.set_output_on()
PowerSource.set_volts(2.0)
Stopwatch.Wait(1)
PowerSource.Measure()
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 3600:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.01)
        Stopwatch.Measure()
        Platinum.Measure()
        Thermocouple.Measure()
        datagram.add_data()
        DataStore.writeData()

PowerSource.set_volts(2.5)
PowerSource.Measure()
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 3600:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.01)
        Stopwatch.Measure()
        Platinum.Measure()
        Thermocouple.Measure()
        datagram.add_data()
        DataStore.writeData()

PowerSource.set_volts(2.0)
PowerSource.Measure()
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 3600:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.01)
        Stopwatch.Measure()
        Platinum.Measure()
        Thermocouple.Measure()
        datagram.add_data()
        DataStore.writeData()
