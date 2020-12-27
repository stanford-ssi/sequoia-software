import json
import struct

SCHEMAS_PATH = "./packet_schemas/schemas"

ENDIAN = ">"
U_8 = "B"  # B is unsigned char in python struct

GENERIC_PACKET_TYPE_NUM = 1
TELEMETRY_PACKET_TYPE_NUM = 2

MAGIC_NUMBER = 99  # must be between -128 to 127

NAME_TO_FMT = {
    "float_32": "f",
    "int_8": "b",
    "bool": "z"
}

fmt_to_byte_size = {
    "f": 4,
    "b": 1,
}


def unpack(arr, fmt_str):
    data_list = []
    k_arr = 0
    j_bit = 0
    for fmt in fmt_str:
        if fmt is not NAME_TO_FMT["bool"]:
            raw_bytes = arr[k_arr: k_arr + fmt_to_byte_size[fmt]]
            val = struct.unpack(ENDIAN + fmt, raw_bytes)[0]
            data_list.append(val)
            k_arr += fmt_to_byte_size[fmt]
        else:
            # get truth value at jth position at the kth byte in the byte array
            bitmask = 1 << j_bit
            raw_byte = arr[k_arr:k_arr + 1]
            val = bitmask & struct.unpack(ENDIAN + U_8, raw_byte)[0]
            val = bool(val)
            data_list.append(val)
            j_bit = (j_bit + 1) % 8
            if j_bit is 0:
                k_arr += 1
    return data_list


def pack(data, fmt_str):
    packed_data = bytearray()
    bool_list = []
    for fmt, val in zip(fmt_str, data):
        if fmt is NAME_TO_FMT["bool"]:
            bool_list.append(val)
        else:
            packed_data += struct.pack(ENDIAN + fmt, val)

    packed_bools = bytearray()
    j = 0
    bool_byte = 0
    for b in bool_list:
        bool_byte |= (b << j)
        j = (j + 1) % 8
        if j is 0:
            packed_bools += struct.pack(ENDIAN + U_8, bool_byte)  # unsigned char to represent 8 bits!
            bool_byte = 0
    if j is not 0 and len(bool_list) > 0:
        packed_bools += struct.pack(ENDIAN + U_8, bool_byte)
    packed_data += packed_bools

    return packed_data


class Packet:
    """
    A class to represent data to be sent or received with the radio.
    It maintains a dictionary mapping fields to values, which can be
    serialized into a bytearray.
    """

    # Default values to appease linter
    _fields = {}
    _fmt = ENDIAN
    type_num = 0

    # use big endian
    type_name_to_fmt_str = NAME_TO_FMT

    @staticmethod
    def initialize_fmt_and_fields(filename):
        packet_str = open(filename).read()
        packet_schema = json.loads(packet_str)
        # Assumes packet schema has been validated

        fmt = ""  # Using big endian, see type_name_to_fmt_str above
        fields = {}  # store field names as dictionary, mapping field name to count

        for field in packet_schema:
            count = 1
            if "count" in field:
                count = field["count"]

            fields[field["name"]] = count
            for i in range(0, count):
                fmt += Packet.type_name_to_fmt_str[field["type"]]

        return fmt, fields

    def __init__(self):
        """Initialize. Subclasses should set self._fmt and self._names, to define the possible field values.
        The first two element of the fmt string should generally be the magic number and the packet type number"""
        self._data = None

    @property
    def field_names(self):
        """Returns the names of every field name serialized in this struct"""
        return self._fields.keys()

    @property
    def data(self) -> dict:
        """Returns data serialized in this struct, as a dict """
        return self._data.copy()

    @data.setter
    def data(self, data: dict) -> None:
        """Set data, validating it to make sure it specifies exactly the right fields"""
        for field in data.keys():
            if field not in self._fields:
                print("Invalid key in data: " + field)
        for field in self._fields:
            if field not in data:
                print("Missing key: " + field)

        for field, val in data.items():
            if type(val) is not list:
                data[field] = [val]
        self._data = data

    @property
    def raw_data(self) -> bytearray:
        """Get raw values as a bitarray"""
        data_list = []
        for field, vals in self.data.items():
            for val in vals:
                data_list.append(val)
        arr = pack(data_list, self._fmt)
        return arr

    @raw_data.setter
    def raw_data(self, arr: bytearray) -> None:
        """Set raw data from bitarray"""
        data = {}
        data_list = unpack(arr, self._fmt)
        data_iterator = 0
        for field, count in self._fields.items():
            val_list = data_list[data_iterator: data_iterator + count]
            data[field] = val_list
            data_iterator += count
        self._data = data

    def print_raw_data(self):
        """Helper function for pretty-printing raw data"""
        print(self.raw_data.hex())


