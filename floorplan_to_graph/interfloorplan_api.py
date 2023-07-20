from curses.ascii import isalpha
import json
import _pickle as pickle
from floorplan_graph_creation import *
import path_finding_testing
from dijkstar import find_path
import os
from create_file_paths import *
import time

with open(abstract_graph, 'rb') as f:
    abstract_graph = pickle.load(f)

import time as time

def main(start_building_room, destination_building_room):
    # start_building_room = "1-190"
    # destination_building_room = "1-115"

    # 1-190 --> 1-115
    # 1-190 --> 10-100LA
    print("PATH_FINDING_STARTED")
    start_time_all = time.perf_counter()

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
            start_location = [int(start_location.split(',')[0][1:]), int(
                start_location.split(',')[1][:-1])]
    for rooms in room_locations_end:
        if rooms[0] == destination_building_room.split('-')[-1]:
            end_location = rooms[1]
            end_location = [int(end_location.split(',')[0][1:]), int(
                end_location.split(',')[1][:-1])]
    if len(start_location) == 0:
        raise Exception("Start Location Not Found")
    if len(end_location) == 0:
        raise Exception("End Location Not Found")



    if [start_building, start_floor] == [destination_building, destination_floor]:
        floor_plan = str(start_building) + "_" + str(start_floor)
        path_list = [{'floorplan': floor_plan, 'start': start_location, 'end': end_location}]
        print("FULL TIME TAKEN: ",time.perf_counter() - start_time_all)
        return path_list

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

        if node.type == 'supernode' and node.building == start_building and node.floor == int(compare_floor):
            # print("success")
            start_supernode = node
        if node.type == 'supernode' and node.building == destination_building and node.floor == int(compare_floor_2):
            # print("success")
            end_supernode = node

    abstract_path = find_path(abstract_graph, start_supernode, end_supernode)
    nodes, edges, costs, total_cost = abstract_path

    path_list = []

    # Do navigation for first node:
    floor_plan = str(start_building) + "_" + str(start_floor)
    first_floorplan = {}
    first_floorplan['floorplan'] = floor_plan
    first_floorplan['start'] = f"Room {start_building_room.split('-')[-1]}"
    first_floorplan['start location'] = start_location
    ee_location = nodes[1].coordinates
    first_floorplan['end'] = f"Entry to {str(nodes[2].building)+'-'+str(nodes[2].floor)}"
    first_floorplan['end location'] = ee_location

    nodes.pop(0)    
    cur_node = nodes.pop(0)   
    next_node = None 

    path_list.append(first_floorplan)

    # Do navigation for nodes in the middle
    while(len(nodes) > 2):
        start_text = f"Exit from {str(cur_node.building)+'-'+str(cur_node.floor)}"
        if cur_node.type=='sh': start_text = 'Stairs'
        if cur_node.type=='eh': start_text = 'Elevator'
        cur_node = nodes.pop(0)
        if cur_node.type == 'ea' or cur_node.type == 'sa':
            print("Keep going to floor ", nodes[0].floor)
            continue
        next_node = nodes.pop(0)
        end_text = f"Entry to {str(nodes[0].building)+'-'+str(nodes[0].floor)}"
        if next_node.type=='sh': end_text = 'Stairs'
        if next_node.type=='eh': end_text = 'Elevator'
        ee_location1 = cur_node.coordinates
        ee_location2 = next_node.coordinates
        floor_plan = str(cur_node.building)+'_'+str(cur_node.floor)
        path_list.append({'floorplan': floor_plan, 'start': start_text, 'start location': ee_location1, 'end': end_text, 'end location': ee_location2})


    start_text = f"Exit from {str(next_node.building)+'-'+str(next_node.floor)}"
    if next_node.type=='sh': start_text = 'Stairs'
    if next_node.type=='eh': start_text = 'Elevator'

    floor_plan = str(destination_building) + \
        "_" + str(destination_floor)
    ee_location = nodes[0].coordinates
    path_list.append({'floorplan': floor_plan, 'start': start_text, 'start location': ee_location, 'end': f"Room {destination_building_room.split('-')[-1]}", 'end location': end_location})
    
    print("FULL TIME TAKEN: ",time.perf_counter() - start_time_all)
    return path_list


if __name__ == '__main__':
    for f in os.listdir(results_dir):
        os.remove(results_dir + '/' + f)
    print("")
    start = str(input("Start Location: "))
    end = str(input("End Destination: "))
    print("")
    output = main(start, end)
    print(output)
