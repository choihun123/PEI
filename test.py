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

totalData = np.zeros([1, 4])
data = np.array([0, 1, 2, 3])
np.append(totalData, data)
print totalData
