from svgpathtools.parser import parse_transform
from svgpathtools.path import transform as path_transform
import math 
from collections import defaultdict
import numpy as np
from IPython.display import SVG, display

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

def update_attribute(attribute, key, val):
  """
  Updates style (or creates if not existent) of an attribute
  params:
    - attribute: dictionary of the form outputted by svg2paths2
    - key: new key to add (e.g., stroke)
    - val: new value to add for the key (e.g., 'red')
  returns the new attribute
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

def get_palette(widths):
  """
  Updates style (or creates if not existent) of an attribute
  params:
    - widths: something of the form '-1,1,2,4'
  returns a dictionary width -> color
  """
  widths = [float(x) for x in widths.split(",")] #should be sorted as well
  res = dict()
  for (i, width) in enumerate(widths):
    res[width] = COLORS[i]
  return res

def inverse_transform(real_point, transform):
  """
  returns the complex point p such that
  real_coordinates(p, transform) == real_point
  """
  matrix = parse_transform(transform)
  output_x, output_y = real_point.real - matrix[0][-1], real_point.imag - matrix[1][-1]
  output_matrix = np.array([[output_x, output_y]])
  res = output_matrix @ np.linalg.inv(matrix[0:2, 0:2])
  real, imag = res[0]
  return real + 1j*imag

def get_real_path(path, attribute):
  return  path_transform(path, parse_transform(attribute.get('transform', '')))

def build_corner_dict(paths, attributes):
  """
  Returns two dictionaries:
  - start_paths: Maps (real) positions -> list of (i, path, attribute) that start on such points
  - end_paths:  Maps (real) positions -> list of (i, path, attribute) that ends on such points
  """
  start_paths = defaultdict(list)
  end_paths = defaultdict(list)
  for i, (path, attribute) in enumerate(zip(paths, attributes)):
    real_path = get_real_path(path, attribute)
    real_start, real_end = real_path.start, real_path.end
    real_start_key, real_end_key = int(real_start.real) + 1j*int(real_start.imag), int(real_end.real) + 1j * int(real_end.imag)
    start_paths[real_start_key].append((i, path, attribute))
    end_paths[real_end_key].append((i, path, attribute))
  print("Start_paths and end_paths succesfully constructed!")
  return start_paths, end_paths
  
def is_door(path, attribute):
  """
  Returns wheter a given path is a door by checking
  1. it's not closed
  2. it's continuous
  3. it's curved
  4. The curve length of the path / linear length = pi / 2sqrt(2) [what you'd expect in a quarter of a circle]
  """
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

MAX_CHANGE = 0.5 # real coordinates that differ up to this value will be considered the same
def change_door(door_path, door_attribute, start_dict, end_dict):
  # takes a path of a door and returns 
  # the "closed segment" of it and its respective index
  # start_dict is a dictionary from position -> paths that start on that position
  # end_dict is a dictionary from position -> paths that end on that position
  # Returns None if it couldn't find a segment that share a vertice with the door
  # DOES NOT WORK CONSISTENTLY

  first_start, first_end = door_path.start, door_path.end
  transform = door_attribute.get('transform', '')
  real_path = get_real_path(door_path, door_attribute)
  start, end = real_path.start, real_path.end
  # start, end = real_coordinates(first_start, transform), real_coordinates(first_end, transform)
  start_int, end_int = int(start.real)+1j*int(start.imag), int(end.real)+1j*int(end.imag)

  print("start, end", start, end)
  print("attribute, ", door_attribute)

  final_path = None
  final_path_index = None
  # Checking segments that start in the same point as the door 
  print("start_dict.get(start, []):")
  for i, segment, segment_attribute in start_dict.get(start_int, []):
    segment_transform = segment_attribute.get('transform', '')
    real_segment = get_real_path(segment, segment_attribute)
    segment_start, segment_end = real_segment.start, real_segment.end
    if segment == door_path:
      continue
    if abs(segment_end.real - end.real) < MAX_CHANGE or \
       abs(segment_end.imag - end.imag) < MAX_CHANGE: 
      print("\t", segment_start,segment_end, f"position {i}")
      transformed_start, transformed_end = inverse_transform(segment_end, transform), inverse_transform(end, transform)
      final_path = Path(Line(segment.end, first_end))
      final_path_index = i
  # Cheking segments that start at the point where the door ends
  print("start_dict.get(end, [])")
  for i, segment, segment_attribute in start_dict.get(end_int, []):
    segment_transform = segment_attribute.get('transform', '')
    real_segment = get_real_path(segment, segment_attribute)
    segment_start, segment_end = real_segment.start, real_segment.end
    if segment == door_path:
      continue
    if abs(segment_end.real - start.real) < MAX_CHANGE or \
       abs(segment_end.imag - start.imag) < MAX_CHANGE:
      print("\t", segment_start,segment_end, f"position {i}")
      transformed_start, transformed_end = inverse_transform(segment_end, transform), inverse_transform(start, transform)
      final_path = Path(Line(segment.end, first_start))
      final_path_index = i
  #Checking segments that end where the door starts
  print("end_dict.get(start, [])")
  for i, segment, segment_attribute in end_dict.get(start_int, []):
    segment_transform = segment_attribute.get('transform', '')
    real_segment = get_real_path(segment, segment_attribute)
    segment_start, segment_end = real_segment.start, real_segment.end
    if segment == door_path:
      continue
    if abs(segment_start.real - end.real) < MAX_CHANGE or \
       abs(segment_start.imag - end.imag) < MAX_CHANGE:
      print("\t", segment_start,segment_end, f"position {i}")
      transformed_start, transformed_end = inverse_transform(segment_start, transform), inverse_transform(end, transform)
      final_path = Path(Line(transformed_start, transformed_end))
      final_path_index = i
  #Checking segments that end where the door ends
  print("end_dict.get(end, [])")
  for i, segment, segment_attribute in end_dict.get(end_int,[]):
    segment_transform = segment_attribute.get('transform', '')
    real_segment = get_real_path(segment, segment_attribute)
    segment_start, segment_end = real_segment.start, real_segment.end
    if segment == door_path:
      continue
    if abs(segment_start.real - start.real) < MAX_CHANGE or \
       abs(segment_start.imag - start.imag) < MAX_CHANGE:
       print("\t", segment_start,segment_end, f"position {i}")
       transformed_start, transformed_end = inverse_transform(segment_start, transform), inverse_transform(start, transform)
       final_path = Path(Line(transformed_start, transformed_end))
       final_path_index = i
      #  return final_path
  print("ENDED, final_path: ")
  print(final_path)
  print("final_path_index: ", final_path_index)
  print()
  return final_path, final_path_index
    
def find_and_update_doors(paths, attributes, start_paths, end_paths):
  new_paths= paths.copy()
  new_attributes = attributes.copy()

  door_ids = []
  to_delete_segments = []
  for i, (path, attribute) in enumerate(zip(new_paths, new_attributes)):
    if not is_door(path, attributes[i]):
      continue
    print("Found door at position i = ", i)
    # Finding what path to add and 
    new_path, new_path_index = change_door(path, attribute, paths, attributes)
    color = COLORS[0]
    if new_path is not None: #if it was able to find a segment close to it
      new_paths[i] = new_path # update the door with a segment that closes it 
      #to_delete_segments.append(new_path_index) #don't forget to delete the segment next to the door 
      new_attributes[i] = update_attribute(attribute, 'stroke-width', 0.7) #so that it's more visible 
      color = np.random.choice(COLORS[1:])
    new_attributes[i] = update_attribute(new_attributes[i], 'stroke', color) #so that it's more visible 
    door_ids.append(i)
  print("Number of doors found:", len(door_ids))
  new_paths = remove_from_list(new_paths, to_delete_segments)
  new_attributes = remove_from_list(new_attributes, to_delete_segments)
  return new_paths, new_attributes
