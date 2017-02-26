"""
Tests for AdditionalParticipantPacket.py
"""

import unittest
from struct import pack

from racedata.AdditionalParticipantPacket import AdditionalParticipantPacket


class TestAdditionalParticipantPacket(unittest.TestCase):
    """Unit tests for AdditionalParticipantPacket class.

    """
    expected_build_version_number = 12345
    expected_packet_type = 2
    expected_count = 42

    expected_offset = 16
    expected_name = [
        "Felipe Nasr",
        "Jolyon Palmer",
        "Pascal Wehrlein",
        "Stoffel Vandoorne",
        "Esteban Gutiérrez",
        "Marcus Ericsson",
        "Esteban Ocon",
        "Rio Haryanto",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    expected_packet_length = 1028

    @classmethod
    def binary_data(cls, **kwargs):
        test_data = list()
        packet_string = "HBB"
        packet_string += "64s" * 16

        try:
            test_data.append(kwargs['build_version_number'])
        except KeyError:
            test_data.append(cls.expected_build_version_number)

        try:
            packet_type = kwargs['packet_type']
        except KeyError:
            packet_type = cls.expected_packet_type

        try:
            count = kwargs['count']
        except KeyError:
            count = cls.expected_count

        test_data.append((count << 2) + packet_type)

        try:
            test_data.append(kwargs['offset'])
        except KeyError:
            test_data.append(cls.expected_offset)

        try:
            test_data.extend([name.encode('utf-8') for name in kwargs['name']])
        except KeyError:
            test_data.extend(
                [name.encode('utf-8') for name in cls.expected_name])

        return pack(packet_string, *test_data)

    def test_init(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = AdditionalParticipantPacket
        self.assertIsInstance(instance, expected_result)

    def test_init_wrong_packet_length(self):
        test_binary_data = pack("H", 42)

        from struct import error
        with self.assertRaises(error):
            AdditionalParticipantPacket(test_binary_data)

    def test_property_packet_type(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = self.expected_packet_type
        self.assertEqual(instance.packet_type, expected_result)

    def test_property_count(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = self.expected_count
        self.assertEqual(instance.count, expected_result)

    def test_field_build_version_number(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = self.expected_build_version_number
        self.assertEqual(instance.build_version_number, expected_result)

    def test_field_offset(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = self.expected_offset
        self.assertEqual(instance.offset, expected_result)

    def test_field_name(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = self.expected_name
        self.assertListEqual(instance.name, expected_result)

    def test_field_name_split_on_null(self):
        instance = AdditionalParticipantPacket(self.binary_data(
            name=[name + '\x00Garbage Data' for name in self.expected_name]))
        expected_result = self.expected_name
        self.assertListEqual(instance.name, expected_result)

    def test_magic_eq(self):
        instance_1 = AdditionalParticipantPacket(self.binary_data())
        instance_2 = AdditionalParticipantPacket(self.binary_data())
        self.assertTrue(instance_1 == instance_2)

    def test_magic_eq_diff_class(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        self.assertFalse(instance == self)

    def test_magic_hash(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = hash(self.binary_data())
        self.assertEqual(hash(instance), expected_result)

    def test_magic_ne(self):
        instance_1 = AdditionalParticipantPacket(self.binary_data())
        instance_2 = AdditionalParticipantPacket(self.binary_data(
            offset=32))
        self.assertTrue(instance_1 != instance_2)

    def test_magic_ne_diff_class(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        self.assertTrue(instance != self)

    def test_magic_repr(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = "AdditionalParticipantPacket"
        self.assertEqual(repr(instance), expected_result)

    def test_magic_str(self):
        instance = AdditionalParticipantPacket(self.binary_data())
        expected_result = "AdditionalParticipantPacket"
        self.assertEqual(str(instance), expected_result)
