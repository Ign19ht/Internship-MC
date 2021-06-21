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
DIR = r"Draft/"
TEMP = "temp.csv"
TYPES = {1: "stoop",
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
    markers_data.sort(key=lambda marker: marker.pos.z)
    checker = set()
    with open(PATH + "BP.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "body part"])
        counter = 1
        for marker in markers_data:
            if marker.pos.x > 0.6 or marker.pos.x < -0.6:
                continue
            if marker.pos.y > 0.6 or marker.pos.y < -0.6:
                continue
            if marker.pos.z > 2.7 or marker.pos.z < 0.03:
                continue
            if counter <= 2:  # 2 lowest part of shins
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 21])
                    checker.add(21)
                else:
                    writer.writerow([marker.id, 11])
                    checker.add(11)
            elif counter <= 4:  # 2 highest part of shins
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 22])
                    checker.add(22)
                else:
                    writer.writerow([marker.id, 12])
                    checker.add(12)
            elif counter <= 6:  # 2 lowest part of thighs
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 23])
                    checker.add(23)
                else:
                    writer.writerow([marker.id, 13])
                    checker.add(13)
            elif counter <= 8:  # 2 highest part of thighs
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 24])
                    checker.add(24)
                else:
                    writer.writerow([marker.id, 14])
                    checker.add(14)
            elif counter <= 12:  # 4 markers for back
                writer.writerow([marker.id, 5 * 10 + counter - 8])
                checker.add(5 * 10 + counter - 8)
            elif counter <= 14:  # 2 highest part of arm
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 41])
                    checker.add(41)
                else:
                    writer.writerow([marker.id, 31])
                    checker.add(31)
            elif counter <= 16:  # 2 lowest part of arm
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 42])
                    checker.add(42)
                else:
                    writer.writerow([marker.id, 32])
                    checker.add(32)
            elif counter <= 18:  # 2 highest part of forearm
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 43])
                    checker.add(43)
                else:
                    writer.writerow([marker.id, 33])
                    checker.add(33)
            elif counter <= 20:  # 2 lowest part of forearm
                if marker.pos.x > 0:
                    writer.writerow([marker.id, 44])
                    checker.add(44)
                else:
                    writer.writerow([marker.id, 34])
                    checker.add(34)
            else:
                break
            counter += 1
    if len(checker) == 20:
        print("description is created")
    else:
        print("description is bad")
        print(checker)


def get_name_from_time():
    temp = '_'.join(time.ctime().split())
    return '_'.join(temp.split(":"))


def receive_new_frame(frame_number, markers_data, rigid_body_count, labeled_marker_count, timestamp, is_recording):
    global RECORDING, TIME_START, IS_FIRST

    # create descriptions
    if IS_FIRST:
        create_markers_description(markers_data)
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
    if not os.path.exists(DIR):
        os.mkdir(DIR)

    PATH = DIR + get_name_from_time() + r"/"

    os.mkdir(PATH)

    streaming_client = NatNetClient()

    streaming_client.newFrameListener = receive_new_frame

    streaming_client.run()
