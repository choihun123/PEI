import mlpy
import numpy as np
from pyspatialite import dbapi2 as db
import image

def classify(path, images, down=4):
	""" Runs MLPY's Maximum Likelihood Classification algorithm on the images"""
	pass

if __name__ == '__main__':
	path = "/Users/hunchoi/Code/PEI/tests/june140.tif"
	spat = "/Users/hunchoi/Code/PEI/tests/crops.sqlite"

	# make sqlite connection
	conn = db.connect(spat)
	cur = conn.cursor()

	# store the x and y coordinates
	x, y, nx, ny = ([] for i in range(4))
	label = np.zeros(0)

	# read in selected crop pixels
	sql = "SELECT ST_X(geometry), ST_Y(geometry), id FROM crops"
	rs = cur.execute(sql)
	for row in rs:
		x.append(row[0])
		y.append(row[1]*-1)
		label = np.append(label, row[2])

	# read in selected non-crop pixels
	sql = "SELECT ST_X(geometry), ST_Y(geometry), id FROM noncrops"
	rs = cur.execute(sql)
	for row in rs:
		nx.append(row[0])
		ny.append(row[1]*-1)
		label = np.append(label, row[2])
		
	# read in image TODO this won't be required in the actual method
	tif = image.Image("june140.tif", path)
	tif.array = image.convert2OpenCV(tif.array)

	# create training data
	train = np.zeros([len(x) + len(nx), 4], dtype=np.uint16)

	# get the values of the pixels that have been specified
	for i in xrange(len(x)):
		train[i, :] = tif.array[y[i], x[i], :]
	for i in xrange(len(nx)):
		train[len(x)+i, :] = tif.array[y[i], x[i], :]

	# train the model
	ml = mlpy.MaximumLikelihoodC()
	ml.learn(train, label)

	# classify other points randomly chosen from the image
	results = ml.pred(train)
	print results[:30]
	print results[30:]
	