## Dependencies ##

To be able to run this TOY program once it is complete, you must have the following dependencies installed on your system:
Python, numpy, sci-kit learn, matplotlib, GDAL, OpenCV, and shapefile. Ideally these are all installed with Homebrew or pip.

## Usage of TOY 

python main.py [-h] [-p] [-t] [-k #clusters] [-d downsample rate] [-s save file] [-l load file] directory

**-h** Help. Shows the usage of the command line.

**-p** Shows the pictures of the classification and clustering.

**-t** Translate the NITFs in the directory.

**-k** Number of clusters.

**-d** Downsample rate of images.

**-s** Name of file that saves the list of images.

**-l** Name of file to load that holds the list of images.


## What happens under the hood ##

1. Call **translate()** with the folder path as a parameter. This converts all NITF (National Imagery Transmission Format) images to GeoTIFFs. This will return a number that represents the largest number of pixels in any of the images.
2. Call **cluster()** with the folder path and the return value of translate() as parameters. This clusters all the TIFs using k-means++ on the four bands: B, G, R, Near-infrared. This will return a list of all images that contains information on the cover rates of clusters.
3. Call **classify()** with folder path and the list of images as parameters. This searches for all training sites in the folder, trains the Maximum Likelihood Classifier, and then calculates the error rates based on the quality testing sites. This will return the list of images with the error rates of the Maximum Likelihood Classification, the classification results, and the MLC object.
4. Based on the error-rates, now create masks of each of the clusters of the images so that the user can load the masks into GIS software and map the suggested number of polygons in each cluster.
5. Repeat steps 2-4 until satisfactory results are available, now feeding the MLC object into **classify()** to retain previous training.
 

## Things to watch out for ##

* If using the **save** and **load** functions, it is imperative that you feed the TOY with the same K and downsample rate when you load it as you did when you saved it.
* The higher the downsample rate, the smaller and faster everything will be, at the cost of accuracy.
