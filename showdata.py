from racedata.Packet import Packet
from racedata.TelemetryDataPacket import TelemetryDataPacket
from racedata.ParticipantPacket import ParticipantPacket
import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ("", 5606)
print("Starting listener on port {}".format(server_address[1]))
udp_socket.bind(server_address)

last_track_length = None
last_track_location = None
last_track_variation = None

try:
  while True:
    data, _ = udp_socket.recvfrom(65565)

    if len(data) == 1367:
      packet = Packet(data)

      if last_track_length is None or last_track_length != packet.track_length:
        print("Track Length: {}".format(packet.track_length))
        last_track_length = packet.track_length

    if len(data) == 1347:
      packet = Packet(data)

      if last_track_location is None or last_track_location != packet.track_location:
        print("Track Location: {}".format(packet.track_location))
        last_track_location = packet.track_location

      if last_track_variation is None or last_track_variation != packet.track_variation:
        print("Track Variation: {}".format(packet.track_variation))
        last_track_variation = packet.track_variation

except KeyboardInterrupt:
  print("Closing listener on port {}".format(server_address[1]))
