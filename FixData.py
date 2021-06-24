import csv
from pathlib import Path

from myCSV import myCSV, HeaderType
import math
import os
import shutil
from MarkerDataTypes import MarkerData, Vector

EUCLIDEAN = [0.2459, 0.2756, 0.1446, 0.1752, 0.0642]  # distance between 2 marker in one bone
ERROR = 0.0021


class FixData:
    def __init__(self):
        self.fixed_markers = dict()  # {id of new marker: id of marker from bp file}

    def get_distance(sefl, pos1: Vector, pos2: Vector):
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)

    def fix_data(self, markers_data: [], description: dict):
        fixed_data = dict()  # {marker id from bp file: position of this marker}
        extra_markers = []
        # fill dict
        for bp, marker_id in description.items():
            fixed_data[marker_id] = None

        # divide markers on fixed and extra markers
        for marker in markers_data:
            if marker.id in fixed_data:  # if marker didn't disappear
                fixed_data[marker.id] = marker.pos
            elif marker.id in self.fixed_markers:  # if marker disappeared but we have found it
                fixed_data[self.fixed_markers[marker.id]] = marker.pos
            else:
                extra_markers.append(marker)

        # check for disappeared markers
        is_bad = False
        for marker_id, pos in fixed_data.items():
            if pos is None:  # if marker disappeared
                bp = 0
                for marker_bp, mk_id in description.items():  # get name of body part of disappeared marker
                    if mk_id == marker_id:
                        bp = marker_bp
                        break

                euclidean_dist = EUCLIDEAN[
                    (bp - 10) // 20 * 2 + (bp % 10 - 1) // 2 - bp // 53]  # get distance for its bone

                # find pair for disappeared marker
                pair_bp = bp - 1 if bp % 2 == 0 else bp + 1
                pair_id = description[pair_bp]

                if fixed_data[pair_id] is None:  # if the pair disappeared also
                    is_bad = True
                else:
                    pair_pos = fixed_data[pair_id]
                    for marker in extra_markers:  # searching disappeared marker among extra markers
                        dist = self.get_distance(pair_pos, marker.pos)
                        if euclidean_dist + ERROR >= dist >= euclidean_dist - ERROR:
                            fixed_data[marker_id] = marker.pos
                            self.fixed_markers[marker.id] = marker_id
                            break

        # convert data from dict to sorted list by marker id
        result = []
        for marker_id, pos in fixed_data.items():
            if pos is not None:
                result.append(MarkerData(marker_id, pos))
        result.sort(key=lambda marker: marker.id)
        return result, is_bad

    def post_processing(self):
        path_coords = r"Coords/"
        path_draft = r"Draft/"

        # if package Coords doesn't exist
        if not os.path.exists(path_coords):
            os.mkdir(path_coords)

        files_in_coords = os.listdir(path_coords)
        files_in_draft = os.listdir(path_draft)

        for package in files_in_draft:
            print(package + ":")

            # check for exist
            if package in files_in_coords:
                print("has already been done")
                continue
            else:
                os.mkdir(path_coords + package)

            # get files
            files = sorted(Path(path_draft + package).iterdir(), key=os.path.getmtime)

            # get description
            description = myCSV.get_description()

            # copy bp file from draft to coords
            shutil.copyfile(path_draft + package + r"/BP.csv", path_coords + package + r"/BP.csv")
            print("BP.csv: copied")

            my_csv = myCSV(path_coords + package)

            # fix files
            for file in files:
                if file.name == "BP.csv":
                    continue

                print(file.name + ":", end=" ")

                # create new csv file
                my_csv.create_file(file.name, HeaderType.COORDS)

                with open(path_draft + package + r"/" + file.name) as csv_file:
                    reader = csv.DictReader(csv_file)
                    current_time = "0.0"
                    markers_data = dict()
                    # reading data at one point in time, fix them and save in new file
                    for row in reader:
                        if current_time != row["time"]:
                            # TODO check fix_data (return data, bool)
                            my_csv.save_markers(file.name, self.fix_data(markers_data, description), current_time)
                            current_time = row["time"]
                            markers_data.clear()
                        markers_data = MarkerData(row["id"], Vector(float(row["x"]), float(row["y"]), float(row["z"])))
                    my_csv.save_markers(file.name, self.fix_data(markers_data, description), current_time)

                print("done")

