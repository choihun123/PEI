import numpy as np
import gdal
import gdalconst

#-------------------------------------------------------------------------------

'''
load an (image, transform) from a file name
when loading an orthophoto from file, the image is loaded to a numpy array
and the geographical data is loaded to a GeoTform object
'''
def load(filename):
	# open dataset from gdal
	dataset = gdal.Open(filename, gdalconst.GA_ReadOnly)

	# create image array and read in each raster band
	image = np.empty([dataset.RasterCount, dataset.RasterYSize, \
                                         dataset.RasterXSize], np.uint8)
	for i in range(dataset.RasterCount):
		image[i] = dataset.GetRasterBand(i+1).ReadAsArray( \
                           0, 0, dataset.RasterXSize, dataset.RasterYSize)

	# create geo transform
	transform = GeoTransform(dataset)

	return (image, transform)

'''
save an (image, transform) to a file
'''
def save(image, transform, filename, fmt = "GTiff"):
	driver = gdal.GetDriverByName(fmt) # check if supports create? or is None?
	size = np.shape(image)
	dataset = driver.Create(filename, size[2], size[1], size[0], gdal.GDT_Byte)
	dataset.SetGeoTransform([transform.GeoOffset[0],   transform.GeoTform[0, 0], \
                              transform.GeoTform[0, 1], transform.GeoOffset[1], \
                              transform.GeoTform[1, 0], transform.GeoTform[1, 1]\
                             ])
	dataset.SetProjection(transform.Projection)
	for i in range(size[0]):
		dataset.GetRasterBand(i + 1).WriteArray(image[i])

	return dataset

#-------------------------------------------------------------------------------

'''
return a pyramid version of the image with fewer pixels
pyramids are often easier to work with and display than the full image

*I don't think this is working properly right now
'''
'''
def pyramid(image, transform, reduction):
	size = (np.array(image.shape) / reduction).astype(np.int)
	image_out = np.empty(size)
	transform_out = transform.copy()
	transform_out.GeoTform = transform_out.GeoTform * (np.eye(2) * reduction)

	for y in range(size[0]):
		y_range = y * np.ones(size[1])
		x_range = np.arange(size[1])
		coords = np.array([x_range, y_range])           # get locs of pixels on image out
		coords = transform_out.intrinsicToWorld(coords) # convert those to real world
		coords = transform.worldToIntrinsic(coords)     # and then to pixel locations on base image
		image_out[y,:] = getPixels(image, coords)

	return (image_out, transform_out)
'''
#-------------------------------------------------------------------------------

'''
GeoTransform: class that deals with image world coordinates

data members
------------
GeoOffset  | the real world location of the 0,0 pixel
GeoTform   | 2x2 matrix that converts pixel coordinates to real world locations
Projection | data on the orthoimage projection type - loaded in from GDAL

functions
---------
GeoTransform() | initializer - creates empty object. otherwise, use load 
                   to create a GeoTransform
   args: 
      None
   returns:
      geoTform | a GeoTransform object
 
worldToIntrinsic(worldCoords) | converts a list of world coordinates to local 
                                  pixel coordinates
   args:
      worldCoords | a 2xN array of N world coordinate points
   returns:
      pixelCoords | a 2xN array of N pixel coordinate points

intrinsicToWorld(coords) | converts a list of pixel coordinates to world coordinates
   args:
      coords | a 2xN array of N pixel coordinate points
   returns:
      worldCoords | a 2xN array of N world coordinate points

transform(tform, offset) | transforms this geographic transform
   args: 
      tform  | the transform matrix to multiply the current one by (identity matrix if unspecified)
      offset | the offset array to add to the current one (0,0 if unspecified)
   returns: 
      None

copy() | returns a copy of the current transform
   args:
      None
   returns:
      geotform | a copy of the GeoTransform object
'''
class GeoTransform:
	def __init__(self, dataset=None):
		if dataset==None:
			self.GeoOffset = np.array([[0], [0]])
			self.GeoTform = np.matrix([[1, 0], [0, 1]])
			self.Projection = None
		else:
			gt = dataset.GetGeoTransform()
			self.GeoOffset = np.array([[gt[0]], [gt[3]]])
			self.GeoTform = np.matrix(((gt[1], gt[2]), (gt[4],gt[5])))
			self.Projection = dataset.GetProjection()

	# convert the set of world coordinates in array worldCoords to
	# an array of intrinsic coordinates
	def worldToIntrinsic(self, worldCoords):
		return np.asarray(self.GeoTform.I).dot(worldCoords \
                - self.GeoOffset.dot(np.ones([1,worldCoords.shape[1]])))

	# convert the set of intrinsic coordinates in array coords to
	# an array of world coordinates
	def intrinsicToWorld(self, coords):
		return np.asarray(self.GeoTform).dot(coords) \
                + self.GeoOffset.dot(np.ones([1,coords.shape[1]]))

	def transform(self, tform = np.eye(2), offset = np.array([[0],[0]])):
		self.GeoTform =  tform * self.GeoTform
		self.GeoOffset = self.GeoOffset + offset
		return self

	def copy(self):
		tform = GeoTransform()
		tform.GeoOffset  = self.GeoOffset.copy()
		tform.GeoTform   = self.GeoTform.copy()
		tform.Projection = self.Projection
		return tform

#-------------------------------------------------------------------------------

'''
getPixels(image, icoords) | computationally fast linear interpolation
   args:
      image   | a 2D array of image pixel values (the image to interpolate)
      icoords | a 2xN list of pixel coordinates
   returns: 
      worldCoords | a 1xN array of interpolated values at the locations in icoords

this function takes advantage of scipy math and contains no loops so it is
significantly faster than the default python interpolation
'''
# computationally fast linear interpolation
def getPixels(image, icoords):
		x = icoords[0]
		y = icoords[1]
		# get points to interpolate
		x0 = np.floor(x).astype(int)
		x1 = x0 + 1
		y0 = np.floor(y).astype(int)
		y1 = y0 + 1
		# catch if on edge
		xLim = np.shape(image)[1] - 1
		yLim = np.shape(image)[0] - 1
		x0 = np.clip(x0, 0, xLim)
		x1 = np.clip(x1, 0, xLim)
		y0 = np.clip(y0, 0, yLim)
		y1 = np.clip(y1, 0, yLim)
		# calculate image points
		Ia = image[y0, x0]
		Ib = image[y1, x0]
		Ic = image[y0, x1]
		Id = image[y1, x1]
		# get weight values
		wa = (x1-x) * (y1-y)
		wb = (x1-x) * (y-y0)
		wc = (x-x0) * (y1-y)
		wd = (x-x0) * (y-y0)

		return wa*Ia + wb*Ib + wc*Ic + wd*Id
