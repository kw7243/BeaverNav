from svgpathtools.parser import parse_transform
from svgpathtools.path import transform as path_transform
import math 
from collections import defaultdict
import numpy as np
from svgpathtools import svg2paths2, wsvg

"""
Two functions that convert string of the form 'x:1;y:2;z:3;' to a dictionary of the form {x:1, y:2, z:3}, and viceversa
Useful to update style of an SVG. Used on the 'update_attribute' function below
-Raul
"""

def string_to_dict(s):
	values = s.split(";")
	return {v.split(":")[0]: v.split(":")[1] for v in values if len(v) > 0}

def dict_to_string(d):
	return ";".join(f"{key}:{val}" for key, val in d.items()) + ";"

def remove_from_list(l, indices):
  """
  returns a list with some indexes removed
  e.g remove_from_list([50, 60, 70, 80], [1, 3]) should return [50, 70]
  This is particularly useful to remove some SVG paths that are not valid (or not important)
  Common example:
    paths, attributes, svg_attributes = svg2paths2(svg_path)
    to_delete = [] #indices
    for i, path in enumerate(paths):
      if not a good/interesting path:
        to_delete.append(i)
    new_paths = remove_from_list(new_paths, to_delete)
    new_attributes = remove_from_list(new_attributes, to_delete)
    #Now can use new_paths, new_attributes and svg_attributes to create a new SVG/PDF
  -Raul  
  """

  indices = [-1] + indices + [len(l)]
  res = []
  for i in range(len(indices) -1):
    res +=  l[indices[i]+1: indices[i+1]]
  return res

def show_svg(filename, is_local=True):
  # display(SVG(url='http://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg'))
  if is_local:
    display(SVG(filename=filename))
  else:
    display(SVG(url=filename))
"""
Saves given svg to a temporary file and shows it
"""
def visualize_all_paths(paths, attributes, svg_attributes, output, show = False):
  wsvg(paths, filename=output, attributes=attributes, svg_attributes=svg_attributes)
  if show:
    show_svg(output)

COLORS = ['red', 'green', 'blue', 'yellow', 'cyan', 'purple'] # colors in a given width, in order

def get_real_path(path, attribute):
  return  path_transform(path, parse_transform(attribute.get('transform', '')))

def is_door(path, attribute):
  """
  Returns wheter a given path is a door by checking
  1. it's not closed
  2. it's continuous
  3. it's curved
  4. The curve length of the path / linear length = pi / 2sqrt(2) [what you'd expect in a quarter of a circle]
  """
  if len(path) == 0:
    return False
  if not path.iscontinuous():
    return False
  if path.isclosed() or "C" not in attribute['d']:
    return False
  if "C" not in attribute['d']:
    return False
  real_path = get_real_path(path, attribute)
  start, end = real_path.start, real_path.end
  diff = start-end
  segment_length = math.sqrt((diff.real)**2 + (diff.imag)**2)
  curve_length = real_path.length()
  if segment_length == 0:
    return False
  q = curve_length / segment_length #should be pi / 2sqrt(2) coz math
  good_q = math.pi / (2 * math.sqrt(2))
  return abs(q/good_q - 1) < 1e-2
 

def find_and_update_doors(paths, attributes):
  new_paths= paths.copy()
  new_attributes = attributes.copy()

  door_ids = []
  to_delete_segments = []
  for i, (path, attribute) in enumerate(zip(new_paths, new_attributes)):
    if not is_door(path, attributes[i]):
      continue
    print("Found door at position i = ", i)
    # Finding what path to add and
    to_delete_segments.append(i)
    door_ids.append(i)
 
  print("Number of doors found:", len(door_ids))
  new_paths = remove_from_list(new_paths, to_delete_segments)
  new_attributes = remove_from_list(new_attributes, to_delete_segments)
  return new_paths, new_attributes


if __name__ == '__main__':
  paths, attributes, svg_attributes = svg2paths2('1_2.svg')

  new_paths, new_attributes = find_and_update_doors(paths,attributes)

  # print("new_paths are: ",new_paths)
  # print("new_attributes are: ",new_attributes)
  wsvg(paths, attributes=new_attributes, svg_attributes=svg_attributes, filename='output1.svg')