from audioop import avg
from unittest import result
from cv2 import threshold
from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
#from pdf2image import convert_from_path, convert_from_bytes
from os import listdir
from os.path import isfile, join
import pytesseract
import random
# from google.cloud import vision
import io
import pickle 
import os
import json
import warnings
from PIL import Image
import subprocess
from text_detection import crop_floor_plans
import easyocr
import cairosvg
from svgpathtools import svg2paths2
import sys
beavernav = os. getcwd() + ''
sys.path.append(beavernav)
from text_detection import svg_helper_methods
import keras_ocr

# USING AN ALGORITHM INSPIRED BY https://sci-hub.se/10.1109/icdarw.2019.00006 

# SPECIFICATIONS
# This entire file uses boxes that are defined as a tuple of the 4 corner coordinates
# it also uses lists of such boxes

# PARAMS

# FILE INPUT parameters - used for testing
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
temp_dir = beavernav + '/text_detection/temp_files'
pdffiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
modfiles = [f for f in listdir(mod) if isfile(join(mod, f))]
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = beavernav + '/psychic-ruler-357114-6631612ee47a.json'

# scale size for text detection
scale_percent = 600 # percent of original size
scale_height = 30 
padding_percent_x = 20 # pixels on either side of the bounding box
padding_percent_y = 10 # pixels on either side of the bounding box
min_length = 0
max_length = 50

dpi = 1200

# parameters for EAST
# note that height & weight must be multiples of 32
# haven't played with the min_confidence yet
# usually the image is resized, but here we skip it to prevent information loss
# if we do resize, the bounding boxes have to be scaled
# with a dpi of 960, the height and width are same as below
min_confidence = 0.01
merge_fraction = 1/6 # fractional distance that determines if two bounding boxes correspond to the same text

split_dim = (5,5)

threshx = 100
threshy = 80
threshP = 400 # try 200, or 350

thresh_svg = 20


# r = easyocr.Reader(['en'])
# pipeline = keras_ocr.pipeline.Pipeline()


def main():
	buildings = [1, 2, 3, 4, 5, 6, '6C', 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 24, 26, 31, 32, 33, 34, 35, 36, 37, 38, 39, 56, 57, 66, 68]
	b2 = []
	for b in buildings:
		b2.append(str(b))
	relevant = []
	for floor in pdffiles:
		floor = floor[:-4]
		b = floor[:floor.index('_')]
		if b in b2:
			relevant.append(floor)

	floors = relevant
	#floors = random.sample(relevant, 10)
	floors = ['7_1', '1_1', '5_1', '10_1', '32_1']
	floors = ['7_1']
	floors = ['32_1']
	#floors = ['1_1']
	for floor in floors:
		pre_process_floor_plans(floor)
		saveBoundingBoxes(eroded_dir + '/'+floor + '.png', mod+ '/'+floor + '.png', bbox_dir+ '/'+floor + '.json', 1, True, True, True)
		#remove_text(cropped_png_dir + '/'+floor + '.png', cropped_png_no_lines_dir + '/'+floor + '.png', bbox_dir + '/'+floor + '.json', nontextpngs + '/'+floor + '.png')
		#getText(cropped_png_dir + '/'+floor + '.png', cropped_png_no_lines_dir + '/'+floor + '.png', bbox_dir + '/'+floor + '.json', txt_png_dir + '/'+floor + '.png', txt_dir + '/'+floor + '.json')

	print(floors)


######################################################
# Pre Processing methods
######################################################

