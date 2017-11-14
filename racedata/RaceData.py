"""
Provides classes for the reading and processing of captured Project CARS
telemetry data.
"""
import json
import os
from glob import glob
from itertools import tee
from math import ceil

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
            self._final_packet_hash = descriptor['race_end']

            self._current_drivers = self._get_drivers(
                self._telemetry_data,
                self._packet.num_participants)
            self._dropped_drivers = dict()
            self._stopped_drivers = set()

            self._track = None
            self._elapsed_time = None

            self.laps_in_event, self.total_time = self._detect_race_length(
                self._packet, telemetry_directory)

            self._track = Track(self._packet.track_length)

            drivers_by_index = sorted(
                [driver for driver in self._current_drivers.values()],
                key=lambda x: x.index)
            self._starting_grid = sorted([
                StartingGridEntry(
                    participant_info.race_position,
                    drivers_by_index[index])
                for index, participant_info
                in enumerate(self._packet.participant_info)
                if index < self._packet.num_participants])

    @property
    def all_driver_classification(self):
        classification = self.classification
        for driver in self._dropped_drivers.values():
            classification.append(ClassificationEntry(None, driver, None))

        position = 0
        for entry in sorted(
                classification,
                key=lambda x: (-x.driver.laps_complete, x.driver.race_time)):
            position += 1
            entry.race_position = position

        return sorted(classification)

    @property
    def best_lap(self):
        try:
            return min([
                driver.best_lap for driver
                in self._current_drivers.values()
                if driver.best_lap is not None])
        except ValueError:
            return None

    @property
    def best_sector_1(self):
        try:
            return min([
                driver.best_sector_1 for driver
                in self._current_drivers.values()
                if driver.best_sector_1 is not None])
        except ValueError:
            return None

    @property
    def best_sector_2(self):
        try:
            return min([
                driver.best_sector_2 for driver
                in self._current_drivers.values()
                if driver.best_sector_2 is not None])
        except ValueError:
            return None

    @property
    def best_sector_3(self):
        try:
            return min([
                driver.best_sector_3 for driver
                in self._current_drivers.values()
                if driver.best_sector_3 is not None])
        except ValueError:
            return None

    @property
    def classification(self):
        drivers_by_index = sorted(
            [driver for driver in self._current_drivers.values()],
            key=lambda x: x.index)
        return sorted([
            ClassificationEntry(
                participant_info.race_position,
                drivers_by_index[index],
                self._packet.viewed_participant_index == index)
            for index, participant_info
            in enumerate(self._packet.participant_info)
            if index < self._packet.num_participants])

    @property
    def current_lap(self):
        leader_lap = max([
            participant.current_lap for participant
            in self._packet.participant_info])
        return leader_lap if self.laps_in_event is None \
            else min(leader_lap, self.laps_in_event)

    @property
    def current_time(self):
        return self._packet.current_time

    @property
    def event_time_remaining(self):
        return self._packet.event_time_remaining

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
                if hash(self._last_packet) == self._final_packet_hash:
                    raise StopIteration
                while self._packet is None or self._packet.packet_type != 0:
                    self._packet = next(self._telemetry_data)

                # It seems, occassionally, a garbage packet is thrown.
                while self._packet.game_state == 2 and self._packet.race_state == 0:
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
            self._add_sector_times(self._packet)
            self._calc_elapsed_time()

            if at_time is None or self._elapsed_time >= at_time:
                return self._packet

    def _add_sector_times(self, packet):
        for index, participant_info in enumerate(
                packet.participant_info[:packet.num_participants]):
            driver_name = None
            for driver in self._current_drivers.values():
                if driver.index == index:
                    driver_name = driver.name

            if participant_info.sector == 1:
                sector = 3
            elif participant_info.sector == 2:
                if driver_name in self._stopped_drivers:
                    self._stopped_drivers.remove(driver_name)
                sector = 1
            elif participant_info.sector == 3:
                sector = 2
            else:
                # TODO: Investigate invalid sector number.
                raise ValueError("Invalid Sector Number")

            if self._track.at_pit_entry(participant_info.world_position) \
                    and driver_name not in self._stopped_drivers \
                    and self._packet.race_state == 2:
                self._stopped_drivers.add(driver_name)

            if self._track.at_pit_exit(participant_info.world_position) \
                    and driver_name in self._stopped_drivers:
                self._current_drivers[driver_name].stops += 1
                self._stopped_drivers.remove(driver_name)

            sector_time = SectorTime(
                participant_info.last_sector_time,
                sector,
                participant_info.lap_invalidated)

            self._current_drivers[driver_name].add_sector_time(sector_time)

    @staticmethod
    def _build_descriptor(telemetry_directory, descriptor_filename):
        descriptor = {'race_end': None, 'race_finish': None, 'race_start': None}

        telemetry_data = TelemetryData(telemetry_directory)
        progress = tqdm(
            desc='Detecting Race End',
            total=telemetry_data.packet_count,
            unit='packets')

        old_packet = None
        '''
        try:
            while True:
                # Exhaust packets prior to RACESTATE_RACING
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.race_state == 2:
                        break

                # Exhaust packets prior to RACESTATE_FINISHED
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.race_state == 3:
                        break

                # Exhaust packets through RACE_FINISHED
                while True:
                    try:
                        if packet.packet_type == 0 and packet.race_state == 3:
                            old_packet = packet
                        packet = next(telemetry_data)
                        progress.update()
                        if packet.packet_type == 0 and packet.race_state != 3:
                            break
                    except StopIteration:
                        break

        except StopIteration:
            progress.close()
            descriptor['race_end'] = hash(old_packet)
        '''
        try:
            # Eventually, we'll get through all the packets.
            while True:
                # Exhaust packets prior to RACESTATE_RACING
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.session_state == 5 and packet.race_state == 2:
                        break

                # Exhaust packets until RACESTATE_FINISHED
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.session_state == 5 and packet.race_state == 3:
                        old_packet = packet
                        break

                # Exhaust packets until no longer RACESTATE_FINISHED, updating "last good" packet each time.
                while True:
                    packet = next(telemetry_data)
                    progress.update()
                    if packet.packet_type == 0 and packet.session_state == 5 and packet.race_state == 3:
                        old_packet = packet
                    elif packet.packet_type == 0:
                        break

        except StopIteration:
            progress.close
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
                packet = None
                while packet is None or packet.packet_type != 0:
                    progress.update()
                    packet = next(telemetry_data)

        progress.close()

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
    def _detect_race_length(packet, telemetry_directory):
        laps_in_event = packet.laps_in_event
        if laps_in_event == 0:
            laps_in_event = None
            telemetry_data = TelemetryData(telemetry_directory)
            progress = tqdm(
                desc='Detecting Race Length',
                total=telemetry_data.packet_count,
                unit='packets')
            packet = next(telemetry_data)
            while (packet.packet_type == 0 and packet.race_state == 1) \
                    or packet.packet_type != 0:
                try:
                    progress.update()
                    packet = next(telemetry_data)
                except StopIteration:
                    break

            progress.close()
            total_time = ceil(packet.event_time_remaining)
        else:
            total_time = None

        return laps_in_event, total_time

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
                    if len(name):
                        drivers.append(Driver(index, name))
            elif packet.packet_type == 2:
                for index, name in enumerate(packet.name, packet.offset):
                    if len(name):
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
            try:
                packet = next(telemetry_data)
            except StopIteration:
                progress.close()
                raise
            else:
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
        self.race_position = race_position
        self.driver = driver
        self._viewed_driver = viewed_driver

    def __repr__(self):
        return "ClassificationEntry(" \
               "{s.race_position}, {driver_repr}, {s._viewed_driver})".format(
                    s=self,
                    driver_repr=repr(self.driver))

    def __str__(self):
        return "Classification Entry: " \
               "{s.race_position} {driver_string} " \
               "Viewed: {s._viewed_driver}".format(
                    s=self,
                    driver_string=str(self.driver))

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.race_position < other.race_position
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.race_position <= other.race_position
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.race_position > other.race_position
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.race_position >= other.race_position
        return NotImplemented

    def __hash__(self):
        return hash((self.race_position, self.driver, self._viewed_driver))


