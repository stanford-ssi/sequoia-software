# Some miscellaneous radio functions
# Docs: https://circuitpython.readthedocs.io/projects/rfm9x/en/latest/

# Written by Langston Nashold

import struct
from pycubed import cubesat
from packets import Packet, get_packet_from_raw_data


def send_packet(packet, radio=cubesat.radio1):
    """Send a packet on the UHF radio"""
    radio.send(packet)


def receive_packet() -> Packet:
    """Receive a packet on the UHF radio"""
    raw_data = radio.receive()
    # Uncomment next line if you want an easy way to test
    # raw_data = struct.pack('<iiii', 12345, 2, 3, 4)
    return get_packet_from_raw_data(raw_data)


def setup_radio():
    rfm9x = cubesat.radio1
    # Update settings to improve "effective range"
    # Change number of hertz you're modulating between
    # rfm9x.signal_bandwidth = 62500
    # This changes FEC. Between 5-8. Higher number is more tolerant.
    # rfm9x.coding_rate = 8
    # Higher value allows distinguishes signal from noise
    # From 6 - 12
    # rfm9x.spreading_factor = 8
    # Enables cyclic redundancy check, checking for errors
    # rfm9x.enable_crc = True


if __name__ == '__main__':
    packet = receive_packet()
    print(packet.data)
