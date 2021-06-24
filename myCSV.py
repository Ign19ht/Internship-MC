import csv
from enum import Enum


class HeaderType(Enum):
    COORDS = 0
    ANGLES = 1


HEADERS = [["time", "id", "x", "y", "z"],
           ["time", "leg left", "leg right", "arm left", "arm right", "back", "floor/left leg", "floor/right leg"
            "left leg/lower back", "right leg/lower back", "left arm/upper back", "right arm/upper back",
            "left leg/back", "right leg/back", "left arm/back", "right arm/back"]]


class myCSV:
    def __init__(self, path):
        self.path = path

    def save_markers(self, file_name, markers_data, time):
        with open(self.path + r"/" + file_name, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for marker in markers_data:
                writer.writerow([time, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])

    def save_angles(self, file_name, angles, time):
        with open(self.path + r"/" + file_name, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([time] + angles)

    def create_file(self, file_name, type: HeaderType):
        with open(self.path + r"/" + file_name, 'w', newline='') as csv_file:
            csv.writer(csv_file).writerow(HEADERS[type.value])

    @staticmethod
    def get_description(path):
        description = dict()
        with open(path + r"/BP.csv", 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                description[int(row["body part"])] = row["id"]
        return description

    def save_bp(self, description: dict):
        with open(self.path + "/BP.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "body part"])
            for bp, id in description.items():
                writer.writerow([id, bp])
