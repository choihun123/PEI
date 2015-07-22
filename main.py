import os, sys
from translate import translate
from cluster import cluster

if __name__ == '__main__':
	# verify folder path
	if not os.path.isdir(sys.argv[1]):
		sys.exit("Error: given path is not a directory")
	path = sys.argv[1]

	# translate the NITFs to TIFs if needed
	high = translate(path)
	
	# cluster the TIFs
	allImages = cluster(path, high)

	# classify crop fields
	allImages = classify(path, allImages)

	# calculate error rates

	# based on error rates, re-classify with more emphasis on less correct
	# cluster types

	# calculate error rates again