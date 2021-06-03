from NatNetClient import NatNetClient
import time
import csv

RECORDING = False
TIME_START = 0
TIME_ACTUAL = ""
HEADER = ["time", "id", "x", "y", "z"]


def csv_save(markers_data, timestamp):
    with open(TIME_ACTUAL, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for marker in markers_data:
            writer.writerow([timestamp, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def create_csv():
    with open(TIME_ACTUAL, 'w', newline='') as csvfile:
        csv.writer(csvfile).writerow(HEADER)


def receiveNewFrame(frameNumber, markers_data, labeledMarkerCount, timestamp, isRecording):
    global RECORDING, TIME_START, TIME_ACTUAL
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

    if not RECORDING and isRecording:
        RECORDING = True
        TIME_START = timestamp
        temp = '_'.join(time.ctime().split()) + ".csv"
        TIME_ACTUAL = '_'.join(temp.split(":"))
        TIME_ACTUAL = 'Thursday.csv'
        print(TIME_ACTUAL)
        print("started")
        create_csv()

    if RECORDING and not isRecording:
        RECORDING = False
        print("stopped")

    if RECORDING:
        csv_save(markers_data, timestamp)
        #print("line")


streamingClient = NatNetClient()

streamingClient.newFrameListener = receiveNewFrame

streamingClient.run()