class Driver:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.stops = 0

        self._sector_times = list()

        self._invalidate_next_sector_count = 0

    @property
    def best_lap(self):
        valid_laps = list()
        for invalid, time in zip(self._lap_invalid(), self.lap_times):
            if not invalid:
                valid_laps.append(time)

        try:
            return min(valid_laps)
        except ValueError:
            return None

    @property
    def best_sector_1(self):
        return self._best_sector(1)

    @property
    def best_sector_2(self):
        return self._best_sector(2)

    @property
    def best_sector_3(self):
        return self._best_sector(3)

    @property
    def laps_complete(self):
        return len(self.lap_times)

    @property
    def lap_times(self):
        # Check to see if the first sector is sector 1. Trim if not.
        sector_times = self._trim_sector_times()

        times = [sector.time for sector in sector_times]
        lap_times = list()
        for lap in zip(*[iter(times)]*3):
            lap_times.append(sum(lap))

        return lap_times

    @property
    def race_time(self):
        return sum(self.lap_times)

    @property
    def sector_times(self):
        return [sector.time for sector in self._sector_times]

    def add_sector_time(self, sector_time):
        if sector_time.time == -123.0:
            pass
        elif len(self._sector_times) == 0:
            self._sector_times.append(sector_time)
        elif self._sector_times[-1] != sector_time:
            if sector_time.invalid \
                    and not self._sector_times[-1].invalid \
                    and self._sector_times[-1].time == sector_time.time \
                    and self._sector_times[-1].sector == sector_time.sector:
                self._sector_times[-1] = sector_time
            elif not sector_time.invalid \
                    and self._sector_times[-1].invalid \
                    and self._sector_times[-1].time == sector_time.time \
                    and self._sector_times[-1].sector == sector_time.sector:
                pass
            else:
                if self._invalidate_next_sector_count > 0:
                    self._sector_times.append(SectorTime(
                        sector_time.time,
                        sector_time.sector,
                        True))
                    self._invalidate_next_sector_count -= 1
                else:
                    self._sector_times.append(SectorTime(
                        sector_time.time,
                        sector_time.sector,
                        False))

            if sector_time.invalid:
                self._invalidate_lap(sector_time)

    def _best_sector(self, sector):
        try:
            return min([
                sector_time.time for sector_time in self._sector_times
                if not sector_time.invalid and sector_time.sector == sector])
        except ValueError:
            return None

    def _invalidate_lap(self, sector_time):
        if sector_time.sector == 3:
            self._invalidate_next_sector_count = 3
        elif sector_time.sector == 1:
            self._invalidate_next_sector_count = 2
            for sector in self._sector_times[-1:]:
                sector.invalid = True
        elif sector_time.sector == 2:
            self._invalidate_next_sector_count = 1
            for sector in self._sector_times[-2:]:
                sector.invalid = True
        else:
            raise ValueError("Invalid Sector Number")

    def _lap_invalid(self):
        sector_times = self._trim_sector_times()

        invalids = [sector.invalid for sector in sector_times]
        lap_validity = list()
        for lap in zip(*[iter(invalids)] * 3):
            lap_validity.append(any(lap))

        return lap_validity

    def _trim_sector_times(self):
        sector_times = self._sector_times
        try:
            while sector_times[0].sector != 1:
                sector_times = sector_times[1:]
        except IndexError:
            pass

        return sector_times

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


