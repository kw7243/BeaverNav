import math
import cv2
import os
import json

cropped_pristine_png_files = "cropped_pristine_png_files"
labelled_pngs = "labelled_pngs"
cropping_offsets= "cropping_offsets"

def process_string_coord(coord):
    coord = coord.replace('(','')
    coord = coord.replace(')','')
    coord = coord.replace(' ','')
    coord = coord.split(',')
    coord = tuple(int(item) for item in coord)
    return coord

def process_floorplanname_to_tuple(floorplane_name):
    floorplane_name = floorplane_name.split('_')
    to_return = f'({str(floorplane_name[0])},{str(floorplane_name[1])})'
    return to_return

def main():

    final_output = {}

    floors = sorted(os.listdir(labelled_pngs))
    print(floors)
    with open(cropping_offsets + '/offsets.json', 'r') as out:
        offsets = json.load(out)
    locations = {}
    with open(f"{labelled_pngs}/labelling_legend.json", 'r') as out:
        legend = json.load(out)
    for floorplan in floors:
        if ".png" not in floorplan:
            continue
        # if '13_4' in floorplan:
        #     continue
        # if '13_3' in floorplan:
        #     continue

        img = cv2.imread(f"{labelled_pngs}/{floorplan}")
        # unique_pixels = set()
        # w,h = img.shape[:2]
        # img = cv2.resize(img,(w//30,h//30))
        # w,h = img.shape[:2]
        # for row in range(w):
        #     for col in range(h):
        #         pixel = img[row][col]
        #         if 50 < sum(pixel) < 250*3 and len(set(pixel)) > 2 and max(pixel) - min(pixel) > 70:
        #             if tuple(pixel) not in unique_pixels:
        #                 print(pixel)
        #             unique_pixels.add(tuple(pixel))


        locations[floorplan[:-4]] = {}
        for color in legend[floorplan[:-4]]:
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
                [y_offset,x_offset] = offsets[floorplan[:-4]].replace('(','').replace(')','').replace(' ','').split(',')
                cX = max(0,cX - int(x_offset))
                cY = max(0,cY - int(y_offset))
                if legend[floorplan[:-4]][temp_color] in locations[floorplan[:-4]]:
                    locations[floorplan[:-4]][legend[floorplan[:-4]][temp_color]].append((cX,cY))
                else: locations[floorplan[:-4]][legend[floorplan[:-4]][temp_color]] = [(cX,cY)] 
    
    
    print(locations)
    with open("locations.json","w") as f:
        json.dump(locations,f,indent=5)
    b = [1, 2, 3, 4, 5, 6, '6C', 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 24, 26, 31, 32, 33, 34, 35, 36, 37, 38, 39, 56, 57, 66, 68]
    buildings = []
    for building in b:
        buildings.append(str(building))
    results = {}
    for building in buildings:
        labels = {}
        floorplans = []
        for floorplan in floors:
            if floorplan.split('_')[0] == building:
                floorplans.append(floorplan[:-4])
        elevators = {}
        stairs = {}
        elevators_hallway = {}
        stairs_hallway = {}
        entry_exits = {}




        for floor in floorplans:
            elevators[floor] = locations[floor]['ea'] if 'ea' in locations[floor] else []
            stairs[floor] = locations[floor]['sa'] if 'sa' in locations[floor] else []
            elevators_hallway[floor] = locations[floor]['eh'] if 'eh' in locations[floor] else []
            stairs_hallway[floor] = locations[floor]['sh'] if 'sh' in locations[floor] else []
            entry_exits[floor] = []

        #     for i in locations[floor]:
        #         if i not in ['ea','sa','eh','sh']:
        #             entry_exits[i] = {}

        # for floor in floorplans:
        #     for i in locations[floor]:
        #         entry_exits[i][floor] = locations[floor][i]


            floor_details = []
            for key in locations[floor]:
                print(locations[floor])
                print(key)
                try:
                    key_tuple = process_string_coord(key)
                except ValueError:
                    continue

                for coord in locations[floor][key]:
                    coord_and_floor = coord + key_tuple
                    floor_details.append(coord_and_floor)
            entry_exits[floor] += (floor_details)

            print(entry_exits[floor])

        floorplans.sort()
        ids = [0,0,0,0]
        for i, floor in enumerate(floorplans):
            if i == len(floorplans) - 1:
                continue
            for j, e in enumerate(elevators[floor]):
                if len(e) == 3:
                    continue
                for j2, e2 in enumerate(elevators[floorplans[i+1]]):
                    if len(e2) == 3:
                        continue
                    if math.dist(e,e2) < 50:
                        elevators[floor][j] = e + (ids[0],)
                        elevators[floorplans[i+1]][j2] = e2 + (ids[0],)
                        ids[0] = ids[0] + 1
            for j, e in enumerate(stairs[floor]):
                if len(e) == 3:
                    continue
                for j2, e2 in enumerate(stairs[floorplans[i+1]]):
                    if len(e2) == 3:
                        continue
                    if math.dist(e,e2) < 50:
                        stairs[floor][j] = e + (ids[1],)
                        stairs[floorplans[i+1]][j2] = e2 + (ids[1],)
                        ids[1] = ids[1] + 1
            for j, e in enumerate(elevators_hallway[floor]):
                if len(e) == 3:
                    continue
                for j2, e2 in enumerate(elevators_hallway[floorplans[i+1]]):
                    if len(e2) == 3:
                        continue
                    if math.dist(e,e2) < 50:
                        elevators_hallway[floor][j] = e + (ids[2],)
                        elevators_hallway[floorplans[i+1]][j2] = e2 + (ids[2],)
                        ids[2] = ids[2] + 1

            for j, e in enumerate(stairs_hallway[floor]):
                if len(e) == 3:
                    continue
                
                print("floor is: ",floor)
                for f in floorplans[i+1:]:
                    min_distance = float('inf')
                    print("f is: ",f)
                    for j_minim, e_minim in enumerate(stairs_hallway[f]):
                        if len(e_minim) == 3:
                            continue
                        min_distance = min(min_distance,math.dist(e,e_minim))

                    for j2, e2 in enumerate(stairs_hallway[f]):
                        if len(e2) == 3:
                            continue
                        if abs(math.dist(e,e2) - min_distance) < 0.1:
                            stairs_hallway[floor][j] = e + (ids[3],)
                            stairs_hallway[floorplans[i+1]][j2] = e2 + (ids[3],)
                ids[3] = ids[3] + 1
            
            unique_exits = list(set([(c,d) for (a,b,c,d) in entry_exits[floor]]))
            
            for j, e in enumerate(entry_exits[floor]):
                if len(e) == 5:
                    continue
                ids_ee = [0]*len(unique_exits)
                for j2, e2 in enumerate(entry_exits[floorplans[i+1]]):
                    if len(e2) == 5:
                        continue
                    if math.dist(e,e2) < 50:
                        index = unique_exits.index((entry_exits[floor][j][2],entry_exits[floor][j][3]))
                        entry_exits[floor][j] = e + (ids_ee[index],)
                        entry_exits[floorplans[i+1]][j2] = e2 + (ids_ee[index],)
                        ids_ee[index] = ids_ee[index] + 1

        if len(elevators) > 0: 
            print("we are here")
            print(elevators)
            print(stairs)
            print(elevators_hallway)
            print(stairs_hallway)
            print(entry_exits)

        ### PART 2: Converting into expected output
        for floor, coord_id_list in elevators.items():
            if floor not in final_output:
                final_output[floor] ={}
            
            for coord_id in coord_id_list:
                final_output[floor][f'(el,ac,{coord_id[-1]})'] = tuple([coord_id[0],coord_id[1]])
        
        for floor, coord_id_list in elevators_hallway.items():
            if floor not in final_output:
                final_output[floor] ={}
            
            for coord_id in coord_id_list:
                final_output[floor][f'(el,hw,{coord_id[-1]})'] = tuple([coord_id[0],coord_id[1]])

        for floor, coord_id_list in stairs.items():
            if floor not in final_output:
                final_output[floor] ={}
            
            for coord_id in coord_id_list:
                final_output[floor][f'(sc,ac,{coord_id[-1]})'] = tuple([coord_id[0],coord_id[1]])

        for floor, coord_id_list in stairs_hallway.items():
            if floor not in final_output:
                final_output[floor] ={}
            
            for coord_id in coord_id_list:
                final_output[floor][f'(sc,hw,{coord_id[-1]})'] = tuple([coord_id[0],coord_id[1]])

        for floor, coord_id_list in entry_exits.items():
            if floor not in final_output:
                final_output[floor] = {}
            
            for coord_id in coord_id_list:
                final_output[floor][f'({process_floorplanname_to_tuple(floor)},({coord_id[2]},{coord_id[3]}),ee,{coord_id[-1]})'] = tuple([coord_id[0],coord_id[1]])

    with open("final_output.json","w") as f:
        json.dump(final_output,f,indent=4)


    
if __name__ == "__main__":
    main()