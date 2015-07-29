import os, sys
from translate import translate
from cluster import cluster
from classify import classify

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
	#allImages = cluster(path, high, show=False)

	# classify crop fields
	allImages = classify(path, allImages)

	# calculate error rates

	# based on error rates, re-classify with more emphasis on less correct
	# cluster types

	# calculate error rates again