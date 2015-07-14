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
path = "/Users/hunchoi/Code/PEI/satellite/ntf/july13"

# list of Image objects
allImages = []

# data array for clustering. Initially maximal length
length = len([name for name in os.listdir(path) if name.endswith(".tif")])
data = np.zeros([length*9216*7168, 4])

# used for indexing
count = 0

# iterate through all the files in the directory
for name in os.listdir(path):
	# ignore hidden files and non-TIF files
	if name.startswith('.') or not name.endswith(".tif"):
		continue
	filePath = os.path.join(path, name)
	
	# load a TIF file
	tif = image.Image(filePath)
	if tif.array is None:
		sys.exit("Error: could not open raster")

	# convert array into OpenCV style numpy array (Height,Width,Bands)
	tif.array = image.convert2OpenCV(tif.array)

	# trim the nodata image
	tif.array = image.trimNodata(tif.array)

	# create a smaller image pyramid and save tif in image list
	tif.array = image.pyramid(tif.array, 4)
	allImages.append(tif)

	# constants and variables used for calculations and plotting
	height, width,_ = tif.array.shape
	B, G, R, N = 0, 1, 2, 3

	# iterate through every pixel
	for i in range(height):
		for j in range(width):
			# put into data the values to be clustered			
			data[count, 0] = tif.array[i, j, B] 
			data[count, 1] = tif.array[i, j, G]  
			data[count, 2] = tif.array[i, j, R]  
			data[count, 3] = tif.array[i, j, N]  
			count += 1

# trim the rest of numpy that's not used
data = data[:count, :]

# perform kmeans clustering
centroids, label = kmeans2(data, 3, minit='points')

# save the ratio of each type of cluster in each Image
#image.ratio(allImages, label)

# plot graphs of clustering
#image.plot2DClusters(data, centroids, label)
#image.plot3DClusters(data, centroids, label)

# display the clustering on new images
#image.showMultClusters(allImages, label)