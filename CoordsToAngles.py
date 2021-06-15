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
HEADER = ["time", "leg left", "leg right", "arm left", "arm right", "back",
          "left leg/lower back", "right leg/lower back", "left arm/upper back", "right arm/upper back",
          "left leg/back", "right leg/back", "left arm/back", "right arm/back"]

files_in_coord = os.listdir(PATH_COORDS)
files_in_angles = os.listdir(PATH_ANGLES)


def get_angle_between_bones(bone1, bone2):
    if bone1 is None or bone2 is None:
        return 0

    len_bone1 = math.sqrt(bone1.x ** 2 + bone1.y ** 2 + bone1.z ** 2)
    len_bone2 = math.sqrt(bone2.x ** 2 + bone2.y ** 2 + bone2.z ** 2)

    cos = (bone1.x * bone2.x + bone1.y * bone2.y + bone1.z * bone2.z) / (len_bone1 * len_bone2)

    return math.degrees(math.acos(cos))


def make_angles(markers_data, description):
    bones = []
    angles = []
    for body_part in description:
        marker1 = markers_data[body_part[0]] if body_part[0] in markers_data else None
        marker2 = markers_data[body_part[1]] if body_part[1] in markers_data else None
        marker3 = markers_data[body_part[2]] if body_part[2] in markers_data else None
        marker4 = markers_data[body_part[3]] if body_part[3] in markers_data else None

        bone1 = None
        bone2 = None
        if marker1 is not None and marker2 is not None:
            bone1 = Vector(marker2.x - marker1.x, marker2.y - marker1.y, marker2.z - marker1.z)
        if marker3 is not None and marker4 is not None:
            bone2 = Vector(marker3.x - marker4.x, marker3.y - marker4.y, marker3.z - marker4.z)

        angles.append(get_angle_between_bones(bone1, bone2))
        bones.append(bone1)
        bones.append(bone2)

        # hole back
        if len(bones) == 10:
            back1 = None
            back2 = None
            if marker1 is not None and marker4 is not None:
                back1 = Vector(marker4.x - marker1.x, marker4.y - marker1.y, marker4.z - marker1.z)
                back2 = Vector(marker1.x - marker4.x, marker1.y - marker4.y, marker1.z - marker4.z)
            bones.append(back1)
            bones.append(back2)

    # angles between:

    # lower back and left leg
    angles.append(get_angle_between_bones(bones[1], bones[8]))

    # lower back and right leg
    angles.append(get_angle_between_bones(bones[3], bones[8]))

    # upper back and left arm
    angles.append(get_angle_between_bones(bones[4], bones[9]))

    # upper back and right arm
    angles.append(get_angle_between_bones(bones[6], bones[9]))

    # hole back and left leg
    angles.append(get_angle_between_bones(bones[1], bones[10]))

    # hole back and right leg
    angles.append(get_angle_between_bones(bones[3], bones[10]))

    # hole back and left arm
    angles.append(get_angle_between_bones(bones[4], bones[11]))

    # hole back and right arm
    angles.append(get_angle_between_bones(bones[6], bones[11]))

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
        description = [[0 for _ in range(4)] for _ in range(5)]

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
