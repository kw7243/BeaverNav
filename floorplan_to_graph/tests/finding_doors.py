import door_detection.svg_helper_methods as svg_helper_methods
from svgpathtools import CubicBezier, Path, Line, smoothed_path, wsvg, svg2paths2
from BeaverNav import svg_helper_methods
svg_dir = ""
pdf_dir = ""

show_svg(svg_dir + '/1_0.svg')
filepath = svg_dir + '/1_0.svg'
paths, attributes, svg_attributes = svg2paths2(filepath)
new_paths, new_attributes = [], []
for i, (path, attribute) in enumerate(zip(paths, attributes)):
  if len(path) == 0:
    continue
  new_paths.append(path)
  new_attributes.append(attribute)
paths, attributes = new_paths, new_attributes

start_paths, end_paths = build_corner_dict(paths, attributes)
paths, attributes = find_and_update_doors(paths, attributes, start_paths, end_paths)
visualize_all_paths(paths, attributes, svg_attributes, svg_dir + "/test.svg")
