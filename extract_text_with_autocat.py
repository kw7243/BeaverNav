import pytesseract
import svg_helper_methods
from svgpathtools import CubicBezier, Path, Line, smoothed_path, wsvg, svg2paths2
import cairosvg
import cv2
import numpy as np
from pdf2image import convert_from_path, convert_from_bytes
from os import listdir
from os.path import isfile, join

beavernav = "/Users/yajva/Desktop/BeaverNav"
mypath = "/Users/yajva/Desktop/BeaverNav/SVG Floor Plans"
nontextpngs = "/Users/yajva/Desktop/BeaverNav/Nontext PNG Floor Plans"
svgfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
nontextpngs = [f for f in listdir(nontextpngs) if isfile(join(nontextpngs, f))]

for floor in svgfiles:
  floor = floor[:-4] # get rid of .svg
  print(floor)
  if floor + ".png" in nontextpngs:
    continue
  #img = convert_from_path('/Users/yajva/Desktop/BeaverNav/31_2.pdf', dpi=500)
  #img[0].save("/Users/yajva/Desktop/BeaverNav/31_2.png", "PNG")
  paths, attributes, svg_attributes = svg2paths2(beavernav + "/SVG Floor Plans/" + floor + ".svg")
  cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/Nontext PNG Floor Plans/" + floor + ".png", background_color="white", dpi=400) # choose on dpi

  """new_paths, new_attributes = [],[]
  for i, (path, attribute) in enumerate(zip(paths, attributes)):
      if len(path) == 0:
        continue
      if svg_helper_methods.is_door(path, attribute):
        continue
      real_path = svg_helper_methods.path_transform(path, svg_helper_methods.parse_transform(attribute.get('transform', '')))
      if real_path.length() < 9 or real_path.length() > 5:
          new_paths.append(path)
          new_attributes.append(attribute)
  print("hey")

  paths, attributes = new_paths, new_attributes

  svg_helper_methods.visualize_all_paths(paths, attributes, svg_attributes, output=beavernav + "/Modified SVG Floor Plans/" + floor + ".svg")
  svg_helper_methods.show_svg(beavernav + "/Modified SVG Floor Plans/" + floor + ".svg")
  cairosvg.svg2png(url=beavernav + "/Modified SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/Modified PNG Floor Plans/" + floor + ".png", background_color="white", dpi=400) # choose on dpi

  img = cv2.imread(beavernav + "/Modified PNG Floor Plans/" + floor + ".png")"""
  nontextimg = cv2.imread(beavernav + "/Nontext PNG Floor Plans/" + floor + ".png")
  img = nontextimg.copy()
  img = img[:int(img.shape[0]*0.875),:]
  realimgcopy = img.copy()
  """cv2.imshow("test", img)
  cv2.waitKey()
  cv2.imshow("test", nontextimg)
  cv2.waitKey()"""

  #print(ocr_methods.getNames(img,3,4))

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blur = cv2.blur(gray, (1,1), 0)
  #blur = cv2.GaussianBlur(gray, (1,1), 0)
  blur = cv2.Canny(gray, 50, 200, 3)
  lines = cv2.HoughLinesP(blur,1,np.pi/1440,0,minLineLength=30,maxLineGap=5)
  for (x1,y1,x2,y2) in lines[:,0]:
    cv2.line(img,(x1,y1),(x2,y2),(255,255,255),3)
  """cv2.imshow("test", img)
  cv2.waitKey()"""
  imgcopy = img.copy()

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (1,1), 0)
  #cv2.imshow("test", blur)
  #cv2.waitKey()
  thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
  #cv2.imshow("test", thresh)
  #cv2.waitKey()
  # Dilate to combine adjacent text contours
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,9))
  dilate = cv2.dilate(thresh, kernel, iterations=2)

  # Find contours, highlight text areas, and extract ROIs
  """cv2.imshow("test", dilate)
  cv2.waitKey()"""
  contours, hierarchy = cv2.findContours(dilate,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
  """cv2.imshow("test", dilate)
  cv2.waitKey()"""
  cv2.drawContours(img, contours, -1, (0,0,255), 3)
  """cv2.imshow("test", img)
  cv2.waitKey()"""


  line_items_coordinates = []
  for c in contours:
      area = cv2.contourArea(c)
      x,y,w,h = cv2.boundingRect(c)
      cv2.rectangle(img, (x,y), (x + w,y+h),(0,255,0),3)
      if w > 300 or h > 300 or w <10 or h < 10:
          continue
      temp = imgcopy[y:y+h,x:x+w]
      realtemp = realimgcopy[y:y+h,x:x+w]

      scale_percent = 500 # percent of original size
      width = int(temp.shape[1] * scale_percent / 100)
      height = int(temp.shape[0] * scale_percent / 100)
      dim = (width, height)

      resized = cv2.resize(temp, dim, interpolation = cv2.INTER_LANCZOS4 )
      newtemp=np.full((height+100,width+100,3),255,dtype=np.uint8)
      newtemp[50:height+50,50:width+50,:]=resized

      """cv2.imshow("test", newtemp)
      cv2.waitKey()    

      cv2.imshow("test", img)
      cv2.waitKey()"""

      text = pytesseract.image_to_string(newtemp, config='--psm 6')
      text = text.replace("\n"," ")

      resized = cv2.resize(realtemp, dim, interpolation = cv2.INTER_LANCZOS4 )
      newtemp=np.full((height+100,width+100,3),255,dtype=np.uint8)
      newtemp[50:height+50,50:width+50,:]=resized

      realtext = pytesseract.image_to_string(newtemp, config='--psm 6')
      realtext = realtext.replace("\n"," ")
      #text.strip()
      if len(realtext) <=7 :
        cv2.rectangle(img, (x,y), (x + w,y+h),(255,255,0),3)
        #print(text)
      if len(realtext) >=50:
        cv2.rectangle(img, (x,y), (x + w,y+h),(255,0,255),3)
      if len(realtext) > 7 and len(realtext) < 50:# and all(c.isdigit() or c.isalpha() for c in text):
        #print(realtext)
        cv2.rectangle(img, (x,y), (x + w,y+h),(255,0,0),3)
        nontextimg[y:y+h,x:x+w] = np.array([[(255,255,255)]*(w)]*(h))

          

  """cv2.imshow("test", img)
  cv2.waitKey()
  cv2.imshow("test", nontextimg)
  cv2.waitKey()"""
  cv2.imwrite(beavernav + "/Modified PNG Floor Plans/" + floor + ".png", img)
  cv2.imwrite(beavernav + "/Nontext PNG Floor Plans/" + floor + ".png", nontextimg)
