import sys, os
import numpy as np
from sklearn.cluster import KMeans
import image

"""
This method will use scikit-learn's KMeans() to perform a clustering on all 
TIF files in the specified folder. The parameters perform the following:

folder - path to the folder that has the TIF files
high   - number of pixels in the largest image. Default resolution is 9216x8192
k      - number of clusters to form. Default is 4 clusters.
down   - number of times to downsample the image. Default is 4 times.
ratio  - calculate ratios of clusters for each image and print. Default is True.
plot2D - plot 2 axes of clusters. Default is False. Adjust Line 98 to 
		 change axes.
plot3D - plot 3 axes of clusters. Default is False. Adjust Line 100 to 
		 change axes.
show   - show the clustering of each image. Default is True.

The method returns the list of image objects so that the error-weighted 
classifier can use the ratios. This method currently clusters based on the
four bands of the satellite images (BGRN). The clustering is saved in the .label
data attribute of each image instance as a 1D array. 
"""
def cluster(folder, high=75497472, k=4, down=4, ratio=True, plot2D=False,
			plot3D=False, show=True):
	""" Perform a kmeans clustering on the TIF files in folder """
	# validate input
	if not os.path.isdir(folder):
		sys.exit("Error: given path is not a directory")
	if not 1 <= k <= 6:
		sys.exit("Error: k must be between 1 and 6 (inclusive)")

	# path to image folder
	path = folder

	# list of Image objects
	allImages = []

	# data array for clustering. Initially maximal length
	length = len([name for name in os.listdir(path) if name.endswith(".tif")])
	data = np.zeros([length*high, 4])

	# used for indexing
	count = 0

	# iterate through all the files in the directory
	for name in os.listdir(path):
		# ignore hidden files and non-TIF files
		if name.startswith('.') or not name.endswith(".tif"):
			continue
		filePath = os.path.join(path, name)
		
		# load a TIF file
		tif = image.Image(name, filePath)
		if tif.array is None:
			sys.exit("Error: could not open raster")

		# convert array into OpenCV style numpy array (Height,Width,Bands)
		tif.array = image.GDAL2OpenCV(tif.array)

		# trim the nodata image
		tif.array = image.trimNodata(tif.array)

		# create a smaller image pyramid and save tif in image list
		tif.array = image.pyramid(tif.array, down)
		allImages.append(tif)

		# constants and variables used for calculations and plotting
		height, width,_ = tif.array.shape
		B, G, R, N = 0, 1, 2, 3

		# iterate through every pixel
		for i in xrange(height):
			for j in xrange(width):
				# put into data the values to be clustered			
				data[count, 0] = tif.array[i, j, B]
				data[count, 1] = tif.array[i, j, G]
				data[count, 2] = tif.array[i, j, R]
				data[count, 3] = tif.array[i, j, N]
				count += 1

				# check that data is big enough
				if count > high:
					sys.exit("Error: the highest resolution is too small")

	# trim the rest of numpy that's not used
	data = data[:count, :]

	# perform kmeans clustering
	clstr = KMeans(n_clusters=k, n_jobs=-1)
	clstr.fit(data)
	label = clstr.labels_
	centroids = clstr.cluster_centers_

	# split the label array into a specific one for each image
	image.splitLabel(allImages, label)

	# for cluster consistency between runs
	order = image.sortClusters(centroids)

	# save and print the ratio of each type of cluster in each Image
	if ratio:
		image.ratio(allImages, order)

	# plot graphs of clustering
	if plot2D:
		image.plot2DClusters(data, centroids, label, order, B, G)
	if plot3D:
		image.plot3DClusters(data, centroids, label, order, B, G, R)

	# display the clustering
	if show:
		image.showMultClusters(allImages, order)

	# return all the images to feed into the error-weighted classifier
	return allImages

# if called as a script, run it on the path given
if __name__ == '__main__':
	cluster(sys.argv[1])
