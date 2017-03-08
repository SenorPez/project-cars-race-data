"""
Provides classes for the reading and processing of captured Project CARS
telemetry data.
"""
import json
import os
from glob import glob
from itertools import tee

from natsort import natsorted
from tqdm import tqdm

from racedata.Packet import Packet
from racedata.AdditionalParticipantPacket import AdditionalParticipantPacket
from racedata.ParticipantPacket import ParticipantPacket
from racedata.TelemetryDataPacket import TelemetryDataPacket


class RaceData:
    """Class representing race data.

    Race data is a directory of captured UDP packets broadcast by Project CARS.
    At this time there are three types of packets:
        Telemetry data: Length 1367, contains telemetry data, sent at a user-
            defined update rate.
        Participant info strings: Length 1347, contains names for first 16
            drivers in the race, as well as some track and car information.
        Additional participant info strings: Length 1048, contains 16 additional
            names and the index offset.
    """
    def __init__(self, telemetry_directory: str, *,
                 descriptor_filename: str = 'descriptor.json'):
        """Initialization of the RaceData object.

        Args:
            telemetry_directory: String representing the path to the directory
                where the captured telemetry is stored.
            descriptor_filename: Optional parameter to specify the name of the
                JSON file used to store data regarding captured telemetry data.
        """
        self.__telemetry_directory = telemetry_directory
        self.__descriptor_filename = descriptor_filename

        self._telemetry_data = TelemetryData(telemetry_directory)

        descriptor = None
        try:
            with open(os.path.join(
                    os.path.realpath(telemetry_directory),
                    os.path.relpath(descriptor_filename))) as descriptor_file:
                descriptor = json.load(descriptor_file)
        except (FileNotFoundError, ValueError):
            descriptor = self._build_descriptor(
                telemetry_directory,
                descriptor_filename)
        finally:
            self._packet = self._to_hash(
                self._telemetry_data,
                descriptor['race_start'])
            self._last_packet = None

            self._current_drivers = self._get_drivers(
                self._telemetry_data,
                self._packet.num_participants)
            self._dropped_drivers = dict()

            self._track = None
            self._elapsed_time = None

            drivers_by_index = sorted(
                [driver for driver in self._current_drivers.values()],
                key=lambda x: x.index)
            self._starting_grid = frozenset([
                StartingGridEntry(
                    participant_info.race_position,
                    drivers_by_index[index])
                for index, participant_info
                in enumerate(self._packet.participant_info)
                if index < self._packet.num_participants])
            pass

    @property
    def classification(self):
        drivers_by_index = sorted(
            [driver for driver in self._current_drivers.values()],
            key=lambda x: x.index)
        return frozenset([
            ClassificationEntry(
                participant_info.race_position,
                drivers_by_index[index],
                self._packet.viewed_participant_index == index)
            for index, participant_info
            in enumerate(self._packet.participant_info)
            if index < self._packet.num_participants])

    def get_all_data(self):
        progress = tqdm(
            desc='Processing All Telemetry Data',
            total=self._telemetry_data.packet_count,
            unit='packets')
        try:
            while True:
                _ = self.get_data()
                progress.update()
        except StopIteration:
            progress.close()

    def get_data(self, at_time=None):
        while True:
            self._last_packet = self._packet
            self._packet = None

            try:
                while self._packet is None or self._packet.packet_type != 0:
                    self._packet = next(self._telemetry_data)
            except StopIteration:
                self._packet = self._last_packet
                raise

            if self._packet.num_participants \
                    != self._last_packet.num_participants \
                    and self._packet.num_participants != -1:
                current_drivers = self._get_drivers(
                    self._telemetry_data,
                    self._packet.num_participants)

                # Add any new drivers.
                for key in current_drivers.keys() \
                        - self._current_drivers.keys():
                    self._current_drivers[key] = current_drivers[key]

                # Delete any dropped drivers.
                for key in self._current_drivers.keys() \
                        - current_drivers.keys():
                    self._dropped_drivers[key] = self._current_drivers[key]
                    del self._current_drivers[key]

                # Reset indices for drivers that remain.
                for key in current_drivers.keys():
                    self._current_drivers[key].index \
                        = current_drivers[key].index

            # self._track = Track(self._packet.track_length)
            # self._add_sector_times(self._packet)
            self._calc_elapsed_time()

            if at_time is None or self._elapsed_time >= at_time:
                return self._packet

    @staticmethod
    def _build_descriptor(telemetry_directory, descriptor_filename):
        descriptor = {'race_end': None, 'race_finish': None, 'race_start': None}

        telemetry_data = TelemetryData(telemetry_directory)
        progress = tqdm(
            desc='Detecting Race End',
            total=telemetry_data.packet_count,
            unit='packets')

        old_packet = None
        try:
            while True:
                # Exhaust packets prior to RACE_FINISHED
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.race_state == 3:
                        break

                # Exhaust packets through RACE_FINISHED
                while True:
                    try:
                        if packet.packet_type == 0:
                            old_packet = packet
                        packet = next(telemetry_data)
                        progress.update()
                        if packet.packet_type == 0 and packet.race_state != 3:
                            break
                    except StopIteration:
                        old_packet = packet
                        break

        except StopIteration:
            progress.close()
            descriptor['race_end'] = hash(old_packet)

        telemetry_data = TelemetryData(telemetry_directory, reverse=True)
        progress = tqdm(
            desc='Detecting Race Start and Finish',
            total=telemetry_data.packet_count,
            unit='packets')

        # Exhaust packets after the detected race end
        while True:
            packet = next(telemetry_data)
            progress.update()
            if hash(packet) == descriptor['race_end']:
                break

        # Exhaust packets after RACE_END
        while True:
            packet = next(telemetry_data)
            progress.update()
            if packet.packet_type == 0 and packet.race_state == 2:
                break

        descriptor['race_finish'] = hash(packet)

        # Exhaust packets after the green flag
        while True:
            packet = next(telemetry_data)
            progress.update()
            if packet.packet_type == 0 and (
                    packet.race_state == 0
                    or packet.race_state == 1):
                break

        old_packet = packet
        try:
            # Exhaust packets after the race start, except one.
            while True:
                if packet.packet_type == 0:
                    old_packet = packet
                packet = next(telemetry_data)
                progress.update()
                if packet.packet_type == 0 and (
                        packet.session_state != 5
                        or packet.game_state != 2):
                    break
        # None found so use the first packet, already on `old_packet`
        except StopIteration:
            pass

        progress.close()
        descriptor['race_start'] = hash(old_packet)

        telemetry_data = TelemetryData(telemetry_directory)
        progress = tqdm(
            desc='Detecting Driver Population',
            total=telemetry_data.packet_count,
            unit='packets')

        # Exhaust packets before the detected race start
        while True:
            packet = next(telemetry_data)
            progress.update()
            if hash(packet) == descriptor['race_start']:
                break

        # Due to network lag (I think) driver position and sectors aren't
        # always populated. Exhaust packets until this is true
        while True:
            positions = [
                participant.race_position for participant
                in packet.participant_info][:packet.num_participants]
            sectors = [
                participant.sector for participant
                in packet.participant_info][:packet.num_participants]
            if all(positions) and all(sectors):
                descriptor['race_start'] = hash(packet)
                break
            else:
                packet = next(telemetry_data)

        with open(os.path.join(
                os.path.realpath(telemetry_directory),
                os.path.relpath(descriptor_filename)), 'w') as descriptor_file:
            json.dump(descriptor, descriptor_file)

        return descriptor

    def _calc_elapsed_time(self):
        if self._packet.current_time == -1.0:
            self._elapsed_time = 0.0
            self._last_packet = None
        else:
            driver = next(
                driver for driver in self._current_drivers.values()
                if driver.index == self._packet.viewed_participant_index)
            self._elapsed_time = \
                sum(driver.lap_times) + self._packet.current_time

    @staticmethod
    def _get_drivers(telemetry_data, count):
        drivers = list()
        data, restore = tee(telemetry_data._telemetry_iterator, 2)

        while len(drivers) < count:
            packet = next(data)
            if packet.packet_type == 0 and packet.num_participants != count:
                raise ValueError("Participants not populated before break.")
            elif packet.packet_type == 1:
                for index, name in enumerate(packet.name):
                    drivers.append(Driver(index, name))
            elif packet.packet_type == 2:
                for index, name in enumerate(packet.name, packet.offset):
                    drivers.append(Driver(index, name))

        telemetry_data._telemetry_iterator = restore

        return {driver.name: driver for driver in drivers[:count]}

    @staticmethod
    def _to_hash(telemetry_data, hash_value):
        progress = tqdm(
            desc='Preparing Telemetry Data',
            total=telemetry_data.packet_count,
            unit='packets')

        while True:
            packet = next(telemetry_data)
            progress.update()
            if hash(packet) == hash_value:
                progress.close()
                return packet

    def __repr__(self):
        return "RaceData(\"{}\", descriptor_filename=\"{}\")".format(
            self.__telemetry_directory,
            self.__descriptor_filename)

    def __str__(self):
        return "Race Data for {}".format(self.__telemetry_directory)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.__telemetry_directory)


