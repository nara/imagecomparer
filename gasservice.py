import utils
import cv2

OPENED_FREQ = 15
CLOSED_FREQ = 30
IMAGE_URL = "http://192.168.86.53:5000/pic"
IMAGES_PATH = "images/source/gas"
THRESHOLD = 0.5
CLOSED_RESULT = 0
OPEN_RESULT = 1

def process():
	#imageStream = getImageFromCamera()
	#image = utils.getOpenCvImage(imageStream)
	path = f"{IMAGES_PATH}/general/off-test2.jpg"
	image = cv2.imread(path)

	paths = [f'{IMAGES_PATH}/one.jpg']
	matched =  utils.compareTemplatedImages(image, paths, THRESHOLD) #match image to closed images
	result = CLOSED_RESULT if matched == 1 else OPEN_RESULT
	obj = {'userid': '1', 'locationkey' : 'gas', 'state' : result}
	current = utils.getCurrent(obj)
	utils.saveSetting(obj)

	if current != result:
		utils.saveToDynamo(obj)
		#utils.saveToS3(image, obj)
		print('posted to aws')

	if result == OPEN_RESULT:
		return OPENED_FREQ
	else:
		return CLOSED_FREQ

def getImageFromCamera():
	return utils.getImage(IMAGE_URL)

#utils.execute(CLOSED_FREQ, process)