import sys, os
from translate import translate
from cluster import cluster
from classify import classify
from mask import createMask
from saveload import saveImages, loadImages

if __name__ == '__main__':
	# validate input
	if len(sys.argv) != 4:
		sys.exit("Usage: main.py <directory> <k> <downsample rate>")
	if not os.path.isdir(sys.argv[1]):
		sys.exit("Error: given path is not a directory")
	if int(sys.argv[2]) < 0:
		sys.exit("Error: k cannot be negative")
	if int(sys.argv[3]) < 0:
		sys.exit("Error: downsampling rate cannot be negative")
	#if not 0 < int(sys.argv[4]) < 1:
		#sys.exit("Error: the error threshold must be between 0 and 1")
	
	# use input
	path = sys.argv[1]
	k = int(sys.argv[2])
	down = int(sys.argv[3])

	#TODO add optional command line arguments for K and down and 
	# flags for the other options in cluster.py

	# translate the NITFs to TIFs if needed
	#high = translate(path)
	
	# cluster the TIFs
	allImages = cluster(path, show=False, k=k, down=down)
	#allImages = cluster(path, high, show=True)

	# classify crop fields
	allImages, classification = classify(path, allImages, k=k, down=down)
	#allImages = classify(path, allImages, high)

	# iteratively classify new training data based on errors
	#while True:
		# if the classification is satisfactory, stop iterating process
		# if error_rates are low enough:
			# break

		# otherwise, more training data must be provided. 
		# based on error rates, provide user with a mask to load onto QGIS
	createMask(path, allImages)

		# wait for the user to create more training files based on mask

		# reclassify
		#allImages, classification = classify(path, allImages, down=0)