class ClassificationEntry:
    def __init__(self, race_position, driver, viewed_driver):
        self._race_position = race_position
        self._driver = driver
        self._viewed_driver = viewed_driver

    def __repr__(self):
        return "ClassificationEntry(" \
               "{s._race_position}, {driver_repr}, {s._viewed_driver})".format(
                    s=self,
                    driver_repr=repr(self._driver))

    def __str__(self):
        return "Classification Entry: " \
               "{s._race_position} {driver_string} " \
               "Viewed: {s._viewed_driver}".format(
                    s=self,
                    driver_string=str(self._driver))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash((self._race_position, self._driver, self._viewed_driver))


class Driver:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.lap_times = []

    def __repr__(self):
        return "Driver({s.index}, \"{s.name}\")".format(s=self)

    def __str__(self):
        return "{s.name} (Index {s.index})".format(s=self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.name)


class StartingGridEntry:
    """Class representing a starting grid entry.

    """
    def __init__(self, race_position: int, driver: Driver):
        self._race_position = race_position
        self._driver = driver

    def __repr__(self):
        return "StartingGridEntry({s._race_position}, {driver_repr})".format(
            s=self,
            driver_repr=repr(self._driver))

    def __str__(self):
        return "Starting Grid Entry: {s._race_position} {driver_string}".format(
            s=self,
            driver_string=str(self._driver))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash((self._race_position, self._driver))


