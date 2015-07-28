import subprocess as sp
import os
import sys

def translate(folder):
	""" 
	Uses GDAL_TRANSLATE to convert all the NITFs in folder into TIFs. 
	Returns the number of pixels of the largest iamge.
	"""
	# validate input
	if not os.path.isdir(folder):
		sys.exit("Error: given path is not a directory")

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
							   "512", filePath, folder+"/"+ str(count)+".tif"],
							   stderr=sp.STDOUT)

		# extract numbers from stdout
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
		print 'usage: translate.py <path to folder with NITFs>'
		sys.exit(2)

	# counts number of NITFs
	count = 0

	# iterate through all files
	for name in os.listdir(sys.argv[1]):
		# ignore hidden files and non-NITF files
		if name.startswith('.') or not name.endswith(".ntf"):
			continue
		filePath = os.path.join(sys.argv[1], name)
		
		# call gdal_translate on a whole folder of NITF files. Save in input folder
		sp.check_output(["gdal_translate", "--config", "GDAL_CACHEMAX", "512", 
					  filePath, sys.argv[1]+"/"+ str(count)+".tif"],
					  stderr=sp.STDOUT)

		count += 1