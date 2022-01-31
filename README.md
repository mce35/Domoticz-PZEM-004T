# Domoticz-PZEM-004T-Plugin

A simple Domoticz Python plugin to get power measurements from PZEM-004T energy meter

## Features

Creates the following Domoticz Devices:
* P1 Smart Meter (power (W), energy (Wh))
* Voltage

## Configuration

### Plugin Parameters

| Field | Information|
| ----- | ---------- |
| Serial Port | The port where the meter is connected |
| Address | IP address when using Modbus over TCP |
| Port | TCP port for Modbus over TCP |

## TODO

* Add power factor, current, frequency and alarm monitoring
* Ability to configure alarm threshold
* Ability to monitor multiple meters connected to the same serial port
* Add more logs
