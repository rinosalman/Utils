#!/usr/bin/env python3

# To post-process pycuampcor products
# Author: Bryan Marfito

# Import libraries
import os
from mintpy.utils import readfile, writefile
from mintpy import view, geocode
import numpy as np

#Load all files
offsetFile = "dense_offset_pycuampcor.bip"
latFile = os.path.join("offset_geom", "lat.rdr")
lonFile = os.path.join("offset_geom", "lon.rdr")
losFile = os.path.join("offset_geom", "los.rdr")
covFile = "dense_offset_pycuampcor_cov.bip"
snrFile = "dense_offset_pycuampcor_snr.bip"
xmlFile = "../exp1_pixeloffset/reference/IW1.xml"
rgoff, atr  = readfile.read(offsetFile, datasetName='rangeOffset')
rgoff_std   = np.sqrt(readfile.read(covFile, datasetName='range')[0])

#Convert range pixel shifts into meters, check xml files for details
meta = isce_utils.extract_isce_metadata(xmlFile, update_mode=False)[0]
pixel_size = float(meta['RANGE_PIXEL_SIZE'])
#pixel_size = float(4.291266717869248)

rgoff *= pixel_size
rgoff_std *= pixel_size


# Remove anomalous values
rgoff[np.abs(rgoff) > 2] = np.nan
rgoff_std[np.isnan(rgoff)] = np.nan
rgoff[rgoff == 0] = np.nan
# Skip pixels with SNR < 3
rgoff_snr = readfile.read(snrFile)[0]
rgoff[np.isnan(rgoff_snr)] = np.nan
rgoff[rgoff_snr < 3] = np.nan
# Skip pixels with STD < 15 cm, optional
#rgoff[rgoff_std > 0.15] = np.nan

ds_dict = {'displacement' : np.array(rgoff, dtype=np.float32), 'displacementStd' : np.array(rgoff_std, dtype=np.float32)}
ds_unit_dict = {'displacement' : 'm', 'displacementStd' : 'm'}
writefile.write(ds_dict, out_file="rgOff.h5", metadata=atr, ds_unit_dict=ds_unit_dict, compression='lzf')

#Geocode files, check geocode.py in MintPy
step = 0.000462963  # deg for 50 m
opt = f' --lalo -{step} {step} --lat-file {latFile} --lon-file {lonFile}'

geo_file = 'rgOff.geo'
cmd = f'rgOff.h5 --dset displacement -o {geo_file} {opt}'
geocode.main(cmd.split())
view.main([f'{geo_file}'])

#out_file = 'rgOffStd.geo'
#cmd = f'rgOff.h5 --dset displacementStd -o {out_file} {opt}'
#geocode.main(cmd.split())

#out_file = 'rng.los.geo'
#cmd = f'{losFile} -o {out_file} {opt}'
#geocode.main(cmd.split())
