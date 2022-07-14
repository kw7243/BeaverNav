import cv2
import pytesseract
import numpy as np

def dialte(img,k,itr):
  # Load image, grayscale, Gaussian blur, adaptive threshold
  image = img
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (k,k), 0)
  thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

  # Dilate to combine adjacent text contours
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k,k))
  dilate = cv2.dilate(thresh, kernel, iterations=itr)

  # Find contours, highlight text areas, and extract ROIs
  cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = cnts[0] if len(cnts) == 2 else cnts[1]
  boundingRecs = []
  ROI_number = 0
  for c in cnts:
      area = cv2.contourArea(c)
      if area > 0:
          x,y,w,h = cv2.boundingRect(c)
          #cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
          boundingRecs.append((x, y, x + w, y + h))
          # ROI = image[y:y+h, x:x+w]
          # cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)
          # ROI_number += 1


  #cv2_imshow(image)
  return boundingRecs, dilate

def runOCR(img):

  scale_percent = 500 # percent of original size
  width = int(img.shape[1] * scale_percent / 100)
  height = int(img.shape[0] * scale_percent / 100)
  dim = (width, height)
    
  # resize image
  resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
  newimg=np.full((height+100,width+100,3),255,dtype=np.uint8)
  newimg[50:height+50,50:width+50,:]=resized
  OCR = pytesseract.image_to_string(newimg,lang='eng')
  return OCR.replace("\n"," ").replace("\x0c"," ")
  

def getNames(img_in,k,itr):
  img=img_in[:]
  boundingRecs, dilate = dialte(img,k,itr)
  nameChords = []
  disimg=cv2.cvtColor(dilate, cv2.COLOR_GRAY2BGR);
  for r in boundingRecs:
    ocr = runOCR(img[r[1]:r[3],r[0]:r[2]])
    if len(ocr.strip()) == 0:
      continue
    nameChords.append((ocr,((r[0]+r[2])//2,(r[1]+r[3])//2)))
    cv2.rectangle(img, (r[0], r[1]), (r[2],r[3]), (36,255,12), 3)
    cv2.putText(img, nameChords[-1][0], nameChords[-1][1], cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
  # commented for runtime
  #cv2_imshow(img)

  return nameChords

def eliminateBottom(img):
  tracer=[0,height//2]

  going = True
  state=0
  while going:
    if(state==0):
      if(img[tracer[1],tracer[0],0]==0):
        state+=1
        tracer[0]+=5
      else:
        tracer[0]+=1
    elif(state==1):
      if(img[tracer[1],tracer[0],0]==0):
        state+=1
        tracer[1]+=5
      else:
        tracer[1]+=1
    elif(state==2):
      img[tracer[1]:,:,:]=255
      going = False
  return img
