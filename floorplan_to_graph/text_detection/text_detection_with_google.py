########################################################################
########################################################################
########################################################################
# TRIED, BUT THIS WAS NO BETTER AT TEXT DETECTION THAN EAST
# DON'T USE
########################################################################
########################################################################
########################################################################


from unittest import result
from google.cloud import vision
from os import listdir
from os.path import isfile, join
from pdf2image import convert_from_path, convert_from_bytes
import random
from svgpathtools import svg2paths2
import cairosvg
import time
import json
import re
from google.cloud import vision
from google.cloud import storage
import io
import cv2


# FILE INPUT parameters
beavernav = "/Users/yajva/Desktop/BeaverNav"
mypath = "/Users/yajva/Desktop/BeaverNav/PDF Floor Plans"
nontextpngs = "/Users/yajva/Desktop/BeaverNav/Nontext PNG Floor Plans"
pdffiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def convertPDFtoPNG(floor, dpi):
	img = convert_from_path(beavernav + '/PDF Floor Plans/' + floor + '.pdf', dpi=dpi)
	img[0].save(beavernav + '/PNG Floor Plans/' + floor + '.png', "PNG")
	image = cv2.imread(beavernav+'/PNG Floor Plans/' + floor + '.png')
	return image
# crop the whitespace on the sides and the irrelavant information on the bottom
def cropFloorPlan(image):
	(H, W) = image.shape[:2]
	image = image[int(H * 0.2)//32*32:int(H * 0.75)//32*32, int(W * 0.3)//32*32:int(W * 0.75)//32*32]
	return image

def async_detect_document(gcs_source_uri, gcs_destination_uri):
		"""OCR with PDF/TIFF as source files on GCS"""
		
		# Supported mime_types are: 'application/pdf' and 'image/tiff'
		mime_type = 'application/pdf'

		# How many pages should be grouped into each json output file.
		batch_size = 1

		client = vision.ImageAnnotatorClient()

		feature = vision.Feature(
				type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

		gcs_source = vision.GcsSource(uri=gcs_source_uri)
		input_config = vision.InputConfig(
				gcs_source=gcs_source, mime_type=mime_type)

		gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
		output_config = vision.OutputConfig(
				gcs_destination=gcs_destination, batch_size=batch_size)

		async_request = vision.AsyncAnnotateFileRequest(
				features=[feature], input_config=input_config,
				output_config=output_config)

		operation = client.async_batch_annotate_files(
				requests=[async_request])

		print('Waiting for the operation to finish.')
		operation.result(timeout=420)

		# Once the request has completed and the output has been
		# written to GCS, we can list all the output files.
		storage_client = storage.Client()

		match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
		bucket_name = match.group(1)
		prefix = match.group(2)

		bucket = storage_client.get_bucket(bucket_name)

		# List objects with the given prefix, filtering out folders.
		blob_list = [blob for blob in list(bucket.list_blobs(
				prefix=prefix)) if not blob.name.endswith('/')]
		print('Output files:')
		for blob in blob_list:
				print(blob.name)

		# Process the first output file from GCS.
		# Since we specified batch_size=2, the first response contains
		# the first two pages of the input file.
		output = blob_list[0]

		json_string = output.download_as_string()
		response = json.loads(json_string)

		# The actual response for the first page of the input file.
		first_page_response = response['responses'][0]
		annotation = first_page_response['fullTextAnnotation']

		# Here we print the full text from the first page.
		# The response contains more information:
		# annotation/pages/blocks/paragraphs/words/symbols
		# including confidence scores and bounding boxes
		print('Full text:\n')
		print(annotation['text'])

def detect_text(path):
		"""Detects text in the file."""
		client = vision.ImageAnnotatorClient()

		with io.open(path, 'rb') as image_file:
				content = image_file.read()

		image = vision.Image(content=content)

		response = client.text_detection(image=image)
		texts = response.text_annotations
		print('Texts:')

		results = {}

		for text in texts:
				print('\n"{}"'.format(text.description))

				vertices = (['({},{})'.format(vertex.x, vertex.y)
										for vertex in text.bounding_poly.vertices])

				print('bounds: {}'.format(','.join(vertices)))
				results[text.description] = [(int(vertex.x), int(vertex.y)) for vertex in text.bounding_poly.vertices]
		
		print(len(texts))

		if response.error.message:
				raise Exception(
						'{}\nFor more info on error messages, check: '
						'https://cloud.google.com/apis/design/errors'.format(
								response.error.message))

		return results

def drawBoxes(image,boxes, color, thickness):
	for (startX, startY, endX, endY) in boxes:
		image = cv2.rectangle(image, (startX, startY), (endX, endY), color, thickness)

	return image
	
def main():
	for floor in random.sample(pdffiles, 1):
		floor = floor[:-4]
		floor = '32_D8'
		print("Running text detection & recognition on floor " + floor)
		start = time.time()
		
		image = convertPDFtoPNG(floor, 960) # play with dpi
		image = cropFloorPlan(image)
		cv2.imwrite(beavernav+'/PNG Floor Plans/' + floor + '.png', image)

		#cairosvg.svg2png(url=beavernav + "/SVG Floor Plans/" + floor + ".svg", write_to = beavernav + "/Nontext PNG Floor Plans/" + floor + ".png", background_color="white", dpi=1000) # choose on dpi

		results = detect_text(beavernav + '/PNG Floor Plans/' + floor + '.png')

		boxes = []

		for text in results:
			boxes.append((results[text][0][0],results[text][0][1], results[text][2][0], results[text][2][1] ))
			startX = min(results[text][0][0], results[text][2][0])
			endX = max(results[text][0][0], results[text][2][0])
			startY = min(results[text][0][1], results[text][2][1])
			endY = max(results[text][0][1], results[text][2][1])
			print(startX,startY,endX, endY)
		image = drawBoxes(image, boxes, (0,255,255), 2)
		cv2.imshow('Detection', image)
		cv2.waitKey(0)
		cv2.imwrite(beavernav + "/Modified PNG Floor Plans/" + floor + ".png", image)

			





if __name__ == "__main__":
		main()