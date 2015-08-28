from __future__ import division
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 
import matplotlib.pyplot as plt
import cv2
import shapefile
import OrthoImage

"""
An image object and several methods required throughout the whole process of 
clustering, classifying, and error-based training. The image 
object holds the name, file path, raster as a numpy array in OpenCV 
format (Height,Width,Bands), cover rates, and error rates.
"""
class Image:
	def __init__(self, name, path, k):
		self.name = name								# name of image
		self.path = path								# path of image
		self.array,_ = OrthoImage.load(path)            # numpy array of raster
		self.label = None								# clustering of image
		self.cover = np.zeros(k)						# cover rates of cluster
		self.error = np.zeros(k)						# error rates of cluster

def calculatePolygons(images, k, N=20):
	""" 
	Calculates and prints the number of required polygons for each cluster. 
	"""
	# iterate through each image
	for img in images:
		# dot product of cover and error rate
		total = np.dot(img.cover, img.error)

		# print the number of polygons required for each cluster
		print "Required T and Q polygons for " + img.name + ":"
		for i in xrange(k):
			print "cluster"+str(i)+": "+str(int(round(img.cover[i]*img.error[i]\
																/total*N)))

def coverRate(images, order, k):
	""" 
	Saves the cover rate of each type of cluster into each Image object and
	prints the rates.
	"""
	o = order

	# iterate through each image
	for img in images:
		h, w,_ = img.array.shape
		total = h*w

		# find the cover rates of each cluster
		for i in xrange(k):
			img.cover[i] = (np.sum(img.label==o[i]))/total

		# print the cluster ratios, excluding empty ones
		print "Cover rates of "+img.name+": "
		for i in xrange(k):
			if img.cover[i] != 0.0:
				print "cluster"+str(i)+": "+str(img.cover[i])
		print

def GDAL2OpenCV(image):
	""" Converts a GDAL-generated numpy array into a OpenCV numpy array"""
	# rearrange the axes to fit OpenCV array format
	return image.transpose(1,2,0)

def NDVI(image, i, j):
	""" Returns NDVI. Returns 0 if NIR+R is 0 """
	R, NIR = float(image[i, j, 2]), float(image[i, j, 3])

	# NDVI is given by (NIR - R)/(NIR + R)
	if (NIR + R) != 0:
		return (NIR-R)/(NIR+R)
	return 0

def plot2DClusters(data, centroids, label, order, X, Y):
	""" Graphs 2 of 4 axes and shows the k-means clusters in a 2D space """
	o = order

	# plot the data points
	try:
		plt.plot(data[label==o[0],X], data[label==o[0],Y], 'ob') 
		plt.plot(data[label==o[1],X], data[label==o[1],Y], 'og')
		plt.plot(data[label==o[2],X], data[label==o[2],Y], 'or')
		plt.plot(data[label==o[3],X], data[label==o[3],Y], 'oy')
		plt.plot(data[label==o[4],X], data[label==o[4],Y], 'oc')
		plt.plot(data[label==o[5],X], data[label==o[5],Y], 'om')
	except IndexError:
		pass 

	# plot the centroids
	plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
	plt.show()
	plt.close()

def plot3DClusters(data, centroids, label, order, X, Y, Z):
	""" Graphs 3 of 4 axes and shows the k-means clusters in 3D space """
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	o, l = order, label

	# plot the data points
	try:
		ax.scatter(data[l==o[0],X], data[l==o[0],Y], data[l==o[0],Z], c='b')
		ax.scatter(data[l==o[1],X], data[l==o[1],Y], data[l==o[1],Z], c='g')
		ax.scatter(data[l==o[2],X], data[l==o[2],Y], data[l==o[2],Z], c='r')
		ax.scatter(data[l==o[3],X], data[l==o[3],Y], data[l==o[3],Z], c='y')
		ax.scatter(data[l==o[4],X], data[l==o[4],Y], data[l==o[4],Z], c='c')
		ax.scatter(data[l==o[5],X], data[l==o[5],Y], data[l==o[5],Z], c='m')
	except IndexError:
		pass

	# plot the centroids
	ax.scatter(centroids[:,0], centroids[:,1], centroids[:,2], c='w', s=30)
	plt.show()
	plt.close()

def pyramid(image, N):
	""" Returns a smaller image by a factor of N pyramids """
	for i in range(N):
		image = cv2.pyrDown(image)
	return image

def readPolygonTIF(polygonTIF, shpfile, down):
	"""
	Returns the x, y coordinates of the pixels as well as the class 
	labels in numpy arrays based off the polygonTIF. polygonTIF will be 
	effectively downsampled in this function, and thus so are x, y, and class.
	"""
	sample = 2**down

	# arrays to be used to find coordinates and type of the pixels
	x = np.zeros(0)
	y = np.zeros(0)
	classes = np.zeros(0)

	# read in the polygonImage
	polyImage,_ = OrthoImage.load(polygonTIF)
	polyImage = GDAL2OpenCV(polyImage)

	# downsample the polTIF
	if down > 0:
		polyImage = pyramid(polyImage, down)

	# dimensions of TIF image
	h, w,_ = polyImage.shape

	# downsampled dimensions of the bounding box of the polygons
	sf = shapefile.Reader(shpfile)
	lx,_ ,_ , uy = sf.bbox
	lx = lx/sample
	uy = uy/sample*-1

	# iterate through the entire polyImage
	for i in xrange(h):
		for j in xrange(w):
			# if the value of the pixel is 255(crop) then add to the arrays
			# as a crop pixel. The condition is adjusting for downsampling.
			if polyImage[i, j] > 1:
				x = np.append(x, j + lx)
				y = np.append(y, i + uy)
				classes = np.append(classes, 1)

			# else if the value of the pixel is 1 (noncrop) then add to arrays
			# as a noncrop pixel
			elif polyImage[i, j] == 1:
				x = np.append(x, j + lx)
				y = np.append(y, i + uy)
				classes = np.append(classes, 2)

	return x, y, classes

