from PIL import Image
import numpy as np
import cv2
import time
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

    list_of_coords = [(x, y), "horizontal/vertical"]
    
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
    

def crop_image_cv2(filename, new_filename):
    """
    Information for Van + Michael:
        1. Input your 1) Filepath of your png image you wanna crop and 2) the new filepath
        2. The function should crop it easily now

    Given a file name of a floor plan,
    crops out the legend and unnecessary white space
    """
    im = cv2.imread(filename)
    gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Crop out legend and outer border
    height, width = gray_im.shape
    left = int(0.038*width)
    right = int(0.96*width)
    top = int(0.038*height)
    bottom = int(0.89*height)

    gray_im = gray_im[top:bottom, left:right]
    height, width = gray_im.shape

    # Get bounding box of meat of floor plan 
    inverted_im = 255*(gray_im < 100).astype(np.uint8) # invert all black to white
    coords = cv2.findNonZero(inverted_im) # get all white pixel
    x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
    
    # Add 1% padding for cropping
    y_buffer = int(0.01*height) 
    x_buffer = int(0.01*width)

    # Crop the image 
    rect = gray_im[y - y_buffer:(y + h) + y_buffer, x - x_buffer:(x + w) + x_buffer]
    cv2.imwrite(new_filename, rect) # save image