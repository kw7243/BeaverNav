from importlib.resources import read_binary
from math import floor
from pydoc import text
from door_detection.svg_helper_methods import *
from cairosvg import svg2png
import os
import cv2
from PIL import Image
from dijkstar import Graph, find_path
from png_helper_methods import *
from collections import deque
import pickle
import time
from text_detection import text_detection_with_east
import cairosvg
import random
import json
import argparse
import read_labels_new

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1)
}

svg_originals_dir = "full_pipeline_files_test/svg_original_files"
svg_doors_dots_removed_dir = "full_pipeline_files_test/doors_dots_removed_svg"
svg_doors_dots_removed_dir_temp = "full_pipeline_files_test/doors_dots_removed_svg_temp"
cropped_png_files_dir = "full_pipeline_files_test/cropped_png_files"
reduced_res_png_dir = "full_pipeline_files_test/graph_creation_reduced_res_png"
graph_storage_dir = "full_pipeline_files_test/graph_storage"
non_text_pngs_dir = "full_pipeline_files_test/non_text_cropped_pngs"
svg_no_lines_dir = "full_pipeline_files_test/no_lines_svgs"
cropped_png_no_lines_dir = "full_pipeline_files_test/no_lines_cropped_pngs"
bbox_dir = "full_pipeline_files_test/bounding_boxes"
modified_png_dir = "full_pipeline_files_test/boxed_text_pngs"
txt_png_dir = "full_pipeline_files_test/pngs_with_recognized_text"
txt_dir = "full_pipeline_files_test/text_locations"
floorplan_name_graph_correspondence_dir = "full_pipeline_files_test/floorplan_name_graph_correspondence"
cropped_pristine_png_files = "full_pipeline_files_test/cropped_pristine_png_files"
cropping_offsets= "full_pipeline_files_test/cropping_offsets"
temp_dir = 'full_pipeline_files_test/temp_files'

def pixel_valid(image,x,y):
    return sum(get_pixel(image,x,y)) > 250*3

def get_left_right_neighbors(image, x, y):
    """
    Returns left-right white neighbors of (x, y) 
    """

    return [(x + dx, y) for dx in [-1, 1] 
                if in_bounds(image, *(x + dx, y)) and 
                    pixel_valid(image,*(x+dx,y))]

def get_up_down_neighbors(image, x, y):
    """
    Returns up-down white neighbors of (x, y) 
    """
    return [(x, y + dy) for dy in [-1, 1] 
                if in_bounds(image, *(x, y + dy)) and 
                    pixel_valid(image, *(x, y + dy))]

def distances_to_black(image):
    """
    Given an image (internal rep.),
    return the shortest distance of 
    every white pixel to the nearest black pixel

    Runs a BFS w/ every black pixel as the source node
    """
    distances = {} # (x, y) --> distance to black pixel
    visited = set()

    q = deque([])
    for x in range(image['width']):
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*250: # if black pixel
                distances[(x, y)] = 0 
                q.append((x, y)) # add black pixels into q
    
    while q:
        coord = q.popleft()

        for neighbor_coord in get_white_neighbors(image, *coord):
            if neighbor_coord not in visited:
                distances[neighbor_coord] = distances[coord] + 1
                q.append(neighbor_coord)
                visited.add(neighbor_coord)
    
    return distances

def weight_func(coord, distances_to_black_dict,k=1000):
    """
    Given an image, coordinate "v", and constant k,
    w(u, v) = k/d^2

    k = parameter to toggle (higher k --> less tolerance
        for pixels closer to black pixels or image strokes)
    d = distance of v from nearest black pixel
    """
    return k*(1/(distances_to_black_dict[coord]**2))

def get_white_neighbors(image, x, y):
    """
    Returns up-down-left-right neighbors of (x,y)
    that are white/near-white neighbors of 
    a given pixel --> pixel vals > 254)
    """
    return [(x + dx, y + dy) 
                for dx, dy in direction_vector.values() 
                     if in_bounds(image, *(x + dx, y + dy)) 
                        and sum(get_pixel(image, *(x + dx, y + dy) )) > 250*3]

