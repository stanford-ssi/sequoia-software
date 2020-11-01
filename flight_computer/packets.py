import struct


# Represents one set of data to be sent or received
class Packet:
    """
    A class to represent data to be sent or received with the radio.
    It maintains a dictionary mapping fields to values, which can be
    serialized with the CircuitPython struct library.
    """

    def __init__(self):
        """Initialize struct. Subclasses should set self._fmt and self._names, to define the
        struct's possible field values. See
        https://docs.python.org/3/library/struct.html and
        https://circuitpython.readthedocs.io/en/5.3.x/shared-bindings/struct/__init__.html.
        The first two element of the fmt string should generally be the magic number and the packet
        type number"""
        self._data = {}
        # Placeholder
        self._fmt = '<'
        # Placeholder
        self.type_num = 0

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
    def __init__(self):
        super().__init__()
        self._fmt = "<ii"
        self._names = ['magic', 'type']
        self.type_num = 1


class TelemetryPacket(Packet):
    """A Packet for sending telemetry data to earth"""
    type_num = 2

    def __init__(self):
        super().__init__()
        self._fmt = "<iiii"
        self._names = ['magic', 'type', 'temp', 'power']


"""Dict mapping type nums to the packet object"""
_packet_types = [TelemetryPacket]
_packet_types = {packet_type.type_num: packet_type for packet_type in _packet_types}


def get_packet_from_raw_data(raw_data: bytes) -> Packet:
    # Construct a generic packet to check command number
    generic_packet = GenericPacket()
    generic_packet.raw_data = raw_data[:8]

    # Check magic number to make sure it's not corrupted
    if generic_packet.data['magic'] != 12345:
        raise Exception("INVALID MAGIC NUM")

    type_num = generic_packet.data['type']
    if type_num not in _packet_types:
        raise Exception("INVALID PACKET TYPE")

    type = _packet_types[type_num]
    packet = type()
    packet.raw_data = raw_data
    return packet
