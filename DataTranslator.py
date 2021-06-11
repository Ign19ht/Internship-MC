import csv
import math
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class Vector:
    x: Any
    y: Any
    z: Any


@dataclass
class MarkerData:
    id: int
    pos: Vector


# Constants
PATH_DRAFT = r"Draft/"
PATH_COORDS = r"Coords/"
PATH_ANGLES = r"Angles/"
HEADER_ANGLES = ["time", "leg left", "leg right", "arm left", "arm right"]
HEADER_COORDS = ["time", "id", "x", "y", "z"]
# TODO Record euclidean distance
EUCLIDEAN = [0, 0, 0, 0, 0]


# Global variable
PATH_FROM = ""
PATH_TO = ""
HEADER = ""
fixed_markers = dict()


def translate(markers_data, description):
    pass


def fix_data(markers_data, description):
    global fixed_markers
    fixed_data = dict()
    extra_markers = []
    for bp, marker_id in description:
        fixed_data[marker_id] = None

    # divide markers on fixed and extra markers
    for marker_id, pos in markers_data:
        if marker_id in fixed_data:
            fixed_data[marker_id] = pos
        elif marker_id in fixed_markers:
            fixed_data[fixed_markers[marker_id]] = pos
        else:
            extra_markers.append(MarkerData(marker_id, pos))

    # check for disappeared markers
    for marker_id, pos in fixed_data:
        if pos is None:
            bp = 0
            for marker_bp, mk_id in description:
                if mk_id == marker_id:
                    bp = marker_bp
                    break

            dist = EUCLIDEAN[(bp - 10) // 20 * 2 + (bp % 10 - 1) // 2 - bp // 53]

            pair_bp = bp - 1 if bp % 2 == 0 else bp + 1
            pair_id = description[pair_bp]

            if fixed_data[pair_id] is None:
                print("Bone disappeared", bp, pair_bp)
            else:
                pair_pos = fixed_data[pair_id]
                for marker in extra_markers:
                    # TODO add error
                    if dist == get_distance(pair_pos, marker.pos):
                        fixed_data[marker_id] = marker.pos
                        fixed_markers[marker.id] = marker_id
                        break

    result = []
    for marker_id, pos in fixed_data:
        if pos is not None:
            result.append(MarkerData(marker_id, pos))
    result.sort(key=lambda marker: marker.id)
    return result


def make_angles(markers_data, description):
    angles = []
    for body_part in description:
        marker1 = markers_data[body_part[0]]
        marker2 = markers_data[body_part[1]]
        marker3 = markers_data[body_part[2]]
        marker4 = markers_data[body_part[3]]

        bone1 = Vector(marker2.x - marker1.x, marker2.y - marker1.y, marker2.z - marker1.z)
        bone2 = Vector(marker3.x - marker4.x, marker3.y - marker4.y, marker3.z - marker4.z)

        len_bone1 = math.sqrt(bone1.x ** 2 + bone1.y ** 2 + bone1.z ** 2)
        len_bone2 = math.sqrt(bone2.x ** 2 + bone2.y ** 2 + bone2.z ** 2)

        cos = (bone1.x * bone2.x + bone1.y * bone2.y + bone1.z * bone2.z) / (len_bone1 * len_bone2)

        angles.append(math.degrees(math.acos(cos)))
    return angles


def save_data(package_name, file_name, data, time):
    pass


def save_coords(package_name, file_name, markers_data, time):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for marker in markers_data:
            writer.writerow([time, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def save_angles(package_name, file_name, angles, time):
    with open(PATH_ANGLES + package_name + r"/" + file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([time] + angles)


def create_csv(package_name, file_name):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'w', newline='') as csv_file:
        csv.writer(csv_file).writerow(HEADER)


def get_description(package_name):
    pass


def get_description_for_coords(package_name):
    description = dict()
    with open(PATH_DRAFT + package_name + r"/BP.csv", 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            description[row["body part"]] = row["id"]
    return description


def get_description_for_angles(package_name):
    description = [[0 for _ in range(4)] for _ in range(4)]
    with open(PATH_ANGLES + package_name + r"/BP.csv") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            f = int(row["body part"]) // 10 - 1
            l = int(row["body part"]) % 10 - 1
            description[f][l] = row["id"]
    return description


def get_distance(pos1, pos2):
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)


def start():
    for package in os.listdir(PATH_FROM):
        print(package + ":")

        # check for exist
        if package in os.listdir(PATH_TO):
            print("has already been done")
            continue
        else:
            os.mkdir(PATH_TO + package)

        # get files
        files = os.listdir(PATH_FROM + package)

        # initialize description
        description = get_description(package)

        # translation files
        for file in files:
            if file == "BP.csv":
                continue

            print(file + ":", end=" ")

            create_csv(package, file)

            with open(PATH_FROM + package + r"/" + file) as csv_file:
                reader = csv.DictReader(csv_file)
                current_time = "0.0"
                markers_data = dict()
                for row in reader:
                    if current_time != row["time"]:
                        save_data(package, file, translate(markers_data, description), current_time)
                        current_time = row["time"]
                        markers_data.clear()
                    markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
                save_data(package, file, translate(markers_data, description), current_time)

            print("done")


if __name__ == '__main__':
    print("0: Fix Data")
    print("1: Translate to angles")
    a = int(input())
    if a == 0:
        PATH_TO = PATH_COORDS
        PATH_FROM = PATH_DRAFT
        HEADER = HEADER_COORDS
        save_data = save_coords
        translate = fix_data
    else:
        PATH_TO = PATH_ANGLES
        PATH_FROM = PATH_COORDS
        HEADER = HEADER_ANGLES
        save_data = save_angles
        translate = make_angles

    if not os.path.exists(PATH_TO):
        os.mkdir(PATH_TO)

    start()
