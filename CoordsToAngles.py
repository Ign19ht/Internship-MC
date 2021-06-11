import csv
import math
import os
from dataclasses import dataclass


@dataclass
class Vector:
    x: float
    y: float
    z: float


# Constants
PATH_COORDS = r"Coords/"
PATH_ANGLES = r"Angles/"
HEADER = ["time", "leg left", "leg right", "arm left", "arm right"]

files_in_coord = os.listdir(PATH_COORDS)
files_in_angles = os.listdir(PATH_ANGLES)


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


def save_angles(package_name, file_name, angles, time):
    with open(PATH_ANGLES + package_name + r"/" + file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([time] + angles)


def create_angles_file(package_name, file_name):
    with open(PATH_ANGLES + package_name + r"/" + file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(HEADER)


def check_coords_package():
    for package in files_in_coord:
        print(package + ":")

        # check for exist
        if package in files_in_angles:
            print("has already been done")
            continue
        else:
            os.mkdir(PATH_ANGLES + package)

        # get files
        files = os.listdir(PATH_COORDS + package)

        # initialize description
        description = [[0 for _ in range(4)] for _ in range(4)]

        # get description
        with open(PATH_COORDS + package + r"/BP.csv") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                f = int(row["body part"]) // 10 - 1
                l = int(row["body part"]) % 10 - 1
                description[f][l] = row["id"]

        # translation files
        for file in files:
            if file == "BP.csv":
                continue

            print(file + ":", end=" ")

            create_angles_file(package, file)

            with open(PATH_COORDS + package + r"/" + file) as csv_file:
                reader = csv.DictReader(csv_file)
                current_time = "0.0"
                markers_data = dict()
                for row in reader:
                    if current_time != row["time"]:
                        save_angles(package, file, make_angles(markers_data, description), current_time)
                        current_time = row["time"]
                        markers_data.clear()
                    markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
                save_angles(package, file, make_angles(markers_data, description), current_time)

            print("done")


if __name__ == '__main__':
    # if package Coords doesn't exist
    if not os.path.exists(PATH_ANGLES):
        os.mkdir(PATH_ANGLES)

    check_coords_package()
