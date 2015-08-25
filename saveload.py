import cPickle

"""
This method is used to save the list of images into the directory. The 
parameters perform the following functions:

folder   - path to the directory that has the TIF files
images   - list of all image objects
filename - name of the new binary file to be generated

This method does not return anything, but will create a file in the directory
named filename that holds the list in binary. loadImages() should be used to
retrieve it.
"""
def saveImages(folder, images, filename):
	""" Save the list of images """
	# open new file and write binary file
	with open(folder+filename, 'wb') as f:
		# save the whole images list using pickle
		cPickle.dump(images, f, -1)

	# notify user of successful save
	print "List of images saved as '" + filename + "'"

"""
This method is used to load the file previously created.

folder   - path to the directory that has the TIF files
filename - name of the binary file that was generated with saveImages

This method returns the list of images.
"""
def loadImages(folder, filename):
	""" Loads the list of images """
	# open the file to read binary file
	with open(folder+filename, 'rb') as f:
		# load the whole images list using pickle
		images = cPickle.load(f)

	# notify user of successful load and return
	print "List of images '" + filename + "' loaded"
	return images