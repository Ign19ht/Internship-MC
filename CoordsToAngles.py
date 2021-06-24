import csv
import math
import os
from MarkerDataTypes import Vector
from myCSV import myCSV, HeaderType

# Constants
PATH_COORDS = r"Coords/"
PATH_ANGLES = r"Angles/"


class TranslateToAngles:

    def __init__(self):
        self.files_in_coord = os.listdir(PATH_COORDS)
        self.files_in_angles = os.listdir(PATH_ANGLES)

    @staticmethod
    def get_angle_between_bones(bone1, bone2):
        if bone1 is None or bone2 is None:
            return 0

        len_bone1 = math.sqrt(bone1.x ** 2 + bone1.y ** 2 + bone1.z ** 2)
        len_bone2 = math.sqrt(bone2.x ** 2 + bone2.y ** 2 + bone2.z ** 2)

        cos = (bone1.x * bone2.x + bone1.y * bone2.y + bone1.z * bone2.z) / (len_bone1 * len_bone2)

        return math.degrees(math.acos(cos))

    @staticmethod
    def get_vector_of_the_floor(bone):
        if bone is None:
            return None
        else:
            return Vector(bone.x, bone.y, 0)

    @staticmethod
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

            angles.append(TranslateToAngles.get_angle_between_bones(bone1, bone2))
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
        # floor and left leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[0],
                                                                TranslateToAngles.get_vector_of_the_floor(bones[0])))

        # floor and right leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[2],
                                                                TranslateToAngles.get_vector_of_the_floor(bones[2])))

        # lower back and left leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[1], bones[8]))

        # lower back and right leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[3], bones[8]))

        # upper back and left arm
        angles.append(TranslateToAngles.get_angle_between_bones(bones[4], bones[9]))

        # upper back and right arm
        angles.append(TranslateToAngles.get_angle_between_bones(bones[6], bones[9]))

        # hole back and left leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[1], bones[10]))

        # hole back and right leg
        angles.append(TranslateToAngles.get_angle_between_bones(bones[3], bones[10]))

        # hole back and left arm
        angles.append(TranslateToAngles.get_angle_between_bones(bones[4], bones[11]))

        # hole back and right arm
        angles.append(TranslateToAngles.get_angle_between_bones(bones[6], bones[11]))

        return angles

    def translate_all(self):
        for package in self.files_in_coord:
            print(package + ":")

            # check for exist
            if package in self.files_in_angles:
                print("has already been done")
                continue
            else:
                os.mkdir(PATH_ANGLES + package)

            # get files
            files = os.listdir(PATH_COORDS + package)

            # get description
            temp_description = myCSV.get_description(PATH_COORDS + package)
            description = [[0 for _ in range(4)] for _ in range(5)]
            for bp, id in temp_description.items():
                description[bp // 10 - 1][bp % 10 - 1] = id

            # translation files
            for file in files:
                if file == "BP.csv":
                    continue

                print(file + ":", end=" ")

                my_csv = myCSV(PATH_ANGLES + package)
                my_csv.create_file(file, HeaderType.ANGLES)

                with open(PATH_COORDS + package + r"/" + file) as csv_file:
                    reader = csv.DictReader(csv_file)
                    current_time = "0.0"
                    markers_data = dict()
                    for row in reader:
                        if current_time != row["time"]:
                            my_csv.save_angles(file, self.make_angles(markers_data, description), current_time)
                            current_time = row["time"]
                            markers_data.clear()
                        markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
                    my_csv.save_angles(file, self.make_angles(markers_data, description), current_time)

                print("done")


if __name__ == '__main__':
    # if package Coords doesn't exist
    if not os.path.exists(PATH_ANGLES):
        os.mkdir(PATH_ANGLES)

    translator = TranslateToAngles()
    translator.translate_all()
