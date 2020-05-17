# import the necessary packages
from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import datetime as dt

a = dt.datetime.now()
# load the images -- the original, the original + contrast,
# and the original + photoshop
original = cv2.imread("images/source/original-1.jpg")
contrast = cv2.imread("images/open-right-1.jpg")

# convert the images to grayscale
original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

# initialize the figure
'''fig = plt.figure("Images")
images = ("Original", original), ("Contrast", contrast)

# loop over the images
for (i, (name, image)) in enumerate(images):
	# show the image
	ax = fig.add_subplot(1, 3, i + 1)
	ax.set_title(name)
	plt.imshow(image, cmap = plt.cm.gray)
	plt.axis("off")

# show the figure
plt.show()'''

# compare the images
#compare_images(original, original, "Original vs. Original")
compare_images(original, contrast, "Original vs. Contrast")

b = dt.datetime.now()
print(f'time difference {b-a}')