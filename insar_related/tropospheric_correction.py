import mintpy
import mintpy.workflow
from mintpy.utils import ptime, utils1, readfile, writefile, isce_utils, utils as ut
from mintpy.objects import deramp
from mintpy import tropo_gacos, tropo_pyaps3
from mintpy import reference_point
from mintpy.add import add_file
import numpy as np
from matplotlib import pyplot as plt
import os
import ref_point


# data information
dates = '221110-221124'
dates_rlks_alks = '{}_5rlks_28alks'.format(dates)
refDate = '221110'

# create .rsc for *.msk.unw, .lat, and .lon
unw = 'filt_{}_msk.unw'.format(dates_rlks_alks)
los = '{}.los'.format(dates_rlks_alks)
hgt = '{}.hgt'.format(dates_rlks_alks)
cor = '{}.cor'.format(dates_rlks_alks)
wbd = '{}.wbd'.format(dates_rlks_alks)
trackFile = '{}.track.xml'.format(refDate)
os.chdir('../')
os.system('''prep_isce.py -f insar/{}.geo -g insar/ -m {}'''.format(unw,trackFile))
os.chdir('insar')
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(unw,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(los,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(hgt,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(cor,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(wbd,trackFile))

# geocode manually *msk.unw, .los, and .height
lonFile = '{}.lon'.format(dates_rlks_alks)
latFile = '{}.lat'.format(dates_rlks_alks)
geoMskUnw = 'geo_filt_msk.unw'
losGeo = 'los_geocoded_manually.los.geo'
hgtGeo = 'height_geocoded_manually.hgt.dem'
corGeo = 'cor_geocoded_manually.cor.geo'
wbdGeo = 'wbd_geocoded_manually.wbd.geo'
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(unw,latFile,lonFile,geoMskUnw))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(los,latFile,lonFile,losGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(hgt,latFile,lonFile,hgtGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(cor,latFile,lonFile,corGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(wbd,latFile,lonFile,wbdGeo))

# generate water body in MintPy format
wbdGeoMintpy = 'waterBody.geo'
os.system('''generate_mask.py {} -M 0.5 -o {}'''.format(wbdGeo,wbdGeoMintpy))

# masking the files
geoMskUnwWbd = 'geo_filt_msk_wbd.unw'
losGeoWbd = 'los_geocoded_manually_wbd.los.geo'
os.system('''mask.py {} -m {} -o {}'''.format(geoMskUnw,wbdGeoMintpy,geoMskUnwWbd))
os.system('''mask.py {} -m {} -o {}'''.format(losGeo,wbdGeoMintpy,losGeoWbd))

# read attribute
atr = readfile.read_attribute(geoMskUnw)

# update existing attribute
atrroipac = readfile.read_roipac_rsc('../data.rsc')
atr['DATE12'] = dates
utils1.add_attribute(geoMskUnw, atr)

# spatial referencing 
ref_lat, ref_lon = -6.617721, 107.103940
cmd = '{} --lat {} --lon {} --write-data'.format(geoMskUnwWbd,ref_lat,ref_lon)
ref_point.main(cmd.split())

# incidence angle
dsDict = {}
dsDict['incidenceAngle']=readfile.read(losGeo, datasetName='incidenceAngle')[0]
dsDict['height']=readfile.read(hgtGeo, datasetName='height')[0]
writefile.write(dsDict, 'geometry.h5', metadata=atr)

# PyAPS correction
correctedUnw = 'geo_filt_msk_wbd_ERA5.unw'
os.system('''tropo_pyaps3.py -f {} -g geometry.h5 -o {}'''.format(geoMskUnwWbd,correctedUnw))

# GACOS correction
correctedUnw = 'geo_filt_msk_wbd_GACOS.unw'
os.system('''tropo_gacos.py -f {} -g geometry.h5 --dir ./GACOS -o {}'''.format(geoMskUnwWbd,correctedUnw))
