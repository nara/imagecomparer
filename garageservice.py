import utils

OPENED_FREQ = 10
CLOSED_FREQ = 20
IMAGE_URL = "http://192.168.86.52:5000/pic"
IMAGES_PATH = "images/source/garage"
THRESHOLD = 0.5
CLOSED_RESULT = 0
OPEN_RESULT = 1

def process():
	imageStream = getImageFromCamera()
	image = utils.getOpenCvImage(imageStream)
	matched =  utils.compareImages(IMAGES_PATH, image, THRESHOLD) #match image to closed images
	result = CLOSED_RESULT if matched == 1 else OPEN_RESULT
	obj = {'userid': '1', 'locationkey' : 'garage', 'state' : result}
	current = utils.getCurrent(obj)
	utils.saveSetting(obj)

	#utils.saveToDynamo(obj)
	#utils.saveToS3(imageStream, obj)
	#print('posted to aws')

	if current != result:
		utils.saveToDynamo(obj)
		#utils.saveToS3(imageStream, obj)
		print('posted to aws')

	if result == OPEN_RESULT:
		return OPENED_FREQ
	else:
		return CLOSED_FREQ

def getImageFromCamera():
	return utils.getImage(IMAGE_URL)

utils.execute(CLOSED_FREQ, process)