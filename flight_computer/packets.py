import json
import struct


# Represents one set of data to be sent or received
class Packet:
    """
    A class to represent data to be sent or received with the radio.
    It maintains a dictionary mapping fields to values, which can be
    serialized with the CircuitPython struct library.
    """

    # Default values to appease linter
    _names = []
    _fmt = "<"
    type_num = 0

    type_name_to_fmt_str = {
        "padding": "x",
        "float": "f",
        "double": "d",
        "char": "b",
        "unsigned_char": "B",
        "short": "h",
        "unsigned_short": "H",
        "int": "i",
        "unsigned_int": "I",
        "long": "l",
        "unsigned_long": "L",
        "long_long": "q",
        "unsigned_long_long": "Q",
        "string": "s",
    }

    @staticmethod
    def initialize_fmt_and_names(filename):
        packet_str = open(filename).read()
        packet_schema = json.loads(packet_str)
        # Assumes packet schema has been validated
        fmt = ">"  # Use little endian
        names = []
        for field in packet_schema:
            print(field)
            if field["type"] != "padding":
                names.append(field["name"])
            if "count" in field and field["count"] != 1:
                fmt += str(field["count"])
            fmt += Packet.type_name_to_fmt_str[field["type"]]
        return fmt, names

    def __init__(self):
        """Initialize struct. Subclasses should set self._fmt and self._names, to define the
        struct's possible field values. See
        https://docs.python.org/3/library/struct.html and
        https://circuitpython.readthedocs.io/en/5.3.x/shared-bindings/struct/__init__.html.
        The first two element of the fmt string should generally be the magic number and the packet
        type number"""
        self._data = None

    @property
    def field_names(self):
        """Returns the names of every field serialized in this struct"""
        return self._names

    @property
    def data(self) -> dict:
        """Returns data serialized in this struct, as a dict """
        return self._data.copy()

    @data.setter
    def data(self, data: dict) -> None:
        """Set data, validating it to make sure it specifies exactly the right fields"""
        for key in data.keys():
            if key not in self._names:
                print("Invalid key in data: " + key)
        for key in self._names:
            if key not in data:
                print("Missing key: " + key)
        self._data = data

    @property
    def raw_data(self) -> bytes:
        """Return struct serialized as raw data, in bytes object"""
        data_list = [self._data[key] for key in self._names]
        return struct.pack(self._fmt, *data_list)

    @raw_data.setter
    def raw_data(self, raw_data: bytes):
        """Initialize internal data from a raw bytes object"""
        data_list = struct.unpack(self._fmt, raw_data)
        self._data = {key: val for key, val in zip(self._names, data_list)}

    def print_raw_data(self):
        """Helper function for pretty-printing raw data"""
        print(self.raw_data.hex())


class GenericPacket(Packet):
    type_num = 1

    (_names, _fmt) = Packet.initialize_fmt_and_names("./packet_schemas/generic.json")

    def __init__(self):
        super().__init__()


class TelemetryPacket(Packet):
    """A Packet for sending telemetry data to earth"""

    type_num = 2

    (_names, _fmt) = Packet.initialize_fmt_and_names("./packet_schemas/telemetry.json")

    def __init__(self):
        super().__init__()


"""Dict mapping type nums to the packet object"""
_packet_types = [TelemetryPacket]
_packet_types = {packet_type.type_num: packet_type for packet_type in _packet_types}


def get_packet_from_raw_data(raw_data: bytes) -> Packet:
    # Construct a generic packet to check command number
    generic_packet = GenericPacket()
    generic_packet.raw_data = raw_data[:8]

    # Check magic number to make sure it's not corrupted
    if generic_packet.data["magic"] != 12345:
        raise Exception("INVALID MAGIC NUM")

    type_num = generic_packet.data["type"]
    if type_num not in _packet_types:
        raise Exception("INVALID PACKET TYPE")

    type = _packet_types[type_num]
    packet = type()
    packet.raw_data = raw_data
    return packet
