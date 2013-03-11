import os
from loci.plugins.util import BFVirtualStack
from loci.formats import ChannelSeparator
from ij.io import FileSaver
from ij import ImagePlus
import ij
import sys


def run(path):
	index = 0
	# Chose a file to open
	srcDir = path
	print srcDir
	# Chose a directory to store each slice as a file
	targetDir = os.path.join(srcDir,"sequence\\")
	print targetDir
	if targetDir is None:
		# User canceled the diolog
		return
	if srcDir is None:
		# User canceled dialog
		return
	os.mkdir(targetDir)
	for f in os.listdir(srcDir):
		path = os.path.join(srcDir, f)
		# Ready:
		cs = ChannelSeparator()
		cs.setId(path)
		bf = BFVirtualStack(path, cs, False, False, False)
		fname = "%06d"%(index-index%200)
		path = os.path.join(targetDir,fname)
		os.mkdir(path)
		for sliceIndex in xrange(1,bf.getSize() +1):
			print "Well done. Processing slice", sliceIndex
			ip = bf.getProcessor(sliceIndex)
			string = "%06d.tif"%index
			sliceFileName = os.path.join(path, string)
			FileSaver(ImagePlus(str(sliceIndex), ip)).saveAsTiff(sliceFileName)
			index +=1
		print "Finished:",path
run(sys.argv[1])