def pre_process_floor_plans(floor):
	print("Pre processing")
	# unecessary storagee - remove in final version
	mod_svgs = [f for f in listdir(mod_svg_dir) if isfile(join(mod_svg_dir, f))]
	#if floor+'.svg' not in mod_svgs:
	#	deleteSVGLines(svg_dir+ '/'+floor + '.svg', mod_svg_dir+ '/'+floor + '.svg', thresh_svg)
	pngs = [f for f in listdir(png_dir) if isfile(join(png_dir, f))]
	if floor+'.png' not in pngs: 
		cairosvg.svg2png(url=svg_dir+ '/'+floor + '.svg', write_to = png_dir + "/" + floor + ".png", background_color="white", dpi=dpi) # choose on dpi
	# unecessary storagee - remove in final version
	pngs = [f for f in listdir(png_no_lines_dir) if isfile(join(png_no_lines_dir, f))]
	if floor+'.png' not in pngs: 
		cairosvg.svg2png(url=mod_svg_dir+ '/'+floor + '.svg', write_to = png_no_lines_dir + "/" + floor + ".png", background_color="white", dpi=dpi) # choose on dpi
	# unecessary storagee - remove in final version
	cropped_pngs = [f for f in listdir(cropped_png_dir) if isfile(join(cropped_png_dir, f))]
	cropped_pngs_2 = [f for f in listdir(cropped_png_no_lines_dir) if isfile(join(cropped_png_no_lines_dir, f))]
	if floor+'.png' not in cropped_pngs or floor+'.png' not in cropped_pngs_2: 
		dim = crop_floor_plans.crop_image(png_dir + "/" + floor + ".png", cropped_png_dir + '/'+floor + '.png')
		crop_floor_plans.crop_image_with_dimensions(png_no_lines_dir + "/" + floor + ".png", cropped_png_no_lines_dir + '/'+floor + '.png', dim)
	# unecessary storagee - remove in final version
	pngs = [f for f in listdir(eroded_dir) if isfile(join(eroded_dir, f))]
	if floor+'.png' not in pngs: 
		img	 = cv2.imread(cropped_png_no_lines_dir + '/'+floor + '.png')
		kernel = np.ones((5, 5), np.uint8)
		img = cv2.erode(img, kernel, iterations=1)
		res, img = cv2.threshold(img,200,255,cv2.THRESH_BINARY)
		cv2.imwrite(eroded_dir + '/'+floor + '.png', img)

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
	print("[[TXT DETECTION INFO]] loading EAST text detector...")
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
	print("[[TXT DETECTION INFO]] text detection took {:.6f} seconds".format(end - start))

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
	#image = drawBoxes(image, boxes, (255,255,255), -1)

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
# runs text detection using keras ocr (NOT RECOGNITION)
"""
def detectTextWithKerasOCR(image):
	print('[TXT DETECTION INFO] Running KERAS OCR')
	images = [image]
	prediction_groups = pipeline.recognize(images)
	boxes = prediction_groups[0]
	results = []
	for (text,box) in boxes:
		startX = min(box[0][0], box[2][0])
		endX = max(box[0][0], box[2][0])
		startY = min(box[0][1], box[2][1])
		endY = max(box[0][1], box[2][1])
		results.append((startX,startY,endX, endY))

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
def saveBoundingBoxes(image_filename, mod_image_destination, bbx_destination, numPasses = 1, post = False, east = True, keras = False, google=False, easy = False, save=True, debug = False):
	floor = image_filename.split('/')[-1]
	print("[TXT DETECTION INFO] Running text detection on " + floor)
	start = time.time()

	#image = cv2.imread(final_dir+ '/'+floor + '.png')
	image = cv2.imread(image_filename)

	res, image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)

	merged_box_orig = image.copy()

	"""kernel = np.ones((5, 5), np.uint8)
	image = cv2.erode(image, kernel, iterations=1)"""

	if debug: print('Splitting Image')
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
		if (keras):
			quarters[id], boxes2[id] = detectTextWithKerasOCR(quarters[id])
			boxes[id].extend(boxes2[id])
		mergedboxes[id].extend(boxes[id])
		if post: mergedboxes[id] = postProcessing(mergedboxes[id])

	if debug: print("Merging Split Boxes")
	mergedboxes = mergeSplitBoxes(mergedboxes, split_dim, image.shape[0], image.shape[1])
	boxes = mergeSplitBoxes(boxes, split_dim, image.shape[0], image.shape[1])
	#boxes = addPadding(boxes,image.shape[:2], (padding_percent_y, padding_percent_x))
	#mergedboxes = addPadding(mergedboxes,image.shape[:2], (padding_percent_y, padding_percent_x))

	if post: mergedboxes = postProcessing(mergedboxes)
	mergedboxes = trimLargeRectangles(mergedboxes)
	if debug: print("Merged Boxes #: " + str(len(mergedboxes)))
	merged_box_orig = drawBoxes(merged_box_orig, mergedboxes, (255,0,0), 2)

	#image = drawBoxes(image, boxes, (255,255,255), -1)

	if debug: print("Saving Images")
	cv2.imwrite(mod_image_destination, merged_box_orig)
	#cv2.imwrite(nontextpngs + "/" + floor + ".png", image)

	if save:
		with open(bbx_destination, 'w') as out:
			json.dump(mergedboxes,out, indent=5)
	
	end = time.time()
	# show timing information on text prediction
	print("[TXT DETECTION INFO] Saving Bounding Boxes took {:.6f} seconds".format(end - start))


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
		"""if endX + endY - startX - startY > threshP:
			continue"""
		"""if calculateArea((startX, startY, endX, endY)) <= 0.1:
			continue"""
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
			for id2,box2 in enumerate(boxes[id1+1:], start = id1+1):
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
			for id2,box2 in enumerate(boxes[id1+1:], start = id1+1):
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
			for id2,box2 in enumerate(boxes[id1+1:], start = id1+1):
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
						m = (xmin2 - xmax1) <= h*merge_fraction
					else:
						m = (xmin1 - xmax2) <= h*merge_fraction	
				if m:
					merged = merge((xmin1, ymin1, xmax1, ymax1),(xmin2, ymin2, xmax2, ymax2))
					boxes.append(merged)
					found = True
					b1 = id1
					b2 = id2
					break
			if found:
				break
		if found:
			boxes = boxes[:b1] + boxes[b1+1:b2] + boxes[b2+1:]
		
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
			for id2,box2 in enumerate(boxes[id1+1:], start = id1+1):
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

def change_to_int(boxes):
	for i, box in enumerate(boxes):
		(xmin1, ymin1, xmax1, ymax1) = box
		xmin1 = int(xmin1)
		ymin1 = int(ymin1)
		xmax1 = int(xmax1)
		ymax1 = int(ymax1)
		boxes[i] = (xmin1, ymin1, xmax1, ymax1)
	return boxes


"""
# performs post processing on the boxes
# its finalized, look into the method for clarification
"""
def postProcessing(boxes, debug = False):
	start = time.time()
	if debug: print("PostProcessing")
	#print('length of boxes0: ' + str(len(boxes)))
	boxes = fixNegativeCases(boxes)
	boxes = change_to_int(boxes)
	# print('length of boxes1: ' + str(len(boxes)))
	# boxes = trimLargeRectangles(boxes)
	#print('length of boxes2: ' + str(len(boxes)))
	# boxes = mergeIntersectingRectangles(boxes)
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
	if debug: print("[TXT DETECTION INFO][INFO] Post Processing took {:.6f} seconds".format(end - start))

	return boxes

"""
# adds a padding to all the boxes to account for errors in text detection
# takes in a dim (H,W) and padding_percent = (padding for height, width)
"""
def addPadding(boxes, dim, padding_percent):
	padding_h = padding_percent[0]
	padding_w = padding_percent[1]
	(H,W) = dim
	new_boxes = []
	for id, (startX, startY, endX, endY)in enumerate(boxes):
		width = endX - startX
		height = endY - startY
		new_boxes.append((max(0,int(startX - padding_w/100 * width)), max(int(startY - padding_h/100 * height),0),min(int(endX + padding_w/100 * width), W),min(int(endY+padding_h/100 * height),H)))
	return new_boxes

def refine_text_detection(floor):
	 # we know where EAST found ~ 90% of the text

	 # we want to go through the boxes and for each box, find the SVG paths that are contained entirely inside the box

	 # we want to go through all such paths and find the most popular stroke-wdith 
	return




def remove_text(text_img_filename, text_no_lines_img_filename, bbx_filename, no_txt_destination):
	#todo - remove text from the original svg file and save it to nontext pngs
	print("[TXT DETECTION INFO] Removing Text from " +text_img_filename.split('/')[-1])
	text_no_lines_img = cv2.imread(text_no_lines_img_filename)
	with open(bbx_filename, 'r') as handle:
		boxes = json.load(handle)
	(H,W) = text_no_lines_img.shape[:2]
	mask=np.full((H,W,3),255,dtype=np.uint8)
	for (start_x, start_y,end_x, end_y) in boxes:
		if calculateArea((start_x, start_y,end_x, end_y)) <=0:
			continue
		kernel = np.ones((5, 5), np.uint8)
		mask[start_y:end_y, start_x:end_x] = cv2.erode(text_no_lines_img[start_y:end_y, start_x:end_x], kernel, iterations=2)
	ret, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
	orig = cv2.imread(text_img_filename)
	ret, orig = cv2.threshold(orig, 200, 255, cv2.THRESH_BINARY)
	orig = cv2.subtract(cv2.bitwise_not(orig), cv2.bitwise_not(mask))
	orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
	countours,hierarchy=cv2.findContours(orig,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	orig = cv2.bitwise_not(orig)
	# orig = cv2.cvtColor(orig,cv2.COLOR_GRAY2RGB)
	# for cnt in countours:
	# 	area = cv2.contourArea(cnt)
	# 	p = cv2.arcLength(cnt, True)
	# 	((x,y), (width, height), rotation)  = cv2.minAreaRect(cnt)
	# 	if area < 10000 and 2< width < 20 and 2<height < 20:
	# 		orig = cv2.drawContours(orig,[cnt],0,(0,255,255),2)
	#cv2.imwrite(nontextpngs + "/" + floor + "_mask.png",mask )
	cv2.imwrite(no_txt_destination,orig )
	return




######################################################
######################################################

######################################################
# Text Recognition methods
######################################################

def scaleImage(image, scale_percent):
	width = int(image.shape[1] * scale_percent / 100)
	height = int(image.shape[0] * scale_percent / 100)
	dim = (width, height)

	resized = cv2.resize(image, dim, None, interpolation=cv2.INTER_CUBIC)
	res, resized = cv2.threshold(resized,200,255,cv2.THRESH_BINARY)

	return resized

# adds a white border to an image
def addBorder(image, thickness):
	height = image.shape[0]
	width = image.shape[1]
	newimg=np.full((height+thickness*2,width+thickness*2,3),255,dtype=np.uint8)
	newimg[thickness:height+thickness,thickness:width+thickness,:]=image
	return newimg

def smoothen_image(img):
	img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	kernel = np.ones((5, 5), np.uint8)
	img = cv2.erode(img, kernel, iterations=1)
	img = cv2.GaussianBlur(img, (5,5), 0)
	img = cv2.medianBlur(img,5)
	ret,img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	return img

# takes in an original image (WITHOUT BOXES) 
# and returns the text in each of the boxes
def recognizeTextWithGoogle(img):
	cv2.imwrite(mod + "/temp.png", img)
	texts = detect_text( mod + "//temp.png")
	os.remove(mod + "/temp.png")
	text = ''
	for t in texts:
		text = text + t + " "
	text = text[:-1]
	return text

def recognizeTextWithPyTesseract(img):
	config = '-l eng --oem 1 --psm 7'
	text = pytesseract.image_to_string(img, config=config)
	text = text.replace("\n","")
	return text

def recognizeTextWithTesseract(img):
	cv2.imwrite(beavernav+'/temp.png', img)
	subprocess.call(["tesseract", beavernav+'/temp.png', 'out','-l', 'eng', '--oem','1', "--psm", "7"]) 
	with open(beavernav + '/out.txt') as f:
		text = f.read()
	os.remove(beavernav+'/temp.png')
	os.remove(beavernav+'/out.txt')
	return text

def recognizeTextWithEasyOCR(img):
	cv2.imwrite(beavernav+'/temp.png', img)
	bounds = r.readtext(beavernav+'/temp.png')
	text = ''
	if(len(bounds)>0): text = bounds[0][1]
	os.remove(beavernav+'/temp.png')
	return text

def recognizeTextWithKerasOCR(img):
	"""cv2.imshow('test',img)
	cv2.waitKey()"""
	prediction_groups = pipeline.recognize([img])
	boxes = prediction_groups[0]
	text = ''
	if len(boxes) > 0:
		(text,box) = boxes[0]
	return text.upper()

def recognizeText(orig, boxes, google = False, pytess = False, tess = False, easy = True, keras = False, scale = True, smoothen = True):
	results = []
	(H,W) = orig.shape[:2]
	im = orig.copy()
	c = 10000
	for (startX, startY, endX, endY) in boxes:
		height = endY - startY
		width = endX - startX
		# ROI to be recognized
		roi = orig[startY:endY,startX:endX]

		roi = addBorder(roi, 50)

		# scale image for better text detection
		if scale: roi = scaleImage(roi, scale_percent)

		if smoothen: roi =  smoothen_image(roi)

		text = ''

		if google: text = recognizeTextWithGoogle(roi)
		if pytess: text = recognizeTextWithPyTesseract(roi)
		if tess: text = recognizeTextWithTesseract(roi)
		if easy: text = recognizeTextWithEasyOCR(roi)
		if keras: text = recognizeTextWithKerasOCR(roi)
		
		
		# text detection
		#text = text.replace("\n","")
		#text = ''.join([c if ord(c) < 128 else "" for c in text]).strip()# not tested



		# collect results
		#if (any(c.isalpha() for c in text) or any(c.isdigit() for c in text)):
		results.append((text, (startX, startY, endX, endY)))
	return im,results

def detect_text(path, suppressPrints = True):
		"""Detects text in the file."""
		print("Feeding into Google")
		client = vision.ImageAnnotatorClient()

		with io.open(path, 'rb') as image_file:
				content = image_file.read()

		image = vision.Image(content=content)

		response = client.text_detection(image=image)
		texts = response.text_annotations
		if not suppressPrints: print('Texts:')

		results = {}

		for text in texts:
			if True:#(any(c.isalpha() for c in text.description) or any(c.isdigit() for c in text.description)):
				if not suppressPrints: print('\n"{}"'.format(text.description))

				vertices = (['({},{})'.format(vertex.x, vertex.y)
										for vertex in text.bounding_poly.vertices])

				if not suppressPrints: print('bounds: {}'.format(','.join(vertices)))
				t= ''.join([c if ord(c) < 128 else "" for c in text.description]).strip()
				results[t] = [(int(vertex.x), int(vertex.y)) for vertex in text.bounding_poly.vertices]
		
		for text in results:
			startX = min(results[text][0][0], results[text][2][0])
			endX = max(results[text][0][0], results[text][2][0])
			startY = min(results[text][0][1], results[text][2][1])
			endY = max(results[text][0][1], results[text][2][1])
			results[text] = (startX,startY,endX, endY)

		if response.error.message:
				raise Exception(
						'{}\nFor more info on error messages, check: '
						'https://cloud.google.com/apis/design/errors'.format(
								response.error.message))

		return results

def printTextResults(results):
	for (text, (startX, startY, endX, endY)) in results:
			print(f'{text}\n')
			print('bounds: {}'.format(','.join(str((startX, startY, endX, endY)))))


def saveTextResults(results, txt_destination):
	dict = []
	for (text, (startX, startY, endX, endY)) in results:
		center = (int((startX + endX)//2), int((startY + endY)/2))
		dict.append((text,str(center)))
	with open(txt_destination, 'w') as out:
		json.dump(dict,out, indent=5)

def drawText(im,texts, y_offset, color):
	for (text, (start_x, start_y, end_x, end_y)) in texts:
		cv2.rectangle(im, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
		cv2.putText(im, text, (int((start_x + end_x)/2), int((start_y + end_y)/2) - y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
	return im
		
def drawTextNodes(non_text_im_filename, destination_filename, txt_filename, scale_factor = 1, color = (255,255,255)):
	with open(txt_filename, 'r') as handle:
		nodes = json.load(handle)
	img = cv2.imread(non_text_im_filename)
	for [txt, coords] in nodes:
		coords = coords.replace('(','').replace(')','').replace(' ','').split(',')
		coords[0] = int(int(coords[0])//scale_factor)
		coords[1] = int(int(coords[1])//scale_factor)
		img = cv2.circle(img, coords, int(max(15//scale_factor,1)), color, -1)
		if scale_factor< 3:
			cv2.putText(img, txt, (coords[0], coords[1] - int(max(20//scale_factor,1))),
                    cv2.FONT_HERSHEY_SIMPLEX, 2/scale_factor, color, int(max(3//scale_factor,1)))
	cv2.imwrite(destination_filename, img)


def processText(results, floor_num):
	rooms, elevators, stairs, bathrooms, others = [],[],[],[],[]
	for (text, (startX, startY, endX, endY)) in results:
		if min_length < len(text) < max_length:
			if text in [ 'STAI', 'TAIR', 'UP', 'DN', 'ON', 'STAR', 'STNR'] or any( c in text for c in ['STAIR', 'UP', 'DN']) or text[-2:].lower() in ['sb', 'sa']:
				stairs.append(("STAIR", (startX, startY, endX, endY)))
			elif text in [ 'EYE', 'FLFV', 'ELE', 'LEV', 'EVEV', 'ELEY'] or any( c in text for c in ['ELEV']) or text[-2:].lower() in ['e1', 'e2', 'e3', 'e4']:
				elevators.append(('ELEV', (startX, startY, endX, endY)))
			elif text in ['LAV'] or any( c in text for c in ['LAV']):
				bathrooms.append(('LAV', (startX, startY, endX, endY)))
			elif (6 >= len(text) >= 2 and any(c.isdigit() for c in text)):
				t = text
				if len("".join([c for c in text if c.isdigit()])) <= 2:
					if text[0] != floor_num:
						t = floor_num+text
				rooms.append((text, (startX, startY, endX, endY)))
			else: others.append((text, (startX, startY, endX, endY)))
	return rooms, elevators, stairs, bathrooms, others


def getText(lines_img_filename, no_lines_cropped_img_filename, bbox_filename, txt_img_destination,txt_destination, google = False, pytess = False, tess = False, easy = False, keras = True, scale = False, smoothen = False):
	start = time.time()
	floor = lines_img_filename.split("/")[-1][:-4]
	floor_num = floor.split('_')[-1][-1]
	print(floor_num)
	print("[TXT DETECTION INFO] Running text recognition on " + floor)

	im = cv2.imread(no_lines_cropped_img_filename)
	orig = cv2.imread(lines_img_filename)

	with open(bbox_filename, 'r') as handle:
		boxes = json.load(handle)

	im, results = recognizeText(im, boxes, google, pytess, tess, easy, keras, scale, smoothen)

	rooms, elevators, stairs, bathrooms, others = processText(results, floor_num)

	#im = drawText(im, results, 60)
	orig = drawText(orig, rooms, 60, (0,0, 255)) # red
	orig = drawText(orig, elevators, 60, (0,255, 0)) # green
	orig = drawText(orig, stairs, 60, (255,0, 0)) # blue
	orig = drawText(orig, bathrooms, 60, (255,0, 125)) # purple
	#orig = drawText(orig, others, 60, (0,127, 127)) # brown

	cv2.imwrite(txt_img_destination, orig)

	saveTextResults(rooms+elevators+stairs+bathrooms,txt_destination)

	end = time.time()
	print("[TXT DETECTION INFO] Recognizing Text took {:.6f} seconds".format(end - start))

# need to process text
# note that tesseract generally only works well on the room numbers
# enforce 3 digit numbers
# enforce the floor number to be the first number in each room
	
def trim_text_file(txt_filename, txt_destination):
	with open(txt_filename, 'r') as handle:
		nodes = json.load(handle)
	ret_dict = []
	for [txt, coords] in nodes:
		if txt not in ['STAIR', 'ELEV', 'LAV']:
			ret_dict.append((txt,coords))
	# print(ret_dict)
	with open(txt_destination, 'w') as out:
		json.dump(ret_dict,out, indent=5)



if __name__ == "__main__":
		main()