def preprocessing_via_duplicate_graph(image, distances_to_black_dict, k=1000):
    """
    Given internal rep. of an image, 
    returns a graph w/ 2 layers described as follows:

    For every coordinate u in image, we define
    
    Nodes
    u_horizontal - arriving at coordinate u via 
    left-right neighbor

    u_vertical - arriving at coordinate u via 
    up-down neighbor

    Node ex. --> ((2, 5), "horizontal")


    Edges
    (u_horiz, v_horiz) = k/d^2
    (u_vert, v_vert) = k/d^2
    where d = distance of v (horiz and vert respectively)
    from the nearest black pixel

    (u_vert, v_horiz) = (u_horiz, v_vert) = k
    This is to discourage "turns." 
    (ex. an optimal horizontal path leading to 
    node u_horiz should continue along a horizontal
    path rather than turn up-down)

    room is a string representing which room the floorplan corresponds to. e.g. '1_2'

    dict_room_color_coords maps 
    """

### pixel_valid
### get_left_right_neighbors
### weight_func
### get_up_down_neighbors

    graph = Graph()
    # distances = {} # stores pixel distances of coords to nearest black pixel


    for x in range(image['width']):
        for y in range(image['height']):
            if not pixel_valid(image,x,y):
                continue

            u = (x, y)
            for v_horizontal in get_left_right_neighbors(image, *u):
                # w(u_horiz, v_horiz) = k/d^2
                edge_weight = weight_func(v_horizontal,distances_to_black_dict)
                graph.add_edge((u, 'horizontal'), (v_horizontal, 'horizontal'), edge_weight)
                # w(u_vert, v_horiz) = k
                edge_weight = k
                graph.add_edge((u,'vertical'), (v_horizontal,'horizontal'), edge_weight)
                

            for v_vertical in get_up_down_neighbors(image, *u):
                # w(u_vert, v_vert) = k/d^2
                edge_weight = weight_func(v_vertical,distances_to_black_dict)
                graph.add_edge((u, 'vertical'), (v_vertical, 'vertical'), edge_weight)

                # w(u_horiz, v_vert) = k
                edge_weight = k
                graph.add_edge((u,'horizontal'), (v_vertical,'vertical'), edge_weight)
            
            graph.add_edge(u,(u,'horizontal'),0)
            graph.add_edge(u,(u,'vertical'),0)
            graph.add_edge((u,'horizontal'),u,10*edge_weight)
            graph.add_edge((u,'vertical'),u,10*edge_weight)

    return graph

def main():
    
    ### STEP 1: Door, dot removal
    

    start_time_total = time.perf_counter()


    print("Starting... ")
    floors = os.listdir(svg_originals_dir), 1
    print(f"Total floor plans to process: {len(floors)}")

    process_SVGs()

    crop_pngs()

    detect_text()

    remove_text_from_pngs()

    recognize_text()
    
    create_graph()
    print("done all floor plans took: ",time.perf_counter() - start_time_total)

    
    
    print(floorplan_to_graph)

