import optirx
import optirx as rx
import matplotlib.pyplot as plt
import time

dsock = rx.mkdatasock()
version = (2, 9, 0, 0)  # NatNet version to use
ax = plt.axes(projection='3d')

data = dsock.recv(rx.MAX_PACKETSIZE)
# packet = rx.unpack(data, version=version)
# marker_id1 = packet.labeled_markers[0].id
# marker_id2 = packet.labeled_markers[1].id
# print(marker_id1)
# print(marker_id2)

while True:
    data = dsock.recv(rx.MAX_PACKETSIZE)
    print(data)
    packet = rx.unpack(data, version=version)

    coord1 = packet.labeled_markers[0].position
    coord2 = packet.labeled_markers[1].position
    coord3 = packet.labeled_markers[2].position
    # optirx.LabeledMarker.

    # for marker in packet.labeled_markers:
    #     if marker.id == marker_id1:
    #         coord1 = packet.labeled_markers[0].position
    #     if marker.id == marker_id2:
    #         coord2 = packet.labeled_markers[0].position

    # ax.scatter3D(coord[0],coord[1],coord[2],cmap='Green')
    # plt.show()

    # print(coord1)
    # print(coord2)
    # print(coord3)
    # print("*****")

    # print(packet)

    time.sleep(0.01)
