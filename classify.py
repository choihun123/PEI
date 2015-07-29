import mlpy
import numpy as np
from pyspatialite import dbapi2 as db
import shapefile
import image
import OrthoImage

def classify(pathTODO, images, k=4, down=4):
	""" Runs MLPY's Maximum Likelihood Classification algorithm on the images"""
	path = "/Users/hunchoi/Code/PEI/satellite/ntf/test/june140.tif"
	trainData = "/Users/hunchoi/Code/PEI/satellite/ntf/test/train.shp"
	testData = "/Users/hunchoi/Code/PEI/satellite/ntf/test/test.shp"
	#np.set_printoptions(threshold=np.nan)

	# lists to be used to find coordinates and type of the pixels
	x, y, classes = readShapefile(trainData)

	# read in original image
	original,_ = OrthoImage.load(path)
	original = image.GDAL2OpenCV(original)

	# constants to be used throughout
	length = len(x)
	sample = 2**down

	# array to be classified
	tif = images[0]

	# create training data
	train = np.zeros([length, 4], dtype=np.uint16)

	# get the values of the pixels that have been specified
	for i in xrange(length):
		#train[i, :] = original[y[i], x[i], :]
		#print train[i]
		train[i, :] = tif.array[y[i]/sample, x[i]/sample, :]

	# train the model
	ml = mlpy.MaximumLikelihoodC()
	ml.learn(train, classes)	

	# create a data array to store the image in a classify-able format
	h, w,_ = tif.array.shape
	data = np.zeros([h*w, 4])
	count = 0
	for i in xrange(h):
		for j in xrange(w):
			# put the whole image into data
			data[count, :] = tif.array[i, j, :]

	# classify the whole image
	results = ml.pred(data)

	# display the classification results
	image.showClassification(results, h, w)

	# lists to be used to find coordinates and type of the pixels
	testX, testY, testClass = readShapefile(testData)

	# use the test pixels to calculate error rates for each cluster
	one, two, three, four, five, six = (0 for i in xrange(6))
	for i in xrange(testClass.size):
		# check if the pixel is correctly classified
		coord = (testY[i]*w + testX[i]) / sample
		if testClass[i] != results[coord]:
			# if incorrect, figure out which cluster it's in and increment 
			# the number of errors in the corresponding cluster
			error = tif.label[coord]
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

	# calculate error rate for each cluster
	if one != 0:
		print "Cluster 1: " + str(float(one)/testClass.size)
	if two != 0:
		print "Cluster 2: " + str(float(two)/testClass.size)
	if three != 0:
		print "Cluster 3: " + str(float(three)/testClass.size)
	if four != 0:
		print "Cluster 4: " + str(float(four)/testClass.size)
	if five != 0:
		print "Cluster 5: " + str(float(five)/testClass.size)
	if six != 0:
		print "Cluster 6: " + str(float(six)/testClass.size)

def readShapefile(shapes):
	"""
	Returns the x, y coordinates of the pixels, as well as the class labels
	in arrays based off the shapefile 
	"""
	# lists to be used to find coordinates and type of the pixels
	x = []
	y = []
	classes = np.zeros(0)

	# open the shapefile and read in all the pixels of the polygons
	sf = shapefile.Reader(shapes)
	shapes = list(sf.iterShapes())
	records = sf.records()
	for i in xrange(len(shapes)):
		for point in shapes[i].points:
			x.append(point[0])
			y.append(point[1]*-1)

			# if the polygon is a crop field polygon, label it class 1
			if records[i][0] == 'crops':
				classes = np.append(classes, 1)

			# else label it class 2
			else:
				classes = np.append(classes, 2)

	return x, y, classes