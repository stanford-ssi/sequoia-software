import unittest
from flight_computer import packets

sample_telemetry_data = {
    "magic": packets.MAGIC_NUMBER,
    "type": packets.schema_to_type_num["telemetry"],
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


class TestPackets(unittest.TestCase):

    def test_raw_data(self):
        """ test the raw data functions ie getters, setters, and packet from raw data """
        # CALLS
        # Setter
        packet1 = packets.Packet("telemetry")
        packet1.data = sample_telemetry_data

        # Getter
        packet2 = packets.Packet("telemetry")
        packet2.raw_data = packet1.raw_data

        # Packet from Raw Data
        packet3 = packets.get_packet_from_raw_data(packet1.raw_data)

        # ASSERTS
        # test setters and getters end to end
        self.assertEqual(packet1.raw_data, packet2.raw_data, packet3.raw_data)
        self.assertEqual(packet1.data, packet2.data, packet3.data)

        # test whether the raw data is the expected values
        self.assertEqual(packet2.raw_data[0], packets.MAGIC_NUMBER)
        self.assertEqual(packet2.raw_data[1], packets.schema_to_type_num["telemetry"])

        # test whether the data is the expected values
        self.assertEqual(packet1.data, sample_telemetry_data)

        # PRINTS
        packet1.print_raw_data()

    def test_data(self):
        """ test the raw data functions ie getters, setters, and packet from raw data """
        # CALLS
        # Setter
        packet1 = packets.Packet("telemetry")
        packet1.data = sample_telemetry_data

        # Getter
        packet2 = packets.Packet("telemetry")
        packet2.data = packet1.data

        # Packet from Raw Data -> Data
        packet3 = packets.get_packet_from_raw_data(packet1.raw_data)

        # ASSERTS
        # test setters and getters end to end
        self.assertEqual(packet1.raw_data, packet2.raw_data, packet3.raw_data)
        self.assertEqual(packet1.data, packet2.data, packet3.data)

        # test whether the data matches what we inputted
        self.assertEqual(packet1.data, sample_telemetry_data)

        # PRINTS
        print(packet1.data)


if __name__ == '__main__':
    unittest.main()
