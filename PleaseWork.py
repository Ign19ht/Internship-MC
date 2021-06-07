from NatNetClient import NatNetClient
import time
import csv
import os

# Global variables
RECORDING = False
IS_FIRST = True
TIME_START = 0
COUNT = [0, 0, 0]
PATH = ""

# Constants
HEADER = ["time", "id", "x", "y", "z"]
DIR = r"Coords/"
TEMP = "temp.csv"
TYPES = {1: "upLift",
         2: "squat",
         3: "sitStand"}


def csv_save(markers_data, timestamp):
    with open(PATH + TEMP, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for marker in markers_data:
            writer.writerow([timestamp - TIME_START, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def create_csv():
    with open(PATH + TEMP, 'w', newline='') as csv_file:
        csv.writer(csv_file).writerow(HEADER)


def set_file_name():
    global COUNT
    print("Input type:")
    type = int(input())
    if type == 0:
        os.remove(PATH + TEMP)
        print("deleted")
    else:
        COUNT[type - 1] += 1
        os.rename(PATH + TEMP, PATH + TYPES[type] + "_" + str(COUNT[type - 1]) + ".csv")
        print("name is set")


def create_markers_description(markers_data):
    markers_data.sort(key=lambda marker: marker.pos.y)
    with open(PATH + "BP.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "body part"])
        counter = 0

        # 2 lowest part of legs
        for i in range(0, 2):
            if markers_data[counter].pos.x > 0:
                writer.writerow([markers_data[counter].id, 21])
            else:
                writer.writerow([markers_data[counter].id, 11])
            counter += 1

        # # 2 highest part of legs
        # for i in range(0, 2):
        #     if markers_data[counter].pos.x > 0:
        #         writer.writerow([markers_data[counter].id, 22])
        #     else:
        #         writer.writerow([markers_data[counter].id, 12])
        #     counter += 1
        #
        # # 2 lowest part of hands
        # for i in range(0, 2):
        #     if markers_data[counter].pos.x > 0:
        #         writer.writerow([markers_data[counter].id, 41])
        #     else:
        #         writer.writerow([markers_data[counter].id, 31])
        #     counter += 1
        #
        # # 2 highest part of hands
        # for i in range(0, 2):
        #     if markers_data[counter].pos.x > 0:
        #         writer.writerow([markers_data[counter].id, 42])
        #     else:
        #         writer.writerow([markers_data[counter].id, 32])
        #     counter += 1


def get_name_from_time():
    temp = '_'.join(time.ctime().split())
    return '_'.join(temp.split(":"))


def receive_new_frame(frame_number, markers_data, rigid_body_count, labeled_marker_count, timestamp, is_recording):
    global RECORDING, TIME_START, IS_FIRST

    if IS_FIRST:
        create_markers_description(markers_data)
        print("description is created")
        IS_FIRST = False

    # print("frame ", frameNumber)
    # print("labeled ", labeled_marker_count)
    # print("rigid ", rigid_body_count)
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
        print("started")
        create_csv()

    if RECORDING and not is_recording:
        RECORDING = False
        print("stopped")
        set_file_name()

    if RECORDING:
        csv_save(markers_data, timestamp)
        # print("recording...", frameNumber)


if __name__ == '__main__':
    PATH = DIR + get_name_from_time() + r"/"

    os.mkdir(PATH)

    streaming_client = NatNetClient()

    streaming_client.newFrameListener = receive_new_frame

    streaming_client.run()
