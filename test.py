import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
from image import *
import gdal
import gdalconst
import struct

# Find path to the images 
path = "/Users/hunchoi/Code/PEI/sample_images/2.png"

# Open the file
img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
if img is None:
	sys.exit("Image failed to read")

def test(NIR, R):
	if (NIR + R) != 0:
		return (NIR - R)/(NIR + R)
	return 0

print test(186, 71)
print test(0., 255.)
print test(20., 100.)
print test(100., 20.)
print test(0.,0.)


"""
Hold this Code
	# list of Image objects
	Images = []

	# iterate through all the files in the directory
	for name in os.listdir(path):
		# ignore hidden files and non-files
		if name.startswith('.'):
			continue
		filePath = os.path.join(path, name)
		if not os.path.isfile(filePath):
			continue
"""