# Some miscallenous radio functions
# Docs: https://circuitpython.readthedocs.io/projects/rfm9x/en/latest/

# Written by Langston Nashold
import uart

import board
import time
import digitalio
import struct
from pycubed import cubesat

def sendTelemetryData(radio = cubesat.radio1):
    fmt = "<iff"
    # little endian standard size
    # see https://docs.python.org/3/library/struct.html
    packet = struct.pack(fmt, 5, cubesat.temperature_cpu, cubesat.current_draw)
    radio.send(packet)
    #print("Radio1 Sent: " + str(packet))
    #print("Unpacked: " + str(struct.unpack(fmt, packet)))
def sendString(s, radio = cubesat.radio1):
    fmt = "100s"
    packet = struct.pack(fmt, s)
    radio.send(packet)
    print("Radio1 Sent: " + str(packet))

def receiveCommand(radio = cubesat.radio1):
    fmt = "<ii100s"

    data = radio.receive()
    print("Received (raw)" + str(data))
    if data != None:
        unpacked = struct.unpack(fmt, data)
        if (unpacked[0] != 613789):
            print("ERROR: Magic num doesn't match")
        handleCommand(unpacked[1], unpacked[2])

def handleCommand(commandNum, data):
    if commandNum == 32:
        print("Send image command received")
        s = data.decode('utf-8').rstrip('\x00')
        result = uart.takeImage()
        sendString(result)

def setupRadio():
    rfm9x = cubesat.radio1
    # Update settings to improve "effective range"
    # Change number of hertz you're modulating between
    #rfm9x.signal_bandwidth = 62500
    # This changes FEC. Between 5-8. Higher number is more tolerant.
    #rfm9x.coding_rate = 8
    # Higher value allows distinguishes signal from noise
    # From 6 - 12
    #rfm9x.spreading_factor = 8
    # Enables cyclic redudancy check, checking for errors
    #rfm9x.enable_crc = True

if cubesat.hardware['Radio1']:
    while True:
        setupRadio()
        sendTelemetryData()
        receiveCommand()
        time.sleep(0.1)
    # Send something