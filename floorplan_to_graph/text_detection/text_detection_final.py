from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
from pdf2image import convert_from_path
from os import listdir
from os.path import isfile, join
# import pytesseract
import random
# from google.cloud import vision
import os
import json
import warnings
from PIL import Image
import crop_floor_plans
import cairosvg
from svgpathtools import svg2paths2
import sys
beavernav = os. getcwd()
sys.path.append(beavernav)
import svg_helper_methods


# USING AN ALGORITHM INSPIRED BY https://sci-hub.se/10.1109/icdarw.2019.00006 

# SPECIFICATIONS
# This entire file uses boxes that are defined as a tuple of the 4 corner coordinates
# it also uses lists of such boxes

# PARAMS

# FILE INPUT parameters
mypath = beavernav + '/PDF_floor_plans'
mod = beavernav + '/text_detection/modified_png_floor_plans'
nontextpngs = beavernav + "/text_detection/nontext_PNG_floor_plans"
cropped_png_dir = beavernav + "/cropped_png_floor_plans"
txt_png_dir = beavernav + "/text_detection/text_png_floor_plans"
bbox_dir = beavernav + '/text_detection/text_bounding_boxes'
txt_dir = beavernav + '/text_detection/text_files'
png_dir = beavernav + '/png_floor_plans'
svg_dir = beavernav + '/SVG_floor_plans'
mod_svg_dir = beavernav + '/text_detection/modified_svg_floor_plans'
png_no_lines_dir = beavernav+'/text_detection/png_lines_removed'
cropped_png_no_lines_dir = beavernav + '/text_detection/cropped_lines_removed_pngs'
eroded_dir = beavernav + '/text_detection/final_pngs'
final_dir = beavernav + '/text_detection/final_pngs'
pdffiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
modfiles = [f for f in listdir(mod) if isfile(join(mod, f))]
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = beavernav + '/psychic-ruler-357114-6631612ee47a.json'

dpi = 1200

padding_percent_x = 20 # pixels on either side of the bounding box
padding_percent_y = 10 # pixels on either side of the bounding box


# parameters for EAST
# note that height & weight must be multiples of 32
# haven't played with the min_confidence yet
# usually the image is resized, but here we skip it to prevent information loss
# if we do resize, the bounding boxes have to be scaled
# with a dpi of 960, the height and width are same as below
min_confidence = 0.01
merge_fraction = 1/3 # fractional distance that determines if two bounding boxes correspond to the same text

split_dim = (3,3)

threshx = 100
threshy = 90
threshP = 400 # try 200, or 350

thresh_svg = 10


def pre_process_floor_plans(floor):
	"""Image.MAX_IMAGE_PIXELS = None
	image = Image.open(mod + "/" + floor + ".png")
	print("hey")
	cropped_image_obj = image.crop((x_min, y_min, x_max, y_max))
	print("hey")
	cropped_image_obj.save(cropped_png_dir + '/'+floor + '.png')
	cropped_image_obj.close()
	"""
	print("Pre processing")
	# unecessary storagee - remove in final version
	mod_svgs = [f for f in listdir(mod_svg_dir) if isfile(join(mod_svg_dir, f))]
	if floor+'.svg' not in mod_svgs:
		deleteSVGLines(svg_dir+ '/'+floor + '.svg', mod_svg_dir+ '/'+floor + '.svg', thresh_svg)
	pngs = [f for f in listdir(png_dir) if isfile(join(png_dir, f))]
	if floor+'.png' not in pngs: 
		cairosvg.svg2png(url=svg_dir+ '/'+floor + '.svg', write_to = png_dir + "/" + floor + ".png", background_color="white", dpi=dpi) # choose on dpi
	# unecessary storagee - remove in final version
	pngs = [f for f in listdir(png_no_lines_dir) if isfile(join(png_no_lines_dir, f))]
	if floor+'.png' not in pngs: 
		cairosvg.svg2png(url=mod_svg_dir+ '/'+floor + '.svg', write_to = png_no_lines_dir + "/" + floor + ".png", background_color="white", dpi=dpi) # choose on dpi
	# unecessary storagee - remove in final version
	cropped_pngs = [f for f in listdir(cropped_png_dir) if isfile(join(cropped_png_dir, f))]
	if floor+'.png' not in cropped_pngs: 
		dim = crop_floor_plans.crop_image(png_dir + "/" + floor + ".png", cropped_png_dir + '/'+floor + '.png')
	# unecessary storagee - remove in final version
	cropped_pngs = [f for f in listdir(cropped_png_no_lines_dir) if isfile(join(cropped_png_no_lines_dir, f))]
	if floor+'.png' not in cropped_pngs: 
		crop_floor_plans.crop_image_with_dimensions(png_no_lines_dir + "/" + floor + ".png", cropped_png_no_lines_dir + '/'+floor + '.png', dim)
	# unecessary storagee - remove in final version
	pngs = [f for f in listdir(eroded_dir) if isfile(join(eroded_dir, f))]
	if floor+'.png' not in pngs: 
		img	 = cv2.imread(cropped_png_no_lines_dir + '/'+floor + '.png')
		kernel = np.ones((5, 5), np.uint8)
		img = cv2.erode(img, kernel, iterations=1)
		res, img = cv2.threshold(img,200,255,cv2.THRESH_BINARY)
		cv2.imwrite(eroded_dir + '/'+floor + '.png', img)

