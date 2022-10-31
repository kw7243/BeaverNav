from distutils.command.build import build
import math
import cv2
import os
import json
from pathlib import Path
import copy

labelled_pngs = "full_pipeline_files_test/labelled_pngs"
cropped_png_files_dir = "full_pipeline_files_test/cropped_png_files"
cropping_offsets= "full_pipeline_files_test/cropping_offsets"
labelling_legend = "full_pipeline_files_test/labelling_legend.json"
final_output_name = "full_pipeline_files_test/special_feature_coordinates.json"

def process_string_coord(coord):
    coord = coord.replace('(','')
    coord = coord.replace(')','')
    coord = coord.replace(' ','')
    coord = coord.split('_')
    coord = tuple(int(item) for item in coord)
    return coord

def process_floorplanname_to_tuple(floorplane_name):
    floorplane_name = floorplane_name.split('_')
    to_return = f'({str(floorplane_name[0])},{str(floorplane_name[1])})'
    return to_return

def find_locations_base_floorplan(floorplans, cropping_offsets, labelled_pngs, building, locations,i=0, prints = False):
    with open(cropping_offsets + '/offsets.json', 'r') as out:
        offsets = json.load(out)
    with open(labelling_legend, 'r') as out:
        legend = json.load(out)

    cropping_offsets = Path(cropping_offsets)
    labelled_pngs = Path(labelled_pngs)
    building = Path(building)

    if prints: print(floorplans)
    ### calculate base
    base_floorplan = floorplans[i][:-4]
    locations[base_floorplan] = {}
    img_path_leaf = Path(floorplans[0])
    img = cv2.imread(str(labelled_pngs / building / img_path_leaf))
    
    if prints: print("base locations here is: ",locations)
    for color in legend[base_floorplan]:
        temp_color = color
        color = color.replace('(','')
        color = color.replace(')','')
        color = color.replace(' ','')
        color = color.split(',')
        color = tuple(int(item) for item in color)
        # have to invert because cv2 uses BGR not RGB
        lower = (max(color[2] - 30,0 ), max(color[1] - 30,0 ), max(color[0] - 30,0 ))
        upper = (min(color[2] + 30,255 ), min(color[1] + 30,255 ), min(color[0] + 30,255 ))
        temp_img = cv2.inRange(img, lower, upper)
        contours, hierarchy = cv2.findContours(temp_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(temp_img, contours, -1, (0,255,0), 3)
        # cv2.imshow("test",temp_img)
        # cv2.waitKey()
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # [y_offset,x_offset] = offsets[base_floorplan]
            # cX = max(0,cX - int(x_offset))
            # cY = max(0,cY - int(y_offset))
            if prints: print("base_floorplan is: ",base_floorplan)
            if prints: print("legend is: ",legend.keys())
            if prints: print("base_locations dict are: ",locations)
            if legend[base_floorplan][temp_color] in locations[base_floorplan]:
                locations[base_floorplan][legend[base_floorplan][temp_color]].append((cX,cY))
            else: locations[base_floorplan][legend[base_floorplan][temp_color]] = [(cX,cY)] 
    
    base_elevators = {}
    base_stairs = {}
    base_elevators_hallway = {}
    base_stairs_hallway = {}
    base_entry_exits = {}
    
    base_elevators[base_floorplan] = {}
    base_elevators[base_floorplan]['ea'] = locations[base_floorplan]['ea'] if 'ea' in locations[base_floorplan] else []
    base_stairs[base_floorplan] = {}
    base_stairs[base_floorplan]['sa'] = locations[base_floorplan]['sa'] if 'sa' in locations[base_floorplan] else []
    base_elevators_hallway[base_floorplan] = {}
    base_elevators_hallway[base_floorplan]['eh'] = locations[base_floorplan]['eh'] if 'eh' in locations[base_floorplan] else []
    base_stairs_hallway[base_floorplan] = {}
    base_stairs_hallway[base_floorplan]['sh'] = locations[base_floorplan]['sh'] if 'sh' in locations[base_floorplan] else []
    base_entry_exits[base_floorplan] = {}
    base_entry_exits[base_floorplan]['ee'] = []

    for key in locations[base_floorplan]:
        try:
            key_tuple = process_string_coord(key)
            print("key_tuple, key" + str(key_tuple) + ' ' + key)
        except ValueError:
            continue
        for coord in locations[base_floorplan][key]:
            coord_and_floor = coord + key_tuple
            base_entry_exits[base_floorplan]['ee'].append(coord_and_floor)
    
    if prints: print(base_elevators)
    if prints: print(base_stairs)
    if prints: print(base_elevators_hallway)
    if prints: print(base_stairs_hallway)
    if prints: print(base_entry_exits)

    ### assign ids
    def assign_ids_reg(base_something):
        """
        Does not work with entry_exits
        """
        type = list(base_something[base_floorplan].keys())[0]
        base_something = copy.deepcopy(base_something)
        if prints: print("base_something is: ",base_something)
        if prints: print("base_floorplan is: ",base_floorplan)
        if prints: print("type is: ",type)
        coord_list = base_something[base_floorplan][type]
        new_coord_list = []
        if prints: print("coord_list is: ",coord_list)
        for id in range(len(coord_list)):
            elem = coord_list[id] + (id,)
            new_coord_list.append(elem)
        base_something[base_floorplan][type] = new_coord_list
        return base_something
        
    def assign_ids_ee(base_entry_exits):
        '''
        Only works with entry_exits
        '''
        base_entry_exits = copy.deepcopy(base_entry_exits)
        print(base_entry_exits)
        type = list(base_entry_exits[base_floorplan].keys())[0]

        hashmap = {}
        coord_list = base_entry_exits[base_floorplan][type]
        new_coord_list = []
        print(coord_list)
        for coord_r, coord_c, building, floor in coord_list:
            hashmap[(building,floor)] = 0
        
        for coord_r, coord_c, building, floor in coord_list:
            new_coord_list.append((coord_r,coord_c,building,floor,hashmap[((building,floor))]))
            hashmap[(building,floor)] += 1
        base_entry_exits[base_floorplan][type] = new_coord_list
        return base_entry_exits

    return assign_ids_reg(base_elevators), assign_ids_reg(base_stairs), assign_ids_reg(base_elevators_hallway), assign_ids_reg(base_stairs_hallway), assign_ids_ee(base_entry_exits)

def find_locations_all_but_base_floorplan(floorplan, cropping_offsets, labelled_pngs, building, locations, prints = False):
    with open(cropping_offsets + '/offsets.json', 'r') as out:
        offsets = json.load(out)
    with open(labelling_legend, 'r') as out:
        legend = json.load(out)
    
   


    cropping_offsets = Path(cropping_offsets)
    labelled_pngs = Path(labelled_pngs)
    building = Path(building)

    ### calculate base
    floorplane_filename = floorplan
    floorplan = floorplan[:-4]
    if floorplan not in legend:
        print("floorplan is " + floorplan)
        return None, None, None, None, None
    locations[floorplan] = {}
    img_path_leaf = Path(floorplane_filename)
    img = cv2.imread(str(labelled_pngs / building / img_path_leaf))
    if prints: print(str(labelled_pngs / building / img_path_leaf))
    if prints: print("base locations here is: ",locations)
    for color in legend[floorplan]:
        temp_color = color
        color = color.replace('(','')
        color = color.replace(')','')
        color = color.replace(' ','')
        color = color.split(',')
        color = tuple(int(item) for item in color)
        # have to invert because cv2 uses BGR not RGB
        lower = (max(color[2] - 30,0 ), max(color[1] - 30,0 ), max(color[0] - 30,0 ))
        upper = (min(color[2] + 30,255 ), min(color[1] + 30,255 ), min(color[0] + 30,255 ))
        temp_img = cv2.inRange(img, lower, upper)
        contours, hierarchy = cv2.findContours(temp_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(temp_img, contours, -1, (0,255,0), 3)
        # cv2.imshow("test",temp_img)
        # cv2.waitKey()
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # [y_offset,x_offset] = offsets[floorplan]
            # cX = max(0,cX - int(x_offset))
            # cY = max(0,cY - int(y_offset))
            if prints: print("floorplan is: ",floorplan)
            if prints: print("legend is: ",legend.keys())
            if prints: print("locations dict are: ",locations)
            if legend[floorplan][temp_color] in locations[floorplan]:
                locations[floorplan][legend[floorplan][temp_color]].append((cX,cY))
            else: locations[floorplan][legend[floorplan][temp_color]] = [(cX,cY)] 
    
    elevators = {}
    stairs = {}
    elevators_hallway = {}
    stairs_hallway = {}
    entry_exits = {}
    
    elevators[floorplan] = {}
    elevators[floorplan]['ea'] = locations[floorplan]['ea'] if 'ea' in locations[floorplan] else []
    stairs[floorplan] = {}
    stairs[floorplan]['sa'] = locations[floorplan]['sa'] if 'sa' in locations[floorplan] else []
    elevators_hallway[floorplan] = {}
    elevators_hallway[floorplan]['eh'] = locations[floorplan]['eh'] if 'eh' in locations[floorplan] else []
    stairs_hallway[floorplan] = {}
    stairs_hallway[floorplan]['sh'] = locations[floorplan]['sh'] if 'sh' in locations[floorplan] else []
    entry_exits[floorplan] = {}
    entry_exits[floorplan]['ee'] = []

    for key in locations[floorplan]:
        try:
            key_tuple = process_string_coord(key)
        except ValueError:
            continue
        for coord in locations[floorplan][key]:
            coord_and_floor = coord + key_tuple
            entry_exits[floorplan]['ee'].append(coord_and_floor)
    
    return elevators, stairs, elevators_hallway, stairs_hallway, entry_exits

def main(prints = True):
    labelled_pngs_dir = Path(labelled_pngs)

    final_output = {}

    for i, building_dir in enumerate(os.listdir(labelled_pngs_dir)):
        if "DS" in building_dir:
            continue
        building_dir = Path(building_dir)
        floorplan_base_name = Path(max(os.listdir(labelled_pngs_dir / building_dir)))
        floorplan_base_path = labelled_pngs_dir / building_dir / floorplan_base_name
        floorplans = sorted(os.listdir(labelled_pngs / building_dir))
        base_floorplan_file = min(floorplans)
        if "DS" in base_floorplan_file:
            floorplans = floorplans[1:]
            base_floorplan_file = min(floorplans)
        base_floorplan = base_floorplan_file[:-4]
        base_elevators, base_stairs, base_elevators_hallway, base_stairs_hallway, base_entry_exits = find_locations_base_floorplan(floorplans,cropping_offsets,labelled_pngs,building_dir,{}, prints = prints)
        
        def aggregator(elevators,stairs,elevators_hallway,stairs_hallway,entry_exits,floorplan):
            new_dict = {}
            new_dict[floorplan] = {}

            elevators = copy.deepcopy(elevators[floorplan])
            stairs = copy.deepcopy(stairs[floorplan])
            elevators_hallway = copy.deepcopy(elevators_hallway[floorplan])
            stairs_hallway = copy.deepcopy(stairs_hallway[floorplan])
            entry_exits = copy.deepcopy(entry_exits[floorplan])

            for dictionary in [elevators,stairs,elevators_hallway,stairs_hallway,entry_exits]:
                for key, value in dictionary.items():
                    new_dict[floorplan][key] = value

            return new_dict

        final_output[base_floorplan] = aggregator(base_elevators,base_stairs,base_stairs_hallway,base_elevators_hallway,base_entry_exits,base_floorplan)

        for floorplan_file in os.listdir(labelled_pngs_dir / Path(building_dir)):
            if '.png' not in floorplan_file:
                continue
            floorplan = floorplan_file[:-4]
            if prints: print("base_floorplan is: ",base_floorplan_file)
            if floorplan_file == base_floorplan_file:
                continue

            elevators, stairs, elevators_hallway, stairs_hallway, entry_exits = find_locations_all_but_base_floorplan(floorplan_file,cropping_offsets,labelled_pngs_dir,building_dir,{}, prints = prints)
            if prints: print(elevators, stairs, elevators_hallway, stairs_hallway, entry_exits)
            if elevators == None:
                continue

            def iding_input(something,base_something):
                ided_coord_list = []
                type = list(something[floorplan].keys())[0]
                if prints: print(type)

                deepcopy_list = copy.deepcopy(something[floorplan][type])
                if prints: print(deepcopy_list)
                for coord_curr in deepcopy_list:
                    coord_r = coord_curr[0]
                    coord_c = coord_curr[1]
                    min_id = None
                    min_distance = float('inf')

                    for coord_base in base_something[base_floorplan][type]:
                        coord_r_base = coord_base[0]
                        coord_c_base = coord_base[1]
                        id_base = coord_base[-1]
                        distance = math.dist((coord_r,coord_c),(coord_r_base,coord_c_base))
                        min_distance = min(distance,min_distance)
                        if min_distance == distance:
                            min_id = id_base
                    
                    to_append = coord_curr + (min_id,)
                    ided_coord_list.append(to_append)
                    something[floorplan][type] = ided_coord_list
                
                return something
            
            elevators = iding_input(elevators, base_elevators)
            stairs = iding_input(stairs, base_stairs)
            elevators_hallway = iding_input(elevators_hallway, base_elevators_hallway)
            stairs_hallway = iding_input(stairs_hallway, base_stairs_hallway)
            entry_exits = iding_input(entry_exits, base_entry_exits)

            to_add = aggregator(elevators, stairs, elevators_hallway, stairs_hallway, entry_exits,floorplan)
            final_output[floorplan] = to_add
    
    with open(labelling_legend, 'r') as out:
        legend = json.load(out)

    with open(cropping_offsets + '/offsets.json', 'r') as out:
        offsets = json.load(out)

    for k in final_output:
        for k2 in final_output[k]:
            for k3 in final_output[k][k2]:
                for i, (coord) in enumerate(final_output[k][k2][k3]):
                    [row_offset,col_offset] = offsets[k2]
                    coord = list(coord)
                    coord[0] = max(0,coord[0] - int(col_offset))
                    img = cv2.imread(f"{cropped_png_files_dir}/{k2}.png")
                    (H,W) = img.shape[:2]
                    coord[0] = min(coord[0], W)
                    coord[1] = max(0,coord[1] - int(row_offset))
                    coord[1] = min(coord[1], H)
                    final_output[k][k2][k3][i] = coord            
  
    with open(final_output_name,"w") as f:
        json.dump(final_output,f,indent = 0)
    
    return final_output

if __name__ == '__main__':
    # locations = {}
    # floorplans = sorted(os.listdir(Path(labelled_pngs) / Path("Building13")))
    final_output = main()
    for key, value in final_output.items():
        print(key)
        print(value)
        print("----------------")
        print("----------------")