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
        <param field="Mode1" label="Slaves" width="100px" required="true" default="1">
            <description><br/>List of slaves to query on the MODBUS bus. When there is a single meter it should be 1. Used to query multiple meters on the same bus. Example: 1,2,3</description>
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
    __UNIT_POWERFACTOR = 3
    __UNIT_FREQ = 4

    def __init__(self):
        Domoticz.Log("Start PZEM plugin")
        self.pzem = None
        self.slave = []

    def onStart(self):
        if Parameters['Mode1'] == '':
            self.slaves = [1]
        else:
            self.slaves = list(map(int, Parameters['Mode1'].split(',')))
        Domoticz.Log('Reading from slaves: ' + ','.join(str(x) for x in self.slaves))
        if Parameters["Address"] == "0.0.0.0" or Parameters["Address"] == "":
            Domoticz.Log("PZEM plugin started, serial port=" + Parameters["SerialPort"])
            self.pzem = pzem.PZEM004TSerial(Parameters["SerialPort"], self.slaves)
        else:
            Domoticz.Log("PZEM plugin started, remote=" + Parameters["Address"] + ":" + Parameters["Port"])
            self.pzem = pzem.PZEM004TTCP(Parameters["Address"], int(Parameters["Port"]), self.slaves)
        self.pzem.reconnect()

        for slave in self.slaves:
            if not self.__UNIT_P1_SMART_METER+(slave-1)*4 in Devices:
                Domoticz.Device(Name="PZEM-004T meter " + str(slave), Type=250, Subtype=1, Unit=self.__UNIT_P1_SMART_METER+(slave-1)*4).Create()
            if not self.__UNIT_VOLTAGE+(slave-1)*4 in Devices:
                Domoticz.Device(Name="PZEM-004T voltage " + str(slave), TypeName="General", Subtype=8, Unit=self.__UNIT_VOLTAGE+(slave-1)*4).Create()
            if not self.__UNIT_POWERFACTOR+(slave-1)*4 in Devices:
                Domoticz.Device(Name="PZEM-004T power factor " + str(slave), TypeName="General", Subtype=31, Unit=self.__UNIT_POWERFACTOR+(slave-1)*4).Create()
            if not self.__UNIT_FREQ+(slave-1)*4 in Devices:
                Domoticz.Device(Name="PZEM-004T frequency " + str(slave), TypeName="General", Subtype=31, Unit=self.__UNIT_FREQ+(slave-1)*4).Create()

        # Set plugin heartbeat to 10s
        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Log("PZEM plugin stopped")
        self.pzem.close()

    def onHeartbeat(self):
        results = self.pzem.readAll()

        for slave in self.slaves:
            if results[slave]['error'] == "":
                #Domoticz.Log('slave={:d}\tV={:.1f}\tA={:.3f}\tW={:.1f}\tWh={:d}\tHz={:.1f}\tPF={:.2f}'.format(slave, results[slave]['voltage'], results[slave]['current'], results[slave]['power'], results[slave]['energy'], results[slave]['frequency'], results[slave]['powerFactor']))
                if self.__UNIT_P1_SMART_METER+(slave-1)*4 in Devices:
                    sValue = str(results[slave]['energy']) + ';0;0;0;' + str(results[slave]['power']) + ';0'
                    Devices[self.__UNIT_P1_SMART_METER+(slave-1)*4].Update(nValue = 0, sValue = sValue)
                if self.__UNIT_VOLTAGE+(slave-1)*4 in Devices:
                    sValue = str(results[slave]['voltage'])
                    Devices[self.__UNIT_VOLTAGE+(slave-1)*4].Update(nValue = 0, sValue = sValue)
                if self.__UNIT_POWERFACTOR+(slave-1)*4 in Devices:
                    sValue = str(results[slave]['powerFactor'])
                    Devices[self.__UNIT_POWERFACTOR+(slave-1)*4].Update(nValue = 0, sValue = sValue)
                if self.__UNIT_FREQ+(slave-1)*4 in Devices:
                    sValue = str(results[slave]['frequency'])
                    Devices[self.__UNIT_FREQ+(slave-1)*4].Update(nValue = 0, sValue = sValue)
            else:
                Domoticz.Error('slave={:d} error={:s}'.format(slave, results[slave]['error']))


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
