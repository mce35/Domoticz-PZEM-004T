import pzem
import sys

pzinst = pzem.PZEM004TSerial(sys.argv[1], [1])

results = pzinst.readAll()
voltage = results[1]['voltage']
current = results[1]['current']
power = results[1]['power']
energy = results[1]['energy']
frequency = results[1]['frequency']
powerFactor = results[1]['powerFactor']
alarm = results[1]['alarm']

print('V={:.1f}\tA={:.3f}\tW={:.1f}\tWh={:d}\tHz={:.1f}\tPF={:.2f}'.format(voltage, current, power, energy, frequency, powerFactor))
