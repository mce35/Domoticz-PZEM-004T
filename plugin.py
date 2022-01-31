#!/usr/bin/env python3
# coding: utf-8 -*-
#
# Author: mce35
#
"""
<plugin key="PZEM-004T" name="PZEM-004T energy meter" author="mce35" version="0.1">
    <description>
        <h1>Plugin for Peacefair PZEM-004T energy meter</h1><br/>
            <br/><h2> Informations</h2><br/>
            This plugin reads data from a single PZEM-004T meter connected to an USB port
            <br/><h2>Parameters</h2>
    </description>
    <params>
        <param field="SerialPort" label="Serial Port" width="300px" required="true" default="/dev/ttyUSB0" >
            <description><br/>Set the serial port where the PZEM is connected (/dev/ttyUSB0 for example)</description>
        </param>
        <param field="Address" label="IP" width="150px" required="true" default="0.0.0.0">
            <description><br/>Set the PZEM-004T IP adresse when using modbus over TCP (leave it to 0.0.0.0 to use serial port)</description>
        </param>
        <param field="Port" label="Port" width="100px" required="true" default="502">
            <description><br/>Set the Port (502 by default)</description>
        </param>
    </params>
</plugin>
"""

import Domoticz
import pzem

class BasePlugin:
    enabled = False
    __UNIT_P1_SMART_METER = 1
    __UNIT_VOLTAGE = 2

    def __init__(self):
        Domoticz.Log("Start PZEM plugin")
        self.pzem = None

    def onStart(self):
        Domoticz.Log("PZEM plugin started!")
        if Parameters["Address"] == "0.0.0.0" or Parameters["Address"] == "":
            self.pzem = pzem.PZEM004TSerial(Parameters["SerialPort"])
        else:
            self.pzem = pzem.PZEM004TTCP(Parameters["Address"], int(Parameters["Port"]))
        self.pzem.reconnect()

        if not self.__UNIT_P1_SMART_METER in Devices:
            Domoticz.Device(Name="PZEM-004T meter", Type=250, Subtype=1, Unit=self.__UNIT_P1_SMART_METER).Create()
        if not self.__UNIT_VOLTAGE in Devices:
            Domoticz.Device(Name="PZEM-004T voltage", TypeName="General", Subtype=8, Unit=self.__UNIT_VOLTAGE).Create()

        # Set plugin heartbeat to 10s
        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Log("PZEM plugin stopped")
        self.pzem.close()

    def onHeartbeat(self):
        (voltage, current, power, energy, frequency, powerFactor, alarm) = self.pzem.readAll()
        #Domoticz.Debug('V={:.1f}\tA={:.3f}\tW={:.1f}\tWh={:d}\tHz={:.1f}\tPF={:.2f}'.format(voltage, current, power, energy, frequency, powerFactor))
        if voltage == 0:
            return
        if self.__UNIT_P1_SMART_METER in Devices:
            sValue = str(energy) + ';0;0;0;' + str(power) + ';0'
            Devices[self.__UNIT_P1_SMART_METER].Update(nValue = 0, sValue = sValue)
        if self.__UNIT_VOLTAGE in Devices:
            sValue = str(voltage)
            Devices[self.__UNIT_VOLTAGE].Update(nValue = 0, sValue = sValue)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
