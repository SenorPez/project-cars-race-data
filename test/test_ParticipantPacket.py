"""
Tests for ParticipantPacket.py
"""

import unittest
from hashlib import md5
from struct import pack

from racedata.Packet import Packet
from racedata.ParticipantPacket import ParticipantPacket


class TestParticipantPacket(unittest.TestCase):
    """Unit tests for ParticipantPacket class.

    """
    expected_build_version_number = 12345
    expected_packet_type = 1
    expected_count = 42

    expected_car_name = "F1 W07 Hybrid"
    expected_car_class_name = "F1 2016"
    expected_track_location = "Abu Dhabi"
    expected_track_variation = "Grand Prix"

    expected_name = [
        "Nico Rosberg",
        "Lewis Hamilton",
        "Daniel Ricciardo",
        "Sebastian Vettel",
        "Max Verstappen",
        "Kimi Räikkönen",
        "Sergio Pérez",
        "Valtteri Bottas",
        "Nico Hülkenberg",
        "Fernando Alonso",
        "Felipe Massa",
        "Carlos Sainz Jr.",
        "Romain Grosjean",
        "Daniil Kvyat",
        "Jenson Button",
        "Kevin Magnussen"
    ]
    expected_fastest_lap = [
        103.729,
        104.495,
        104.889,
        104.970,
        105.137,
        105.163,
        105.187,
        105.249,
        105.261,
        105.675,
        105.715,
        105.928,
        105.949,
        106.145,
        106.189,
        106.219
    ]
    expected_packet_length = 1347

    def assertListAlmostEqual(self, list1, list2, delta):
        for item1, item2 in zip(list1, list2):
            self.assertAlmostEqual(item1, item2, delta=delta)

    @classmethod
    def binary_data(cls, **kwargs):
        test_data = list()
        packet_string = "=HB64s64s64s64s"
        packet_string += "64s" * 16
        packet_string += "16f"

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
            test_data.append(kwargs['car_name'].encode('utf-8'))
        except KeyError:
            test_data.append(cls.expected_car_name.encode('utf-8'))

        try:
            test_data.append(kwargs['car_class_name'].encode('utf-8'))
        except KeyError:
            test_data.append(cls.expected_car_class_name.encode('utf-8'))

        try:
            test_data.append(kwargs['track_location'].encode('utf-8'))
        except KeyError:
            test_data.append(cls.expected_track_location.encode('utf-8'))

        try:
            test_data.append(kwargs['track_variation'].encode('utf-8'))
        except KeyError:
            test_data.append(cls.expected_track_variation.encode('utf-8'))

        try:
            test_data.extend([name.encode('utf-8') for name in kwargs['name']])
        except KeyError:
            test_data.extend(
                [name.encode('utf-8') for name in cls.expected_name])

        try:
            test_data.extend(kwargs['fastest_lap'])
        except KeyError:
            test_data.extend(cls.expected_fastest_lap)

        return pack(packet_string, *test_data)

    def test_init(self):
        instance = Packet(self.binary_data())
        expected_result = ParticipantPacket
        self.assertIsInstance(instance, expected_result)

    def test_direct_init(self):
        with self.assertRaises(NotImplementedError):
            ParticipantPacket(self.binary_data())

    def test_init_wrong_packet_length(self):
        test_binary_data = pack("H", 42)

        with self.assertRaises(ValueError):
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

    def test_field_car_class_name(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_car_class_name
        self.assertEqual(instance.car_class_name, expected_result)

    def test_field_car_class_name_split_on_null(self):
        instance = Packet(self.binary_data(
            car_class_name=self.expected_car_class_name + "\x00Garbage Data"))
        expected_result = self.expected_car_class_name
        self.assertEqual(instance.car_class_name, expected_result)

    def test_field_car_name(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_car_name
        self.assertEqual(instance.car_name, expected_result)

    def test_field_car_name_split_on_null(self):
        instance = Packet(self.binary_data(
            car_class_name=self.expected_car_name + "\x00Garbage Data"))
        expected_result = self.expected_car_name
        self.assertEqual(instance.car_name, expected_result)
        
    def test_field_fastest_lap(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_fastest_lap
        self.assertListAlmostEqual(
            instance.fastest_lap_time,
            expected_result,
            delta=0.001)

    def test_field_name(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_name
        self.assertListEqual(instance.name, expected_result)

    def test_field_name_split_on_null(self):
        instance = Packet(self.binary_data(
            name=[name+'\x00Garbage Data' for name in self.expected_name]))
        expected_result = self.expected_name
        self.assertListEqual(instance.name, expected_result)

    def test_field_track_location(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_track_location
        self.assertEqual(instance.track_location, expected_result)

    def test_field_track_location_split_on_null(self):
        instance = Packet(self.binary_data(
            track_location=self.expected_track_location + "\x00Garbage Data"))
        expected_result = self.expected_track_location
        self.assertEqual(instance.track_location, expected_result)

    def test_field_track_variation(self):
        instance = Packet(self.binary_data())
        expected_result = self.expected_track_variation
        self.assertEqual(instance.track_variation, expected_result)

    def test_field_track_variation_split_on_null(self):
        instance = Packet(self.binary_data(
            track_variation=self.expected_track_variation + "\x00Garbage Data"))
        expected_result = self.expected_track_variation
        self.assertEqual(instance.track_variation, expected_result)

    def test_magic_eq(self):
        instance_1 = Packet(self.binary_data())
        instance_2 = Packet(self.binary_data())
        self.assertTrue(instance_1 == instance_2)

    def test_magic_eq_diff_class(self):
        instance = Packet(self.binary_data())
        self.assertFalse(instance == self)

    def test_magic_hash(self):
        instance = Packet(self.binary_data())
        expected_result = int(
            md5(self.binary_data()).hexdigest(), 16) & 0xfffffffffffffff
        self.assertEqual(hash(instance), expected_result)

    def test_magic_ne(self):
        instance_1 = Packet(self.binary_data())
        instance_2 = Packet(self.binary_data(
            car_name='125cc Shifter Kart'))
        self.assertTrue(instance_1 != instance_2)

    def test_magic_ne_diff_class(self):
        instance = Packet(self.binary_data())
        self.assertTrue(instance != self)

    def test_magic_repr(self):
        instance = Packet(self.binary_data())
        expected_result = "ParticipantPacket"
        self.assertEqual(repr(instance), expected_result)

    def test_magic_str(self):
        instance = Packet(self.binary_data())
        expected_result = "ParticipantPacket"
        self.assertEqual(str(instance), expected_result)
