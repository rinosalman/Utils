#!/usr/bin/env python3

# Import libraries
import os
from mintpy.utils import readfile, writefile, isce_utils
from mintpy.cli import geocode
from mintpy.cli import save_gdal
import numpy as np

#Load all files
offsetFile = "offset.bip"
latFile = os.path.join("pycu_geom", "lat.rdr")
lonFile = os.path.join("pycu_geom", "lon.rdr")
covFile = "offset_cov.bip"
snrFile = "offset_snr.bip"
azoff, atr  = readfile.read(offsetFile, datasetName='azimuthOffset')

step = 0.000462963  # deg for 50 m
opt = f' --lalo -{step} {step} --lat-file {latFile} --lon-file {lonFile}'
azoff_snr = readfile.read(snrFile)[0]
azoff_std = np.sqrt(readfile.read(covFile, datasetName='azimuth')[0])

ds_dict = {'snr' : np.array(azoff_snr, dtype=np.float32)}
writefile.write(ds_dict, out_file="snr.h5", metadata=atr, compression='lzf')
out_file = 'snr.geo'
cmd = f'snr.h5 --dset snr -o {out_file} {opt}'
geocode.main(cmd.split())
cmd = f'{out_file}'
save_gdal.main(cmd.split())
