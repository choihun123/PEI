import mlpy
import numpy as np
from pyspatialite import dbapi2 as db
import image
import OrthoImage

def classify(pathTODO, images, k=4, down=4):
	""" Runs MLPY's Maximum Likelihood Classification algorithm on the images"""
	path = "/Users/hunchoi/Code/PEI/satellite/ntf/test/june140.tif"
	spat = "/Users/hunchoi/Code/PEI/satellite/ntf/test/crops.sqlite"
	test = "/Users/hunchoi/Code/PEI/satellite/ntf/test/test.sqlite"

	# store the x and y coordinates
	x = []
	y = []
	classes = np.zeros(0)

	# make sqlite connection to training
	conn = db.connect(spat)
	cur = conn.cursor()

	# read in selected crop pixels coordinate
	sql = "SELECT ST_X(geometry), ST_Y(geometry), id FROM crops"
	rs = cur.execute(sql)
	for row in rs:
		x.append(row[0])
		y.append(row[1]*-1)
		classes = np.append(classes, row[2])

	# read in selected non-crop pixels
	sql = "SELECT ST_X(geometry), ST_Y(geometry), id FROM noncrops"
	rs = cur.execute(sql)
	for row in rs:
		x.append(row[0])
		y.append(row[1]*-1)
		classes = np.append(classes, row[2])
		
	# read in original image
	original,_ = OrthoImage.load(path)
	original = image.GDAL2OpenCV(original)

	# constants to be used throughout
	length = len(x)
	sample = 2**down

	# create training data
	train = np.zeros([length, 4], dtype=np.uint16)

	# get the values of the pixels that have been specified
	for i in xrange(length):
		train[i, :] = original[y[i], x[i], :]
		#print train[i]

	# train the model
	ml = mlpy.MaximumLikelihoodC()
	ml.learn(train, classes)

	# array to be classified
	tif = images[0]

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

	# read in test pixels
	testX = []
	testY = []
	tests = np.zeros(0)

	# make sqlite connection to test data
	conn = db.connect(test)
	cur = conn.cursor()

	# read in coordinates and id of each test point
	sql = "SELECT ST_X(geometry), ST_Y(geometry), id FROM tests"
	rs = cur.execute(sql)
	for row in rs:
		testX.append(row[0])
		testY.append(row[1]*-1)
		tests = np.append(tests, row[2])

	# use the test pixels to calculate error rates for each cluster
	one, two, three, four, five, six = (0 for i in xrange(6))
	for i in xrange(tests.size):
		# check if the pixel is correctly classified
		coord = (testY[i]*w + testX[i]) / sample
		if tests[i] != results[coord]:
			# if incorrect, figure out which cluster it's in
			error = tif.label[coord]

			# increment the number of errors in the corresponding cluster
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
		print "Cluster 1: " + str(float(one)/tests.size)
	if two != 0:
		print "Cluster 2: " + str(float(two)/tests.size)
	if three != 0:
		print "Cluster 3: " + str(float(three)/tests.size)
	if four != 0:
		print "Cluster 4: " + str(float(four)/tests.size)
	if five != 0:
		print "Cluster 5: " + str(float(five)/tests.size)
	if six != 0:
		print "Cluster 6: " + str(float(six)/tests.size)