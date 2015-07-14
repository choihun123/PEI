from subprocess import call
import os
import sys

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
	call(["gdal_translate", "--config", "GDAL_CACHEMAX", "512", filePath,
		  sys.argv[1]+"/"+ str(count)+".tif"])

	count += 1