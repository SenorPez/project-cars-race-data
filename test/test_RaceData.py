"""
Tests for RaceData.py
"""
import unittest
from inspect import isgenerator
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch, sentinel

from racedata.RaceData import RaceData, TelemetryData


class TestRaceData(unittest.TestCase):
    """Unit tests for RaceData class.

    """
    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_init(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_init_no_descriptor_happy_path(self, mock_telemetry_data, *_):
        """
        Three packets: Race Start, Race Finish, Race End.
        Nothing spurious.
        """
        mock_race_end_packet = MagicMock()
        mock_race_end_packet.packet_type = 0
        mock_race_end_packet.race_state = 3

        mock_race_finish_packet = MagicMock()
        mock_race_finish_packet.packet_type = 0
        mock_race_finish_packet.race_state = 2

        mock_race_start_packet = MagicMock()
        mock_race_start_packet.packet_type = 0
        mock_race_start_packet.race_state = 1
        mock_race_start_packet.session_state = 5

        mock_data_1 = MagicMock()
        mock_data_1.packet_count = 3
        mock_data_1.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_2 = MagicMock()
        mock_data_2.packet_count = 3
        mock_data_2.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_3 = MagicMock()
        mock_data_3.packet_count = 3
        mock_data_3.__next__.side_effect = [
            mock_race_end_packet,
            mock_race_finish_packet,
            mock_race_start_packet]

        mock_data_4 = MagicMock()
        mock_data_4.packet_count = 3
        mock_data_4.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_telemetry_data.side_effect = [
            mock_data_1,
            mock_data_2,
            mock_data_3,
            mock_data_4]

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            m.side_effect = [FileNotFoundError, mock.DEFAULT]
            instance = RaceData(sentinel.directory)

        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_init_no_descriptor_extra_end_packet(self, mock_telemetry_data, *_):
        """
        Extra garbage packet at the end.
        """
        mock_extra_packet = MagicMock()
        mock_extra_packet.packet_type = 0
        mock_extra_packet.race_state = 2

        mock_race_end_packet = MagicMock()
        mock_race_end_packet.packet_type = 0
        mock_race_end_packet.race_state = 3

        mock_race_finish_packet = MagicMock()
        mock_race_finish_packet.packet_type = 0
        mock_race_finish_packet.race_state = 2

        mock_race_start_packet = MagicMock()
        mock_race_start_packet.packet_type = 0
        mock_race_start_packet.race_state = 1
        mock_race_start_packet.session_state = 5

        mock_data_1 = MagicMock()
        mock_data_1.packet_count = 3
        mock_data_1.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet,
            mock_extra_packet]

        mock_data_2 = MagicMock()
        mock_data_2.packet_count = 3
        mock_data_2.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet,
            mock_extra_packet]

        mock_data_3 = MagicMock()
        mock_data_3.packet_count = 3
        mock_data_3.__next__.side_effect = [
            mock_extra_packet,
            mock_race_end_packet,
            mock_race_finish_packet,
            mock_race_start_packet]

        mock_data_4 = MagicMock()
        mock_data_4.packet_count = 3
        mock_data_4.__next__.side_effect = [
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet,
            mock_extra_packet]

        mock_telemetry_data.side_effect = [
            mock_data_1,
            mock_data_2,
            mock_data_3,
            mock_data_4]

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            m.side_effect = [FileNotFoundError, mock.DEFAULT]
            instance = RaceData(sentinel.directory)

        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_init_no_descriptor_extra_start_packet(
            self,
            mock_telemetry_data,
            *_):
        """
        Extra garbage packet at the start.
        """
        mock_extra_packet = MagicMock()
        mock_extra_packet.packet_type = 0
        mock_extra_packet.session_state = 4

        mock_race_end_packet = MagicMock()
        mock_race_end_packet.packet_type = 0
        mock_race_end_packet.race_state = 3

        mock_race_finish_packet = MagicMock()
        mock_race_finish_packet.packet_type = 0
        mock_race_finish_packet.race_state = 2

        mock_race_start_packet = MagicMock()
        mock_race_start_packet.packet_type = 0
        mock_race_start_packet.race_state = 1
        mock_race_start_packet.session_state = 5

        mock_data_1 = MagicMock()
        mock_data_1.packet_count = 3
        mock_data_1.__next__.side_effect = [
            mock_extra_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_2 = MagicMock()
        mock_data_2.packet_count = 3
        mock_data_2.__next__.side_effect = [
            mock_extra_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_3 = MagicMock()
        mock_data_3.packet_count = 3
        mock_data_3.__next__.side_effect = [
            mock_race_end_packet,
            mock_race_finish_packet,
            mock_race_start_packet,
            mock_extra_packet]

        mock_data_4 = MagicMock()
        mock_data_4.packet_count = 3
        mock_data_4.__next__.side_effect = [
            mock_extra_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_telemetry_data.side_effect = [
            mock_data_1,
            mock_data_2,
            mock_data_3,
            mock_data_4]

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            m.side_effect = [FileNotFoundError, mock.DEFAULT]
            instance = RaceData(sentinel.directory)

        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_init_no_descriptor_unpopulated(self, mock_telemetry_data, *_):
        """
        Start packet without driver population.
        """
        mock_race_end_packet = MagicMock()
        mock_race_end_packet.packet_type = 0
        mock_race_end_packet.race_state = 3

        mock_race_finish_packet = MagicMock()
        mock_race_finish_packet.packet_type = 0
        mock_race_finish_packet.race_state = 2

        mock_race_start_packet = MagicMock()
        mock_race_start_packet.packet_type = 0
        mock_race_start_packet.race_state = 1
        mock_race_start_packet.session_state = 5
        mock_race_start_packet.game_state = 2

        mock_unpopulated_packet = MagicMock()
        mock_unpopulated_packet.packet_type = 0
        mock_unpopulated_packet.race_state = 1
        mock_unpopulated_packet.session_state = 5
        mock_unpopulated_packet.game_state = 2
        mock_unpopulated_packet.num_participants = 1

        mock_participant = MagicMock()
        mock_participant.race_position = 0
        mock_participant.sector = 0

        mock_unpopulated_packet.participant_info = [mock_participant]

        mock_data_1 = MagicMock()
        mock_data_1.packet_count = 3
        mock_data_1.__next__.side_effect = [
            mock_unpopulated_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_2 = MagicMock()
        mock_data_2.packet_count = 3
        mock_data_2.__next__.side_effect = [
            mock_unpopulated_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_data_3 = MagicMock()
        mock_data_3.packet_count = 3
        mock_data_3.__next__.side_effect = [
            mock_race_end_packet,
            mock_race_finish_packet,
            mock_race_start_packet,
            mock_unpopulated_packet]

        mock_data_4 = MagicMock()
        mock_data_4.packet_count = 3
        mock_data_4.__next__.side_effect = [
            mock_unpopulated_packet,
            mock_race_start_packet,
            mock_race_finish_packet,
            mock_race_end_packet]

        mock_telemetry_data.side_effect = [
            mock_data_1,
            mock_data_2,
            mock_data_3,
            mock_data_4]

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            m.side_effect = [FileNotFoundError, mock.DEFAULT]
            instance = RaceData(sentinel.directory)

        expected_result = RaceData
        self.assertIsInstance(instance, expected_result)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_eq_true(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance_1 = RaceData(sentinel.directory_1)
            instance_2 = RaceData(sentinel.directory_1)

        self.assertTrue(instance_1 == instance_2)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_eq_false(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance_1 = RaceData(sentinel.directory_1)
            instance_2 = RaceData(sentinel.directory_2)

        self.assertFalse(instance_1 == instance_2)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_eq_diff_class(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        self.assertFalse(instance == self)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_ne_true(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance_1 = RaceData(sentinel.directory_1)
            instance_2 = RaceData(sentinel.directory_2)

        self.assertTrue(instance_1 != instance_2)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_ne_false(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance_1 = RaceData(sentinel.directory_1)
            instance_2 = RaceData(sentinel.directory_1)

        self.assertFalse(instance_1 != instance_2)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_ne_diff_class(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        self.assertTrue(instance != self)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_hash(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        expected_value = hash(sentinel.directory)
        self.assertEqual(hash(instance), expected_value)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_repr_default(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        expected_value = "RaceData(\"sentinel.directory\", " \
                         "descriptor_filename=\"descriptor.json\")"
        self.assertEqual(repr(instance), expected_value)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_repr_custom(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(
                sentinel.directory,
                descriptor_filename="custom.json")

        expected_value = "RaceData(\"sentinel.directory\", " \
                         "descriptor_filename=\"custom.json\")"
        self.assertEqual(repr(instance), expected_value)

    @patch('racedata.RaceData.json')
    @patch('racedata.RaceData.os')
    @patch('racedata.RaceData.TelemetryData')
    def test_magic_str_default(self, mock_telemetry_data, _, mock_json):
        mock_data = MagicMock()
        mock_data.packet_count = 1
        mock_data.__next__.return_value = sentinel.packet
        mock_telemetry_data.return_value = mock_data

        mock_json.load.return_value = {'race_start': hash(sentinel.packet)}

        m = mock_open()
        with patch('racedata.RaceData.open', m):
            instance = RaceData(sentinel.directory)

        expected_value = "Race Data for sentinel.directory"
        self.assertEqual(str(instance), expected_value)


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
            _ = TelemetryData(sentinel.directory)

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
        with patch('racedata.RaceData.open', m):
            self.assertIsInstance(next(instance), expected_result)

        m.assert_called_once_with(mock_packet, 'rb')
