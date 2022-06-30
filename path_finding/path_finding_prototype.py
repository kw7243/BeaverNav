import time
import pickle
from PIL import Image
import numpy as np
from dijkstar import Graph, find_path

##############################
#   IMAGE HELPER FUNCTIONS   #
##############################

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Dictionary:
    image = {
        'height': height,
        'width': width,
        'pixels': [0 --> 255 if grayscale else (R,G,B) values],
    }

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def get_pixel(image, x, y):
    """
    Retrieves value of a pixel at (x,y) of 
    an image dictionary if in bounds, otherwise None
    """
    location = y*image["width"] + x
    return image['pixels'][location] if in_bounds(image, x, y) else None


def set_pixel(image, c, x, y):
    """
    Sets pixel at (x,y) to value c
    """

    location = y*image["width"] + x
    image['pixels'][location] = c


def in_bounds(image, x, y):
    """ 
    Returns bool representing whether (x,y) 
    is in bounds of an image
    """
    return 0 <= x < image["width"] and 0 <= y < image["height"]


##############################
#      IMAGE PROCESSING      #
##############################

def reduce_resolution(cropped_image, new_filename = None, r=16):
    """
    Given internal rep. of cropped image,
    return an internal representation of it
    with resolution reduced by r
    """

    # Convert from internal rep. to Image object
    cropped_image_obj = Image.new(mode='RGB', size=(cropped_image['width'], cropped_image['height']))
    cropped_image_obj.putdata(cropped_image['pixels'])

    reduced_obj = cropped_image_obj.resize((dim//r for dim in cropped_image_obj.size), )
    cropped_image_obj.close()

    # Convert reduced Image obj to internal rep
    w, h = reduced_obj.size
    reduced_image = {'height': h, 'width': w, 'pixels': list(reduced_obj.getdata())} 

    if new_filename is not None:
        reduced_obj.save(new_filename)

    reduced_obj.close()
    return reduced_image, r



def expand_coords(list_of_coords, r = 16):
    """
    Converts a list of coordinates in lower res image
    to coordinates in higher res image
    based on the reduction factor r

    Ex. 
    In a lower res image reduced by 5, 
    (1, 1) corresponds to all 25 coordinates 
    inclusive within this range: (5, 5) --> (10, 10)
    """
    print(list_of_coords)
    return [(x*r + dx, y*r + dy) 
                for dx in range(r)
                    for dy in range(r)
                        for (x, y), tag in list_of_coords]


def left_right(image):
    """
    Scans image left-right via a vertical 1D
    line, incrementing x location of the scan
    until reach a black pixel

    Returns x_min
    """
    for x in range(image['width']):
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*250:
                return x

def top_down(image):
    """
    Scans image TOP-DOWN via a 
    horizontal line (size = image width)
    by marching it along the image height until find 
    a black pixel (reached border)

    Returns y_min
    """
    for y in range(image['height']):
        for x in range(image['width']):
            if sum(get_pixel(image, x, y)) < 3*250:
                return y

def right_left(image):
    """
    Scans image right-left via a vertical 1D
    line, incrementing x location of the scan
    until reach a black pixel

    Returns x_max
    """
    for x in range(image['width'] - 1, 0, -1):
        for y in range(image['height']):
              if sum(get_pixel(image, x, y)) < 3*250:
                return x

def bottom_up(image):
    """
    Scans image BOTTOM-UP for a black pixel
    and returns the y-coordinate of it

    Returns y_max
    """
    for y in range(image['height'] - 1, 0, -1):
        for x in range(image['width']):
            if sum(get_pixel(image, x, y)) < 3*250:
                return y


def crop_image(filename, new_filename = None):
    """
    Given an internal representation of 
    a floor plan image, crop it to remove
    the border, legend, and extra whitespace

    Returns internal rep.
    """
    # Open Image object
    image = Image.open(filename)

    w, h = image.size
    # Crop out border and legend
    borders = (160, 160, w - 180, h - 500)
    cropped_image_obj = image.crop(borders)

    image.close()

    w, h = cropped_image_obj.size
    cropped_image = {'height': h, 'width': w, 'pixels': list(cropped_image_obj.getdata())} 

    # Crop out whitespace
    x_min = left_right(cropped_image) - 10
    x_max = right_left(cropped_image) + 10
    y_min = top_down(cropped_image) - 10
    y_max = bottom_up(cropped_image) + 10

    cropped_image_obj = cropped_image_obj.crop((x_min, y_min, x_max, y_max))

    # Convert cropped Image obj to internal rep
    w, h = cropped_image_obj.size
    cropped_image = {'height': h, 'width': w, 'pixels': list(cropped_image_obj.getdata())} 

    # Save cropped Image if new file name provided
    if new_filename is not None:
        cropped_image_obj.save(new_filename)

    cropped_image_obj.close()

    return cropped_image # return internal representation

def binary_filter(old_filename, new_filename=None):
    """
    Returns a new image rep. w/ non-white 
    pixels converted to pure black

    Optionally
    """
    im = load_color_image(old_filename)
    im["pixels"] = [(0, 0, 0) if sum(pixel) < 3*250 else (255, 255, 255) 
                        for pixel in im["pixels"]]

    if new_filename is not None:
        save_color_image(im, new_filename)

    return im



def save_image_with_path_drawn(image_filename, new_filename, relevant_coords):
    """
    Colors all coords in "relevant_coords" RED 
    on a copy of an image and saves the new image
    w/ a path drawn
    """
    im_copy = load_color_image(f"{image_filename}") # create copy of image
    
    for pixel in relevant_coords:
        set_pixel(im_copy, (255,0,0), *pixel) # color red
    
    save_color_image(im_copy, new_filename)


########################
#   PREPROCESSING      #
########################

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def get_radial_sweep(image, x, y, r):
    """
    Returns ALL coordinates within r pixels of (x,y) 
    contained within the image
    """
    return [(x + dx, y + dy) 
                for dx in range(-r, r + 1)
                    for dy in range(-r, r + 1) if in_bounds(image, *(x + dx, y + dy))]

def get_neighbors(image, x, y):
    """
    Returns up-down-left-right neighbors of (x,y)
    that are IN BOUNDS of an image
    """
    return [(x + dx, y + dy) 
                for dx, dy in direction_vector.values() 
                     if in_bounds(image, *(x + dx, y + dy))]


def get_acceptable_neighbors(x, y, acceptable_pixels):
    """
    Returns up-down-left-right neighbors of (x,y)
    that are in a given set "acceptable_pixels"
    """
    return [(x + dx, y + dy) 
                for dx, dy in direction_vector.values() 
                    if (x + dx, y + dy) in acceptable_pixels]


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


def preprocess_via_threshold(image, threshold=4):
    """
    Given an image, returns a set of pixels that 
    are not within "threshold" pixels of darker pixels
    (white pixels a good distance away from black pixels)

    This is to produce a BFS tree w/ paths that don't 
    hug against walls (to produce more realistic paths)
    """
    acceptable_pixels = set()

    for x in range(image['width']):
        for y in range(image['height']):
            new_coord = (x,y)

            if (sum(get_pixel(image, *new_coord)) > 250*3 and 
                    all(sum(get_pixel(image, *coord)) > 250*3 
                        for coord in get_radial_sweep(image, *new_coord, threshold))):
                # add in coordinate only if it itself is white
                # and all neighbors 
                # in "threshold" pixel radius are white
                acceptable_pixels.add(new_coord)

    return acceptable_pixels            


def distance_to_black(image, coord):
    """
    Given a coordinate and image, 
    return the MANHATTAN distance to the 
    nearest black pixel (sum of its RGB values < 240)

    Uses BFS to search from the source coordinate until
    a black pixel is reached
    """
    agenda = [(coord, 0)] # (coordinate, distance so far)
    visited = set()

    while agenda:
        curr_node = agenda.pop(0)

        if sum(get_pixel(image, *curr_node[0])) < 3*240:
            # found a black pixel, so return its distance from 
            # the source coordinate
            return curr_node[1] 

        if curr_node[1] >= 50:
            return 50

        for neighbor_coord in get_neighbors(image, *curr_node[0]):
            if neighbor_coord not in visited:
                agenda.append((neighbor_coord, curr_node[1] + 1))
                visited.add(neighbor_coord)
        
    return float("inf") # if no black pixels exist in image

def weight_func(image, coord, k):
    """
    Given an image, coordinate "v", and constant k,
    w(u, v) = k/d^2

    k = parameter to toggle (higher k --> less tolerance
        for pixels closer to black pixels or image strokes)
    d = distance of v from nearest black pixel
    """
    return k*(1/((distance_to_black(image, coord))**2))


def preprocessing_via_graph_creation(image, k=1000):
    """
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
    
    for x in range(image['width']):
        for y in range(image['height']):
            u = (x, y)

            for v in get_white_neighbors(image, *u):
                # add edge (u, v) to graph w/ w(u, v) as weight
                edge_weight = weight_func(image, v, k) 
                graph.add_edge(u, v, edge_weight)

    return graph



def get_left_right_neighbors(image, x, y):
    """
    Returns left-right white neighbors of (x, y) 
    """
    return [(x + dx, y) for dx in [-1, 1] 
                if in_bounds(image, *(x + dx, y)) and 
                    sum(get_pixel(image, *(x + dx, y))) > 250*3]

def get_up_down_neighbors(image, x, y):
    """
    Returns up-down white neighbors of (x, y) 
    """
    return [(x, y + dy) for dy in [-1, 1] 
                if in_bounds(image, *(x, y + dy)) and 
                    sum(get_pixel(image, *(x, y + dy))) > 250*3]


def preprocessing_via_duplicate_graph(image, k=1000):
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
    """
    graph = Graph()
    distances = {} # stores pixel distances of coords to nearest black pixel

    for x in range(image['width']):
        for y in range(image['height']):
            
            if sum(get_pixel(image, x, y)) < 250*3:
                continue

            u = (x, y)
            for v_horizontal in get_left_right_neighbors(image, *u):
                # w(u_horiz, v_horiz) = k/d^2
                if v_horizontal in distances:
                    edge_weight = distances[v_horizontal]
                else:
                    edge_weight = weight_func(image, v_horizontal, k)
                    distances[v_horizontal] = edge_weight
                graph.add_edge((u, 'horizontal'), (v_horizontal, 'horizontal'), edge_weight)

                # w(u_vert, v_horiz) = k
                edge_weight = k
                graph.add_edge((u,'vertical'), (v_horizontal,'horizontal'), edge_weight)
                
            for v_vertical in get_up_down_neighbors(image, *u):
                # w(u_vert, v_vert) = k/d^2
                if v_vertical in distances:
                    edge_weight = distances[v_vertical]
                else:
                    edge_weight = weight_func(image, v_vertical, k)
                    distances[v_vertical] = edge_weight
                graph.add_edge((u, 'vertical'), (v_vertical, 'vertical'), edge_weight)

                # w(u_horiz, v_vert) = k
                edge_weight = k
                graph.add_edge((u,'horizontal'), (v_vertical,'vertical'), edge_weight)
            
    return graph


########################
#       Dijkstar       #
########################

def Dijkstar_shortest_path(graph, start, end):
    """
    Returns nodes (pixel coordinates) comprising
    shortest path from start --> end
    """
    nodes, edges, costs, total_cost = find_path(graph, start, end)
    return nodes

def Dijkstar_duplicated_graph(duplicated_graph, start, end):
    """
    Given a duplicated graph and start and end
    coordinates, return the shortest path 
    among ALL paths between the possible
    node states of the duplicated graph
    """
    start_A = (start, 'horizontal')
    start_B = (start, 'vertical')
    end_A = (end, 'horizontal')
    end_B = (end, 'vertical')

    path_info = [find_path(duplicated_graph, start, end) 
                    for start in [start_A, start_B] 
                        for end in [end_A, end_B]]
    
    # From list of paths' info, return the nodes
    # comprising the path w/ the lowest cost
    nodes, edges, costs, total_cost = min(path_info, key = lambda x: x[3])
    return nodes



########################
#         BFS          #
########################

def bfs(image, start):
    """
    Returns BFS tree rooted at a start pixel in the form
    of parent pointers for an image
    """
    tree = {"start": start, "parent_ptrs": {start: start}} 

    parent = tree["parent_ptrs"] # mapping (x1,y1): (x2,y2)
    agenda = [start] # holds coordinates to explore

    while agenda:
        curr_node = agenda.pop(0)

        for child in get_white_neighbors(image, *curr_node):
            if child not in parent: # if unvisited
                parent[child] = curr_node
                agenda.append(child)

    return tree

def build_sp(tree, end, start = None): 
    """
    Builds a shortest path from parent pointers
    """
    if start == None:
        start = tree["start"]

    parent = tree["parent_ptrs"]
    if end not in parent: # end unreachable
        return None
    
    # initialize
    curr_node = end
    path = [end]

    # backtracks from end node via parent pointers
    # until reach start
    while curr_node != start:
        curr_node = parent[curr_node]
        path.append(curr_node)

    return path[::-1]


########################
#        TESTING       #
########################

def test_bfs(floor_plan, batch, start_coords):
    """
    Runs BFS from given start coordinates
    on an image and saves BFS tree (parent dict.) to 
    a pickle file
    """
    DIRECTORY = f"{floor_plan}_test"
    im_filepath = f"{DIRECTORY}/{floor_plan}_reduced.png"
    image = load_color_image(im_filepath)

    for test_num, start_coord in enumerate(start_coords):
        start_t = time.perf_counter()
        parent = bfs(image, start_coord)
        print(f"BFS test {test_num} time: {time.perf_counter() - start_t}")

        # Draw BFS tree
        save_image_with_path_drawn(im_filepath, f"{DIRECTORY}/{floor_plan}_bfs.png", parent["parent_ptrs"])

        # Save pickle file
        pickle_name = f"{DIRECTORY}/{floor_plan}_batch{batch}_{test_num}.pickle"
        
        with open(pickle_name, "wb") as f:
            pickle.dump(parent, f)

def test_bfs_paths(floor_plan, pickle_batch, test_batch, test_num, end_coords):
    """
    Saves PNGs w/ shortest path drawn given a BFS tree
    and a list of destination coordinates
    """
    DIRECTORY = f"{floor_plan}_test"
    pickle_name = f"{DIRECTORY}/{floor_plan}_batch{pickle_batch}_{test_num}.pickle"
    im_filepath = f"{DIRECTORY}/{floor_plan}_reduced.png"

    with open(pickle_name, "rb") as f: # unpickle
        tree = pickle.load(f)
    
    for test_num, end_coord in enumerate(end_coords):
        path = build_sp(tree, end_coord)
        start = tree["start"]
        save_image_with_path_drawn(im_filepath, f"{DIRECTORY}/{floor_plan}_sp_{start}_batch{test_batch}_{test_num}.png", path)

def ask_for_coords(coords):
    """
    Appends user-given coordinates to given list
    """
    user = ""
    while user != "done":
        user = input("Type in coordinates (ex. 120 150): ")
        try:
            coord = tuple(int(num) for num in user.split())
            coords.append(coord)
        except ValueError as e:
            pass

def full_bfs_test():
    # PRODUCING PICKLE FILES
    floor_plan = input("Floor plan? : ") 
    batch = input("Batch? : ")

    # Grab source coordinates for BFS
    start_coords = []
    ask_for_coords(start_coords)
    test_bfs(floor_plan, batch, start_coords)


    # DRAWING PATHS FROM PICKLE FILES
    floor_plan = input("Floor plan? : ") 
    pickle_batch = input("Pickle batch? : ")
    test_batch = input("Test batch? : ")
    test_num = input("Pickle test number? : ")

    # Grab destination coordinates
    end_coords = []
    ask_for_coords(end_coords)
    test_bfs_paths(floor_plan, pickle_batch, test_batch, test_num, end_coords)
 


def test_reduce_and_crop(DIRECTORY, floor_plan):
    original_filename = f"{DIRECTORY}/{floor_plan}_nontext.png"
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    reduced_filename = f"{DIRECTORY}/{floor_plan}_reduced.png"

    start = time.perf_counter()
    cropped = crop_image(original_filename, cropped_filename)
    end_crop = time.perf_counter()
    print(f"Crop time: {end_crop - start}")

    reduced, reduction_factor = reduce_resolution(cropped, reduced_filename, r=17)
    end_reduce = time.perf_counter()
    print(f"Reduce time: {end_reduce - end_crop}")
    print(f"Total time: {end_reduce - start}")
    return reduced, reduction_factor    


def test_duplicate_graph(DIRECTORY, floor_plan, reduced_im):
    print("RUNNING TEST...")
    start = time.perf_counter()
    graph = preprocessing_via_duplicate_graph(reduced_im, 25)
    print("FINISHED TEST...")
    print(f"Duplicate graph creation: {time.perf_counter() - start}")

    # Save graph to pickle file
    with open(f"{DIRECTORY}/{floor_plan}_graph.pickle", "wb") as f:
        pickle.dump(graph, f)
    
    return graph


def test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor):
    """
    Given a graph, a start and end coordinate on the UNALTERED IMAGE,
    return an image w/ the shortest path drawn between start and end
    """
    start_reduced = (start[0]//reduction_factor, start[1]//reduction_factor)
    end_reduced = (end[0]//reduction_factor, end[1]//reduction_factor)

    # Get path
    path_low_res = Dijkstar_duplicated_graph(graph, start_reduced, end_reduced)
    path_high_res = expand_coords(path_low_res, reduction_factor)

    # Draw path onto CROPPED image
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    new_filename = f"{DIRECTORY}/{floor_plan}_{start}_{end}_path.png"
    save_image_with_path_drawn(cropped_filename, new_filename, path_high_res)

def test():
    floor_plan = input("Floor plan? (ex. 1_2): ")
    DIRECTORY = f"tests/{floor_plan}_test"

    with open(f"{DIRECTORY}/{floor_plan}_graph.pickle", "rb") as f:
        graph = pickle.load(f)
    
    start = 270, 360
    end = 2700, 3100
    test_path_finding(DIRECTORY, floor_plan, graph, start, end, 17)


if __name__ == "__main__":
    test()