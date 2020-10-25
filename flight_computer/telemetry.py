import struct
from pycubed import cubesat
class Packet:
    # Placeholder
    fmt = ""
    # TODO: Make raw_data an autoprop?
    def __init__(self):
        self.raw_data = ''

    def extract(self):
        return struct.unpack(Packet.fmt, self.raw_data)

    def initialize(self, *kwargs):
        self.raw_data = struct.pack(Packet.fmt, kwargs)


class TelemetryData(Packet):
    """FMT: integer, cpu temp, cubesat draw"""
    fmt = "<iff"

    def initalizeFromSensors(self):
        super.initialize(self, 5, cubesat.temperature_cpu, cubesat.current_draw)

class Command(Packet):
    """Magic number, command number, and arbitrary JSON text of command"""
    fmt = "<ii100s"

    def __init__(self):
        self.cmd_num = 0
        self.cmd_str = ''
        self.magic = 0

    def extract(self, raw_data):
        unpacked = super.extract(raw_data)
        [self.magic, self.cmd_num, self.cmd_str] = unpacked
        return unpacked
