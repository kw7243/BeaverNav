from door_detection.svg_helper_methods import *
from cairosvg import svg2png
import os
import cv2
from PIL import Image
import pyvips
from dijkstar import Graph, find_path
from png_helper_methods import *
from collections import deque
import pickle
import time

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1)
}

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
    svg_originals_dir = "full_pipeline_files_test/svg_original_files"
    svg_doors_dots_removed_dir = "full_pipeline_files_test/doors_dots_removed_svg"
    cropped_png_files_dir = "full_pipeline_files_test/cropped_png_files"
    reduced_res_png_dir = "full_pipeline_files_test/graph_creation_reduced_res_png"
    graph_storage_dir = "full_pipeline_files_test/graph_storage"
    non_text_pngs_dir = "full_pipeline_files_test/non_text_cropped_pngs"

    print("Starting... ")
    print(f"Total floor plans to process: {len(os.listdir(svg_originals_dir))}")

    for i, floorplan in enumerate(os.listdir(svg_originals_dir)):
        if '.svg' not in floorplan:
            continue

        print(f"SVG processing number {i}: {floorplan}...")
        paths, attr, svg_attr = svg2paths2(f"{svg_originals_dir}/{floorplan}")
        print(svg_attr)
        threshold = determining_threshold_dots(svg_attr)

        paths, attr = remove_empty_paths(paths, attr)
        paths, attr = remove_doors(paths, attr)
        paths, attr = remove_dots(paths, attr, threshold)

        wsvg(paths, filename=f"{svg_doors_dots_removed_dir}/{floorplan[:-4]}_doors_dots_removed.svg", attributes=attr, svg_attributes=svg_attr)

    ### STEP 2: Save to png + crop it
    for i, floorplan in enumerate(os.listdir(svg_doors_dots_removed_dir)):
        if ".svg" not in floorplan:
            continue
        
        start_time = time.perf_counter()
        print("step 2 has begun")
        new_filename = f"{cropped_png_files_dir}/{floorplan[:-4]}_cropped.png"
        image = pyvips.Image.new_from_file(f"{svg_doors_dots_removed_dir}/{floorplan}", dpi=1200)
        image.write_to_file(new_filename)
        print(new_filename)

        # svg2png(url=f"{svg_doors_dots_removed_dir}/{floorplan}",write_to=new_filename,background_color="white",dpi=200)

        Image.MAX_IMAGE_PIXELS = 100000000000

        img = cv2.imread(new_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(img.shape)
        w, h = img.shape

        threshold_used, img = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
        data_temp = img.tolist()
        data = []

        for top_list in data_temp:
            for elem in top_list:
                data.append(elem)
        
        internal_rep = {
            "height":h,
            "width":w,
            "pixels":data
        }
        
        print("thresholding is done")
        print("loaded")
        print("type of rep is: ",type(internal_rep))
        print(len(internal_rep["pixels"]))
        save_color_image(internal_rep,"temp_file_useless.png")
        print('saved')
        print("new_filename is: ",new_filename)
        internal_rep = load_color_image("temp_file_useless.png")
        print(internal_rep.keys())
        print(len(internal_rep["pixels"]))
        crop_image_cv2("temp_file_useless.png",new_filename)
        print("done processing, took: ",time.perf_counter() - start_time)


    ###STEP 3: Converting each image into a graph
    floorplan_to_graph = {}

    for png_file in os.listdir(non_text_pngs_dir):
        if '.png' not in png_file:
            continue
        floorplan_name = png_file[:-4]
        print("floorplan is: ",floorplan_name)

        internal_rep = load_color_image(f"{non_text_pngs_dir}/{png_file}")

        new_filename = reduced_res_png_dir + '/' + floorplan_name + "_low_res" + ".png"

        print(internal_rep["width"])
        print(internal_rep["height"])
        internal_rep, scaling_factor = custom_resizing(internal_rep)
        internal_rep = color_processing_thresholding(internal_rep)
        save_color_image(internal_rep,new_filename)
        
        print(internal_rep["width"])
        print(internal_rep["height"])
        distances_to_black_dict = distances_to_black(internal_rep)

        floorplan_graph = preprocessing_via_duplicate_graph(internal_rep,distances_to_black_dict)

        with open(f"{graph_storage_dir}/{floorplan_name}_graph.pickle","wb") as f:
            pickle.dump(floorplan_graph,f)
        
        floorplan_to_graph[floorplan_name] = (f"{graph_storage_dir}/{floorplan_name}_graph.pickle",scaling_factor)
    
    print(floorplan_to_graph)

if __name__ == "__main__":
    main()
    # file = "full_pipeline_files_test/svg_original_files/5_1.svg"
    # image = pyvips.Image.new_from_file(file, dpi=200)
    # image.write_to_file("junk1.png")
    # svg2png(url=file,write_to="junk3.png",background_color="white",dpi=200)

