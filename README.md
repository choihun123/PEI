<b>Dependencies</b>

To be able to run this TOY program once it is complete, you must have the following dependencies installed on your system:
Python, numpy, sci-kit learn, matplotlib, GDAL, OpenCV, and shapefile. Ideally these are all installed with Homebrew or pip.

<b>Usage of TOY</b> 

python main.py \<file path> \<k clusters>

<b> What happens under the hood </b>

1. Call <b>translate()</b> with the folder path as a parameter. This converts all NITF (National Imagery Transmission Format) images to GeoTIFFs. This will return a number that represents the largest number of pixels in any of the images.
2. Call <b>cluster()</b> with the folder path and the return value of translate() as parameters. This clusters all the TIFs using k-means++ on the four bands: B, G, R, Near-infrared. This will return a list of all images that contains information on the ratios of clusters.
3. Call <b>classify()</b> with folder path and the list of images as parameters. This searches for all training sites in the folder, trains the Maximum Likelihood Classifier, and then calculates the error rates based on the quality testing sites. This will return the list of images with the error rates of the Maximum Likelihood Classification, but will not return the classification results.
4. Based on the error-rates, now create masks of the images so that the user can load the masks into GIS software and map more crop fields in the clusters that had higher error rates. 
5. Repeat steps 2-4 until satisfactory results are available.
