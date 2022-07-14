from svgpathtools.parser import parse_transform
from svgpathtools.path import transform as path_transform
import math 
from collections import defaultdict
import numpy as np
from IPython.display import SVG, display
from svgpathtools import svg2paths2, wsvg, Path

"""
Two functions that convert string of the form 'x:1;y:2;z:3;' to a dictionary of the form {x:1, y:2, z:3}, and viceversa
Useful to update style of an SVG. Used on the 'update_attribute' function below
-Raul
"""

def remove_from_list(l, indices_to_delete):
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
  res = []

  for i,item in enumerate(l):
    if i in indices_to_delete:
      continue
    res.append(item)

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
	"""
	Given a list of Path objects 
	and corresponding list of attribute dictionaries,
	find doors and remove them

	Returns new list of paths and attributes w/
	doors removed
	"""
	door_ids = []
	to_delete_segments = set()

	# iterate over paths and attributes
	for i, (path, attribute) in enumerate(zip(paths, attributes)):
		if is_door(path, attribute):
			print("Found door at position i = ", i)
			to_delete_segments.add(i)
			door_ids.append(i)

	print(f"Number of doors found: {len(door_ids)}")
	new_paths = remove_from_list(paths, to_delete_segments)
	new_attributes = remove_from_list(attributes, to_delete_segments)
	return new_paths, new_attributes


def remove_empty_paths_attributes(paths,attributes):
  indices_to_remove = set()

  for i, path in enumerate(paths):
    if path == Path():
      indices_to_remove.add(i)

  paths = remove_from_list(paths, indices_to_remove)
  attributes = remove_from_list(attributes, indices_to_remove)

  return paths,attributes


if __name__ == '__main__':
  paths, attributes, svg_attributes = svg2paths2('1_2.svg')
  paths, attributes = remove_empty_paths_attributes(paths,attributes)
  new_paths, new_attributes = find_and_remove_doors(paths,attributes)
  visualize_all_paths(new_paths,new_attributes,svg_attributes,'output_final.svg',show=True)
