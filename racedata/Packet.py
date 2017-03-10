"""
Provides a base class for packets output by Project CARS.
"""
from collections import deque
from hashlib import md5
from struct import calcsize, unpack


class Packet(object):
    """Base class representing a packet output by Project CARS.

    Instantiating a new Packet class returns an object of the appropriate
    subclass, as determined by the length of the binary data string passed to
    the constructor. If no appropriate subclass exists, a ValueError is raised.
    """
    _packet_string = "HB"

    def __init__(self, packet_data: bytes):
        """Initialization of Packet object.

        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast. Though not really; the subclasses should be called
                instead.
        """
        self._hash = int(md5(packet_data).hexdigest(), 16) & 0xfffffffffffffff
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

    def __new__(cls, packet_data):
        for subclass in cls.__subclasses__():
            if len(packet_data) == calcsize(subclass._packet_string):
                return object.__new__(subclass)

        raise ValueError

    def __repr__(self):
        return self.__str__()

    def __str__(self): # pragma: no cover
        raise NotImplementedError

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
