"""
Only need to run this once, DON'T RUN AGAIN

May not work due to file path changing
"""

import pytesseract
#import svg_helper_methods
from svgpathtools import svg2paths2
import cairosvg
import cv2
import numpy as np
#from pdf2image import convert_from_path, convert_from_bytes
from os import listdir
from os.path import isfile, join

beavernav = os. getcwd() + ''
mypath = beavernav + "/backend_file_storage/svg_original_files"
pngs = "/Users/yajva/Desktop/BeaverNav/PNG Floor Plans"
svgfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
pngs = [f for f in listdir(pngs) if isfile(join(pngs, f))]

"""for floor in svgfiles:
	floor = floor[:-4] # get rid of .svg
	print(floor)
	paths, attributes, svg_attributes = svg2paths2(beavernav + "/SVG Floor Plans/" + floor + ".svg")
	cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/PNG Floor Plans/" + floor + ".png", background_color="white", dpi=400) # choose on dpi


"""

def main():
	cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + '5_1' + ".svg", write_to = beavernav + "/PNG Floor Plans/" + 5_1 + "_1.png", background_color="white", dpi=200) # choose on dpi


if __name__ == "__main__":
		main()

