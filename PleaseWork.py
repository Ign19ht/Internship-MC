from MarkerDataTypes import MarkerData, Vector
from NatNetClient import NatNetClient
import time
from myCSV import myCSV, HeaderType
import os
from FixData import FixData

# Constants
DIR_DRAFT = r"Draft/"
DIR_COORDS = r"Coords/"
TEMP = "temp.csv"
TYPES = {1: "stoop",
         2: "squat",
         3: "sitStand"}


class Record:
    def __init__(self):
        self.recording = False
        self.is_first = True
        self.time_start = 0
        self.count = [0, 0, 0]
        self.description = dict()
        self.fixer = FixData()
        temp = '_'.join(time.ctime().split())
        package_name = '_'.join(temp.split(":"))
        self.draft_path = DIR_DRAFT + package_name
        self.coords_path = DIR_COORDS + package_name
        self.draft_csv = myCSV(self.draft_path)
        self.coords_csv = myCSV(self.coords_path)
        os.mkdir(self.draft_path)
        os.mkdir(self.coords_path)

    def set_file_name(self):
        print("Input type:")
        type = int(input())
        if type == 0:
            os.remove(self.draft_path + r"/" + TEMP)
            os.remove(self.coords_path + r"/" + TEMP)
            print("deleted")
        else:
            self.count[type - 1] += 1
            os.rename(self.draft_path + r"/" + TEMP,
                      self.draft_path + r"/" + TYPES[type] + "_" + str(self.count[type - 1]) + ".csv")
            os.rename(self.coords_path + r"/" + TEMP,
                      self.coords_path + r"/" + TYPES[type] + "_" + str(self.count[type - 1]) + ".csv")
            print("name is set")

    def create_markers_description(self, markers_data):
        markers_data.sort(key=lambda marker: marker.pos.z)
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
                    self.description[21] = marker.id
                else:
                    self.description[11] = marker.id
            elif counter <= 4:  # 2 highest part of shins
                if marker.pos.x > 0:
                    self.description[22] = marker.id
                else:
                    self.description[12] = marker.id
            elif counter <= 6:  # 2 lowest part of thighs
                if marker.pos.x > 0:
                    self.description[23] = marker.id
                else:
                    self.description[13] = marker.id
            elif counter <= 8:  # 2 highest part of thighs
                if marker.pos.x > 0:
                    self.description[24] = marker.id
                else:
                    self.description[14] = marker.id
            elif counter <= 12:  # 4 markers for back
                self.description[5 * 10 + counter - 8] = marker.id
            elif counter <= 14:  # 2 highest part of arm
                if marker.pos.x > 0:
                    self.description[41] = marker.id
                else:
                    self.description[31] = marker.id
            elif counter <= 16:  # 2 lowest part of arm
                if marker.pos.x > 0:
                    self.description[42] = marker.id
                else:
                    self.description[32] = marker.id
            elif counter <= 18:  # 2 highest part of forearm
                if marker.pos.x > 0:
                    self.description[43] = marker.id
                else:
                    self.description[33] = marker.id
            elif counter <= 20:  # 2 lowest part of forearm
                if marker.pos.x > 0:
                    self.description[44] = marker.id
                else:
                    self.description[34] = marker.id
            else:
                break
            counter += 1
        if len(self.description) == 20:
            print("description is created")
        else:
            print("description is bad")
            print(self.description)

    def receive_new_frame(self, frame_number, markers_data, rigid_body_count, labeled_marker_count, timestamp, is_recording):
        # create descriptions
        if self.is_first:
            self.create_markers_description(markers_data)
            self.draft_csv.save_bp(self.description)
            self.coords_csv.save_bp(self.description)
            self.is_first = False

        if not self.recording and is_recording:
            self.recording = True
            self.time_start = timestamp
            print("started")
            self.draft_csv.create_file(TEMP, HeaderType.COORDS)
            self.coords_csv.create_file(TEMP, HeaderType.COORDS)

        if self.recording and not is_recording:
            self.recording = False
            print("stopped")
            self.set_file_name()

        if self.recording:
            self.draft_csv.save_markers(markers_data, timestamp - self.time_start)
            self.coords_csv.save_markers(self.fixer.fix_data(markers_data, self.description), timestamp - self.time_start)


if __name__ == '__main__':
    if not os.path.exists(DIR_DRAFT):
        os.mkdir(DIR_DRAFT)

    if not os.path.exists(DIR_COORDS):
        os.mkdir(DIR_COORDS)

    recorder = Record()

    streaming_client = NatNetClient()

    streaming_client.newFrameListener = recorder.receive_new_frame

    streaming_client.run()
