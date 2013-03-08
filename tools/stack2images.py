import os
from loci.plugins.util import BFVirtualStack
from loci.formats import ChannelSeparator

def run():
	# Chose a file to open
	od = OpenDialog("Chose File to Split", None)
	srcDir = od.getDirectory()
	if srcDir is None:
		# User canceled dialog
		return
	path = os.path.join(srcDir, od.getFileName())
	# Chose a directory to store each slice as a file
	targetDir = DirectoryChooser("Chose folder in which to save").getDirectory()
	if targetDir is None:
		# User canceled the diolog
		return
	# Ready:
	cs = ChannelSeparator()
	cs.setId(path)
	bf = BFVirtualStack(path, cs, False, False, False)
	for sliceIndex in xrange(1,bf.getSize() +1):
		print "Well done. Processing slice", sliceIndex
		ip = bf.getProcessor(sliceIndex)
		sliceFileName = os.path.join(targetDir, str(sliceIndex) + ".tif")
		FileSaver(ImagePlus(str(sliceIndex), ip)).saveAsTiff(sliceFileName)
run()