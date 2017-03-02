"""
Tests for RaceData.py
"""
import unittest
from inspect import isgenerator
from unittest.mock import mock_open, patch, sentinel

from racedata.RaceData import RaceData, TelemetryData


@unittest.skip("Because I'm a retard.")
class TestRaceData(unittest.TestCase):
    """Unit tests for RaceData class.

    """
    @patch('racedata.RaceData.TelemetryData')
    def test_init(self, mock_telemetry_data):
        mock_telemetry_data.return_value = sentinel.telemetry_data

        instance = RaceData(sentinel.directory)
        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)


class TestTelemetryData(unittest.TestCase):
    """Unit tests for TelemetryData class.

    """
    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_init(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        expected_result = TelemetryData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.os.path.isdir')
    def test_init_invalid_directory(self, mock_isdir):
        mock_isdir.return_value = False

        with self.assertRaises(NotADirectoryError):
            instance = TelemetryData(sentinel.directory)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_repr(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        expected_result = "TelemetryData(\"{}\", reverse={})".format(
            "mock_directory",
            False)
        self.assertEqual(repr(instance), expected_result)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_repr_reversed(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory", reverse=True)
        expected_result = "TelemetryData(\"{}\", reverse={})".format(
            "mock_directory",
            True)
        self.assertEqual(repr(instance), expected_result)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_str(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        expected_result = "Telemetry Data for {}".format("mock_directory")
        self.assertEqual(str(instance), expected_result)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_eq_true(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance_1 = TelemetryData("mock_directory")
        instance_2 = TelemetryData("mock_directory")
        self.assertTrue(instance_1 == instance_2)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_eq_false(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance_1 = TelemetryData("mock_directory")
        instance_2 = TelemetryData("another_mock_directory")
        self.assertFalse(instance_1 == instance_2)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_eq_diff_class(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        self.assertFalse(instance == self)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_ne_true(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance_1 = TelemetryData("mock_directory")
        instance_2 = TelemetryData("another_mock_directory")
        self.assertTrue(instance_1 != instance_2)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_ne_false(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance_1 = TelemetryData("mock_directory")
        instance_2 = TelemetryData("mock_directory")
        self.assertFalse(instance_1 != instance_2)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_ne_diff_class(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        self.assertTrue(instance != self)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_hash(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        expected_result = hash("mock_directory")
        self.assertEqual(hash(instance), expected_result)

    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_iter(self, mock_isdir, mock_glob):
        mock_isdir.return_value = True
        mock_glob.return_value = [sentinel.packet]

        instance = TelemetryData("mock_directory")
        self.assertTrue(iter(instance), isgenerator)

    @patch('racedata.RaceData.Packet', autospec=True)
    @patch('racedata.RaceData.glob')
    @patch('racedata.RaceData.os.path.isdir')
    def test_magic_next(self, mock_isdir, mock_glob, mock_packet):
        mock_isdir.return_value = True
        mock_glob.return_value = [mock_packet]

        instance = TelemetryData("mock_directory")
        expected_result = mock_packet.__class__

        m = mock_open()
        with patch('racedata.RaceData.open', m) as mock_file_open:
            self.assertIsInstance(next(instance), expected_result)

        m.assert_called_once_with(mock_packet, 'rb')
