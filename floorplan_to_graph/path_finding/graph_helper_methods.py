from collections import deque
from floorplan_to_graph.png_helper_methods import *
from dijkstar import Graph, find_path


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
                        and sum(get_pixel(image, *(x + dx, y + dy) )) >= 250*3]


def get_left_right_neighbors(image, x, y):
    """
    Returns left-right white neighbors of (x, y) 
    """
    return [(x + dx, y) for dx in [-1, 1] 
                if in_bounds(image, *(x + dx, y)) and 
                    sum(get_pixel(image, *(x + dx, y))) >= 250*3]

def get_up_down_neighbors(image, x, y):
    """
    Returns up-down white neighbors of (x, y) 
    """
    return [(x, y + dy) for dy in [-1, 1] 
                if in_bounds(image, *(x, y + dy)) and 
                    sum(get_pixel(image, *(x, y + dy))) >= 250*3]