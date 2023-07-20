from curses.ascii import isalpha
import json
import _pickle as pickle
from floorplan_graph_creation import *
import path_finding_testing
from dijkstar import find_path
import os
from create_file_paths import *
import time
import cv2

def main(start_location, end_location, floor_plan):
    graph_name = floor_plan + "_graph.pickle"
    if floor_plan != "0_0":
        pixel_graph = pickle.load(open(pruned_graphs + '/' + graph_name, 'rb'))
    else: 
        pixel_graph = outside
    # print(room_locations)

    # get location of start room as a pixel
    # get location of end room as a pixel

    print("start", start_location, "end", end_location)
    # get scaling factor
    with open(scaling_factors_path) as f:
        scaling_factors = json.load(f)
    scaling_factor = scaling_factors[floor_plan + '.png']
    # print(scaling_factor)
    # scale locations
    # get graph
    # ffed into test_path_finding
    new_filename, extra = path_finding_testing.test_path_finding(cropped_png_files_dir, floor_plan,
                                pixel_graph, start_location, end_location, scaling_factor)

    return cv2.imread(new_filename)


if __name__ == '__main__':
    for f in os.listdir(results_dir):
        os.remove(results_dir + '/' + f)
    print("")
    floor_plan = str(input("Floorplan: "))
    start = str(input("Start Pixel Location: "))
    end = str(input("End Pixel Destination: "))
    print("")
    output = main(start, end, floor_plan)