class GenericPacket(Packet):
    type_num = GENERIC_PACKET_TYPE_NUM

    (_fmt, _fields) = Packet.initialize_fmt_and_fields(SCHEMAS_PATH + "/generic.json")

    def __init__(self):
        super().__init__()


class TelemetryPacket(Packet):
    """A Packet for sending telemetry data to earth"""

    type_num = TELEMETRY_PACKET_TYPE_NUM

    (_fmt, _fields) = Packet.initialize_fmt_and_fields(SCHEMAS_PATH + "/telemetry.json")

    def __init__(self):
        super().__init__()


"""Dict mapping type nums to the packet object"""
_packet_types = [GenericPacket, TelemetryPacket]
_packet_types = {packet_type.type_num: packet_type for packet_type in _packet_types}


def get_packet_from_raw_data(raw_data: bytes) -> Packet:
    # Construct a generic packet to check command number
    generic_packet = GenericPacket()
    generic_packet.raw_data = raw_data[:2]
    # first byte is magic number, second byte is packet type

    # Check magic number to make sure it's not corrupted
    if generic_packet.data["magic"][0] != MAGIC_NUMBER:
        raise Exception("INVALID MAGIC NUM")

    # Check packet type to make sure its not corrupted
    type_num = generic_packet.data["type"][0]
    if type_num not in _packet_types:
        raise Exception("INVALID PACKET TYPE")

    packet_type = _packet_types[type_num]
    packet = packet_type()
    packet.raw_data = raw_data
    return packet


def test_instantiate_generic():
    sample_generic_data = {
        "magic": MAGIC_NUMBER,
        "type": GENERIC_PACKET_TYPE_NUM
    }
    packet1 = GenericPacket()
    packet1.data = sample_generic_data

    packet1.print_raw_data()
    print(packet1.data)

    packet2 = GenericPacket()
    packet2.raw_data = packet1.raw_data
    print(packet2.data)
    print(packet1.raw_data == packet2.raw_data)


test_instantiate_generic()


def test_instantiate_telemetry():
    sample_telemetry_data = {
        "magic": MAGIC_NUMBER,
        "type": TELEMETRY_PACKET_TYPE_NUM,
        "attitude": [1, 2, 3, 4],
        "angular_rates": [5, 6, 7],
        "battery_voltage": 8,
        "temperature": 9,
        "reset_count": 10,
        "antennas_deployed": [True, True],
        "solar_panels_deployed": [False, True],
        "reboot_code": True,
        "last_uplink_success": False,
    }
    packet1 = TelemetryPacket()
    packet1.data = sample_telemetry_data

    packet1.print_raw_data()
    print(packet1.data)

    packet2 = TelemetryPacket()
    packet2.raw_data = packet1.raw_data
    packet2.print_raw_data()

    print(packet2.data)

    print(packet1.raw_data == packet2.raw_data)

    packet3 = get_packet_from_raw_data(packet2.raw_data)
    print("packet3", packet3.data)
    print(packet3.raw_data == packet2.raw_data)


test_instantiate_telemetry()
