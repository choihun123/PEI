## Dependencies ##

To be able to run this TOY program, you must have the following dependencies installed on your system:
Python 2.7+, numpy, sci-kit learn, matplotlib, GDAL, OpenCV, and shapefile. Ideally these are all installed with Homebrew or pip.

## Usage of TOY 

python main.py [-h] [-p] [-t] [-k #clusters] [-d downsample rate] [-s save file] [-l load file] directory

**-h** Help. Shows the usage of the command line.

**-p** Shows the pictures of the classification and clustering.

**-t** Translate the NITFs in the directory.

**-k** Number of clusters.

**-d** Downsample rate of images.

**-s** Name of file that saves the list of images.

**-l** Name of file to load that holds the list of images.

**directory** - The folder with the NITFs and all training/testing files in it.

## What happens under the hood ##

1. Call **translate()** with the folder path as a parameter. This converts all NITF (National Imagery Transmission Format) images to GeoTIFFs. This will return a number that represents the largest number of pixels in any of the images. 
2. The TOY will wait for the user to draw the first batch of training/testing polygons.
3. Call **cluster()** with the folder path and the return value of translate() as parameters. This clusters all the TIFs using k-means++ on the four bands: B, G, R, Near-infrared. This will return a list of image objects that contains information on the cover rates of clusters.
4. Call **classify()** with folder path and the list of images as parameters. This searches for all training sites in the folder, trains the Maximum Likelihood Classifier, and then calculates the error rates based on the quality testing sites. This will return the list of images with the error rates of the Maximum Likelihood Classification, the classification results, and the MLC object.
5. Based on the error and cover rates, now create masks of each of the clusters of the images so that the user can load the masks into QGIS and map the suggested number of polygons in each cluster.
6. Repeat steps 4 and 5 until results are satisfactory, now feeding the MLC object into **classify()** to retain previous training.

## Polygon drawing instructions ##
1. Open QGIS. If you are drawing the first batch of training/testing polygons, open a TIF file generated by the TOY. If you are drawing training/testing polygons for the iterative part, open all the masks of one image (files with "M" appended to the image name). 
2. Create a "New Shapefile layer" that contains polygons and name it "[Q or T][image name].shp". Note: do not include the final letter of the name if you are working with masks. For example, if the mask is called "M06jun140a.tif" then you'd create "T06jun140.tif".
3. If you are doing the first batch, draw a few crop field and non-crop field polygons anywhere in each image. If you are working with masks, draw in the suggested number of polygons (or a multiple of the numbers) for each of the masks.
When drawing polygons, assign the attribute 'id' to have value 255 if the polygon **is** a crop field, or 1 if the polygon **is not** a crop field.
4. After drawing the polygons, use the "Rasterize" tool (found under Raster->Conversion) and use the shapefile you made as the Input file, 'id' as the Attribute Field, then click "Select" to create a new file called "[Q or T][image name].tif". Click the option for "Raster resolution in map units per pixel". Press OK.
5. If the new raster is just black, right-click the legend entry and go to Properties. Under style->band rendering, set the max to 255. The crop field polygons of the raster should be very visible and should be exactly where the polygons were, while the non-crop field polygons will still be invisible. This means everything worked. If the crop field polygons still do not appear, something is wrong.
6. Repeat this for all images. Then you are ready to continue with the TOY.

## Things to watch out for ##
* K will default to 4 if no K is given in the command line. Downsample rate will default to 1. 
* If using the **save** and **load** functions, it is imperative that you feed the TOY with the same K and downsample rate when you load it as you did when you saved it.
* The TOY will save the state **after** it has clustered and classified the first time **only**. So when the user loads the state in another run, it will always pick up from just after the first classification.
* The higher the downsample rate, the smaller and faster everything will be, but at the cost of accuracy. It is not recommended to downsample more than 1, since anymore downsampling will make the images very blurry and thus make drawing polygons nearly impossible. A typical computer cannot handle down=0 (I run out of RAM with 16GB on my machine..) so in the future running the TOY on a stronger computer will be helpful. If you just want to see a rough clustering and classification quickly, down=4 works nicely.
* The mask files each represent one cluster of the image. Cluster 0 is denoted by 'a', Cluster 1 by 'b', etc.
* At the stage where the user creates polygons, the user **MUST** save the files in the following formats:
 * Training data must be saved as "T[image name].shp". For example, "T06jun140.shp" is a valid name.
 * Quality testing data must be saved as "Q[image name].shp". For example, "Q06jun141.shp" is a valid name.
 * The rasterized polygons must be saved "[Q or T][image name].tif". For example, "T06jun140.tif" is a valid name.
* If no Q polygons exist for an image, no error rates will be printed since none can be calculated.
* For debugging purposes, if you want to see if the TOY is correctly reading the polygons , in classify.py you can decomment lines 69 and 144.
