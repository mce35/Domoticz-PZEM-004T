# Library for Peacefair PZEM-004T Energy monitor

import serial
from pymodbus.client import ModbusSerialClient
from pymodbus.client import ModbusTcpClient
from pymodbus.framer import FramerType

class PZEM004T:
    def __init__(self, slaves):
        self.slaves = slaves
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
        results = {}
        for current_slave in self.slaves:
            results[current_slave] = {}
            data = False
            tries = 0
            while tries < 5:
                try:
                    # Read all registers (10) from PZEM (reading any other number of registers does not work)
                    req = self.modbus_client.read_input_registers(0, count = 10, slave = current_slave)#, 0xF8)
                    data = req.registers
                    err = ""
                    break
                except Exception as e:
                    tries += 1
                    err=str(e)
                    print(e)
                self.reconnect()
                print("read failed on " + self.port_name + "/slave=" + str(current_slave) + ", trying again " + str(tries))
            if data == False:
                results[current_slave]['error'] = "read failed on " + self.port_name + "/slave=" + str(current_slave) + ": " + err
            else:
                results[current_slave]['error'] = ""
                results[current_slave]['voltage'] = data[0] / 10.0 # [V]
                results[current_slave]['current'] = (data[1] + (data[2] << 16)) / 1000.0 # [A]
                results[current_slave]['power'] = (data[3] + (data[4] << 16)) / 10.0 # [W]
                results[current_slave]['energy'] = data[5] + (data[6] << 16) # [Wh]
                results[current_slave]['frequency'] = data[7] / 10.0 # [Hz]
                results[current_slave]['powerFactor'] = data[8] / 100.0
                results[current_slave]['alarm'] = data[9] # 0 = no alarm

        return results

class PZEM004TSerial(PZEM004T):
    def __init__(self, usb_port, slaves):
        PZEM004T.__init__(self, slaves)
        self.port_name = usb_port
        self.modbus_client = ModbusSerialClient(
            framer = FramerType.RTU,
            port=self.port_name,
            baudrate=9600,
            timeout=3,
            parity='N',
            stopbits=1,
            bytesize=8,
            retries=5
        )
        self.modbus_client.connect()

class PZEM004TTCP(PZEM004T):
    def __init__(self, host, port, slaves):
        PZEM004T.__init__(self, slaves)
        self.port_name = host + ":" + str(port)
        self.modbus_client = ModbusTcpClient(host, port, framer = FramerType.RTU)
