#DMMtest.py

Stopwatch.zeroTimer()
while Stopwatch.getSinceLastZeroed() < 300:
    Stopwatch.Measure()
    Thermocouple.Measure()
    Platinum.Measure()
