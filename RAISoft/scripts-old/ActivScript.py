# Script for measurement of activation energies of the DC conductivity
# by measurement of CV characteristics at set of fixed temperatures

PeltierP.set_PID_params(Kp=10000, Ti=1.32, Td=0.33, looptime=0.1)
PeltierP.startRegulation()

Temperatures = range(20,65,5)
Temperatures.reverse()

for temperature in Temperatures:
    voltage = temperature / 1000.0
    PeltierP.setNew_setpoint(value=voltage, tolerance=0.0005, evalPeriod=300)
    PeltierP.waitForSetpoint()
    PeltierP.Measure()
    Stopwatch.Measure()
    SweeperV.Measure(start=1, stop=40, number=40, delay=5)
    Platinum.Measure()
    datagram.add_data()
    DataStore.writeData()
