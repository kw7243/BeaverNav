import time
import pickle
from collections import deque
from PIL import Image
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

def reduce_resolution(cropped_image, new_filename=None, r=16):
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
    return reduced_image



def expand_coords(list_of_coords, r=16):
    """
    Converts a list of coordinates in lower res image
    to coordinates in higher res image
    based on the reduction factor r

    Ex. 
    In a lower res image reduced by 5, 
    (1, 1) corresponds to all 25 coordinates 
    inclusive within this range: (5, 5) --> (10, 10)
    """
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
    borders = (160, 160, w - 160, h - 500)
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


def distances_to_black(image):
    """
    Given an image (internal rep.),
    return the shortest distance of 
    every white pixel to the nearest black pixel
    """
    distances = {} # (x, y) --> distance to black pixel
    visited = set()

    q = deque([])
    for x in range(image['width']):
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*250:
                # black pixel
                q.append((x, y))
                distances[(x, y)] = 0

    while q:
        coord = q.popleft()

        for neighbor_coord in get_white_neighbors(image, *coord):
            if neighbor_coord not in visited:
                distances[neighbor_coord] = distances[coord] + 1
                q.append(neighbor_coord)
                visited.add(neighbor_coord)
    
    return distances



def distance_to_black(image, coord):
    """
    Given a coordinate and image (internal rep.), 
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

        if curr_node[1] >= 20:
            return 20

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
    distances = distances_to_black(image) # stores pixel distances of coords to nearest black pixel

    for x in range(image['width']):
        for y in range(image['height']):
            
            if sum(get_pixel(image, x, y)) < 250*3:
                continue

            u = (x, y)
            for v_horizontal in get_left_right_neighbors(image, *u):
                # w(u_horiz, v_horiz) = k/d^2
                edge_weight = k*1/(distances[v_horizontal])**2
                graph.add_edge((u, 'horizontal'), (v_horizontal, 'horizontal'), edge_weight)

                # w(u_vert, v_horiz) = k
                edge_weight = k
                graph.add_edge((u,'vertical'), (v_horizontal,'horizontal'), edge_weight)
                
            for v_vertical in get_up_down_neighbors(image, *u):
                # w(u_vert, v_vert) = k/d^2
                edge_weight = k* 1/(distances[v_vertical])**2
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
#        TESTING       #
########################

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


def test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor):
    original_filename = f"{DIRECTORY}/{floor_plan}_nontext.png"
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    reduced_filename = f"{DIRECTORY}/{floor_plan}_reduced.png"

    try: # in case already cropped and reduced already
        return load_color_image(reduced_filename)

    except FileNotFoundError as e:
        start = time.perf_counter()
        cropped = crop_image(original_filename, cropped_filename)
        end_crop = time.perf_counter()
        print(f"Crop time: {end_crop - start}")

        reduced = reduce_resolution(cropped, reduced_filename, reduction_factor)
        end_reduce = time.perf_counter()
        print(f"Reduce time: {end_reduce - end_crop}")
        print(f"Total time: {end_reduce - start}")
        return reduced  


def test_duplicate_graph(DIRECTORY, floor_plan, reduced_im):
    print("\nCREATING GRAPH...")
    start = time.perf_counter()
    graph = preprocessing_via_duplicate_graph(reduced_im, 25)
    print("FINISHED GRAPH CREATION...")
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
    t_start = time.perf_counter()
    path_low_res = Dijkstar_duplicated_graph(graph, start_reduced, end_reduced)
    t_find_path = time.perf_counter()
    print(f"Dijkstar find_path (duplicated graph) time: {t_find_path - t_start}")

    path_high_res = expand_coords(path_low_res, reduction_factor)
    t_expand_coords = time.perf_counter()
    print(f"Expanding coords time: {t_expand_coords - t_find_path}")

    # Draw path onto CROPPED image
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    new_filename = f"{DIRECTORY}/{floor_plan}_{start}_{end}_path.png"

    save_image_with_path_drawn(cropped_filename, new_filename, path_high_res)
    print(f"Draw path time: {time.perf_counter() - t_expand_coords}")

    print(f"User interface time: {time.perf_counter() - t_start}")


def test_full_Dijkstar(DIRECTORY, floor_plan, reduction_factor):
    """
    Given a floor plan, reduction factor,
    and its directory w.r.t. path_finding, runs a full test:

    1. Crop and reduce image
    2. Ask user for start and end coordinates
    3. Create graph if doesn't already exist
    4. Draw the shortest path between the start and end coords.
    """
    reduced = test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor)

    print("\nEnter start coordinates")
    start_coords = ask_for_coords()
    print("\nEnter end coordinates")
    end_coords = ask_for_coords()

    try:
        with open(f"{DIRECTORY}/{floor_plan}_graph.pickle", "rb") as f:
            graph = pickle.load(f)
    except FileNotFoundError as e:
        graph = test_duplicate_graph(DIRECTORY, floor_plan, reduced)

    for start, end in zip(start_coords, end_coords):
        test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor)


def test():
    floor_plan = input("Floor plan? (ex. 1_2): ")
    DIRECTORY = f"tests/{floor_plan}_test"
    reduction_factor = int(input("Reduction factor?: "))

    reduced_im = test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor)
    test_duplicate_graph(DIRECTORY, floor_plan, reduced_im)

if __name__ == "__main__":
    test()