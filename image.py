
from __future__ import division
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
import OrthoImage

# An image object that will hold several properties of each image
class Image:
	def __init__(self, name, path):
		self.name = name								# name of image
		self.path = path								# path of image
		self.array,_ = OrthoImage.load(path)            # numpy array of raster
		self.cluster1 = 0.0 						    # cluster1 ratio
		self.cluster2 = 0.0  							# cluster2 ratio
		self.cluster3 = 0.0  							# cluster3 ratio
		self.cluster4 = 0.0  							# cluster4 ratio
		#self.cluster5 = 0.0  							# cluster5 ratio
		#self.cluster6 = 0.0  							# cluster6 ratio

def convert2OpenCV(image):
	""" Converts a GDAL-generated numpy array into a OpenCV-style numpy array"""
	# rearrange the axes to fit OpenCV array format
	convert = image.transpose(1,2,0)
	return convert

def NDVI(image, i, j):
	""" Returns NDVI. Returns 0 if NIR+R is 0 """
	R, NIR = float(image[i, j, 2]), float(image[i, j, 3])

	# NDVI is given by (NIR - R)/(NIR + R)
	if (NIR + R) != 0:
		return (NIR-R)/(NIR+R)
	return 0

def plot2DClusters(data, centroids, label, order):
	""" Graphs 2 of 4 axes and shows the k-means clusters in a 2D space """
	o = order

	# plot the data points
	plt.plot(data[label==o[0],1], data[label==o[0],2], 'ob', 
			 data[label==o[1],1], data[label==o[1],2], 'or',
			 data[label==o[2],1], data[label==o[2],2], 'om',
			 data[label==o[3],1], data[label==o[3],2], 'oc')
			 #data[label==o[4],1], data[label==o[4],2], 'oy',
			 #data[label==o[5],1], data[label==o[5],2], 'ow'

	# plot the centroids
	plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
	plt.show()
	plt.close()

def plot3DClusters(data, centroids, label, order):
	""" Graphs 3 of 4 axes and shows the k-means clusters in 3D space """
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	o, l = order, label

	# plot the data points
	ax.scatter(data[l==o[0],0], data[l==o[0],1], data[l==o[0],2], c='b')
	ax.scatter(data[l==o[1],0], data[l==o[1],1], data[l==o[1],2], c='g')
	ax.scatter(data[l==o[2],0], data[l==o[2],1], data[l==o[2],2], c='r')
	ax.scatter(data[l==o[3],0], data[l==o[3],1], data[l==o[3],2], c='m')
	#ax.scatter(data[l==o[4],0], data[l==o[4],1], data[l==o[4],2], c='m')
	#ax.scatter(data[l==o[5],0], data[l==o[5],1], data[l==o[5],2], c='m')

	# plot the centroids
	ax.scatter(centroids[:,0], centroids[:,1], centroids[:,2], c='c')
	plt.show()
	plt.close()

def pyramid(image, N):
	""" Returns a smaller image by a factor of N pyramids """
	for i in range(N):
		image = cv2.pyrDown(image)
	return image

def ratio(images, label, order):
	""" Saves the ratio of each type of cluster into each Image object """
	# iterate through each image
	count = 0
	for image in images:
		# total pixels in ths image
		h, w,_ = image.array.shape
		total = h * w

		# find the ratios of each cluster. Up to 6.
		image.cluster1 = (np.sum(label[count:(count + h*w)]==order[0]))/total
		image.cluster2 = (np.sum(label[count:(count + h*w)]==order[1]))/total
		image.cluster3 = (np.sum(label[count:(count + h*w)]==order[2]))/total
		image.cluster4 = (np.sum(label[count:(count + h*w)]==order[3]))/total
		#image.cluster5 = (np.sum(label[count:(count + h*w)]==order[4]))/total
		#image.cluster6 = (np.sum(label[count:(count + h*w)]==order[5]))/total

		print "Ratios of {0}: {1}, {2}, {3}, {4}".format(image.name,
														 image.cluster1,
														 image.cluster2,
														 image.cluster3,
														 image.cluster4)
		count += h*w

def showClusters(label, height, width, name, order):
	""" Displays one visual representation of the clustering """
	# the image to be displayed
	image = np.zeros([height, width, 3], dtype=np.uint8)

	# iterate through the label 
	it = np.nditer(label, flags=['f_index'])
	while not it.finished:
		# reverse calculate the coordinates of the pixel in question
		x = it.index % width
		y = it.index / width

		# fill the pixel with a color according to its label. Up to 6 labels.
		if it[0] == order[0]:
			image[y, x] = (255,0,0)       # Blue
		elif it[0] == order[1]:
			image[y, x] = (0, 255, 0)     # Green
		elif it[0] == order[2]:
			image[y, x] = (0, 0, 255)     # Red
		elif it[0] == order[3]:
			image[y, x] = (0, 255, 255)   # Yellow
		#elif it[0] == order[4]:
			#image[y, x] = (255, 255, 0)   # Cyan
		#elif it[0] == order[5]:
			#image[y, x] = (255, 0, 255)   # Magenta

		it.iternext()

	# display the image
	cv2.imshow(name, image)

def showMultClusters(images, label, order):
	""" Displays all the clusterings """
	# iterate through each image to display
	count = 0
	for image in images:
		h, w,_ = image.array.shape

		# portion the label array and show individual clustering
		showClusters(label[count:(count + h*w)], h, w, image.name, order)
		count += h * w

	cv2.waitKey(0)

def sortClusters(centroids):
	""" Sorts the clusters in order from highest to lowest """
	k, dim = centroids.shape

	# create numpy array of sums of dimensions of each centroid
	sums = np.zeros([k])
	for i in xrange(k):
		sums[i] = np.sum(centroids[i])

	# find and save indexes that would sort the sums 
	order = np.argsort(sums)
	return order

def trimNodata(image):
	""" Returns an image with the nodata pixels trimmed """
	# the dimensions of the image
	height, width, bands = image.shape
	newHeight, newWidth = 0, 0

	# reverse iterate to find new boundaries
	for i in xrange(height-1, 0, -1):
		# assuming the nodata is always from the far edge, find the index where
		# image is no longer nodata.
		if (image[i, 0]!=np.array([0,0,0,0])).all():
			newHeight = i + 1
			break

	for i in xrange(width-1, 0, -1):
		# find index where image is no longer nodata
		if (image[0, i]!=np.array([0,0,0,0])).all():
			newWidth = i + 1
			break

	# return a new image with smaller dimensions with nodata trimmed
	trimmed = np.asarray(image[:newHeight, :newWidth, :], dtype=np.uint16)
	return trimmed
 	