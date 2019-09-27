
# project libraries imports:
# instruments:
from instruments.Keithley import SM2602_sweepV
from instruments.Keithley import SM2602_channel
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
SweeperV = SM2602_sweepV('dualSmeter', channel='a')
SweeperV.Activate()

Piezo = SM2602_channel('dualSmeter', channel='b')
Piezo.Activate()
# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()

#begin
piezoVoltage = Piezo.get_volts()
shift = 0
while not (piezo <= 0):
    piezoVoltage = piezoVoltage - (shift / 50.0)
    Piezo.set_volts(piezoVoltage)
    shift = shift + 1
    Stopwatch.Wait(0.2)
    Stopwatch.Measure()
    Piezo.Measure()
    SweeperV.Measure(start=1e-4, stop=1e-3, number=6, delay=0.1)
    datagram.add_data()
    DataStore.writeData()

#end