def process_SVGs():
    print("****************")   
    print("STEP 1 HAS BEGUN: PROCESSING SVGS")
    print("****************")   
    start_time = time.perf_counter()
    floors = os.listdir(svg_originals_dir)
    for i, floorplan in enumerate(floors):
        if '.svg' not in floorplan:
            continue
        print(f"SVG processing number {i}: {floorplan}...")
        if floorplan[:-4] not in ['1_0', '1_1']:
            continue
        paths, attr, svg_attr = svg2paths2(f"{svg_originals_dir}/{floorplan}")
        threshold_low = determining_threshold_dots(svg_attr) /2
        threshold_high = 1000

        paths, attr = remove_empty_paths(paths, attr)

        if f"{floorplan[:-4]}.png" not in os.listdir(cropped_pristine_png_files) :
            print("Generating PNG of " + floorplan)
            wsvg(paths, filename=f"temp.svg", attributes=attr, svg_attributes=svg_attr)
            cairosvg.svg2png(url ='temp.svg', write_to=f"{cropped_pristine_png_files}/{floorplan[:-4]}.png", background_color='white',dpi = text_detection_with_east.dpi )
            os.remove('temp.svg')
        else: print("Already cropped " + floorplan)
        paths, attr = remove_doors(paths, attr)
        #paths, attr = remove_dots(paths, attr, threshold_low)
        #paths, attr = remove_large_paths(paths, attr, threshold_high)

        if f"{floorplan[:-4]}.svg" not in os.listdir(svg_doors_dots_removed_dir):
            print("Processing " + floorplan)
            wsvg(paths, filename=f"{svg_doors_dots_removed_dir}/{floorplan[:-4]}.svg", attributes=attr, svg_attributes=svg_attr)
        else: 
            print("Already processed " + floorplan)
        newpaths, newattr, dot_paths, dot_attr = remove_dots(paths, attr, threshold_low)
        wsvg(newpaths, filename=f"{svg_doors_dots_removed_dir}/{floorplan[:-4]}_dots_removed.svg", attributes=newattr, svg_attributes=svg_attr)
        wsvg(dot_paths, filename=f"{svg_doors_dots_removed_dir}/{floorplan[:-4]}_dots_only.svg", attributes=dot_attr, svg_attributes=svg_attr)
        
    print("DONE WITH STEP 1. TIME TAKEN: ",time.perf_counter() - start_time)

def add_height_width_to_svgs():
    floors = os.listdir(svg_doors_dots_removed_dir)
    for i, floorplan in enumerate(floors):
        if floorplan == ".DS_Store":
            continue
        f = open(f"{svg_doors_dots_removed_dir}/{floorplan}", 'r+')
        f.seek(0)
        f_content = f.readlines()
        #print(f_content)
        if len(f_content)>=0:
            for i,line in enumerate(f_content):
                if 'x="0px" y="0px" viewBox="0 0 1224 792"' in str(line):
                    #print("found")
                    #print(line)
                    print("Modifying " + floorplan)
                    f_content[i] = line.replace('x="0px" y="0px" viewBox="0 0 1224 792"', 'width="1224pt" height="792pt" viewBox="0 0 1224 792"')
                    #print(f_content[i])
            f.seek(0)
            f.truncate()
            f.write(''.join(f_content))
            f.close()

def process_SVGs_2():
    print("****************")   
    print("STEP 1.5 HAS BEGUN: PRE-PROCESSING SVGS FOR TEXT DETECTION")
    print("****************")   
    start_time = time.perf_counter()
    floors = os.listdir(svg_doors_dots_removed_dir)
    for i, floorplan in enumerate(floors):
        if '.svg' not in floorplan:
            continue
        print(f"SVG processing number {i}: {floorplan}...")
        threshold_high = 1000
        if f"{floorplan[:-4]}.svg" not in os.listdir(svg_no_lines_dir):
            paths, attr, svg_attr = svg2paths2(f"{svg_originals_dir}/{floorplan}")
            paths, attr = remove_empty_paths(paths, attr)
            paths, attr = remove_doors(paths, attr)
            #paths, attr = remove_large_paths(paths, attr, threshold_high)
            wsvg(paths, filename=f"temp.svg", attributes=attr, svg_attributes=svg_attr)
            deleteSVGLines(f"{svg_originals_dir}/{floorplan}", f"{svg_no_lines_dir}/{floorplan[:-4]}.svg", text_detection_with_east.thresh_svg)
        else:
            print("Already removed lines from " + floorplan)
    print("DONE WITH STEP 1.5. TIME TAKEN: ",time.perf_counter() - start_time)

