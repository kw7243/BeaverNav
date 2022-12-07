from ast import Str
from math import floor
import os
import pickle
import json
from path_finding_prototype import *
import random

graph_storage_dir = "full_pipeline_files_test/graph_storage"
txt_dir = "full_pipeline_files_test/text_locations"
floorplan_name_graph_correspondence_dir = "full_pipeline_files_test/floorplan_name_graph_correspondence/floorplan_name_graph_correspondence.json"
cropped_png_files_dir = "full_pipeline_files_test/cropped_png_files"
reduced_res_png_dir = "full_pipeline_files_test/graph_creation_reduced_res_png"
temp_dir = "full_pipeline_files_test/temp_files"
with open(floorplan_name_graph_correspondence_dir) as f:
    scaling_factors = json.load(f)
abstract_graph = "full_pipeline_files_test/special_feature_coordinates.json"
with open( abstract_graph, 'r') as out:
    special_features = json.load(out)

def main():
    
    for graph_name in os.listdir(graph_storage_dir):
        floor_plan = graph_name[:-13]
        print(floor_plan)
        if floor_plan != "1_1":
            continue
        if f"{floor_plan}_graph.pickle" in os.listdir(temp_dir):
            continue
        pixel_graph = pickle.load(open(graph_storage_dir + '/' + graph_name, 'rb'))
        scaling_factor = scaling_factors[floor_plan][1]
        with open(txt_dir + '/' + floor_plan + '.json', 'r') as f:
            room_locations = json.load(f)
        special_feature_coords = special_features[floor_plan][floor_plan]
        for node_type in special_feature_coords:
            if node_type not in ['sa', 'ea']:
                for coord_set in special_feature_coords[node_type]:
                    string_version = str((coord_set[0],coord_set[1]))
                    room_locations.append([node_type,string_version])
        # print(room_locations)
        relevant_pixels = set()
        relevant_nodes = set()
        guarantee_check = {}
        while len(guarantee_check) < len(room_locations):
            print("Iteration ")
            for iteration in range(2):
                node_queue = room_locations.copy()
                random.shuffle(node_queue)
                while (len(node_queue) > 1):
                    start_location = node_queue[0][1]
                    start_location = (int(start_location.split(',')[0][1:]), int(
                        start_location.split(',')[1][:-1]))
                    end_location = node_queue[1][1]
                    end_location = (int(end_location.split(',')[0][1:]), int(
                        end_location.split(',')[1][:-1]))
                    start_reduced = (int(start_location[0]//scaling_factor), int(start_location[1]//scaling_factor))
                    end_reduced = (int(end_location[0]//scaling_factor), int(end_location[1]//scaling_factor))
                    path = Dijkstar_duplicated_graph(pixel_graph, start_reduced, end_reduced)
                    for (x,y), tag in path:
                        relevant_pixels.add((x,y))
                    node_queue.pop(0)
                    node_queue.pop(0)  
                    guarantee_check[start_location] = 1 
                    guarantee_check[end_location] = 1 
                    # print(start_location,end_location)
        # print(relevant_pixels)
        save_image_with_path_drawn(f"{reduced_res_png_dir}/{floor_plan}.png", f"{temp_dir}/{floor_plan}.png", relevant_pixels)

        large_node_list = pixel_graph.get_data().copy()
        for node in large_node_list:
            if node[0] not in relevant_pixels:
                pixel_graph.remove_node(node)
        
        with open(f"{temp_dir}/{floor_plan}_graph.pickle", "wb") as f:
            pickle.dump(pixel_graph, f)
        



if __name__ == '__main__':
    start_time = time.perf_counter()
    output = main()
    end_time = time.perf_counter()
    print("TIME TAKEN TO PRUNE GRAPH", end_time - start_time)