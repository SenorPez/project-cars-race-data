"""
Provides a class for the Participant Info Strings output by Project CARS
"""

from racedata.Packet import Packet


class ParticipantPacket(Packet):
    """Class representing Participant Info String.

    The first 16 drivers of the race are included in the participant info
    strings that are sent.

    The participant info string packets have a length of 1347 and is packet type
    1.
    """

    _packet_string = "=HB64s64s64s64s"
    _packet_string += "64s" * 16
    _packet_string += "16f"

    def __init__(self, packet_data: bytes):
        """Initialization of ParticipantPacket object.

        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast.
        """
        super().__init__(packet_data)

        self.car_name = str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0]
        self.car_class_name = str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0]
        self.track_location = str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0]
        self.track_variation = str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0]

        self.name = [str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0] for _ in range(16)]

        self.fastest_lap_time = [
            float(self._unpacked_data.popleft()) for _ in range(16)]

    def __new__(cls, packet_data):
        raise NotImplementedError

    def __str__(self):
        return "ParticipantPacket"
