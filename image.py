from __future__ import division
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
import OrthoImage

# An image object that will hold several properties of each image
class Image:
	def __init__(self, name):
		self.name = name                                # name of image
		self.array,_ = OrthoImage.load(name)            # numpy array of raster
		"""self.cluster1 = 0.0  # cluster1 ratio
		self.cluster2 = 0.0  # cluster2 ratio
		self.cluster3 = 0.0  # cluster3 ratio
		self.cluster4 = 0.0  # cluster4 ratio"""

def convert2OpenCV(image):
	""" Converts a GDAL-generated numpy array into a OpenCV-style numpy array"""
	# rearrange the axes to fit OpenCV array format
	convert = image.transpose(1,2,0)
	return convert

def ignoreNoData(image, i, j):
	"""
	Returns true if the pixel has no data. Adjusted for nodata pixels 
	attaining values during pyramid calculations. Very few normal pixels
	should be affected by this threshold. 
	"""
	# check that the pixel has no or close to no data
	if (image[i, j, 0] <= 10 and
		image[i, j, 1] <= 10 and
		image[i, j, 2] <= 10 and
		image[i, j, 3] <= 10):
		return True
	return False

def NDVI(image, i, j):
	""" Returns NDVI. Returns 0 if NIR+R is 0 """
	R, NIR = float(image[i, j, 2]), float(image[i, j, 3])

	# NDVI is given by (NIR - R)/(NIR + R)
	if (NIR + R) != 0:
		return (NIR-R)/(NIR+R)
	return 0

def plot2DClusters(data, centroids, label):
	""" Graphs 2 of 4 axes and shows the k-means clusters in a 2D space """
	# plot the data points
	plt.plot(data[label==0,1], data[label==0,2], 'ob', 
			 data[label==1,1], data[label==1,2], 'or')

	# plot the centroids
	plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
	plt.show()
	plt.close()

def plot3DClusters(data, centroids, label):
	""" Graphs 3 of 4 axes and shows the k-means clusters in 3D space """
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	# plot the data points
	ax.scatter(data[label==0,0], data[label==0,1], data[label==0,2], c='b')
	ax.scatter(data[label==1,0], data[label==1,1], data[label==1,2], c='g')
	#ax.scatter(data[label==2,0], data[label==2,1], data[label==2,2], c='r')
	#ax.scatter(data[label==3,0], data[label==3,1], data[label==3,2], c='m')

	# plot the centroids
	ax.scatter(centroids[:,0], centroids[:,1], centroids[:,2], c='r')
	plt.show()

def plotRaster():
	""" Graph the clusters by color on the original raster """
	pass

def pyramid(image, N):
	""" Returns a smaller image by a factor of N pyramids """
	for i in range(N):
		image = cv2.pyrDown(image)
	return image