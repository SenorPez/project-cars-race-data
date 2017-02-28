"""
Provides a class for the Additional Participant Info Strings output
by Project CARS.
"""

from racedata.Packet import Packet


class AdditionalParticipantPacket(Packet):
    """Class representing Additional Participant Info Strings.

    If there are more than 16 drivers in the race, additional participant info
    string packets are sent. These contain information about drivers 17-n.

    The additional participant info string packets have a length of 1028 bytes
    and is packet type 2.
    """

    _packet_string = "=HBB"
    _packet_string += "64s" * 16

    def __init__(self, packet_data: bytes):
        """Initialization of AdditionalParticipantPacket object.

        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast.
        """
        super().__init__(packet_data)

        self.offset = int(self._unpacked_data.popleft())

        self.name = [str(
            self._unpacked_data.popleft(),
            encoding='utf-8',
            errors='strict').split('\x00', 1)[0] for _ in range(16)]

    def __new__(cls, packet_data):
        raise NotImplementedError

    def __str__(self):
        return "AdditionalParticipantPacket"
