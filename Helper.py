import csv
import math
import statistics
from dataclasses import dataclass

import numpy


@dataclass
class Vector:
    x: float
    y: float
    z: float


description = [[0 for _ in range(4)] for _ in range(5)]


with open(r"Draft/Fri_Jun_11_13_10_00_2021/BP.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        f = int(row["body part"]) // 10 - 1
        l = int(row["body part"]) % 10 - 1
        description[f][l] = row["id"]

data = [[] for _ in range(5)]


def do(markers_data):
    global data
    for i in range(0, 5):
        marker1 = markers_data[description[i][0]]
        marker2 = markers_data[description[i][1]]
        marker3 = markers_data[description[i][2]]
        marker4 = markers_data[description[i][3]]

        bone1 = Vector(marker2.x - marker1.x, marker2.y - marker1.y, marker2.z - marker1.z)
        bone2 = Vector(marker3.x - marker4.x, marker3.y - marker4.y, marker3.z - marker4.z)

        len_bone1 = math.sqrt(bone1.x ** 2 + bone1.y ** 2 + bone1.z ** 2)
        len_bone2 = math.sqrt(bone2.x ** 2 + bone2.y ** 2 + bone2.z ** 2)

        if i <= 1:
            data[0].append(len_bone1)
            data[1].append(len_bone2)
        elif i <= 3:
            data[2].append(len_bone1)
            data[3].append(len_bone2)
        elif i == 4:
            data[4].append(len_bone1)
            data[4].append(len_bone2)


with open(r"Draft/Fri_Jun_11_13_10_00_2021/squat_2.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    current_time = "0.0"
    markers_data = dict()
    for row in reader:
        if current_time != row["time"]:
            do(markers_data)
            current_time = row["time"]
            markers_data.clear()
        markers_data[row["id"]] = Vector(float(row["x"]), float(row["y"]), float(row["z"]))
    do(markers_data)

for dt in data:
    max = numpy.max(dt)
    min = numpy.min(dt)
    average = (max - min) / 2 + min
    dif = max - average
    print(average, max, min, dif)


