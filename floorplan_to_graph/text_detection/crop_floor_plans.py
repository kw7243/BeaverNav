### Convert pdf to svg
import subprocess
import time
import os
from os import listdir
from os.path import isfile, join
import cairosvg
from PIL import Image
import cv2
import numpy as np

beavernav = os. getcwd()

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
    Image.MAX_IMAGE_PIXELS = None
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        # img = img.convert('RGB')  # in case we were given a greyscale image
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

def in_bounds(image, x, y):
    """ 
    Returns bool representing whether (x,y) 
    is in bounds of an image
    """
    return 0 <= x < image["width"] and 0 <= y < image["height"]
    
def get_pixel(image, x, y):
    """
    Retrieves value of a pixel at (x,y) of 
    an image dictionary if in bounds, otherwise None
    """
    location = y*image["width"] + x

    # print("image_length is: ",len(image['pixels']))
    # print("location is: ",location)
    # print("(x,y) is: ",(x,y))

    return image['pixels'][location] if in_bounds(image, x, y) else None

def left_right(image):
    """
    Scans image left-right via a vertical 1D
    line, incrementing x location of the scan
    until reach a black pixel

    Returns x_min
    """
    for x in range(image['width']):
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*254:
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
            if sum(get_pixel(image, x, y)) < 3*254:
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
              if sum(get_pixel(image, x, y)) < 3*254:
                return x

def bottom_up(image):
    """
    Scans image BOTTOM-UP for a black pixel
    and returns the y-coordinate of it

    Returns y_max
    """
    for y in range(image['height'] - 1, 0, -1):
        for x in range(image['width']):
            if sum(get_pixel(image, x, y)) < 3*254:
                return y

def crop_image(filename, destination):
    """
    Given a raw png file, crops the file

    Returns the cropped file
    """
    # Open Image object
    Image.MAX_IMAGE_PIXELS = 1000000000
    image = Image.open(filename)

    width, height = image.size
    left = 0.038*width
    right = 0.96*width
    top = 0.038*height
    bottom = 0.89*height

    cropped_image_obj = image.crop((left, top, right, bottom))

    w, h = cropped_image_obj.size
    cropped_image = {'height': h, 'width': w, 'pixels': list(cropped_image_obj.getdata())} 

    # Crop out whitespace
    x_min = (left_right(cropped_image) - 40)
    x_max = (right_left(cropped_image) + 40)
    y_min = (top_down(cropped_image) - 40)
    y_max = (bottom_up(cropped_image) + 40)

    cropped_image_obj = cropped_image_obj.crop((x_min, y_min, x_max, y_max))

    # Convert cropped Image obj to internal rep
    w, h = cropped_image_obj.size

    # Save cropped Image if new file name provided
    new_filename = destination

    cropped_image_obj.save(new_filename)

    cropped_image_obj.close()
    
    x_min = x_min + left
    x_max = x_max + left
    y_min = y_min + top
    y_max = y_max + top
    return (x_min, y_min, x_max, y_max)

def crop_image_with_dimensions(filename, destination, dim):
    """
    Given a raw png file, crops the file

    Returns the cropped file
    """
    (x_min, y_min, x_max, y_max) = dim

    # Open Image object
    Image.MAX_IMAGE_PIXELS = 1000000000
    image = Image.open(filename)
    cropped_image_obj = image.crop((x_min, y_min, x_max, y_max))

    # Save cropped Image if new file name provided
    new_filename = destination

    cropped_image_obj.save(new_filename)

    cropped_image_obj.close()

def convertSVGtoPNG(floor, dpi):
	cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/PNG Floor Plans/" + floor + ".png", background_color="white", dpi=dpi) # choose on dpi

def crop_image_cv2(filename, new_filename=None):
    """
    Information for Van + Michael:
        1. Input your 1) Filepath of your png image you wanna crop and 2) the new filepath
        2. The function should crop it easily now
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
    im_copy = gray_im[::]
    width,height = im_copy.shape

    gray_im = 255*(gray_im < 100).astype(np.uint8) # To invert the text to white
    cv2.imwrite("7_1_inverted.png", gray_im) # Save the image
    coords = cv2.findNonZero(gray_im) # get all white pixel
    x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
    rect = im_copy[y-int(0.01*width):(y+h)+int(0.01*width), x-int(0.01*height):x+w+int(0.01*height)] # Crop the image - note we do this on the original image
    cv2.imwrite(new_filename, rect) # Save the image

    return (y-int(0.01*width)+top,(y+h)+int(0.01*width)+top, x-int(0.01*height)+left,x+w+int(0.01*height)+left)



if __name__ == '__main__':

    svgfiles = [f for f in listdir(svg_folder_path) if isfile(join(svg_folder_path, f))]
    for svg in svgfiles:
        floor = svg[:-4]
        convertSVGtoPNG(floor, 1200)
    ### STEP THREE:
    # I've written this step here, just run it, it should work assuming steps one and two are done correctly
    for png in os.listdir(png_folder_path):
        png_file_path = png_folder_path + "/"+png
        print(png_file_path)
        crop_image(png_file_path, png_cropped_folder_path+ '/'+png)