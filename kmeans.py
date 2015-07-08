import sys
import numpy as np 
import cv2
import matplotlib.pyplot as plt 
from image import *
from scipy.cluster.vq import kmeans, kmeans2, vq, whiten

# read in the image
if __name__ == '__main__':
	img = cv2.imread("/Users/hunchoi/Code/PEI/sample_images/messi5.jpg")
	# check an image was read in
	if img == None:
		print 'Error: No image read'
		sys.exit()

	# create a smaller image pyramid
	small = cv2.pyrDown(img)
	#cv2.imshow('image', small)
	#cv2.waitKey(0)

	# Use averaging filter on the image to remove noise
	blurred = cv2.GaussianBlur(small, (3,3), 0)
	#cv2.imshow('image', blurred)
	#cv2.waitKey(0)
	
	# for each pixel in the image, add the green value to the dataset list
	height, width,_ = blurred.shape
	data = np.empty([(height*width), 2], dtype=float)
	for i in range(0, height):
		for j in range(0, width):
			data[(i*width+j), 0] = blurred[i,j,1]
			data[(i*width+j), 1] = blurred[i,j,2]

	# Perform kmeans2 clustering
	centroids, label = kmeans2(data, 4, minit='points')
	plt.plot(data[label==0,0], data[label==0,1], 'ob', 
			 data[label==1,0], data[label==1,1], 'or',
			 data[label==2,0], data[label==2,1], 'om',
			 data[label==3,0], data[label==3,1], 'oc',)
	plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
	plt.show()
	plt.close()
	print label

"""
	# perform kmeans clustering
	white = whiten(data)
	centroids,_ = kmeans(white, 2)
	# assign each sample to a cluster
	idx,_ = vq(data,centroids)

	plt.plot(data[idx==0,0],data[idx==0,1],'ob', data[idx==1,0],data[idx==1,1],'or')
	plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
	plt.show()

	# plot on graph
	plt.plot(red, green, 'go')
	plt.show()
	plt.close()"""