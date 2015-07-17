<b>Dependencies</b>

To be able to run this TOY program, you must have the following dependencies installed on your system:
Python
numpy
scipy
GDAL


<b>Usage of TOY</b> 

python main.py -various options \<file path> \<k clusters>

<b> What happens under the hood </b>

1. Call <b>translate()</b> with the folder path as a parameter. This converts all NITFs to TIFs. This will return a number that represents the largest number of pixels in any of the images.
2. Call <b>cluster()</b> with the folder path and the return value of translate() as parameters. This clusters all the TIFs using k-means on the four bands: B, G, R, N. This will return a list of all images that contains information on the ratios of clusters.
3. Call <b>classify()</b>.
