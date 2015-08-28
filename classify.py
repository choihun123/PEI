#-------------------------------------------------------------------------------
# Author: Hun Choi
#-------------------------------------------------------------------------------
import sys, os
import mlpy
import numpy as np
import image

"""
This method will use mlpy's Maximum Likelihood Classifier to perform a basic
clustering on the TIF files in folder. The training data is supplied in the 
format "T[image name].tif" and quality testing (error-rating) data in the format
"Q[image name].tif". The parameters perform the following:

folder - path to the directory that has the TIF files
images - list of all image objects
ml     - the Maximum Likelihood Classifier (MLC) object. Default is None. 
high   - number of pixels in the largest image. Default resolution is 9216x8192
k      - number of clusters formed. Default is 4 clusters.
down   - number of times the image has been downsampled. Default is 0 times.
show   - show the classification of each image. Default is True.

This method returns the list of image objects, classification results, and
the MLC object. It is expected that the MLC object will be entered as a 
parameter in future calls of classify(). The error rates are saved 
as instance variables in the image objects. 
"""
def classify(folder, images, ml=None, high=75497472, k=4, down=0, show=True):
	""" Runs MLPY's Maximum Likelihood Classification algorithm on the images"""
	# validate input
	if not os.path.isdir(folder):
		sys.exit("Error: given path is not a directory")
	if down < 0:
		sys.exit("Error: downsampling rate cannot be negative")
	if high < 0:
		sys.exit("Error: high cannot be negative")

	print "Classifying the images..."

	# Maximum likelihood classifier object
	if ml is None:
		ml = mlpy.MaximumLikelihoodC()
	allTrain = np.zeros([0, 4], dtype=np.uint16)
	allClass = np.zeros(0)

	# the magnitude of down sampling
	sample = 2**down

	# iterate through all T (training) TIF files
	for name in os.listdir(folder):
		if not name.endswith(".tif") or not name.startswith("T"):
			continue

		# iterate through all images and find the image with training data
		for img in images:
			if img.name not in name:
				continue

			# path to training polygon TIF and shapefile
			trainImage = os.path.join(folder, name)
			fileName,_ = os.path.splitext(name)
			trainSHPFile = os.path.join(folder, fileName + '.shp')

			# lists to be used to find coordinates and type of the pixels
			trainX, trainY, trainClass = image.readPolygonTIF(trainImage, \
														trainSHPFile, down)
			
			# for debugging, uncomment to see polygons. red=crop green=non crop
			#image.showPolygons(img, trainX, trainY, trainClass)

			# number of training pixels
			length = trainX.shape[0]

			# create training data
			train = np.zeros([length, 4], dtype=np.uint16)

			# get the values of the pixels that have been specified
			for i in xrange(length):
				train[i, :] = img.array[trainY[i], trainX[i], :]

			# append this training data to the overall training data
			allTrain = np.append(allTrain, train, axis=0)
			allClass = np.append(allClass, trainClass)

			# dont bother iterating through the rest of the images
			break

	# if allClass or allTrain is empty, then no training data in the directory
	if allClass.size == 0 or allTrain.size == 0:
		sys.exit("Error: no training data in directory")
			
	# train the model
	ml.learn(allTrain, allClass)

	# create a data array to store the images in a classify-able format
	data = np.zeros([high*len(images)/sample**2, 4])
	count = 0

	# iterate through images and fill the data array
	for img in images:
		h, w,_ = img.array.shape
		for i in xrange(h):
			for j in xrange(w):
				try:
					# put the whole image into data
					data[count, :] = img.array[i, j, :]
					count += 1

				except IndexError:
					sys.exit("Error: high is too small")

	# trim the unused part of data off
	data = data[:count, :]

	# classify all the images
	results = ml.pred(data)

	# display the classification results
	if show:
		image.showMultClassification(results, images)

	# iterate through all Q (quality test) TIF files
	for name in os.listdir(folder):
		if not name.endswith(".tif") or not name.startswith("Q"):
			continue

		# iterate through all images and find the images with testing data
		for img in images:
			if img.name not in name:
				continue
			# error counter for each cluster
			errorCount = np.zeros(k, dtype=float)

			# path to testing polygon TIF and shapefile
			testImage = os.path.join(folder, name)
			fileName,_ = os.path.splitext(name)
			testSHPFile = os.path.join(folder, fileName + '.shp')

			# lists to be used to find coordinates and type of the pixels
			testX, testY, testClass = image.readPolygonTIF(testImage, \
														testSHPFile, down)
			
			# for debugging, uncomment to see polygons. red=crop green=non crop
			#image.showPolygons(img, testX, testY, testClass)

			# dimensions of image
			_, w,_ = img.array.shape

			# if no testing pixels are in the Q TIF
			if testClass.size == 0:
				print "Warning: "+img.name+" quality testing data is empty"
				break

			# iterate through all the test pixels
			for i in xrange(testClass.size):
				# check if the pixel is correctly classified
				coord = testY[i]*w + testX[i]
				if testClass[i] != results[coord]:
					# if incorrect, figure out which cluster it's in and 
					# increment the error count of corresponding cluster
					error = img.label[coord]
					errorCount[error] += 1

			# save the error rates in image object
			for i in xrange(k):
				img.error[i] = errorCount[i]/testClass.size

			# print error rate for each cluster
			print "Error rates of "+img.name+": "
			for i in xrange(k):
				print "cluster"+str(i)+": "+str(img.error[i])

			# total error rate for image
			totalError = np.sum(img.error)
			print "Total error rate: " + str(totalError) + '\n'

			# dont bother looking at other images
			break

	return images, results, ml