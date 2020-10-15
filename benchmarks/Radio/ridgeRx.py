"""
From Spacecraft Design Lab
"""

# Ridge Testing RX code
import board
import time
import busio, digitalio
import adafruit_rfm9x

"""
----------INPUT PARAMETERS----------
"""
#Bandwidth
#Values: 7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000, 500000
BW = 500000

#Spreading Factor
#Values: 7, 8, 9, 10, 11, or 12
sf = 12

#Coding Rate
#Values: 5, 6, 7, or 8
cr = 5

#Preamble Length
#Values: 6 -> 65535 (default=8)
pl = 8

#Message String
#String sent between radios
messsage = 'Odds of success: 3720 to 1'

"""
----------Configurations----------
"""
# Configure SD card (b/c it's on the the same SPI bus as radios)
sdcs = digitalio.DigitalInOut(board.CS_SD)
sdcs.switch_to_output(value=True)
# Define radio
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
radio1.tx_power = 20
radio1.signal_bandwidth = BW
radio1.coding_rate = cr
radio1.spreading_factor = sf
radio1.preamble_length = pl
radio1.enable_crc = False

count = 0

dropvec = []
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

        if text == message:
            dropvec.append(0)
        else:
            dropvec.append(1)

        if count > 100:
            break

print(sum(dropvec))
print(dropvec)