def svg_to_png_coords(file,coords):
	(x,y) = coords
	conversion_factor = dpi/72
	return (int(conversion_factor * x),int(conversion_factor * y))

def png_to_svg_coords(file,coords):
	(x,y) = coords
	conversion_factor = 72/dpi
	return (conversion_factor * x,conversion_factor * y)
	

def deleteSVGLines(file, destination, threshold):
	paths, attributes, svg_attributes = svg2paths2(file)

	new_paths, new_attributes = [],[]
	for i, (path, attribute) in enumerate(zip(paths, attributes)):
			if len(path) == 0:
				continue
			if svg_helper_methods.is_door(path, attribute):
				continue
			real_path = svg_helper_methods.path_transform(path, svg_helper_methods.parse_transform(attribute.get('transform', '')))
			if real_path.length() < threshold:
					new_paths.append(path)
					new_attributes.append(attribute)

	paths, attributes = new_paths, new_attributes

	svg_helper_methods.visualize_all_paths(paths, attributes, svg_attributes, output=destination)
	#svg_helper_methods.show_svg(destination)


def convertPDFtoPNG(floor, dpi):
	with warnings.catch_warnings(record=True) as w:
		warnings.simplefilter('ignore', Image.DecompressionBombWarning)
		img = convert_from_path(beavernav + '/PDF Floor Plans/' + floor + '.pdf', dpi=dpi)
		img[0].save(beavernav + '/PNG Floor Plans/' + floor + '.png', "PNG")
		image = cv2.imread(beavernav+'/PNG Floor Plans/' + floor + '.png')
		return image

