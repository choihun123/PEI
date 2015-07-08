import sys
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2
import image

# to show the whole numpy array, decomment
#np.set_printoptions(threshold='nan')

if __name__ == '__main__':
	# path to image folder
	path = "/Users/hunchoi/Code/PEI/tests/output.tif"

	# load a TIF file
	tif = image.Image(path)
	if tif.array is None:
		sys.exit("Error: could not open raster")

	# convert array into OpenCV style numpy array (Height,Width,Bands)
	tif.array = image.convert2OpenCV(tif.array)
	
	# create a smaller image pyramid
	tif.array = image.pyramid(tif.array, 5)
	
	# constants and variables used for calculations and plotting
	height, width,_ = tif.array.shape
	B, G, R, N = 0, 1, 2, 3
	data = np.zeros([(height*width), 4])

	# iterate through every pixel
	count = 0
	for i in range(height):
		for j in range(width):
			# ignore pixels with no data
			if tif.array[i, j, R] <= 10:
				if image.ignoreNoData(tif.array, i, j):
					continue

			# the two values to use with kmeans
			data[count, 0] = tif.array[i, j, B]  # x-axis
			data[count, 1] = tif.array[i, j, G]  # y-axis
			data[count, 2] = tif.array[i, j, R]  # z-axis
			data[count, 3] = tif.array[i, j, N]  # w-axis
			count += 1

	# deletes trailing 0's from nodata pixels
	data = np.delete(data, np.s_[count:], 0)

	# perform kmeans clustering and plot
	centroids, label = kmeans2(data, 2, minit='points')
	#image.plot2DClusters(data, centroids, label)
	image.plot3DClusters(data, centroids, label)

	
