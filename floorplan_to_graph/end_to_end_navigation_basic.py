from curses.ascii import isalpha
import json
import _pickle as pickle
from floorplan_graph_creation import *
import path_finding_testing
from dijkstar import find_path
import os
from create_file_paths import *

with open(abstract_graph, 'rb') as f:
    abstract_graph = pickle.load(f)


def find_path_same_floor(start_location, end_location, floor_plan):
    graph_name = floor_plan + "_graph.pickle"
    pixel_graph = pickle.load(open(graph_storage_dir + '/' + graph_name, 'rb'))

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
    return path_finding_testing.test_path_finding(cropped_png_files_dir, floor_plan,
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

    if start_building == "32" and start_floor.isalpha() : start_floor = start_building_room.split('-')[1][:2] 
    if destination_building == "32" and destination_floor.isalpha() : destination_floor = destination_building_room.split('-')[1][:2] 
    if start_building == "56" and "00" in start_building_room.split('-')[1]: raise Exception("Navigation to building 56 floor 00 not supported")
    if destination_building_room == "56" and "00" in destination_building_room.split('-')[1]: raise Exception("Navigation to building 56 floor 00 not supported")
    if "M" in start_building_room.split('-')[1]: raise Exception(f"Navigation to {start_building_room} not supported")
    if "M" in destination_building_room.split('-')[1]: raise Exception(f"Navigation to {start_building_room} not supported")
    if "Z" in start_building_room.split('-')[1]: raise Exception(f"Navigation to {start_building_room} not supported")
    if "Z" in destination_building_room.split('-')[1]: raise Exception(f"Navigation to {destination_building_room} not supported")
    if start_building_room[:3] == "3_5" or destination_building_room[:3] == "3_5": raise Exception(f"Navigation to 3_5 not supported")
    if start_building_room[:3] == "8_5" or destination_building_room[:3] == "8_5": raise Exception(f"Navigation to 8_5 not supported")
    if start_building_room[:3] == "6_5" or destination_building_room[:3] == "6_5": raise Exception(f"Navigation to 6_5 not supported")
    if start_building_room[:3] == "4_5" or destination_building_room[:3] == "4_5": raise Exception(f"Navigation to 4_5 not supported")
    if start_building_room[:3] == "18_6" or destination_building_room[:3] == "18_6": raise Exception(f"Navigation to 18_6 not supported")

    with open(cleaned_txt_dir + '/' + str(start_building) + "_" + str(start_floor) + '.json', 'r') as f:
        room_locations_start = json.load(f)
    with open(cleaned_txt_dir + '/' + str(destination_building) + "_" + str(destination_floor) + '.json', 'r') as f:
        room_locations_end = json.load(f)

    # Finding the locations of start and end rooms
    start_location = ''
    end_location = ''
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
    if len(start_location) == 0:
        raise Exception("Start Location Not Found")
    if len(end_location) == 0:
        raise Exception("End Location Not Found")



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
        compare_floor = start_floor
        if "G" in start_floor:
            compare_floor = int(start_floor[1:]) + 40
        if "D" in start_floor:
            compare_floor = int(start_floor[1:]) + 20

        compare_floor_2 = destination_floor
        if "G" in destination_floor:
            compare_floor_2 = int(destination_floor[1:]) + 40
        if "D" in destination_floor:
            compare_floor_2 = int(destination_floor[1:]) + 20
        print()

        if node.type == 'supernode' and node.building == start_building and node.floor == int(compare_floor):
            # print("success")
            start_supernode = node
        if node.type == 'supernode' and node.building == destination_building and node.floor == int(compare_floor_2):
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

    # print(nodes)

    # Do navigation for first node:
    floor_plan = str(start_building) + "_" + str(start_floor)
    print("Starting at Building ", str(start_building),
            " and Floor ", str(start_floor))

    dictionary = {}
    dictionary['text'] = "Starting at Building " + \
        str(start_building) + " and Floor " + str(start_floor)
    ee_location = nodes[1].coordinates
    if len(nodes) >= 2:
        dictionary['text'] += staircase_instruction(nodes[1], nodes[3])
        print(dictionary['text'])
    # print(ee_location)
    filename = find_path_same_floor(
        start_location, ee_location, floor_plan)
    dictionary['image_data'] = filename
    list_of_messages.append(dictionary)
    nodes.pop(0)    
    nodes.pop(0)    

    # Do navigation for nodes in the middle
    while(len(nodes) > 2):
        dictionary = {}
        cur_node = nodes.pop(0)
        if cur_node.type == 'ea' or cur_node.type == 'sa':
            print("Keep going to floor ", nodes[0].floor)
            continue
        next_node = nodes.pop(0)
        ee_location1 = cur_node.coordinates
        ee_location2 = next_node.coordinates
        print("Then go to Building ", str(
            cur_node.building), " and Floor ", str(cur_node.floor))

        dictionary['text'] = "Then go to Building " + \
            str(cur_node.building) + " and Floor " + str(cur_node.floor) + staircase_instruction(next_node, nodes[1])
        print(dictionary['text'])
        floor_plan = str(cur_node.building)+'_'+str(cur_node.floor)
        # print(ee_location1,ee_location2)
        filename = find_path_same_floor(ee_location1, ee_location2, floor_plan)
        dictionary['image_data'] = filename
        list_of_messages.append(dictionary)

    dictionary = {}
    floor_plan = str(destination_building) + \
        "_" + str(destination_floor)
    print("End at Building ", str(destination_building),
            " and Floor ", str(destination_floor))
    dictionary['text'] = " End at Building " + \
        str(destination_building) + \
        " and Floor " + str(destination_floor)
    ee_location = nodes[0].coordinates
    # print(ee_location)
    filename = find_path_same_floor(
        ee_location, end_location, floor_plan)
    dictionary['image_data'] = filename
    list_of_messages.append(dictionary)
    



    # for i in range(len(nodes)//2):
    #     dictionary = {}

    #     if i == 0:
    #         floor_plan = str(start_building) + "_" + str(start_floor)
    #         print("Starting at Building ", str(start_building),
    #               " and Floor ", str(start_floor))

    #         dictionary['text'] = "Starting at Building " + \
    #             str(start_building) + " and Floor " + str(start_floor)
    #         ee_location = nodes[2*i + 1].coordinates
    #         if len(nodes) >= 2:
    #             dictionary['text'] += staircase_instruction(nodes[2*i + 1], nodes[2*i + 3])
    #             print(dictionary['text'])
    #         # print(ee_location)
    #         filename = find_path_same_floor(
    #             start_location, ee_location, floor_plan)
    #         dictionary['image_data'] = filename
    #         list_of_messages.append(dictionary)
    #         continue

    #     if i == len(nodes)//2 - 1:
    #         floor_plan = str(destination_building) + \
    #             "_" + str(destination_floor)
    #         print("End at Building ", str(destination_building),
    #               " and Floor ", str(destination_floor))
    #         dictionary['text'] = " End at Building " + \
    #             str(destination_building) + \
    #             " and Floor " + str(destination_floor)
    #         ee_location = nodes[2*i].coordinates
    #         # print(ee_location)
    #         filename = find_path_same_floor(
    #             ee_location, end_location, floor_plan)
    #         dictionary['image_data'] = filename
    #         list_of_messages.append(dictionary)
    #         continue

    #     if nodes[2*i].type == 'ea' or nodes[2*i].type == 'sa':
    #         print("Keep going to floor ", nodes[2*i + 1].floor)
    #         continue

    #     ee_location1 = nodes[2*i].coordinates
    #     ee_location2 = nodes[2*i+1].coordinates
    #     print("Then go to Building ", str(
    #         nodes[2*i].building), " and Floor ", str(nodes[2*i].floor))

    #     dictionary['text'] = "Then go to Building " + \
    #         str(nodes[2*i].building) + " and Floor " + str(nodes[2*i].floor) + staircase_instruction(nodes[2*i + 1], nodes[2*i + 3])
    #     print(dictionary['text'])
    #     floor_plan = str(nodes[2*i].building)+'_'+str(nodes[2*i].floor)
    #     # print(ee_location1,ee_location2)
    #     filename = find_path_same_floor(ee_location1, ee_location2, floor_plan)
    #     dictionary['image_data'] = filename
    #     list_of_messages.append(dictionary)

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
