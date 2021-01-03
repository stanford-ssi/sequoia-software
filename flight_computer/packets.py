import json
import struct
import os

MAGIC_NUMBER = 99  # must be between -128 to 127

type_num_to_schema = {
    1: "generic",
    2: "telemetry"
}
schema_to_type_num = dict({reversed(item) for item in type_num_to_schema.items()})

schemas_path = "./packet_schemas/schemas/"

ENDIAN = ">"
U_8 = "B"  # B is unsigned char in python struct

type_name_to_fmt = {
    "float_32": "f",
    "int_8": "b",
    "bool": "z"
}

fmt_to_byte_size = {
    "f": 4,
    "b": 1,
}


class Packet:
    """A class to represent data to be sent or received with the radio.
    It maintains a dictionary mapping fields to values, which can be
    serialized into a bytearray."""

    def __init__(self, packet_type):
        """Initialize a Packet object that stores a mapping of fields to values, a format string to serialize its data,
        a packet type number, and a mapping of how many values are mapped to each field"""
        self._data = {}
        self._field_to_count = {}
        self._fmt = ""
        self._type_num = packet_type if isinstance(packet_type, int) else schema_to_type_num[packet_type]

        def initialize_fmt_and_fields():
            packet_path = os.path.join(
                os.path.dirname(__file__), schemas_path + type_num_to_schema[self._type_num] + ".json"
            )

            packet_str = open(packet_path).read()
            packet_schema = json.loads(packet_str)
            # Assumes packet schema has been validated

            for field in packet_schema:
                # count = 1
                # if "count" in field:
                count = field["count"] if "count" in field else 1

                self._field_to_count[field["name"]] = count
                for _ in range(count):
                    self._fmt += type_name_to_fmt[field["type"]]

        initialize_fmt_and_fields()

    @property
    def field_names(self):
        """Returns the names of every field name serialized in this struct"""
        return self._data.keys()

    @property
    def data(self) -> dict:
        """Returns data serialized in this struct, as a dict """
        return self._data.copy()

    @data.setter
    def data(self, data: dict) -> None:
        """Set data, validating it to make sure it specifies exactly the right fields"""
        for field in data.keys():
            if field not in self._field_to_count:
                raise Exception("Invalid key in data: " + field)
        for field in self._field_to_count:
            if field not in data:
                raise Exception("Missing key: " + field)

        for field, val in data.items():
            if type(val) is not list:
                data[field] = [val]
        self._data = data

    @property
    def raw_data(self) -> bytearray:
        """Get raw values as a bitarray"""
        val_list = []
        for field, vals in self.data.items():
            for val in vals:
                val_list.append(val)

        packed_data = bytearray()
        bool_list = []
        for fmt, val in zip(self._fmt, val_list):
            if fmt is type_name_to_fmt["bool"]:
                bool_list.append(val)
            else:
                packed_data += struct.pack(ENDIAN + fmt, val)

        # compress all bools into a few bytes
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

    @raw_data.setter
    def raw_data(self, arr: bytearray) -> None:
        """Set raw data from bytearray"""

        """make a list of values parsed according to the packets fmt string"""
        val_list = []
        k_arr = 0
        j_bit = 0
        for fmt in self._fmt:
            if fmt is not type_name_to_fmt["bool"]:
                raw_bytes = arr[k_arr: k_arr + fmt_to_byte_size[fmt]]
                val = struct.unpack(ENDIAN + fmt, raw_bytes)[0]
                val_list.append(val)
                k_arr += fmt_to_byte_size[fmt]
            else:
                # decompress bytes into bools
                # get truth value at jth position at the kth byte in the byte array
                bitmask = 1 << j_bit
                raw_byte = arr[k_arr:k_arr + 1]
                val = bitmask & struct.unpack(ENDIAN + U_8, raw_byte)[0]
                val = bool(val)
                val_list.append(val)
                j_bit = (j_bit + 1) % 8
                if j_bit is 0:
                    k_arr += 1
        data = {}
        data_iterator = 0
        for field, count in self._field_to_count.items():
            vals = val_list[data_iterator: data_iterator + count]
            data[field] = vals
            data_iterator += count
        self._data = data

    def print_raw_data(self):
        """Helper function for pretty-printing raw data"""
        print(self.raw_data.hex())


def get_packet_from_raw_data(raw_data: bytearray) -> Packet:
    """Generate packet object from the given raw data as a bytearray object"""
    # Construct a generic packet to check command number
    generic_packet = Packet("generic")
    generic_packet.raw_data = raw_data[:2]
    # first byte is magic number, second byte is packet type

    # Check magic number to make sure it's not corrupted
    if generic_packet.data["magic"] != [MAGIC_NUMBER]:
        raise Exception("INVALID MAGIC NUM")

    # Check packet type to make sure its not corrupted
    type_num = generic_packet.data["type"][0]
    if type_num not in type_num_to_schema:
        raise Exception("INVALID PACKET TYPE")

    packet = Packet(type_num)
    packet.raw_data = raw_data
    return packet


