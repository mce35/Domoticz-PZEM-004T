# Library for Peacefair PZEM-004T Energy monitor

import serial
from pymodbus.client import ModbusSerialClient
from pymodbus.client import ModbusTcpClient
from pymodbus.framer.rtu_framer import ModbusRtuFramer

class PZEM004T:
    def __init__(self):
        self.port_name = ""
        self.modbus_client = None

    def reconnect(self):
        tries = 0
        while tries < 5:
            try:
                if self.modbus_client.is_socket_open():
                    self.modbus_client.close()
                if self.modbus_client.connect():
                    break;
            except:
                print("Cannot connect to " + self.port_name + ", retrying")
                tries += 1

        return self.modbus_client.is_socket_open()

    def close(self):
        self.modbus_client.close()

    def readAll(self):
        tries = 0
        data = False
        while tries < 5:
            try:
                # Read all registers (10) from PZEM (reading any other number of registers does not work)
                req = self.modbus_client.read_input_registers(0, 10, slave=1)#, 0xF8)
                data = req.registers;
                break
            except Exception as e:
                tries += 1
                print(e)
            self.reconnect()
            print("read failed on " + self.port_name + ", trying again " + str(tries))
        if data == False:
            return (0, 0, 0, 0, 0, 0, 0)
        voltage = data[0] / 10.0 # [V]
        current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
        power = (data[3] + (data[4] << 16)) / 10.0 # [W]
        energy = data[5] + (data[6] << 16) # [Wh]
        frequency = data[7] / 10.0 # [Hz]
        powerFactor = data[8] / 100.0
        alarm = data[9] # 0 = no alarm

        return (voltage, current, power, energy, frequency, powerFactor, alarm)

class PZEM004TSerial(PZEM004T):
    def __init__(self, usb_port):
        PZEM004T.__init__(self)
        self.port_name = usb_port
        self.modbus_client = ModbusSerialClient(
            method='rtu',
            port=self.port_name,
            baudrate=9600,
            timeout=3,
            parity='N',
            stopbits=1,
            bytesize=8,
            retries=5
        )

class PZEM004TTCP(PZEM004T):
    def __init__(self, host, port):
        PZEM004T.__init__(self)
        self.port_name = host + ":" + str(port)
        self.modbus_client = ModbusTcpClient(host, port, ModbusRtuFramer)
