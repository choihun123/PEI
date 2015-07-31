import sys
import os
import mlpy
import numpy as np
import image

"""
This method will use mlpy's Maximum Likelihood Classifier to perform a basic
clustering on the TIF files in folder. The training data is supplied in the 
format "T[image name].SHP" and quality testing (error-rating) data in the format 
"Q[image name].SHP". The parameters perform the following:

folder - path to the folder that has the TIF files
images - list of images derived from clustering
high   - number of pixels in the largest image. Default resolution is 9216x8192
k      - number of clusters formed. Default is 4 clusters.
down   - number of times the image has been downsampled. Default is 4 times.
show   - show the classification of each image. Default is True.

The method returns the list of image objects so that the error-based mask
creator can use the error-ratings. The error rates are saved as class variables
of the Image class. The classification is not saved. 
"""
def classify(folder, images, high=75497472, k=4, down=4, show=True):
	""" Runs MLPY's Maximum Likelihood Classification algorithm on the images"""
	# validate input
	if not os.path.isdir(folder):
		sys.exit("Error: given path is not a directory")
	if not 1 <= k <= 6:
		sys.exit("Error: k must be between 1 and 6 (inclusive)")

	# Maximum likelihood classifier object
	ml = mlpy.MaximumLikelihoodC()
	allTrain = np.zeros([0, 4], dtype=np.uint16)
	allClass = np.zeros(0)

	# the magnitude of down sampling
	sample = 2**down

	# iterate through all T (training) SHP files
	for name in os.listdir(folder):
		if not name.endswith(".shp") or not name.startswith("T"):
			continue

		# iterate through all images and find the images with training data
		for img in images:
			if img.name not in name:
				continue

			# lists to be used to find coordinates and type of the pixels
			filePath = os.path.join(folder, name)
			trainX, trainY, trainClass = image.readShapefile(filePath)

			# number of training pixels
			length = len(trainX)

			# create training data
			train = np.zeros([length, 4], dtype=np.uint16)

			# get the values of the pixels that have been specified
			for i in xrange(length):
				train[i, :] = img.array[trainY[i]/sample, trainX[i]/sample, :]

			# append this training data to the overall training data
			allTrain = np.append(allTrain, train, axis=0)
			allClass = np.append(allClass, trainClass)
			
	# train the model
	ml.learn(allTrain, allClass)

	# create a data array to store the images in a classify-able format
	data = np.zeros([high/sample*len(images), 4])
	count = 0

	# iterate through images and fill the data array
	for img in images:
		h, w,_ = img.array.shape
		for i in xrange(h):
			for j in xrange(w):
				# put the whole image into data
				data[count, :] = img.array[i, j, :]
				count += 1

				# check that data is big enough
				if count > high/sample:
					sys.exit("Error: the highest resolution is too small")

	# trim the unused part of data off
	data = data[:count, :]

	# classify all the images
	results = ml.pred(data)

	# display the classification results
	if show:
		image.showMultClassification(results, images)

	# use the test pixels to calculate error rates for each cluster
	one, two, three, four, five, six = (0 for i in xrange(6))
	total = 0  # total number of test pixels

	# iterate through all Q (quality test) SHP files
	for name in os.listdir(folder):
		if not name.endswith(".shp") or not name.startswith("Q"):
			continue

		# iterate through all images and find the images with training data
		for img in images:
			if img.name not in name:
				continue

			# lists to be used to find coordinates and type of the pixels
			filePath = os.path.join(folder, name)
			testX, testY, testClass = image.readShapefile(filePath)

			# update total number of test pixels
			total += testClass.size

			# iterate through all the test pixels
			for i in xrange(testClass.size):
				# check if the pixel is correctly classified
				coord = (testY[i]*w + testX[i]) / sample
				if testClass[i] != results[coord]:
					# if incorrect, figure out which cluster it's in and 
					# increment the error count of corresponding cluster
					error = img.label[coord]
					if error == 0:
						one += 1
					elif error == 1:
						two += 1
					elif error == 2:
						three += 1
					elif error == 3:
						four += 1
					elif error == 4:
						five += 1
					elif error == 5:
						six += 1

	# save the error rates in image object
	image.Image.error1 = float(one)/total
	image.Image.error2 = float(two)/total
	image.Image.error3 = float(three)/total
	image.Image.error4 = float(four)/total
	image.Image.error5 = float(five)/total
	image.Image.error6 = float(six)/total
	
	# print error rate for each cluster and total error rate
	if one != 0:
		print "Cluster 1: " + str(image.Image.error1)
	if two != 0:
		print "Cluster 2: " + str(image.Image.error2)
	if three != 0:
		print "Cluster 3: " + str(image.Image.error3)
	if four != 0:
		print "Cluster 4: " + str(image.Image.error4)
	if five != 0:
		print "Cluster 5: " + str(image.Image.error5)
	if six != 0:
		print "Cluster 6: " + str(image.Image.error6)
	totalError = one + two + three + four + five + six
	print "Total error rate: " + str(float(totalError)/total)
	
	return images