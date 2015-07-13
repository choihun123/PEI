import sys
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2
import image

# to show the whole numpy array, decomment
#np.set_printoptions(threshold='nan')

# path to image folder
path = "/Users/hunchoi/Code/PEI/tests/output.tif"

# load a TIF file
tif = image.Image(path)
if tif.array is None:
	sys.exit("Error: could not open raster")

# convert array into OpenCV style numpy array (Height,Width,Bands)
tif.array = image.convert2OpenCV(tif.array)

# create a smaller image pyramid
tif.array = image.pyramid(tif.array, 4)
#cv2.imshow("image", tif.array)

# constants and variables used for calculations and plotting
height, width,_ = tif.array.shape
B, G, R, N = 0, 1, 2, 3
data = np.zeros([(height*width), 4])

# iterate through every pixel
for i in range(height):
	for j in range(width):
		# put into data the values to be clustered			
		data[(i*width + j), 0] = tif.array[i, j, B]  # x-axis
		data[(i*width + j), 1] = tif.array[i, j, G]  # y-axis
		data[(i*width + j), 2] = tif.array[i, j, R]  # z-axis
		data[(i*width + j), 3] = tif.array[i, j, N]  # w-axis


# perform kmeans clustering and plot
centroids, label = kmeans2(data, 4, minit='points')
#image.plot2DClusters(data, centroids, label)
#image.plot3DClusters(data, centroids, label)

# display the clustering on a new image
image.showClusters(label, height, width)