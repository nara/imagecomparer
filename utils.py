# USAGE
# python compare.py

# import the necessary packages
from skimage.measure import compare_ssim as ssim
from tinydb import TinyDB, Query
import matplotlib.pyplot as plt
import numpy as np
import cv2
import datetime as dt
import time, traceback
import threading
import requests
import io
import os
import config
import boto3
import objectview

db = TinyDB(config.db_path)
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def execute(delay, task):
	runloop(delay, task)
	#threading.Thread(target=lambda: runloop(delay, task)).start()

def runloop(delay, task):
	next_time = time.time() + delay
	while True:
		time.sleep(max(0, next_time - time.time()))
		try:
			print ('calling task')
			delay = task()
		except Exception:
			traceback.print_exc()
		next_time += (time.time() - next_time) // delay * delay + delay

def compareImages(sourcePath, currentImage, threshold):
	currentImage = cv2.cvtColor(currentImage, cv2.COLOR_BGR2GRAY)
	#get images from source path. loop and compare with current image. and use threshold.
	directory = os.fsencode(sourcePath)
	for file in os.listdir(directory):
		fileName = os.fsdecode(file)
		fileName = os.path.join(sourcePath, fileName)
		source = cv2.imread(fileName)
		source = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
		s = ssim(source, currentImage)
		print(f'ssim {s:.2f}')
		if s > threshold:
			return 1
		else:
			continue
	# if match found, return 1. if no match (meaning garage open), return 0.
	return 0

def compareTemplatedImages(currentImage, templatePaths, threshold):
	#inputPath = "C:/Nara/Learning/python/garageservice/images/source/gas/on-withlight.jpg"
	input_gray = cv2.cvtColor(currentImage, cv2.COLOR_BGR2GRAY)

	for templatePath in templatePaths:
		#templatePath = "C:/Nara/Learning/python/garageservice/images/source/gas/one.jpg"
		templateImage = cv2.imread(templatePath)
		template_gray = cv2.cvtColor(templateImage, cv2.COLOR_BGR2GRAY)

		matchingImages = getMatchingOccurrences(input_gray, template_gray)
		print(templatePath)
		print(f'matched count {len(matchingImages)}')
		if len(matchingImages) < 3:
			continue

		for matchingImage in matchingImages:
			#source = cv2.cvtColor(matchingImage, cv2.COLOR_BGR2GRAY)
			s = ssim(matchingImage, template_gray)
			print(f'ssim {s:.2f}')
			if s < threshold:
				return 1
			else:
				continue
		
		break
		# if match found, return 1. if no match (meaning garage open), return 0.
	return 0

def _show_image(img, left_top, w, h):
    x, y = left_top
    cv2.rectangle(img, (x, y), (x+w, y+h), 255, 2)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def _show_image_2(img):
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getMatchingOccurrences(input_gray, template_gray):
	#inputImage = cv2.imread("C:/Nara/Learning/python/garageservice/images/source/gas/on-withlight.jpg")
	
	w, h = template_gray.shape[::-1]

	method = cv2.TM_CCOEFF_NORMED
	result = []

	while True:

		res = cv2.matchTemplate(input_gray, template_gray,method)
		threshold = 0.8
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

		if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			top_left = min_loc
		else:
			top_left = max_loc

		if max_val > threshold:
			bottom_right = (top_left[0]+w, top_left[1]+h)
			result.append(input_gray[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]].copy())
			cv2.rectangle(input_gray, top_left, bottom_right, 255, cv2.FILLED)
			_show_image(input_gray, top_left, w, h)
		else:
			break

	i = 0
	while i < len(result):
		cv2.imwrite(f'C:/Nara/Learning/python/garageservice/images/source/gas/temp/res-{i}.png', result[i])
		i = i + 1

	return result
	
	
def getOpenCvImage(imageStream):
	filebytes = np.asarray(bytearray(imageStream.read()), dtype=np.uint8)
	img = cv2.imdecode(filebytes, cv2.IMREAD_UNCHANGED)
	return img

def getImage(url):
	r = requests.get(url, stream=True)
	try:
		if r.status_code == 200:
			r.raw.decode_content = True
			stream = io.BytesIO(r.content)
			return stream
	finally:
		r.close()

def getCurrent(obj):
	query = Query()
	existing = db.search(query.locationkey == obj['locationkey'])
	if len(existing) == 0:
		return -1
	else:
		return existing[0]['state']

def saveSetting(obj):
	query = Query()
	db.upsert(obj, query.locationkey == obj['locationkey'])
	
def saveToDynamo(obj):
	table = dynamodb.Table('homestates')
	table.put_item(Item=obj)
	return

def saveToS3(image, obj):
	image.seek(0)
	s3.upload_fileobj(image, 'nara.home.project.images', f'file-{obj["userid"]}-{obj["locationkey"]}.jpg')
	return

def findTemplateImageIn(img, template):
	res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF)