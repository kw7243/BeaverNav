import numpy as np
import time
import cv2
# import pytesseract
import random
# from google.cloud import vision
from os import listdir
from os.path import isfile, join
import io
import os
import json
import subprocess
import easyocr
import sys
import text_detection_final
beavernav = os. getcwd()
sys.path.append(beavernav)

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

r = easyocr.Reader(['en'])

min_length = 0
max_length = 50

scale_percent = 100


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

# takes in an original image (WITHOUT BOXES) 
# and returns the text in each of the boxes
def recognizeTextWithGoogle(orig, boxes, scale = True):
	print("Using Google Text Detection")
	results = {}
	(H,W) = orig.shape[:2]
	im = orig.copy()
	im = text_detection_final.drawBoxes(im,boxes,(255,0,0),2)
	for (startX, startY, endX, endY) in boxes:
		# ROI to be recognized
		roi = orig[startY:endY,startX:endX]

		# scale image for better text detection
		if scale: roi = scaleImage(roi, scale_percent)

		roi = addBorder(roi, 50)

		# text detection with google
		cv2.imwrite(mod + "/temp.png", roi)
		texts = detect_text( mod + "//temp.png")
		os.remove(mod + "/temp.png")
		text = ''
		for t in texts:
			text = text + t + " "
		text = text[:-1]

		# collect results
		if (any(c.isalpha() for c in text) or any(c.isdigit() for c in text)):
			if min_length < len(text) < max_length:
				results[text] = (startX, startY, endX, endY)
	return im, results

def recognizeTextWithPyTesseract(orig, boxes, scale = True):
	results = {}
	(H,W) = orig.shape[:2]
	im = orig.copy()
	for (startX, startY, endX, endY) in boxes:
		# ROI to be recognized
		roi = orig[startY:endY,startX:endX]

		kernel = np.ones((3, 3), np.uint8)
		roi = cv2.erode(roi, kernel, iterations=2)

		# scale image for better text detection
		if scale: roi = scaleImage(roi, scale_percent)

		roi = addBorder(roi, 50)

		res, roi = cv2.threshold(roi,200,255,cv2.THRESH_BINARY)

		# text detection
		config = '-l eng --oem 1 --psm 7'
		text = pytesseract.image_to_string(roi, config=config)
		text = text.replace("\n","")


		# collect results
		if (any(c.isalpha() for c in text) or any(c.isdigit() for c in text)):
			if min_length < len(text) < max_length:
				results[text] = (startX, startY, endX, endY)
	return im,results

def recognizeTextWithTesseract(orig, boxes, scale = True):
	results = {}
	(H,W) = orig.shape[:2]
	im = orig.copy()
	c = 10000
	for (startX, startY, endX, endY) in boxes:
		height = endY - startY
		width = endX - startX
		# ROI to be recognized
		roi = orig[startY:endY,startX:endX]

		kernel = np.ones((3, 3), np.uint8)
		roi = cv2.erode(roi, kernel, iterations=2)

		# scale image for better text detection
		if scale: roi = scaleImage(roi, scale_percent)

		roi = addBorder(roi, 50)

		res, roi = cv2.threshold(roi,200,255,cv2.THRESH_BINARY)
		cv2.imwrite(beavernav+'/temp.png', roi)
		subprocess.call(["tesseract", beavernav+'/temp.png', 'out','-l', 'eng', '--oem','1', "--psm", "7"]) 
		with open(beavernav + '/out.txt') as f:
			text = f.read()
		os.remove(beavernav+'/temp.png')
		os.remove(beavernav+'/out.txt')
		
		# text detection
		"""text = tesserocr.image_to_text(Image.fromarray(newroi))"""
		text = text.replace("\n","")
		text = ''.join([c if ord(c) < 128 else "" for c in text]).strip()# not tested



		# collect results
		if (any(c.isalpha() for c in text) or any(c.isdigit() for c in text)):
			if min_length < len(text) < max_length:
				results[text] = (startX, startY, endX, endY)
		"""else:
			results[str(c)] = (startX, startY, endX, endY)
			c = c+1"""
	return im,results

