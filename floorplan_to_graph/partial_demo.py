import json
import _pickle as pickle
import path_finding_testing as pf
from graph_class import Node, Internal_Graph
from dijkstar import find_path
import os

results_dir = "backend_file_storage/results"
abstract_graph_path = "backend_file_storage/abstract_graph.pickle"
with open(abstract_graph_path, 'rb') as f:
    abstract_graph = pickle.load(f)
graph_storage_dir = "backend_file_storage/pruned_graphs"
txt_dir = "backend_file_storage/text_locations"
floorplan_name_graph_correspondence_dir = "backend_file_storage/graph_creation_reduced_res_png/scaling_factors.json"
cropped_png_files_dir = "backend_file_storage/cropped_png_files"

graph_storage_dir = "backend_file_storage/pruned_graphs"


def find_path_same_floor(start_location, end_location, floor_plan):
    graph_name = floor_plan + "_graph.pickle"
    pixel_graph = pickle.load(open(graph_storage_dir + '/' + graph_name, 'rb'))

    # print(room_locations)

    # get location of start room as a pixel
    # get location of end room as a pixel

    # print(start_location, end_location)
    # get scaling factor
    with open(floorplan_name_graph_correspondence_dir) as f:
        scaling_factors = json.load(f)
    scaling_factor = scaling_factors[floor_plan + '.png']
    # print(scaling_factor)
    # scale locations
    # get graph
    # ffed into test_path_finding
    return pf.test_path_finding(cropped_png_files_dir, floor_plan,
                                pixel_graph, start_location, end_location, scaling_factor)

import time as time

def main(start_building_room, destination_building_room):
    # start_building_room = "1-190"
    # destination_building_room = "1-115"

    # 1-190 --> 1-115
    # 1-190 --> 10-100LA
    print("PATH_FINDING_STARTED")
    start_time_all = time.perf_counter()
    list_of_messages = []

    start_building = start_building_room.split('-')[0]
    destination_building = destination_building_room.split('-')[0]

    start_floor = start_building_room.split('-')[1][0]
    destination_floor = destination_building_room.split('-')[1][0]

    with open(txt_dir + '/' + str(start_building) + "_" + str(start_floor) + '.json', 'r') as f:
        room_locations_start = json.load(f)
    with open(txt_dir + '/' + str(destination_building) + "_" + str(destination_floor) + '.json', 'r') as f:
        room_locations_end = json.load(f)
    for rooms in room_locations_start:
        if rooms[0] == start_building_room.split('-')[-1]:
            start_location = rooms[1]
            start_location = (int(start_location.split(',')[0][1:]), int(
                start_location.split(',')[1][:-1]))
    for rooms in room_locations_end:
        if rooms[0] == destination_building_room.split('-')[-1]:
            end_location = rooms[1]
            end_location = (int(end_location.split(',')[0][1:]), int(
                end_location.split(',')[1][:-1]))

    if [start_building, start_floor] == [destination_building, destination_floor]:
        floor_plan = str(start_building) + "_" + str(start_floor)
        filename = find_path_same_floor(
            start_location, end_location, floor_plan)
        list_of_messages = []
        dictionary = {}
        dictionary['text'] = 'same floorplan'
        dictionary['image_data'] = filename
        list_of_messages.append(dictionary)
        print("FULL TIME TAKEN: ",time.perf_counter() - start_time_all)
        return list_of_messages

    # find a path from supernodes corresponding to start floor plan to end floor plan
    for node in abstract_graph.get_data():
        if node.type == 'supernode' and node.building == start_building and node.floor == int(start_floor):
            # print("success")
            start_supernode = node
        if node.type == 'supernode' and node.building == destination_building and node.floor == int(destination_floor):
            # print("success")
            end_supernode = node

    abstract_path = find_path(abstract_graph, start_supernode, end_supernode)
    nodes, edges, costs, total_cost = abstract_path
    # print([str(node) for node in nodes])
    # returns a list of Node objects on that path
    # run individual path finding on 0-1, 2-3, 2i -> 2i + 1

    def staircase_instruction(node, next_node):
        if node.type == 'sh':
            return f"\nTake staircase to floor {next_node.floor}."
        elif node.type == 'eh':
            return f"\nTake elevator to floor {next_node.floor}."
        else:
            return ''

    print(nodes)
    for i in range(len(nodes)//2):
        dictionary = {}

        if i == 0:
            floor_plan = str(start_building) + "_" + str(start_floor)
            print("Starting at Building ", str(start_building),
                  " and Floor ", str(start_floor))

            dictionary['text'] = "Starting at Building " + \
                str(start_building) + " and Floor " + str(start_floor)
            ee_location = nodes[2*i + 1].coordinates
            if len(nodes) >= 2:
                dictionary['text'] += staircase_instruction(nodes[2*i + 1], nodes[2*i + 3])
                print(dictionary['text'])
            # print(ee_location)
            filename = find_path_same_floor(
                start_location, ee_location, floor_plan)
            dictionary['image_data'] = filename
            list_of_messages.append(dictionary)
            continue

        if i == len(nodes)//2 - 1:
            floor_plan = str(destination_building) + \
                "_" + str(destination_floor)
            print("End at Building ", str(destination_building),
                  " and Floor ", str(destination_floor))
            dictionary['text'] = " End at Building " + \
                str(destination_building) + \
                " and Floor " + str(destination_floor)
            ee_location = nodes[2*i].coordinates
            # print(ee_location)
            filename = find_path_same_floor(
                ee_location, end_location, floor_plan)
            dictionary['image_data'] = filename
            list_of_messages.append(dictionary)
            continue

        if nodes[2*i].type == 'ea' or nodes[2*i].type == 'sa':
            continue

        ee_location1 = nodes[2*i].coordinates
        ee_location2 = nodes[2*i+1].coordinates
        print("Then go to Building ", str(
            nodes[2*i].building), " and Floor ", str(nodes[2*i].floor))

        dictionary['text'] = "Then go to Building " + \
            str(nodes[2*i].building) + " and Floor " + str(nodes[2*i].floor) + staircase_instruction(nodes[2*i + 1], nodes[2*i + 3])
        print(dictionary['text'])
        floor_plan = str(nodes[2*i].building)+'_'+str(nodes[2*i].floor)
        # print(ee_location1,ee_location2)
        filename = find_path_same_floor(ee_location1, ee_location2, floor_plan)
        dictionary['image_data'] = filename
        list_of_messages.append(dictionary)

    print("FULL TIME TAKEN: ",time.perf_counter() - start_time_all)
    return list_of_messages


if __name__ == '__main__':
    for f in os.listdir(results_dir):
        os.remove(results_dir + '/' + f)
    print("")
    start = str(input("Start Location: "))
    end = str(input("End Destination: "))
    print("")
    output = main(start, end)
    print(output)
