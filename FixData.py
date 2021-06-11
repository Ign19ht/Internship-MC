import csv
import math
import os
from dataclasses import dataclass


@dataclass
class Vector:
    x: float
    y: float
    z: float


@dataclass
class MarkerData:
    id: int
    pos: Vector


# Constants
HEADER = ["time", "id", "x", "y", "z"]
PATH_COORDS = r"Coords/"
PATH_DRAFT = r"Draft/"
# TODO Record euclidean distance
EUCLIDEAN = [0, 0, 0, 0, 0]
files_in_coords = os.listdir(PATH_COORDS)
files_in_draft = os.listdir(PATH_DRAFT)
AMOUNT_OF_MARKERS = 20


# Global variable
fixed_markers = dict()


def csv_save(package_name, file_name, markers_data, time):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for marker in markers_data:
            writer.writerow([time, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def create_csv(package_name, file_name):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'w', newline='') as csv_file:
        csv.writer(csv_file).writerow(HEADER)


def read_bp_file(package_name):
    description = dict()
    with open(PATH_DRAFT + package_name + r"/BP.csv", 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            description[row["id"]] = row["body part"]
    return description


def get_distance(pos1, pos2):
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)


def fix_data(markers_data, description):
    global fixed_markers
    fixed_data = dict()
    extra_markers = []
    for marker_id in description:
        fixed_data[marker_id] = None

    # divide markers on fixed and extra markers
    for marker_id, pos in markers_data:
        if marker_id in description:
            fixed_data[marker_id] = pos
        elif marker_id in fixed_markers:
            fixed_data[fixed_markers[marker_id]] = pos
        else:
            extra_markers.append(MarkerData(marker_id, pos))

    # check for disappeared markers
    for marker_id, pos in fixed_data:
        if pos is None:
            dist = EUCLIDEAN[(bd - 10) // 20 * 2 + (bd % 10 - 1) // 2 - bd // 53]

            pair_bd = bd - 1 if bd % 2 == 0 else bd + 1
            pair_id = 0
            for mk_id, body_part in description:
                if body_part == pair_bd:
                    pair_id = mk_id
                    break

            if fixed_data[pair_id] is None:
                print("Bone disappeared", bd, pair_bd)
            else:
                pair_pos = fixed_data[pair_id]
                for marker in extra_markers:
                    # TODO add error
                    if dist == get_distance(pair_pos, marker.pos):
                        fixed_data[marker_id] = marker.pos
                        fixed_markers[marker.id] = marker_id
                        break

    # result = []
    # for marker_id, pos in fixed_data:
    #     if pos
    # return fixed_data


def read_draft():
    for package in files_in_coords:
        print(package + ":")

        # check for exist
        if package in files_in_draft:
            print("has already been done")
            continue
        else:
            os.mkdir(PATH_COORDS + package)

        # get files
        files = os.listdir(PATH_COORDS + package)

        # get description
        description = read_bp_file(package)

        # fix files
        for file in files:
            if file == "BP.csv":
                continue

            print(file + ":", end=" ")

            create_csv(package, file)

            with open(PATH_DRAFT + package + r"/" + file) as csv_file:
                reader = csv.DictReader(csv_file)
                current_time = "0.0"
                markers_data = dict()
                for row in reader:
                    if current_time != row["time"]:
                        csv_save(package, file, fix_data(markers_data, description), current_time)
                        current_time = row["time"]
                        markers_data.clear()
                    # markers_data.append(MarkerData(row["id"], Vector(float(row["x"]), float(row["y"]), float(row["z"]))))
                    markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
                csv_save(package, file, fix_data(markers_data, description), current_time)

            print("done")


if __name__ == "__main__":
    a = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44, 51, 52, 53, 54]
    for bd in a:
        print(bd, (bd - 10) // 20 * 2 + (bd % 10 - 1) // 2 - bd // 53)
