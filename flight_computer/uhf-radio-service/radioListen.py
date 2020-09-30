"""
From Spacecraft Design Lab
"""

import board
import time
import busio, digitalio
import adafruit_rfm9x

# Configure SD card (b/c it's on the the same SPI bus as radios)
sdcs = digitalio.DigitalInOut(board.CS_SD)
sdcs.switch_to_output(value=True)

# Define radios
rf_cs1 = digitalio.DigitalInOut(board.RF1_CS)
rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
rf_cs1.switch_to_output(value=True)
rf_rst1.switch_to_output(value=True)
rf_cs2 = digitalio.DigitalInOut(board.RF2_CS)
rf_rst2 = digitalio.DigitalInOut(board.RF2_RST)
rf_cs2.switch_to_output(value=True)
rf_rst2.switch_to_output(value=True)

# Setup SPI bus
spi  = busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO)

# Initialize radio
try:
    radio1 = adafruit_rfm9x.RFM9x(spi, rf_cs2, rf_rst2, 433.0)
except Exception as e:
    print('[ERROR][RADIO 1]',e)
count = 0
radio1.tx_power = 23

powervec = []
while True:
    packet = radio1.receive()
    if packet is None:
        print('I got nothin bud')
        time.sleep(1)
    else:
        text = str(packet,'ascii')
        count += 1
        rssi = radio1.rssi
        print(text)
        print('Signal Strength: {0} dB'.format(rssi))
        time.sleep(1)
        powervec.append(rssi)
        if count > 20:
            break