class TelemetryData:
    """Class representing a directory of telemetry data.

    The directory of telemetry data consists of files that are the captured
    telemetry data from the Project CARS UDP broadcast.
    """
    def __init__(self, telemetry_directory: str, *, reverse: bool=False):
        """Initialization of TelemetryData object.
        
        Args:
            telemetry_directory: String representing the path to the directory
                where the captured telemetry is stored.
            reverse: Boolean representing if the telemetry packets should be
                returned in reverse order.
        """
        self.__reverse = reverse

        if not os.path.isdir(telemetry_directory):
            raise NotADirectoryError

        self.packet_count = len(glob(telemetry_directory + os.sep + 'pdata*'))
        self._telemetry_directory = telemetry_directory
        self._telemetry_iterator = self._get_telemetry_data(reverse)

    def _get_telemetry_data(self, reverse):
        for packet_filename in natsorted(
                glob(self._telemetry_directory + os.sep + 'pdata*'),
                reverse=reverse):
            with open(packet_filename, 'rb') as packet_file:
                packet = Packet(packet_file.read())
                yield packet

    def __repr__(self):
        return "TelemetryData(\"{}\", reverse={})".format(
            self._telemetry_directory,
            self.__reverse)

    def __str__(self):
        return "Telemetry Data for {}".format(self._telemetry_directory)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash(self._telemetry_directory)

    def __iter__(self):
        return self._telemetry_iterator

    def __next__(self):
        return next(self._telemetry_iterator)
