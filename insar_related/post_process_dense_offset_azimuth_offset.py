#!/usr/bin/env python3

# To post-process pycuampcor products
# Author: Bryan Marfito

# Import libraries
import os, sys, glob
from mintpy.utils import readfile, writefile, isce_utils
from mintpy.cli import view, geocode
import numpy as np


# read in relevant information
atr = readfile.read_roipac_rsc('../data.rsc')
ER = float(atr['EARTH_RADIUS'])
H = float(atr['HEIGHT'])
RPS = float(4.291266717869248)#atr['RANGE_PIXEL_SIZE'])
APS = float(4.125603617541468)#atr['AZIMUTH_PIXEL_SIZE'])

# read in the data
offsetFile='190411-190718_denseoffset.off.geo'
azoff,atr = readfile.read(offsetFile, datasetName='azimuthOffset')
rgoff,atr = readfile.read(offsetFile, datasetName='rangeOffset')

# converting offsets to meters
azimuth_pixel_size=APS*ER/(ER+H)
range_pixel_size=RPS
azoff *= azimuth_pixel_size
rgoff *= range_pixel_size

# masking really large values
azoff[np.abs(azoff)>4] = np.nan
azoff[np.abs(azoff)<-4] = np.nan
azoff[np.abs(azoff)==0] = np.nan
rgoff[np.abs(rgoff)>4] = np.nan
rgoff[np.abs(rgoff)<-4] = np.nan
rgoff[np.abs(rgoff)==0] = np.nan

# save files
Dict = {'az_displacement' : np.array(azoff, dtype=np.float32), 'rg_displacement' : np.array(rgoff, dtype=np.float32)}
ds_unit_dict = {'az_displacement' : 'm', 'rg_displacement' : 'm'}
writefile.write(Dict, out_file="az_rg_offsets_mtr.h5", metadata=atr, ds_unit_dict=ds_unit_dict, compression='lzf')

