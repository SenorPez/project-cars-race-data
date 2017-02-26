"""
Provides a base class for packets output by Project CARS.
"""

from collections import deque
from struct import unpack


class Packet:
    """Base class representing a packet output by Project CARS.

    This class should probably never be called directly; Project CARS does not
    ever output packets that will match the format required of this class.
    Instead, AdditionalParticipantPacket, ParticipantPacket, and
    TelemetryDataPacket should be used.
    """
    _packet_string = "HB"

    def __init__(self, packet_data: bytes):
        """Initialization of Packet object.

        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast. Though not really; the subclasses should be called
                instead.

        Raises:
            struct.error: Raised if an error occurs while unpacking the binary
                data.
        """
        self._hash = hash(packet_data)
        self._unpacked_data = self._unpack_data(packet_data)

        self.build_version_number = int(self._unpacked_data.popleft())
        self._packet_type = int(self._unpacked_data.popleft())

    @property
    def packet_type(self):
        return self._packet_type & int('00000011', 2)

    @property
    def count(self):
        return (self._packet_type & int('11111100', 2)) >> 2

    def _unpack_data(self, packet_data: bytes) -> deque:
        """Unpacks the binary data according to the packet string definition.

        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast.
        """
        return deque(unpack(self._packet_string, packet_data))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Packet"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._hash == other._hash
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self._hash == other._hash
        return NotImplemented

    def __hash__(self):
        return self._hash