"""
# crop the whitespace on the sides and the irrelavant information on the bottom
# may not work on all floor plans 
# YR's bootleg version
"""
def cropFloorPlan(image):
	(H, W) = image.shape[:2]
	image = image[int(H * 0.038)//32*32:int(H * 0.89)//32*32, int(W * 0.038)//32*32:int(W *  0.96)//32*32]
	return image

def cropFloorPlanFromPath(filepath, destination):
	image = cv2.imread(filepath)
	(H, W) = image.shape[:2]
	image = image[int(H * 0.038)//32*32:int(H * 0.89)//32*32, int(W * 0.038)//32*32:int(W *  0.96)//32*32]
	cv2.imwrite(destination, image)


"""
# splits an image into a grid of images determined by split_dim= (x,y) ex. (3,3)
# useful for processing high resolution images separately
# returns a list of the split images"""
def splitImage(image, split_dim):
	(r,c) = split_dim
	(H,W) = image.shape[:2]
	arr = []
	for i in range(r*c):
		row = i//c
		col = i - r * (i//c)
		arr.append(image[int((H*row/r)//32 * 32):int(H*(row + 1)/r//32*32), int((W*col/c)//32*32):int((W*(col+1)/c)//32*32)])

	return arr

######################################################
######################################################

"""
# runs text detection (NOT RECOGNITION)
#	takes in a processed image and its original
# runs EAST on the image and draws boxes on the original"""
def runEast(image):


	results = []
	(H, W) = image.shape[:2]
	(newW, newH) = (W, H)
	rW = W / float(newW)
	rH = H / float(newH)
	
	# define the two output layer names for the EAST detector model that
	# we are interested -- the first is the output probabilities and the
	# second can be used to derive the bounding box coordinates of text
	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]

	# load the pre-trained EAST text detector
	print("[INFO] loading EAST text detector...")
	net = cv2.dnn.readNet(beavernav + '/text_detection/frozen_east_text_detection.pb')
	# construct a blob from the image and then perform a forward pass of
	# the model to obtain the two output layer sets

	blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
		(123.68, 116.78, 103.94), swapRB=True, crop=False)
	start = time.time()
	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)
	end = time.time()
	# show timing information on text prediction
	print("[INFO] text detection took {:.6f} seconds".format(end - start))

	# grab the number of rows and columns from the scores volume, then
	# initialize our set of bounding box rectangles and corresponding
	# confidence scores
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []
	# loop over the number of rows
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the geometrical
		# data used to derive potential bounding box coordinates that
		# surround text
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability, ignore it
			if scoresData[x] < min_confidence:
				continue
			# compute the offset factor as our resulting feature maps will
			# be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)
			# extract the rotation angle for the prediction and then
			# compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)
			# use the geometry volume to derive the width and height of
			# the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]
			# compute both the starting and ending (x, y)-coordinates for
			# the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)
			# add the bounding box coordinates and probability score to
			# our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	# apply non-maxima suppression to suppress weak, overlapping bounding
	# boxes
	boxes = non_max_suppression(np.array(rects), probs=confidences)

	# remove the text from the image
	image = drawBoxes(image, boxes, (255,255,255), -1)

	results = []
	for box in boxes:
		results.append(box)

	# show the output image
	return image, results

"""
# runs text detection using easy ocr (NOT RECOGNITION)
# was used for testing but is no longer necessary"""
def detectTextWithEasyOCR(image):
	cv2.imwrite(beavernav+'/temp.png', image)
	bounds = r.readtext('temp.png')
	os.remove(beavernav+'/temp.png')
	boxes = []
	for b in bounds:
		coords = b[0]
		startX = min(coords[0][0], coords[2][0])
		endX = max(coords[0][0], coords[2][0])
		startY = min(coords[0][1], coords[2][1])
		endY = max(coords[0][1], coords[2][1])
		boxes.append((startX,startY,endX, endY))
		print((startX,startY,endX, endY))
	# remove the text from the image
	image = drawBoxes(image, boxes, (255,255,255), -1)

	results = []
	for box in boxes:
		results.append(box)

	# show the output image
	return image, results

"""
# This runs EAST, removes text, then google OCR, then easy OCR if desired
# running both on the original and then combining breaks our post processing algorithm
# PARAMS:
# numPasses - how many passes of east to do. potentially using more passes will catch leftover. Experiments show that > 1 pass is no better than 1 pass
# post - whether or not to do postprocessing (this should be set to True unless debugging)
# east - whether or not to use east (this should be set to True unless debugging)
# post - whether or not to do postprocessing (this should be set to True unless debugging)
# google - whether or not to do google API (this should be set to False unless debugging, since the google api is not very good)
# easy - whether or not to do easyOCR (this should be set to False unless debugging, since the google api is not very good)
# save - whether or not to save the bounding boxes. If so, they are saved in a pickle file as a list of boxes, defined by a tuple of 4 coordinates
"""
def saveBoundingBoxes(floor, numPasses, post = True, east = True, google=True, easy = True, save=True):
	print("Running text detection & recognition on floor " + floor)
	start = time.time()

	image = cv2.imread(final_dir+ '/'+floor + '.png')

	res, image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)

	merged_box_orig = image.copy()

	print('Splitting Image')
	quarters = splitImage(image,split_dim)

	boxes = []
	mergedboxes = []
	boxes2 = []
	for i in range(split_dim[0] * split_dim[1]):
		boxes.append([])
		mergedboxes.append([])
		boxes2.append([])

	for id, im in enumerate(quarters):
		if east:
			for i in range(numPasses):
				quarters[id], boxes2[id] = runEast(quarters[id])
				boxes[id].extend(boxes2[id])
		if easy:
			quarters[id], boxes2[id] = detectTextWithEasyOCR(quarters[id])
			boxes[id].extend(boxes2[id])
		if (google):
			cv2.imwrite(mod + "/" + floor + '_0' + str(id) + ".png", quarters[id])
			results = detect_text( mod + "/" + floor + '_0' + str(id) + ".png")
			for text in results:
				boxes[id].append(results[text])
			os.remove(mod + "/" + floor + '_0' + str(id) + ".png")
		mergedboxes[id].extend(boxes[id])
		if post: mergedboxes[id] = postProcessing(mergedboxes[id])

	print("Merging Split Boxes")
	mergedboxes = mergeSplitBoxes(mergedboxes, split_dim, image.shape[0], image.shape[1])
	boxes = mergeSplitBoxes(boxes, split_dim, image.shape[0], image.shape[1])
	boxes = addPadding(boxes,image.shape[:2], (padding_percent_y, padding_percent_x))
	mergedboxes = addPadding(mergedboxes,image.shape[:2], (padding_percent_y, padding_percent_x))

	if post: mergedboxes = postProcessing(mergedboxes)
	mergedboxes = trimLargeRectangles(mergedboxes)
	print("Merged Boxes #: " + str(len(mergedboxes)))
	merged_box_orig = drawBoxes(merged_box_orig, mergedboxes, (255,0,0), 2)

	#image = drawBoxes(image, boxes, (255,255,255), -1)

	print("Saving Images")
	cv2.imwrite(mod + "/" + floor + ".png", merged_box_orig)
	cv2.imwrite(nontextpngs + "/" + floor + ".png", image)

	if save:
		with open(bbox_dir + '/' + floor + 'bbs.json', 'w') as out:
			json.dump(mergedboxes,out)
	
	end = time.time()
	# show timing information on text prediction
	print("[INFO] Saving Bounding Boxes took {:.6f} seconds".format(end - start))


######################################################
# Post Processing methods
######################################################

"""
# color should be tuple of RGB
# thickness of -1 is fill the box
# given a list of boxes, it draws all of them on the image with color and thickness"""
def drawBoxes(image,boxes, color, thickness):
	for (startX, startY, endX, endY) in boxes:
		image = cv2.rectangle(image, (startX, startY), (endX, endY), color, thickness)

	return image

# self explanatory
def calculateIntersectionArea(box1,box2):
	(xmin1, ymin1, xmax1, ymax1) = box1
	(xmin2, ymin2, xmax2, ymax2) = box2
	# determine the coordinates of the intersection rectangle
	x_left = max(xmin1, xmin2)
	y_top = max(ymin1, ymin2)
	x_right = min(xmax1, xmax2)
	y_bottom = min(ymax1, ymax2)

	if x_right <= x_left or y_bottom <= y_top:
		return 0.0

	# The intersection of two axis-aligned bounding boxes is always an
	# axis-aligned bounding box
	intersection_area = (x_right - x_left) * (y_bottom - y_top)

	return intersection_area

# self explanatory
def calculateIoU(box1,box2):
	I = calculateIntersectionArea(box1,box2)
	U = calculateArea(box1) + calculateArea(box2) - I
	if I > U:
		print(str(I)+ " " +  str(U))
		print()
		print('IoU > 1.0')
	return I/U

# self explanatory
def calculateArea(box1):
	(xmin1, ymin1, xmax1, ymax1) = box1
	bb1_area = (xmax1 - xmin1) * (ymax1 - ymin1)
	if bb1_area < 0:
		print('area < 0')
	return bb1_area

# merge two rectangles into their smallest bounding box
def merge(box1,box2):
	(xmin1, ymin1, xmax1, ymax1) = box1
	(xmin2, ymin2, xmax2, ymax2) = box2

	# determine the coordinates of the union rectangle
	x_left = min(xmin1, xmin2)
	y_top = min(ymin1, ymin2)
	x_right = max(xmax1, xmax2)
	y_bottom = max(ymax1, ymax2)

	return (x_left, y_top,x_right, y_bottom)

"""
# Sometimes boxes may have negative coordinates
# we trim these to 0
"""
def fixNegativeCases(boxes):
	for id, box in enumerate(boxes):
		(startX, startY, endX, endY)  = box
		startX = max(0,startX)
		startY = max(0,startY)
		boxes[id] = (startX, startY, endX, endY)
			
	return boxes

"""
# trim rectangles that are too large, or too tall, or too much perimeter
"""
def trimLargeRectangles(boxes):
	ret = []
	for (startX, startY, endX, endY) in boxes:
		if endY - startY > threshy:
			continue
		if endX + endY - startX - startY > threshP:
			continue
		if calculateArea((startX, startY, endX, endY)) <= 0.1:
			continue
		ret.append((startX, startY, endX, endY))

	return ret

"""
# merges rectangle if their intersection is > 0.4 of their union
"""
def mergeIntersectingRectangles(boxes):
	found = True
	while found:
		found = False
		b1,b2 = 0,0
		for id1,box1 in enumerate(boxes):
			for id2,box2 in enumerate(boxes, start = id1+1):
				if str(box1) == str(box2):
					continue
				if calculateIoU(box1,box2) > 0.4:
					merged = merge(box1,box2)
					boxes.append(merged)
					found = True
					b1 = id1
					b2 = id2
					break
			if found:
				boxes = boxes[0:b1] + boxes[b1+1:b2] + boxes[b2+1:]
				break
		
	return boxes

"""
# this method has an issue
# it was being used in post processing but has been removed, because I couldn't figure out the progress
"""
def discardDuplicateRectangles(boxes):
	found = True
	while found:
		found = False
		b1 = 0
		for id1,box1 in enumerate(boxes):
			for id2,box2 in enumerate(boxes, start = id1+1):
				if str(box1) == str(box2):
					continue
				I = calculateIntersectionArea(box1,box2)
				if I/calculateArea(box1) > 0.7:
					#print('found a duplicate')
					found = True
					b1 = id1
					break
				if I/calculateArea(box2) > 0.7:
					#print('found a duplicate')
					found = True
					b1 = id2
					break
			if found:
				boxes = boxes[0:b1] + boxes[b1+1:]
				break
		
	return boxes

""" 
merges rectangles according to the definition in the paper above
 Let h be the height of the taller rectangle (r1), 
ymin the coordinate of the upper edge of r1 and ymax the position 
of the lower edge of r1. r1 and r2 are aligned if r2 is entirely 
contained in the interval [ymin - h/2, ymax + h/2]. We allow an offset
 of h/2 at the top and bottom to deal with ascenders and descenders in 
 r2. If two rectangles are aligned we then check their horizontal 
 distance: r1 and r2 are near if their distance is lower than h/2.
 """
def mergeYAlignedRectangles(boxes):
	found = True
	while found:
		found = False
		b1,b2 = 0,0
		for id1,box1 in enumerate(boxes):
			(xmin1, ymin1, xmax1, ymax1) = box1
			for id2,box2 in enumerate(boxes, start = id1+1):
				if str(box1) == str(box2):
					continue
				(xmin2, ymin2, xmax2, ymax2) = box2
				h1 = ymax1 - ymin1
				h2 = ymax2 - ymin2
				m = False
				h = 0
				if (h1 >= h2):
					h = h1
					m = ymax2 <= ymax1 + h*merge_fraction and ymin2 >= ymin1 - h*merge_fraction
				else:
					h = h2
					m = ymax1 <= ymax2 + h*merge_fraction and ymin1 >= ymin2 - h*merge_fraction
				if m:
					if xmin1 <= xmin2:
						m = (xmin2 - xmax1) <= h/3
					else:
						m = (xmin1 - xmax2) <= h/3	
				if m:
					merged = merge((xmin1, ymin1, xmax1, ymax1),(xmin2, ymin2, xmax2, ymax2))
					boxes.append(merged)
					found = True
					b1 = id1
					b2 = id2
					break
			if found:
				boxes = boxes[0:b1] + boxes[b1+1:b2] + boxes[b2+1:]
				break
		
	return boxes

"""
# does the same as the above, but in the X direction
# was used during trials, but should not be necessary for final execution
"""
def mergeXAlignedRectangles(boxes):
	found = True
	while found:
		found = False
		b1,b2 = 0,0
		for id1,box1 in enumerate(boxes):
			(xmin1, ymin1, xmax1, ymax1) = box1
			for id2,box2 in enumerate(boxes, start = id1+1):
				if str(box1) == str(box2):
					continue
				(xmin2, ymin2, xmax2, ymax2) = box2
				h1 = xmax1 - xmin1
				h2 = xmax2 - xmin2
				m = False
				h = 0
				if (h1 >= h2):
					h = h1
					m = xmax2 <= xmax1 + h/2 and xmin2 >= xmin1 - h/2
				else:
					h = h2
					m = xmax1 <= xmax2 + h/2 and xmin1 >= xmin2 - h/2	
				if m:
					if ymin1 <= ymin2:
						m = (ymin2 - ymax1) <= h/3
					else:
						m = (ymin1 - ymax2) <= h/3	
				if m:
					merged = merge((xmin1, ymin1, xmax1, ymax1),(xmin2, ymin2, xmax2, ymax2))
					boxes.append(merged)
					found = True
					b1 = id1
					b2 = id2
					break
			if found:
				boxes = boxes[0:b1] + boxes[b1+1:b2] + boxes[b2+1:]
				break
		
	return boxes

"""
# takes in a list of list boxes corersponding to boxes for the split images
# combines them into one list for the big image
"""
def mergeSplitBoxes(boxes_split, split_dim, orig_h, orig_w):
	(r,c) = split_dim
	(H,W) = (orig_h, orig_w)
	new_boxes = []
	for i in range(r*c):
		row = i//c 
		col = i - r * (i//c)
		for box in boxes_split[i]:
			(xmin,ymin,xmax,ymax) = box
			x1 = xmin + int((W*col/c)//32 * 32)
			x2 = xmax + int((W*col/c)//32 * 32)
			y1 = ymin + int((H*row/r)//32 * 32)
			y2 = ymax + int((H*row/r)//32 * 32)
			if (x1,y1,x2,y2) not in new_boxes:
				new_boxes.append((x1,y1,x2,y2))
	return new_boxes

"""
# performs post processing on the boxes
# its finalized, look into the method for clarification
"""
def postProcessing(boxes):
	start = time.time()
	print("PostProcessing")
	#print('length of boxes0: ' + str(len(boxes)))
	boxes = fixNegativeCases(boxes)
	#print('length of boxes1: ' + str(len(boxes)))
	boxes = trimLargeRectangles(boxes)
	#print('length of boxes2: ' + str(len(boxes)))
	boxes = mergeIntersectingRectangles(boxes)
	#print('length of boxes3: ' + str(len(boxes)))
	#print(*boxes, sep = "\n")
	#boxes = discardDuplicateRectangles(boxes)
	#print('length of boxes4: ' + str(len(boxes)))
	#print(*boxes, sep = "\n")
	boxes = mergeYAlignedRectangles(boxes)
	#print('length of boxes5: ' + str(len(boxes)))
	#print(*boxes, sep = "\n")
	#boxes = mergeXAlignedRectangles(boxes)
	end = time.time()
	print("[INFO] Post Processing took {:.6f} seconds".format(end - start))

	return boxes

"""
# adds a padding to all the boxes to account for errors in text detection
# takes in a dim (H,W) and padding_percent = (padding for height, width)
"""
def addPadding(boxes, dim, padding_percent):
	padding_h = padding_percent[0]
	padding_w = padding_percent[1]
	(H,W) = dim
	for id, (startX, startY, endX, endY)in enumerate(boxes):
		width = endX - startX
		height = endY - startY
		boxes[id] = (max(0,int(startX - padding_w/100 * width)), max(int(startY - padding_h/100 * height),0),min(int(endX + padding_w/100 * width), W),min(int(endY+padding_h/100 * height),H))
	return boxes


def remove_text(floor):
	#todo - remove text from the original svg file and save it to nontext pngs
	print("removing text")
	text_no_lines_img = cv2.imread(cropped_png_no_lines_dir + "/" + floor + ".png")
	with open(bbox_dir + '/' + floor + 'bbs.json', 'r') as handle:
		boxes = json.load(handle)
	(H,W) = text_no_lines_img.shape[:2]
	mask=np.full((H,W,3),255,dtype=np.uint8)
	for (start_x, start_y,end_x, end_y) in boxes:
		mask[start_y:end_y, start_x:end_x] = text_no_lines_img[start_y:end_y, start_x:end_x]
	ret, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
	orig = cv2.imread(cropped_png_dir + '/' + floor + '.png')
	ret, orig = cv2.threshold(orig, 200, 255, cv2.THRESH_BINARY)
	orig = cv2.bitwise_not(cv2.subtract(cv2.bitwise_not(orig), cv2.bitwise_not(mask)))
	#cv2.imwrite(nontextpngs + "/" + floor + "_mask.png",mask )
	cv2.imwrite(nontextpngs + "/" + floor + ".png",orig )
	return
