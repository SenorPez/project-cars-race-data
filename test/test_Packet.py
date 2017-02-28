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
        with self.assertRaises(ValueError):
            Packet(self.binary_data())