class SectorTime:
    def __init__(self, time, sector, invalid):
        self.time = time
        self.sector = sector
        self.invalid = bool(invalid)

    def __repr__(self):
        return "SectorTime({}, {}, {})".format(
            self.time,
            self.sector,
            self.invalid)

    def __str__(self):
        return "Sector {} Time: {}, Invalid: {}".format(
            self.sector,
            self.time,
            self.invalid)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __hash__(self):
        return hash((self.time, self.sector, self.invalid))


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

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._race_position < other._race_position
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self._race_position <= other._race_position
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not hash(self) == hash(other)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self._race_position > other._race_position
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self._race_position >= other._race_position
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


class Track:
    """Represents a Project CARS track.

    Notes
        Track detection requires the existence of `lib/track_data.json` that
        contains the track data.

    Acknowledgements
        Way too many thanks to mrbelowski, who made much of the data publicly
        available through his CrewChief app, preventing me from having to
        reinvent the wheel.
        https://github.com/mrbelowski/CrewChiefV4/
    """
    def __init__(self, track_length):
        try:
            with open(os.path.join(
                    os.path.dirname(__file__),
                    'lib/track_data.json')) as track_json:
                track_data = json.load(track_json)

            track = sorted(
                track_data.values(),
                key=lambda x: abs(x['length'] - float(track_length)))[0]

            try:
                self._name = track['display_name']
            except KeyError:
                self._name = None

            try:
                # If all the pit keys are present, we populate the pit
                # information
                self._pit_entry = (
                    float(track['pit_entry'][0]),
                    float(track['pit_entry'][1]))
                self._pit_exit = (
                    float(track['pit_exit'][0]),
                    float(track['pit_exit'][1]))
                self._pit_radius = float(track['pit_radius'])
            except KeyError:
                self._pit = False
            else:
                self._pit = True
        except FileNotFoundError:
            self._pit = False
        except ValueError as json_error:
            raise json_error

    def at_pit_entry(self, coordinates):
        return self._pit \
           and abs(self._pit_entry[0] - coordinates[0]) < self._pit_radius \
           and abs(self._pit_entry[1] - coordinates[2]) < self._pit_radius

    def at_pit_exit(self, coordinates):
        return self._pit \
            and abs(self._pit_exit[0]-coordinates[0]) < self._pit_radius \
            and abs(self._pit_exit[1]-coordinates[2]) < self._pit_radius
