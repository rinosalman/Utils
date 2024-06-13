#!/usr/bin/env/ python3
# Generate multilooked lat.rdr, lon.rdr, and z.rdr with the same size as filt_topophase.flat
# Run in an environment where ISCE2 is installed
# Author: Bryan Marfito

# Enable isce2 as a Python module
import isce
# Import topsApp mergeburst library
from isceobj.TopsProc import runMergeBursts
import os


#Use the parameters from topsApp.xml
alks=40
rlks=120

fileNames = ["lon.rdr.full.vrt", "lat.rdr.full.vrt", "z.rdr.full.vrt"]
for x in fileNames:
    x = str(x)
    outputfileName=x[:-9]
    #Create intermediate ISCE files
    print("Generating intermediate files")
    intOutput = outputfileName + "_intermediate.isce"
    os.system("gdal_translate {0} {1} -of ENVI -co interleave=bip".format(x, intOutput))
    #Generate VRT file and make the file ISCE compatible
    os.system("gdal2isce_xml.py -i {0}".format(intOutput))
    #Fix the xml file for consistency with ISCE
    os.system("fixImageXml.py -i {0} -b".format(intOutput))
    #Run multilook on the images
    print("Running multilook")
    runMergeBursts.multilook(intOutput, outputfileName, alks, rlks)
    #Remove intermediate file to save disk space
    os.remove(intOutput)
    os.remove(intOutput[:-5] + ".hdr")
    os.remove(intOutput + ".vrt")
    os.remove(intOutput + ".xml")
    os.remove(intOutput + ".aux.xml")