def crop_pngs():
    ### STEP 2: Save to png + crop it
    print("****************")
    print("STEP 2 HAS BEGUN: CROPPING PNGS")
    print("****************")  
    start_time = time.perf_counter()
    errors = []
    offsets = {}
    try:
        with open(cropping_offsets + '/offsets.json', 'r') as out:
            offsets = json.load(out)
    except:
        pass
    for i, floorplan in enumerate(os.listdir(svg_doors_dots_removed_dir)):
        if ".svg" not in floorplan or "DS" in floorplan:
            continue
        if f"{floorplan[:-4]}.png" in os.listdir(cropped_png_files_dir) and f"{floorplan[:-4]}.png" in os.listdir(cropped_png_no_lines_dir):
            print(f"Already cropped number {i}: " +floorplan[:-4] + '.png')
            continue
        
        print(f"Cropping floor number {i}: " + f"{floorplan[:-4]}.png")     
        new_filename = f"{cropped_png_files_dir}/{floorplan[:-4]}.png"
        new_filename_lines_removed = f"{cropped_png_no_lines_dir}/{floorplan[:-4]}.png"
        cairosvg.svg2png(url=f"{svg_doors_dots_removed_dir}/{floorplan}", write_to = new_filename, background_color="white", dpi=text_detection_with_east.dpi)
        cairosvg.svg2png(url=f"{svg_no_lines_dir}/{floorplan}", write_to = new_filename_lines_removed, background_color="white", dpi=text_detection_with_east.dpi)
        
        Image.MAX_IMAGE_PIXELS = 100000000000

        img = cv2.imread(new_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = img.shape

        threshold_used, img = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
        try:
            (a,b,c,d) = crop_image_cv2(new_filename,new_filename)
            temp_img = cv2.imread(new_filename)
            img_no_lines = cv2.imread(new_filename_lines_removed)
            img_no_lines = img_no_lines[a:b,c:d]
            res, img_no_lines = cv2.threshold(img_no_lines,240,255,cv2.THRESH_BINARY)
            cv2.imwrite(new_filename_lines_removed,img_no_lines)
        except:
            print('ERROR WITH FLOORPLAN ' + floorplan)
            errors.append(floorplan)
        # stores offets as tuple of (building_floor, (y_offset, x_offset))
        offsets[floorplan[:-4]] =  (a,c)
        with open(cropping_offsets + '/offsets.json', 'w') as out:
            json.dump(offsets,out, indent=5)
    print('ERRORS WITH FLOORPLANS ' + str(errors))
    
    print("DONE WITH STEP 2. TIME TAKEN: ",time.perf_counter() - start_time)

def detect_text():
    ###STEP 3: Detecting Text
    start_time = time.perf_counter()
    print("****************")
    print("STEP 3 HAS BEGUN: DETECTING TEXT")
    print("****************")
    for i, floorplan in enumerate(os.listdir(cropped_png_no_lines_dir)):
        start_time = time.perf_counter()
        if f"{floorplan[:-4]}.json" in os.listdir(bbox_dir) or "DS" in floorplan:
            print(f"Already ran text detection on number {i}: " +floorplan[:-4] + '.png')
            continue
        print(f"Running text detection on number {i}: " +floorplan[:-4] + '.png')
        text_detection_with_east.saveBoundingBoxes(f"{cropped_png_no_lines_dir}/{floorplan[:-4]}.png", f"{modified_png_dir}/{floorplan[:-4]}.png", f"{bbox_dir}/{floorplan[:-4]}.json", 1, True, True, True)
    print("DONE WITH STEP 3. TIME TAKEN: ",time.perf_counter() - start_time)

def remove_text_from_pngs():
    start_time = time.perf_counter()
    print("****************")
    print("STEP 4 HAS BEGUN: REMOVING TEXT")
    print("****************")
    for i, floorplan in enumerate(os.listdir(modified_png_dir)):
        start_time = time.perf_counter()
        if f"{floorplan[:-4]}.png" in os.listdir(non_text_pngs_dir) or "DS" in floorplan:
            print(f"Already removed text from number {i}: " +floorplan[:-4] + '.png')
            continue
        print(f"Removing text from number {i}: " +floorplan[:-4] + '.png')
        text_detection_with_east.remove_text(f"{cropped_png_files_dir}/{floorplan[:-4]}.png", f"{cropped_png_no_lines_dir}/{floorplan[:-4]}.png", f"{bbox_dir}/{floorplan[:-4]}.json", f"{non_text_pngs_dir}/{floorplan[:-4]}.png")
    print("DONE WITH STEP 4. TIME TAKEN: ",time.perf_counter() - start_time)

def recognize_text():
    start_time = time.perf_counter()
    print("****************")
    print("STEP 5 HAS BEGUN: RECOGNIZING TEXT")
    print("****************")
    for i, floorplan in enumerate(os.listdir(modified_png_dir)):
        if f"{floorplan[:-4]}.png" in os.listdir(txt_png_dir) or "DS" in floorplan:
            print(f"Already recognized text on number {i}: " +floorplan[:-4] + '.png')
            continue
        print(f"Recognizing text on number {i}: " +floorplan[:-4] + '.png')
        text_detection_with_east.getText(f"{cropped_png_files_dir}/{floorplan[:-4]}.png", f"{cropped_png_no_lines_dir}/{floorplan[:-4]}.png", f"{bbox_dir}/{floorplan[:-4]}.json", f"{txt_png_dir}/{floorplan[:-4]}.png", f"{txt_dir}/{floorplan[:-4]}.json", easy = True, keras = False)
    print("DONE WITH STEP 5. TIME TAKEN: ",time.perf_counter() - start_time)

def create_low_res_png():
    start_time = time.perf_counter()
    print("****************")
    print("STEP 6 HAS BEGUN: CREATING GRAPH")
    print("****************")
    floorplan_to_graph = {}

    Image.MAX_IMAGE_PIXELS = 100000000000
    for i,png_file in enumerate(os.listdir(non_text_pngs_dir)):
        if '.png' not in png_file:
            continue
        floorplan_name = png_file[:-4]
        if f"{png_file[:-4]}.png" in os.listdir(reduced_res_png_dir) or "DS" in png_file:
            print(f"Already created reduced res png of number {i}: " +png_file[:-4] + '.png')
            continue
        print(f"Creating reduced res png of number {i}: " +png_file[:-4] + '.png')

        internal_rep = load_color_image(f"{non_text_pngs_dir}/{png_file}")

        new_filename = reduced_res_png_dir + '/' + floorplan_name + ".png"

        # print(internal_rep["width"])
        # print(internal_rep["height"])
        internal_rep, scaling_factor = custom_resizing(internal_rep)
        internal_rep = color_processing_thresholding(internal_rep)
        save_color_image(internal_rep,new_filename)
    print("DONE WITH STEP 6. TIME TAKEN: ",time.perf_counter() - start_time)

    return 
        # print(internal_rep["width"])
        # print(internal_rep["height"])

def create_graph():
    floorplan_to_graph = {}
    for png_file in os.listdir(reduced_res_png_dir):
        text_detection_with_east.drawTextNodes(f"{reduced_res_png_dir}/{png_file}", f"{reduced_res_png_dir}/{png_file}", f"{txt_dir}/{png_file[:-4]}.txt", )
        floorplan_name = png_file[:-4]
        internal_rep = load_color_image(png_file)
        distances_to_black_dict = distances_to_black(internal_rep)

        floorplan_graph = preprocessing_via_duplicate_graph(internal_rep,distances_to_black_dict)

        with open(f"{graph_storage_dir}/{floorplan_name}_graph.pickle","wb") as f:
            pickle.dump(floorplan_graph,f)
        
        floorplan_to_graph[floorplan_name] = (f"{graph_storage_dir}/{floorplan_name}_graph.pickle",scaling_factor)

    with open(floorplan_name_graph_correspondence_dir + '/' + "floorplan_name_graph_correspondence.json","w") as out:
        json.dump(floorplan_to_graph,out, indent = 5)
    print(floorplan_to_graph)
    
    return 
    
def read_labels():
    start_time = time.perf_counter()
    print("****************")
    print("STEP 5.5 HAS BEGUN: READING STAIR/ELEVATOR LABELS")
    print("****************")
    read_labels_new.main()
    print("DONE WITH STEP 5.5. TIME TAKEN: ",time.perf_counter() - start_time)

def trim_text_files():
    start_time = time.perf_counter()
    print("****************")
    print("STEP MISC HAS BEGUN: TRIMMING TEXT FILES")
    print("****************")
    for i, floorplan in enumerate(os.listdir(txt_dir)):
        if "DS" in floorplan:
            continue
        print(f"Trimming text on number {i}: " +floorplan[:-5] + '.json')
        text_detection_with_east.trim_drtext_file(f"{txt_dir}/{floorplan[:-5]}.json", f"{txt_dir}/{floorplan[:-5]}.json")
    print("DONE WITH STEP MISC. TIME TAKEN: ",time.perf_counter() - start_time)

def draw_text_nodes():
    start_time = time.perf_counter()
    print("****************")
    print("STEP MISC HAS BEGUN: DRAWING TEXT NODES")
    print("****************")
    with open(reduced_res_png_dir + '/' + "scaling_factors.json","r") as file:
        factors = json.load(file)
    for i, floorplan in enumerate(os.listdir(reduced_res_png_dir)):
        if "DS" in floorplan:
            continue
        if '.png' not in floorplan:
            continue
        scaling_factor = factors[floorplan]
        print(f"Drawing text nodes on number {i}: " +floorplan[:-4] + '.png')
        text_detection_with_east.drawTextNodes(f"{reduced_res_png_dir}/{floorplan[:-4]}.png", f"{temp_dir}/{floorplan[:-4]}.png", f"{txt_dir}/{floorplan[:-4]}.json", scale_factor=scaling_factor, color = (0,0,255))
    print("DONE WITH STEP MISC. TIME TAKEN: ",time.perf_counter() - start_time)

def store_scaling_factor():
    start_time = time.perf_counter()
    print("****************")
    print("STEP MISC 1 HAS BEGUN: STORING SCALING FACTOR")
    print("****************")
    factors = {}
    for i,png_file in enumerate(os.listdir(reduced_res_png_dir)):
        if '.png' not in png_file:
            continue
        print(f"Finding scaling factor of number {i}: " +png_file[:-4] + '.png')
        reduced_img = cv2.imread(f"{reduced_res_png_dir}/{png_file}")
        full_img = cv2.imread(f"{non_text_pngs_dir}/{png_file}")
        w_reduced = reduced_img.shape[0]
        w_full = full_img.shape[0]
        scaling_factor = w_full/w_reduced
        factors[png_file] = scaling_factor
    with open(reduced_res_png_dir + '/' + "scaling_factors.json","w") as out:
        json.dump(factors,out, indent = 5)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=bool, default=False)
    parser.add_argument("--a", type=bool, default=False)
    parser.add_argument("--p2", type=bool, default=False)
    parser.add_argument("--c", type=bool, default=False)
    parser.add_argument("--d", type=bool, default=False)
    parser.add_argument("--rm", type=bool, default=False)
    parser.add_argument("--rt", type=bool, default=False)
    parser.add_argument("--rr", type=bool, default=False)
    parser.add_argument("--cg", type=bool, default=False)
    parser.add_argument("--rl", type=bool, default=False)
    parser.add_argument("--tt", type=bool, default=False)
    parser.add_argument("--dt", type=bool, default=False)
    parser.add_argument("--sf", type=bool, default=False)
    args = parser.parse_args()
    if args.p:
        process_SVGs()
    if args.a:
        add_height_width_to_svgs()
    if args.p2:
        process_SVGs_2()
    if args.c:
        crop_pngs()
    if args.d:
        detect_text()
    if args.rm:
        remove_text_from_pngs()
    if args.rt:
        recognize_text()
    if args.rr:
        create_low_res_png()
    if args.cg:
        create_graph()
    if args.rl:
        read_labels()
    if args.tt:
        trim_text_files()
    if args.dt:
        draw_text_nodes()
    if args.sf:
        store_scaling_factor()
    #main()