def showClassification(results, image):
	""" Displays the classification results """
	# image of classification to be displayed
	height, width,_ = image.array.shape
	classify = np.zeros([height, width, 3], dtype=np.uint8)

	# iterate through the classification results
	it = np.nditer(results, flags=['f_index'])
	while not it.finished:
		# calculate the coordinates of the pixel in question
		x = it.index % width
		y = it.index / width

		# if crop field pixel, display as red. Else display as green
		if it[0] == 1:
			classify[y, x] = (0, 0, 255)
		else:
			classify[y, x] = (0, 255, 0)

		it.iternext()

	cv2.imshow("Classification of " + image.name, classify)

def showClusters(image, order):
	""" Displays one visual representation of the clustering """
	# the clustered image to be displayed
	h, w,_ = image.array.shape
	cluster = np.zeros([h, w, 3], dtype=np.uint8)

	# iterate through image's label 
	it = np.nditer(image.label, flags=['f_index'])
	while not it.finished:
		# calculate the coordinates of the pixel in question
		x = it.index % w
		y = it.index / w

		# fill the pixel with a color according to its label
		if it[0] == order[0]:
			cluster[y, x] = (255,0,0)       # Blue
		elif it[0] == order[1]:
			cluster[y, x] = (0, 255, 0)     # Green
		elif it[0] == order[2]:
			cluster[y, x] = (0, 0, 255)     # Red
		elif it[0] == order[3]:
			cluster[y, x] = (0, 255, 255)   # Yellow
		elif it[0] == order[4]:
			cluster[y, x] = (255, 255, 0)   # Cyan
		elif it[0] == order[5]:
			cluster[y, x] = (255, 0, 255)   # Magenta

		it.iternext()

	# display the image
	cv2.imshow("Clustering of " + image.name, cluster)

def showMultClassification(results, images):
	""" Displays all the classification results in images """
	# count how much of the results array to feed
	count = 0

	# iterate through each image
	for img in images:
		# properties of this image
		h, w,_ = img.array.shape

		# show individual classification result
		showClassification(results[count:(count+h*w)], img)

		# increment by the number of pixels in the previous image
		count += h*w

	cv2.waitKey(0)
	cv2.destroyAllWindows()

def showMultClusters(images, order):
	""" Displays all the clusterings """
	# iterate through each image to display
	for img in images:
		# show individual clustering
		showClusters(img, order)

	cv2.waitKey(0)
	cv2.destroyAllWindows()

def showPolygons(image, x, y, classes):
	""" Shows the shapefile and colors crops as red and noncrops as green """
	# properties of this image
	h, w,_ = image.array.shape

	# create a new image to display the shapefile
	shapes = np.zeros([h, w, 3], dtype=np.uint8)

	# iterate through image's label 
	it = np.nditer(classes, flags=['f_index'])
	while not it.finished:
		# calculate the coordinates of the pixel in question
		px = x[it.index]
		py = y[it.index]
		
		# Draw crop field pixels as red and anything else as green
		if it[0] == 1:
			shapes[py, px] = (0, 0, 255)
		elif it[0] == 2:
			shapes[py, px] = (0, 255, 0)

		it.iternext()

	cv2.imshow("Shapefile of " + image.name, shapes)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def sortClusters(centroids):
	""" Sorts the clusters in order from highest to lowest """
	k,_ = centroids.shape

	# create numpy array of sums of dimensions of each centroid
	sums = np.zeros(k)
	for i in xrange(k):
		sums[i] = np.sum(centroids[i])

	# return array of indexes that would sort the sums 
	return np.argsort(sums)

def splitLabel(images, label):
	""" Splits the label array so each image has its own label array """
	# iterate through each image
	count = 0
	for img in images:
		# properties of this image
		h, w,_ = img.array.shape

		# find the label array for this image
		img.label = label[count:(count + h*w)]

		# increment by the number of pixels in the previous image
		count += h*w

def trimNodata(image):
	"""
	Returns an image with the nodata pixels trimmed. Assumes the nodata is
	at the bottom and right of the image, and thus can only be used on 
	satellite images.
	"""
	# the dimensions of the image
	height, width, bands = image.shape
	newHeight, newWidth = 0, 0

	# reverse iterate to find new boundaries
	for i in xrange(height-1, 0, -1):
		# assuming the nodata is always from the far edge, find the index where
		# image is no longer nodata.
		if not np.array_equal(image[i, 0], np.array([0,0,0,0])):
			newHeight = i + 1
			break

	for i in xrange(width-1, 0, -1):
		# find index where image is no longer nodata
		if not np.array_equal(image[0, i], np.array([0,0,0,0])):
			newWidth = i + 1
			break

	# return a new image with smaller dimensions with nodata trimmed
	return np.asarray(image[:newHeight, :newWidth, :], dtype=np.uint16)