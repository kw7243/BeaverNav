import time as time
import pickle
from PIL import Image

########################
#   HELPER FUNCTIONS   #
########################

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

def get_acceptable_neighbors(x, y, acceptable_pixels):
    """
    Returns up-down-left-right neighbors of (x,y)
    that are in the set "acceptable_pixels"
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

# def get_neighbors_racist(image, x, y):
#     """
#     Returns only neighbors if they're > 5 pixels away from black pixels
#     """
#     result = []
#     for direction in direction_vector:
#         new_coord = (x + direction_vector[direction][0], y + direction_vector[direction][1])

#         if (in_bounds(image, *new_coord) and sum(get_pixel(image, *new_coord)) > 250*3 
#             and all(sum(get_pixel(image, *coord)) > 250*3 for coord in get_coord_box(image, *new_coord))):
            
#             result.append(new_coord)

#     return result


########################
#    PREPROCESSING     #
########################

def preprocessing_function(image, threshold = 4):
    """
    Given an image, returns a set of pixels that 
    are not within "threshold" pixels of darker pixels
    (white pixels a good distance away from black pixels)

    This is to produce a BFS tree w/ paths that don't 
    hug against walls (to produce more realistic paths)
    """
    acceptable_pixels = set()

    for x in range(1,image['width']):
        for y in range(1,image['height']):
            new_coord = (x,y)

            if (sum(get_pixel(image, *new_coord)) > 250*3 and 
                all(sum(get_pixel(image, *coord)) > 250*3 
                    for coord in get_radial_sweep(image, *new_coord, threshold))):
                # add in coordinate only if it itself is white
                # and all neighbors 
                # in "threshold" pixel radius are white
                acceptable_pixels.add(new_coord)

    return acceptable_pixels            



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

def apsp(image, sources):
    """
    Runs APSP on an image given a 
    representative set of sources 
    """
    parent = {}
    for src in sources:
        parent[src] = bfs(image, src)
    
    return parent

def save_image_with_path_drawn(image_name, new_name, relevant_pixels):
    """
    Colors all pixels in "relevant pixels" RED 
    on a copy of an image and saves the new image
    w/ a path drawn
    """
    im_copy = load_color_image(f"{image_name}") # create copy of image
    
    for pixel in relevant_pixels:

        set_pixel(im_copy, (255,0,0), *pixel) # color red
    
    save_color_image(im_copy, new_name)



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


def test_paths(floor_plan, pickle_batch, test_batch, test_num, end_coords):
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


def test():
    # # PRODUCING PICKLE FILES
    # floor_plan = input("Floor plan? : ") 
    # batch = input("Batch? : ")

    # # Grab source coordinates for BFS
    # start_coords = [] 
    # ask_for_coords(start_coords)
    # test_bfs(floor_plan, batch, start_coords)


    # DRAWING PATHS FROM PICKLE FILES
    floor_plan = input("Floor plan? : ") 
    pickle_batch = input("Pickle batch? : ")
    test_batch = input("Test batch? : ")
    test_num = input("Pickle test number? : ")

    # Grab destination coordinates
    end_coords = []
    ask_for_coords(end_coords)
    test_paths(floor_plan, pickle_batch, test_batch, test_num, end_coords)


def main():
    DIRECTORY = "7_1_test"
    pickle_name = f"{DIRECTORY}/7_1_reduced_batchA_0.pickle"
    im_name = f"{DIRECTORY}/7_1_reduced"

    with open(pickle_name, "rb") as f:
        tree = pickle.load(f)
        save_image_with_path_drawn(im_name, "test.png", tree["parent_ptrs"])


if __name__ == "__main__":
    test()
    # main()