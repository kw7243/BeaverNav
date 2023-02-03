from ast import Str
from collections import defaultdict
from math import floor
import os
import pickle
import json

from path_finding_prototype import *
import random
from create_file_paths import *

with open(f"{reduced_res_png_dir}/scaling_factors.json") as f:
    scaling_factors = json.load(f)
with open(special_features, 'r') as out:
    special_features = json.load(out)
random.seed(10) # for reproducibility


def main():
    for graph_name in os.listdir(graph_storage_dir):
        floor_plan = graph_name[:-13]
        print(floor_plan)
        # if floor_plan != "1_1":
        #     continue
        if (f"{floor_plan}_graph.pickle" in os.listdir(pruned_graphs) or len(floor_plan) < 1) :
            continue
        scaling_factor = scaling_factors[floor_plan + ".png"]
        with open(txt_dir + '/' + floor_plan + '.json', 'r') as f:
            room_locations = json.load(f)
        try:
            special_feature_coords = special_features[floor_plan][floor_plan]
        except:
            print(f"Floor plan {floor_plan} hasn't been labelled with special features ")
            continue
        pixel_graph = pickle.load(
            open(graph_storage_dir + '/' + graph_name, 'rb'))
        print("loaded")
        for node_type in special_feature_coords:
            if node_type not in ['sa', 'ea']:
                for coord_set in special_feature_coords[node_type]:
                    string_version = str((coord_set[0], coord_set[1]))
                    room_locations.append([node_type, string_version])
        old_rooms = room_locations.copy()
        room_locations = []
        for room in old_rooms:
            if room [0] in ["ELEV", "STAIR"]:
                continue
            room_locations.append(room)
        # print(room_locations)
        relevant_pixels = set()
        relevant_nodes = set()
        guarantee_check = {}
        iter = 0 # make sure that the program doesn't get held up on some irrelevant floorplan
        while (len(guarantee_check) / len(room_locations) + iter/100) < 0.99:
            print("Iteration ", iter)
            iter += 1
            for iteration in range(2):
                node_queue = room_locations.copy()
                unreachable_nodes = defaultdict(lambda: 0)
                random.shuffle(node_queue)
                while (len(node_queue) > 1):
                    start_location = node_queue[0][1]
                    start_location = (int(start_location.split(',')[0][1:]), int(
                        start_location.split(',')[1][:-1]))
                    end_location = node_queue[1][1]
                    end_location = (int(end_location.split(',')[0][1:]), int(
                        end_location.split(',')[1][:-1]))
                    start_reduced = (
                        int(start_location[0]//scaling_factor), int(start_location[1]//scaling_factor))
                    end_reduced = (
                        int(end_location[0]//scaling_factor), int(end_location[1]//scaling_factor))
                    try:
                        path = Dijkstar_duplicated_graph(
                            pixel_graph, start_reduced, end_reduced)
                    except:
                        print("failed to find a path between", node_queue[0], node_queue[1])
                        unreachable_nodes[start_location] += 1
                        unreachable_nodes[end_location] += 1
                        random.shuffle(node_queue)
                        if max(unreachable_nodes.values()) < 5:
                            continue
                        path = []
                    for (x,y), tag in path:
                        relevant_pixels.add((x,y))

                    node_queue.pop(0)
                    node_queue.pop(0)
                    guarantee_check[start_location] = 1
                    guarantee_check[end_location] = 1
                    # print(start_location,end_location)
        # print(relevant_pixels)
        save_image_with_path_drawn(
            f"{reduced_res_png_dir}/{floor_plan}.png", f"{pruned_graphs}/{floor_plan}.png", relevant_pixels)

        large_node_list = pixel_graph.get_data().copy()
        for node in large_node_list:
            if node[0] not in relevant_pixels:
                pixel_graph.remove_node(node)

        with open(f"{pruned_graphs}/{floor_plan}_graph.pickle", "wb") as f:
            pickle.dump(pixel_graph, f)


if __name__ == '__main__':
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print("TIME TAKEN TO PRUNE GRAPH", end_time - start_time)
