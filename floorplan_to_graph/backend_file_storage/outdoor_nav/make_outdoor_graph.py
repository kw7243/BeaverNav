import sys
sys.path.append('../../')
import os
import pickle
import cv2
from graph_helper_methods import *
from png_helper_methods import *

results_dir = "results"
graph_file = "mid_sized.pickle"
campus_map_file = "test_without_construction_jan19 copy.png"
to_draw_on_file = "Campus_Basemap_pure_copy.png"
# APPROACH:
# 1.
print("hello")

# Input start pixel location, end pixel location
# And draw a red path on the image
def preprocessing_via_graph_creation(image, k=1000):
    """
    DEPRECATED!!!!


    Given an image, return a weighted directed graph as such:
    Nodes
    - Pixel coordinates

    Edges
    - (coord1, coord2)
    - Weighted by weight function above

    Graph in the form of adjacency set

    k = parameter to toggle (higher k --> less tolerance
    for pixels closer to black pixels or image strokes)
    """
    graph = Graph()

    internal_rep = load_color_image(image)

    for x in range(internal_rep['width']):
        if x % 100 == 0:
            print(x)
        for y in range(internal_rep['height']):
            if sum(get_pixel(internal_rep, x, y)) < 3*250:
                continue
            u = (x, y)

            for v in get_white_neighbors(internal_rep, *u):
                # add edge (u, v) to graph w/ w(u, v) as weight
                graph.add_edge(u, v, 1)

    with open(graph_file, "wb") as f:
        pickle.dump(graph, f)

    return graph


def dijkstar_path_find_draw_image(graph_file, start, end):
    print("path finding started")
    start_time = time.time()
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)
    print("done loading. Took: ", time.time() - start_time)
    start_path_finding = time.time()
    nodes, _, _, _ = find_path(graph, start, end)
    print("path_finding: ",time.time() - start_path_finding)
    start_drawing = time.time()
    save_image_with_path_drawn(
        to_draw_on_file, f'results/{start}_to_{end}.png', nodes)
    print("drawing done: ",time.time() - start_drawing)
    return 'success'

def ask_for_coords():
    """
    Appends user-given coordinates to list
    and returns it
    """
    coords = []
    user = ""
    while user != "done":
        user = input("Type in coordinates (ex. 120 150): ")
        try:
            coord = tuple(int(num) for num in user.split())
            coords.append(coord)
        except ValueError as e:
            pass

    return coords

if __name__ == '__main__':
    # Graph Creation
    # preprocessing_via_graph_creation(campus_map_file)
    # print("graph creation done")
    # Testing
    for f in os.listdir(results_dir):
        os.remove(results_dir + '/' + f)
    print("")
    start = tuple(int(num) for num in (input("Start location: ")).split())
    end = tuple(int(num) for num in (input("End location: ")).split())
    print("")
    output = dijkstar_path_find_draw_image(graph_file, start, end)
    print(output)
