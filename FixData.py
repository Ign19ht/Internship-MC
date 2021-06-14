import csv
import math
import os
import shutil
from dataclasses import dataclass
from pathlib import Path


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
EUCLIDEAN = [0.2459, 0.2756, 0.1446, 0.1752, 0.0642]  # distance between 2 marker in one bone
ERROR = 0.0021
files_in_coords = os.listdir(PATH_COORDS)
files_in_draft = os.listdir(PATH_DRAFT)


# Global variable
fixed_markers = dict()  # {id of new marker: id of marker from bp file}


def csv_save(package_name, file_name, markers_data, time):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for marker in markers_data:
            writer.writerow([time, marker.id, marker.pos.x, marker.pos.y, marker.pos.z])


def create_csv(package_name, file_name):
    with open(PATH_COORDS + package_name + r"/" + file_name, 'w', newline='') as csv_file:
        csv.writer(csv_file).writerow(HEADER)


def get_description(package_name):
    description = dict()
    with open(PATH_DRAFT + package_name + r"/BP.csv", 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            description[int(row["body part"])] = row["id"]
    return description


def get_distance(pos1, pos2):
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)


def fix_data(markers_data, description):
    global fixed_markers
    fixed_data = dict()  # {marker id from bp file: position of this marker}
    extra_markers = []
    # fill dict
    for bp, marker_id in description.items():
        fixed_data[marker_id] = None

    # divide markers on fixed and extra markers
    for marker_id, pos in markers_data.items():
        if marker_id in fixed_data:  # if marker didn't disappear
            fixed_data[marker_id] = pos
        elif marker_id in fixed_markers:  # if marker disappeared but we have found it
            fixed_data[fixed_markers[marker_id]] = pos
        else:
            extra_markers.append(MarkerData(marker_id, pos))

    # check for disappeared markers
    for marker_id, pos in fixed_data.items():
        if pos is None:  # if marker disappeared
            bp = 0
            for marker_bp, mk_id in description.items():  # get name of body part of disappeared marker
                if mk_id == marker_id:
                    bp = marker_bp
                    break

            euclidean_dist = EUCLIDEAN[(bp - 10) // 20 * 2 + (bp % 10 - 1) // 2 - bp // 53]  # get distance for its bone

            # find pair for disappeared marker
            pair_bp = bp - 1 if bp % 2 == 0 else bp + 1
            pair_id = description[pair_bp]

            if fixed_data[pair_id] is None:  # if the pair disappeared also
                print("Bone disappeared", bp, pair_bp)
            else:
                pair_pos = fixed_data[pair_id]
                for marker in extra_markers:  # searching disappeared marker among extra markers
                    dist = get_distance(pair_pos, marker.pos)
                    if euclidean_dist + ERROR >= dist >= euclidean_dist - ERROR:
                        fixed_data[marker_id] = marker.pos
                        fixed_markers[marker.id] = marker_id
                        break

    # convert data from dict to sorted list by marker id
    result = []
    for marker_id, pos in fixed_data.items():
        if pos is not None:
            result.append(MarkerData(marker_id, pos))
    result.sort(key=lambda marker: marker.id)
    return result


def read_draft():
    for package in files_in_draft:
        print(package + ":")

        # check for exist
        if package in files_in_coords:
            print("has already been done")
            continue
        else:
            os.mkdir(PATH_COORDS + package)

        # get files
        files = sorted(Path(r"Draft/Fri_Jun_11_13_10_00_2021").iterdir(), key=os.path.getmtime)
        # files = os.listdir(PATH_DRAFT + package)
        # files.sort(key=os.path.getctime)

        # get description
        description = get_description(package)

        # copy bp file from draft to coords
        shutil.copyfile(PATH_DRAFT + package + r"/BP.csv", PATH_COORDS + package + r"/BP.csv")

        # fix files
        for file in files:
            if file.name == "BP.csv":
                continue

            print(file.name + ":", end=" ")

            # create new csv file
            create_csv(package, file.name)

            with open(PATH_DRAFT + package + r"/" + file.name) as csv_file:
                reader = csv.DictReader(csv_file)
                current_time = "0.0"
                markers_data = dict()
                # reading data at one point in time, fix them and save in new file
                for row in reader:
                    if current_time != row["time"]:
                        csv_save(package, file.name, fix_data(markers_data, description), current_time)
                        current_time = row["time"]
                        markers_data.clear()
                    markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
                csv_save(package, file.name, fix_data(markers_data, description), current_time)

            print("done")


if __name__ == "__main__":
    # if package Coords doesn't exist
    if not os.path.exists(PATH_COORDS):
        os.mkdir(PATH_COORDS)

    read_draft()
