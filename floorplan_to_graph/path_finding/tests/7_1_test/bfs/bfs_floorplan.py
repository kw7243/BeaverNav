from json import load
from PIL import Image

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

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
    Returns the pixel value for the relevant x,y coordinates.
    Note that pixel values range from (1,1) to (image['width'],image['height'] with this current implementation
    """
    return image['pixels'][(y - 1) * image['width'] + x - 1] if in_bounds((x,y), image) else None


def set_pixel(image, x, y, c):
    """
    Sets the pixel value for the desired x,y coordinates.
    Note that pixel values range from (1,1) to (image['width'],image['height'] with this current implementation
    """
    image['pixels'][(y-1)*image['width']+x-1]= c

def in_bounds(coord, image):
    """ 
    Returns bool saying whether coordinate is in bounds of an image
    """

    return 0 <= coord[0] < image["width"] and 0 <= coord[1] < image["height"]

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def get_white_neighbors(image, x, y):
    """
    Returns only white/near-white neighbors of 
    a given pixel --> pixel vals > 254)
    """
    result = []
    for direction in direction_vector:
        new_coord = (x + direction_vector[direction][0], y + direction_vector[direction][1])

        if in_bounds(new_coord, image) and sum(get_pixel(image, *new_coord)) > 250*3:
            result.append(new_coord)

    return result

def get_coord_box(image, x, y):
    result = []
    for dx in range(-5,6):
        for dy in range(-5,6):
            if dx == 0 and dy == 0:
                continue

            new_coord = (x+dx,y+dy)

            if in_bounds(new_coord, image):
                result.append(new_coord)

    return result


def get_neighbors_racist(image, x, y):
    """
    Returns only neighbors if they're > 5 pixels away from black pixels
    """
    result = []
    for direction in direction_vector:
        new_coord = (x + direction_vector[direction][0], y + direction_vector[direction][1])

        if (in_bounds(new_coord, image) and sum(get_pixel(image, *new_coord)) > 250*3 
            and all(sum(get_pixel(image, *coord)) > 250*3 for coord in get_coord_box(image, *new_coord))):
            
            result.append(new_coord)

    return result


def bfs(image, start):
    """
    Returns BFS tree rooted at a start pixel in the form
    of parent pointers for an image
    """
    parent = {start: start} # mapping (x1,y1): (x2,y2)
    agenda = [start]

    while agenda:
        curr_node = agenda.pop(0)

        for child in get_neighbors_racist(image, *curr_node):
            if child not in parent: # if unvisited
                parent[child] = curr_node
                agenda.append(child)

    return parent 

def unweighted_sp(parent, start, end): 
    """
    Builds a shortest unweighted path from parent pointers
    """
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


def save_image_with_path_drawn(image_name, new_name, relevant_pixels):
    """
    Colors all pixels in "relevant pixels" blue on a copy of an image
    and saves it
    """
    im_copy = load_color_image(image_name) # create copy of image
    
    for pixel in relevant_pixels:
        set_pixel(im_copy, *pixel, (0,0,255)) # color blue
    
    save_color_image(im_copy, new_name)

def test():
    im_name = "floorplantest_reduced.png"
    im = load_color_image(im_name)
    
    ## Single-source SP from start to every other node ##
    start = (661, 255)
    parent = bfs(im, start)
    ##########################################

    # Visualize BFS tree
    # save_image_with_path_drawn(im_name, "floorplantest_tree.png", parent)
    ####################


    # Test #1: random end points
    end = (1270, 1060)
    sp = unweighted_sp(parent, start, end)
    save_image_with_path_drawn(im_name, "floorplantest_sp_atrium_far.png", sp)

    # # Test #2: far end of hallway
    # end = (737, 687)
    # sp = unweighted_sp(parent, start, end)
    # save_image_with_path_drawn(im_name, "floorplantest_sp_hallway_far.png", sp)

    # # Test #3: atrium
    # end = (823, 1004)
    # sp = unweighted_sp(parent, start, end)
    # save_image_with_path_drawn(im_name, "floorplantest_sp_atrium.png", sp)

    # # Test #4: far room
    # end = (1160, 984)
    # sp = unweighted_sp(parent, start, end)
    # save_image_with_path_drawn(im_name, "floorplantest_sp_far_room.png", sp)

def main():
    for pixel in load_color_image("doorway.png")["pixels"]:
        if any(val < 254 for val in pixel):
            print(pixel)


if __name__ == "__main__":
    test()
    # main()