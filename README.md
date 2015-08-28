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

## Polygon drawing instructions ##
1. Open QGIS. Open all the masks of one image and create a "New Shapefile layer" that contains polygons and name it "[Q or T][image name].shp". Note: do not include the final letter of the name. For example, if the mask is called "M06jun140a.tif" then you'd create "T06jun140.tif".
2. Draw in the suggested number of polygons (or a multiple of the numbers) for each of the masks.
When drawing polygons, assign the attribute 'id' to have value 255 if the polygon is a crop field, or 1 if the polygon is not a crop field.
3. After drawing the polygons, use the "Rasterize" tool (found under Raster->Conversion) and use the file you made as the Input file, 'id' as the Attribute Field, then select and create a new file called "[Q or T][image name].tif". Click the option for "Raster resolution in map units per pixel". Press OK.
4. If the new raster is just black, right-click the legend entry and go to Properties. Under style->band rendering, set the max to 255. The crop field polygons should be very visible, while the non-crop field polygons will still be invisible. If the crop field polygons still do not appear, something is wrong.
4. Repeat this for all images. Then you are ready to continue with the TOY.

## Things to watch out for ##
* K will default to 4 if no K is given in the command line. Downsample rate will default to 1. 
* If using the **save** and **load** functions, it is imperative that you feed the TOY with the same K and downsample rate when you load it as you did when you saved it.
* The higher the downsample rate, the smaller and faster everything will be, but at the cost of accuracy.
* The mask files each represent one cluster of the image. Cluster 0 is denoted by 'a', Cluster 1 by 'b', etc.
* At the stage where the user creates polygons, the user **MUST** save the files in the following formats:
 * Training data must be saved as "T[image name].shp". For example, "T06jun140.shp" is a valid name.
 * Quality testing data must be saved as "Q[image name].shp". For example, "Q06jun141.shp" is a valid name.
 * The rasterized polygons must be saved "[Q or T][image name].tif". For example, "T06jun140.tif" is a valid name.

