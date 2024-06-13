#!/usr/bin/env python3

# To post-process pycuampcor products
# Author: Bryan Marfito

# Import libraries
import os, sys
from mintpy.utils import readfile, writefile, isce_utils
from mintpy.cli import view, geocode
import numpy as np

snr=sys.argv[1]

#Load all files
offsetFile = "offset.bip"
latFile = os.path.join("pycu_geom", "lat.rdr")
lonFile = os.path.join("pycu_geom", "lon.rdr")
losFile = os.path.join("pycu_geom", "los.rdr")
covFile = "offset_cov.bip"
snrFile = "offset_snr.bip"
waterMask = "wbd/waterMask.h5"
xmlFile = "../exp1_pixeloffset/reference/IW1.xml"
azoff, atr  = readfile.read(offsetFile, datasetName='azimuthOffset')
azoff_std   = np.sqrt(readfile.read(covFile, datasetName='azimuth')[0])
watermsk = readfile.read(waterMask)[0]

#Convert range pixel shifts into meters, check xml files for details
meta = isce_utils.extract_isce_metadata(xmlFile, update_mode=False)[0]
azi_pixel_size = float(meta['AZIMUTH_PIXEL_SIZE'])
Re, h_sat = float(meta['EARTH_RADIUS']), float(meta['HEIGHT'])
pixel_size = azi_pixel_size * Re / (Re+h_sat)
#pixel_size = float(4.291266717869248)

print("Convert pixel shifts to meters")
azoff *= pixel_size
azoff_std *= pixel_size


# Remove anomalous values
azoff[watermsk==0] = np.nan
azoff[np.abs(azoff) > 20] = np.nan
azoff_std[np.isnan(azoff)] = np.nan
azoff[azoff == 0] = np.nan
# Skip pixels with SNR < 3
azoff_snr = readfile.read(snrFile)[0]
azoff[np.isnan(azoff_snr)] = np.nan
azoff[azoff_snr < snr] = np.nan
# Skip pixels with STD < 15 cm, optional
#azoff[azoff_std > 0.15] = np.nan

ds_dict = {'displacement' : np.array(azoff, dtype=np.float32), 'displacementStd' : np.array(azoff_std, dtype=np.float32)}
ds_unit_dict = {'displacement' : 'm', 'displacementStd' : 'm'}
writefile.write(ds_dict, out_file="azOff.h5", metadata=atr, ds_unit_dict=ds_unit_dict, compression='lzf')

#Geocode files, check geocode.py in MintPy
step = 0.000462963  # deg for 50 m
opt = f' --lalo -{step} {step} --lat-file {latFile} --lon-file {lonFile}'

geo_file = 'azOff.geo'
cmd = f'azOff.h5 --dset displacement -o {geo_file} {opt}'
geocode.main(cmd.split())
view.main([f'{geo_file}'])

#out_file = 'azOffStd.geo'
#cmd = f'azOff.h5 --dset displacementStd -o {out_file} {opt}'
#geocode.main(cmd.split())

#out_file = 'losAz.geo'
#cmd = f'{losFile} -o {out_file} {opt}'
#geocode.main(cmd.split())
