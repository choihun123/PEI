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