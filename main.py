import sys, os
from translate import translate
from cluster import cluster
from classify import classify
from mask import createMask

if __name__ == '__main__':
	# verify folder path
	if not os.path.isdir(sys.argv[1]):
		sys.exit("Error: given path is not a directory")
	path = sys.argv[1]

	#TODO add optional command line arguments for K and down and 
	# flags for the other options in cluster.py

	# translate the NITFs to TIFs if needed
	#high = translate(path)
	
	# cluster the TIFs
	allImages = cluster(path, show=False)
	#allImages = cluster(path, high, show=True)

	# classify crop fields
	allImages = classify(path, allImages, show=True)
	#allImages = classify(path, allImages, high)

	# iteratively classify new training data based on errors
	#while True:
		# if the classification is satisfactory, stop iterating process


		# otherwise, more training data must be provided. 
		# based on error rates, provide user with a mask to load onto QGIS
	createMask(path, allImages)

		# wait for the user to create more training files based on mask

		# reclassify
