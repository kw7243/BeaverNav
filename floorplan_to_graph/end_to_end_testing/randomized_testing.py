from distutils.command.build import build
import sys
import os
import json
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from create_file_paths import *
import end_to_end_navigation_basic

def process_location_coordinates(coord_str):
    coord_str = coord_str.replace('(','')
    coord_str = coord_str.replace(')','')
    coord_str = coord_str.replace(' ','')
    coord_str = coord_str.split(',')
    coord_str = (int(coord_str[0]),int(coord_str[1]))
    return coord_str

# generate a list of floorplans
def generate_list_of_floorplans():
    floorplans = []
    for file in os.listdir(pruned_graphs):
        if ".pickle" in file:
            floorplan = file[:-7].split('_')[:2]
            if floorplan not in floorplans:
                floorplans.append(floorplan)
    return floorplans

# generate a list of all the rooms 
def generate_list_of_rooms():
    all_rooms = []
    for txt_file in os.listdir(cleaned_txt_dir):
        if ".json" not in txt_file:
            continue
        floorplan = txt_file[:-4].split('_')[:2]
        room_nodes = {}
        with open(f"{cleaned_txt_dir}/{txt_file}", 'r') as f:
            room_nodes = json.load(f)
        for room in room_nodes:
            all_rooms.append([floorplan[0], floorplan[1], room[0], process_location_coordinates(room[1])])
    return all_rooms

# generate pairs of rooms randomly

# run path finding continuously 

# store all results in a new folder

def run_all_tests(correct_paths, all_rooms):
    errors = []
    sampling = random.sample(all_rooms, 100)
    while(len(sampling) > 0):
        start_room = sampling.pop(0)
        start_room = start_room[0] + '-' + start_room[2]
        end_room = sampling.pop(0)
        end_room = end_room[0] + '-' + end_room[2]
        if (start_room, end_room) in correct_paths:
            continue
        print("Testing navigation from ", start_room, ' to ', end_room)
        try:
            end_to_end_navigation_basic.main(start_room, end_room)
        except Exception as e:
            errors.append("NAVIGATION FAILED FROM " +  start_room +  " TO " + end_room + " "  + str(e))
            print("NAVIGATION FAILED FROM ", start_room, " TO ", end_room)
            print(e)
        correct_paths.append((start_room, end_room))
        print(correct_paths)
    print(errors)
    with open(testing_results, 'w') as f:
        json.dump( correct_paths, f, indent=5)
    with open(testing_errors, 'w') as f:
            json.dump(errors, f, indent=5)

# catch error and print the rooms that caused it 

def main():
    generate_list_of_floorplans()
    all_rooms = generate_list_of_rooms()
    correct_paths = []
    try:
        with open(testing_results, 'r') as f:
            correct_paths = json.load(f)
    except:
        pass
    run_all_tests(correct_paths, all_rooms)


if __name__ == "__main__":
    main()