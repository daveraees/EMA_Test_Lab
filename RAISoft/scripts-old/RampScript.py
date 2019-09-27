

PeltierP.set_PID_params(Kp=2310.42, Ti=5.18, Td=0.77, looptime=0.1)

setpoint = 0.030
PeltierP.setNew_setpoint(value=setpoint, tolerance=0.0002, evalPeriod=30)
PeltierP.startRegulation()
PeltierP.waitForSetpoint()

#start ramping the temperature
step = 0.005
rampTime = 300.0  # time of ramp in seconds
PeltierP.linRamp(difference=step, duration=rampTime)

Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < rampTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.1)
        Stopwatch.Measure()
        Platinum.Measure()
        PeltierP.Measure()
        datagram.add_data()
        DataStore.writeData()

PeltierP.setNew_setpoint(value=0.030, tolerance=0.0002, evalPeriod=180)
Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 300:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.1)
        Stopwatch.Measure()
        Platinum.Measure()
        PeltierP.Measure()
        datagram.add_data()
        DataStore.writeData()
