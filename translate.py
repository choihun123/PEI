#-------------------------------------------------------------------------------
# Author: Hun Choi
#-------------------------------------------------------------------------------
import subprocess as sp
import sys, os

""" 
This method uses GDAL_TRANSLATE to convert all the NITFs in specified 
directory into TIFs. Uses extra cache memory and baseline profile. The 
parameter performs the following:

folder - path to the directory that has the TIF files

This method returns the number of pixels of the largest image, which is used
in cluster.py and classify.py. 

Can also call this script from the command line separately:
python translate.py /Users/jsmith/folder
"""
def translate(folder):
	""" Translate NITFs to TIFs """
	# validate input
	if not os.path.isdir(folder):
		sys.exit("Error: given path is not a directory")

	print " Translating NITFs to TIFs..."
	
	# counts number of NITFs
	count = 0

	# highest resolution of image, to be used in cluster.py
	high = 0

	# iterate through all files
	for name in os.listdir(folder):
		# ignore hidden files and non-NITF files
		if name.startswith('.') or not name.endswith(".ntf"):
			continue
		filePath = os.path.join(folder, name)
		
		# convert all NITFs in folder to TIFs in same folder
		output = sp.check_output(["gdal_translate", "--config", "GDAL_CACHEMAX", 
							   "512", "-co", "PROFILE=BASELINE", filePath, 
							   folder + "/"+ name[:7] + str(count)+".tif"],
							   stderr=sp.STDOUT)

		# delete the RPB and XML file that contains the geographic data
		os.remove(folder + "/"+ name[:7] + str(count) + ".RPB")
		os.remove(folder + "/"+ name[:7] + str(count) + ".tif.aux.xml")

		# extract image dimensions from stdout
		output = output.replace(',',' ')
		n = [int(s) for s in output.split() if s.isdigit()]

		# calculate number of pixels. Replace high if larger
		current = n[0] * n[1]
		if current > high:
			high = current

		count += 1

	return high

# if called as a script, translate
if __name__ == "__main__":
	# validate input
	if len(sys.argv) != 2:
		print 'Usage: translate.py <path to folder with NITFs>'
		sys.exit(2)

	# counts number of NITFs
	count = 0

	# iterate through all files
	for name in os.listdir(sys.argv[1]):
		# ignore hidden files and non-NITF files
		if name.startswith('.') or not name.endswith(".ntf"):
			continue
		filePath = os.path.join(sys.argv[1], name)
		
		# convert all NITFs in folder to TIFs in same folder
		output = sp.check_output(["gdal_translate", "--config", "GDAL_CACHEMAX", 
							   "512", "-co", "PROFILE=BASELINE", filePath, 
							   sys.argv[1] + "/"+ name[:7] + str(count)+".tif"],
							   stderr=sp.STDOUT)

		# delete the RPB and XML file that contains the geographic data
		os.remove(sys.argv[1] + "/"+ name[:7] + str(count) + ".RPB")
		os.remove(sys.argv[1] + "/"+ name[:7] + str(count) + ".tif.aux.xml")

		count += 1