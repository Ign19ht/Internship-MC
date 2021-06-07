from NatNetClient import NatNetClient
import time
import csv

# Global variables
RECORDING = False
TIME_START = 0
TIME_ACTUAL = ""

# Constants
HEADER = ["time", "id", "x", "y", "z"]


def csv_save(markers_data, timestamp):
    with open(TIME_ACTUAL, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for marker in markers_data:
            writer.writerow([timestamp - TIME_START, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def create_csv():
    with open(TIME_ACTUAL, 'w', newline='') as csvfile:
        csv.writer(csvfile).writerow(HEADER)


def create_markers_description(markers_data):
    markers_data.sort(key= lambda marker: marker.pos.y)
    with open("BP_" + get_name_from_time(), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "body part"])
        counter = 0

        # 2 lowest part of legs
        for i in range(0, 2):
            if markers_data[counter].id.x > 0:
                writer.writerow([markers_data[counter].id, 21])
            else:
                writer.writerow([markers_data[counter].id, 11])
            counter += 1

        # 2 highest part of legs
        for i in range(0, 2):
            if markers_data[counter].id.x > 0:
                writer.writerow([markers_data[counter].id, 22])
            else:
                writer.writerow([markers_data[counter].id, 12])
            counter += 1

        # 2 lowest part of hands
        for i in range(0, 2):
            if markers_data[counter].id.x > 0:
                writer.writerow([markers_data[counter].id, 41])
            else:
                writer.writerow([markers_data[counter].id, 31])
            counter += 1

        # 2 highest part of hands
        for i in range(0, 2):
            if markers_data[counter].id.x > 0:
                writer.writerow([markers_data[counter].id, 42])
            else:
                writer.writerow([markers_data[counter].id, 32])
            counter += 1


def get_name_from_time():
    temp = '_'.join(time.ctime().split())
    return '_'.join(temp.split(":")) + ".csv"


def receive_new_frame(frame_number, markers_data, labeled_marker_count, timestamp, is_recording):
    global RECORDING, TIME_START, TIME_ACTUAL

    if frame_number == 1:
        create_markers_description(markers_data)

    # print("frame ", frameNumber)
    # print("labeled ", labeledMarkerCount)
    # print("timestamp ", timestamp)
    # print("isRecording ", isRecording)

    # for marker in markers_data:
    #      print(marker.id)
    #      print(marker.pos.x)
    #      print(marker.pos.y)
    #      print(marker.pos.z)

    # print("***********************")

    if not RECORDING and is_recording:
        RECORDING = True
        TIME_START = timestamp
        TIME_ACTUAL = get_name_from_time()
        print(TIME_ACTUAL)
        print("started")
        create_csv()

    if RECORDING and not is_recording:
        RECORDING = False
        print("stopped")

    if RECORDING:
        csv_save(markers_data, timestamp)
        # print("recording...", frameNumber)


streaming_client = NatNetClient()

streaming_client.newFrameListener = receive_new_frame

streaming_client.run()
