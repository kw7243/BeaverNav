%%time
from svgpathtools import CubicBezier, Path, Line, smoothed_path, wsvg, svg2paths2
from collections import defaultdict
import pprint
from os import listdir, system
from os.path import isfile, join

pdf_dir = "/content/drive/MyDrive/FreshStart/PDF Floor Plans" # replace
svg_dir = "/content/drive/MyDrive/FreshStart/SVG Floor Plans" # replace

svgs = [f for f in listdir(svg_dir) if isfile(join(svg_dir, f))]


pp = pprint.PrettyPrinter(indent=4)

full_widths = set() # set of all possible widths
group_dict = defaultdict(list) # set of widths -> num of floor plan names whose widths are exactly that set
groupcount_dict = defaultdict(int) # set of widths -> floor plan names whose widths are exactly that set
width_dict = dict() #floor plan name -> widths

for i, svg in enumerate(svgs):
  svg_path = join(svg_dir, svg)
  print(f"#{i+1}/{len(svgs)}: {svg_path}")
  paths, attributes, svg_attributes = svg2paths2(svg_path)
  svg = svg[:-4] # getting rid of the trailing svg
  widths = set() # set of widths in this floor plan
  for i, attribute in enumerate(attributes):
    if len(paths[i]) == 0: #bad formatted paths
      continue
    if 'style' not in attribute:
      style_dict = dict()
    else:
      style_dict = string_to_dict(attribute['style'])
    stroke_width = style_dict.get('stroke-width', '-1')
    widths.add(stroke_width)
  group = ",".join(sorted(list(widths), key= lambda x: float(x)))
  groupcount_dict[group] += 1
  group_dict[group].append(svg)
  full_widths.update(widths)
  width_dict[svg] = group 
  print(f"Widths now = {widths}. Widths so far = {full_widths} \n")

pp.pprint(groupcount_dict)
pp.pprint(group_dict)
pp.pprint(width_dict)