def recognizeTextWithEasyOCR(orig, boxes, scale = True):
	results = {}
	(H,W) = orig.shape[:2]
	im = orig.copy()
	c = 10000
	for (startX, startY, endX, endY) in boxes:
		height = endY - startY
		width = endX - startX
		# ROI to be recognized
		roi = orig[startY:endY,startX:endX]

		kernel = np.ones((3, 3), np.uint8)
		roi = cv2.erode(roi, kernel, iterations=1)

		# scale image for better text detection
		if scale: roi = scaleImage(roi, scale_percent)

		roi = addBorder(roi, 50)

		res, roi = cv2.threshold(roi,200,255,cv2.THRESH_BINARY)

		cv2.imwrite(beavernav+'/temp.png', roi)
		bounds = r.readtext('temp.png')
		if(len(bounds)>0): text = bounds[0][1]
		else: text = ''
		os.remove(beavernav+'/temp.png')
		
		# text detection
		#text = text.replace("\n","")
		text = ''.join([c if ord(c) < 128 else "" for c in text]).strip()# not tested



		# collect results
		if (any(c.isalpha() for c in text) or any(c.isdigit() for c in text)):
			results[text] = (startX, startY, endX, endY)
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
	for text in results:
			print(f'{text}\n')
			print('bounds: {}'.format(','.join(str(results[text]))))


def saveTextResults(results, floor):
	dict = {}
	for r in results:
		startX = results[r][0]
		endX = results[r][2]
		startY = results[r][1]
		endY = results[r][3]
		center = (int((startX + endX)//2), int((startY + endY)/2))
		dict[r] = str(center)
	with open(txt_dir + '/'+ floor + ".json", 'w') as out:
		json.dump(dict,out)

def drawText(im,texts, y_offset):
	for text in texts:
		(start_x, start_y,end_x, end_y) = texts[text]
		cv2.rectangle(im, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
		cv2.putText(im, text, (int((start_x + end_x)/2), int((start_y + end_y)/2) - y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
	return im
		
def processText(results):
	rooms = {}
	elevators, stairs = {},{}
	for text in results:
		if min_length < len(text) < max_length:
			if (any(c.isdigit() for c in text)):
				rooms[text] = results[text]
			else: print(text)
			if text in [ 'EYE', 'FLFV', 'ELE', 'LEV'] or 'ELEV' in text:
				elevators[text] = results[text]
			if text in [ 'STAI', 'TAIR'] or 'STAIR' in text:
				stairs[text] = results[text]
	return rooms, elevators, stairs


def getText(floor, google = False, pytess = False, tess = False, easy = True, scale = False):
	start = time.time()
	print("Running text detection on " + floor)

	im = cv2.imread(final_dir + '/' + floor + '.png')
	orig = cv2.imread(cropped_png_dir + '/' + floor + '.png')

	with open(bbox_dir + '/' + floor + 'bbs.json', 'r') as handle:
		boxes = json.load(handle)

	if google: im, results = recognizeTextWithGoogle(im, boxes, scale)
	if pytess: im,results = recognizeTextWithPyTesseract(im, boxes, scale)
	if tess: im,results = recognizeTextWithTesseract(im, boxes, scale)
	if easy: im,results = recognizeTextWithEasyOCR(im , boxes, scale)

	rooms, elevators, stairs = processText(results)

	#im = drawText(im, results, 60)
	orig = drawText(orig, rooms, 60)
	orig = drawText(orig, elevators, 60)
	orig = drawText(orig, stairs, 60)

	cv2.imwrite(txt_png_dir + '/' + floor + '.png', orig)

	saveTextResults(rooms,floor)

	end = time.time()
	print("[INFO] Recognizing Text took {:.6f} seconds".format(end - start))

# need to process text
# note that tesseract generally only works well on the room numbers
# enforce 3 digit numbers
# enforce the floor number to be the first number in each room
	

