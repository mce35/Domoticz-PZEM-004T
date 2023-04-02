import pzem
import sys

pzinst = pzem.PZEM004TSerial(sys.argv[1])
(voltage, current, power, energy, frequency, powerFactor, alarm) = pzinst.readAll()

print('V={:.1f}\tA={:.3f}\tW={:.1f}\tWh={:d}\tHz={:.1f}\tPF={:.2f}'.format(voltage, current, power, energy, frequency, powerFactor))
