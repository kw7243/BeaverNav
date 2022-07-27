from svgpathtools.parser import parse_transform
from svgpathtools.path import transform as path_transform
from IPython.display import SVG, display
from svgpathtools import svg2paths2, wsvg, Path
import numpy as np
import math

COLORS = ['red', 'green', 'blue', 'yellow', 'cyan', 'purple'] # colors in a given width, in order 

def string_to_dict(s):
    """
    Given a string of the form "x:1;y:2;z:3;",
    returns the corresponding dictionary
    """
    items = s.split(";")
    return {item.split(":")[0]: item.split(":")[1] for item in items if item}

def dict_to_string(d):
    """
    Given a dictionary, returns a representative
    string such as "x:1;y:2;z:3;"
    """
    return ";".join(f"{key}:{val}" for key, val in d.items()) + ";" 

def get_palette(widths):
    """
    Updates style (or creates if not existent) of an attribute
    params:
    - widths: something of the form '-1,1,2,4'
    returns a dictionary width -> color
    """
    widths = [float(x) for x in widths.split(",")] #should be sorted as well
    res = dict()

    for i, width in enumerate(widths):
        res[width] = COLORS[i]

    return res

def update_attribute(attribute, key, val):
    """
    Updates style (or creates if not existent) of an attribute
    
    Params:
    - attribute: dictionary of the form outputted by svg2paths2
    - key: new key to add (e.g., stroke)
    - val: new value to add for the key (e.g., 'red')
    
    Returns the new attribute
    """
    new_attribute = attribute.copy()
    if 'style' not in new_attribute:
        style = ''
    else:
        style = new_attribute['style']
    
    d = string_to_dict(style)
    d[key] = val #update!
    s = dict_to_string(d)
    new_attribute['style'] = s
    return new_attribute


def inverse_transform(real_point, transform):
    """
    Returns the complex point p such that
    real_coordinates(p, transform) == real_point
    """
    matrix = parse_transform(transform)
    output_x, output_y = real_point.real - matrix[0][-1], real_point.imag - matrix[1][-1]
    output_matrix = np.array([[output_x, output_y]])
    res = output_matrix @ np.linalg.inv(matrix[0:2, 0:2])
    real, imag = res[0]
    return real + 1j*imag


def remove_from_list(l, indices_to_delete):
    """
    Given a list l and a set of indicies to delete,
    return a new list w/o elements at those indices
    """
    res = []

    for i, item in enumerate(l):
        if i not in indices_to_delete:
            res.append(item)

    return res

def show_svg(filename, is_local=True):
    if is_local:
        display(SVG(filename=filename))
    else:
        display(SVG(url=filename))


def visualize_paths(paths, attributes, svg_attributes, file_name, show=False):
    """
    Saves given svg to a temporary file and shows it
    """
    wsvg(paths, filename=file_name, attributes=attributes, svg_attributes=svg_attributes)
    if show:
        show_svg(file_name)


def get_real_path(path, attribute):
    return path_transform(path, parse_transform(attribute.get('transform', '')))


def is_door(path, attribute):
    """
    Returns True if given path is a door else False.

    Conditions for a door:
    - Not empty
    - Continuous
    - Not closed
    - Curved (designated by presence of a "C" command AKA curveto)
    - Arc length of the path/linear length = pi/2sqrt(2) 
      [what you'd expect in a quarter of a circle]
    """
    if not(path.iscontinuous() and not path.isclosed() and 
            ("C" in attribute["d"] or "c" in attribute["d"])):
        return False
    
    real_path = get_real_path(path, attribute)
    curve_length = real_path.length() # get arc length of path

    if curve_length > 20:
        return False

    diff = real_path.start - real_path.end
    segment_length = math.sqrt((diff.real)**2 + (diff.imag)**2) # get distance between endpoints of path
    

    if segment_length == 0:
        return False
    
    test_ratio = curve_length / segment_length
    ideal_ratio1 = math.pi / (2*math.sqrt(2)) # for a quarter circle arc
    ideal_ratio2 = math.pi/2 + 1 # for quarter circle arc + radial line

    # Is door only if ratios within 1% of ideal ratios
    return abs(test_ratio/ideal_ratio1 - 1) < 1e-1 or abs(test_ratio/ideal_ratio2 - 1) < 1e-1
 

def remove_doors(paths, attributes):
    """
    Given a list of Path objects 
    and corresponding list of attribute dictionaries,
    find door paths and remove them from both the image's
    paths and attributes 

    Returns new list of paths and attributes w/
    doors removed
    """
    indices_to_delete = set()

    # iterate over paths and attributes
    for i, (path, attribute) in enumerate(zip(paths, attributes)):
        if is_door(path, attribute):
            print(get_real_path(path, attribute).length())
            # print("Found door at position i = ", i)
            indices_to_delete.add(i)

    # print(f"Number of doors found: {i}")
    new_paths = remove_from_list(paths, indices_to_delete)
    new_attributes = remove_from_list(attributes, indices_to_delete)
    return new_paths, new_attributes


def remove_empty_paths(paths, attributes):
    """
    Conversion to SVG sometimes results in empty paths,
    which interfere w/ many operations

    Returns new paths and attributes w/ empty paths removed/
    """
    indices_to_remove = set()

    for i, path in enumerate(paths):
        if path == Path():
            indices_to_remove.add(i)

    paths = remove_from_list(paths, indices_to_remove)
    attributes = remove_from_list(attributes, indices_to_remove)

    return paths, attributes


def get_doors(paths, attributes):
    """
    Returns new paths and attributes of those 
    corresponding to doors
    """
    to_delete = set()

    for i, (path, attribute) in enumerate(zip(paths, attributes)):
        if not is_door(path, attribute):
            to_delete.add(i)
    
    door_paths = remove_from_list(paths, to_delete)
    door_attributes = remove_from_list(attributes, to_delete)

    return door_paths, door_attributes


if __name__ == "__main__":
    paths, attr, svg_attr = svg2paths2("door_detection/tests/32_1.svg")
    paths, attr = remove_empty_paths(paths, attr)
    print(svg_attr)
    new_paths, new_attr = remove_doors(paths, attr)

    wsvg(new_paths, filename="door_detection/tests/32_1_no_doors_threshold.svg", attributes=new_attr, svg_attributes=svg_attr)
