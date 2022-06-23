%%time
import svg_helper_methods
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


%%time
%%time
from svgpathtools import CubicBezier, Path, Line, smoothed_path, wsvg, svg2paths2
from collections import defaultdict
import pprint
from os import listdir, system
from os.path import isfile, join
from svgpathtools.parser import parse_transform
from svgpathtools.path import transform as path_transform
import cairosvg
import cv2
from google.colab.patches import cv2_imshow
from os.path import isfile, join
import os
pdf_dir = "/content/drive/MyDrive/FreshStart/PDF Floor Plans"
svg_dir = "/content/drive/MyDrive/FreshStart/SVG Floor Plans"

def color_widths(room, nontext_png_dir, text_dir, text_png_dir, nontext_svg_dir, text_svg_dir, init_threshold=10, overwrite_drive=False):
  """
  room: {building}_{room number}
  output_dir: The directory where all the intermediate svgs will be written to. This is in terms of the colab sessions.
  overwrite_drive: If False then the function won't run if the output png already exists.
  Step 1: Creates a new SVG with paths of different widths color coded. Deletes doors as well
  Step 2: We choose the largest width to be the text. NOTE: This has not been disproven, but may still not work. Deprecated: User picks which width captures all of the text
  Step 3: Isolate those paths
  Step 4: User can choose to resize the width of those paths
  Step 5: User picks the length threshold. Paths with length above this threshold will be ignored, those with length above will be considered text
  Step 5.5: Save the nontext portions of the svg & convert it to a png
  Step 6: Save the text from the svg and convert to a png
  Step 7: Detect text using cv2 & write it to a txt file
  Step 8: save final png
  Issues: Potentially fixed: Need user input for every floor plan - fixed
          Catches extra text at the bottom: copywrite text. Potential solution: Crop svg to only consider the inside of the large box. - fixed
          Misses the large pieces & differing of text (Huntington Hall) - may not be necessary it still grabs their room number
  """
  os.makedirs(nontext_png_dir, exist_ok=True)
  os.makedirs(text_dir, exist_ok=True)
  os.makedirs(text_png_dir, exist_ok=True)
  if os.path.exists(f"{nontext_png_dir}/{room}_final.png") and not overwrite_drive:
    print(f"{nontext_png_dir}/{room}_final.png already exists and overwrite_drive is set to False, so won't run.")
    return

  output_name = room 
  output_dir = "."

  svg = f"{output_name}.svg"
  svg_path = join(svg_dir, svg)

  paths, attributes, svg_attributes = svg2paths2(svg_path)
  #commented for runtime
  show_svg(svg_path) #Show original 
  
  new_paths = []
  new_attributes = []
  color_attributes = []

  # Step 1:  
  for i, (path, attribute) in enumerate(zip(paths, attributes)):
    if len(path) == 0:
      continue
    if is_door(path, attribute):
      continue
    new_paths.append(path)
    new_attributes.append(attribute)

  complete_paths, complete_attributes = new_paths, new_attributes
  paths, attributes = new_paths,new_attributes
  nontext_paths, nontext_attributes = [], []


  # commented for runtime
  visualize_all_paths(paths, attributes, svg_attributes, output=f"{output_dir}/{output_name}_colored.svg")
  show_svg(f"{output_dir}/{output_name}_colored.svg")
  
  # no need to save the cleaned png
  #cleaned_svg_path = f"{room}_cleaned.svg"
  #cleaned_png_path = f"{png_dir}/{room}_cleaned.png"
  #visualize_all_paths(new_paths, new_attributes, svg_attributes, output=cleaned_svg_path)
  # wsvg(new_paths, new_attributes, svg_attributes, filename=cleaned_svg_path)
  #cairosvg.svg2png(url=cleaned_svg_path, write_to = cleaned_png_path , background_color="white", dpi=400) # choose on dpi
  # return
  

  #Step 5: 
  print("Step 5")
  threshold = init_threshold
  while True:
    #new_paths, new_attributes = [], []     # For coloring the edges that will be shown 
    final_paths, final_attributes = [], [] # Keep the edges we care about (the ones that have the text)
    nontext_paths_temp, nontext_attributes_temp = [], [] #Keeps track of whatever is _not_ text
    for i, (path, attribute) in enumerate(zip(paths, attributes)):
      real_path = path_transform(path, parse_transform(attribute.get('transform', '')))
      new_attribute = attribute.copy()
      if real_path.length() < threshold:
        # color it
        new_attribute = update_attribute(attribute, 'stroke', 'red')
        # Only keep the ones that are below the threshold
        final_paths.append(path)
        final_attributes.append(attribute)
      else:
        nontext_paths_temp.append(path)
        nontext_attributes_temp.append(attribute)


    #commented for runtime
    visualize_all_paths(final_paths, final_attributes, svg_attributes, output=f"{output_dir}/{output_name}_threshold_{threshold}.svg")
    show_svg(f"{output_dir}/{output_name}_threshold_{threshold}.svg")

    #shouldn't be necessary - no more need for user input. Left here for debugging 
    #x = input(f"Using threshold = {threshold} will keep the edges in red. Press enter to accept or input another threshold")
    x=""
    if len(x.strip()) == 0:
      # accepted
      output_name = f"{output_name}_threshold_{threshold}"
      # paths, attributes = final_paths, final_attributes
      # Keep track of the nontext found here 
      nontext_paths.extend(nontext_paths_temp)
      nontext_attributes.extend(nontext_attributes_temp)
      break
    else:
      threshold = float(x)



  # Step 6:
  print("Step 6")
  nontext_svg_temp = f"{nontext_svg_dir}/{room}_nontext.svg"
  nontext_png_temp = f"{nontext_png_dir}/{room}_nontext.png"

  visualize_all_paths(nontext_paths, nontext_attributes, svg_attributes, output=nontext_svg_temp)
  cairosvg.svg2png(url=nontext_svg_temp, write_to = nontext_png_temp, background_color="white", dpi=400) # choose on dpi



  # Step 7:
  print("Step 7")
  final_svg_temp = f"{text_svg_dir}/{room}_text.svg"
  # commented for runtime
  if not paths: # make sure that there is actually text
    return
  visualize_all_paths(paths, attributes, svg_attributes, output=final_svg_temp)
  show_svg(final_svg_temp)


  # Step 8: 
  print("Step 8")
  png_temp = f"{final_svg_temp[:-4]}.png"
  
  print("Converting to png...")
  cairosvg.svg2png(url=final_svg_temp, write_to = png_temp, background_color="white", dpi=400) # choose on dpi
  print("Converted")
  image = cv2.imread(png_temp)
  os.remove(png_temp)

  # image = cv2.imread(f"{drive_dir}/{room}_final.png")

  image[-300:,:,:]=255
  image = image[:int(image.shape[0]*0.9),:,:]
  #commented for runtime
  #cv2_imshow(image)

  k = 5
  itr = 2
  names=[]
  while True:
    try:
      names=getNames(image,k,itr)
    finally: 
      names = []

    #x = input(f"Currently using kernel of size = ({k},{k}) with {itr} dilation iterations. NOTE: k MUST BE ODD. Press enter to accept or enter another: k, itr ")
    x = ""
    if len(x.strip()) == 0: 
      break
    else: 
      x=x.split(",")
      k=int(x[0])
      itr=int(x[1])

  print(len(names))

  if True: # check that the widths wer are considering are actually letters      
    print("Writing to txt file")
    file = open(f"{text_dir}/{room}_text.txt", "w+")
    file.write(str(names))
    file.close()

    #commented for runtime
    #cv2_imshow(image)

    # Step 9:
    print("Step 9")
    cv2.imwrite(f"{text_png_dir}/{room}_text_image.png", image)
    # cv2.imwrite(f"{drive_dir}/{output_name}_2.png", image) #also save the full information - unecessary save
    print(f"Written image to {text_png_dir}/{room}_text.png")


