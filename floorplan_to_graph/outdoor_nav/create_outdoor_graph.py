import sys
sys.path.append('../')
import os
import pickle
import cv2
from graph_helper_methods import *
from png_helper_methods import *
from path_finding_testing import ask_for_coords


CAMPUS_MAP = "main_campus_small-test.png"
NEW_FILENAME = "small_outdoor_graph.pickle"


def create_unweighted_graph(image):
    """
    Given an image in an internal representation, 
    return a unweighted directed graph as such:

    Nodes
    - Pixel coordinates

    Edges
    - (coord1, coord2)

    Dijkstar graph
    """
    graph = dijkstar.Graph()

    for x in range(image['width']):
        if x % 100 == 0:
            print(x)
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*250:
                # if not white, ignore as node
                continue
            
            u = (x, y)
            for v in get_white_neighbors(image, *u):
                # add edge (u, v) to graph w/ w(u, v) as weight
                graph.add_edge(u, v, 1)
            
    return graph

def create_and_save_graph():
    image = load_color_image(CAMPUS_MAP)

    start = time.perf_counter()
    graph = create_unweighted_graph(image)
    print(f"Graph creation time: {time.perf_counter() - start}")

    with open(NEW_FILENAME, "wb") as f:
        pickle.dump(graph, f)

def save_image_with_path_drawn(image_filename, new_filename, relevant_coords):
    """
    Colors all coords in "relevant_coords" RED 
    on a copy of an image and saves the new image
    w/ a path drawn
    """
    im_copy = cv2.imread(image_filename) # create copy of image
    
    t_start = time.perf_counter()

    for pixel in relevant_coords:
        im_copy[pixel[1], pixel[0]] = [0,0,255]
    t_find_path = time.perf_counter()
    print(f"time: {t_find_path - t_start}")
    print(new_filename)
    cv2.imwrite(new_filename, im_copy)    

def main():
    print("\nEnter start coordinates")
    start_coords = ask_for_coords()
    print("\nEnter end coordinates")
    end_coords = ask_for_coords()

    for start, end in zip(start_coords, end_coords):
        # load graph
        with open(NEW_FILENAME, "rb") as f:
            graph = pickle.load(f)

        # get path
        nodes, _, _, _ = dijkstar.find_path(graph, start, end) 

        # draw onto new image
        new_filename = f"{start}_{end}_path.png"

        save_image_with_path_drawn(CAMPUS_MAP, new_filename, nodes)



if __name__ == "__main__":
    main()