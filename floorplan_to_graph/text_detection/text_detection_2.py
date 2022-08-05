########################################################################
########################################################################
########################################################################
# TRIED, BUT THIS WAS NO BETTER AT TEXT DETECTION THAN EAST
# DON'T USE
########################################################################
########################################################################
########################################################################


import pytesseract
#import svg_helper_methods
from svgpathtools import svg2paths2
import cairosvg
import cv2
import numpy as np
#from pdf2image import convert_from_path, convert_from_bytes
from os import listdir
from os.path import isfile, join

import cv2
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', 500)
#pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract/'

beavernav = "/Users/yajva/Desktop/BeaverNav"
mypath = "/Users/yajva/Desktop/BeaverNav/SVG Floor Plans"
nontextpngs = "/Users/yajva/Desktop/BeaverNav/Nontext PNG Floor Plans"
svgfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
nontextpngs = [f for f in listdir(nontextpngs) if isfile(join(nontextpngs, f))]

for floor in svgfiles:
	floor = floor[:-4] # get rid of .svg
	if floor + ".png" != "1_0.png":
		continue
	#img = convert_from_path('/Users/yajva/Desktop/BeaverNav/31_2.pdf', dpi=500)
	#img[0].save("/Users/yajva/Desktop/BeaverNav/31_2.png", "PNG")
	paths, attributes, svg_attributes = svg2paths2(beavernav + "/SVG Floor Plans/" + floor + ".svg")
	cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/Nontext PNG Floor Plans/" + floor + ".png", background_color="white", dpi=600) # choose on dpi

	nontextimg = cv2.imread(beavernav + "/Nontext PNG Floor Plans/" + floor + ".png")
	img = nontextimg.copy()
	img = img[int(img.shape[0]*0.1):int(img.shape[0]*0.25),int(img.shape[1]*0.3):int(img.shape[1]*0.4)]
	realimgcopy = img.copy()
	cv2.imshow("test", img)
	cv2.waitKey()
	cv2.imshow("test", nontextimg)
	cv2.waitKey()

	scale_percent = 100 # percent of original size
	width = int(img.shape[1] * scale_percent / 100)
	height = int(img.shape[0] * scale_percent / 100)
	dim = (width, height)
	img = cv2.resize(img, dim, interpolation = cv2.INTER_LANCZOS4)
	cv2.imshow("test", img)
	cv2.waitKey()


	"""gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur = cv2.Canny(gray, 50, 200, 3)
	lines = cv2.HoughLinesP(blur,1,np.pi/1440,0,minLineLength=30,maxLineGap=5)
	for (x1,y1,x2,y2) in lines[:,0]:
		cv2.line(img,(x1,y1),(x2,y2),(255,255,255),3)
	cv2.imshow("test", img)
	cv2.waitKey()"""

	"""gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (1,1), 0)
	ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	cv2.imshow("test", thresh)
	cv2.waitKey()"""
	#print(pytesseract.image_to_string(thresh))
	boxes = pytesseract.image_to_boxes(img)
	df_img = pd.DataFrame([x.split(' ') for x in 
	boxes.split('\n')], 
						columns=['char', 'left', 'top', 'width',        'height', 'other'])
	df_img = df_img[ ~ df_img['left'].isnull()]
	# dropping whitespace characters like
	# [',' '.' '/' '~' '"' "'" ':' '°' '-' '|' '=' '%' '”']
	df_img = df_img[ ~ df_img['char'].str.contains(r'[^\w\s]')].reset_index(drop=True)
	df_img[['left', 'top', 'width', 'height']] = df_img[['left', 'top', 'width', 'height']].astype(int)
	print(df_img.head(70))
	h, w, _ = img.shape
	for b in boxes.splitlines():
		b = b.split(' ')
		print(b[0])
		if str(b[0]) != '~':
			continue
		img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 255), 1)
	cv2.imshow("test", img)
	cv2.waitKey()

	boxes = pytesseract.image_to_boxes(img)
	print(boxes)
	df_img = pd.DataFrame([x.split(' ') for x in 
	boxes.split('\n')], 
						columns=['char', 'left', 'top', 'width',        'height', 'other'])
	df_img = df_img[ ~ df_img['left'].isnull()]
	# dropping whitespace characters like
	# [',' '.' '/' '~' '"' "'" ':' '°' '-' '|' '=' '%' '”']
	df_img = df_img[ ~ df_img['char'].str.contains(r'[^\w\s]')].reset_index(drop=True)
	df_img[['left', 'top', 'width', 'height']] = df_img[['left', 'top', 'width', 'height']].astype(int)
	print(df_img.head(70))
	h, w, _ = img.shape
	for b in boxes.splitlines():
		b = b.split(' ')
		print(b[0])
		if str(b[0]) == '~':
			continue
		img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)
	cv2.imshow("test", img)
	cv2.waitKey()


	


