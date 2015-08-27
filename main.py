import sys, os, getopt
from translate import translate
from cluster import cluster
from classify import classify
from mask import createMask
from saveload import saveImages, loadImages
import image

def main(argv):
	# figure out the input
	try:
		opts, args = getopt.getopt(argv, "hptk:d:s:l:")
	except getopt.GetoptError:
		print "Usage: main.py [-h] [-p] [-t] [-k #clusters] "\
				"[-d downsample rate] [-s save file] [-l load file] directory"
		sys.exit(2)

	# initial parameters for specific methods
	show = False
	trans = False
	k = 4
	down = 3
	save = None
	load = None
	ml = None

	# options
	for opt, arg in opts:
		# help function
		if opt == '-h':
			print "Usage: main.py [-h] [-p] [-t] [-k #clusters] "\
				"[-d downsample rate] [-s save file] [-l load file] directory"
			sys.exit()

		# show pictures of clustering and classification
		elif opt == '-p':
			show = True

		# translate NITFs
		elif opt == '-t':
			trans = True

		# number of clusters
		elif opt == '-k':
			if int(arg) <= 0:
				print "Error: k must be positive"
				sys.exit(2)
			k = int(arg)

		# downsample rate
		elif opt == '-d':
			if int(arg) < 0:
				print "Error: downsample rate cannot be negative"
				sys.exit(2)
			down = int(arg)

		# save file
		elif opt == '-s':
			if arg == '':
				print "Error: save file must have a name"
				sys.exit(2)
			save = arg

		# load file
		elif opt == '-l':
			if arg == '':
				print "Error: load file must have a name"
				sys.exit(2)
			load = arg

		# unhandled option
		else:
			assert False, "Error: unhandled option"

	# image directory
	if len(args) != 1:
		print "Usage: main.py [-h] [-p] [-t] [-k #clusters] "\
				"[-d downsample rate] [-s save file] [-l load file] directory"
		sys.exit(2)
	folder = args[0]

	# translate the NITFs to TIFs if needed
	if trans:
		high = translate(folder)
		
		# cluster the TIFs
		allImages = cluster(folder, high, show=True)

		# classify crop fields
		allImages, results, ml = classify(folder, allImages, high, k=k, down=down)

		# save the file
		if save is not None:
			saveImages(folder, allImages, save)

		# if the classification is satisfactory return results. Otherwise, 
		# unsatisfactory results so create masks.
		answer = raw_input("Is this classification satisfactory? y/n\n")
		while True:
			if answer == 'y':
				return results
			elif answer == 'n':
				createMask(folder, allImages)
				break
			else:
				answer = raw_input("Please input 'y' or 'n' and press Enter\n")	
		
	# if there is a save file ready for use
	elif load is not None and save is None:
		allImages = loadImages(folder, load)

	else:
		# cluster the TIFs
		allImages = cluster(folder, show=show, k=k, down=down)
	
		# classify crop fields
		allImages, results, ml = classify(folder, allImages, k=k, down=down, \
											show=show)

		# save the files
		if save is not None:
			saveImages(folder, allImages, save)

		# if the classification is satisfactory return results. Otherwise, 
		# unsatisfactory results so create masks.
		answer = raw_input("Is this classification satisfactory? y/n\n")
		while True:
			if answer == 'y':
				return results
			elif answer == 'n':
				createMask(folder, allImages)
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
		if trans:
			allImages, results, ml = classify(folder, allImages, high, k=k, \
												ml=ml, show=show)
		else:
			allImages, results, ml = classify(folder, allImages, k=k, ml=ml,\
												show=show)

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
	main(sys.argv[1:])	