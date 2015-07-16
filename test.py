import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
from image import *
import gdal
import gdalconst
import struct
from cluster import cluster
from translate import translate

path = "/Users/hunchoi/Code/PEI/satellite/ntf/test"
high = translate(path)
print high
cluster(path, high, down=3, plot2D=True, plot3D=True)
