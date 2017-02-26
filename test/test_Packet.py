"""
Tests for Packet.py
"""

import unittest
from struct import pack

from racedata.Packet import Packet


class TestPacket(unittest.TestCase):
    """Unit tests for Packet class.
    
    """
    expected_build_version_number = 12345
    expected_packet_type = 3
    expected_count = 42
    
    @classmethod
    def binary_data(cls, **kwargs):
        test_data = list()
        packet_string = "HB"
        
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
            
        return pack(packet_string, *test_data)
    
    def test_init(self):
        instance = Packet(self.binary_data())
        expected_result = Packet
        self.assertIsInstance(instance, expected_result)
        
    def test_init_wrong_packet_length(self):
        test_binary_data = pack("H", 42)
        
        from struct import error
        with self.assertRaises(error):
            Packet(test_binary_data)

    def test_property_packet_type(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_packet_type
        self.assertEqual(instance.packet_type, expected_result)

    def test_property_count(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_count
        self.assertEqual(instance.count, expected_result)
            
    def test_field_build_version_number(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_build_version_number
        self.assertEqual(instance.build_version_number, expected_result)

    def test_magic_eq(self):
        instance_1 = Packet(self.binary_data())
        instance_2 = Packet(self.binary_data())
        self.assertTrue(instance_1 == instance_2)

    def test_magic_eq_diff_class(self):
        instance = Packet(self.binary_data())
        self.assertFalse(instance == self)

    def test_magic_hash(self):
        instance = Packet(self.binary_data())
        expected_result = hash(self.binary_data())
        self.assertEqual(hash(instance), expected_result)

    def test_magic_ne(self):
        instance_1 = Packet(self.binary_data())
        instance_2 = Packet(self.binary_data(
            build_version_number=42))
        self.assertTrue(instance_1 != instance_2)

    def test_magic_ne_diff_class(self):
        instance = Packet(self.binary_data())
        self.assertTrue(instance != self)

    def test_magic_repr(self):
        instance = Packet(self.binary_data())
        expected_result = "Packet"
        self.assertEqual(repr(instance), expected_result)

    def test_magic_str(self):
        instance = Packet(self.binary_data())
        expected_result = "Packet"
        self.assertEqual(str(instance), expected_result)
