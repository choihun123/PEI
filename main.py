import sys, os
from translate import translate
from cluster import cluster
from classify import classify
from mask import createMask
from saveload import saveImages, loadImages
import image

def main():
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
	allImages, results, ml = classify(path, allImages, k=k, down=down)
	#allImages, results, ml = classify(path, allImages, high, k=k, down=down)

	# if the classification is satisfactory return results. Otherwise, 
	# unsatisfactory results so create masks.
	answer = raw_input("Is this classification satisfactory? y/n\n")
	while True:
		if answer == 'y':
			return results
		elif answer == 'n':
			createMask(path, allImages)
			break
		else:
			answer = raw_input("Please input 'y' or 'n' and press Enter\n")	

	# iteratively classify new training data based on errors
	while True:
		# calculate new number of polygons required for each cluster
		image.calculatePolygons(allImages, k, N=20)

		# wait for the user to create more training files based on calculations
		print "Waiting for user to draw new training data."
		raw_input("Press Enter to continue...")

		# reclassify
		allImages, results, ml = classify(path, allImages, k=k, ml=ml)
		#allImages, results, ml = classify(path, allImages, high, k=k, ml=ml)

		# if classification is satisfactory, then return results
		answer = raw_input("Is this classification satisfactory? y/n\n")
		while True:
			if answer == 'y':
				return results
			elif answer == 'n':
				break
			else:
				answer = raw_input("Please input 'y' or 'n' and press Enter\n")

if __name__ == '__main__':
	main()	