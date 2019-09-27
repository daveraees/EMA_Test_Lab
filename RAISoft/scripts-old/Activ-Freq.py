# Script for measurement of activation energies of the AC conductivity
# by measurement of frequency-dependences at a set of fixed temperatures

PeltierP.set_PID_params(Kp=11000, Ti=1.32, Td=0.33, looptime=0.1)
PeltierP.startRegulation()

Temperatures = range(20,130,10)
Temperatures.reverse()

for temperature in Temperatures:
    voltage = temperature / 1000.0
    PeltierP.setNew_setpoint(value=voltage, tolerance=0.001, evalPeriod=300)
    PeltierP.waitForSetpoint()
    PeltierP.Measure()
    Stopwatch.Measure()
    LCR.Measure(fromFreq=50, toFreq=5e6, number=40)
    Platinum.Measure()
    datagram.add_data()
    DataStore.writeData()
