import numpy as np 
import cv2
import matplotlib.pyplot as plt 
from image import *
import os

# read in the images one by one and save properties
if __name__ == '__main__':
	# list of image objects to cluster with after processing
	imageList = []

	# path to images folder
	path = "/Users/hunchoi/Code/PEI/tarball_images"

	# iterate through all the files in a certain directory
	for name in os.listdir(path):
		# create absolute path to the file
		filePath = os.path.join(path, name)

		# ignore hidden files
		if not name.startswith('.') and os.path.isfile(filePath):
			# read in an image in color and grayscale
			colorImg = cv2.imread(filePath, 1)
			grayImg = cv2.imread(filePath, 0)
			image = Image(filePath)

			# extract all the properties of the image
			image.color = averageColor(colorImg)	
			image.intensity = averageIntensity(grayImg)
			image.stdDev = stdDev(grayImg)
			image.thirdMoment = thirdMoment(grayImg)
			image.entropy = entropy(grayImg)

			# add to imageList
			imageList.append(image)

			# plot two selected properties
			plt.plot(image.thirdMoment, image.intensity, 'bo')
			#plt.axis([0,255,0,255])

	# the graph is shown
	plt.xlabel('Third moment'), plt.ylabel('Average intensity')
	plt.show()
	plt.close()

	# proceed to call clustering algorithm then show clustered graph